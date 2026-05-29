#!/usr/bin/env python3
"""Dashboard Module: Live monitoring metrics for judges."""
import sqlite3, os, platform
from memory import get_recent_incidents

def get_dashboard_data():
    """Return structured dashboard metrics."""
    conn = sqlite3.connect("sentinel_memory.db")
    total = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM incidents WHERE status='pending'").fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM incidents WHERE status='approved'").fetchone()[0]
    conn.close()
    recent = get_recent_incidents(limit=5)
    db_size = os.path.getsize("sentinel_memory.db") // 1024 if os.path.exists("sentinel_memory.db") else 0
    return {
        "agent": "Sentinel Edge",
        "version": "1.0.0",
        "status": "online",
        "mode": "edge-cloud-hybrid",
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "memory_db_size_kb": db_size
        },
        "metrics": {
            "total_incidents": total,
            "pending_approval": pending,
            "executed": approved
        },
        "recent_incidents": [{"id": i["id"], "type": i["alert_type"], "status": i["status"], "timestamp": i["timestamp"]} for i in recent],
        "endpoints": ["/health", "/analyze", "/incidents", "/report/<id>", "/approve/<id>", "/dashboard"],
        "tracks": ["Track 5: EdgeAgent (primary)", "Track 1: MemoryAgent (overlap)", "Track 4: Autopilot Agent (overlap)"]
    }