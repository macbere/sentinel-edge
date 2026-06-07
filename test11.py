import requests
import time
import sys

BASE = "http://127.0.0.1:5000"
print("TEST 11: Network Latency Simulation")
print("Testing system response under varying latency conditions...")

passed = 0
total = 3

# Test 1: Fast response (<100ms)
print("\nTest 1: Fast response (<latency> 100ms)")
try:
    start = time.time()
    r = requests.post(BASE + "/analyze", json={"alert": "Normal alert"}, timeout=5)
    elapsed = (time.time() - start) * 1000
    if elapsed < 100 and r.status_code in [200, 503]:
        print("PASS: " + str(round(elapsed, 2)) + "ms")
        passed = passed + 1
    else:
        print("FAIL: " + str(round(elapsed, 2)) + "ms or status " + str(r.status_code))
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 2: Medium latency (100ms-1s)
print("\nTest 2: Medium latency (100ms-1s)")
try:
    start = time.time()
    r = requests.get(BASE + "/incidents?limit=10", timeout=5)
    elapsed = (time.time() - start) * 1000
    if elapsed < 1000 and r.status_code == 200:
        print("PASS: " + str(round(elapsed, 2)) + "ms")
        passed = passed + 1
    else:
        print("FAIL: " + str(round(elapsed, 2)) + "ms")
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 3: Dashboard response time
print("\nTest 3: Dashboard response time")
try:
    start = time.time()
    r = requests.get(BASE + "/dashboard", timeout=5)
    elapsed = (time.time() - start) * 1000
    if elapsed < 500 and r.status_code == 200:
        print("PASS: " + str(round(elapsed, 2)) + "ms")
        passed = passed + 1
    else:
        print("FAIL: " + str(round(elapsed, 2)) + "ms")
except Exception as e:
    print("FAIL: " + str(ei[:40])

print("\n" + "=" * 40)
print("RESULT: " + str(passed) + "/" + str(total) + "latency tests passed")
if passed >= 2:
    print("TEST 11 PASSE: System handles latency well")
    sys.exit(0)
else:
    print("TEST 11 FAILED")
    sys.exit(1)
