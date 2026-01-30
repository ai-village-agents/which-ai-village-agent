#!/usr/bin/env python3
"""
Quick accessibility audit for HTML pages.
"""

import os
import re
import sys

def check_file(filepath):
    print(f"\n=== Checking {filepath} ===")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for lang attribute
    if '<html lang=' not in content and '<html>' in content:
        print("❌ Missing lang attribute on <html> tag")
    else:
        print("✅ Has lang attribute")
    
    # Check heading structure
    headings = re.findall(r'<h([1-6])[^>]*>', content)
    if headings:
        print(f"✅ Headings found: {sorted(headings)}")
        # Check if h1 exists
        if '1' not in headings:
            print("⚠️  No H1 heading found")
    else:
        print("⚠️  No headings found")
    
    # Check for images without alt text
    img_tags = re.findall(r'<img[^>]*>', content)
    for img in img_tags:
        if 'alt=' not in img.lower():
            print(f"❌ Image without alt text: {img[:50]}...")
    
    if img_tags:
        print(f"✅ Found {len(img_tags)} image(s)")
    
    # Check for form labels
    if '<input' in content or '<textarea' in content:
        # Simple check for form elements
        input_tags = re.findall(r'<input[^>]*>', content)
        for inp in input_tags:
            if 'type="text"' in inp or 'type="email"' in inp or 'type="password"' in inp:
                if 'id=' in inp:
                    # Check if there's a label with for= attribute
                    id_match = re.search(r'id="([^"]*)"', inp)
                    if id_match:
                        id_value = id_match.group(1)
                        if f'for="{id_value}"' not in content:
                            print(f"⚠️  Input field without associated label: id={id_value}")
    
    # Check for ARIA attributes
    if 'aria-' in content:
        print("✅ ARIA attributes present")
    else:
        print("ℹ️  No ARIA attributes found (may be fine for simple pages)")
    
    # Check viewport meta tag
    if 'viewport' in content:
        print("✅ Viewport meta tag present")
    else:
        print("❌ Missing viewport meta tag")
    
    # Check for skip links
    if 'skip' in content.lower() and ('<a' in content or '<button' in content):
        print("✅ Skip link may be present")
    else:
        print("ℹ️  No skip link found (consider adding for keyboard navigation)")

def main():
    pages = ["docs/index.html", "docs/share/index.html", "docs/press-kit/index.html"]
    
    for page in pages:
        if os.path.exists(page):
            check_file(page)
        else:
            print(f"⚠️  File not found: {page}")

if __name__ == "__main__":
    main()
