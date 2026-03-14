"""
Databricks Weekly Digest - Main Entry Point

Usage:
    python run.py                    # Full pipeline: aggregate + summarize + podcast
    python run.py --skip-podcast     # Just the written digest, no audio
    python run.py --digest-only      # Aggregate + summarize, skip distribution
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
        return yaml.safe_load(f)


def aggregate(config: dict) -> list:
    from src.aggregators import BlogAggregator, YouTubeAggregator, ReleasesAggregator

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

    yt_cfg = config["sources"]["youtube"]
    if yt_cfg["enabled"]:
        agg = YouTubeAggregator(yt_cfg["channels"], yt_cfg["max_items_per_channel"])
        all_items.extend(agg.fetch(lookback))

    all_items.sort(key=lambda x: x.published, reverse=True)
    return all_items


def summarize(items: list, config: dict, api_key: str) -> str:
    from src.summarizer import Summarizer
    s = Summarizer(api_key, config["summarizer"]["model"])
    return s.summarize(items, config["summarizer"]["max_digest_items"])


def generate_podcast(digest: str, config: dict, api_key: str, output_dir: Path) -> dict:
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
    return gen.generate(digest, output_dir)


def distribute(digest: str, podcast_result: dict | None, config: dict):
    dist = config["distribution"]

    if dist["email"]["enabled"]:
        from src.distribution import EmailSender
        sender = EmailSender(dist["email"])
        subject = f"Databricks Weekly Digest - {datetime.now().strftime('%b %d, %Y')}"
        sender.send(subject, digest)

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


def main():
    parser = argparse.ArgumentParser(description="Databricks Weekly Digest")
    parser.add_argument("--skip-podcast", action="store_true", help="Skip podcast generation")
    parser.add_argument("--digest-only", action="store_true", help="Skip distribution")
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

    if args.from_digest:
        digest = Path(args.from_digest).read_text(encoding="utf-8")
        print(f"Loaded digest from {args.from_digest}")
    else:
        print("=" * 60)
        print(f"DATABRICKS WEEKLY DIGEST - {date_str}")
        print("=" * 60)

        print("\n[1/4] Aggregating content...")
        items = aggregate(config)
        print(f"  Total: {len(items)} items collected")

        if not items:
            print("  No content found. Exiting.")
            sys.exit(0)

        print("\n[2/4] Generating digest...")
        digest = summarize(items, config, api_key)

    digest_path = output_dir / "digest.md"
    digest_path.write_text(digest, encoding="utf-8")
    print(f"  Digest saved: {digest_path}")

    podcast_result = None
    if not args.skip_podcast:
        print("\n[3/4] Generating podcast...")
        try:
            podcast_result = generate_podcast(digest, config, api_key, output_dir)
        except Exception as e:
            print(f"  Podcast generation failed: {e}")
            print("  Continuing without podcast...")
    else:
        print("\n[3/4] Podcast skipped")

    if not args.digest_only:
        print("\n[4/4] Distributing...")
        distribute(digest, podcast_result, config)
    else:
        print("\n[4/4] Distribution skipped")

    print("\n" + "=" * 60)
    print("DONE!")
    print(f"  Output directory: {output_dir}")
    if podcast_result:
        print(f"  Podcast script:  {podcast_result['dialogue_path']}")
        print(f"  Podcast audio:   {podcast_result['audio_path']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
