
"""Perception Module: Validates and preprocesses incoming alerts."""
import re, json

def validate_alert(alert_text: str) -> dict:
    """Basic validation + enrichment of alert input."""
    if not alert_text or len(alert_text) < 10:
        return {"valid": False, "error": "Alert too short"}

    # Extract common indicators (IP, timestamp, user)
    indicators = {
        "ips": [ip for ip in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', alert_text) if ip not in {'47.77.199.98','127.0.0.1','0.0.0.0'} and not ip.startswith('10.') and not ip.startswith('192.168.')],
        "timestamps": re.findall(r"\d{2}:\d{2}(?:UTC|Z)?", alert_text, re.I),
        "users": re.findall(r"(?:user|login|account)\s+[:\-]?\s*(\w+)", alert_text, re.I)
    }
    return {"valid": True, "text": alert_text.strip(), "indicators": indicators}
