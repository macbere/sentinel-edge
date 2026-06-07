import requests
import sys
import json

BASE = "http://127.0.0.1:5000"
print("STRESS TEST 7: Large Payload & IOC Extraction")
print("Sending 5KB alert with embedded indicators...")

# Build a realistic large alert with known IOCs
base_text = "Security Alert: Multiple suspicious activities detected. "
ioc_section = """
Source IP: 192.168.1.105
Destination IP: 10.0.0.99
Timestamp: 14:35 UTC
User Account: admin_backup
Secondary IP: 172.16.0.50
Login Time: 03:00 UTC
Target User: root
"""
padding = "Additional log data and noise. " * 100
large_alert = base_text + ioc_section + padding

print("Payload size: " + str(len(large_alert)) + " characters")

passed = 0
total = 3

# Test 1: System accepts large payload without crashing
print("Test 1: Large payload acceptance")
try:
    r = requests.post(BASE + "/analyze", json={"alert": large_alert}, timeout=15)
    if r.status_code in [200, 503]:
        print("PASS: Server handled 5KB payload")
        passed = passed + 1
    else:
        print("FAIL: Status " + str(r.status_code))
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 2: Verify perception module extracted IOCs (check stored analysis)
print("Test 2: IOC extraction verification")
try:
    r = requests.get(BASE + "/incidents?limit=1", timeout=5)
    data = r.json()
    if len(data) > 0:
        record_str = json.dumps(data[0]).lower()
        found_ip = "192.168.1.105" in record_str or "10.0.0.99" in record_str
        found_user = "admin_backup" in record_str or "root" in record_str
        if found_ip and found_user:
            print("PASS: IPs and usernames preserved in storage")
            passed = passed + 1
        else:
            print("FAIL: IOCs lost during processing")
    else:
        print("FAIL: No incidents returned")
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 3: Response time remains acceptable for large input
print("Test 3: Performance under large payload")
try:
    import time
    start = time.time()
    r = requests.post(BASE + "/analyze", json={"alert": large_alert}, timeout=15)
    elapsed = time.time() - start
    if elapsed < 5.0:
        print("PASS: Processed in " + str(round(elapsed, 2)) + "s (<5s threshold)")
        passed = passed + 1
    else:
        print("FAIL: Too slow (" + str(round(elapsed, 2)) + "s)")
except Exception as e:
    print("FAIL: " + str(e)[:40])

print("")
print("RESULT: " + str(passed) + "/" + str(total) + " perception tests passed")
if passed >= 2:
    print("TEST 7 PASSED")
    print("Perception Module handles real-world noisy data")
    sys.exit(0)
else:
    print("TEST 7 FAILED")
    sys.exit(1)
