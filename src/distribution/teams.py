import requests


class TeamsSender:
    """Post digest summary to a Teams channel via incoming webhook."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, title: str, summary: str, links: dict[str, str] | None = None):
        sections = [{
            "activityTitle": title,
            "text": summary,
        }]

        if links:
            actions = [
                {"@type": "OpenUri", "name": name, "targets": [{"os": "default", "uri": url}]}
                for name, url in links.items()
            ]
        else:
            actions = []

        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF3621",
            "summary": title,
            "sections": sections,
            "potentialAction": actions,
        }

        resp = requests.post(self.webhook_url, json=card, timeout=30)
        resp.raise_for_status()
        print(f"  Teams notification sent (status {resp.status_code})")
