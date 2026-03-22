import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

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

    def send(self, subject: str, body_html: str, attachments: list[Path] | None = None):
        if self.method == "gmail":
            self._send_gmail(subject, body_html, attachments or [])
        elif self.method == "logic_app":
            self._send_logic_app(subject, body_html)
        else:
            raise ValueError(f"Unknown email method: {self.method}")

    def _send_gmail(self, subject: str, body_html: str, attachments: list[Path]):
        msg = MIMEMultipart()
        msg["From"] = self.gmail_user
        msg["To"] = ", ".join(self.recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(body_html, "html"))

        for path in attachments:
            if path.exists():
                part = MIMEBase("application", "octet-stream")
                part.set_payload(path.read_bytes())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={path.name}")
                msg.attach(part)

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
