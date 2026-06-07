"""
Audit Logging Module for Sentinel Edge
Provides structured JSON logging for security compliance and forensic analysis.
"""
import json
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

AUDIT_LOG_FILE = LOG_DIR / "audit.log"
ACCESS_LOG_FILE = LOG_DIR / "access.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"

# Create formatters
json_formatter = logging.Formatter('%(message)s')
detailed_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Setup audit logger (JSON structured logs)
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)
audit_handler = RotatingFileHandler(
    AUDIT_LOG_FILE,
    maxBytes=10*1024*1024,
    backupCount=5
)
audit_handler.setFormatter(json_formatter)
audit_logger.addHandler(audit_handler)

# Setup access logger (human-readable)
access_logger = logging.getLogger('access')
access_logger.setLevel(logging.INFO)
access_handler = RotatingFileHandler(
    ACCESS_LOG_FILE,
    maxBytes=10*1024*1024,
    backupCount=5
)
access_handler.setFormatter(detailed_formatter)
access_logger.addHandler(access_handler)

# Setup error logger
error_logger = logging.getLogger('error')
error_logger.setLevel(logging.ERROR)
error_handler = RotatingFileHandler(
    ERROR_LOG_FILE,
    maxBytes=10*1024*1024,
    backupCount=5
)
error_handler.setFormatter(detailed_formatter)
error_logger.addHandler(error_handler)


def log_request(request, response, duration_ms, user_id=None):
    """Log API request with full audit trail."""
    # Sanitize sensitive data from request
    request_data = {}
    if request.is_json:
        try:
            request_data = request.get_json(silent=True) or {}
            sensitive_keys = ['password', 'api_key', 'token', 'secret', 'authorization']
            for key in sensitive_keys:
                if key in request_data:
                    request_data[key] = '****REDACTED***'
        except:
            request_data = {'error': 'Could not parse JSON'}

    # Build audit log entry
    audit_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'event_type': 'api_request',
        'request_id': getattr(request, 'request_id', None),
        'method': request.method,
        'endpoint': request.path,
        'query_params': dict(request.args),
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'user_id': user_id,
        'request_body': request_data if request.method in ['POST', 'PUT', 'PATCH'] else None,
        'response_status': response.status_code,
        'response_size': response.content_length or 0,
        'duration_ms': round(duration_ms, 2),
        'success': 200 <= response.status_code < 400,
        'error_category': _categorize_error(response.status_code)
    }

    # Write JSON audit log
    audit_logger.info(json.dumps(audit_entry))

    # Write human-readable access log
    status_emoji = '❡' if audit_entry['success'] else '❡'
    access_logger.info(
        f"{status_emoji} {request.method} {request.path} | "
        f"Status: {response.status_code} | "
        f"Duration: {duration_ms:.2f}ms | "
        f"IP: {request.remote_addr} | "
        f"User: {user_id or 'anonymous'}"
    )

    # Log errors separately
    if response.status_code >= 400:
        error_logger.error(
            f"Request failed: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Error: {audit_entry.get('error_category')} | "
            f"IP: {request.remote_addr}"
        )


def _categorize_error(status_code):
    """Categorize HTTP error codes for analysis."""
    if 200 <= status_code < 300:
        return None
    elif 400 <= status_code < 500:
        return 'client_error'
    elif 500 <= status_code < 600:
        return 'server_error'
    return 'unknown'


def log_security_event(event_type, details, severity='INFO'):
    """Log security-related events."""
    security_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'event_type': f'security_{event_type}',
        'severity': severity,
        **details
    }
    audit_logger.info(json.dumps(security_entry))
    if severity in ['ERROR', 'CRITICAL']:
        error_logger.error(f"Security event: {event_type} | {details}")


def get_audit_summary(hours=24):
    """Generate audit summary for the specified time period."""
    from collections import defaultdict

    cutoff = datetime.utcnow().timestamp() - (hours * 3600)

    stats = {
        'total_requests': 0,
        'successful_requests': 0,
        'failed_requests': 0,
        'avg_response_time_ms': 0,
        'endpoint_counts': defaultdict(int),
        'status_codes': defaultdict(int),
        'top_ips': defaultdict(int),
        'security_events': 0
    }

    total_duration = 0

    try:
        with open(AUDIT_LOG_FILE, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(
                        entry['timestamp'].replace('Z', '+00:00')
                    ).timestamp()

                    if entry_time < cutoff:
                        continue

                    stats['total_requests'] += 1
                    if entry.get('success'):
                        stats['successful_requests'] += 1
                    else:
                        stats['failed_requests'] += 1

                    total_duration += entry.get('duration_ms', 0)
                    stats['endpoint_counts'][entry['endpoint']] += 1
                    stats['status_codes'][entry['response_status']] += 1
                    stats['top_ips'][entry['client_ip']] += 1

                    if 'security_' in entry.get('event_type', ''):
                        stats['security_events'] += 1

                except (JSONDecodeError, KeyError, ValueError, TypeError):
                    continue

    except FileNotFoundError:
        pass

    if stats['total_requests'] > 0:
        stats['avg_response_time_ms'] = round(
            total_duration / stats['total_requests'], 2
        )

    stats['endpoint_counts'] = dict(stats['endpoint_counts'])
    stats['status_codes'] = dict(stats['status_codes'])
    stats['top_ips'] = dict(
        sorted(stats['top_ips'].items(), key=lambda x: x[1], reverse=True)[:10]
    )

    return stats
