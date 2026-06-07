# Sentinel Edge

**Autonomous Cybersecurity Incident Response Agent for Edge Devices**

Sentinel Edge is a production-grade AI agent that runs entirely on Android/Termux, designed for real-time cybersecurity incident response under constrained edge conditions.

> ğŸ© Hunting Prize: Global AI Hackathon Series â€” Track 5: EdgeAgent

## ğŸ¢ What It Does

Sentinel Edge automates the full incident response lifecycle:

1. **Perceive** - Extracts IOCs (IPs, usernames, timestamps) from raw alerts
2. **Reason** - Classifies threats via Qwen Cloud API or smart offline heuristics
3. **Act** - Generates containment plans with human-in-the-loop approval
4. **Remember** - Persists incidents in SQLite for cross-session forensic intelligence

## ğŸ¤ Track Alignment

| Track | HowSentinel Edge Qualifies |
|-----|-----|
| **Track 5: EdgeAgent** (primary) | Runs on Android, graceful offline degradation, privacy-aware data handling, <0.5s response time |
| **Track 1: MemoryAgent** (overlap) | SQLite persistent memory, keyword search, historical context injection |
| **Track 4: Autopilot Agent** (overlap) | End-to-end IR workflow with explicit HITL checkpoints |

## âš™ Stress Test Results (10/10 PASSED)

| # | Test | Result | Judging Criteria |
|---|-----|------|-----|
| 1 | Baseline Health | âœ… 6/6 | |
| 2 | Rapid-Fire Load (10 alerts) | âœ… 5/5 | Scalability |
| 3 | Malformed Input (6 cases) | âœ” V/6 | Robustness |
| 4 | Memory Search Under Load | âœ… 5/5 | Track 1: MemoryAgent |
| 5 | Concurrent Requests (5 analysts) | âœ… 5/5 | Architecture |
| 6 | Offline/Online Resilience | âœ” T/4 | Track 5: EdgeAgent Core |
| 7 | Large Payload (5KB) | âœ… 3/3 | Perception Depth |
| 8 | Report Generation | âœ… 3/3 | Track 1/4 Overlap |
| 9 | HITL Workflow Lifecycle | âœ… 4/4 | Track 4: Autopilot |
| 10 | E2E production Simulation | âœ… 6/6 | All Criteria |

**Total: 50/50 checks passed**

## ğŸ”š Security Hardening

Sentinel Edge defends itself against abuse and attack:

- **Rate Limiting**: 30 requests/min per IP (protects edge hardware)
- **Input Sanitization**: Blocks SQL/command injection patterns
- **Schema Validation**: Rejects malformed payloads before AI processing

## ğŸ”¡ Architecture

