import re
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from ..models import ContentItem


class RoadmapAggregator:
    """Captures preview/upcoming/announced features from Databricks docs and release notes."""

    PREVIEW_KEYWORDS = [
        "public preview", "private preview", "coming soon",
        "gated preview", "beta", "upcoming",
    ]

    def __init__(
        self,
        urls: list[str] | None = None,
        release_rss: str | None = None,
        max_items: int = 10,
    ):
        self.urls = urls or []
        self.release_rss = release_rss
        self.max_items = max_items

    def fetch(self, lookback_days: int = 7) -> list[ContentItem]:
        items: list[ContentItem] = []

        if self.release_rss:
            items.extend(self._fetch_preview_from_rss(lookback_days))

        for url in self.urls:
            try:
                items.extend(self._scrape_page(url))
            except Exception as e:
                print(f"  Roadmap/{url}: FAILED - {e}")

        items = items[: self.max_items]
        print(f"  Roadmap: fetched {len(items)} preview/upcoming items")
        return items

    def _fetch_preview_from_rss(self, lookback_days: int) -> list[ContentItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        try:
            feed = feedparser.parse(self.release_rss)
        except Exception as e:
            print(f"  Roadmap/RSS: FAILED - {e}")
            return []

        items: list[ContentItem] = []
        for entry in feed.entries[:50]:
            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            text = self._strip_html(entry.get("summary", ""))
            title = entry.get("title", "")
            combined = f"{title} {text}".lower()

            if not any(kw in combined for kw in self.PREVIEW_KEYWORDS):
                continue

            items.append(ContentItem(
                title=title or "Untitled",
                source="Databricks Roadmap",
                url=entry.get("link", ""),
                published=published or datetime.now(timezone.utc),
                summary=text[:500],
                full_text=text[:3000],
                source_type="roadmap",
                tags=["preview"],
            ))

        return items

    def _scrape_page(self, url: str) -> list[ContentItem]:
        resp = requests.get(
            url, timeout=15,
            headers={"User-Agent": "DatabricksWeeklyDigest/1.0"},
        )
        resp.raise_for_status()
        text = self._strip_html(resp.text)

        sentences = re.split(r"(?<=[.!?])\s+", text)
        preview_chunks = [
            s.strip() for s in sentences
            if any(kw in s.lower() for kw in self.PREVIEW_KEYWORDS)
        ]

        if not preview_chunks:
            return []

        combined = " ".join(preview_chunks)
        return [ContentItem(
            title="Upcoming Features & Previews",
            source="Databricks Roadmap",
            url=url,
            published=datetime.now(timezone.utc),
            summary=combined[:500],
            full_text=combined[:5000],
            source_type="roadmap",
            tags=["preview", "roadmap"],
        )]

    def _parse_date(self, entry) -> datetime | None:
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                from time import mktime
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
        return None

    @staticmethod
    def _strip_html(text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
