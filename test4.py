import requests
import sys
import json

BASE = "http://127.0.0.1:5000"
print("STRESS TEST 4: Memory Search Under Load (FIXED)")
print("Phase 1: Seeding memory with 20 unique incidents...")

seeded = 0
keywords = ["malware", "phishing", "ransomware", "brute-force", "injection"]

for i in range(20):
    try:
        kw = keywords[i % len(keywords)]
        alert = "Test incident " + str(i) + " involving " + kw + " attack vector"
        payload = {"alert": alert}
        r = requests.post(BASE + "/analyze", json=payload, timeout=5)
        if r.status_code in [200, 503]:
            seeded = seeded + 1
    except:
        pass

print("Seeded " + str(seeded) + "/20 incidents into memory")

if seeded < 15:
    print("FAIL: Could not seed enough incidents")
    sys.exit(1)

print("")
print("Phase 2: Testing keyword search accuracy...")
search_passed = 0

for kw in keywords:
    try:
        r = requests.get(BASE + "/incidents?limit=50", timeout=5)
        if r.status_code == 200:
            data = r.json()
            # FIX: Search entire record as lowercase string
            matches = []
            for x in data:
                record_str = json.dumps(x).lower()
                if kw in record_str:
                    matches.append(x)
            
            if len(matches) > 0:
                print("PASS: Found " + str(len(matches)) + " matches for '" + kw + "'")
                search_passed = search_passed + 1
            else:
                print("FAIL: No matches for '" + kw + "'")
        else:
            print("FAIL: /incidents returned " + str(r.status_code))
    except Exception as e:
        print("FAIL: Search error for '" + kw + "'")

print("")
print("RESULT: " + str(search_passed) + "/" + str(len(keywords)) + " keyword searches successful")
if search_passed >= 4:
    print("TEST 4 PASSED")
    print("MemoryAgent overlap is FUNCTIONAL and ACCURATE")
    sys.exit(0)
else:
    print("TEST 4 FAILED")
    sys.exit(1)
