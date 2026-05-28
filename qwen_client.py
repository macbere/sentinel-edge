import requests
import json
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL

def ask_qwen(prompt: str, system_prompt: str = None) -> dict:
    """
    Send a prompt to Qwen Cloud and return structured JSON response.
    Falls back gracefully if API is unavailable (offline mode).
    """
    if not QWEN_API_KEY:
        return {
            "error": "NO_API_KEY",
            "message": "Qwen API key not configured. Running in offline/demo mode.",
            "severity": "unknown",
            "threat_type": "unanalyzed",
            "containment_steps": ["Configure QWEN_API_KEY in .env file"],
            "requires_human_approval": True
        }

    if system_prompt is None:
        system_prompt = """You are Sentinel Edge, an autonomous cybersecurity incident response agent.
Analyze the provided alert and respond ONLY with valid JSON in this exact format:
{
  "severity": "low|medium|high|critical",
  "threat_type": "string describing the threat",
  "containment_steps": ["step1", "step2", "step3"],
  "requires_human_approval": true|false,
  "confidence": 0.0-1.0
}
Do NOT include markdown, explanations, or any text outside the JSON."""

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(
            f"{QWEN_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    except requests.exceptions.ConnectionError:
        return {
            "error": "OFFLINE",
            "message": "Cannot reach Qwen Cloud. Offline fallback active.",
            "severity": "unknown",
            "threat_type": "connection_failed",
            "containment_steps": ["Check network connectivity", "Retry when online"],
            "requires_human_approval": True,
            "confidence": 0.0
        }
    except Exception as e:
        return {
            "error": "API_ERROR",
            "message": str(e),
            "severity": "unknown",
            "threat_type": "analysis_failed",
            "containment_steps": ["Review API configuration", "Check Qwen Cloud status"],
            "requires_human_approval": True,
            "confidence": 0.0
        }
