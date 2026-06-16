"""
Reasoning Module: 4-Step Agentic Chain for Threat Analysis

This module implements a sophisticated multi-step reasoning chain:
1. Threat Classification - Identifies threat type and extracts IOCs
2. Tool Selection - Determines which security tools to invoke
3. Action Plan Generation - Creates containment steps
4. Confidence Validation - Self-checks the output quality

Each step is a separate Qwen API call, logged for transparency.
"""
import requests
import json
import time
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, LLM_PROVIDER
from modules.mcp_threat_intel import threat_intel_mcp

def _call_qwen_step(system_prompt, user_prompt):
    if not QWEN_API_KEY:
        return None
    headers = {"Authorization": "Bearer " + QWEN_API_KEY, "Content-Type": "application/json"}
    payload = {"model": QWEN_MODEL, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "temperature": 0.1, "response_format": {"type": "json_object"}}
    try:
        resp = requests.post(QWEN_BASE_URL + "/chat/completions", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return json.loads(resp.json()["choices"][0]["message"]["content"].strip())
    except Exception as e:
        print(f"Qwen API Error: {e}")
        return None

def _smart_offline(prompt):
    from modules.offline_analyzer import smart_offline_analyze
    return smart_offline_analyze(prompt)

def analyze_with_chain(alert_text, max_retries=1):
    chain = []
    mcp_enrichment = None
    provider = LLM_PROVIDER
    if provider != "qwen":
        return _smart_offline(alert_text)

    # Step 1: Threat Classification
    step1_sys = 'You are a threat classifier. Return JSON: {"threat_type": "string", "severity": "low|medium|high|critical", "iocs": {"ipv4": [], "username": [], "domain": [], "filepath": []}}'
    step1_res = _call_qwen_step(step1_sys, f"Classify this alert: {alert_text}")
    if not step1_res: return _smart_offline(alert_text)
    chain.append({"step": 1, "name": "Threat Classification", "output": step1_res})

    # MCP Tool Invocation: Enrich IOCs with threat intelligence
    iocs = step1_res.get("iocs", {})
    ipv4_list = iocs.get("ipv4", [])
    if ipv4_list:
        primary_ip = ipv4_list[0]
        mcp_enrichment = threat_intel_mcp.lookup_ip(primary_ip)
        chain.append({"step": "mcp", "name": "Threat Intelligence Lookup", "tool": "threat_intelligence_lookup", "input": {"ip": primary_ip}, "output": mcp_enrichment})

    # Step 2: Tool Selection
    step2_sys = 'You are a tool selector. Return JSON: {"tools": ["list of tools needed"]}'
    step2_res = _call_qwen_step(step2_sys, f"Alert: {alert_text}. Classification: {step1_res}. MCP Enrichment: {mcp_enrichment}")
    chain.append({"step": 2, "name": "Tool Selection", "output": step2_res or {"tools": []}})

    # Step 3: Action Plan Generation (now with MCP data)
    step3_sys = 'You are an incident responder. Return JSON: {"containment_steps": ["step1", "step2"], "requires_human_approval": true/false}'
    step3_res = _call_qwen_step(step3_sys, f"Alert: {alert_text}. Classification: {step1_res}. MCP Data: {mcp_enrichment}. Tools: {step2_res}")
    chain.append({"step": 3, "name": "Action Plan Generation", "output": step3_res})

    # Step 4: Confidence Validation
    step4_sys = 'You are a validator. Return JSON: {"confidence": 0.0-1.0, "self_check": "brief explanation"}'
    step4_res = _call_qwen_step(step4_sys, f"Alert: {alert_text}. Plan: {step3_res}")
    chain.append({"step": 4, "name": "Confidence Validation", "output": step4_res})

    final_result = {
        "provider": "qwen",
        "threat_type": step1_res.get("threat_type", "unknown"),
        "severity": step1_res.get("severity", "medium"),
        "containment_steps": step3_res.get("containment_steps", []) if step3_res else [],
        "requires_human_approval": step3_res.get("requires_human_approval", True) if step3_res else True,
        "confidence": step4_res.get("confidence", 0.8) if step4_res else 0.8,
        "reasoning": step4_res.get("self_check", "Multi-step chain completed") if step4_res else "Chain completed",
        "reasoning_chain": chain,
        "mcp_enrichment": mcp_enrichment,
        "iocs": iocs
    }
    return final_result

def analyze_with_retry(prompt, max_retries=2):
    return analyze_with_chain(prompt)
