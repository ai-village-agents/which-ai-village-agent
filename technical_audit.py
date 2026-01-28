#!/usr/bin/env python3
"""
Technical Audit for AI Village Personality Quiz Launch
Checks all critical URLs, configurations, and functionality.
"""
import urllib.request
import json
import sys
import os

def check_url(url, description):
    """Check if URL returns HTTP 200."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        status = resp.getcode()
        if status == 200:
            print(f"✅ {description}: HTTP {status}")
            return True
        else:
            print(f"❌ {description}: HTTP {status}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def check_json_url(url, description):
    """Check if URL returns valid JSON."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.load(resp)
        print(f"✅ {description}: Valid JSON with {len(data) if isinstance(data, (dict, list)) else 'data'}")
        return True
    except Exception as e:
        print(f"❌ {description}: Invalid JSON - {e}")
        return False

def main():
    print("=" * 70)
    print("AI VILLAGE PERSONALITY QUIZ - TECHNICAL AUDIT")
    print("Day 300 Final Verification")
    print("=" * 70)
    
    # Base quiz URL (GitHub Pages)
    base_url = "https://ai-village-agents.github.io/which-ai-village-agent"
    
    # Critical URLs to check
    urls_to_check = [
        (f"{base_url}/", "Quiz main page"),
        (f"{base_url}/?v=health", "Quiz with cache-busting"),
        (f"{base_url}/app.js", "Main JavaScript"),
        (f"{base_url}/data/dimensions.json", "Dimensions data"),
        (f"{base_url}/data/questions.json", "Questions data"),
        (f"{base_url}/data/agents.json", "Agents data"),
    ]
    
    # External resources
    external_urls = [
    ]
    
    # Check all URLs
    all_good = True
    print("\n🔍 Checking quiz infrastructure:")
    for url, desc in urls_to_check:
        if not check_url(url, desc):
            all_good = False
    
    print("\n🔍 Checking external resources:")
    for url, desc in external_urls:
        if not check_url(url, desc):
            all_good = False
    
    # Check JSON validity for data files
    print("\n🔍 Validating JSON data:")
    json_urls = [
        (f"{base_url}/data/dimensions.json", "Dimensions"),
        (f"{base_url}/data/questions.json", "Questions"),
        (f"{base_url}/data/agents.json", "Agents"),
    ]
    
    for url, desc in json_urls:
        if not check_json_url(url, desc):
            all_good = False
    
    # Check local files for completeness
    print("\n🔍 Checking local documentation:")
    local_files = [
        "LAUNCH_KIT.md",
        "docs/launch/day-301-morning-checklist.md",
        "docs/launch/day-302-user-highlights-guide.md",
        "docs/launch/engagement-response-templates.md",
        "docs/launch/social-media-coordination-plan.md",
        "LAUNCH_ANALYTICS.md",
        "TROUBLESHOOTING.md",
    ]
    
    for file in local_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                lines = f.readlines()
            print(f"✅ {file}: {len(lines)} lines")
        else:
            print(f"❌ {file}: Missing")
            all_good = False
    
    # Check UTM parameter examples
    print("\n🔍 Verifying UTM parameter examples:")
    utm_examples = [
        f"{base_url}/?utm_source=substack&utm_medium=post&utm_campaign=day301_launch&utm_content=cta_button",
        f"{base_url}/?utm_source=x&utm_medium=post&utm_campaign=day301_launch&utm_content=thread_cta",
        f"{base_url}/?utm_source=linkedin&utm_medium=post&utm_campaign=day301_launch&utm_content=post_cta",
    ]
    
    for url in utm_examples:
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        utm_params = [k for k in query.keys() if k.startswith('utm_')]
        print(f"✅ UTM example: {len(utm_params)} parameters ({', '.join(utm_params)})")
    
    # Check share URL format
    print("\n🔍 Testing share URL format:")
    test_share = f"{base_url}/?r=deepseek-v3-2&v=eyJzdHJ1Y3R1cmUiOjAuOCwidmVyaWZpY2F0aW9uIjowLjgsImFic3RyYWN0aW9uIjowLjY1LCJyaXNrIjowLjQsImNvbW1zIjowLjMsImNvbGxhYiI6MC45fQ"
    if check_url(test_share, "Share URL test"):
        print(f"✅ Share URL format works")
    else:
        all_good = False
    
    print("\n" + "=" * 70)
    if all_good:
        print("🎉 TECHNICAL AUDIT: ALL CHECKS PASSED")
        print("Launch is ready for Days 301-302 promotion campaign.")
    else:
        print("⚠️ TECHNICAL AUDIT: SOME CHECKS FAILED")
        print("Review failures before launch.")
    print("=" * 70)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    import urllib.parse
    sys.exit(main())
