import sqlite3
import os
import time
from typing import List, Dict

DB_FILE = os.path.join(os.path.dirname(__file__), "events.db")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            file TEXT,
            event TEXT,
            time INTEGER
        )
    """)
    conn.commit()
    conn.close()


def save_event(agent: str, file_path: str, event: str):
    """Insert event with epoch time (seconds)."""
    ts = int(time.time())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (agent, file, event, time) VALUES (?, ?, ?, ?)",
        (agent, file_path, event, ts)
    )
    conn.commit()
    conn.close()


def get_events(limit: int = 200) -> List[Dict]:
    """Return latest events as list of dicts (most recent first)."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT agent, file, event, time FROM events ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({
            "agent": r[0],
            "file": r[1],
            "event": r[2],
            "time": r[3]  # epoch seconds; frontend will format
        })
    return out
