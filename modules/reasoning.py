"""
Reasoning Module: Optimized 4-Step Agentic Chain for Threat Analysis

Improvements over v1:
- MCP enrichment for IPs AND domains
- Parallel MCP lookup thread
- Faster prompts
- Step timing logged
- Graceful degradation
"""
import requests
import json
import time
import threading
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, LLM_PROVIDER
from modules.mcp_threat_intel import threat_intel_mcp


def _call_qwen_step(system_prompt, user_prompt, timeout=25):
    if not QWEN_API_KEY:
        return None
    headers = {
        "Authorization": "Bearer " + QWEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 500,
        "response_format": {"type": "json_object"}
    }
    try:
        start = time.time()
        resp = requests.post(
            QWEN_BASE_URL + "/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        resp.raise_for_status()
        elapsed = round(time.time() - start, 2)
        result = json.loads(resp.json()["choices"][0]["message"]["content"].strip())
        result["_elapsed_ms"] = int(elapsed * 1000)
        return result
    except Exception as e:
        print(f"[Qwen Error] {e}")
        return None


def _mcp_lookup_threaded(iocs, result_container):
    """Run full IOC enrichment in a thread."""
    try:
        results = []
        for ip in iocs.get("ipv4", [])[:2]:
            results.append(threat_intel_mcp.lookup_ip(ip))
        for domain in iocs.get("domain", [])[:2]:
            results.append(threat_intel_mcp.lookup_domain(domain))
        result_container["mcp"] = results[0] if len(results) == 1 else results if results else None
    except Exception as e:
        result_container["mcp"] = None


def _smart_offline(alert_text):
    from modules.offline_analyzer import smart_offline_analyze
    return smart_offline_analyze(alert_text)


def analyze_with_chain(alert_text, max_retries=1):
    chain = []
    total_start = time.time()

    if LLM_PROVIDER != "qwen" or not QWEN_API_KEY:
        return _smart_offline(alert_text)

    # STEP 1: Threat Classification
    step1_sys = (
        'You are a threat classifier. Respond ONLY in JSON: '
        '{"threat_type":"string","severity":"low|medium|high|critical",'
        '"iocs":{"ipv4":[],"username":[],"domain":[],"filepath":[]}}'
    )
    step1_res = _call_qwen_step(step1_sys, f"Classify: {alert_text}")
    if not step1_res:
        return _smart_offline(alert_text)

    elapsed1 = step1_res.pop("_elapsed_ms", 0)
    chain.append({
        "step": 1,
        "name": "Threat Classification",
        "output": step1_res,
        "elapsed_ms": elapsed1
    })

    iocs = step1_res.get("iocs", {})
    has_iocs = any(iocs.get(k) for k in ["ipv4", "domain"])

    # Start MCP lookup in parallel thread
    mcp_container = {}
    mcp_thread = None
    if has_iocs:
        mcp_thread = threading.Thread(
            target=_mcp_lookup_threaded,
            args=(iocs, mcp_container)
        )
        mcp_thread.start()

    # STEP 2: Tool Selection
    step2_sys = (
        'You are a security tool selector. Respond ONLY in JSON: '
        '{"tools":["tool1","tool2"],"rationale":"brief reason"}. '
        'IMPORTANT TOOL SELECTION RULES: '
        'If the threat involves GitHub, GitLab, source code, secrets, API keys, or cloud repositories — '
        'select from: ["GitHub Advanced Security","GitGuardian","Trufflehog","Secret Scanner","SAST"]. '
        'If the threat involves ransomware, malware, or endpoint infection — '
        'select from: ["CrowdStrike Falcon","ESET Endpoint Security","EDR","Malwarebytes"]. '
        'If the threat involves network scanning, brute force, or unauthorized access — '
        'select from: ["Fail2Ban","Cloudflare","SIEM","IDS/IPS"]. '
        'If the threat involves data exfiltration or insider threat — '
        'select from: ["DLP","UEBA","SIEM","Netflow Analyzer"]. '
        'If the threat involves phishing or email — '
        'select from: ["Email Gateway","DMARC Analyzer","URL Sandbox","Proofpoint"]. '
        'Always match tools to the actual attack vector.'
    )
    step2_input = (
        f"Threat: {step1_res.get('threat_type')} | "
        f"Severity: {step1_res.get('severity')} | "
        f"Alert: {alert_text[:200]}"
    )
    step2_res = _call_qwen_step(step2_sys, step2_input)
    elapsed2 = step2_res.pop("_elapsed_ms", 0) if step2_res else 0
    chain.append({
        "step": 2,
        "name": "Tool Selection",
        "output": step2_res or {"tools": [], "rationale": "fallback"},
        "elapsed_ms": elapsed2
    })

    # Wait for MCP
    if mcp_thread:
        mcp_thread.join(timeout=10)
    mcp_enrichment = mcp_container.get("mcp")

    if mcp_enrichment:
        enrichment_list = mcp_enrichment if isinstance(mcp_enrichment, list) else [mcp_enrichment]
        for enrichment in enrichment_list:
            chain.append({
                "step": "mcp",
                "name": f"Threat Intel: {enrichment.get('ioc_type','ioc').upper()} Lookup",
                "tool": "threat_intelligence_lookup",
                "input": {"ioc": enrichment.get("ioc_value")},
                "output": enrichment
            })

    # STEP 3: Action Plan Generation
    step3_sys = (
        'You are an incident responder. Respond ONLY in JSON: '
        '{"containment_steps":["step1","step2","step3"],"requires_human_approval":true}'
    )
    mcp_summary = ""
    if mcp_enrichment:
        items = mcp_enrichment if isinstance(mcp_enrichment, list) else [mcp_enrichment]
        for item in items:
            if item.get("ioc_type") == "ip":
                mcp_summary += f" | IP {item.get('ioc_value')} abuse score: {item.get('abuse_confidence_score',0)}%"
            elif item.get("ioc_type") == "domain":
                mcp_summary += f" | Domain {item.get('ioc_value')} risk: {item.get('risk_level','unknown')}"

    step3_input = (
        f"Alert: {alert_text[:200]}"
        f" | Threat: {step1_res.get('threat_type')}"
        f" | Severity: {step1_res.get('severity')}"
        f" | Tools: {step2_res.get('tools',[]) if step2_res else []}"
        f"{mcp_summary}"
    )
    step3_res = _call_qwen_step(step3_sys, step3_input)
    elapsed3 = step3_res.pop("_elapsed_ms", 0) if step3_res else 0
    chain.append({
        "step": 3,
        "name": "Action Plan Generation",
        "output": step3_res or {"containment_steps": [], "requires_human_approval": True},
        "elapsed_ms": elapsed3
    })

    # STEP 4: Confidence Validation
    step4_sys = (
        'You are a validator. Respond ONLY in JSON: '
        '{"confidence":0.0,"self_check":"one sentence validation"}'
    )
    step4_input = (
        f"Threat: {step1_res.get('threat_type')} | "
        f"Severity: {step1_res.get('severity')} | "
        f"Plan: {step3_res.get('containment_steps',[]) if step3_res else []}"
    )
    step4_res = _call_qwen_step(step4_sys, step4_input)
    elapsed4 = step4_res.pop("_elapsed_ms", 0) if step4_res else 0
    chain.append({
        "step": 4,
        "name": "Confidence Validation",
        "output": step4_res or {"confidence": 0.8, "self_check": "Validation unavailable"},
        "elapsed_ms": elapsed4
    })

    total_elapsed = round(time.time() - total_start, 2)

    return {
        "provider": "qwen",
        "threat_type": step1_res.get("threat_type", "unknown"),
        "severity": step1_res.get("severity", "medium"),
        "containment_steps": step3_res.get("containment_steps", []) if step3_res else [],
        "requires_human_approval": step3_res.get("requires_human_approval", True) if step3_res else True,
        "confidence": step4_res.get("confidence", 0.8) if step4_res else 0.8,
        "reasoning": step4_res.get("self_check", "Chain completed") if step4_res else "Chain completed",
        "reasoning_chain": chain,
        "mcp_enrichment": mcp_enrichment,
        "iocs": iocs,
        "total_chain_elapsed_ms": int(total_elapsed * 1000)
    }


def analyze_with_retry(prompt, max_retries=2):
    return analyze_with_chain(prompt)


def enrich_iocs(iocs):
    """Enrich all IOC types using the expanded MCP module."""
    try:
        return threat_intel_mcp.enrich_all_iocs(iocs)
    except Exception:
        return []
