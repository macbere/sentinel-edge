# Contributing to Sentinel Edge

Thank you for your interest in contributing to Sentinel Edge!

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork to your machine
3. Install dependencies with: pip install -r requirements.txt
4. Copy environment template with: cp .env.template .env
5. Add your QWEN_API_KEY and ABUSEIPDB_API_KEY to .env
6. Start the server with: ./start.sh --prod

## API Keys Required

- QWEN_API_KEY - Get from https://dashscope.console.aliyun.com/
- ABUSEIPDB_API_KEY - Get from https://www.abuseipdb.com/register

## Running Tests

Run this command to execute all 15 edge case tests:
python test_edge_cases.py

## Pull Request Guidelines

- One feature or fix per PR
- Include tests for new features
- Update README if adding new endpoints
- Never commit API keys or .env files

## Project Modules

- app.py - Flask API server and route definitions
- modules/reasoning.py - 4-step Qwen agentic chain
- modules/mcp_threat_intel.py - AbuseIPDB MCP integration
- modules/action.py - Containment execution and HITL
- modules/dashboard.py - Real-time metrics
- modules/correlation.py - APT campaign detection
- modules/audit.py - Structured audit logging
- modules/security.py - Rate limiting and sanitization
- modules/offline_analyzer.py - Smart offline fallback
- templates/index.html - Frontend dashboard

## License

By contributing, you agree your contributions will be licensed under the MIT License.
