# Sentinel Edge — Deployment Guide

## Requirements
- Python 3.10+
- pip
- Git
- Alibaba Cloud ECS account
- Qwen Cloud API key (free tier available)
- AbuseIPDB API key (free tier available)

## Local Development (Android/Termux)
git clone https://github.com/macbere/sentinel-edge.git
cd sentinel-edge
pip install -r requirements.txt
cp .env.template .env
Add QWEN_API_KEY and ABUSEIPDB_API_KEY to .env
./start.sh --prod

## Alibaba Cloud ECS Deployment
ssh root@YOUR_ECS_IP
git clone https://github.com/macbere/sentinel-edge.git
cd sentinel-edge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
Add your API keys to .env

## systemd Service (Auto-restart)
Copy the service file:
cp deploy/sentinel-edge.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sentinel-edge
systemctl start sentinel-edge

## Nginx Setup
apt install nginx -y
cp deploy/nginx.conf /etc/nginx/sites-available/sentinel-edge
ln -s /etc/nginx/sites-available/sentinel-edge /etc/nginx/sites-enabled/
systemctl restart nginx

## Verify Deployment
curl http://YOUR_IP/health
curl -X POST http://YOUR_IP/analyze -H "Content-Type: application/json" -d '{"alert": "Test ransomware alert"}'

## Environment Variables
QWEN_API_KEY=your_key_here
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-max
ABUSEIPDB_API_KEY=your_key_here
LLM_PROVIDER=qwen
HOST=0.0.0.0
PORT=5000
DEBUG=False
