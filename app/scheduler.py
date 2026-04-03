import json
import os
import threading
import time
from datetime import datetime

REMINDER_FILE = "data/reminders.json"

def _load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []
    with open(REMINDER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_reminders(items):
    os.makedirs("data", exist_ok=True)
    with open(REMINDER_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

def reminder_loop():
    while True:
        try:
            reminders = _load_reminders()
            now = datetime.now()

            changed = False
            for r in reminders:
                if r.get("done"):
                    continue
                when = datetime.fromisoformat(r["when"])
                if now >= when:
                    print(f"\n🔔 [REMINDER] {r['title']} (due: {r['when']})\nYou: ", end="")
                    r["done"] = True
                    changed = True

            if changed:
                _save_reminders(reminders)

        except Exception as e:
            print(f"\n[Scheduler Error] {e}\n")

        time.sleep(15)

def start_scheduler():
    t = threading.Thread(target=reminder_loop, daemon=True)
    t.start()