
"""Reasoning Module: Qwen API wrapper with validation + retry logic."""
import requests, json, time
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL

def analyze_with_retry(prompt: str, max_retries: int = 2) -> dict:
    """Call Qwen with automatic retry on malformed JSON."""
    if not QWEN_API_KEY:
        return {
            "error": "NO_API_KEY",
            "message": "Qwen API key not configured. Running in offline/demo mode.",
            "severity": "unknown",
            "threat_type": "unanalyzed",
            "containment_steps": ["Configure QWEN_API_KEY in .env file", "Verify network connectivity"],
            "requires_human_approval": True,
            "confidence": 0.0,
            "reasoning": "Offline fallback: awaiting API credentials",
            "fallback": True
        }

    system_prompt = """You are Sentinel Edge, a cybersecurity incident response agent.
Respond ONLY with valid JSON matching this schema:
{
  "severity": "low|medium|high|critical",
  "threat_type": "string",
  "containment_steps": ["string"],
  "requires_human_approval": boolean,
  "confidence": float (0.0-1.0),
  "reasoning": "brief explanation"
}"""

    for attempt in range(max_retries + 1):
        try:
            headers = {"Authorization": f"Bearer {QWEN_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": QWEN_MODEL,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            resp = requests.post(f"{QWEN_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            content = content.replace("", "")
            result = json.loads(content)
            # Validate required fields
            if all(k in result for k in ["severity", "threat_type", "containment_steps"]):
                return result
        except (json.JSONDecodeError, requests.RequestException) as e:
            if attempt == max_retries:
                return {
                "error": "ANALYSIS_FAILED",
                "message": str(e),
                "severity": "unknown",
                "threat_type": "analysis_error",
                "containment_steps": ["Review alert manually", "Retry analysis"],
                "requires_human_approval": True,
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
                "fallback": True
            }
            time.sleep(1)
    return {"error": "MAX_RETRIES_EXCEEDED", "fallback": True}
