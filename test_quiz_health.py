#!/usr/bin/env python3
"""
Quick health check for quiz launch Day 301
"""
import requests
import json
import sys
import re
import time
import random

BASE_URL = "https://ai-village-agents.github.io/which-ai-village-agent"
DATA_URL = f"{BASE_URL}/data"
TIMEOUT = 10

EXPECTED_AGENT_IDS = [
    "gpt-5-2", "gpt-5", "gpt-5-1",
    "gemini-2-5-pro", "gemini-3-pro",
    "deepseek-v3-2",
    "claude-haiku-4-5", "claude-3-7",
    "claude-sonnet-4-5", "claude-opus-4-5",
    "opus-4-5-claude-code"
]

EXPECTED_DIM_IDS = [
    "structure", "verification", "abstraction",
    "risk", "comms", "collab"
]

def get_with_retry(url, *, timeout=TIMEOUT, attempts=3, base_delay=0.5, max_delay=2.0):
    delay = base_delay
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code >= 500 or response.status_code == 429:
                if attempt == attempts:
                    response.raise_for_status()
                else:
                    sleep_for = min(max_delay, delay * (1 + random.random()))
                    print(f"NOTICE: GET {url} returned {response.status_code}; retrying in {sleep_for:.2f}s")
                    time.sleep(sleep_for)
                    delay = min(max_delay, delay * 2)
                    continue
            return response
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt == attempts:
                raise
            sleep_for = min(max_delay, delay * (1 + random.random()))
            print(f"NOTICE: GET {url} failed with {exc.__class__.__name__}; retrying in {sleep_for:.2f}s")
            time.sleep(sleep_for)
            delay = min(max_delay, delay * 2)

def test_quiz_page():
    url = f"{BASE_URL}/"
    print(f"Testing quiz page: {url}")
    try:
        r = get_with_retry(url, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"  ERROR: Status code {r.status_code}")
            return False
        print(f"  OK: Status {r.status_code}, length {len(r.text)}")
        
        # Check for key elements
        content = r.text
        checks = [
            ("Quiz title", "Which AI Village Agent Are You?"),
            ("Loading placeholder", "Loading"),
            ("Start copy", "How it works"),
        ]
        all_ok = True
        for name, substring in checks:
            if substring in content:
                print(f"  OK: Found {name}")
            else:
                print(f"  WARNING: {name} not found")
                all_ok = False

        script_srcs = re.findall(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', content, flags=re.IGNORECASE)
        script_hits = [s for s in script_srcs if "app.js" in s]
        inline_loader = ("app.js" in content) and ("createElement('script')" in content)
        if script_hits:
            print(f"  OK: Found module script tag for app.js ({script_hits[0]})")
        elif inline_loader:
            print("  OK: Found inline loader that injects the app.js module script")
        else:
            print("  WARNING: app.js loader script tag not found")
            all_ok = False

        return all_ok
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def test_agents_json():
    url = f"{DATA_URL}/agents.json"
    print(f"\nTesting agents.json: {url}")
    try:
        r = get_with_retry(url, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"  ERROR: Status code {r.status_code}")
            return False
        print(f"  OK: Status {r.status_code}")
        
        data = json.loads(r.text)
        if not isinstance(data, dict) or "agents" not in data:
            print(f"  ERROR: Expected object with agents list, got {type(data)}")
            return False
        
        agents = data["agents"]
        if not isinstance(agents, list):
            print(f"  ERROR: agents field is not a list")
            return False

        print(f"  OK: Found {len(agents)} agents")
        if len(agents) != 11:
            print(f"  ERROR: Expected 11 agents, found {len(agents)}")
            return False
        
        # Check all 11 agents
        found_ids = [agent.get("id") for agent in agents]
        missing = set(EXPECTED_AGENT_IDS) - set(found_ids)
        extra = set(found_ids) - set(EXPECTED_AGENT_IDS)
        if missing:
            print(f"  ERROR: Missing agents: {missing}")
            return False
        if extra:
            print(f"  ERROR: Unexpected agents present: {extra}")
            return False
        print(f"  OK: All 11 agents present")
        
        # Check vectors
        for agent in agents:
            if "vector" not in agent:
                print(f"  ERROR: Agent {agent.get('id')} missing vector")
                return False
            vector = agent["vector"]
            for key in EXPECTED_DIM_IDS:
                if key not in vector:
                    print(f"  ERROR: Agent {agent['id']} missing {key}")
                    return False
        print(f"  OK: All vectors have 6 dimensions")
        
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def test_questions_json():
    url = f"{DATA_URL}/questions.json"
    print(f"\nTesting questions.json: {url}")
    try:
        r = get_with_retry(url, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"  ERROR: Status code {r.status_code}")
            return False
        print(f"  OK: Status {r.status_code}")

        data = json.loads(r.text)
        questions = data.get("questions")
        dims = data.get("dimensions")
        if not isinstance(questions, list):
            print("  ERROR: questions field is not a list")
            return False
        if not isinstance(dims, list):
            print("  ERROR: dimensions field missing or not a list")
            return False

        if len(questions) != 12:
            print(f"  WARNING: Expected 12 questions, found {len(questions)}")
        else:
            print("  OK: All 12 questions present")

        dim_mismatch = set(EXPECTED_DIM_IDS) - set(dims)
        if dim_mismatch:
            print(f"  WARNING: Question dimension ids mismatch: missing {dim_mismatch}")
        else:
            print("  OK: Question dimension ids present")

        for q in questions:
            if "id" not in q or "prompt" not in q or "weights" not in q:
                print(f"  ERROR: Question missing required fields: {q}")
                return False
        print("  OK: Questions include ids, prompts, and weights")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def test_dimensions_json():
    url = f"{DATA_URL}/dimensions.json"
    print(f"\nTesting dimensions.json: {url}")
    try:
        r = get_with_retry(url, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"  ERROR: Status code {r.status_code}")
            return False
        print(f"  OK: Status {r.status_code}")

        data = json.loads(r.text)
        dims = data.get("dimensions")
        if not isinstance(dims, list):
            print("  ERROR: dimensions field missing or not a list")
            return False

        dim_ids = [d.get("id") for d in dims]
        missing = set(EXPECTED_DIM_IDS) - set(dim_ids)
        if missing:
            print(f"  ERROR: Missing expected dimensions: {missing}")
            return False
        print(f"  OK: Found {len(dims)} dimensions")

        for d in dims:
            for key in ("label", "left", "right"):
                if key not in d:
                    print(f"  ERROR: Dimension {d.get('id')} missing {key}")
                    return False
        print("  OK: Dimension labels and endpoints present")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("Day 301 Quiz Launch Health Check")
    print("=" * 60)
    
    quiz_ok = test_quiz_page()
    agents_ok = test_agents_json()
    questions_ok = test_questions_json()
    dimensions_ok = test_dimensions_json()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Quiz page: {'PASS' if quiz_ok else 'FAIL'}")
    print(f"  Agents.json: {'PASS' if agents_ok else 'FAIL'}")
    print(f"  Questions.json: {'PASS' if questions_ok else 'FAIL'}")
    print(f"  Dimensions.json: {'PASS' if dimensions_ok else 'FAIL'}")
    
    if quiz_ok and agents_ok and questions_ok and dimensions_ok:
        print("\n✅ All health checks passed. Ready for launch!")
        sys.exit(0)
    else:
        print("\n❌ Health checks failed. Investigate before launch.")
        sys.exit(1)

if __name__ == "__main__":
    main()
