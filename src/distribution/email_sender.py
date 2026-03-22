import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import boto3


def load_confirmed_subscribers_from_r2() -> list[str]:
    """Fetch confirmed subscriber emails from R2 subscribers.json."""
    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket = os.environ.get("R2_BUCKET_NAME", "databricksdigest")

    if not all([account_id, access_key, secret_key]):
        print("  R2 credentials not available, cannot load subscribers")
        return []

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    try:
        resp = client.get_object(Bucket=bucket, Key="subscribers.json")
        data = json.loads(resp["Body"].read().decode("utf-8"))
        confirmed = [
            s["email"] for s in data.get("subscribers", [])
            if s.get("status") == "confirmed"
        ]
        print(f"  Loaded {len(confirmed)} confirmed subscribers from R2")
        return confirmed
    except client.exceptions.NoSuchKey:
        print("  No subscribers.json found in R2")
        return []
    except Exception as e:
        print(f"  Failed to load subscribers from R2: {e}")
        return []


class EmailSender:
    """Send digest via Gmail SMTP or Logic App webhook."""

    def __init__(self, config: dict):
        self.method = config.get("method", "gmail")
        self.gmail_user = config.get("gmail_user", "")
        self.gmail_app_password = config.get("gmail_app_password", "")
        self.logic_app_url = config.get("logic_app_url", "")

        static_recipients = config.get("recipients", [])
        r2_subscribers = load_confirmed_subscribers_from_r2()
        all_emails = set(static_recipients) | set(r2_subscribers)
        self.recipients = [e for e in all_emails if e]

    def send(self, subject: str, episode_date: str):
        if not self.recipients:
            print("  No recipients to send to, skipping email")
            return

        site_url = os.environ.get(
            "SITE_URL",
            "https://databricks-weekly-digest-guyman-2003s-projects.vercel.app",
        )
        episode_url = f"{site_url}?episode={episode_date}"
        unsubscribe_url = f"{site_url}/api/unsubscribe"

        html = f"""\
<div style="font-family: -apple-system, system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px;">
  <h2 style="color: #FF3621; margin: 0 0 16px;">Databricks Weekly</h2>
  <p style="color: #333; line-height: 1.6;">
    This week's digest is ready &mdash; covering the latest Databricks releases,
    blog posts, and community highlights.
  </p>
  <a href="{episode_url}"
     style="display: inline-block; margin: 24px 0; padding: 12px 28px;
            background: #FF3621; color: white; text-decoration: none;
            border-radius: 8px; font-weight: 600;">
    Read This Week's Digest
  </a>
  <p style="color: #888; font-size: 13px; line-height: 1.5;">
    You're receiving this because you subscribed at
    <a href="{site_url}" style="color: #888;">{site_url}</a>.<br/>
    <a href="{unsubscribe_url}" style="color: #888;">Unsubscribe</a>
  </p>
</div>"""

        if self.method == "gmail":
            self._send_gmail(subject, html)
        elif self.method == "logic_app":
            self._send_logic_app(subject, html)
        else:
            raise ValueError(f"Unknown email method: {self.method}")

    def _send_gmail(self, subject: str, body_html: str):
        msg = MIMEMultipart("alternative")
        msg["From"] = f'"Databricks Weekly" <{self.gmail_user}>'
        msg["To"] = ", ".join(self.recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.gmail_user, self.gmail_app_password)
            server.sendmail(self.gmail_user, self.recipients, msg.as_string())

        print(f"  Email sent to {len(self.recipients)} recipients via Gmail")

    def _send_logic_app(self, subject: str, body_html: str):
        import requests
        payload = {
            "subject": subject,
            "body": body_html,
            "recipients": self.recipients,
        }
        resp = requests.post(self.logic_app_url, json=payload, timeout=30)
        resp.raise_for_status()
        print(f"  Email sent via Logic App (status {resp.status_code})")
