class ConfluencePublisher:
    """Publish digest as a Confluence page.

    Designed to work with the Atlassian MCP tools available in Cursor,
    or standalone via the Confluence REST API.
    """

    def __init__(self, cloud_id: str, space_id: str, parent_page_id: str):
        self.cloud_id = cloud_id
        self.space_id = space_id
        self.parent_page_id = parent_page_id

    def publish(self, title: str, body_markdown: str) -> str:
        """Publish a digest page. Returns page URL.

        For now, this is a stub. Wire up via:
        - Atlassian MCP (createConfluencePage) when running from Cursor
        - Confluence REST API when running headless/cron
        """
        print(f"  [STUB] Would publish to Confluence: {title}")
        print(f"  Space: {self.space_id}, Parent: {self.parent_page_id}")
        print(f"  Body length: {len(body_markdown)} chars")
        return ""
