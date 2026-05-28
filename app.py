from flask import Flask, request, jsonify
from qwen_client import ask_qwen
from memory import init_db, save_incident, get_recent_incidents
import json

app = Flask(__name__)

# Initialize database on startup
init_db()

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "online",
        "agent": "Sentinel Edge",
        "mode": "edge-cloud-hybrid"
    })

@app.route("/analyze", methods=["POST"])
def analyze_alert():
    """Analyze a cybersecurity alert using Qwen + persist to memory."""
    data = request.get_json(silent=True)
    if not data or "alert" not in data:
        return jsonify({"error": "Missing 'alert' field in JSON body"}), 400

    alert_text = data["alert"]
    
    # Include recent incidents as context for better analysis (MemoryAgent overlap)
    recent = get_recent_incidents(limit=3)
    context = ""
    if recent:
        context = "\n\nRECENT INCIDENT CONTEXT:\n" + "\n".join(
            [f"- {i['timestamp']}: {i['alert_type']} ({i['status']})" for i in recent]
        )

    full_prompt = f"ALERT TO ANALYZE:\n{alert_text}{context}"
    
    # Get AI analysis (with offline fallback built-in)
    result = ask_qwen(full_prompt)
    
    # Persist to memory regardless of online/offline status
    threat_type = result.get("threat_type", "unknown")
    incident_id = save_incident(threat_type, json.dumps(result))
    result["incident_id"] = incident_id
    
    status_code = 200 if "error" not in result else 503
    return jsonify(result), status_code

@app.route("/incidents", methods=["GET"])
def list_incidents():
    """Retrieve recent incidents from persistent memory."""
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_recent_incidents(limit=limit))

@app.route("/approve/<int:incident_id>", methods=["POST"])
def approve_action(incident_id):
    """Human-in-the-loop approval checkpoint (Track 4 Autopilot overlap)."""
    # In production, this would trigger actual remediation
    # For hackathon demo, we just update status
    import sqlite3
    conn = sqlite3.connect("sentinel_memory.db")
    conn.execute("UPDATE incidents SET status = 'approved' WHERE id = ?", (incident_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Incident {incident_id} approved by human operator"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
