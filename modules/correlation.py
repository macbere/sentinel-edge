"""
Automated Incident Correlation Engine
Identifies patterns, groups related incidents, and detects attack campaigns
"""
import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict


class CorrelationEngine:
    """Analyzes incidents to find correlations and attack patterns"""

    def __init__(self, db_path: str = "sentinel_memory.db"):
        self.db_path = db_path

    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        return conn

    def _extract_iocs_from_analysis(self, analysis_json: str) -> Dict[str, List[str]]:
        iocs = {"ipv4": [], "username": [], "domain": [], "filepath": []}
        try:
            ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
            iocs["ipv4"] = re.findall(ipv4_pattern, analysis_json)

            username_pattern = r'"username":\s*\[([^\]]+)\]'
            matches = re.findall(username_pattern, analysis_json)
            for match in matches:
                usernames = re.findall(r'"([^"]+)"', match)
                iocs["username"].extend(usernames)

            domain_pattern = r'"domain":\s*\[([^\]]+)\]'
            matches = re.findall(domain_pattern, analysis_json)
            for match in matches:
                domains = re.findall(r'"([^"]+)"', match)
                iocs["domain"].extend(domains)

            filepath_pattern = r'"filepath":\s*\[([^\]]+)\]'
            matches = re.findall(filepath_pattern, analysis_json)
            for match in matches:
                filepaths = re.findall(r'"([^"]+)"', match)
                iocs["filepath"].extend(filepaths)
        except Exception:
            pass
        return iocs

    def _calculate_time_proximity_score(self, timestamp1: str, timestamp2: str) -> float:
        try:
            dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
            time_diff = abs((dt1 - dt2).total_seconds())
            if time_diff <= 3600:
                return 1.0
            elif time_diff <= 86400:
                return 0.5
            else:
                return 0.1
        except Exception:
            return 0.0

    def _calculate_ioc_overlap_score(self, iocs1: Dict, iocs2: Dict) -> float:
        if not iocs1 or not iocs2:
            return 0.0
        total_overlap = 0
        total_iocs = 0
        for ioc_type in ["ipv4", "username", "domain", "filepath"]:
            set1 = set(iocs1.get(ioc_type, []))
            set2 = set(iocs2.get(ioc_type, []))
            if set1 or set2:
                overlap = len(set1 & set2)
                total = len(set1 | set2)
                if total > 0:
                    total_overlap += overlap / total
                    total_iocs += 1
        return total_overlap / total_iocs if total_iocs > 0 else 0.0

    def _calculate_threat_type_score(self, threat_type1: str, threat_type2: str) -> float:
        if threat_type1 == threat_type2:
            return 1.0
        attack_chain = {
            "network_scan": ["brute_force_attack", "unauthorized_access"],
            "brute_force_attack": ["unauthorized_access", "privilege_escalation"],
            "unauthorized_access": ["privilege_escalation", "data_exfiltration"],
            "privilege_escalation": ["data_exfiltration", "ransomware_beacon"],
            "malware_execution": ["ransomware_beacon", "data_exfiltration"]
        }
        if threat_type1 in attack_chain and threat_type2 in attack_chain[threat_type1]:
            return 0.8
        if threat_type2 in attack_chain and threat_type1 in attack_chain[threat_type2]:
            return 0.8
        return 0.0

    def _find_shared_iocs(self, iocs1: Dict, iocs2: Dict) -> Dict[str, List[str]]:
        shared = {}
        for ioc_type in ["ipv4", "username", "domain", "filepath"]:
            set1 = set(iocs1.get(ioc_type, []))
            set2 = set(iocs2.get(ioc_type, []))
            common = list(set1 & set2)
            if common:
                shared[ioc_type] = common
        return shared

    def _calculate_time_span(self, timestamp1: str, timestamp2: str) -> str:
        try:
            dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
            diff = abs((dt1 - dt2).total_seconds())
            if diff < 60:
                return f"{int(diff)} seconds"
            elif diff < 3600:
                return f"{int(diff/60)} minutes"
            elif diff < 86400:
                return f"{int(diff/3600)} hours"
            else:
                return f"{int(diff/86400)} days"
        except Exception:
            return "unknown"

    def _identify_attack_pattern(self, threat_types: List[str]) -> str:
        if not threat_types:
            return "Unknown"
        stages = {
            "reconnaissance": ["network_scan"],
            "initial_access": ["brute_force_attack", "unauthorized_access", "phishing_attempt"],
            "execution": ["malware_execution", "sql_injection"],
            "persistence": ["privilege_escalation"],
            "impact": ["data_exfiltration", "ransomware_beacon"]
        }
        detected_stages = []
        for threat_type in threat_types:
            for stage, types in stages.items():
                if threat_type in types and stage not in detected_stages:
                    detected_stages.append(stage)
        if not detected_stages:
            return " -> ".join(threat_types)
        return " -> ".join(detected_stages)

    def _calculate_campaign_severity(self, incidents: List[Dict]) -> str:
        severity_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        max_severity = 0
        for inc in incidents:
            severity = inc.get("severity", "low")
            score = severity_scores.get(severity, 1)
            max_severity = max(max_severity, score)
        if len(incidents) >= 5:
            max_severity = min(max_severity + 1, 4)
        severity_map = {4: "critical", 3: "high", 2: "medium", 1: "low"}
        return severity_map.get(max_severity, "low")

    def correlate_incidents(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        conn = self._get_db_connection()
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        query = """
            SELECT id, alert_type, analysis, timestamp, status
            FROM incidents
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        """
        incidents = conn.execute(query, (cutoff_time,)).fetchall()
        conn.close()

        if len(incidents) < 2:
            return []

        incident_data = []
        for inc in incidents:
            iocs = self._extract_iocs_from_analysis(inc["analysis"])
            try:
                analysis_dict = json.loads(inc["analysis"]) if isinstance(inc["analysis"], str) else inc["analysis"]
            except Exception:
                analysis_dict = {}

            incident_data.append({
                "id": inc["id"],
                "alert_text": inc["alert_type"],
                "timestamp": inc["timestamp"],
                "threat_type": analysis_dict.get("threat_type", "unknown"),
                "severity": analysis_dict.get("severity", "unknown"),
                "iocs": iocs
            })

        correlations = []
        processed_pairs = set()

        for i, inc1 in enumerate(incident_data):
            for j, inc2 in enumerate(incident_data):
                if i >= j:
                    continue
                pair_key = (min(inc1["id"], inc2["id"]), max(inc1["id"], inc2["id"]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)

                time_score = self._calculate_time_proximity_score(inc1["timestamp"], inc2["timestamp"])
                ioc_score = self._calculate_ioc_overlap_score(inc1["iocs"], inc2["iocs"])
                threat_score = self._calculate_threat_type_score(inc1["threat_type"], inc2["threat_type"])

                correlation_score = (time_score * 0.3 + ioc_score * 0.5 + threat_score * 0.2)

                if correlation_score > 0.4:
                    correlations.append({
                        "incident_ids": [inc1["id"], inc2["id"]],
                        "correlation_score": round(correlation_score, 2),
                        "time_score": round(time_score, 2),
                        "ioc_score": round(ioc_score, 2),
                        "threat_score": round(threat_score, 2),
                        "shared_iocs": self._find_shared_iocs(inc1["iocs"], inc2["iocs"]),
                        "threat_types": [inc1["threat_type"], inc2["threat_type"]],
                        "time_span": self._calculate_time_span(inc1["timestamp"], inc2["timestamp"])
                    })

        campaigns = self._group_into_campaigns(correlations, incident_data)
        return campaigns

    def _group_into_campaigns(self, correlations: List[Dict], incidents: List[Dict]) -> List[Dict]:
        if not correlations:
            return []

        graph = defaultdict(set)
        for corr in correlations:
            id1, id2 = corr["incident_ids"]
            graph[id1].add(id2)
            graph[id2].add(id1)

        visited = set()
        campaigns = []

        for incident_id in graph:
            if incident_id in visited:
                continue
            campaign_ids = []
            queue = [incident_id]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                campaign_ids.append(current)
                queue.extend(graph[current] - visited)

            if len(campaign_ids) >= 2:
                campaign_incidents = [inc for inc in incidents if inc["id"] in campaign_ids]
                campaign_incidents.sort(key=lambda x: x["timestamp"])

                relevant_corrs = [c for c in correlations if any(i in campaign_ids for i in c["incident_ids"])]
                avg_correlation = sum(c["correlation_score"] for c in relevant_corrs) / max(len(relevant_corrs), 1)

                threat_types = [inc["threat_type"] for inc in campaign_incidents]
                attack_pattern = self._identify_attack_pattern(threat_types)

                all_iocs = {}
                for inc in campaign_incidents:
                    for ioc_type, values in inc["iocs"].items():
                        if ioc_type not in all_iocs:
                            all_iocs[ioc_type] = []
                        all_iocs[ioc_type].extend(values)
                for ioc_type in all_iocs:
                    all_iocs[ioc_type] = list(set(all_iocs[ioc_type]))

                primary_ip = all_iocs.get('ipv4', ['Unknown'])[0] if all_iocs.get('ipv4') else 'Unknown'

                campaigns.append({
                    "campaign_id": f"campaign_{campaign_incidents[0]['timestamp'][:10]}_{campaign_ids[0]}",
                    "incident_ids": campaign_ids,
                    "incident_count": len(campaign_ids),
                    "avg_correlation_score": round(avg_correlation, 2),
                    "attack_pattern": attack_pattern,
                    "threat_types": list(set(threat_types)),
                    "time_span": self._calculate_time_span(
                        campaign_incidents[0]["timestamp"],
                        campaign_incidents[-1]["timestamp"]
                    ),
                    "start_time": campaign_incidents[0]["timestamp"],
                    "end_time": campaign_incidents[-1]["timestamp"],
                    "severity": self._calculate_campaign_severity(campaign_incidents),
                    "threat_actor_profile": {
                        "actor_id": f"APT-Unknown-{primary_ip}",
                        "known_iocs": all_iocs,
                        "tactics": list(set(threat_types)),
                        "confidence": round(avg_correlation, 2)
                    }
                })

        campaigns.sort(key=lambda x: x["avg_correlation_score"], reverse=True)
        return campaigns


correlation_engine = CorrelationEngine()
