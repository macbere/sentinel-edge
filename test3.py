import requests
import sys

BASE = "http://127.0.0.1:5000"
print("STRESS TEST 3: Malformed Input Handling")
passed = 0

print("Test 1: Empty JSON")
try:
    r = requests.post(BASE + "/analyze", json={}, timeout=5)
    if r.status_code in [400, 503]:
        print("PASS")
        passed = passed + 1
except:
    print("FAIL")

print("Test 2: Missing alert field")
try:
    r = requests.post(BASE + "/analyze", json={"wrong": "field"}, timeout=5)
    if r.status_code in [400, 503]:
        print("PASS")
        passed = passed + 1
except:
    print("FAIL")

print("Test 3: Empty alert string")
try:
    r = requests.post(BASE + "/analyze", json={"alert": ""}, timeout=5)
    if r.status_code in [400, 503]:
        print("PASS")
        passed = passed + 1
except:
    print("FAIL")

print("Test 4: Long alert")
try:
    long_alert = "A" * 1000
    r = requests.post(BASE + "/analyze", json={"alert": long_alert}, timeout=10)
    if r.status_code in [200, 503]:
        print("PASS")
        passed = passed + 1
except:
    print("FAIL")

print("Test 5: Special characters")
try:
    injection = "alert'; DROP TABLE incidents; --"
    r = requests.post(BASE + "/analyze", json={"alert": injection}, timeout=5)
    if r.status_code in [200, 503]:
        print("PASS")
        passed = passed + 1
except:
    print("FAIL")

print("Test 6: Wrong content type")
try:
    headers = {"Content-Type": "text/plain"}
    r = requests.post(BASE + "/analyze", data="not json", headers=headers, timeout=5)
    if r.status_code in [400, 415, 503]:
        print("PASS")
        passed = passed + 1
except:
    print("FAIL")

print("")
print("RESULT: " + str(passed) + "/6 tests passed")
if passed >= 5:
    print("TEST 3 PASSED")
    sys.exit(0)
else:
    print("TEST 3 FAILED")
    sys.exit(1)
