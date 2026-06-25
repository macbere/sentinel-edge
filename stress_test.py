import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://47.77.199.98"
TIMEOUT = 60

def run_test(name, func):
    print(f"Testing {name}...")
    try:
        func()
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False

def test_health():
    r = requests.get(f"{URL}/health", timeout=10)
    if r.status_code != 200: raise Exception(f"Status {r.status_code}")

def test_analyze():
    r = requests.post(f"{URL}/analyze", json={"alert": "Ransomware beacon from 185.220.101.45 targeting finance-db"}, timeout=TIMEOUT)
    if r.status_code != 200: raise Exception(f"Status {r.status_code}")
    data = r.json()
    if "reasoning_chain" not in data: raise Exception("Missing reasoning chain")
    if "mcp_enrichment" not in data: raise Exception("Missing MCP enrichment")

def test_dashboard():
    r = requests.get(f"{URL}/dashboard", timeout=10)
    if r.status_code != 200: raise Exception(f"Status {r.status_code}")
    data = r.json()
    if "Track 4" not in data.get("track", ""): raise Exception("Wrong track")

def test_correlate():
    r = requests.get(f"{URL}/correlate", timeout=30)
    if r.status_code != 200: raise Exception(f"Status {r.status_code}")
    data = r.json()
    if data.get("campaigns_detected", 0) == 0: raise Exception("No campaigns detected")

def test_concurrent():
    def req(_):
        r = requests.get(f"{URL}/dashboard", timeout=15)
        return r.status_code == 200
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(req, range(5)))
    if sum(results) != 5: raise Exception(f"Only {sum(results)}/5 passed")

if __name__ == "__main__":
    print("=" * 50)
    print("SENTINEL EDGE STRESS TEST")
    print("=" * 50)
    tests = [
        ("Health Check", test_health),
        ("Analyze 4-step chain + MCP", test_analyze),
        ("Dashboard Metrics + Track 4", test_dashboard),
        ("APT Correlation Engine", test_correlate),
        ("Concurrent Load 5 users", test_concurrent),
    ]
    passed = sum(run_test(name, func) for name, func in tests)
    print("=" * 50)
    print(f"RESULT: {passed}/{len(tests)} tests passed")
    print("STATUS: ALL PASSED" if passed == len(tests) else "STATUS: SOME FAILED")
    print("=" * 50)
