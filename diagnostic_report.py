#!/usr/bin/env python3
"""Sentinel Edge - Comprehensive System Diagnostic Report"""
import os, sys, json, sqlite3, subprocess, time
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

print("=" * 80)
print("SENTINEL EDGE - COMPREHENSIVE SYSTEM DIAGNOSTIC REPORT")
print(f"Generated: {datetime.now().isoformat()}")
print("=" * 80)
print()

# 1. SYSTEM INFORMATION
print("📊 SECTION 1: SYSTEM INFORMATION")
print("-" * 80)
print(f"Platform: {sys.platform}")
print(f"Python Version: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print()

# 2. PROJECT STRUCTURE
print("📁 SECTION 2: PROJECT STRUCTURE")
print("-" * 80)
project_files = []
for root, dirs, files in os.walk('.'):
    skip = False
    for x in ['venv', '.git', '__pycache__', 'logs']:
        if x in root:
            skip = True
            break
    if skip:
        continue
    for file in files:
        filepath = os.path.join(root, file)
        try:
            size = os.path.getsize(filepath)
            project_files.append((filepath, size))
            print(f"{filepath:50} {size:8,} bytes")
        except:
            pass
total_size = sum(size for _, size in project_files)
print(f"\nTotal Files: {len(project_files)}")print(f"Total Size: {total_size:,} bytes ({total_size/1024:.2f} KB)")
print()

# 3. CONFIGURATION ANALYSIS
print("⚙️  SECTION 3: CONFIGURATION ANALYSIS")
print("-" * 80)
try:
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                if 'KEY' in key or 'PASSWORD' in key or 'SECRET' in key:
                    masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                    print(f"{key:30} = {masked}")
                else:
                    print(f"{key:30} = {value}")
except Exception as e:
    print(f"Error reading .env: {e}")
print()

# 4. MODULE ANALYSIS
print("🧩 SECTION 4: MODULE ANALYSIS")
print("-" * 80)
modules_dir = Path('modules')
if modules_dir.exists():
    for module_file in modules_dir.glob('*.py'):
        print(f"\n📄 Module: {module_file.name}")
        with open(module_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            print(f"   Lines of Code: {len(lines)}")
            functions = sum(1 for line in lines if line.strip().startswith('def '))
            classes = sum(1 for line in lines if line.strip().startswith('class '))
            print(f"   Functions: {functions}")
            print(f"   Classes: {classes}")
print()

# 5. DATABASE STATISTICS
print("💾 SECTION 5: DATABASE STATISTICS")
print("-" * 80)
try:
    conn = sqlite3.connect('sentinel_memory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Database Tables: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]        print(f"  - {table_name:30} {count:,} records")
    cursor.execute("SELECT threat_type, COUNT(*) as count FROM incidents GROUP BY threat_type ORDER BY count DESC LIMIT 5")
    threats = cursor.fetchall()
    print(f"\nTop 5 Threat Types:")
    for threat, count in threats:
        print(f"  - {threat:30} {count:,} incidents")
    conn.close()
except Exception as e:
    print(f"Error reading database: {e}")
print()

# 6. API ENDPOINT TESTING
print("🌐 SECTION 6: API ENDPOINT TESTING")
print("-" * 80)
base_url = "http://127.0.0.1:5000"
if HAS_REQUESTS:
    endpoints = {
        "/health": {"method": "GET"},
        "/dashboard": {"method": "GET"},
        "/incidents": {"method": "GET"},
        "/correlate": {"method": "GET"},
        "/audit": {"method": "GET"},
        "/analyze": {"method": "POST", "data": {"alert": "Test alert for diagnostic"}, "headers": {"Content-Type": "application/json"}}
    }
    for endpoint, config in endpoints.items():
        try:
            url = base_url + endpoint
            if config["method"] == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=config.get("data", {}), headers=config.get("headers", {}), timeout=10)
            status = "✅ PASS" if response.status_code == 200 else f"⚠️  FAIL ({response.status_code})"
            print(f"{status} | {endpoint:20} | Status: {response.status_code} | Size: {len(response.content):,} bytes")
            if endpoint == "/health":
                data = response.json()
                print(f"         └─ Status: {data.get('status', 'N/A')}")
            elif endpoint == "/dashboard":
                data = response.json()
                metrics = data.get('metrics', {})
                print(f"         └─ Total Incidents: {metrics.get('total_incidents', 'N/A')}")
            elif endpoint == "/correlate":
                data = response.json()
                print(f"         └─ Campaigns Detected: {data.get('campaigns_detected', 'N/A')}")
            elif endpoint == "/analyze":
                data = response.json()
                print(f"         └─ Provider: {data.get('provider', 'N/A')}")
                print(f"         └─ Threat Type: {data.get('threat_type', 'N/A')}")
                print(f"         └─ Confidence: {data.get('confidence', 'N/A')}")
        except requests.exceptions.ConnectionError:
            print(f"❌ FAIL | {endpoint:20} | Server not running")        except requests.exceptions.Timeout:
            print(f"⏱️  TIMEOUT | {endpoint:20} | Request timed out")
        except Exception as e:
            print(f"❌ ERROR | {endpoint:20} | {str(e)}")
else:
    print("⚠️  requests module not available - skipping API tests")
print()

# 7. GIT REPOSITORY STATUS
print("📦 SECTION 7: GIT REPOSITORY STATUS")
print("-" * 80)
try:
    result = subprocess.run(['git', 'log', '--oneline', '-10'], capture_output=True, text=True, timeout=5)
    print("Last 10 Commits:")
    print(result.stdout)
    result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, timeout=5)
    if result.stdout.strip():
        print("Uncommitted Changes:")
        print(result.stdout)
    else:
        print("✅ Working directory clean")
except Exception as e:
    print(f"Error accessing git: {e}")
print()

# 8. DEPENDENCIES
print("📚 SECTION 8: DEPENDENCIES")
print("-" * 80)
try:
    with open('requirements.txt', 'r') as f:
        deps = f.readlines()
        print(f"Total Dependencies: {len(deps)}")
        for dep in deps:
            print(f"  - {dep.strip()}")
except Exception as e:
    print(f"Error reading requirements.txt: {e}")
print()

# 9. TEST RESULTS
print("🧪 SECTION 9: TEST RESULTS")
print("-" * 80)
try:
    with open('edge_case_results.json', 'r') as f:
        results = json.load(f)
        print(f"Total Tests: {results.get('total_tests', 'N/A')}")
        print(f"Passed: {results.get('passed', 'N/A')}")
        print(f"Failed: {results.get('failed', 'N/A')}")
        print(f"Pass Rate: {results.get('pass_rate', 'N/A')}")
        if results.get('failed_tests'):
            print("\nFailed Tests:")            for test in results['failed_tests']:
                print(f"  ❌ {test}")
except Exception as e:
    print(f"Error reading test results: {e}")
print()

# 10. SECURITY & COMPLIANCE
print("🔒 SECTION 10: SECURITY & COMPLIANCE")
print("-" * 80)
print("Checking for competitor references...")
result = subprocess.run(['grep', '-r', '-i', 'claude\\|anthropic', '--exclude-dir=venv', '--exclude-dir=.git', '--exclude-dir=logs', '--exclude-dir=__pycache__', '--exclude=*.db', '.'], capture_output=True, text=True, timeout=10)
if result.stdout.strip():
    print(f"⚠️  WARNING: Found competitor references:\n{result.stdout}")
else:
    print("✅ No Claude/Anthropic references found")
print("\nSecurity Features:")
security_checks = [('modules/security.py', 'Security module'), ('modules/audit.py', 'Audit logging'), ('rate_limit', 'Rate limiting in app.py')]
for check, desc in security_checks:
    if os.path.exists(check) or (check in open('app.py').read() if os.path.exists('app.py') else False):
        print(f"  ✅ {desc}")
    else:
        print(f"  ⚠️  {desc} - Not found")
print()

# 11. PERFORMANCE METRICS
print("⚡ SECTION 11: PERFORMANCE METRICS")
print("-" * 80)
if HAS_REQUESTS:
    try:
        endpoints_to_test = ["/health", "/dashboard", "/incidents"]
        response_times = []
        for endpoint in endpoints_to_test:
            start = time.time()
            response = requests.get(base_url + endpoint, timeout=5)
            elapsed = (time.time() - start) * 1000
            response_times.append(elapsed)
            print(f"{endpoint:20} {elapsed:6.2f} ms")
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"\nAverage Response Time: {avg_time:.2f} ms")
            if avg_time < 100:
                print("✅ Performance: Excellent")
            elif avg_time < 500:
                print("✅ Performance: Good")
            else:
                print("⚠️  Performance: Needs optimization")
    except Exception as e:
        print(f"Error testing performance: {e}")
