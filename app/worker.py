import time
from app.queue_db import init_db, fetch_next_job, mark_done, mark_failed

def process_job(kind: str, payload: str):
    # plug WhatsApp/calendar/email handlers here
    # for now simulate success
    return True

def run_worker():
    init_db()
    while True:
        job = fetch_next_job()
        if not job:
            time.sleep(2)
            continue

        job_id, kind, payload, retries = job
        try:
            process_job(kind, payload)
            mark_done(job_id)
        except Exception as e:
            mark_failed(job_id, str(e), retries + 1)

if __name__ == "__main__":
    run_worker()