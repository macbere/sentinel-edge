import sqlite3
from datetime import datetime

DB_PATH = "sentinel_memory.db"

def init_db():
    """Initialize SQLite database with incidents table."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            analysis TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

def save_incident(alert_type: str, analysis: str) -> int:
    """Save a new incident and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "INSERT INTO incidents (timestamp, alert_type, analysis) VALUES (?, ?, ?)",
        (datetime.utcnow().isoformat(), alert_type, analysis)
    )
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def get_recent_incidents(limit: int = 5) -> list:
    """Retrieve recent incidents for context/memory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        "SELECT * FROM incidents ORDER BY id DESC LIMIT ?", 
        (limit,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
