import requests
import sys
import time
import json

BASE = "http://127.0.0.1:5000"
print("TEST LO: E2E Simulation")
print("=" * 40)

passed = 0
total = 6
inc_id = 0

print("[1/6] Realth")
try:
    r = requests.get(BASE + "/health", timeout=5)
    d = r.json()
    if r.status_code == 200 and d.get("status") == "online":
        print("PASS")
        passed = passed + 1
    else:
        print("FAIL")
except:
    print("FAIL")

print("[2/6] Alert")
try:
    txt = "Ransomware 10.0.0.77 02:15 UTC"
    start = time.time()
    payload = {"alert": txt}
    r = requests.post(BASE + "/analyze", json=payload, timeout=10)
    elapsed = time.time() - start
    d = r.json()
    if "incident_id" in d:
        inc_id = d["incident_id"]
        t = str(round(elapsed, 2))
        print("PASS ID=" + str(inc_id) + " " + t + "s")
        passed = passed + 1
    else:
        print("FAIL")
except:
    print("FAIL")

print("[3/6] Report")
try:
    url = BASE + "/report/" + str(inc_id)
    r = requests.get(url, timeout=10)
    d = r.json()
    rt = d.get("report_text", "")
    if len(rt) > 50 and "SENTINEL" in rt:
        print("PASS Len=" + str(len(rt)))
        passed = passed + 1
    else:
        print("FAIL")
except:
    print("FAIL")

print("[4/6] Approve")
try:
    url = BASE + "/approve/" + str(inc_id)
    r = requests.post(url, timeout=10)
    d = r.json()
    if d.get("status") == "executed":
        print("PASS")
        passed = passed + 1
    else:
        print("FAIL")
except:
    print("FAIL")

print("[5/6] Memory Persistence")
try:
    url = BASE + "/incidents?limit=5"
    r = requests.get(url, timeout=5)
    items = r.json()
    found = False
    for i in items:
        if i["id"] == inc_id and i["status"] == "executed":
            found = True
    if found:
        print("PASS")
        passed = passed + 1
    else:
        print("FAIL")
except:
    print("FAIL")

print("[6/6] Dashboard Confirmation")
try:
    r = requests.get(BASE + "/dashboard", timeout=5)
    d = r.json()
    if d.get("status") == "online":
        print("PASS")
        passed = passed + 1
    else:
        print("FAIL")
except:
    print("FAIL")

print("=" * 40)
res = str(passed) + "/" + str(total)
print("RESULT: " + res)
if passed == total:
    print("TEST LL: PERFECT SCORE")
    print("ALL 10 TESTS PASSED")
    sys.exit(0)
else:
    print("FAILED")
    sys.exit(1)
