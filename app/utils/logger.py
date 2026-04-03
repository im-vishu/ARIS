import json
import os
from datetime import datetime

LOG_FILE = "logs/aris_actions.log"

def log_event(event_type: str, payload: dict):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")