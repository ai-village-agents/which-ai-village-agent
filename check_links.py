#!/usr/bin/env python3
import os
import re

def extract_links(md_content):
    """Extract markdown links [text](url) from content."""
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(pattern, md_content)
    return links

def check_link_exists(text, url):
    """Check if linked file exists locally."""
    if url.startswith('http'):
        return True  # External links assumed OK
    if url.startswith('./'):
        url = url[2:]
    if url.startswith('/'):
        url = url[1:]
    return os.path.exists(url)

def main():
    with open('LAUNCH_KIT.md', 'r') as f:
        content = f.read()
    
    links = extract_links(content)
    print("Checking links in LAUNCH_KIT.md:")
    print("=" * 60)
    
    all_good = True
    for text, url in links:
        if check_link_exists(text, url):
            print(f"✅ {text[:40]:<40} -> {url}")
        else:
            print(f"❌ {text[:40]:<40} -> {url} (MISSING)")
            all_good = False
    
    print("=" * 60)
    if all_good:
        print("✅ All links in LAUNCH_KIT.md are valid")
    else:
        print("⚠️ Some links are broken")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    exit(main())
