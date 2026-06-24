import requests
import time
from concurrent.futures import ThreadPoolExecutor

URL = "http://47.77.199.98:5000"
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
    r = requests.post(f"{URL}/analyze", json={"alert": "Ransomware beacon from 10.0.0.77"}, timeout=TIMEOUT)
    if r.status_code != 200: raise Exception(f"Status {r.status_code}")
    data = r.json()
    if "reasoning_chain" not in data: raise Exception("Missing reasoning chain")
    if "mcp_enrichment" not in data: raise Exception("Missing MCP enrichment")

def test_dashboard():
    r = requests.get(f"{URL}/dashboard", timeout=10)
    if r.status_code != 200: raise Exception(f"Status {r.status_code}")

def test_correlate():
    r = requests.get(f"{URL}/correlate", timeout=30)
    if r.status_code != 200: raise Exception(f"Status {r.status_code}")

def test_concurrent():
    def req():
        r = requests.post(f"{URL}/analyze", json={"alert": "Load test"}, timeout=TIMEOUT)
        return r.status_code == 200
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(lambda _: req(), range(5)))
    if sum(results) != 5: raise Exception(f"Only {sum(results)}/5 passed")

if __name__ == "__main__":
    print("="*50)
    print("SENTINEL EDGE STRESS TEST")
    print("="*50)
    run_test("Health Check", test_health)
    run_test("Analyze (4-step chain + MCP)", test_analyze)
    run_test("Dashboard Metrics", test_dashboard)
    run_test("APT Correlation", test_correlate)
    run_test("Concurrent Load (5 users)", test_concurrent)
    print("="*50)
    print("TEST COMPLETE")
