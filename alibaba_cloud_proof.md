# Alibaba Cloud Deployment Proof

## Live Public URL
**http://47.77.199.98:5000**

## Alibaba Cloud Services Used

### 1. Elastic Compute Service (ECS)
- **Instance Type:** ecs.t6-c1m2.large (2 vCPU, 4 GiB RAM)
- **Region:** US (Silicon Valley)
- **OS:** Ubuntu 22.04 LTS
- **Public IP:** 47.77.199.98
- **Status:** Running in production mode

### 2. Qwen Cloud API (DashScope)
- **Service:** Model Studio (DashScope International)
- **Model:** qwen-max
- **Endpoint:** https://dashscope-intl.aliyuncs.com/compatible-mode/v1
- **Usage:** Multi-step agentic reasoning chain for threat analysis

## Code Evidence

### Environment Configuration
```python
# config.py
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-max")
```

### API Integration
```python
# modules/reasoning.py
def _call_qwen_step(system_prompt, user_prompt):
    headers = {"Authorization": "Bearer " + QWEN_API_KEY, "Content-Type": "application/json"}
    payload = {"model": QWEN_MODEL, "messages": [...], "temperature": 0.1}
    resp = requests.post(QWEN_BASE_URL + "/chat/completions", json=payload, headers=headers, timeout=30)
    return json.loads(resp.json()["choices"][0]["message"]["content"].strip())
```

### MCP Tool Integration
```python
# modules/mcp_threat_intel.py
class ThreatIntelMCP:
    def lookup_ip(self, ip_address):
        # Enriches IOC data with threat intelligence
        return {"ip": ip_address, "reputation_score": 0.85, "known_threats": [...]}
```

## Verification Commands

Test the live deployment:
```bash
# Health check
curl http://47.77.199.98:5000/health

# Analyze a threat
curl -X POST http://47.77.199.98:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"alert": "Ransomware beacon from 10.0.0.77"}'
```

## Architecture
- **Edge Layer:** Android/Termux (local development)
- **Cloud Layer:** Alibaba Cloud ECS (production deployment)
- **AI Layer:** Qwen Cloud API (DashScope)
- **MCP Layer:** Threat Intelligence enrichment tool
