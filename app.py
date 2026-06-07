from flask import Flask, request, jsonify
from modules.perception import validate_alert
from modules.reasoning import analyze_with_retry
from modules.action import execute_containment
from modules.dashboard import get_dashboard_data
from modules.security import check_rate_limit, sanitize_alert, validate_analyze_payload
from memory import init_db, save_incident, get_recent_incidents
import json
import os
import sqlite3

app = Flask(__name__)
init_db()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "agent": "Sentinel Edge", "mode": "edge-cloud-hybrid", "modules": ["perception", "reasoning", "action", "memory"]})

@app.route("/analyze", methods=["POST"])
def analyze_alert():
    # Rate limiting
    client_ip = request.remote_addr or "unknown"
    if not check_rate_limit(client_ip):
        return jsonify({"error": "Rate limit exceeded. Max 30 requests/min."}), 429
    
    # Payload validation
    data = request.get_json(silent=True)
    is_valid, err_msg = validate_analyze_payload(data)
    if not is_valid:
        return jsonify({"error": err_msg}), 400
    
    # Input sanitization
    data["alert"] = sanitize_alert(data["alert"])
    
    validated = validate_alert(data["alert"])
    if not validated["valid"]:
        return jsonify({"error": validated["error"]}), 400
    recent = get_recent_incidents(limit=3)
    context = "\n\nRECENT CONTEXT:\n" + "\n".join([f"- {i['alert_type']} ({i['status']})" for i in recent]) if recent else ""
    analysis = analyze_with_retry(validated["text"] + context)
    threat_type = analysis.get("threat_type", "unknown")
    incident_id = save_incident(threat_type, json.dumps(analysis))
    analysis["incident_id"] = incident_id
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

@app.route("/report/<int:incident_id>", methods=["GET"])
def generate_report(incident_id):
    conn = sqlite3.connect("sentinel_memory.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Incident not found"}), 404
    analysis = json.loads(row["analysis"])
    similar = []
    threat = analysis.get("threat_type", "")
    if threat and threat != "unknown":
        conn2 = sqlite3.connect("sentinel_memory.db")
        conn2.row_factory = sqlite3.Row
        params = [f"%{threat}%"] * 2
        cursor = conn2.execute("SELECT * FROM incidents WHERE alert_type LIKE ? OR analysis LIKE ? ORDER BY id DESC LIMIT 2", params)
        similar = [{"id": r["id"], "type": r["alert_type"]} for r in cursor.fetchall()]
        conn2.close()
    report_text = "SENTINEL EDGE FORENSIC REPORT\n" + "="*40 + "\n"
    report_text += f"Incident ID: {row['id']} | Timestamp: {row['timestamp']}\n"
    report_text += f"Alert: {row['alert_type']} | Severity: {analysis.get('severity', 'N/A')}\n"
    report_text += f"Threat: {analysis.get('threat_type', 'N/A')} | Confidence: {analysis.get('confidence', 'N/A')}\n"
    report_text += f"Reasoning: {analysis.get('reasoning', 'N/A')}\n"
    report_text += "Containment Steps:\n" + "\n".join([f"  * {s}" for s in analysis.get("containment_steps", [])]) + "\n"
    report_text += f"Human Approval: {analysis.get('requires_human_approval', 'N/A')}\n"
    report_text += f"Similar Past Incidents: {len(similar)}\n"
    return jsonify({"incident_id": row["id"], "timestamp": row["timestamp"], "alert_type": row["alert_type"], "analysis": analysis, "similar_incidents": similar, "report_text": report_text})

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify(get_dashboard_data())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
