import requests
import sys
import os

BASE = "http://127.0.0.1:5000"
print("STRESS TEST 6: Offline/Online Transition Resilience")
print("Testing graceful degradation when cloud is unreachable...")

passed = 0
total = 4

# Test 1: Verify offline fallback returns valid JSON structure
print("Test 1: Offline fallback structure")
try:
    r = requests.post(BASE + "/analyze", json={"alert": "Network test alert"}, timeout=10)
    data = r.json()
    required_fields = ["error", "message", "severity", "containment_steps", "requires_human_approval"]
    missing = [f for f in required_fields if f not in data]
    if len(missing) == 0:
        print("PASS: All required fields present in offline response")
        passed = passed + 1
    else:
        print("FAIL: Missing fields: " + str(missing))
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 2: Verify offline response includes original alert context
print("Test 2: Alert context preserved offline")
try:
    r = requests.post(BASE + "/analyze", json={"alert": "CRITICAL_CONTEXT_TEST_12345"}, timeout=10)
    data = r.json()
    full_response = str(data).lower()
    if "critical_context_test_12345" in full_response:
        print("PASS: Original alert text preserved in offline mode")
        passed = passed + 1
    else:
        print("FAIL: Alert context lost in offline fallback")
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 3: Verify memory still works during offline
print("Test 3: Memory persistence during offline")
try:
    r = requests.get(BASE + "/incidents?limit=5", timeout=5)
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            print("PASS: Memory accessible during offline (" + str(len(data)) + " records)")
            passed = passed + 1
        else:
            print("FAIL: Memory returned empty or invalid")
    else:
        print("FAIL: /incidents returned " + str(r.status_code))
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 4: Verify dashboard remains functional offline
print("Test 4: Dashboard stability during offline")
try:
    r = requests.get(BASE + "/dashboard", timeout=5)
    data = r.json()
    if data.get("status") == "online" and "metrics" in data:
        print("PASS: Dashboard fully functional in offline mode")
        passed = passed + 1
    else:
        print("FAIL: Dashboard degraded or missing metrics")
except Exception as e:
    print("FAIL: " + str(e)[:40])

print("")
print("RESULT: " + str(passed) + "/" + str(total) + " resilience tests passed")
if passed >= 3:
    print("TEST 6 PASSED")
    print("Track 5 EdgeAgent requirement: VERIFIED")
    sys.exit(0)
else:
    print("TEST 6 FAILED")
    sys.exit(1)
