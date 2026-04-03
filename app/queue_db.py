import sqlite3
from contextlib import contextmanager

DB_PATH = "data/aris_queue.db"

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            retries INTEGER NOT NULL DEFAULT 0,
            last_error TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

def enqueue(kind: str, payload: str):
    with get_conn() as c:
        c.execute("INSERT INTO jobs (kind, payload) VALUES (?, ?)", (kind, payload))

def fetch_next_job():
    with get_conn() as c:
        row = c.execute(
            "SELECT id, kind, payload, retries FROM jobs WHERE status='pending' ORDER BY id LIMIT 1"
        ).fetchone()
        if row:
            c.execute("UPDATE jobs SET status='processing' WHERE id=?", (row[0],))
        return row

def mark_done(job_id: int):
    with get_conn() as c:
        c.execute("UPDATE jobs SET status='done' WHERE id=?", (job_id,))

def mark_failed(job_id: int, error: str, retries: int, max_retries: int = 3):
    new_status = "pending" if retries < max_retries else "failed"
    with get_conn() as c:
        c.execute(
            "UPDATE jobs SET status=?, retries=?, last_error=? WHERE id=?",
            (new_status, retries, error[:1000], job_id),
        )