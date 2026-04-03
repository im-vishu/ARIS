import smtplib
from email.message import EmailMessage
from app.config import settings

def send_email(to: str, subject: str, body: str) -> dict:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT)) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)

    return {"success": True, "to": to, "subject": subject}