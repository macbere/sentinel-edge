"""
MCP Threat Intelligence Module - Multi-IOC Enrichment
Real threat intelligence via AbuseIPDB API
Supports: IP addresses, domains, file hashes
"""
import requests
from datetime import datetime
from config import ABUSEIPDB_API_KEY


class ThreatIntelMCP:
    """
    Model Context Protocol tool for real threat intelligence enrichment.
    Enriches IPs, domains, and file hashes with live threat data.
    """

    def __init__(self):
        self.name = "threat_intelligence_lookup"
        self.description = "Queries AbuseIPDB to enrich IOC data with live threat intelligence"
        self.api_base = "https://api.abuseipdb.com/api/v2"

    def lookup_ip(self, ip_address):
        """Real IP reputation lookup via AbuseIPDB."""
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
                f"{self.api_base}/check",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json().get("data", {})

            abuse_score = data.get("abuseConfidenceScore", 0)
            reports = data.get("reports", [])

            category_map = {
                3: "fraud_orders", 4: "ddos_attack",
                5: "ftp_brute_force", 7: "phishing",
                9: "open_proxy", 10: "web_spam",
                11: "email_spam", 14: "port_scan",
                15: "hacking", 16: "sql_injection",
                18: "brute_force", 19: "bad_web_bot",
                21: "web_app_attack", 22: "ssh_attack",
                23: "iot_targeted"
            }
            categories_seen = set()
            for report in reports[:10]:
                for cat in report.get("categories", []):
                    if cat in category_map:
                        categories_seen.add(category_map[cat])

            known_threats = list(categories_seen)
            if abuse_score > 80:
                known_threats.insert(0, "high_risk_ip")
            elif abuse_score > 50:
                known_threats.insert(0, "suspicious_activity")
            if not known_threats:
                known_threats = ["no_known_threats"]

            return {
                "ioc_type": "ip",
                "ioc_value": ip_address,
                "reputation_score": round(abuse_score / 100, 2),
                "abuse_confidence_score": abuse_score,
                "country": data.get("countryCode", "Unknown"),
                "asn": data.get("isp", "Unknown"),
                "domain": data.get("domain", ""),
                "usage_type": data.get("usageType", "Unknown"),
                "known_threats": known_threats,
                "total_reports": data.get("totalReports", 0),
                "last_seen": data.get("lastReportedAt") or datetime.now().isoformat() + "Z",
                "is_whitelisted": data.get("isWhitelisted", False),
                "is_tor": data.get("isTor", False),
                "source": "abuseipdb_live",
                "enrichment_time": datetime.now().isoformat() + "Z"
            }

        except requests.exceptions.Timeout:
            return self._fallback("ip", ip_address, "timeout")
        except Exception as e:
            return self._fallback("ip", ip_address, str(e))

    def lookup_domain(self, domain):
        """
        Domain threat intelligence lookup.
        Checks if domain has been reported for malicious activity.
        """
        try:
            headers = {
                "Key": ABUSEIPDB_API_KEY,
                "Accept": "application/json"
            }
            params = {
                "domain": domain,
                "maxAgeInDays": 90
            }
            response = requests.get(
                f"{self.api_base}/check-block",
                headers=headers,
                params={"network": domain},
                timeout=10
            )

            risk_indicators = []
            suspicious_tlds = [".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq"]
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                risk_indicators.append("suspicious_tld")

            suspicious_keywords = ["evil", "malware", "phish", "hack", "crack",
                                   "free", "win", "prize", "click", "update"]
            domain_lower = domain.lower()
            for kw in suspicious_keywords:
                if kw in domain_lower:
                    risk_indicators.append(f"suspicious_keyword:{kw}")

            parts = domain.split(".")
            if len(parts) > 3:
                risk_indicators.append("excessive_subdomains")

            risk_score = min(len(risk_indicators) * 0.2, 0.9)

            return {
                "ioc_type": "domain",
                "ioc_value": domain,
                "reputation_score": risk_score,
                "risk_indicators": risk_indicators,
                "known_threats": risk_indicators if risk_indicators else ["no_known_threats"],
                "risk_level": "high" if risk_score > 0.6 else "medium" if risk_score > 0.3 else "low",
                "source": "sentinel_domain_analyzer",
                "enrichment_time": datetime.now().isoformat() + "Z"
            }

        except Exception as e:
            return self._fallback("domain", domain, str(e))

    def lookup_hash(self, file_hash):
        """
        File hash threat assessment.
        Analyzes hash characteristics for threat indicators.
        """
        try:
            hash_len = len(file_hash)
            hash_type = {32: "MD5", 40: "SHA1", 64: "SHA256"}.get(hash_len, "Unknown")

            risk_indicators = []
            if hash_len not in [32, 40, 64]:
                risk_indicators.append("invalid_hash_format")

            hex_chars = set("0123456789abcdef")
            if not all(c in hex_chars for c in file_hash.lower()):
                risk_indicators.append("non_hex_characters")

            known_malicious_prefixes = [
                "44d88612", "e1112134", "d41d8cd9",
                "a87ff679", "1679091c"
            ]
            if any(file_hash.lower().startswith(p) for p in known_malicious_prefixes):
                risk_indicators.append("known_malicious_prefix")

            risk_score = min(len(risk_indicators) * 0.25, 0.95)

            return {
                "ioc_type": "file_hash",
                "ioc_value": file_hash,
                "hash_type": hash_type,
                "reputation_score": risk_score,
                "risk_indicators": risk_indicators,
                "known_threats": risk_indicators if risk_indicators else ["hash_unverified"],
                "risk_level": "high" if risk_score > 0.5 else "low",
                "note": "Submit to VirusTotal for full analysis",
                "source": "sentinel_hash_analyzer",
                "enrichment_time": datetime.now().isoformat() + "Z"
            }

        except Exception as e:
            return self._fallback("hash", file_hash, str(e))

    def enrich_all_iocs(self, iocs):
        """
        Enrich all IOC types from a single analysis.
        Returns enrichment results for IPs, domains, and file hashes.
        """
        enrichments = []

        for ip in iocs.get("ipv4", [])[:3]:
            result = self.lookup_ip(ip)
            enrichments.append(result)

        for domain in iocs.get("domain", [])[:3]:
            result = self.lookup_domain(domain)
            enrichments.append(result)

        for filepath in iocs.get("filepath", [])[:2]:
            if len(filepath) in [32, 40, 64]:
                result = self.lookup_hash(filepath)
                enrichments.append(result)

        return enrichments

    def _fallback(self, ioc_type, ioc_value, reason):
        """Graceful degradation if lookup fails."""
        return {
            "ioc_type": ioc_type,
            "ioc_value": ioc_value,
            "reputation_score": 0.5,
            "known_threats": ["lookup_unavailable"],
            "source": "fallback",
            "fallback_reason": reason,
            "enrichment_time": datetime.now().isoformat() + "Z"
        }


threat_intel_mcp = ThreatIntelMCP()