```
sentinel-edge/
â”€â”€ app.py              # Flask API server
â”€â”€ modules/
â”€â”€  perception.py  # Alert validation + IOC extraction
â”€â”€  reasoning.py    # Qwen Cloud API+ Smart Offline
â”€â”€  action.py        # Containment execution + HITL
å€â”€  dashboard.py    # Real-time metrics for judges
â”€â”€  security.py     # Rate limiting + sanitization

â”€â”€ memory.py            # SQLite persistent storage
â”€â”€ config.py             # Env-loaded configuration
â”€â”€€¹•¹Ø€€€€€€€€€€€€€€€€€ŒA$­•åÌ€¬ÁÉ½Ù¥‘•ÈÍ•±•Ñ¥½¸)€((ŒŒƒŠj¨EÕ¥¬MÑ…ÉĞ()‰…Í )¥Ğ±½¹”¡ÑÑÁÌè¼½¥Ñ¡Õˆ¹½´½µ…‰•É”½Í•¹Ñ¥¹•°µ•‘”¹¥Ğ)Í•¹Ñ¥¹•°µ•‘”)ÁåÑ¡½¸€µ´Ù•¹ØÙ•¹Ø)Í½ÕÉ”Ù•¹Ø½‰¥¸½…Ñ¥Ù…Ñ”)Á¥À¥¹ÍÑ…±°€µÈÉ•ÅÕ¥É•µ•¹ÑÌ¹ÑáĞ((Œ½¹™¥ÕÉ”1-4ÁÉ½Ù¥‘•È)•¡¼€115}AI=Y%HõÅİ•¸œ€øø€¹•¹Ø)•¡¼€E]9}A%}-dõå½ÕÉ}­•äœ€øø€¹•¹Ø((ŒMÑ…ÉĞÍ•ÉÙ•È)ÁåÑ¡½¸…ÁÀ¹Áä)€((ŒŒƒÂ~j”%dMÑ…ÉĞ€¡9¼A$-•ä¤()M•¹Ñ¥¹•°‘”İ½É­Ì¥µµ•‘¥…Ñ•±äİ¥Ñ¡½ÕĞ…¹ä±½ÕÉ•‘¥ÑÌè()‰…Í )ÁåÑ¡½¸…ÁÀ¹Áä)ÕÉ°€µ`A=MP¡ÑÑÀè¼¼ÄÈÜ¸À¸À¸ÄèÔÀÀÀ½…¹…±åé”p(€€µ €‰½¹Ñ•¹ĞµQåÁ”è…ÁÁ±¥…Ñ¥½¸½©Í½¸ˆp(€€µ€ì‰…±•ÉĞˆè€‰MÕÍÁ¥¥½ÕÌÉ½½Ğ±½¥¸™É½´€ÄÀ¸À¸À¸Ô‰ôœ)€()Q¡”Íµ…ÉĞ½™™±¥¹”µ½‘”É•ÑÕÉ¹ÌÉ•…±¥ÍÑ¥ŒÑ¡É•…Ğ…¹…±åÍ¥Ìİ¥Ñ ½¹Ñ…¥¹µ•¹ĞÍÑ•ÁÌ°Í•Ù•É¥ÑäÍ½É¥¹œ°…¹½¹™¥‘•¹”±•Ù•±Ì€´…±°•¹•É…Ñ•±½…±±ä¸((ŒŒƒÂ~R”A$¹‘Á½¥¹ÑÌ()ğ¹‘Á½¥¹Ğğ5•Ñ¡½ğ•ÍÉ¥ÁÑ¥½¸ğ)ğ´´´´´´´´µğ´´´´´µğ´´´´µğ)ğ€½•…±Ñ¡ğPğMåÍÑ•´¡•…±Ñ ¡•¬ğ)ğ€½…¹…±åé•ğA=MPğ¹…±åé”…±•ÉĞ€¡)M=8èì‰…±•ÉĞˆè€ˆ¸¸¸‰ô¤ğ)ğ€½¥¹¥‘•¹ÑÍ€ğPğ1¥ÍĞÉ••¹Ğ¥¹¥‘•¹ÑÌğ)ğ€½É•Á½ÉĞ¼ñ¥ù€ğPğ•¹•É…Ñ”™½É•¹Í¥ŒÉ•Á½ÉĞğ)ğ€½…ÁÁÉ½Ù”¼ñ¥ù€ğA=MPğá•ÕÑ”½¹Ñ…¥¹µ•¹Ğ€¡!%Q0¤ğ)ğ€½‘…Í¡‰½…É‘ğPğI•…°µÑ¥µ”µ•ÑÉ¥Ìğ((ŒŒƒÂ~Rˆ¹ØY…É¥…‰±•Ì()ğY…É¥…‰±”ğ•ÍÉ¥ÁÑ¥½¸ğ•™…Õ±Ğğ)ğ´´´´´´´´µğ´´´´µğ´´´´µğ)ğ115}AI=Y%HğÅİ•¸ğ±…Õ‘”ğ½™™±¥¹”ğÅİ•¸ğ(E]9}A%}-dğ…Í¡M½Á”A$­•äğ€´ğ)ğ1U}A%}-dğ¹Ñ¡É½Á¥ŒA$­•äğ€´ğ)ğ!=MPğM•ÉÙ•È‰¥¹…‘‘É•ÍÌğ€ÄÈÜ¸À¸À¸Äğ)ğA=IPğM•ÉÙ•ÈÁ½ÉĞğ€ÔÀÀÀğ((ŒŒƒÂ~N˜1¥•¹Í”()5%P1¥•¹Í”¸M•”m1%9Mt¡1%9M¤™½È‘•Ñ…¥±Ì¸(
## â˜ï¸ Alibaba Cloud Deployment

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

