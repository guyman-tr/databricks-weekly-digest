"""
Publish a digest episode to the website.

Copies digest + audio from output/ to web/public/episodes/
and creates the meta.json needed by the website.

Usage:
    python publish.py                          # Publish latest episode
    python publish.py --date 2026-03-14        # Publish specific date
"""

import argparse
import json
import re
import shutil
from pathlib import Path


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
    """Pull a one-line description from the digest's 'Big Ones' or 'What's New' section titles."""
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

    digest_src = source_dir / "digest.md"
    if digest_src.exists():
        shutil.copy2(digest_src, target_dir / "digest.md")
        print(f"  Copied digest.md")

    for ext in (".wav", ".mp3", ".ogg"):
        audio_src = source_dir / f"podcast{ext}"
        if audio_src.exists():
            shutil.copy2(audio_src, target_dir / f"podcast{ext}")
            print(f"  Copied podcast{ext} ({audio_src.stat().st_size / 1024 / 1024:.1f} MB)")
            break

    script_src = source_dir / "podcast_script.txt"
    if script_src.exists():
        shutil.copy2(script_src, target_dir / "podcast_script.txt")
        print(f"  Copied podcast_script.txt")

    meta = {
        "title": f"Databricks Weekly - {date}",
        "date": date,
        "description": extract_description(digest_src) if digest_src.exists() else "",
        "itemCount": count_items(digest_src) if digest_src.exists() else 0,
    }
    meta_path = target_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"  Created meta.json")

    print(f"\nPublished episode {date} to {target_dir}")
    print(f"Now run: cd web && npm run build")


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
