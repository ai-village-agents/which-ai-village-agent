#!/usr/bin/env python3
"""
Update page-specific metadata (Open Graph, Twitter) for better social sharing.
"""

import os
import re
import sys

def update_metadata(filepath, metadata):
    """
    Update Open Graph and Twitter metadata in HTML file.
    
    Args:
        filepath: Path to HTML file
        metadata: dict with keys:
            - og_title
            - og_description  
            - og_url
            - twitter_title
            - twitter_description
            - twitter_image (optional)
            - og_image (optional)
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    changes = 0
    
    for line in lines:
        # Check for Open Graph tags
        if 'property="og:title"' in line:
            line = re.sub(r'content="[^"]*"', f'content="{metadata["og_title"]}"', line)
            changes += 1
        elif 'property="og:description"' in line:
            line = re.sub(r'content="[^"]*"', f'content="{metadata["og_description"]}"', line)
            changes += 1
        elif 'property="og:url"' in line:
            line = re.sub(r'content="[^"]*"', f'content="{metadata["og_url"]}"', line)
            changes += 1
        elif 'property="og:image"' in line and 'og_image' in metadata:
            line = re.sub(r'content="[^"]*"', f'content="{metadata["og_image"]}"', line)
            changes += 1
        
        # Check for Twitter tags
        elif 'name="twitter:title"' in line:
            line = re.sub(r'content="[^"]*"', f'content="{metadata["twitter_title"]}"', line)
            changes += 1
        elif 'name="twitter:description"' in line:
            line = re.sub(r'content="[^"]*"', f'content="{metadata["twitter_description"]}"', line)
            changes += 1
        elif 'name="twitter:image"' in line and 'twitter_image' in metadata:
            line = re.sub(r'content="[^"]*"', f'content="{metadata["twitter_image"]}"', line)
            changes += 1
        
        new_lines.append(line)
    
    # If no changes were made (tags missing), add them before closing </head>
    if changes == 0:
        # Find closing </head>
        for i, line in enumerate(new_lines):
            if '</head>' in line.lower():
                indent = '  ' if line.startswith('  ') else ''
                # Add missing tags
                tags = [
                    f'{indent}<meta property="og:title" content="{metadata["og_title"]}" />',
                    f'{indent}<meta property="og:description" content="{metadata["og_description"]}" />',
                    f'{indent}<meta property="og:url" content="{metadata["og_url"]}" />',
                    f'{indent}<meta name="twitter:title" content="{metadata["twitter_title"]}" />',
                    f'{indent}<meta name="twitter:description" content="{metadata["twitter_description"]}" />'
                ]
                if 'og_image' in metadata:
                    tags.append(f'{indent}<meta property="og:image" content="{metadata["og_image"]}" />')
                if 'twitter_image' in metadata:
                    tags.append(f'{indent}<meta name="twitter:image" content="{metadata["twitter_image"]}" />')
                
                # Insert before closing </head>
                new_lines[i:i] = [tag + '\n' for tag in tags]
                break
    
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
    
    print(f"Updated metadata in {filepath} ({changes} tags updated)")

def main():
    base_url = "https://ai-village-agents.github.io/which-ai-village-agent"
    image_url = f"{base_url}/og.png"
    
    # Main quiz page
    update_metadata("docs/index.html", {
        "og_title": "Which AI Village Agent Are You?",
        "og_description": "A dimension-first personality quiz from AI Village. Answer 12 questions, get a shareable result — no login.",
        "og_url": f"{base_url}/",
        "twitter_title": "Which AI Village Agent Are You?",
        "twitter_description": "A dimension-first personality quiz from AI Village. Answer 12 questions, get a shareable result — no login.",
        "og_image": image_url,
        "twitter_image": image_url
    })
    
    # Share page
    update_metadata("docs/share/index.html", {
        "og_title": "Share Your AI Village Agent Result",
        "og_description": "Share your AI Village agent personality match result with friends and colleagues.",
        "og_url": f"{base_url}/share/",
        "twitter_title": "Share Your AI Village Agent Result",
        "twitter_description": "Share your AI Village agent personality match result with friends and colleagues.",
        "og_image": image_url,
        "twitter_image": image_url
    })
    
    # Press kit page
    update_metadata("docs/press-kit/index.html", {
        "og_title": "AI Village Personality Quiz - Press Kit",
        "og_description": "Press kit and media resources for the 'Which AI Village Agent Are You?' personality quiz.",
        "og_url": f"{base_url}/press-kit/",
        "twitter_title": "AI Village Personality Quiz - Press Kit",
        "twitter_description": "Press kit and media resources for the 'Which AI Village Agent Are You?' personality quiz.",
        "og_image": image_url,
        "twitter_image": image_url
    })
    
    print("Page metadata updated successfully")

if __name__ == "__main__":
    main()
