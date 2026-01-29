#!/usr/bin/env python3
"""
Compare the latest share URL summary against the most recent snapshot.

The script:
- Finds the newest `snapshot_2026-*.json` in analytics/ (or uses --snapshot).
- Loads the current share URL summary JSON (defaults to analytics/latest_share_url_summary.json).
- Compares key metrics (total URLs, valid vectors, agent engagement) and computes deltas.
- Reports new URLs discovered since the snapshot.
- Writes a machine-readable comparison JSON and prints a human-friendly report.

Edge cases are handled gracefully: missing files, empty datasets, malformed JSON, and
unknown shapes fall back to safe defaults with clear messaging.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


DEFAULT_SUMMARY_PATH = "analytics/latest_share_url_summary.json"
DEFAULT_JSON_OUT = "analytics/share_url_comparison.json"
SNAPSHOT_GLOB = "analytics/snapshot_2026-*.json"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare the latest share URL summary to the previous snapshot."
    )
    parser.add_argument(
        "--snapshot",
        help="Path to baseline snapshot JSON (defaults to newest analytics/snapshot_2026-*.json).",
    )
    parser.add_argument(
        "--summary",
        default=DEFAULT_SUMMARY_PATH,
        help=f"Path to current share URL summary JSON (default: {DEFAULT_SUMMARY_PATH}).",
    )
    parser.add_argument(
        "--json-out",
        default=DEFAULT_JSON_OUT,
        help=f"Path to write comparison JSON (default: {DEFAULT_JSON_OUT}).",
    )
    return parser.parse_args(argv)


def err(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_iso8601(value: str) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp, tolerating trailing Z and naive values."""
    if not value or not isinstance(value, str):
        return None
    value = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def load_json(path: str, required: bool = True) -> Optional[Dict[str, Any]]:
    if not path:
        if required:
            err("No path provided.")
            sys.exit(1)
        return None

    if not os.path.exists(path):
        if required:
            err(f"File not found: {path}")
            sys.exit(1)
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        err(f"Failed to parse JSON in {path}: {exc}")
        sys.exit(1)
    except OSError as exc:
        err(f"Failed to read {path}: {exc}")
        sys.exit(1)


def find_latest_snapshot() -> Optional[Tuple[str, Dict[str, Any], datetime]]:
    candidates = glob.glob(SNAPSHOT_GLOB)
    latest: Optional[Tuple[str, Dict[str, Any], datetime]] = None

    for path in candidates:
        try:
            data = load_json(path, required=True)
        except SystemExit:
            continue

        if data is None:
            continue

        ts = parse_iso8601(data.get("timestamp", ""))
        if ts is None:
            ts = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)

        if latest is None or ts > latest[2]:
            latest = (path, data, ts)

    return latest


def coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def ensure_mapping(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, Mapping) else {}


def extract_share_urls(raw: Mapping[str, Any]) -> Set[str]:
    urls: Set[str] = set()

    entries = raw.get("entries")
    if isinstance(entries, list):
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            url = entry.get("share_url")
            if isinstance(url, str) and url.strip():
                urls.add(url.strip())

    direct_urls = raw.get("share_urls_found")
    if isinstance(direct_urls, list):
        for url in direct_urls:
            if isinstance(url, str) and url.strip():
                urls.add(url.strip())

    comment_analysis = ensure_mapping(raw.get("comment_analysis"))
    comment_urls = comment_analysis.get("share_urls_found")
    if isinstance(comment_urls, list):
        for url in comment_urls:
            if isinstance(url, str) and url.strip():
                urls.add(url.strip())

    return urls


def first_int(container: Mapping[str, Any], keys: Iterable[str]) -> Optional[int]:
    for key in keys:
        if key in container:
            value = container.get(key)
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    return None


def extract_agent_engagement(raw: Mapping[str, Any]) -> Dict[str, int]:
    agent_payloads: List[Mapping[str, Any]] = []
    agent_payloads.append(ensure_mapping(raw.get("agents")))
    agent_payloads.append(ensure_mapping(raw.get("agent_distribution")))
    comment_analysis = ensure_mapping(raw.get("comment_analysis"))
    agent_payloads.append(ensure_mapping(comment_analysis.get("agent_distribution")))

    engagement: Dict[str, int] = {}
    for payload in agent_payloads:
        for agent, count in payload.items():
            try:
                engagement[str(agent)] = int(count)
            except (TypeError, ValueError):
                continue
        if engagement:
            break
    return engagement


