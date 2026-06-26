from flask import Flask, request, jsonify
from modules.perception import validate_alert
from modules.reasoning import analyze_with_retry
from modules.action import execute_containment
from modules.dashboard import get_dashboard_data
from modules.security import check_rate_limit, sanitize_alert, validate_analyze_payload
from modules.audit import log_request, log_security_event, get_audit_summary
from modules.correlation import correlation_engine
from modules.correlation import correlation_engine
import time
import uuid
from memory import init_db, save_incident, get_recent_incidents
import json
import os
import sqlite3

app = Flask(__name__)
init_db()


@app.before_request
def before_request():
    """Start timing request and assign request ID."""
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())


@app.after_request
def after_request(response):
    """Log request after completion."""
    if hasattr(request, 'start_time'):
        duration_ms = (time.time() - request.start_time) * 1000
        log_request(request, response, duration_ms)
    return response


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
    analysis = analyze_with_retry(validated["text"])  # Pass clean alert only, context pollutes keyword matching
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
    from modules.action import approve_and_execute
    result = approve_and_execute(incident_id)
    if "error" in result:
        return jsonify(result), 404
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


@app.route("/audit", methods=["GET"])
def audit_summary():
    """Get audit log summary for monitoring."""
    hours = request.args.get('hours', 24, type=int)
    summary = get_audit_summary(hours)
    return jsonify({
        "status": "success",
        "period_hours": hours,
        "summary": summary
    })



@app.route("/correlate", methods=["GET"])
def get_correlations():
    hours = request.args.get('hours', 24, type=int)
    campaigns = correlation_engine.correlate_incidents(hours)
    return jsonify({"status": "success", "period_hours": hours, "campaigns_detected": len(campaigns), "campaigns": campaigns})


@app.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify(get_dashboard_data())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

@app.route("/", methods=["GET"])
def index():
    from flask import render_template
    return render_template("index.html")


@app.route("/chain/<int:incident_id>", methods=["GET"])
def chain_view(incident_id):
    from modules.chain_view import get_chain_view
    data = get_chain_view(incident_id)
    if not data:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify(data)


@app.route("/chain/view/<int:incident_id>", methods=["GET"])
def chain_view_page(incident_id):
    from flask import render_template
    return render_template("chain.html")


@app.route("/qwen", methods=["GET"])
def qwen_page():
    from flask import render_template
    return render_template("qwen.html")


@app.route("/demo", methods=["GET"])
def demo_page():
    from flask import render_template
    return render_template("demo.html")


@app.route("/demo/run", methods=["POST"])
def demo_run():
    import json as _json
    scenario = request.get_json(silent=True) or {}
    scenario_type = scenario.get("scenario", "ransomware")

    scenarios = {
        "ransomware": "Critical ransomware beacon detected from Tor exit node 185.220.101.45 targeting finance-db server — encryption started on 2847 files",
        "phishing": "Spear phishing email from spoofed domain payroll-update.net targeting HR director sarah.johnson with malicious PDF attachment Q4_Salary_Adjustment.pdf",
        "insider": "Insider threat detected — employee james.wilson downloaded 8.3GB proprietary source code to personal USB drive at 2:47 AM outside business hours",
        "malware": "Malware execution detected — trojan svchost32.exe installed via malicious Word macro in finance_report_q3.docm sent to accounting team",
        "credential": "Credential theft — 247 brute force SSH attempts from 185.220.101.45 followed by successful unauthorized login to finance-db-server admin account",
        "exfiltration": "Data exfiltration alert — 4.7GB of encrypted financial records being transferred to C2 server 91.108.56.130 via HTTPS port 443"
    }

    alert = scenarios.get(scenario_type, scenarios["ransomware"])

    from modules.reasoning import analyze_with_chain
    from memory import save_incident
    from modules.action import execute_containment

    analysis = analyze_with_chain(alert)
    threat_type = analysis.get("threat_type", "unknown")
    incident_id = save_incident(threat_type, _json.dumps(analysis))
    analysis["incident_id"] = incident_id

    if "containment_steps" in analysis:
        execute_containment(incident_id, analysis["containment_steps"], analysis.get("requires_human_approval", True))

    return _json.dumps({
        "success": True,
        "incident_id": incident_id,
        "scenario": scenario_type,
        "alert": alert,
        "threat_type": analysis.get("threat_type"),
        "severity": analysis.get("severity"),
        "confidence": analysis.get("confidence"),
        "containment_steps": analysis.get("containment_steps", []),
        "mcp_enrichment": analysis.get("mcp_enrichment"),
        "chain_url": f"/chain/view/{incident_id}"
    }), 200, {"Content-Type": "application/json"}


@app.route("/judge", methods=["GET"])
def judge_page():
    from flask import render_template
    return render_template("judge.html")
