import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def _get_creds():
    token_path = "credentials/token.json"
    cred_path = "credentials/google_credentials.json"
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
        creds = flow.run_local_server(port=0)
        os.makedirs("credentials", exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds

def create_calendar_event(summary: str, start_iso: str, end_iso: str, timezone: str) -> dict:
    creds = _get_creds()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": summary,
        "start": {"dateTime": start_iso, "timeZone": timezone},
        "end": {"dateTime": end_iso, "timeZone": timezone},
    }

    created = service.events().insert(
        calendarId=settings.GOOGLE_CALENDAR_ID,
        body=event
    ).execute()

    return {"success": True, "id": created["id"], "htmlLink": created.get("htmlLink", "")}