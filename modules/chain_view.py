"""
AI Decision Chain View Module
Provides structured chain data for visual display
"""
import sqlite3
import json
from datetime import datetime


def get_chain_view(incident_id):
    """Get full AI decision chain for an incident."""
    conn = sqlite3.connect("sentinel_memory.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    try:
        analysis = json.loads(row["analysis"])
    except Exception:
        return None

    chain = analysis.get("reasoning_chain", [])
    mcp = analysis.get("mcp_enrichment")
    iocs = analysis.get("iocs", {})

    steps = []

    # Step 0: Alert Ingestion
    steps.append({
        "step": 0,
        "module": "Perception",
        "name": "Alert Ingestion",
        "icon": "🔍",
        "status": "completed",
        "output": {
            "alert": row["alert_type"],
            "iocs_extracted": {k: v for k, v in iocs.items() if v},
            "timestamp": row["timestamp"]
        },
        "color": "blue"
    })

    # Steps from reasoning chain
    color_map = {
        1: "purple",
        2: "indigo",
        3: "violet",
        4: "green",
        "mcp": "cyan"
    }

    icon_map = {
        1: "🧠",
        2: "🔧",
        3: "📋",
        4: "✅",
        "mcp": "🔌"
    }

    for item in chain:
        step_num = item.get("step")
        steps.append({
            "step": step_num,
            "module": "Qwen AI" if step_num != "mcp" else "AbuseIPDB MCP",
            "name": item.get("name", ""),
            "icon": icon_map.get(step_num, "⚡"),
            "status": "completed",
            "output": item.get("output", {}),
            "elapsed_ms": item.get("elapsed_ms", 0),
            "color": color_map.get(step_num, "gray")
        })

    # Campaign Correlation Step
    steps.append({
        "step": "correlation",
        "module": "Correlation Engine",
        "name": "Campaign Correlation",
        "icon": "🎯",
        "status": "completed",
        "output": {
            "info": "Incident analyzed against historical patterns",
            "incident_id": incident_id
        },
        "color": "orange"
    })

    # Human Approval Step
    approval_status = "pending" if row["status"] == "pending" else "approved"
    steps.append({
        "step": "approval",
        "module": "Human-in-the-Loop",
        "name": "Human Approval Gate",
        "icon": "👤",
        "status": approval_status,
        "output": {
            "requires_approval": analysis.get("requires_human_approval", True),
            "current_status": row["status"],
            "severity": analysis.get("severity", "unknown")
        },
        "color": "yellow"
    })

    # Containment Step
    containment_steps = analysis.get("containment_steps", [])
    steps.append({
        "step": "containment",
        "module": "Action Module",
        "name": "Containment Plan",
        "icon": "🛡️",
        "status": "ready" if row["status"] == "pending" else "executed",
        "output": {
            "steps": containment_steps,
            "count": len(containment_steps)
        },
        "color": "red"
    })

    return {
        "incident_id": incident_id,
        "alert": row["alert_type"],
        "timestamp": row["timestamp"],
        "status": row["status"],
        "threat_type": analysis.get("threat_type", "unknown"),
        "severity": analysis.get("severity", "unknown"),
        "confidence": analysis.get("confidence", 0),
        "provider": analysis.get("provider", "unknown"),
        "total_elapsed_ms": analysis.get("total_chain_elapsed_ms", 0),
        "mcp_enrichment": mcp,
        "chain_steps": steps
    }
