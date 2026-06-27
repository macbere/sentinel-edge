# Sentinel Edge — Judge Guide

## Live URLs
- Dashboard: http://47.77.199.98
- Demo Mode: http://47.77.199.98/demo
- AI Chain View: http://47.77.199.98/chain/view/91
- Metrics: http://47.77.199.98/metrics
- Judge Panel: http://47.77.199.98/judge
- Why Qwen: http://47.77.199.98/qwen
- Evidence Panel: http://47.77.199.98/dashboard/evidence
- GitHub: https://github.com/macbere/sentinel-edge

## Quick Test Commands
curl http://47.77.199.98/health
curl -X POST http://47.77.199.98/analyze -H "Content-Type: application/json" -d '{"alert": "Ransomware beacon from 185.220.101.45"}'
curl http://47.77.199.98/correlate
curl http://47.77.199.98/dashboard/evidence

## Track Qualification — Track 4: Autopilot Agent
- Automates real-world workflows end-to-end: YES — full IR lifecycle
- Handles ambiguous inputs: YES — offline fallback for any alert text
- Invokes external tools: YES — AbuseIPDB MCP live API
- Human-in-the-loop checkpoints: YES — approval gate on all critical incidents
- Production-readiness: YES — Alibaba Cloud ECS, Nginx, systemd, 70+ incidents

## Judging Criteria Evidence
### Innovation & AI Creativity (30%)
- 4 sequential Qwen API calls per analysis
- Real AbuseIPDB MCP integration
- Edge-cloud hybrid with offline fallback
- Graph-based APT campaign detection

### Technical Depth & Engineering (30%)
- 8 independent modules
- 5 workers x 4 threads — 20 concurrent capacity
- Nginx reverse proxy + systemd auto-restart
- 15/15 edge case tests passing

### Problem Value & Impact (25%)
- Real SOC automation pain point
- Productization ready — REST API, dashboard, audit trails
- Scales horizontally behind Alibaba Cloud SLB

### Presentation & Documentation (15%)
- Live demo at http://47.77.199.98/demo
- Architecture diagram in repo
- Full API documentation in API.md
- This judge guide

## API Reference
GET  /health              System status
POST /analyze             4-step AI analysis
GET  /dashboard           Live metrics
GET  /correlate           APT campaign detection
GET  /incidents           Incident list
POST /approve/id          Human approval
GET  /report/id           Forensic report
GET  /chain/view/id       AI decision chain UI
GET  /demo                Live demo mode
GET  /metrics             Visual analytics
GET  /judge               Judge Q&A panel
GET  /qwen                Why Qwen panel
GET  /dashboard/evidence  Evidence panel
POST /simulate/failure    Resilience testing
