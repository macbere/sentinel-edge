import requests
import json
import time
import hashlib
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, CLAUDE_API_KEY, LLM_PROVIDER

SYSTEM_PROMPT = """You are Sentinel Edge, an autonomous cybersecurity incident response agent.
Analyze the provided alert and respond ONLY with valid JSON in this exact format:
{
  "severity": "low|medium|high|critical",
  "threat_type": "string describing the threat",
  "containment_steps": ["step1", "step2", "step3"],
  "requires_human_approval": true|false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}
Do NOT include markdown, explanations, or any text outside the JSON."""

def _smart_offline(prompt):
    """Use enhanced offline analyzer for realistic threat classification."""
    from modules.offline_analyzer import smart_offline_analyze
    return smart_offline_analyze(prompt)


def _call_qwen(prompt):
    if not QWEN_API_KEY:
        return None
    headers = {
        "Authorization": "Bearer " + QWEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
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
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content.strip())

def _call_claude(prompt):
    if not CLAUDE_API_KEY:
        return None
    headers = {
        "x-ipi-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-latest",
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        json=payload,
        headers=headers,
        timeout=30
    )
    resp.raise_for_status()
    content = resp.json()["content"][0]["text"]
    cleaned = content.replace("```json", "").replace("``` ", "").strip()
    return json.loads(cleaned)

def analyze_with_retry(prompt, max_retries=2):
    provider = LLM_PROVIDER
    for attempt in range(max_retries + 1):
        try:
            if provider == "claude":
                result = _call_claude(prompt)
            elif provider == "qwen":
                result = _call_qwen(prompt)
            else:
                result = None
            if result is None:
                return _smart_offline(prompt)
            required = ["severity", "threat_type", "containment_steps"]
            if all(k in result for k in required):
                result["provider"] = provider
                return result
            return _smart_offline(prompt)
        except Exception:
            return _smart_offline(prompt)
    return _smart_offline(prompt)
