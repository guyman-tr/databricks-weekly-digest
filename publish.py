"""
Publish a digest episode to the website.

Copies track-specific digests to web/public/episodes/ and uploads audio
files to Cloudflare R2 for CDN delivery. Creates meta.json with R2 audio URLs.

Usage:
    python publish.py                          # Publish latest episode
    python publish.py --date 2026-03-14        # Publish specific date
"""

import argparse
import json
import os
import re
import shutil
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

TRACK_SLUGS = ["de", "analytics"]
TRACK_NAMES = {"de": "Data Engineering", "analytics": "Analytics & Data Science"}


def get_r2_client():
    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")

    if not all([account_id, access_key, secret_key]):
        return None

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def upload_to_r2(client, local_path: Path, r2_key: str) -> str | None:
    bucket = os.environ.get("R2_BUCKET_NAME", "databricksdigest")
    public_url = os.environ.get("R2_PUBLIC_URL", "").rstrip("/")

    if not public_url:
        print(f"  WARNING: R2_PUBLIC_URL not set, audio won't be accessible")
        return None

    content_type = "audio/wav" if local_path.suffix == ".wav" else "audio/mpeg"

    client.upload_file(
        str(local_path),
        bucket,
        r2_key,
        ExtraArgs={"ContentType": content_type},
    )

    url = f"{public_url}/{r2_key}"
    size_mb = local_path.stat().st_size / 1024 / 1024
    print(f"  Uploaded {local_path.name} to R2 ({size_mb:.1f} MB) -> {url}")
    return url


def find_latest_output() -> Path | None:
    output_dir = Path(__file__).parent / "output"
    if not output_dir.exists():
        return None
    dates = sorted(
        [d for d in output_dir.iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name)],
        reverse=True,
    )
    return dates[0] if dates else None


def extract_description(digest_path: Path) -> str:
    text = digest_path.read_text(encoding="utf-8")
    topics = []
    for line in text.split("\n"):
        if line.startswith("### ") and not line.startswith("### Raw"):
            title = re.sub(r"^###\s*\d+\.\s*", "", line).strip()
            title = re.sub(r"\*+", "", title).strip()
            if title and len(topics) < 3:
                topics.append(title)
    return ", ".join(topics) if topics else ""


def count_items(digest_path: Path) -> int:
    text = digest_path.read_text(encoding="utf-8")
    return len(re.findall(r"^### \d+\.", text, re.MULTILINE))


def publish(source_dir: Path):
    date = source_dir.name
    target_dir = Path(__file__).parent / "web" / "public" / "episodes" / date
    target_dir.mkdir(parents=True, exist_ok=True)

    r2_client = get_r2_client()
    if not r2_client:
        print("  WARNING: R2 credentials not configured, skipping audio upload")

    tracks_meta: dict = {}

    for slug in TRACK_SLUGS:
        digest_src = source_dir / f"digest-{slug}.md"
        if not digest_src.exists():
            continue

        shutil.copy2(digest_src, target_dir / f"digest-{slug}.md")
        print(f"  [{slug}] Copied digest-{slug}.md")

        audio_url = None
        for ext in (".wav", ".mp3", ".ogg"):
            audio_src = source_dir / f"podcast-{slug}{ext}"
            if audio_src.exists():
                if r2_client:
                    r2_key = f"episodes/{date}/podcast-{slug}{ext}"
                    audio_url = upload_to_r2(r2_client, audio_src, r2_key)
                else:
                    shutil.copy2(audio_src, target_dir / f"podcast-{slug}{ext}")
                    size_mb = audio_src.stat().st_size / 1024 / 1024
                    print(f"  [{slug}] Copied podcast-{slug}{ext} ({size_mb:.1f} MB)")
                break

        script_src = source_dir / f"podcast_script-{slug}.txt"
        if script_src.exists():
            shutil.copy2(script_src, target_dir / f"podcast_script-{slug}.txt")
            print(f"  [{slug}] Copied podcast_script-{slug}.txt")

        track_meta = {
            "name": TRACK_NAMES.get(slug, slug),
            "itemCount": count_items(digest_src),
            "description": extract_description(digest_src),
        }
        if audio_url:
            track_meta["audioUrl"] = audio_url

        tracks_meta[slug] = track_meta

    if not tracks_meta:
        legacy_digest = source_dir / "digest.md"
        if legacy_digest.exists():
            shutil.copy2(legacy_digest, target_dir / "digest.md")
            print("  Copied legacy digest.md")

    meta = {
        "title": f"Databricks Weekly - {date}",
        "date": date,
        "tracks": tracks_meta,
    }
    meta_path = target_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"  Created meta.json")

    print(f"\nPublished episode {date} to {target_dir}")


def main():
    parser = argparse.ArgumentParser(description="Publish episode to website")
    parser.add_argument("--date", type=str, help="Episode date (YYYY-MM-DD)")
    args = parser.parse_args()

    if args.date:
        source_dir = Path(__file__).parent / "output" / args.date
    else:
        source_dir = find_latest_output()

    if not source_dir or not source_dir.exists():
        print("ERROR: No episode found to publish.")
        print("Run 'python run.py' first to generate an episode.")
        return

    print(f"Publishing episode from {source_dir}...")
    publish(source_dir)


if __name__ == "__main__":
    main()
