from twilio.rest import Client
from app.config import settings

def send_whatsapp(to: str, message: str) -> dict:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    msg = client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        body=message,
        to=f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
    )
    return {"success": True, "sid": msg.sid, "to": to}