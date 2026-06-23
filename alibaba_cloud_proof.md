# Alibaba Cloud Deployment Proof

## Live Public URL
**http://47.77.199.98**

## Alibaba Cloud Services Used

### 1. Elastic Compute Service (ECS)
- **Instance Type:** ecs.t6-c1m2.large (2 vCPU, 4 GiB RAM)
- **Region:** US (Silicon Valley)
- **OS:** Ubuntu 22.04 LTS
- **Public IP:** 47.77.199.98
- **Status:** Running as permanent systemd service (auto-restarts on reboot)

### 2. Qwen Cloud API (DashScope International)
- **Model:** qwen-max
- **Endpoint:** https://dashscope-intl.aliyuncs.com/compatible-mode/v1
- **Usage:** 4-step agentic reasoning chain — Classification, Tool Selection, Action Plan, Validation

### 3. AbuseIPDB Threat Intelligence (MCP Tool)
- **Integration:** Real-time IP reputation lookup during every analysis
- **Source field in response:** abuseipdb_live

## Live Verification

Run these commands to verify the deployment is live:

curl http://47.77.199.98/health

curl -X POST http://47.77.199.98/analyze \
  -H "Content-Type: application/json" \
  -d '{"alert": "Ransomware beacon from 10.0.0.77"}'

## Code Evidence

### Qwen API Integration (modules/reasoning.py)
```python
def _call_qwen_step(system_prompt, user_prompt):
    headers = {
        "Authorization": "Bearer " + QWEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    resp = requests.post(
        QWEN_BASE_URL + "/chat/completions",
        json=payload,
        headers=headers,
        timeout=30
    )
    return json.loads(resp.json()["choices"][0]["message"]["content"].strip())
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-max")
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY", "")
[Unit]
Description=Sentinel Edge Cybersecurity Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/sentinel-edge
EnvironmentFile=/root/sentinel-edge/.env
ExecStart=/root/sentinel-edge/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 --timeout 120 app:app
Restart=always
RestartSec=5
Architecture
Edge Layer: Android/Termux (local development and testing)
Cloud Layer: Alibaba Cloud ECS (production — permanent systemd service)
AI Layer: Qwen Cloud API via DashScope International
MCP Layer: AbuseIPDB real-time threat intelligence
