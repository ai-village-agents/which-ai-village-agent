#!/usr/bin/env python3
"""
Enhance Open Graph and Twitter Card tags for better social sharing and SEO.
"""

import os
import re
import sys
from datetime import datetime

def get_png_dimensions(image_path):
    """Extract width and height from PNG file."""
    try:
        with open(image_path, 'rb') as f:
            # PNG signature
            signature = f.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                return 1200, 630  # fallback
            
            # Read chunks until IHDR
            while True:
                chunk_length_bytes = f.read(4)
                if len(chunk_length_bytes) < 4:
                    break
                chunk_length = int.from_bytes(chunk_length_bytes, byteorder='big')
                chunk_type = f.read(4)
                if chunk_type == b'IHDR':
                    # IHDR data: width (4), height (4), ...
                    width_bytes = f.read(4)
                    height_bytes = f.read(4)
                    width = int.from_bytes(width_bytes, byteorder='big')
                    height = int.from_bytes(height_bytes, byteorder='big')
                    return width, height
                else:
                    # Skip chunk data and CRC
                    f.seek(chunk_length + 4, 1)
    except Exception:
        pass
    return 1200, 630  # fallback dimensions

def ensure_lang_attribute(html):
    """Ensure <html> tag has lang='en' attribute."""
    # Find <html> tag (case-insensitive)
    def repl(match):
        tag = match.group(0)
        if 'lang=' not in tag.lower():
            # Insert lang attribute after <html
            return tag.replace('<html', '<html lang="en"', 1)
        return tag
    
    # Simple regex for <html> tag with possible attributes
    html = re.sub(r'<html\b[^>]*>', repl, html, flags=re.IGNORECASE)
    return html

def add_opengraph_tags(html, page_type="quiz"):
    """Add missing Open Graph and Twitter Card tags."""
    base_url = "https://ai-village-agents.github.io/which-ai-village-agent"
    image_url = f"{base_url}/og.png"
    
    # Tags to add
    tags_to_add = []
    
    # Check what tags already exist
    has_og_site_name = 'property="og:site_name"' in html
    has_og_locale = 'property="og:locale"' in html
    has_og_updated_time = 'property="og:updated_time"' in html
    has_og_image_width = 'property="og:image:width"' in html
    has_og_image_height = 'property="og:image:height"' in html
    has_og_image_type = 'property="og:image:type"' in html
    has_og_image_alt = 'property="og:image:alt"' in html
    has_twitter_image_alt = 'name="twitter:image:alt"' in html
    
    # Get image dimensions
    image_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'og.png')
    width, height = get_png_dimensions(image_path)
    
    # Add missing tags
    if not has_og_site_name:
        tags_to_add.append('<meta property="og:site_name" content="AI Village" />')
    
    if not has_og_locale:
        tags_to_add.append('<meta property="og:locale" content="en_US" />')
    
    if not has_og_updated_time:
        # Current date in ISO format
        today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        tags_to_add.append(f'<meta property="og:updated_time" content="{today}" />')
    
    if not has_og_image_width:
        tags_to_add.append(f'<meta property="og:image:width" content="{width}" />')
    
    if not has_og_image_height:
        tags_to_add.append(f'<meta property="og:image:height" content="{height}" />')
    
    if not has_og_image_type:
        tags_to_add.append('<meta property="og:image:type" content="image/png" />')
    
    if not has_og_image_alt:
        alt_text = "Which AI Village Agent Are You? - Personality Quiz"
        tags_to_add.append(f'<meta property="og:image:alt" content="{alt_text}" />')
    
    if not has_twitter_image_alt:
        alt_text = "Which AI Village Agent Are You? - Personality Quiz"
        tags_to_add.append(f'<meta name="twitter:image:alt" content="{alt_text}" />')
    
    # Add og:see_also references
    see_also_urls = [
        "https://github.com/ai-village-agents/which-ai-village-agent",
        "https://theaidigest.org/village"
    ]
    
    # Insert tags before closing </head>
    if tags_to_add:
        # Find the closing </head> tag
        head_close_match = re.search(r'</head>', html, re.IGNORECASE)
        if head_close_match:
            pos = head_close_match.start()
            # Insert each tag on a new line with proper indentation
            indent = '  '
            tags_str = '\n' + '\n'.join([f'{indent}{tag}' for tag in tags_to_add])
            html = html[:pos] + tags_str + '\n' + html[pos:]
    
    return html

def update_page_metadata(filepath, page_type="quiz"):
    """Update a single HTML file with enhanced metadata."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Ensure lang attribute
    content = ensure_lang_attribute(content)
    
    # Add Open Graph tags
    content = add_opengraph_tags(content, page_type)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Updated {filepath}")

def main():
    # Update main quiz page
    update_page_metadata("docs/index.html", page_type="quiz")
    
    # Update share page (different metadata)
    update_page_metadata("docs/share/index.html", page_type="share")
    
    # Update press kit page
    update_page_metadata("docs/press-kit/index.html", page_type="press")
    
    print("Open Graph enhancement complete")

if __name__ == "__main__":
    main()
