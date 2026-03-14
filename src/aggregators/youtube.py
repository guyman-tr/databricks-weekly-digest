import feedparser
import requests
from datetime import datetime, timedelta, timezone
from ..models import ContentItem


class YouTubeAggregator:

    FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def __init__(self, channels: list[dict], max_items_per_channel: int = 5):
        self.channels = channels
        self.max_per_channel = max_items_per_channel

    def fetch(self, lookback_days: int = 7) -> list[ContentItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        all_items = []

        for channel in self.channels:
            channel_name = channel["name"]
            channel_id = channel["channel_id"]
            try:
                items = self._fetch_channel(channel_name, channel_id, cutoff)
                all_items.extend(items)
                print(f"  YouTube/{channel_name}: fetched {len(items)} videos")
            except Exception as e:
                print(f"  YouTube/{channel_name}: FAILED - {e}")

        return all_items

    def _fetch_channel(self, channel_name: str, channel_id: str, cutoff: datetime) -> list[ContentItem]:
        feed_url = self.FEED_URL.format(channel_id=channel_id)
        feed = feedparser.parse(feed_url)
        items = []

        for entry in feed.entries:
            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            video_id = self._extract_video_id(entry)
            transcript = self._get_transcript(video_id) if video_id else ""

            items.append(ContentItem(
                title=entry.get("title", "Untitled"),
                source=f"YouTube/{channel_name}",
                url=entry.get("link", ""),
                published=published or datetime.now(timezone.utc),
                summary=entry.get("summary", "")[:500],
                full_text=transcript[:5000] if transcript else entry.get("summary", "")[:1000],
                source_type="youtube",
            ))

            if len(items) >= self.max_per_channel:
                break

        return items

    def _get_transcript(self, video_id: str) -> str:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            return " ".join(segment["text"] for segment in transcript_list)
        except Exception:
            return ""

    @staticmethod
    def _extract_video_id(entry) -> str | None:
        link = entry.get("link", "")
        if "v=" in link:
            return link.split("v=")[-1].split("&")[0]
        yt_id = entry.get("yt_videoid")
        if yt_id:
            return yt_id
        return None

    def _parse_date(self, entry) -> datetime | None:
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                from time import mktime
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
        return None
