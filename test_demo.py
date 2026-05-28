#!/usr/bin/env python3
import requests, json
BASE = "http://127.0.0.1:5000"
print("🧪 Testing Sentinel Edge...")
print("Health:", requests.get(f"{BASE}/health").json())
print("Analyze (offline):", requests.post(f"{BASE}/analyze", json={"alert":"test"}).json())
print("🎉 Demo ready!")