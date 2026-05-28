
from flask import Flask, request, jsonify
from modules.perception import validate_alert
from modules.reasoning import analyze_with_retry
from modules.action import execute_containment
from memory import init_db, save_incident, get_recent_incidents
import json, os

app = Flask(__name__)
init_db()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "agent": "Sentinel Edge", "mode": "edge-cloud-hybrid", "modules": ["perception", "reasoning", "action", "memory"]})

@app.route("/analyze", methods=["POST"])
def analyze_alert():
    data = request.get_json(silent=True)
    if not data or "alert" not in data:
        return jsonify({"error": "Missing 'alert' field"}), 400

    # Perception: validate input
    validated = validate_alert(data["alert"])
    if not validated["valid"]:
        return jsonify({"error": validated["error"]}), 400

    # Add context from memory (Track 1 overlap)
    recent = get_recent_incidents(limit=3)
    context = "\n\nRECENT CONTEXT:\n" + "\n".join([f"- {i['alert_type']} ({i['status']})" for i in recent]) if recent else ""

    # Reasoning: analyze with self-correction
    analysis = analyze_with_retry(validated["text"] + context)

    # Persist to memory
    threat_type = analysis.get("threat_type", "unknown")
    incident_id = save_incident(threat_type, json.dumps(analysis))
    analysis["incident_id"] = incident_id

    # Action: prepare containment (with human-in-loop)
    if "containment_steps" in analysis:
        analysis["action_plan"] = execute_containment(incident_id, analysis["containment_steps"], analysis.get("requires_human_approval", True))

    status = 200 if "error" not in analysis else 503
    return jsonify(analysis), status

@app.route("/incidents", methods=["GET"])
def list_incidents():
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_recent_incidents(limit=limit))

@app.route("/approve/<int:incident_id>", methods=["POST"])
def approve_action(incident_id):
    from modules.action import execute_containment
    # Fetch incident to get steps
    conn = sqlite3.connect("sentinel_memory.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Incident not found"}), 404
    analysis = json.loads(row["analysis"])
    steps = analysis.get("containment_steps", [])
    result = execute_containment(incident_id, steps, require_approval=False)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
