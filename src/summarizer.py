from google import genai
from google.genai import types
from .models import ContentItem


TRACK_DIGEST_PROMPT = """You are a senior Databricks platform engineer creating a weekly digest.
This digest is for the **{track_name}** audience.

TRACK FOCUS: {track_focus}

Below is raw content collected this week from the Databricks blog, YouTube channels, release notes,
and roadmap/preview announcements.
Select the {max_items} most relevant items for {track_name} practitioners.

RULES:
- ONLY include items relevant to {track_name}: {track_focus}
- Skip items that clearly belong to a different audience
- Items touching multiple areas should be analyzed from the {track_name} perspective
- For preview/roadmap items (source_type = "roadmap"), note they are in preview
- Explain WHY each item matters to {track_name} practitioners specifically
- Be opinionated -- if something is a big deal, say so
- Group related items together

OUTPUT FORMAT (markdown):
# Databricks Weekly: {track_name} - {date_range}

## The Big Ones
[1-2 items that are genuinely important this week for {track_name}, if any exist. Skip this section if nothing stands out.]

## What's New
[3-5 items covering new features, releases, announcements relevant to {track_name}]

## Worth Knowing
[1-3 items that are useful but not urgent -- tips, community content, minor updates]

For each item use this structure:
### N. **Item Title**
**Source:** [Source Name](URL)
**Why it matters:** Clear explanation of impact for {track_name} practitioners.

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

    def summarize(
        self,
        items: list[ContentItem],
        max_items: int = 7,
        track_name: str | None = None,
        track_focus: str | None = None,
    ) -> str:
        if not items:
            label = track_name or "General"
            return f"# Databricks Weekly: {label}\n\nNo new content found this week."

        content_block = self._format_items(items)

        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=7)
        date_range = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"

        prompt = TRACK_DIGEST_PROMPT.format(
            track_name=track_name or "General",
            track_focus=track_focus or "all Databricks developments",
            max_items=max_items,
            date_range=date_range,
            content=content_block,
        )

        label = track_name or "General"
        print(f"  [{label}] Summarizing {len(items)} items with {self.model}...")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4000,
            ),
        )

        digest = response.text
        print(f"  [{label}] Digest generated ({len(digest)} chars)")
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
Tags: {', '.join(item.tags) if item.tags else 'none'}
Summary: {item.summary}
Content: {item.full_text[:2000]}
"""
            blocks.append(block)
        return "\n".join(blocks)
