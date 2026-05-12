import os
import sqlite3
import time
from pathlib import Path
from typing import Any


DB_FILE = Path(os.getenv("FIM_DB_FILE", Path(__file__).with_name("events.db")))


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                file TEXT NOT NULL,
                event TEXT NOT NULL,
                severity TEXT NOT NULL,
                time INTEGER NOT NULL,
                hash TEXT,
                size INTEGER
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_time ON events(time)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_event ON events(event)")


def severity_for(event: str, file_path: str) -> str:
    lower_path = file_path.lower()
    critical_markers = ("passwd", "shadow", "sudoers", "authorized_keys", ".env", "web.config")

    if event == "file_deleted":
        return "high"
    if any(marker in lower_path for marker in critical_markers):
        return "critical"
    if event == "file_modified":
        return "medium"
    return "low"


def save_event(agent: str, file_path: str, event: str, file_hash: str | None, size: int | None) -> dict[str, Any]:
    ts = int(time.time())
    severity = severity_for(event, file_path)

    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO events (agent, file, event, severity, time, hash, size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (agent, file_path, event, severity, ts, file_hash, size),
        )
        event_id = cur.lastrowid

    return {
        "id": event_id,
        "agent": agent,
        "file": file_path,
        "event": event,
        "severity": severity,
        "time": ts,
        "hash": file_hash,
        "size": size,
    }


def get_events(limit: int = 200, event: str | None = None, agent: str | None = None) -> list[dict[str, Any]]:
    limit = min(max(limit, 1), 500)
    clauses = []
    params: list[Any] = []

    if event:
        clauses.append("event = ?")
        params.append(event)
    if agent:
        clauses.append("agent = ?")
        params.append(agent)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(
            f"""
            SELECT id, agent, file, event, severity, time, hash, size
            FROM events
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()

    return [dict(row) for row in rows]


def get_stats() -> dict[str, Any]:
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        by_event = conn.execute(
            "SELECT event, COUNT(*) AS count FROM events GROUP BY event ORDER BY count DESC"
        ).fetchall()
        by_severity = conn.execute(
            "SELECT severity, COUNT(*) AS count FROM events GROUP BY severity ORDER BY count DESC"
        ).fetchall()
        recent_agents = conn.execute(
            "SELECT agent, MAX(time) AS last_seen FROM events GROUP BY agent ORDER BY last_seen DESC LIMIT 10"
        ).fetchall()

    return {
        "total": total,
        "by_event": {row["event"]: row["count"] for row in by_event},
        "by_severity": {row["severity"]: row["count"] for row in by_severity},
        "recent_agents": [dict(row) for row in recent_agents],
    }
