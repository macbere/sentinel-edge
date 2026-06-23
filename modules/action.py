"""
Action Module: Containment Execution with Human-in-the-Loop
Handles approval workflow and containment plan execution.
"""
import sqlite3
import json
from datetime import datetime


def execute_containment(incident_id, containment_steps, require_approval=True):
    """
    Execute or queue containment actions for an incident.
    If require_approval=True, marks as pending_approval.
    If require_approval=False, marks as executed immediately.
    """
    conn = sqlite3.connect("sentinel_memory.db")

    if require_approval:
        conn.execute(
            "UPDATE incidents SET status = ? WHERE id = ?",
            ("pending", incident_id)
        )
        conn.commit()
        conn.close()
        return {
            "incident_id": incident_id,
            "status": "pending_approval",
            "steps": containment_steps,
            "message": "Awaiting human approval before execution",
            "requires_approval": True,
            "queued_at": datetime.now().isoformat() + "Z"
        }
    else:
        execution_log = []
        for i, step in enumerate(containment_steps):
            execution_log.append({
                "step": i + 1,
                "action": step,
                "status": "executed",
                "executed_at": datetime.now().isoformat() + "Z"
            })

        conn.execute(
            "UPDATE incidents SET status = ? WHERE id = ?",
            ("executed", incident_id)
        )
        conn.commit()
        conn.close()

        return {
            "incident_id": incident_id,
            "status": "executed",
            "steps": containment_steps,
            "execution_log": execution_log,
            "executed_at": datetime.now().isoformat() + "Z",
            "message": f"Successfully executed {len(containment_steps)} containment actions"
        }


def approve_and_execute(incident_id):
    """
    Approve a pending incident and execute its containment steps.
    Called when human clicks Approve in the dashboard.
    """
    conn = sqlite3.connect("sentinel_memory.db")
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        "SELECT * FROM incidents WHERE id = ?",
        (incident_id,)
    ).fetchone()
    conn.close()

    if not row:
        return {"error": "Incident not found", "incident_id": incident_id}

    try:
        analysis = json.loads(row["analysis"])
    except Exception:
        return {"error": "Could not parse incident analysis", "incident_id": incident_id}

    containment_steps = analysis.get("containment_steps", [])

    if not containment_steps:
        containment_steps = ["Review and monitor the incident", "Document findings"]

    return execute_containment(incident_id, containment_steps, require_approval=False)


def get_incident_status(incident_id):
    """Get current status of an incident."""
    conn = sqlite3.connect("sentinel_memory.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT id, status, timestamp, alert_type FROM incidents WHERE id = ?",
        (incident_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    return {
        "incident_id": row["id"],
        "status": row["status"],
        "timestamp": row["timestamp"],
        "alert_type": row["alert_type"]
    }
