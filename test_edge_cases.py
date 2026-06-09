#!/usr/bin/env python3
"""
Comprehensive Edge Case Testing for Sentinel Edge
Tests system robustness, error handling, and performance limits
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
TEST_RESULTS = []

def log_test(name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    TEST_RESULTS.append({
        "name": name,
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    print(f"{status} - {name}")
    if details and not passed:
        print(f"   Details: {details}")

def test_1_health_endpoint():
    """Test 1: Health endpoint availability"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=30)
        data = r.json()
        passed = r.status_code == 200 and data.get("status") == "online"
        log_test("Health Endpoint", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Health Endpoint", False, str(e))

def test_2_malformed_json():
    """Test 2: Malformed JSON handling"""
    try:
        r = requests.post(f"{BASE_URL}/analyze", 
                         data="not json",
                         headers={"Content-Type": "application/json"},
                         timeout=30)
        passed = r.status_code in [400, 415]
        log_test("Malformed JSON", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Malformed JSON", False, str(e))
def test_3_missing_alert_field():
    """Test 3: Missing required alert field"""
    try:
        r = requests.post(f"{BASE_URL}/analyze",
                         json={"wrong_field": "test"},
                         timeout=30)
        passed = r.status_code == 400
        log_test("Missing Alert Field", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Missing Alert Field", False, str(e))

def test_4_empty_alert():
    """Test 4: Empty alert string"""
    try:
        r = requests.post(f"{BASE_URL}/analyze",
                         json={"alert": ""},
                         timeout=30)
        passed = r.status_code in [200, 400]  # Either handled or rejected
        log_test("Empty Alert", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Empty Alert", False, str(e))

def test_5_very_long_alert():
    """Test 5: Very long alert (10KB)"""
    try:
        long_alert = "Suspicious activity " * 500
        r = requests.post(f"{BASE_URL}/analyze",
                         json={"alert": long_alert},
                         timeout=60)
        passed = r.status_code == 200
        log_test("Very Long Alert (10KB)", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Very Long Alert (10KB)", False, str(e))

def test_6_unicode_characters():
    """Test 6: Unicode and special characters"""
    try:
        r = requests.post(f"{BASE_URL}/analyze",
                         json={"alert": "Suspicious login from 10.0.0.1 恶意活动 🚨"},
                         timeout=30)
        passed = r.status_code == 200
        log_test("Unicode Characters", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Unicode Characters", False, str(e))

def test_7_sql_injection_attempt():
    """Test 7: SQL injection in alert field"""
    try:
        r = requests.post(f"{BASE_URL}/analyze",                         json={"alert": "'; DROP TABLE incidents; --"},
                         timeout=30)
        # Should be sanitized or rejected
        passed = r.status_code in [200, 400]
        log_test("SQL Injection Attempt", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("SQL Injection Attempt", False, str(e))

def test_8_multiple_iocs():
    """Test 8: Alert with multiple IOCs"""
    try:
        alert = "Multiple suspicious activities: Login from 192.168.1.100, Connection to 10.0.0.50:443, User admin attempted access, File /etc/passwd accessed, Domain evil.com contacted"
        r = requests.post(f"{BASE_URL}/analyze",
                         json={"alert": alert},
                         timeout=30)
        data = r.json()
        iocs = data.get("iocs", {})
        passed = r.status_code == 200 and len(iocs) >= 3
        details = f"Found {len(iocs)} IOC types: {list(iocs.keys())}"
        log_test("Multiple IOCs Extraction", passed, details)
    except Exception as e:
        log_test("Multiple IOCs Extraction", False, str(e))

def test_9_rapid_sequential_requests():
    """Test 9: 20 rapid sequential requests"""
    try:
        start = time.time()
        success_count = 0
        for i in range(20):
            r = requests.post(f"{BASE_URL}/analyze",
                            json={"alert": f"Test alert {i}"},
                            timeout=30)
            if r.status_code == 200:
                success_count += 1
        elapsed = time.time() - start
        passed = success_count >= 18  # Allow 10% failure
        details = f"{success_count}/20 successful in {elapsed:.2f}s"
        log_test("Rapid Sequential (20 requests)", passed, details)
    except Exception as e:
        log_test("Rapid Sequential (20 requests)", False, str(e))

def test_10_dashboard_metrics():
    """Test 10: Dashboard metrics accuracy"""
    try:
        r = requests.get(f"{BASE_URL}/dashboard", timeout=30)
        data = r.json()
        metrics = data.get("metrics", {})
        passed = (r.status_code == 200 and 
                 "total_incidents" in metrics and
                 "pending_approval" in metrics)
        details = f"Total incidents: {metrics.get('total_incidents', 0)}"
        log_test("Dashboard Metrics", passed, details)
    except Exception as e:
        log_test("Dashboard Metrics", False, str(e))

def test_11_audit_logging():
    """Test 11: Audit logging completeness"""
    try:
        # Make a test request
        requests.post(f"{BASE_URL}/analyze",
                     json={"alert": "Audit test alert"},
                     timeout=30)
        time.sleep(0.5)  # Wait for log
        
        r = requests.get(f"{BASE_URL}/audit", timeout=30)
        data = r.json()
        summary = data.get("summary", {})
        passed = r.status_code == 200 and summary.get("total_requests", 0) > 0
        details = f"Total logged requests: {summary.get('total_requests', 0)}"
        log_test("Audit Logging", passed, details)
    except Exception as e:
        log_test("Audit Logging", False, str(e))

def test_12_incident_persistence():
    """Test 12: Incident persistence in database"""
    try:
        # Create unique alert
        unique_alert = f"Unique test alert {int(time.time())}"
        r1 = requests.post(f"{BASE_URL}/analyze",
                          json={"alert": unique_alert},
                          timeout=30)
        incident_id = r1.json().get("incident_id")
        
        # Retrieve incident
        r2 = requests.get(f"{BASE_URL}/incidents", timeout=30)
        response_data = r2.json()
        incidents = response_data if isinstance(response_data, list) else response_data.get("incidents", [])
        
        found = any(i.get("id") == incident_id for i in incidents)
        passed = r1.status_code == 200 and found
        details = f"Incident {incident_id} persisted"
        log_test("Incident Persistence", passed, details)
    except Exception as e:
        log_test("Incident Persistence", False, str(e))
def test_13_threat_classification_accuracy():
    """Test 13: Threat classification accuracy"""
    try:
        test_cases = [
            ("Ransomware beacon detected from 10.0.0.77 targeting finance-db", "ransomware_beacon"),
            ("Brute force SSH attack with 500 failed attempts from 192.168.1.100", "brute_force_attack"),
            ("SQL injection attempt detected in login form from 203.0.113.42", "sql_injection"),
            ("Unauthorized access detected with invalid credentials from 10.0.0.99", "unauthorized_access")
        ]
        
        correct = 0
        for alert, expected_type in test_cases:
            r = requests.post(f"{BASE_URL}/analyze",
                            json={"alert": alert},
                            timeout=30)
            data = r.json()
            if data.get("threat_type") == expected_type:
                correct += 1
        
        passed = correct >= 3  # 75% accuracy
        details = f"{correct}/{len(test_cases)} correct classifications"
        log_test("Threat Classification Accuracy", passed, details)
    except Exception as e:
        log_test("Threat Classification Accuracy", False, str(e))

def test_14_concurrent_requests():
    """Test 14: 10 concurrent requests"""
    try:
        import threading
        
        results = []
        def make_request(i):
            try:
                r = requests.post(f"{BASE_URL}/analyze",
                                json={"alert": f"Concurrent test {i}"},
                                timeout=60)
                results.append(r.status_code)
            except:
                results.append(500)
        
        threads = [threading.Thread(target=make_request, args=(i,)) for i in range(10)]
        start = time.time()
        [t.start() for t in threads]
        [t.join() for t in threads]
        elapsed = time.time() - start
        
        success = results.count(200)
        passed = success >= 6
        details = f"{success}/10 successful in {elapsed:.2f}s"
        log_test("Concurrent Requests (10)", passed, details)
    except Exception as e:
        log_test("Concurrent Requests (10)", False, str(e))

def test_15_endpoint_discovery():
    """Test 15: All endpoints accessible"""
    try:
        endpoints = ["/health", "/dashboard", "/incidents", "/audit"]
        accessible = 0
        
        for endpoint in endpoints:
            try:
                r = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
                if r.status_code == 200:
                    accessible += 1
            except:
                pass
        
        passed = accessible == len(endpoints)
        details = f"{accessible}/{len(endpoints)} endpoints accessible"
        log_test("Endpoint Discovery", passed, details)
    except Exception as e:
        log_test("Endpoint Discovery", False, str(e))

def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("EDGE CASE TESTING SUMMARY")
    print("="*70)
    
    total = len(TEST_RESULTS)
    passed = sum(1 for t in TEST_RESULTS if t["passed"])
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    
    if failed > 0:
        print("\nFailed Tests:")
        for test in TEST_RESULTS:
            if not test["passed"]:
                print(f"  ❌ {test['name']}: {test['details']}")
    
    print("\n" + "="*70)
    
    # Save results to file
    with open("edge_case_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "results": TEST_RESULTS
        }, f, indent=2)
    
    print(f"Results saved to: edge_case_results.json")
    print("="*70)

if __name__ == "__main__":
    print("Starting Edge Case Testing Suite...")
    print(f"Target: {BASE_URL}\n")
    
    # Run all tests
    test_1_health_endpoint()
    test_2_malformed_json()
    test_3_missing_alert_field()
    test_4_empty_alert()
    test_5_very_long_alert()
    test_6_unicode_characters()
    test_7_sql_injection_attempt()
    test_8_multiple_iocs()
    test_9_rapid_sequential_requests()
    test_10_dashboard_metrics()
    test_11_audit_logging()
    test_12_incident_persistence()
    test_13_threat_classification_accuracy()
    test_14_concurrent_requests()
    test_15_endpoint_discovery()
    
    # Print summary
    print_summary()