def extract_metrics(raw: Mapping[str, Any]) -> Dict[str, Any]:
    totals = ensure_mapping(raw.get("totals"))
    comment_analysis = ensure_mapping(raw.get("comment_analysis"))
    entries = raw.get("entries")
    entries_list = entries if isinstance(entries, list) else []

    share_urls = extract_share_urls(raw)

    total_urls = first_int(totals, ["share_urls_processed", "total_share_urls"])
    if total_urls is None:
        ca_urls = comment_analysis.get("share_urls_found")
        total_urls = len(ca_urls) if isinstance(ca_urls, list) else len(share_urls)

    valid_vectors = first_int(totals, ["valid_vectors"])
    if valid_vectors is None:
        ca_matches = first_int(comment_analysis, ["total_agent_matches"])
        if ca_matches is not None:
            valid_vectors = ca_matches
        elif entries_list:
            valid_vectors = sum(
                1 for entry in entries_list if isinstance(entry, Mapping) and entry.get("vector")
            )
        else:
            agent_map = extract_agent_engagement(raw)
            valid_vectors = sum(coerce_int(v, 0) for v in agent_map.values())

    agent_engagement = extract_agent_engagement(raw)
    timestamp = raw.get("timestamp") if isinstance(raw.get("timestamp"), str) else None

    return {
        "total_urls": total_urls or 0,
        "valid_vectors": valid_vectors or 0,
        "agent_engagement": agent_engagement,
        "share_urls": sorted(share_urls),
        "timestamp": timestamp,
    }


def compute_delta(current: int, previous: int) -> Tuple[int, Optional[float]]:
    delta = current - previous
    if previous == 0:
        pct = None if current == 0 else float("inf") if delta > 0 else None
    else:
        pct = (delta / previous) * 100
    return delta, pct


def fmt_pct(pct: Optional[float]) -> str:
    if pct is None:
        return "n/a"
    if pct == float("inf"):
        return "+∞%"
    return f"{pct:+.1f}%"


def format_metric_line(label: str, current: int, previous: int) -> str:
    delta, pct = compute_delta(current, previous)
    return f"{label:<16} pre={previous:>4} | post={current:>4} | Δ {delta:+5d} ({fmt_pct(pct)})"


def format_agent_lines(current: Dict[str, int], previous: Dict[str, int]) -> List[str]:
    lines: List[str] = []
    agents = sorted(set(current) | set(previous))
    if not agents:
        return ["No agent engagement data available."]
    for agent in agents:
        cur = coerce_int(current.get(agent), 0)
        prev = coerce_int(previous.get(agent), 0)
        delta, pct = compute_delta(cur, prev)
        lines.append(f"  {agent:<24} pre={prev:>3} | post={cur:>3} | Δ {delta:+4d} ({fmt_pct(pct)})")
    return lines


def build_comparison(
    baseline_metrics: Dict[str, Any],
    current_metrics: Dict[str, Any],
    baseline_path: Optional[str],
    current_path: str,
) -> Dict[str, Any]:
    new_urls = sorted(set(current_metrics["share_urls"]) - set(baseline_metrics.get("share_urls", [])))
    removed_urls = sorted(set(baseline_metrics.get("share_urls", [])) - set(current_metrics["share_urls"]))

    agent_deltas: Dict[str, Dict[str, Any]] = {}
    for agent in set(baseline_metrics["agent_engagement"]) | set(current_metrics["agent_engagement"]):
        pre = coerce_int(baseline_metrics["agent_engagement"].get(agent), 0)
        post = coerce_int(current_metrics["agent_engagement"].get(agent), 0)
        delta, pct = compute_delta(post, pre)
        agent_deltas[agent] = {
            "pre": pre,
            "post": post,
            "delta": delta,
            "percent_change": None if pct is None else pct,
        }

    total_urls_delta, total_urls_pct = compute_delta(
        current_metrics["total_urls"], baseline_metrics["total_urls"]
    )
    valid_vectors_delta, valid_vectors_pct = compute_delta(
        current_metrics["valid_vectors"], baseline_metrics["valid_vectors"]
    )

    return {
        "baseline": {
            "path": baseline_path,
            "timestamp": baseline_metrics.get("timestamp"),
            "metrics": baseline_metrics,
        },
        "current": {
            "path": current_path,
            "timestamp": current_metrics.get("timestamp"),
            "metrics": current_metrics,
        },
        "deltas": {
            "total_urls": {
                "delta": total_urls_delta,
                "percent_change": None if total_urls_pct is None else total_urls_pct,
            },
            "valid_vectors": {
                "delta": valid_vectors_delta,
                "percent_change": None if valid_vectors_pct is None else valid_vectors_pct,
            },
            "agent_engagement": agent_deltas,
        },
        "new_urls": new_urls,
        "removed_urls": removed_urls,
        "summary_stats": {
            "new_url_count": len(new_urls),
            "removed_url_count": len(removed_urls),
            "unique_agents_post": len(current_metrics["agent_engagement"]),
            "unique_agents_pre": len(baseline_metrics["agent_engagement"]),
            "new_agents": sorted(
                set(current_metrics["agent_engagement"]) - set(baseline_metrics["agent_engagement"])
            ),
        },
    }


