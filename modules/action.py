
"""Action Module: Executes containment steps with safety checks."""
import sqlite3, json

def execute_containment(incident_id: int, steps: list, require_approval: bool = True) -> dict:
    """Simulate containment execution (safe for demo)."""
    if require_approval:
        return {"status": "pending_approval", "incident_id": incident_id, "steps": steps}

    # In production: execute actual remediation here
    executed = []
    for step in steps:
        executed.append({"step": step, "status": "simulated", "timestamp": "2026-05-29T00:00:00Z"})

    # Update DB status
    conn = sqlite3.connect("sentinel_memory.db")
    conn.execute("UPDATE incidents SET status = ? WHERE id = ?", ("executed", incident_id))
    conn.commit()
    conn.close()
    return {"status": "executed", "incident_id": incident_id, "results": executed}
