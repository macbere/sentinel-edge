# Sentinel Edge

**Autonomous Cybersecurity Incident Response Agent**

Sentinel Edge is a production-grade AI agent that automates end-to-end cybersecurity incident response workflows using a 4-step agentic reasoning chain powered by Qwen Cloud API, with real-time threat intelligence enrichment via AbuseIPDB.

> 🏆 Submitted to: Global AI Hackathon Series with Qwen Cloud — **Track 4: Autopilot Agent**

## 🎥 Demo Video

[▶️ Watch the Sentinel Edge Hackathon Demo](https://youtu.be/QvPTKNo8VRM)

## 🔍 What It Does

Sentinel Edge automates the full incident response lifecycle end-to-end:

1. **Perceive** — Extracts IOCs from raw security alerts
2. **Reason** — Runs a 4-step agentic chain via Qwen Cloud API
3. **Enrich** — Queries AbuseIPDB in real-time for threat intelligence
4. **Act** — Generates containment plans with human-in-the-loop approval
5. **Remember** — Persists all incidents in SQLite for forensic correlation

## 🎯 Track 4: Autopilot Agent — Qualification

| Requirement | How Sentinel Edge Qualifies |
|---|---|
| Automates real-world workflows end-to-end | Full incident response: alert to analysis to containment to approval |
| Handles ambiguous inputs | Offline fallback handles any unstructured alert text |
| Invokes external tools | AbuseIPDB MCP tool called live during every analysis |
| Human-in-the-loop checkpoints | Every critical/high severity incident requires human approval |
| Production-readiness | Alibaba Cloud ECS, Gunicorn, Nginx, systemd, 70+ incidents |

## 🧠 4-Step Agentic Reasoning Chain

Every /analyze request triggers 4 sequential Qwen API calls:

Step 1: Threat Classification — identifies threat type, severity, extracts IOCs
MCP Tool: AbuseIPDB Lookup — enriches IP reputation and abuse score
Step 2: Tool Selection — decides which security tools are needed
Step 3: Action Plan Generation — creates containment steps
Step 4: Confidence Validation — self-checks the plan quality

## ☁️ Alibaba Cloud Deployment

Live URL: http://47.77.199.98

| Service | Usage |
|---|---|
| Elastic Compute Service (ECS) | Hosts the production Flask/Gunicorn server |
| Qwen Cloud API (DashScope) | Powers the 4-step agentic reasoning chain |
| Nginx | Reverse proxy on port 80 |
| systemd | Auto-restart on reboot or failure |

Test the live deployment:

curl http://47.77.199.98/health

curl -X POST http://47.77.199.98/analyze -H "Content-Type: application/json" -d '{"alert": "Ransomware beacon from 185.220.101.45 targeting finance-db"}'

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /health | GET | System status |
| /analyze | POST | 4-step AI threat analysis |
| /dashboard | GET | Real-time metrics |
| /correlate | GET | APT campaign detection |
| /incidents | GET | Incident list |
| /approve/id | POST | Human approval |
| /report/id | GET | Forensic report |
| /chain/view/id | GET | AI decision chain page |
| /demo | GET | One-click attack simulator |
| /metrics | GET | Visual analytics |
| /judge | GET | Judge Q&A panel |
| /qwen | GET | Why Qwen panel |
| /dashboard/evidence | GET | Evidence panel |
| /incidents-all | GET | All incidents with filters |

## 🛡️ Security Features

- Rate Limiting — 30 requests per minute per IP
- Input Sanitization — blocks SQL and command injection
- Schema Validation — rejects malformed payloads before AI processing
- Audit Logging — every request logged with full JSON audit trail
- Offline Fallback — smart heuristic analyzer when Qwen is unavailable

## 🧪 Test Results (49/49 — 100% Pass Rate)

Full test suite: 49/49 passed at 100%

Coverage includes: health, input validation, threat analysis, MCP enrichment, dashboard, evidence panel, APT correlation, incidents, frontend pages, failure simulation, and concurrent load.

See test_full.py for the complete test suite.

| Category | Tests | Result |
|---|---|---|
| Health and connectivity | 5 | PASS |
| Input validation | 4 | PASS |
| Threat analysis | 10 | PASS |
| MCP enrichment | 2 | PASS |
| Dashboard metrics | 5 | PASS |
| Evidence panel | 4 | PASS |
| APT correlation | 3 | PASS |
| Incidents | 3 | PASS |
| Frontend pages | 5 | PASS |
| Failure simulation | 4 | PASS |
| Concurrent load | 1 | PASS |
| Total | 49 | 100% |

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
- Real MCP integration with live AbuseIPDB threat intelligence
- Edge-cloud hybrid architecture with graceful offline degradation
- Automated APT campaign detection using graph-based correlation engine

### Technical Depth & Engineering (30%)
- Modular architecture with 10 independent modules
- Production deployment with 5 workers x 4 threads on Alibaba Cloud ECS
- Non-trivial logic including correlation engine, audit system, offline analyzer
- Error handling with timeouts, fallbacks, and input validation at every layer

### Problem Value & Impact (25%)
- Real SOC automation pain point
- Productization ready with REST API, dashboard, audit trails, HITL workflow
- Scalable stateless API design with database-backed persistence

### Presentation & Documentation (15%)
- Demo video linked above
- Architecture diagram in SVG and text formats
- Proof of Alibaba Cloud deployment in alibaba_cloud_proof.md
- Comprehensive README, API.md, JUDGE_GUIDE.md, DEMO_SCRIPT.md

## 📁 Repository Structure

app.py — Flask API server (14 routes)
config.py — Environment configuration
memory.py — SQLite persistent storage
seed.py — 70 rich incident seeder
test_full.py — 49-test full suite
modules/perception.py — IOC extraction
modules/reasoning.py — 4-step Qwen agentic chain
modules/mcp_threat_intel.py — AbuseIPDB real threat intelligence
modules/action.py — Containment execution and HITL
modules/dashboard.py — Real-time metrics
modules/correlation.py — Campaign detection engine
modules/audit.py — Structured audit logging
modules/security.py — Rate limiting and sanitization
modules/offline_analyzer.py — Smart offline fallback
modules/chain_view.py — AI decision chain data
templates/index.html — Main dashboard
templates/demo.html — One-click attack simulator
templates/metrics.html — Visual analytics
templates/judge.html — Judge Q&A panel
templates/qwen.html — Why Qwen panel
templates/chain.html — AI decision chain viewer
templates/incidents_all.html — All incidents with filters
alibaba_cloud_proof.md — Proof of Alibaba Cloud deployment
architecture_diagram.svg — Visual architecture diagram
Dockerfile and docker-compose.yml — Container config
LICENSE — MIT License

MIT License — Copyright (c) 2026 Sentinel Edge
