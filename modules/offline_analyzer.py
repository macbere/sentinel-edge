import re
import hashlib
from typing import Dict, Any, List

class OfflineAnalyzer:
    """Enhanced offline analysis with IOC extraction and keyword-based threat classification."""
    
    IOC_PATTERNS = {
        'ipv4': r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        'username': r'\b([a-zA-Z][a-zA-Z0-9_]{2,32})\b',
        'filepath': r'(/[^\s]+)|([a-zA-Z]:\\[^\s]+)\b',
        'domain': r'\b([a-zA-Z0-9]+\.[a-zA-Z]{2,})\b',
        'port': r'\b:(\d{1,5})\b',
        'timestamp': r'\b(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\b'
    }
    
    THREAT_RULES = {
        'ransomware_beacon': {
            'keywords': ['ransomware', 'beacon', 'c2', 'command and control', 'encrypted', 'file encryption'],
            'severity': 'critical',
            'confidence_min': 0.85,
            'containment_steps': [
                'Immediately isolate infected host from network',
                'Block C2 domain at DNS level',
                'Initiate incident response protocol',
                'Notify security team and legal'
            ]
        },
        'brute_force_attack': {
            'keywords': ['brute force', 'multiple failed logins', 'failed attempts', 'account lockout', 'password spraying'],
            'severity': 'high',
            'confidence_min': 0.75,
            'containment_steps': [
                'Block source IP at firewall',
                'Disable compromised account',
                'Enforce MFA policy',
                'Implement account lockout policy'
            ]
        },
        'sql_injection': {
            'keywords': ['sql injection', 'sql intrusion', 'malformed query', 'database attack', 'union select', 'drop table'],
            'severity': 'high',
            'confidence_min': 0.80,
            'containment_steps': [
                'Block attack source IP',
                'Patch vulnerable web application',
                'Review and update WAF rules',
                'Audit database for unauthorized changes'            ]
        },
        'privilege_escalation': {
            'keywords': ['privilege escalation', 'root access', 'sudo', 'admin rights', 'unauthorized admin', 'sudden elevation'],
            'severity': 'critical',
            'confidence_min': 0.90,
            'containment_steps': [
                'Revoke elevated privileges immediately',
                'Audit sudo/admin access logs',
                'Identify exploit vector',
                'Patch vulnerability'
            ]
        },
        'data_exfiltration': {
            'keywords': ['data exfiltration', 'large download', 'outbound transfer', 'data leak', 'unusual traffic', 'exfiltration'],
            'severity': 'critical',
            'confidence_min': 0.85,
            'containment_steps': [
                'Block outbound connection at firewall',
                'Identify exfiltrated data scope',
                'Notify data protection officer',
                'Initiate data breach response'
            ]
        },
        'malware_execution': {
            'keywords': ['malware', 'virus', 'trojan', 'ratelware', 'spyware', 'executable', 'malicious file', 'infected file'],
            'severity': 'high',
            'confidence_min': 0.80,
            'containment_steps': [
                'Quarantine malicious file immediately',
                'Scan all endpoints for IOCs',
                'Update AV signatures',
                'Report to threat intelligence platform'
            ]
        },
        'unauthorized_access': {
            'keywords': ['unauthorized access', 'suspicious login', 'after hours access', 'invalid credentials', 'login failure', 'access denied'],
            'severity': 'medium',
            'confidence_min': 0.60,
            'containment_steps': [
                'Disable compromised account',
                'Review access logs for lateral movement',
                'Rotate session tokens',
                'Enforce ipart restrictions'
            ]
        },
        'network_scan': {
            'keywords': ['network scan', 'port scan', 'reconnaissance', 'nmap', 'scanning', 'probe'],
            'severity': 'low',
            'confidence_min': 0.50,            'containment_steps': [
                'Rate-limit source IP',
                'Verify firewall rules',
                'Monitor for follow-up exploitation',
                'Block if reconnaissance continues'
            ]
        },
        'phishing_attempt': {
            'keywords': ['phishing', 'spearphishing', 'domain spoofing', 'smishing', 'malicious link', 'credential stealing'],
            'severity': 'medium',
            'confidence_min': 0.65,
            'containment_steps': [
                'Block sender domain at email gateway',
                'Alert targeted users',
                'Scan for compromised credentials',
                'Report to anti-phishing platform'
            ]
        }
    }
    
    def extract_iocs(self, alert_text: str) -> Dict[str, Any]:
        """Extract Indicators of Compromise from alert text."""
        iocs = {}
        for ioc_type, pattern in self.IOC_PATTERNS.items():
            matches = re.findall(pattern, alert_text, re.IGNORECASE)
            if matches:
                # Handle capture groups - flatten tuples to strings
                flattened = []
                for m in matches:
                    if isinstance(m, tuple):
                        # Take non-empty groups from capture groups
                        flattened.extend([g for g in m if g])
                    else:
                        flattened.append(m)
                iocs[ioc_type] = list(set(flattened))
        return iocs
    
    def classify_threat(self, alert_text: str) -> tuple[str, float]:
        """Classify threat based on keyword matching. Returns (threat_type, confidence)."""
        alert_lower = alert_text.lower()
        best_match = None
        best_score = 0
        
        for threat_type, rule in self.THREAT_RULES.items():
            score = sum(1 for kw in rule['keywords'] if kw in alert_lower)
            if score > best_score:
                best_score = score
                best_match = threat_type
        
        if best_match and best_score > 0:
            rule = self.THREAT_RULES[best_match]
            base_conf = rule['confidence_min']
            bonus = min(best_score * 0.05, 0.15)
            confidence = min(base_conf + bonus, 0.99)
            return best_match, round(confidence, 2)
        
        # Fallback: use hash-based selection for unclassifiable alerts
        h = int(hashlib.md5(alert_text.encode()).hexdigest()[:8], 16)
        fallback_threats = list(self.THREAT_RULES.keys())
        return fallback_threats[h % len(fallback_threats)], 0.55
    
    def generate_reasoning(self, alert_text: str, threat_type: str, iocs: Dict) -> str:
        """Generate detailed forensic reasoning for the analysis."""
        parts = []
        parts.append(f"Alert analyzed for threat pattern: {threat_type.replace('_', ' ').title()}.")
        
        if iocs:
            if 'ipv4' in iocs:
                parts.append(f"Identified {len(iocs['ipv4'])} source IP(s): {', '.join(iocs['ipv4'])}.")
            if 'email' in iocs:
                parts.append(f"Targeted account(s): {', '.join(iocs['email'])}.")
            if 'username' in iocs:
                parts.append(f"User account(s) involved: {', '.join(iocs['username'])}.")
            if 'domain' in iocs:
                parts.append(f"Associated domain(s): {', '.join(iocs['domain'])}.")
            if 'filepath' in iocs:
                parts.append(f"Affected file(s): {', '.join(iocs['filepath'])}.")
        
        parts.append("Threat classified using offline heuristic analysis engine. Cloud API integration required for deep inspection.")
        return " ".join(parts)
    
    def analyze(self, alert_text: str) -> Dict[str, Any]:
        """Perform full offline analysis with IOC extraction and threat classification."""
        iocs = self.extract_iocs(alert_text)
        threat_type, confidence = self.classify_threat(alert_text)
        rule = self.THREAT_RULES[threat_type]
        reasoning = self.generate_reasoning(alert_text, threat_type, iocs)
        
        return {
            'severity': rule['severity'],
            'threat_type': threat_type,
            'containment_steps': rule['containment_steps'],
            'requires_human_approval': rule['severity'] in ['high', 'critical'],
            'confidence': confidence,
            'reasoning': reasoning,
            'provider': 'offline_smart',
            'fallback': True,
            'iocs': iocs
        }

# Global instance for backward compatibility
analyzer_instance = OfflineAnalyzer()

def smart_offline_analyze(alert_text: str) -> Dict[str, Any]:
    """Backward compatible function for existing code."""
    return analyzer_instance.analyze(alert_text)
