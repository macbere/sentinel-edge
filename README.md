# Sentinel Edge

**Autonomous Cybersecurity Incident Response Agent — Alibaba Cloud x Qwen Hackathon**

Sentinel Edge is a production-grade AI agent that automates end-to-end cybersecurity incident response workflows using a 4-step agentic reasoning chain powered by Qwen Cloud API, with real-time threat intelligence enrichment via AbuseIPDB.

> 🏆 Submitted to: Global AI Hackathon Series with Qwen Cloud — **Track 4: Autopilot Agent**

## 🎥 Demo Video
**[Watch the Demo Video](#)** *(Link will be updated before submission)*

## 🔍 What It Does

Sentinel Edge automates the full incident response lifecycle end-to-end:

1. **Perceive** — Extracts IOCs (IPs, domains, usernames, filepaths) from raw security alerts
2. **Reason** — Runs a 4-step agentic chain via Qwen Cloud API
3. **Enrich** — Queries AbuseIPDB in real-time to enrich IP reputation and threat context
4. **Act** — Generates containment plans with mandatory human-in-the-loop approval gates
5. **Remember** — Persists all incidents in SQLite for cross-session forensic correlation

## 🎯 Track 4: Autopilot Agent — Qualification

| Requirement | How Sentinel Edge Qualifies |
|---|---|
| Automates real-world workflows end-to-end | Full incident response: alert to analysis to containment plan to approval |
| Handles ambiguous inputs | Offline fallback analyzer handles any unstructured alert text |
| Invokes external tools | AbuseIPDB MCP tool called live during every analysis |
| Human-in-the-loop checkpoints | Every critical/high severity incident requires human approval |
| Production-readiness | Deployed on Alibaba Cloud ECS with Gunicorn, audit logging, rate limiting |

## 🧠 4-Step Agentic Reasoning Chain

Every /analyze request triggers 4 sequential Qwen API calls:

Step 1: Threat Classification — Identifies threat type, severity, extracts IOCs
MCP Tool: AbuseIPDB Lookup — Enriches IP reputation, country, abuse score
Step 2: Tool Selection — Decides which security tools are needed
Step 3: Action Plan Generation — Creates containment steps
Step 4: Confidence Validation — Self-checks the plan, assigns confidence score
Human Approval Gate — Incident Stored — Dashboard Updated

## ☁️ Alibaba Cloud Deployment

Live URL: http://47.77.199.98

| Service | Usage |
|---|---|
| Elastic Compute Service (ECS) | Hosts the production Flask/Gunicorn server |
| Qwen Cloud API (DashScope) | Powers the 4-step agentic reasoning chain |

Test the live deployment:

curl http://47.77.199.98/health

curl -X POST http://47.77.199.98/analyze -H "Content-Type: application/json" -d '{"alert": "Ransomware beacon from 10.0.0.77"}'

## 🏗️ Architecture

See architecture_diagram.svg for the full visual diagram.

EDGE LAYER: SIEM Logs, IDS Alerts, Network Flow, User Input
SENTINEL EDGE AGENT: Perception, Reasoning, MCP, Action, Memory
ALIBABA CLOUD: Qwen Cloud API + ECS
OUTPUT: JSON API, Dashboard, Audit Logs, Reports

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /health | GET | System status and module list |
| /analyze | POST | Submit alert for full agentic analysis |
| /dashboard | GET | Real-time metrics and incident stats |
| /correlate | GET | Detect attack campaigns from incident history |
| /incidents | GET | List all stored incidents |
| /approve/id | POST | Human approval for pending actions |
| /report/id | GET | Full forensic report for an incident |

## 🛡️ Security Features

- Rate Limiting — 30 requests per minute per IP
- Input Sanitization — Blocks SQL and command injection patterns
- Schema Validation — Rejects malformed payloads before AI processing
- Audit Logging — Every request logged with full JSON audit trail
- Offline Fallback — Smart heuristic analyzer when Qwen API is unavailable

## 🧪 Test Results (15/15 — 100% Pass Rate)

| Test | Result |
|---|---|
| Health endpoint | PASS |
| Malformed JSON handling | PASS |
| Missing alert field rejection | PASS |
| Empty alert handling | PASS |
| Very long alerts 10KB | PASS |
| Unicode character support | PASS |
| SQL injection protection | PASS |
| Multiple IOC extraction | PASS |
| Rapid sequential requests 20 | PASS |
| Dashboard metrics accuracy | PASS |
| Audit logging completeness | PASS |
| Incident persistence | PASS |
| Threat classification accuracy 4/4 | PASS |
| Concurrent requests 10/10 | PASS |
| Endpoint discovery | PASS |

## 🚀 Quick Start

git clone https://github.com/macbere/sentinel-edge.git
cd sentinel-edge
pip install -r requirements.txt
cp .env.template .env
Add your QWEN_API_KEY and ABUSEIPDB_API_KEY to .env
./start.sh --prod

## 🏆 Judging Criteria Alignment

### Innovation & AI Creativity (30%)
- 4-step agentic reasoning chain with 4 sequential Qwen API calls per analysis
- Real MCP integration with live AbuseIPDB threat intelligence lookup
- Edge-cloud hybrid architecture with graceful offline degradation
- Automated campaign detection using graph-based correlation engine

### Technical Depth & Engineering (30%)
- Modular architecture with 8 independent modules
- Production deployment with Gunicorn on Alibaba Cloud ECS
- Non-trivial logic including correlation engine, audit system, offline analyzer
- Error handling with timeouts, fallbacks, input validation at every layer

### Problem Value & Impact (25%)
- Real-world pain point — SOC teams spend hours on manual incident triage
- Productization potential — REST API, dashboard, audit trails, HITL workflow
- Scalable stateless API design with database-backed persistence

### Presentation & Documentation (15%)
- Architecture diagram in SVG and text formats
- Proof of Alibaba Cloud deployment in alibaba_cloud_proof.md
- Comprehensive README with quick start guide
- Demo video link above

## 📁 Repository Structure

app.py — Flask API server
config.py — Environment configuration
memory.py — SQLite persistent storage
modules/perception.py — IOC extraction and alert parsing
modules/reasoning.py — 4-step Qwen agentic chain
modules/mcp_threat_intel.py — AbuseIPDB real threat intelligence
modules/action.py — Containment execution and HITL
modules/dashboard.py — Real-time metrics
modules/correlation.py — Campaign detection engine
modules/audit.py — Structured audit logging
modules/security.py — Rate limiting and sanitization
modules/offline_analyzer.py — Smart offline fallback
requirements.txt
Dockerfile
alibaba_cloud_proof.md
architecture_diagram.svg
LICENSE

MIT License — Copyright (c) 2026 Sentinel Edge