else:
    print("⚠️  requests module not available")print()

# 12. AI PROVIDER ANALYSIS
print("🤖 SECTION 12: AI PROVIDER ANALYSIS")
print("-" * 80)
if HAS_REQUESTS:
    try:
        response = requests.post(base_url + "/analyze", json={"alert": "Ransomware beacon detected from 10.0.0.77"}, headers={"Content-Type": "application/json"}, timeout=30)
        data = response.json()
        print(f"AI Provider: {data.get('provider', 'N/A')}")
        print(f"Threat Type: {data.get('threat_type', 'N/A')}")
        print(f"Severity: {data.get('severity', 'N/A')}")
        print(f"Confidence: {data.get('confidence', 'N/A')}")
        print(f"Has Reasoning: {'Yes' if data.get('reasoning') else 'No'}")
        print(f"Has IOCs: {'Yes' if data.get('iocs') else 'No'}")
        print(f"Has Action Plan: {'Yes' if data.get('action_plan') else 'No'}")
        if data.get('iocs'):
            iocs = data['iocs']
            print(f"\nIOC Extraction:")
            print(f"  - IPv4 Addresses: {len(iocs.get('ipv4', []))}")
            print(f"  - Usernames: {len(iocs.get('username', []))}")
            print(f"  - Domains: {len(iocs.get('domain', []))}")
            print(f"  - Filepaths: {len(iocs.get('filepath', []))}")
    except Exception as e:
        print(f"Error testing AI provider: {e}")
else:
    print("⚠️  requests module not available")
print()

print("=" * 80)
print("END OF DIAGNOSTIC REPORT")
print("=" * 80)
