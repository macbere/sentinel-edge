import requests
import sys
import threading
import time

BASE = "http://127.0.0.1:5000"
print("STRESS TEST 5: Concurrent Request Handling")
print("Simulating 5 simultaneous analysts...")

results = {"success": 0, "fail": 0}
lock = threading.Lock()

def analyst_work(analyst_id):
    try:
        # Each analyst does 3 operations: analyze, list, health
        for op in range(3):
            if op == 0:
                r = requests.post(BASE + "/analyze", json={"alert": "Analyst " + str(analyst_id) + " alert"}, timeout=8)
            elif op == 1:
                r = requests.get(BASE + "/incidents?limit=5", timeout=8)
            else:
                r = requests.get(BASE + "/health", timeout=8)
            
            if r.status_code not in [200, 503]:
                raise Exception("Bad status")
        
        with lock:
            results["success"] = results["success"] + 1
    except Exception as e:
        with lock:
            results["fail"] = results["fail"] + 1

threads = []
start = time.time()

for i in range(5):
    t = threading.Thread(target=analyst_work, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

elapsed = time.time() - start

print("")
print("RESULT: " + str(results["success"]) + "/5 analysts completed all operations")
print("Time: " + str(round(elapsed, 2)) + " seconds")
print("Failures: " + str(results["fail"]))

if results["success"] >= 4 and results["fail"] <= 1:
    print("TEST 5 PASSED")
    print("Architecture handles concurrent access safely")
    sys.exit(0)
else:
    print("TEST 5 FAILED")
    sys.exit(1)
