import time
import hashlib
import re

_rate_limits = {}
RATE_LIMIT = 30  # max requests per minute per IP
WINDOW = 60  # seconds

def check_rate_limit(ip):
    """Returns True if request is allowed, False if rate limited."""
    now = time.time()
    key = ip or "default"
    if key not in _rate_limits:
        _rate_limits[key] = []
    # Remove old entries outside window
    _rate_limits[key] = [t for t in _rate_limits[key] if now - t < WINDOW]
    if len(_rate_limits[key]) >= RATE_LIMIT:
        return False
    _rate_limits[key].append(now)
    return True

def sanitize_alert(text):
    """Remove potentially dangerous patterns from alert text."""
    if not isinstance(text, str):
        return ""
    # Limit length to prevent memory exhaustion
    text = text[:10000]
    # Remove null bytes and control chars
    text = text.replace("\x00", "")
    # Strip dangerous SQL/command injection patterns (defensive)
    dangerous = ["DOP TABLE", "DROP DATABASE", "DELETE FROM", "INSERT INTO", "UPDATE SET", "/*", "*/", ";s", "|f", "&&"]
    upper = text.upper()
    for pattern in dangerous:
        if pattern in upper:
            text = text.replace(pattern, "[REDACTED]")
    return text.strip()

def validate_analyze_payload(data):
    """Validate /analyze request body. Returns (is_valid, error_msg)."""
    if data is None:
        return False, "Request body must be JSON"
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object"
    if "alert" not in data:
        return False, "Missing required field: alert"
    if not isinstance(data["alert"], str):
        return False, "Field 'alert' must be a string"
    if len(data["alert"].strip()) == 0:
        return False, "Alert cannot be empty"
    return True, ""
