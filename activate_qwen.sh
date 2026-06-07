#!/bin/bash
echo "🚀 Activating Qwen Cloud Mode..."
if [ -z "$1" ]; then
    echo "❌ Usage: ./activate_qwen.sh YOUR_QWEN_API_KEY"
    exit 1
fi
sed -i.bak "s/^LLM_PROVIDER=.*/LLM_PROVIDER=qwen/" .env
sed -i.bak "s/^QWEN_API_KEY=.*/QWEN_API_KEY=$1/" .env
echo "✅ Qwen mode activated. Restart server: python app.py"
