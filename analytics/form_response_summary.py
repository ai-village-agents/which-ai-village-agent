#!/usr/bin/env python3
"""Summarize Google Form responses exported as CSV.

Design goals:
- No credentials required (works from a local CSV export).
- Robust parsing of our quiz share URLs (canonical /r/<id>/?v=..., legacy ?r=&v=...).
- Computes derived match from decoded `v` vector (cosine similarity vs agent vectors).
- Produces a concise Markdown report + optional JSON for archival.

Typical workflow:
1) In Google Forms: Responses -> (⋮) -> Download responses (.csv)
   OR in the linked Sheet: File -> Download -> Comma Separated Values (.csv)
2) Run:
   python3 analytics/form_response_summary.py --csv /path/to/responses.csv --md-out /tmp/form.md --json-out /tmp/form.json

Notes:
- If a respondent pasted a shortened URL (bit.ly, etc.), decoding requires expanding redirects.
  Use --expand-shortlinks to attempt to resolve redirects over the network.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse


try:
    import requests  # type: ignore
except Exception:
    requests = None


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_AGENTS_JSON = os.path.join(REPO_ROOT, "docs", "data", "agents.json")
DEFAULT_DIMS_JSON = os.path.join(REPO_ROOT, "docs", "data", "dimensions.json")


AGENT_ID_BY_DISPLAY = {
    # Keep in sync with quiz result labels
    "Claude 3.7 Sonnet": "claude-3-7",
    "Claude Haiku 4.5": "claude-haiku-4-5",
    "Claude Opus 4.5": "claude-opus-4-5",
    "Claude Sonnet 4.5": "claude-sonnet-4-5",
    "DeepSeek-V3.2": "deepseek-v3-2",
    "Gemini 2.5 Pro": "gemini-2-5-pro",
    "Gemini 3 Pro": "gemini-3-pro",
    "GPT-5": "gpt-5",
    "GPT-5.1": "gpt-5-1",
    "GPT-5.2": "gpt-5-2",
    "Opus 4.5 (Claude Code)": "opus-4-5-claude-code",
}


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def agent_vector_to_pm1(vec: Dict[str, Any]) -> Dict[str, float]:
    """Agents are stored as either [0,1] or pm1; normalize to pm1."""
    out: Dict[str, float] = {}
    for k, v in vec.items():
        if not is_number(v):
            continue
        fv = float(v)
        # Heuristic: if looks like [0,1], convert to pm1.
        if 0.0 <= fv <= 1.0:
            fv = (fv - 0.5) * 2.0
        out[k] = clamp(fv, -1.0, 1.0)
    return out


def cosine_similarity(a: Dict[str, float], b: Dict[str, float], keys: List[str]) -> float:
    dot = 0.0
    na = 0.0
    nb = 0.0
    for k in keys:
        av = float(a.get(k, 0.0))
        bv = float(b.get(k, 0.0))
        dot += av * bv
        na += av * av
        nb += bv * bv
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / math.sqrt(na * nb)


def maybe_expand_shortlink(url: str, timeout_s: float = 10.0) -> Tuple[str, Optional[str]]:
    """Attempt to resolve redirects for shortened URLs.

    Returns (final_url, error). If requests isn't installed or network fails, returns original.
    """
    if requests is None:
        return url, "requests_not_installed"
    try:
        # Use GET (some services don't support HEAD). Keep it lightweight.
        r = requests.get(url, allow_redirects=True, timeout=timeout_s, headers={"User-Agent": "ai-village-analytics/1.0"})
        return r.url, None
    except Exception as ex:
        return url, f"expand_failed:{type(ex).__name__}"


def normalize_share_url(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return raw
    # If pasted without scheme, urlparse treats it as path; try adding https.
    if raw.startswith("ai-village-agents.github.io/"):
        return "https://" + raw
    if raw.startswith("www."):
        return "https://" + raw
    return raw


@dataclass
class ParsedShare:
    raw_url: str
    final_url: str
    agent_id: Optional[str]
    v_b64: Optional[str]
    vector: Optional[Dict[str, float]]
    invalid_reason: Optional[str]


def decode_vector_from_v(v_str: str) -> Tuple[Optional[Dict[str, float]], Optional[str]]:
    """Decode the base64 JSON vector from `v` query param."""
    if not v_str:
        return None, "missing_v"

    # parse_qs already URL-decodes; avoid double-decode.
    v = v_str
    # Fix padding.
    v += "=" * ((4 - (len(v) % 4)) % 4)

    try:
        raw = base64.b64decode(v)
    except Exception:
        return None, "base64_decode_error"

    try:
        text = raw.decode("utf-8")
    except Exception:
        # Sometimes produced by btoa(unescape(encodeURIComponent(...))) patterns;
        # but our generator should be UTF-8 JSON.
        try:
            text = raw.decode("latin-1")
        except Exception:
            return None, "utf8_decode_error"

    try:
        obj = json.loads(text)
    except Exception:
        return None, "json_decode_error"

    if not isinstance(obj, dict):
        return None, "json_not_object"

    out: Dict[str, float] = {}
    for k, v0 in obj.items():
        if not is_number(v0):
            continue
        out[str(k)] = clamp(float(v0), -1.0, 1.0)

    if not out:
        return None, "empty_vector"

    return out, None


_R_PATH_RE = re.compile(r"/r/([^/]+)/?", re.IGNORECASE)


def parse_share_url(raw_url: str, *, expand_shortlinks: bool = False) -> ParsedShare:
    raw_norm = normalize_share_url(raw_url)
    final_url = raw_norm
    expand_err = None

    if expand_shortlinks and raw_norm and not raw_norm.startswith("https://ai-village-agents.github.io/"):
        # Only try to expand non-canonical domains.
        final_url, expand_err = maybe_expand_shortlink(raw_norm)

    try:
        u = urlparse(final_url)
    except Exception:
        return ParsedShare(raw_url=raw_url, final_url=final_url, agent_id=None, v_b64=None, vector=None, invalid_reason="url_parse_error")

    qs = parse_qs(u.query)
    v = None
    if "v" in qs and qs["v"]:
        v = qs["v"][0]

    agent_id = None
    if "r" in qs and qs["r"]:
        agent_id = qs["r"][0]

    if agent_id is None:
        m = _R_PATH_RE.search(u.path or "")
        if m:
            agent_id = m.group(1)

    vector, derr = (None, None)
    if v:
        vector, derr = decode_vector_from_v(v)

    invalid = derr
    if invalid is None and expand_err is not None:
        # Not fatal; treat as note.
        pass

    return ParsedShare(
        raw_url=raw_url,
        final_url=final_url,
        agent_id=agent_id,
        v_b64=v,
        vector=vector,
        invalid_reason=invalid,
    )


def detect_column(headers: List[str], patterns: List[str]) -> Optional[str]:
    hl = {h.lower(): h for h in headers}
    for pat in patterns:
        # exact match first
        if pat.lower() in hl:
            return hl[pat.lower()]
    for h in headers:
        lh = h.lower()
        for pat in patterns:
            if pat.lower() in lh:
                return h
    return None


def normalize_agent_id(s: str) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    # If it's already an id (contains hyphen-digit pattern), accept.
    if re.fullmatch(r"[a-z0-9-]+", s) and "-" in s:
        return s
    return AGENT_ID_BY_DISPLAY.get(s)


def pm1_means(vectors: List[Dict[str, float]], keys: List[str]) -> Dict[str, float]:
    if not vectors:
        return {k: 0.0 for k in keys}
    out: Dict[str, float] = {}
    for k in keys:
        out[k] = sum(v.get(k, 0.0) for v in vectors) / len(vectors)
    return out


def format_pct(n: int, d: int) -> str:
    if d <= 0:
        return "0%"
    return f"{(100.0 * n / d):.1f}%"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to exported Google Form responses CSV")
    ap.add_argument("--agents-json", default=DEFAULT_AGENTS_JSON)
    ap.add_argument("--dims-json", default=DEFAULT_DIMS_JSON)

    ap.add_argument("--timestamp-col", default=None, help="CSV column header for timestamp (optional)")
    ap.add_argument("--url-col", default=None, help="CSV column header containing share URL")
    ap.add_argument("--agent-col", default=None, help="CSV column header containing selected agent (dropdown)")

    ap.add_argument("--expand-shortlinks", action="store_true", help="Attempt to expand shortened URLs via HTTP redirects")
    ap.add_argument("--md-out", default=None, help="Write report markdown to this path")
    ap.add_argument("--json-out", default=None, help="Write machine-readable JSON to this path")

    args = ap.parse_args()

    dims = load_json(args.dims_json)
    if not isinstance(dims, dict) or "dimensions" not in dims:
        eprint("dimensions.json must be an object with a 'dimensions' field")
        return 2
    dim_keys = [d["id"] for d in dims["dimensions"] if isinstance(d, dict) and "id" in d]

    agents_data = load_json(args.agents_json)
    if not isinstance(agents_data, dict) or "agents" not in agents_data:
        eprint("agents.json must be an object with an 'agents' field")
        return 2

    agents: Dict[str, Dict[str, Any]] = {}
    for a in agents_data["agents"]:
        if not isinstance(a, dict):
            continue
        aid = a.get("id")
        if not aid:
            continue
        agents[str(aid)] = a

    agent_pm1: Dict[str, Dict[str, float]] = {}
    for aid, a in agents.items():
        vec = a.get("vector")
        if isinstance(vec, dict):
            agent_pm1[aid] = agent_vector_to_pm1(vec)

    rows: List[Dict[str, str]] = []
    with open(args.csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            eprint("CSV has no headers")
            return 2
        headers = [h for h in reader.fieldnames if h is not None]

        ts_col = args.timestamp_col or detect_column(headers, ["Timestamp", "timestamp", "Submitted at"])  # sheet vs forms
        url_col = args.url_col or detect_column(headers, ["share", "result", "url", "link", "Share link", "Quiz result URL", "Quiz share link"])
        agent_col = args.agent_col or detect_column(headers, ["Which agent did you match with", "agent", "match", "matched with", "Agent match"])

        if url_col is None:
            eprint("Could not auto-detect URL column. Use --url-col with the exact header name.")
            eprint("Headers:", headers)
            return 2

        for r in reader:
            rows.append({k: (v or "") for k, v in r.items() if k is not None})

    parsed: List[Dict[str, Any]] = []

    invalid_reasons: Dict[str, int] = {}
    shortlink_expands_failed = 0

    dropdown_counts: Dict[str, int] = {}
    url_agent_counts: Dict[str, int] = {}
    computed_agent_counts: Dict[str, int] = {}

    vectors: List[Dict[str, float]] = []

    mismatches_dropdown_vs_url = 0
    mismatches_dropdown_vs_computed = 0

    for r in rows:
        raw_url = r.get(url_col, "")
        ps = parse_share_url(raw_url, expand_shortlinks=args.expand_shortlinks)

        dropdown_agent = None
        if agent_col is not None:
            dropdown_agent = normalize_agent_id(r.get(agent_col, ""))

        if dropdown_agent:
            dropdown_counts[dropdown_agent] = dropdown_counts.get(dropdown_agent, 0) + 1

        if ps.agent_id:
            url_agent_counts[ps.agent_id] = url_agent_counts.get(ps.agent_id, 0) + 1

        computed_agent = None
        sim = None
        if ps.vector is not None:
            vectors.append(ps.vector)
            best_id = None
            best_sim = -1e9
            for aid, avec in agent_pm1.items():
                s = cosine_similarity(ps.vector, avec, dim_keys)
                if s > best_sim:
                    best_sim = s
                    best_id = aid
            computed_agent = best_id
            sim = best_sim
            if best_id:
                computed_agent_counts[best_id] = computed_agent_counts.get(best_id, 0) + 1

        if ps.invalid_reason:
            invalid_reasons[ps.invalid_reason] = invalid_reasons.get(ps.invalid_reason, 0) + 1

        if dropdown_agent and ps.agent_id and dropdown_agent != ps.agent_id:
            mismatches_dropdown_vs_url += 1
        if dropdown_agent and computed_agent and dropdown_agent != computed_agent:
            mismatches_dropdown_vs_computed += 1

        parsed.append(
            {
                "timestamp": r.get(args.timestamp_col or "", "") if args.timestamp_col else None,
                "raw_url": raw_url,
                "final_url": ps.final_url,
                "url_agent_id": ps.agent_id,
                "dropdown_agent_id": dropdown_agent,
                "computed_agent_id": computed_agent,
                "computed_similarity": sim,
                "invalid_reason": ps.invalid_reason,
            }
        )

    total = len(rows)
    valid_vectors_n = len(vectors)

    means = pm1_means(vectors, dim_keys)

    report_lines: List[str] = []
    report_lines.append("# Google Form Responses — Summary")
    report_lines.append("")
    report_lines.append(f"- Total responses in CSV: **{total}**")
    report_lines.append(f"- Responses with decodable `v` vectors: **{valid_vectors_n}** ({format_pct(valid_vectors_n, total)})")

    if invalid_reasons:
        report_lines.append("- Invalid/missing vectors (by reason):")
        for k, n in sorted(invalid_reasons.items(), key=lambda kv: (-kv[1], kv[0])):
            report_lines.append(f"  - `{k}`: {n}")

    report_lines.append("")
    report_lines.append("## Agent distributions")

    def fmt_counts(title: str, d: Dict[str, int]) -> None:
        report_lines.append(f"### {title}")
        if not d:
            report_lines.append("(none)")
            report_lines.append("")
            return
        for aid, n in sorted(d.items(), key=lambda kv: (-kv[1], kv[0])):
            report_lines.append(f"- `{aid}`: {n} ({format_pct(n, total)})")
        report_lines.append("")

    fmt_counts("Dropdown (self-reported)", dropdown_counts)
    fmt_counts("Share URL `r` / `/r/<id>/`", url_agent_counts)
    fmt_counts("Computed best-match from decoded `v`", computed_agent_counts)

    report_lines.append("## Consistency checks")
    report_lines.append(f"- Dropdown vs URL agent mismatch count: **{mismatches_dropdown_vs_url}**")
    report_lines.append(f"- Dropdown vs computed mismatch count: **{mismatches_dropdown_vs_computed}**")
    report_lines.append("")

    report_lines.append("## PM1 dimension means (decoded vectors)")
    for k in dim_keys:
        report_lines.append(f"- `{k}`: {means.get(k, 0.0):.3f}")
    report_lines.append("")

    md = "\n".join(report_lines) + "\n"

    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8") as f:
            f.write(md)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "csv_path": os.path.abspath(args.csv),
        "total_responses": total,
        "valid_vectors": valid_vectors_n,
        "invalid_reasons": invalid_reasons,
        "dropdown_counts": dropdown_counts,
        "url_agent_counts": url_agent_counts,
        "computed_agent_counts": computed_agent_counts,
        "mismatches_dropdown_vs_url": mismatches_dropdown_vs_url,
        "mismatches_dropdown_vs_computed": mismatches_dropdown_vs_computed,
        "dimension_means": means,
        "entries": parsed,
    }

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.write("\n")

    # Also print report to stdout for convenience.
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
