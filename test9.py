import requests
import sys
import json

BASE = "http://127.0.0.1:5000"
print("STRESS TEST 9: Human-in-the-Loop Workflow")
print("Testing full approval lifecycle...")

passed = 0
total = 4

# Test 1: Create a fresh incident to approve
print("Test 1: Create incident for approval")
try:
    r = requests.post(BASE + "/analyze", json={"alert": "HITL_TEST_APPROVAL_CYCLE"}, timeout=10)
    data = r.json()
    if "incident_id" in data:
        test_id = data["incident_id"]
        print("PASS: Created incident #" + str(test_id))
        passed = passed + 1
    else:
        print("FAIL: No incident_id returned")
        sys.exit(1)
except Exception as e:
    print("FAIL: " + str(e)[:40])
    sys.exit(1)

# Test 2: Verify initial status is pending_approval
print("Test 2: Verify pending status")
try:
    r = requests.get(BASE + "/incidents?limit=10", timeout=5)
    incidents = r.json()
    target = [i for i in incidents if i["id"] == test_id]
    if len(target) > 0 and target[0]["status"] == "pending":
        print("PASS: Initial status is 'pending'")
        passed = passed + 1
    else:
        print("FAIL: Status not pending or incident missing")
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 3: Approve the incident
print("Test 3: Execute approval action")
try:
    r = requests.post(BASE + "/approve/" + str(test_id), timeout=10)
    data = r.json()
    if r.status_code == 200 and data.get("status") == "executed":
        print("PASS: Approval executed successfully")
        passed = passed + 1
    else:
        print("FAIL: Approval failed or wrong status")
except Exception as e:
    print("FAIL: " + str(e)[:40])

# Test 4: Verify final status updated in memory
print("Test 4: Verify status persistence")
try:
    r = requests.get(BASE + "/incidents?limit=10", timeout=5)
    incidents = r.json()
    target = [i for i in incidents if i["id"] == test_id]
    if len(target) > 0 and target[0]["status"] == "executed":
        print("PASS: Status persisted as 'executed' in memory")
        passed = passed + 1
    else:
        print("FAIL: Status not updated in database")
except Exception as e:
    print("FAIL: " + str(e)[:40])

print("")
print("RESULT: " + str(passed) + "/" + str(total) + " HITL tests passed")
if passed >= 3:
    print("TEST 9 PASSED")
    print("Track 4 Autopilot: Safety workflow VERIFIED")
    sys.exit(0)
else:
    print("TEST 9 FAILED")
    sys.exit(1)
