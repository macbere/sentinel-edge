# Sentinel Edge

**Autonomous Cybersecurity Incident Response Agent for Edge Devices**

Sentinel Edge is a production-grade AI agent that runs entirely on Android/Termux, designed for real-time cybersecurity incident response under constrained edge conditions.

> 🎩 Hunting Prize: Global AI Hackathon Series — Track 5: EdgeAgent

## 🏢 What It Does

Sentinel Edge automates the full incident response lifecycle:

1. **Perceive** - Extracts IOCs (IPs, usernames, timestamps) from raw alerts
2. **Reason** - Classifies threats via Qwen Cloud API or smart offline heuristics
3. **Act** - Generates containment plans with human-in-the-loop approval
4. **Remember** - Persists incidents in SQLite for cross-session forensic intelligence

## 🏤 Track Alignment

| Track | HowSentinel Edge Qualifies |
|-----|-----|
| **Track 5: EdgeAgent** (primary) | Runs on Android, graceful offline degradation, privacy-aware data handling, <0.5s response time |
| **Track 1: MemoryAgent** (overlap) | SQLite persistent memory, keyword search, historical context injection |
| **Track 4: Autopilot Agent** (overlap) | End-to-end IR workflow with explicit HITL checkpoints |

## ⚙ Stress Test Results (10/10 PASSED)

| # | Test | Result | Judging Criteria |
|---|-----|------|-----|
| 1 | Baseline Health | ✅ 6/6 | |
| 2 | Rapid-Fire Load (10 alerts) | ✅ 5/5 | Scalability |
| 3 | Malformed Input (6 cases) | ✔ V/6 | Robustness |
| 4 | Memory Search Under Load | ✅ 5/5 | Track 1: MemoryAgent |
| 5 | Concurrent Requests (5 analysts) | ✅ 5/5 | Architecture |
| 6 | Offline/Online Resilience | ✔ T/4 | Track 5: EdgeAgent Core |
| 7 | Large Payload (5KB) | ✅ 3/3 | Perception Depth |
| 8 | Report Generation | ✅ 3/3 | Track 1/4 Overlap |
| 9 | HITL Workflow Lifecycle | ✅ 4/4 | Track 4: Autopilot |
| 10 | E2E production Simulation | ✅ 6/6 | All Criteria |

**Total: 50/50 checks passed**

## 🔚 Security Hardening

Sentinel Edge defends itself against abuse and attack:

- **Rate Limiting**: 30 requests/min per IP (protects edge hardware)
- **Input Sanitization**: Blocks SQL/command injection patterns
- **Schema Validation**: Rejects malformed payloads before AI processing

## 🔡 Architecture

```
sentinel-edge/
── app.py              # Flask API server
── modules/
──  perception.py  # Alert validation + IOC extraction
──  reasoning.py    # Qwen Cloud API+ Smart Offline
──  action.py        # Containment execution + HITL
吀─  dashboard.py    # Real-time metrics for judges
──  security.py     # Rate limiting + sanitization

── memory.py            # SQLite persistent storage
── config.py             # Env-loaded configuration
──����؀������������������A$����̀���ɽ٥��ȁ͕���ѥ��)���((����j��Eե���Mх��()�����͠)��Ё�����������輽��ѡՈ����������ɔ�͕�ѥ������������)���͕�ѥ��������)��ѡ������ٕ�؁ٕ��)ͽ�ɍ��ٕ�ؽ������ѥمє)�������х����ȁɕ�եɕ����̹���((��������ɔ�1-4��ɽ٥���)������115}AI=Y%H��ݕ����������)������E]9}A%}-d����}��䜀�������((��Mх�Ё͕�ٕ�)��ѡ���������)���((����~j��%d�Mх�Ѐ�9��A$�-��()M��ѥ��������ݽɭ́�������ѕ��ݥѡ��Ё��䁍��Ր��ɕ�����()�����͠)��ѡ���������)��ɰ��`�A=MP�����輼��ܸ����������������锁p(��� ����ѕ�еQ���聅������ѥ����ͽ���p(������쉅���Ј耉M��������́ɽ�Ё�������ɽ���������ԉ��)���()Q���͵��Ё�������������ɕ��ɹ́ɕ����ѥ��ѡɕ�Ё�����ͥ́ݥѠ����х�����Ё�ѕ�̰�͕ٕɥ��͍�ɥ���������������������ٕ�̀����������Ʌѕ���������((����~R��A$���������()��������Ё��5�ѡ������͍ɥ�ѥ����)𴴴������𴴴���𴴴���)��������ѡ�����P���M��ѕ������Ѡ��������)����������镁����A=MP�������锁����Ѐ�)M=8�쉅���Ј耈��������)�������������́����P���1��Ёɕ���Ё��������́�)�����ɕ���м�������P������Ʌє���ɕ�ͥ��ɕ���Ё�)��������ɽٔ��������A=MP���ᕍ�є����х�����Ѐ�!%Q0���)�������͡���ɑ�����P���I����ѥ������ɥ�́�((����~R���؁Y�ɥ�����()��Y�ɥ��������͍ɥ�ѥ��������ձЁ�)𴴴������𴴴��𴴴���)��115}AI=Y%H����ݕ�������Ց���������������ݕ���(�E]9}A%}-d����͡M�����A$���������)��1U}A%}-d����ѡɽ����A$���������)��!=MP���M��ٕȁ��������ɕ�́����ܸ����ā�)��A=IP���M��ٕȁ���Ё��������((����~N��1����͔()5%P�1����͔��M���m1%9Mt�1%9M����ȁ��х��̸(
## ☁️ Alibaba Cloud Deployment

Sentinel Edge is designed for deployment on Alibaba Cloud ECS (Elastic Compute Service).

### Quick Deploy (Automated)

```bash
# Prerequisites: Alibaba Cloud CLI configured
./deploy_alibaba.sh
```

### Manual Deploy (Docker)

```bash
# Build image
docker build -t sentinel-edge .

# Run container
docker run -d \
  --name sentinel-edge \
  -p 5000:5000 \
  --env-file .env \
  sentinel-edge
```

### Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Configuration

For production deployment on Alibaba Cloud:

1. **ECS Instance**: Use `ecs.t6-c1m1.large` (2 vCPU, 2GB RAM)
2. **Security Group**: Open port 5000 for API access
3. **SSL/TLS**: Use Alibaba Cloud SLB with HTTPS
4. **Monitoring**: Enable CloudMonitor for metrics
5. **Backup**: Use OSS for database backups

### Environment Variables for Production

```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=your_production_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-max
HOST=0.0.0.0
PORT=5000
DEBUG=False
```



## 🎯 Automated Incident Correlation Engine
- Pattern Recognition: Identifies related incidents by IP, username, domain, filepath
- Campaign Detection: Groups incidents into attack campaigns using graph analysis
- Threat Actor Profiling: Creates profiles with aggregated IOCs and tactics
- Attack Chain Analysis: Maps progression (recon -> access -> execution -> impact)
- Correlation Scoring: Weighted algorithm (time 30%, IOC overlap 50%, threat 20%)
- API Endpoint: /correlate?hours=24 returns detected campaigns

## 🧪 Edge Case Testing (15/15 - 100% Pass Rate)
- Health endpoint availability
- Malformed JSON handling
- Missing alert field rejection
- Empty alert handling
- Very long alerts (10KB)
- Unicode character support
- SQL injection protection
- Multiple IOC extraction
- Rapid sequential requests (20)
- Dashboard metrics accuracy
- Audit logging completeness
- Incident persistence
- Threat classification accuracy (4/4)
- Concurrent requests (10/10)
- Endpoint discovery
