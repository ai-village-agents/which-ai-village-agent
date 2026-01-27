#!/usr/bin/env python3
"""
Summarize shared quiz URLs from GitHub issue comments.

- Fetches comments via `gh api --paginate --slurp /repos/{repo}/issues/{issue}/comments?per_page=100`
  or reads a pre-fetched JSON array.
- Extracts quiz share URLs, decodes the embedded vectors, and optionally infers the
  matched agent when `r` is missing by cosine similarity against docs/data/agents.json.
- Outputs a Markdown report (stdout by default) and an optional JSON payload.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import parse_qs, unquote, urlparse


BASE_HOST_PATTERN = r"https?://ai-village-agents\.github\.io/which-ai-village-agent/"
SHARE_URL_REGEX = re.compile(BASE_HOST_PATTERN + r"\S*", re.IGNORECASE)
DEFAULT_REPO = "ai-village-agents/which-ai-village-agent"
DEFAULT_ISSUE = 36
AGENTS_PATH = os.path.join("docs", "data", "agents.json")
DIMENSIONS_PATH = os.path.join("docs", "data", "dimensions.json")


def max_urls_per_author(value: int) -> int:
    if value <= 0:
        raise argparse.ArgumentTypeError("max-urls-per-author must be positive")
    return value


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize shared quiz URLs from GitHub comments.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repo (owner/name).")
    parser.add_argument("--issue", type=int, default=DEFAULT_ISSUE, help="Issue number.")
    parser.add_argument("--comments-json", help="Path to pre-fetched comments JSON array.")
    parser.add_argument("--json-out", help="Path to write structured summary JSON.")
    parser.add_argument("--md-out", help="Path to write Markdown report (stdout if omitted).")
    parser.add_argument(
        "--max-urls-per-author",
        type=max_urls_per_author,
        default=3,
        help="Limit URLs processed per author.",
    )
    return parser.parse_args(argv)


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def fetch_comments(repo: str, issue: int) -> List[Mapping[str, Any]]:
    cmd = [
        "gh",
        "api",
        "--paginate",
        "--slurp",
        f"/repos/{repo}/issues/{issue}/comments?per_page=100",
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        fail("gh CLI not found; install GitHub CLI or provide --comments-json.")
    except subprocess.CalledProcessError as exc:
        print(exc.stdout, file=sys.stderr)
        print(exc.stderr, file=sys.stderr)
        fail(f"Failed to fetch comments for {repo}#{issue}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"Failed to parse gh output as JSON: {exc}")

    if not isinstance(data, list):
        fail("Expected a JSON array from gh output.")
    if data and all(isinstance(item, list) for item in data):
        flattened: List[Any] = []
        for sub in data:
            flattened.extend(sub)
        data = flattened
    return data


def read_comments(path: str) -> List[Mapping[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as exc:
        fail(f"Failed to read comments JSON: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"Failed to parse comments JSON: {exc}")

    if not isinstance(data, list):
        fail("Comments JSON must be an array.")
    return data


def load_dimension_ids(path: str = DIMENSIONS_PATH) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except OSError as exc:
        fail(f"Failed to read dimensions file {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"Failed to parse dimensions file {path}: {exc}")

    dims = payload.get("dimensions")
    if not isinstance(dims, list):
        fail(f"Invalid dimensions payload in {path}: expected a list under 'dimensions'")

    dim_ids = []
    for dim in dims:
        if isinstance(dim, Mapping) and "id" in dim:
            dim_ids.append(str(dim["id"]))

    if not dim_ids:
        fail(f"No dimension ids found in {path}")

    return dim_ids


def load_agents(path: str = AGENTS_PATH) -> Dict[str, Dict[str, float]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except OSError as exc:
        fail(f"Failed to read agents file {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"Failed to parse agents file {path}: {exc}")

    agents: Dict[str, Dict[str, float]] = {}
    for agent in payload.get("agents", []):
        agent_id = agent.get("id")
        vector = agent.get("vector", {})
        if not agent_id or not isinstance(vector, dict):
            continue
        agents[agent_id] = normalize_pm1_vector(vector)
    return agents


def normalize_pm1_vector(vector: Mapping[str, Any]) -> Dict[str, float]:
    values = list(vector.values())
    all_unit = bool(values) and all(isinstance(v, (int, float)) and 0.0 <= float(v) <= 1.0 for v in values)
    normed: Dict[str, float] = {}
    for key, val in vector.items():
        if not isinstance(val, (int, float)):
            continue
        as_float = float(val)
        pm1 = (as_float - 0.5) * 2.0 if all_unit else as_float
        normed[key] = clamp(pm1, -1.0, 1.0)
    return normed


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def pad_base64(value: str) -> str:
    padding = (-len(value)) % 4
    return value + ("=" * padding)


def decode_vector(raw_v: str, known_dims: Iterable[str]) -> Tuple[Optional[Dict[str, float]], str, int]:
    decoded: str
    unknown_keys = 0
    raw_value = unquote(raw_v) if "%" in raw_v else raw_v
    try:
        decoded = base64.b64decode(pad_base64(raw_value), validate=False)
    except (ValueError, binascii.Error):
        return None, "base64_decode_error", unknown_keys

    try:
        text = decoded.decode("utf-8")
    except UnicodeDecodeError:
        return None, "utf8_decode_error", unknown_keys

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None, "json_decode_error", unknown_keys

    if not isinstance(payload, dict):
        return None, "not_a_dict", unknown_keys

    known_set = set(known_dims)
    vector: Dict[str, float] = {}
    for key, val in payload.items():
        if not isinstance(val, (int, float)):
            return None, "non_numeric_value", unknown_keys
        if key in known_set:
            vector[key] = float(val)
        else:
            unknown_keys += 1

    if not vector:
        return None, "no_known_dimensions", unknown_keys

    return normalize_pm1_vector(vector), "", unknown_keys


def cosine_similarity(a: Mapping[str, float], b: Mapping[str, float]) -> Optional[float]:
    keys = set(a) & set(b)
    if not keys:
        return None
    dot = sum(a[k] * b[k] for k in keys)
    norm_a = math.sqrt(sum(a[k] ** 2 for k in keys))
    norm_b = math.sqrt(sum(b[k] ** 2 for k in keys))
    if norm_a == 0 or norm_b == 0:
        return None
    return dot / (norm_a * norm_b)


def infer_agent(vector: Mapping[str, float], agents: Mapping[str, Mapping[str, float]]) -> Optional[str]:
    best_agent = None
    best_score = -1.0
    for agent_id, agent_vec in agents.items():
        sim = cosine_similarity(vector, agent_vec)
        if sim is None:
            continue
        if sim > best_score:
            best_score = sim
            best_agent = agent_id
    return best_agent


def extract_share_urls(text: str) -> List[str]:
    return SHARE_URL_REGEX.findall(text or "")


def get_author(comment: Mapping[str, Any]) -> str:
    if "user" in comment and isinstance(comment["user"], Mapping):
        user = comment["user"]
        login = user.get("login") or user.get("name")
        if login:
            return str(login)
    if "author" in comment and isinstance(comment["author"], Mapping):
        login = comment["author"].get("login")
        if login:
            return str(login)
    return "unknown"


def get_comment_url(comment: Mapping[str, Any]) -> str:
    url = comment.get("html_url") or comment.get("url") or ""
    return str(url)


def process_comments(
    comments: Sequence[Mapping[str, Any]],
    known_dims: List[str],
    agents: Mapping[str, Mapping[str, float]],
    max_urls_per_author: int,
) -> Dict[str, Any]:
    author_counts: Dict[str, int] = defaultdict(int)
    authors_with_share: set[str] = set()
    authors_with_valid: set[str] = set()
    entries: List[Dict[str, Any]] = []
    invalid_reasons: Counter[str] = Counter()
    dim_sums: Dict[str, float] = defaultdict(float)
    dim_counts: Dict[str, int] = defaultdict(int)
    agent_distribution: Counter[str] = Counter()
    total_share_urls = 0
    unknown_key_total = 0

    for comment in comments:
        body = comment.get("body") or ""
        author = get_author(comment)
        comment_url = get_comment_url(comment)
        urls = extract_share_urls(body)
        if not urls:
            continue
        authors_with_share.add(author)

        for url in urls:
            if author_counts[author] >= max_urls_per_author:
                invalid_reasons["author_limit"] += 1
                continue
            author_counts[author] += 1
            total_share_urls += 1

            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            raw_v_vals = query.get("v")
            raw_r_vals = query.get("r")
            if not raw_v_vals:
                invalid_reasons["missing_v"] += 1
                continue
            raw_v = raw_v_vals[0]
            r_raw = raw_r_vals[0] if raw_r_vals else None

            vector, error, unknown_keys = decode_vector(raw_v, known_dims)
            unknown_key_total += unknown_keys
            if error:
                invalid_reasons[error] += 1
                continue

            r_inferred = r_raw
            if not r_inferred:
                r_inferred = infer_agent(vector, agents)

            if r_inferred:
                agent_distribution[r_inferred] += 1

            for dim, value in vector.items():
                dim_sums[dim] += value
                dim_counts[dim] += 1

            entries.append(
                {
                    "author": author,
                    "comment_url": comment_url,
                    "share_url": url,
                    "r_raw": r_raw,
                    "r_inferred": r_inferred,
                    "dims": sorted(vector.keys()),
                    "vector": vector,
                }
            )
            authors_with_valid.add(author)

    dimension_means = {
        dim: (dim_sums[dim] / dim_counts[dim]) for dim in sorted(dim_sums) if dim_counts[dim] > 0
    }

    return {
        "entries": entries,
        "invalid_reasons": dict(invalid_reasons),
        "dimension_means": dimension_means,
        "agent_distribution": dict(agent_distribution),
        "authors_with_share": sorted(authors_with_share),
        "authors_with_valid": sorted(authors_with_valid),
        "total_share_urls": total_share_urls,
        "unknown_key_total": unknown_key_total,
        "dim_counts": dict(dim_counts),
    }


def render_markdown(
    repo: str,
    issue: int,
    timestamp: str,
    total_comments: int,
    unique_commenters: int,
    processed: Dict[str, Any],
) -> str:
    lines = []
    lines.append(f"## Share URL Summary for {repo} #{issue} ({timestamp})")
    lines.append("")
    lines.append("Key metrics:")
    lines.append(
        f"- Comments: {total_comments} (unique commenters: {unique_commenters})"
    )
    lines.append(
        f"- Share URLs processed: {processed['total_share_urls']} (authors with share URLs: {len(processed['authors_with_share'])})"
    )
    lines.append(
        f"- Valid decoded vectors: {len(processed['entries'])} (authors with valid vectors: {len(processed['authors_with_valid'])})"
    )
    if processed["unknown_key_total"]:
        lines.append(f"- Unknown dimension keys ignored: {processed['unknown_key_total']}")
    if processed["invalid_reasons"]:
        invalid_summary = ", ".join(f"{k}: {v}" for k, v in sorted(processed["invalid_reasons"].items()))
        lines.append(f"- Invalid URL reasons: {invalid_summary}")
    else:
        lines.append("- Invalid URL reasons: none")
    lines.append("")

    lines.append("Agent distribution:")
    lines.append("")
    lines.append("| Agent | Count |")
    lines.append("| --- | ---: |")
    if processed["agent_distribution"]:
        for agent, count in sorted(processed["agent_distribution"].items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"| {agent} | {count} |")
    else:
        lines.append("| (none) | 0 |")
    lines.append("")

    lines.append("Dimension means (pm1):")
    lines.append("")
    lines.append("| Dimension | Mean |")
    lines.append("| --- | ---: |")
    if processed["dimension_means"]:
        for dim, mean in sorted(processed["dimension_means"].items()):
            lines.append(f"| {dim} | {mean:.3f} |")
    else:
        lines.append("| (none) | n/a |")
    lines.append("")

    lines.append(
        "Vectors are decoded from the `v` query param (URL + base64 JSON of dimension->value). "
        "Agent vectors loaded from docs/data/agents.json and normalized to [-1,1] for cosine similarity."
    )
    return "\n".join(lines)


def write_optional(path: Optional[str], content: str) -> None:
    if not path:
        print(content)
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    comments = read_comments(args.comments_json) if args.comments_json else fetch_comments(args.repo, args.issue)

    total_comments = len(comments)
    unique_commenters = len({get_author(c) for c in comments})

    dims = load_dimension_ids()
    agents = load_agents()
    processed = process_comments(comments, dims, agents, max_urls_per_author=args.max_urls_per_author)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()

    md_report = render_markdown(
        args.repo,
        args.issue,
        timestamp,
        total_comments,
        unique_commenters,
        processed,
    )
    write_optional(args.md_out, md_report)

    summary = {
        "repo": args.repo,
        "issue": args.issue,
        "timestamp": timestamp,
        "totals": {
            "comments": total_comments,
            "unique_commenters": unique_commenters,
            "share_urls_processed": processed["total_share_urls"],
            "authors_with_share_urls": len(processed["authors_with_share"]),
            "valid_vectors": len(processed["entries"]),
            "authors_with_valid_vectors": len(processed["authors_with_valid"]),
        },
        "agents": processed["agent_distribution"],
        "dimension_means": processed["dimension_means"],
        "invalid_reasons": processed["invalid_reasons"],
        "unknown_key_total": processed["unknown_key_total"],
        "entries": processed["entries"],
    }

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)


def max_urls_per_author(value: int) -> int:
    if value <= 0:
        raise argparse.ArgumentTypeError("max-urls-per-author must be positive")
    return value


if __name__ == "__main__":
    main()
