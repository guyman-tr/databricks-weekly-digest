from google import genai
from google.genai import types
from .models import ContentItem


DIGEST_PROMPT = """You are a senior Databricks platform engineer creating a weekly digest for your data engineering team.

Below is raw content collected this week from the Databricks blog, YouTube channels, and release notes.
Create a structured digest with the {max_items} most important items.

RULES:
- Focus on things that MATTER to a data engineering team: new features they can use, breaking changes, performance improvements, best practices
- Skip marketing fluff, customer stories, and executive interviews unless they contain real technical substance
- For each item, explain WHY it matters to the team, not just WHAT it is
- Be opinionated -- if something is a big deal, say so
- Group related items together (e.g., multiple Unity Catalog updates become one item)

OUTPUT FORMAT (markdown):
# Databricks Weekly Digest - {date_range}

## The Big Ones
[1-2 items that are genuinely important this week, if any exist. Skip this section if nothing stands out.]

## What's New
[3-5 items covering new features, releases, announcements]

## Worth Knowing
[1-3 items that are useful but not urgent -- tips, community content, minor updates]

## Raw Sources
[Bulleted list of all source URLs for reference]

---
RAW CONTENT:

{content}
"""


class Summarizer:

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def summarize(self, items: list[ContentItem], max_items: int = 7) -> str:
        if not items:
            return "# Databricks Weekly Digest\n\nNo new content found this week."

        content_block = self._format_items(items)

        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=7)
        date_range = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"

        prompt = DIGEST_PROMPT.format(
            max_items=max_items,
            date_range=date_range,
            content=content_block,
        )

        print(f"  Summarizing {len(items)} items with {self.model}...")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4000,
            ),
        )

        digest = response.text
        print(f"  Digest generated ({len(digest)} chars)")
        return digest

    @staticmethod
    def _format_items(items: list[ContentItem]) -> str:
        blocks = []
        for i, item in enumerate(items, 1):
            block = f"""--- Item {i} ---
Type: {item.source_type}
Source: {item.source}
Title: {item.title}
URL: {item.url}
Date: {item.published.strftime('%Y-%m-%d')}
Summary: {item.summary}
Content: {item.full_text[:2000]}
"""
            blocks.append(block)
        return "\n".join(blocks)
