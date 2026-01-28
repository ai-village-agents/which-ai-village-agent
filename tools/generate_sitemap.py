#!/usr/bin/env python3
"""Generate docs/sitemap.xml for GitHub Pages.

We intentionally list only canonical, crawlable paths (no query params).
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_JSON = REPO_ROOT / "docs" / "data" / "agents.json"
SITEMAP_XML = REPO_ROOT / "docs" / "sitemap.xml"

BASE = "https://ai-village-agents.github.io/which-ai-village-agent/"


def main() -> None:
    data = json.loads(AGENTS_JSON.read_text(encoding="utf-8"))
    agents = data["agents"]

    today = _dt.date.today().isoformat()

    urls: list[str] = [BASE]
    urls += [f"{BASE}press-kit/"]

    # Per-agent share landing pages (canonical; no query params).
    urls += [f"{BASE}r/{a['id']}/" for a in agents]

    # Build sitemap.
    xml_lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        xml_lines += [
            "  <url>",
            f"    <loc>{u}</loc>",
            f"    <lastmod>{today}</lastmod>",
            "  </url>",
        ]
    xml_lines.append("</urlset>")

    out = "\n".join(xml_lines) + "\n"
    SITEMAP_XML.write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
