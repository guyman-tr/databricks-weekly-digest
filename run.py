"""
Databricks Weekly Digest - Main Entry Point

Usage:
    python run.py                    # Full pipeline: aggregate + summarize + podcast (both tracks)
    python run.py --skip-podcast     # Just the written digests, no audio
    python run.py --digest-only      # Aggregate + summarize, skip distribution
    python run.py --track de         # Only generate for Data Engineering track
    python run.py --track analytics  # Only generate for Analytics & DS track
    python run.py --from-digest PATH # Generate podcast from existing digest file
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv
import os

load_dotenv()


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    email = config["distribution"]["email"]
    if os.getenv("EMAIL_ENABLED", "").lower() == "true":
        email["enabled"] = True
    if os.getenv("SMTP_USER"):
        email["gmail_user"] = os.getenv("SMTP_USER")
    if os.getenv("SMTP_PASS"):
        email["gmail_app_password"] = os.getenv("SMTP_PASS")

    return config


def aggregate(config: dict) -> list:
    from src.aggregators import BlogAggregator, YouTubeAggregator, ReleasesAggregator, RoadmapAggregator

    lookback = config["digest"]["lookback_days"]
    all_items = []

    blog_cfg = config["sources"]["databricks_blog"]
    if blog_cfg["enabled"]:
        agg = BlogAggregator(blog_cfg["rss_url"], blog_cfg["max_items"])
        all_items.extend(agg.fetch(lookback))

    release_cfg = config["sources"]["databricks_releases"]
    if release_cfg["enabled"]:
        agg = ReleasesAggregator(release_cfg["rss_url"], release_cfg["max_items"])
        all_items.extend(agg.fetch(lookback))

    roadmap_cfg = config["sources"].get("databricks_roadmap", {})
    if roadmap_cfg.get("enabled"):
        agg = RoadmapAggregator(
            urls=roadmap_cfg.get("urls", []),
            release_rss=roadmap_cfg.get("release_rss"),
            max_items=roadmap_cfg.get("max_items", 10),
        )
        all_items.extend(agg.fetch(lookback))

    yt_cfg = config["sources"]["youtube"]
    if yt_cfg["enabled"]:
        agg = YouTubeAggregator(yt_cfg["channels"], yt_cfg["max_items_per_channel"])
        all_items.extend(agg.fetch(lookback))

    all_items.sort(key=lambda x: x.published, reverse=True)
    return all_items


def summarize_track(items: list, config: dict, api_key: str, track_cfg: dict) -> str:
    from src.summarizer import Summarizer
    s = Summarizer(api_key, config["summarizer"]["model"])
    return s.summarize(
        items,
        config["summarizer"]["max_digest_items"],
        track_name=track_cfg["name"],
        track_focus=track_cfg["focus"],
    )


def generate_podcast_track(
    digest: str, config: dict, api_key: str, output_dir: Path, track_cfg: dict,
) -> dict:
    from src.podcast import PodcastGenerator
    pc = config["podcast"]
    gen = PodcastGenerator(
        api_key=api_key,
        host1_name=pc["hosts"]["host1"]["name"],
        host1_voice=pc["hosts"]["host1"]["voice"],
        host1_role=pc["hosts"]["host1"]["role"],
        host2_name=pc["hosts"]["host2"]["name"],
        host2_voice=pc["hosts"]["host2"]["voice"],
        host2_role=pc["hosts"]["host2"]["role"],
        tts_model=pc["tts_model"],
        text_model=config["summarizer"]["model"],
        target_words=pc["target_words"],
    )
    slug = track_cfg["slug"]
    return gen.generate(
        digest,
        output_dir,
        file_suffix=f"-{slug}",
        track_name=track_cfg["name"],
        track_intro=track_cfg["podcast_intro"],
    )


def distribute(digest: str, podcast_result: dict | None, config: dict, date_str: str):
    dist = config["distribution"]

    if dist["email"]["enabled"]:
        from src.distribution import EmailSender
        sender = EmailSender(dist["email"])
        subject = f"Databricks Weekly Digest - {datetime.now().strftime('%b %d, %Y')}"
        sender.send(subject, date_str)

    if dist["teams"]["enabled"]:
        from src.distribution import TeamsSender
        sender = TeamsSender(dist["teams"]["webhook_url"])
        title = f"Databricks Weekly - {datetime.now().strftime('%b %d')}"
        sender.send(title, digest[:500])

    if dist["confluence"]["enabled"]:
        from src.distribution import ConfluencePublisher
        pub = ConfluencePublisher(
            dist["confluence"]["cloud_id"],
            dist["confluence"]["space_id"],
            dist["confluence"]["parent_page_id"],
        )
        title = f"Databricks Weekly Digest - {datetime.now().strftime('%b %d, %Y')}"
        pub.publish(title, digest)


def get_tracks(config: dict, track_filter: str | None) -> list[dict]:
    """Return list of track configs to process, optionally filtered by slug."""
    tracks = []
    for _key, track_cfg in config["tracks"].items():
        if track_filter and track_cfg["slug"] != track_filter:
            continue
        tracks.append(track_cfg)
    return tracks


def main():
    parser = argparse.ArgumentParser(description="Databricks Weekly Digest")
    parser.add_argument("--skip-podcast", action="store_true", help="Skip podcast generation")
    parser.add_argument("--digest-only", action="store_true", help="Skip distribution")
    parser.add_argument("--track", type=str, choices=["de", "analytics"], help="Only generate specific track")
    parser.add_argument("--from-digest", type=str, help="Generate podcast from existing digest file")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found. Set it in .env or environment.")
        sys.exit(1)

    config = load_config()
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(__file__).parent / "output" / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    tracks = get_tracks(config, args.track)
    if not tracks:
        print(f"ERROR: No track matching '{args.track}'")
        sys.exit(1)

    if args.from_digest:
        digest = Path(args.from_digest).read_text(encoding="utf-8")
        print(f"Loaded digest from {args.from_digest}")
        track_cfg = tracks[0]
        slug = track_cfg["slug"]
        digest_path = output_dir / f"digest-{slug}.md"
        digest_path.write_text(digest, encoding="utf-8")

        if not args.skip_podcast:
            print(f"\nGenerating podcast for {track_cfg['name']}...")
            try:
                result = generate_podcast_track(digest, config, api_key, output_dir, track_cfg)
                print(f"  Audio: {result['audio_path']}")
            except Exception as e:
                print(f"  Podcast generation failed: {e}")
        return

    print("=" * 60)
    print(f"DATABRICKS WEEKLY DIGEST - {date_str}")
    print(f"Tracks: {', '.join(t['name'] for t in tracks)}")
    print("=" * 60)

    print("\n[1] Aggregating content...")
    items = aggregate(config)
    print(f"  Total: {len(items)} items collected")

    if not items:
        print("  No content found. Exiting.")
        sys.exit(0)

    all_results: dict[str, dict] = {}

    for track_cfg in tracks:
        slug = track_cfg["slug"]
        name = track_cfg["name"]
        print(f"\n{'-' * 40}")
        print(f"TRACK: {name}")
        print(f"{'-' * 40}")

        print(f"\n[2/{name}] Generating digest...")
        digest = summarize_track(items, config, api_key, track_cfg)
        digest_path = output_dir / f"digest-{slug}.md"
        digest_path.write_text(digest, encoding="utf-8")
        print(f"  Saved: {digest_path}")

        podcast_result = None
        if not args.skip_podcast:
            print(f"\n[3/{name}] Generating podcast...")
            try:
                podcast_result = generate_podcast_track(digest, config, api_key, output_dir, track_cfg)
            except Exception as e:
                print(f"  Podcast generation failed: {e}")
                print("  Continuing without podcast...")
        else:
            print(f"\n[3/{name}] Podcast skipped")

        all_results[slug] = {
            "digest": digest,
            "digest_path": str(digest_path),
            "podcast": podcast_result,
        }

    if not args.digest_only:
        print("\n[4] Distributing...")
        combined = "\n\n---\n\n".join(
            r["digest"] for r in all_results.values()
        )
        distribute(combined, None, config, date_str)
    else:
        print("\n[4] Distribution skipped")

    print("\n" + "=" * 60)
    print("DONE!")
    print(f"  Output directory: {output_dir}")
    for slug, result in all_results.items():
        print(f"  [{slug}] Digest: {result['digest_path']}")
        if result["podcast"]:
            print(f"  [{slug}] Audio:  {result['podcast']['audio_path']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
