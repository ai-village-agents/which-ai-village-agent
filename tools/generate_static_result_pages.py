#!/usr/bin/env python3
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = ROOT / "docs" / "data" / "agents.json"
OUT_ROOT = ROOT / "docs" / "r"

OG_IMAGE = "https://ai-village-agents.github.io/which-ai-village-agent/og.png"
CANONICAL_ROOT = "https://ai-village-agents.github.io/which-ai-village-agent/"


def escape(val: str) -> str:
    return html.escape(val, quote=True)


def build_page(agent: dict) -> str:
    agent_id = agent["id"]
    name = agent["name"]
    tagline = agent["tagline"]
    title = f"I matched with {name} — Which AI Village Agent Are You?"
    description = f"I matched with {name}: {tagline} Take the quiz and share your result."
    canonical = f"{CANONICAL_ROOT}r/{agent_id}/"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}" />
  <link rel="canonical" href="{canonical}" />

  <meta property="og:type" content="website" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(description)}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{OG_IMAGE}" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{escape(title)}" />
  <meta name="twitter:description" content="{escape(description)}" />
  <meta name="twitter:image" content="{OG_IMAGE}" />
</head>
<body>
  <main>
    <h1>{escape(title)}</h1>
    <p>{escape(description)}</p>
    <p><a href="../../?r={escape(agent_id)}">Open your full result</a></p>
  </main>
  <script>
    (function() {{
      const params = new URLSearchParams(window.location.search);
      const v = params.get('v');
      const dest = new URL('../../', window.location.href);
      if (v) {{
        dest.searchParams.set('r', '{escape(agent_id)}');
        dest.searchParams.set('v', v);
        window.location.replace(dest.toString());
        return;
      }}
      window.location.replace(dest.toString());
    }})();
  </script>
</body>
</html>
"""


def main():
    data = json.loads(AGENTS_PATH.read_text(encoding="utf-8"))
    agents = data.get("agents", [])
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        html_doc = build_page(agent)
        target_dir = OUT_ROOT / agent["id"]
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "index.html").write_text(html_doc, encoding="utf-8")
    print(f"Wrote {len(agents)} page(s) to {OUT_ROOT}")


if __name__ == "__main__":
    main()
