from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ContentItem:
    title: str
    source: str
    url: str
    published: datetime
    summary: str = ""
    full_text: str = ""
    source_type: str = ""  # "blog", "youtube", "release"
    tags: list[str] = field(default_factory=list)

    def __str__(self):
        date_str = self.published.strftime("%Y-%m-%d")
        return f"[{self.source_type}] {self.title} ({self.source}, {date_str})"
