#!/usr/bin/env python3
"""
Test that UTM parameters don't break quiz functionality.
"""
import urllib.parse

# Canonical URLs from LAUNCH_KIT.md
canonical_urls = [
    "https://ai-village-agents.github.io/which-ai-village-agent/?utm_source=substack&utm_medium=post&utm_campaign=day301_launch&utm_content=cta_button",
    "https://ai-village-agents.github.io/which-ai-village-agent/?utm_source=x&utm_medium=post&utm_campaign=day301_launch&utm_content=thread_cta",
    "https://ai-village-agents.github.io/which-ai-village-agent/?utm_source=linkedin&utm_medium=post&utm_campaign=day301_launch&utm_content=post_cta",
]

# Test share URL with UTM parameters
share_url = "https://ai-village-agents.github.io/which-ai-village-agent/?r=deepseek-v3-2&v=eyJzdHJ1Y3R1cmUiOjAuOCwidmVyaWZpY2F0aW9uIjowLjgsImFic3RyYWN0aW9uIjowLjY1LCJyaXNrIjowLjQsImNvbW1zIjowLjMsImNvbGxhYiI6MC45fQ&utm_source=twitter&utm_medium=share&utm_campaign=day301_launch&utm_content=user_share"

print("Testing URL parameter parsing logic...")
print("=" * 60)

for url in canonical_urls:
    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)
    
    print(f"\nURL: {url[:80]}...")
    print(f"UTM parameters found: {[k for k in query_params.keys() if k.startswith('utm_')]}")
    
    # Check that quiz parameters aren't present
    quiz_params = ['r', 'v']
    for param in quiz_params:
        if param in query_params:
            print(f"  WARNING: Quiz parameter '{param}' found in canonical URL!")
        else:
            print(f"  OK: Quiz parameter '{param}' not present")

# Test share URL with UTM
print("\n" + "=" * 60)
print("Testing share URL with UTM parameters:")
parsed = urllib.parse.urlparse(share_url)
query_params = urllib.parse.parse_qs(parsed.query)
print(f"Quiz parameters: r={query_params.get('r', ['NOT FOUND'])[0]}, v={query_params.get('v', ['NOT FOUND'])[0][:30]}...")
print(f"UTM parameters: {[k for k in query_params.keys() if k.startswith('utm_')]}")

# JavaScript simulation
print("\n" + "=" * 60)
print("JavaScript URLSearchParams behavior simulation:")
print("const params = new URLSearchParams(window.location.search);")
print("const r = params.get('r');")
print("const v = params.get('v');")
print("const utm_source = params.get('utm_source');")

# Simulate URLSearchParams behavior
params_dict = {}
for key, values in query_params.items():
    params_dict[key] = values[0]

r = params_dict.get('r')
v = params_dict.get('v')
utm_source = params_dict.get('utm_source')

print(f"\nResults:")
print(f"  r = {r}")
print(f"  v = {v[:30] if v else 'None'}...")
print(f"  utm_source = {utm_source}")
print(f"  Quiz would {'load result' if r and v else 'start normally'}")

print("\n" + "=" * 60)
print("Conclusion: UTM parameters should not interfere with quiz functionality")
print("as URLSearchParams.get() only looks for specific parameters.")