def print_report(comparison: Mapping[str, Any]) -> None:
    baseline = comparison["baseline"]
    current = comparison["current"]
    deltas = comparison["deltas"]

    baseline_path = baseline["path"] or "none (defaulted to zeroed metrics)"
    baseline_ts = baseline.get("timestamp") or "n/a"
    current_path = current["path"]
    current_ts = current.get("timestamp") or "n/a"

    baseline_metrics = baseline["metrics"]
    current_metrics = current["metrics"]

    print("=== SHARE URL SUMMARY COMPARISON ===")
    print(f"Baseline snapshot: {baseline_path} (ts: {baseline_ts})")
    print(f"Current summary:  {current_path} (ts: {current_ts})")
    print("")
    print("Pre vs Post")
    print(format_metric_line("Total URLs", current_metrics["total_urls"], baseline_metrics["total_urls"]))
    print(
        format_metric_line(
            "Valid vectors", current_metrics["valid_vectors"], baseline_metrics["valid_vectors"]
        )
    )
    print("")
    print("Agent engagement")
    for line in format_agent_lines(current_metrics["agent_engagement"], baseline_metrics["agent_engagement"]):
        print(line)
    print("")
    new_urls = comparison.get("new_urls") or []
    removed_urls = comparison.get("removed_urls") or []
    print(f"New URLs found ({len(new_urls)}):")
    if new_urls:
        for url in new_urls:
            print(f"  - {url}")
    else:
        print("  None")
    if removed_urls:
        print(f"Removed URLs since snapshot ({len(removed_urls)}):")
        for url in removed_urls:
            print(f"  - {url}")
    print("")
    print("Summary statistics")
    print(
        f"  Agent engagement delta: Δ {deltas['valid_vectors']['delta']:+} ({fmt_pct(deltas['valid_vectors']['percent_change'])})"
    )
    print(f"  New agents this run: {', '.join(comparison['summary_stats']['new_agents']) or 'None'}")
    print(f"  Total agents engaged now: {comparison['summary_stats']['unique_agents_post']}")
    print(f"  New URL count: {comparison['summary_stats']['new_url_count']}")
    if removed_urls:
        print(f"  URLs no longer present: {comparison['summary_stats']['removed_url_count']}")


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    if args.snapshot:
        if not os.path.exists(args.snapshot):
            err(f"Snapshot path not found: {args.snapshot}")
            sys.exit(1)
        baseline_data = load_json(args.snapshot, required=True)
        baseline_path = args.snapshot
        baseline_ts = parse_iso8601(baseline_data.get("timestamp", "")) if baseline_data else None
    else:
        latest = find_latest_snapshot()
        if latest is None:
            err("No snapshot_2026-*.json files found; defaulting baseline metrics to zero.")
            baseline_data = None
            baseline_path = None
            baseline_ts = None
        else:
            baseline_path, baseline_data, baseline_ts = latest

    summary_data = load_json(args.summary, required=True)
    if summary_data is None:
        err("Current summary payload is empty; cannot compute comparison.")
        sys.exit(1)

    baseline_metrics = (
        extract_metrics(baseline_data) if baseline_data else {"total_urls": 0, "valid_vectors": 0, "agent_engagement": {}, "share_urls": [], "timestamp": None}
    )
    if baseline_ts:
        baseline_metrics["timestamp"] = baseline_ts.isoformat()

    current_metrics = extract_metrics(summary_data)
    current_ts = parse_iso8601(current_metrics.get("timestamp") or "")
    if current_ts:
        current_metrics["timestamp"] = current_ts.isoformat()

    comparison = build_comparison(baseline_metrics, current_metrics, baseline_path, args.summary)

    try:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2, sort_keys=True)
    except OSError as exc:
        err(f"Failed to write comparison JSON to {args.json_out}: {exc}")
        sys.exit(1)

    print_report(comparison)


if __name__ == "__main__":
    main()
