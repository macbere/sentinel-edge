# Sentinel Edge API Documentation

## Base URL

Production: http://47.77.199.98
Local: http://127.0.0.1:5000

## Authentication

Currently open API. Rate limited to 30 requests per minute per IP address.

## Endpoints

### GET /health
Returns system status and loaded modules.

Request:
curl http://47.77.199.98/health

Response:
{
  "agent": "Sentinel Edge",
  "mode": "edge-cloud-hybrid",
  "modules": ["perception", "reasoning", "action", "memory"],
  "status": "online"
}

### POST /analyze
Submits a security alert for full 4-step agentic analysis.

Request:
curl -X POST http://47.77.199.98/analyze \
  -H "Content-Type: application/json" \
  -d '{"alert": "Ransomware beacon from 185.220.101.45"}'

Response fields:
- threat_type: Identified threat category
- severity: low, medium, high, or critical
- confidence: 0.0 to 1.0 confidence score
- containment_steps: List of recommended actions
- requires_human_approval: true or false
- reasoning_chain: Full 4-step Qwen reasoning chain
- mcp_enrichment: Real-time AbuseIPDB threat intelligence
- iocs: Extracted indicators of compromise
- incident_id: Stored incident reference number
- total_chain_elapsed_ms: Total processing time

### GET /dashboard
Returns real-time system metrics and statistics.

Request:
curl http://47.77.199.98/dashboard

Response fields:
- metrics.total_incidents: All-time incident count
- metrics.pending_approval: Incidents awaiting human approval
- metrics.executed: Approved and executed incidents
- ai_provider_stats.qwen_analyses: Real Qwen API call count
- ai_provider_stats.offline_fallbacks: Offline analysis count
- top_threats: Top 5 threat types by frequency
- recent_incidents: Last 5 incidents with status
- system.uptime: Server uptime

### GET /correlate
Detects coordinated attack campaigns from incident history.

Request:
curl http://47.77.199.98/correlate
curl http://47.77.199.98/correlate?hours=48

Parameters:
- hours: Lookback period in hours (default: 24)

Response fields:
- campaigns_detected: Number of campaigns found
- campaigns: List of detected campaigns
- campaigns[].attack_pattern: Kill chain stages
- campaigns[].threat_actor_profile: Actor IOCs and tactics
- campaigns[].severity: Campaign severity level
- campaigns[].incident_count: Number of linked incidents

### GET /incidents
Returns list of recent incidents.

Request:
curl http://47.77.199.98/incidents
curl http://47.77.199.98/incidents?limit=20

Parameters:
- limit: Number of incidents to return (default: 10)

### GET /report/<id>
Returns full forensic report for a specific incident.

Request:
curl http://47.77.199.98/report/5

Response includes full analysis, reasoning chain, similar incidents, and formatted report text.

### POST /approve/<id>
Approves and executes containment actions for a pending incident.

Request:
curl -X POST http://47.77.199.98/approve/5

Response fields:
- status: executed
- execution_log: Step-by-step execution record with timestamps
- message: Summary of actions taken

### GET /audit
Returns audit log summary for monitoring.

Request:
curl http://47.77.199.98/audit
curl http://47.77.199.98/audit?hours=48

## Error Responses

400 Bad Request - Missing or invalid alert field
429 Too Many Requests - Rate limit exceeded
404 Not Found - Incident ID does not exist
503 Service Unavailable - AI provider unavailable

## Rate Limits

- 30 requests per minute per IP address
- Applies to all endpoints
- Returns 429 with error message when exceeded

## Threat Types Detected

- ransomware_beacon
- brute_force_attack
- privilege_escalation
- unauthorized_access
- network_scan
- phishing_attempt
- sql_injection
- data_exfiltration
- malware_execution
