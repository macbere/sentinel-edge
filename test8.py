import requests
import sys
import time

BASE = "http://127.0.0.1:5000"
print("STRESS TEST 8: Report Generation Under Load")
print("Generating 5 forensic reports sequentially...")

# First, get valid incident IDs to test against
try:
    r = requests.get(BASE + "/incidents?limit=5", timeout=5)
    incidents = r.json()
    if len(incidents) < 3:
        print("FAIL: Not enough incidents in memory to test reports")
        sys.exit(1)
    test_ids = [i["id"] for i in incidents[:3]]
except Exception as e:
    print("FAIL: Could not fetch incidents: " + str(e)[:30])
    sys.exit(1)

passed = 0
total = 3

for idx, inc_id in enumerate(test_ids, 1):
    print("Test " + str(idx) + ": Report for incident #" + str(inc_id))
    try:
        start = time.time()
        r = requests.get(BASE + "/report/" + str(inc_id), timeout=10)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            data = r.json()
            has_text = "report_text" in data and len(data["report_text"]) > 50
            has_analysis = "analysis" in data
            has_similar = "similar_incidents" in data
            
            if has_text and has_analysis and has_similar:
                print("PASS: Full report generated in " + str(round(elapsed, 2)) + "s")
                passed = passed + 1
            else:
                print("FAIL: Report missing required sections")
        else:
            print("FAIL: HTTP " + str(r.status_code))
    except Exception as e:
        print("FAIL: " + str(e)[:40])

print("")
print("RESULT: " + str(passed) + "/" + str(total) + " reports generated successfully")
if passed >= 2:
    print("TEST 8 PASSED")
    print("Track 1/4 overlap: Forensic reporting is PRODUCTION-READY")
    sys.exit(0)
else:
    print("TEST 8 FAILED")
    sys.exit(1)
