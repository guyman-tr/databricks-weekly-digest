import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


class EmailSender:
    """Send digest via Gmail SMTP or Logic App webhook."""

    def __init__(self, config: dict):
        self.method = config.get("method", "gmail")
        self.gmail_user = config.get("gmail_user", "")
        self.gmail_app_password = config.get("gmail_app_password", "")
        self.recipients = config.get("recipients", [])
        self.logic_app_url = config.get("logic_app_url", "")

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
