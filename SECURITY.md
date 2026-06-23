# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x | Yes |

## Security Features

Sentinel Edge implements the following security measures:

- Rate Limiting - 30 requests per minute per IP address
- Input Sanitization - All alert text is sanitized before processing
- SQL Injection Protection - Parameterized queries throughout
- Schema Validation - All API payloads validated before AI processing
- Audit Logging - Every request logged with full JSON audit trail
- Environment Variables - All secrets loaded from .env, never hardcoded
- Human-in-the-Loop - Critical actions require human approval before execution

## Reporting a Vulnerability

If you discover a security vulnerability, do NOT open a public GitHub issue.
Contact the maintainer directly. We will respond within 48 hours.

## Deployment Security

- Never commit .env files to version control
- Use environment variables for all API keys
- Run behind Nginx reverse proxy in production
- Enable Alibaba Cloud Security Group rules
- Monitor audit logs regularly
