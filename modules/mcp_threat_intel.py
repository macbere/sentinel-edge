"""
MCP Threat Intelligence Module - AbuseIPDB Integration
Real threat intelligence lookups via AbuseIPDB API
"""
import requests
from datetime import datetime
from config import ABUSEIPDB_API_KEY

class ThreatIntelMCP:
    """Model Context Protocol tool for real threat intelligence enrichment via AbuseIPDB"""

    def __init__(self):
        self.name = "threat_intelligence_lookup"
        self.description = "Queries AbuseIPDB threat intelligence database to enrich IOC data"
        self.api_url = "https://api.abuseipdb.com/api/v2/check"

    def lookup_ip(self, ip_address):
        """
        Real threat intelligence lookup via AbuseIPDB API.
        Returns enriched data including reputation score, country, ISP, and known threats.
        """
        try:
            headers = {
                "Key": ABUSEIPDB_API_KEY,
                "Accept": "application/json"
            }
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": 90,
                "verbose": True
            }
            response = requests.get(
                self.api_url,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json().get("data", {})

            abuse_score = data.get("abuseConfidenceScore", 0)
            reputation_score = round(abuse_score / 100, 2)

            known_threats = []
            if abuse_score > 80:
                known_threats.append("high_risk_ip")
            if abuse_score > 50:
                known_threats.append("suspicious_activity")
            reports = data.get("reports", [])
            categories_seen = set()
            category_map = {
                3: "fraud_orders", 4: "ddos_attack", 5: "ftp_brute_force",
                6: "ping_of_death", 7: "phishing", 9: "open_proxy",
                10: "web_spam", 11: "email_spam", 14: "port_scan",
                15: "hacking", 16: "sql_injection", 17: "spoofing",
                18: "brute_force", 19: "bad_web_bot", 20: "exploited_host",
                21: "web_app_attack", 22: "ssh_attack", 23: "iot_targeted"
            }
            for report in reports[:10]:
                for cat in report.get("categories", []):
                    if cat in category_map:
                        categories_seen.add(category_map[cat])
            known_threats.extend(list(categories_seen))

            return {
                "ip": ip_address,
                "reputation_score": reputation_score,
                "abuse_confidence_score": abuse_score,
                "country": data.get("countryCode", "Unknown"),
                "asn": data.get("isp", "Unknown ISP"),
                "domain": data.get("domain", ""),
                "known_threats": known_threats if known_threats else ["no_known_threats"],
                "total_reports": data.get("totalReports", 0),
                "last_seen": data.get("lastReportedAt") or datetime.now().isoformat() + "Z",
                "is_whitelisted": data.get("isWhitelisted", False),
                "usage_type": data.get("usageType", "Unknown"),
                "source": "abuseipdb_live"
            }

        except requests.exceptions.Timeout:
            return self._fallback(ip_address, "timeout")
        except requests.exceptions.RequestException as e:
            return self._fallback(ip_address, str(e))
        except Exception as e:
            return self._fallback(ip_address, str(e))

    def _fallback(self, ip_address, reason):
        """Graceful degradation if AbuseIPDB is unreachable."""
        return {
            "ip": ip_address,
            "reputation_score": 0.5,
            "abuse_confidence_score": 50,
            "country": "Unknown",
            "asn": "Unknown",
            "known_threats": ["lookup_unavailable"],
            "total_reports": 0,
            "last_seen": datetime.now().isoformat() + "Z",
            "source": "fallback_unavailable",
            "fallback_reason": reason
        }

# Singleton instance
threat_intel_mcp = ThreatIntelMCP()
