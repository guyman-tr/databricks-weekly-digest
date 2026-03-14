import feedparser
from datetime import datetime, timedelta, timezone
from ..models import ContentItem


class BlogAggregator:

    def __init__(self, rss_url: str, max_items: int = 15):
        self.rss_url = rss_url
        self.max_items = max_items

    def fetch(self, lookback_days: int = 7) -> list[ContentItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        feed = feedparser.parse(self.rss_url)
        items = []

        for entry in feed.entries[:self.max_items * 2]:
            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            summary = entry.get("summary", "")
            if hasattr(entry, "content"):
                full_text = entry.content[0].get("value", summary)
            else:
                full_text = summary

            # Strip HTML tags for cleaner text
            full_text = self._strip_html(full_text)
            summary = self._strip_html(summary)

            items.append(ContentItem(
                title=entry.get("title", "Untitled"),
                source="Databricks Blog",
                url=entry.get("link", ""),
                published=published or datetime.now(timezone.utc),
                summary=summary[:500],
                full_text=full_text[:3000],
                source_type="blog",
                tags=[t.get("term", "") for t in entry.get("tags", [])],
            ))

            if len(items) >= self.max_items:
                break

        print(f"  Blog: fetched {len(items)} posts")
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
