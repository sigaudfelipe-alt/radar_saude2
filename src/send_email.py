"""Send the weekly newsletter via email using SMTP.

This module defines a simple function to send the newsletter's Markdown
content to a list of recipients. It assumes the presence of environment
variables for SMTP credentials. To use it, set up environment variables
EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_SMTP_USER, and EMAIL_SMTP_PASS.
"""

import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from typing import List


def send_newsletter_email(md_path: str, to_list: List[str]) -> None:
    """Read the Markdown file and send it via SMTP to recipients."""
    body_md = Path(md_path).read_text(encoding="utf-8")

    from_addr = os.environ.get("EMAIL_SMTP_USER")
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER")
    smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
    smtp_pass = os.environ.get("EMAIL_SMTP_PASS")
    if not (from_addr and smtp_server and smtp_pass):
        raise EnvironmentError(
            "Missing SMTP configuration. Please set EMAIL_SMTP_USER, EMAIL_SMTP_SERVER, and EMAIL_SMTP_PASS."
        )

    subject = f"[Radar Saúde] {Path(md_path).stem.replace('newsletter-', '').replace('-', '/')}"
    msg = MIMEText(body_md, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_list)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_addr, smtp_pass)
        server.sendmail(from_addr, to_list, msg.as_string())


if __name__ == "__main__":
    # Send a simple test email when executed directly
    md_file = "output/newsletter-demo.md"
    Path(md_file).write_text("Teste de envio Radar Saúde", encoding="utf-8")
    send_newsletter_email(md_path=md_file, to_list=["seuemail@empresa.com"])