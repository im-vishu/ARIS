import json
import os
from datetime import datetime

REMINDER_FILE = "data/reminders.json"

def _load():
    if not os.path.exists(REMINDER_FILE):
        return []
    with open(REMINDER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(items):
    os.makedirs("data", exist_ok=True)
    with open(REMINDER_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

def create_reminder(title: str, when_iso: str) -> dict:
    reminders = _load()
    item = {
        "id": len(reminders) + 1,
        "title": title,
        "when": when_iso,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "done": False
    }
    reminders.append(item)
    _save(reminders)
    return {"success": True, "reminder": item}