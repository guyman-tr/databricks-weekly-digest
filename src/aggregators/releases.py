import feedparser
from datetime import datetime, timedelta, timezone
from ..models import ContentItem


class ReleasesAggregator:

    def __init__(self, rss_url: str, max_items: int = 10):
        self.rss_url = rss_url
        self.max_items = max_items

    def fetch(self, lookback_days: int = 7) -> list[ContentItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        try:
            feed = feedparser.parse(self.rss_url)
        except Exception as e:
            print(f"  Releases: FAILED to parse feed - {e}")
            return []

        items = []

        for entry in feed.entries[:self.max_items * 2]:
            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            summary = self._strip_html(entry.get("summary", ""))

            items.append(ContentItem(
                title=entry.get("title", "Untitled"),
                source="Databricks Release Notes",
                url=entry.get("link", ""),
                published=published or datetime.now(timezone.utc),
                summary=summary[:500],
                full_text=summary[:3000],
                source_type="release",
            ))

            if len(items) >= self.max_items:
                break

        print(f"  Releases: fetched {len(items)} items")
        return items

    def _parse_date(self, entry) -> datetime | None:
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                from time import mktime
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
        return None

    @staticmethod
    def _strip_html(text: str) -> str:
        import re
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
