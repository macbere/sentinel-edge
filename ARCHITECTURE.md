# Sentinel Edge — Architecture

## System Overview

Sentinel Edge is an edge-cloud hybrid autonomous cybersecurity agent.
The phone/edge layer handles application logic.
Alibaba Cloud handles AI inference via Qwen Cloud API.

## Request Flow

1. Alert submitted via POST /analyze
2. Perception module validates input and extracts IOCs
3. Reasoning module makes 4 sequential Qwen API calls
4. MCP module queries AbuseIPDB for real threat intelligence
5. Action module generates containment plan
6. Incident stored in SQLite with full analysis JSON
7. Correlation engine links related incidents into campaigns
8. Human approves via POST /approve/id
9. Execution logged with timestamps

## Modules

- perception.py    — IOC extraction and alert validation
- reasoning.py     — 4-step Qwen agentic chain
- mcp_threat_intel.py — AbuseIPDB real-time enrichment
- action.py        — Containment execution and HITL
- dashboard.py     — Real-time metrics
- correlation.py   — Graph-based campaign detection
- audit.py         — Structured JSON audit logging
- security.py      — Rate limiting and sanitization
- offline_analyzer.py — Smart fallback when Qwen unavailable
- chain_view.py    — AI decision chain data provider

## Infrastructure

- Phone/Termux: Local development and testing
- Alibaba Cloud ECS: Production deployment (47.77.199.98)
- Nginx: Reverse proxy on port 80
- Gunicorn: 5 workers x 4 threads = 20 concurrent capacity
- systemd: Auto-restart on failure or reboot
- SQLite: Persistent incident storage
- Qwen Cloud: qwen-max model via DashScope International
- AbuseIPDB: Real-time IP threat intelligence

## Scaling Path

Current: Single ECS instance, SQLite, 20 concurrent
Next: Multiple ECS behind Alibaba Cloud SLB, RDS PostgreSQL
Future: Alibaba Cloud Container Service, auto-scaling groups
