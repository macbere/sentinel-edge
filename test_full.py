import requests
import json
import threading

BASE = "http://localhost:5000"
passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS  {name}")
        passed += 1
    else:
        print(f"  FAIL  {name} {detail}")
        failed += 1

def get(path, timeout=10):
    return requests.get(BASE + path, timeout=timeout)

def post(path, data, timeout=60):
    return requests.post(BASE + path, json=data, timeout=timeout)

print("=" * 55)
print("SENTINEL EDGE FULL TEST SUITE")
print("=" * 55)

print("\n--- HEALTH ---")
r = get("/health")
test("Health returns 200", r.status_code == 200)
d = r.json()
test("Status is online", d.get("status") == "online")
test("Agent is Sentinel Edge", d.get("agent") == "Sentinel Edge")
test("Mode is edge-cloud-hybrid", d.get("mode") == "edge-cloud-hybrid")
test("Has 4 modules", len(d.get("modules", [])) == 4)

print("\n--- INPUT VALIDATION ---")
test("Empty payload returns 400", post("/analyze", {}).status_code == 400)
test("Missing alert returns 400", post("/analyze", {"foo": "bar"}).status_code == 400)
test("Empty alert returns 400", post("/analyze", {"alert": ""}).status_code == 400)
test("Null alert returns 400", post("/analyze", {"alert": None}).status_code == 400)

print("\n--- THREAT ANALYSIS ---")
r = post("/analyze", {"alert": "Ransomware beacon from 185.220.101.45 targeting finance-db"})
test("Analyze returns 200", r.status_code == 200)
d = r.json()
test("Has threat_type", "threat_type" in d)
test("Has severity", "severity" in d)
test("Has confidence", "confidence" in d)
test("Has reasoning_chain", "reasoning_chain" in d)
test("Has mcp_enrichment", "mcp_enrichment" in d)
test("Has containment_steps", "containment_steps" in d)
test("Has incident_id", "incident_id" in d)
test("Reasoning chain has steps", len(d.get("reasoning_chain", [])) >= 2)
test("Confidence between 0 and 1", 0 <= d.get("confidence", -1) <= 1)
test("Provider is qwen or offline", d.get("provider") in ["qwen", "offline_smart"])

print("\n--- MCP ENRICHMENT ---")
mcp = d.get("mcp_enrichment", {})
test("MCP enrichment present", mcp is not None)
test("MCP has source field", "source" in (mcp or {}))

print("\n--- DASHBOARD ---")
r = get("/dashboard")
test("Dashboard returns 200", r.status_code == 200)
d = r.json()
test("Dashboard has metrics", "metrics" in d)
test("Dashboard has ai_provider_stats", "ai_provider_stats" in d)
test("Dashboard track is Track 4", "Track 4" in d.get("track", ""))
test("Dashboard total_incidents > 0", d.get("metrics", {}).get("total_incidents", 0) > 0)
test("Dashboard qwen_analyses > 0", d.get("ai_provider_stats", {}).get("qwen_analyses", 0) > 0)

print("\n--- EVIDENCE PANEL ---")
r = get("/dashboard/evidence")
test("Evidence returns 200", r.status_code == 200)
d = r.json()
test("Evidence has provider", "provider" in d)
test("Evidence has system", "system" in d)
test("Evidence flask online", d.get("system", {}).get("flask") == "online")
test("Evidence db connected", d.get("system", {}).get("db_connected") == True)

print("\n--- CORRELATION ---")
r = get("/correlate")
test("Correlate returns 200", r.status_code == 200)
d = r.json()
test("Correlate has campaigns", "campaigns" in d)
test("Correlate has period_hours", "period_hours" in d)

print("\n--- INCIDENTS ---")
r = get("/incidents")
test("Incidents returns 200", r.status_code == 200)
test("Incidents is list", isinstance(r.json(), list))
test("Incidents limit works", len(get("/incidents?limit=5").json()) <= 5)

print("\n--- PAGES ---")
test("Root page returns 200", get("/").status_code == 200)
test("Demo page returns 200", get("/demo").status_code == 200)
test("Metrics page returns 200", get("/metrics").status_code == 200)
test("Judge page returns 200", get("/judge").status_code == 200)
test("Qwen page returns 200", get("/qwen").status_code == 200)

print("\n--- SIMULATE FAILURE ---")
r = post("/simulate/failure", {"mode": "cloud_down"})
test("Simulate cloud_down returns 200", r.status_code == 200)
test("Simulate cloud_down status simulated", r.json().get("status") == "simulated")
r = post("/simulate/failure", {"mode": "cloud_restore"})
test("Simulate cloud_restore returns 200", r.status_code == 200)
test("Simulate invalid mode returns 400", post("/simulate/failure", {"mode": "bad"}).status_code == 400)

print("\n--- CONCURRENT LOAD ---")
results = []
def load_req():
    try:
        results.append(requests.get(BASE + "/dashboard", timeout=10).status_code == 200)
    except:
        results.append(False)
threads = [threading.Thread(target=load_req) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
test("5 concurrent requests all pass", all(results))

print("\n" + "=" * 55)
total = passed + failed
print(f"RESULTS: {passed}/{total} passed ({round(passed/total*100)}%)")
print("STATUS: ALL PASSED" if failed == 0 else f"STATUS: {failed} FAILED")
print("=" * 55)
