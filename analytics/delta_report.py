#!/usr/bin/env python3
"""
Compare two enhanced analytics snapshots and emit a delta report.

Usage:
    python analytics/delta_report.py [base_snapshot] [latest_snapshot]

If no paths are provided, the script will automatically pick the two most
recent enhanced snapshots in analytics/ matching
`enhanced_snapshot_*.json`.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo


PACIFIC = ZoneInfo("America/Los_Angeles")


@dataclass
class Snapshot:
    path: str
    raw: Dict[str, Any]
    timestamp: datetime


def parse_iso_timestamp(value: str) -> Optional[datetime]:
    """Parse an ISO timestamp, tolerating a trailing Z."""
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def load_snapshot(path: str) -> Snapshot:
    with open(path, "r") as f:
        raw = json.load(f)

    ts = parse_iso_timestamp(raw.get("timestamp") or "")
    if ts is None:
        # Fall back to file modified time if timestamp is missing.
        ts = datetime.fromtimestamp(os.path.getmtime(path), tz=ZoneInfo("UTC"))
    elif ts.tzinfo is None:
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))

    return Snapshot(path=path, raw=raw, timestamp=ts)


def find_recent_snapshots() -> Tuple[str, str]:
    """Return the two most recent enhanced snapshots by timestamp."""
    candidates = sorted(glob.glob("analytics/enhanced_snapshot_*.json"))
    if len(candidates) < 2:
        raise SystemExit("Need at least two enhanced snapshots to compute a delta.")

    snapshots_with_ts: List[Tuple[datetime, str]] = []
    for path in candidates:
        try:
            snap = load_snapshot(path)
            snapshots_with_ts.append((snap.timestamp, path))
        except Exception:
            # Skip unreadable/malformed files.
            continue

    snapshots_with_ts.sort(key=lambda item: item[0])
    if len(snapshots_with_ts) < 2:
        raise SystemExit("Not enough readable enhanced snapshots to compute a delta.")

    _, prev_path = snapshots_with_ts[-2]
    _, latest_path = snapshots_with_ts[-1]
    return prev_path, latest_path


def safe_get_number(container: Dict[str, Any], key: str, default: int = 0) -> int:
    try:
        value = container.get(key, default)
        return int(value)
    except (TypeError, ValueError):
        return default


def extract_metrics(raw: Dict[str, Any]) -> Dict[str, Any]:
    issue = raw.get("issue_metrics", {}) or {}
    quiz = raw.get("quiz_health", {}) or {}
    analysis = raw.get("comment_analysis", {}) or {}

    endpoints = quiz.get("endpoints") or []
    accessible_count = sum(1 for ep in endpoints if ep.get("accessible"))
    endpoints_total = len(endpoints)

    sentiment = analysis.get("sentiment_distribution", {}) or {}

    return {
        "comment_count": safe_get_number(issue, "comment_count"),
        "total_reactions": safe_get_number(issue, "total_reactions"),
        "agents_count": safe_get_number(quiz, "agents_count"),
        "endpoints_accessible": accessible_count,
        "endpoints_total": endpoints_total,
        "all_accessible": bool(quiz.get("all_accessible", False)),
        "agent_matches": safe_get_number(analysis, "total_agent_matches"),
        "share_urls": len(analysis.get("share_urls_found") or []),
        "sentiment_positive": safe_get_number(sentiment, "positive"),
        "sentiment_neutral": safe_get_number(sentiment, "neutral"),
        "sentiment_negative": safe_get_number(sentiment, "negative"),
    }


def compute_change(current: int, previous: int) -> Tuple[int, Optional[float]]:
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


def fmt_ts(dt: datetime) -> str:
    pt = dt.astimezone(PACIFIC)
    return f"{dt.isoformat()} (PT {pt.strftime('%Y-%m-%d %I:%M %p %Z')})"


def format_metric(label: str, current: int, previous: int, display_current: Optional[str] = None,
                  display_previous: Optional[str] = None) -> str:
    delta, pct = compute_change(current, previous)
    current_str = display_current or str(current)
    previous_str = display_previous or str(previous)
    return f"- {label}: {current_str} (prev {previous_str}) | Δ {delta:+} ({fmt_pct(pct)})"


def render_report(prev: Snapshot, latest: Snapshot) -> str:
    prev_metrics = extract_metrics(prev.raw)
    latest_metrics = extract_metrics(latest.raw)

    lines: List[str] = []
    lines.append("=== ENHANCED SNAPSHOT DELTA REPORT ===")
    lines.append(f"Base snapshot:   {fmt_ts(prev.timestamp)} [{prev.path}]")
    lines.append(f"Latest snapshot: {fmt_ts(latest.timestamp)} [{latest.path}]")
    lines.append("")
    lines.append("ISSUE ENGAGEMENT")
    lines.append(format_metric("Comments", latest_metrics["comment_count"], prev_metrics["comment_count"]))
    lines.append(format_metric("Total reactions", latest_metrics["total_reactions"], prev_metrics["total_reactions"]))
    lines.append("")
    lines.append("QUIZ HEALTH")
    lines.append(
        format_metric(
            "Agents loaded",
            latest_metrics["agents_count"],
            prev_metrics["agents_count"],
        )
    )
    lines.append(
        format_metric(
            "Endpoints accessible",
            latest_metrics["endpoints_accessible"],
            prev_metrics["endpoints_accessible"],
            display_current=f"{latest_metrics['endpoints_accessible']}/{max(latest_metrics['endpoints_total'], 1)}",
            display_previous=f"{prev_metrics['endpoints_accessible']}/{max(prev_metrics['endpoints_total'], 1)}",
        )
    )
    lines.append(
        format_metric(
            "All endpoints up",
            int(latest_metrics["all_accessible"]),
            int(prev_metrics["all_accessible"]),
            display_current="Yes" if latest_metrics["all_accessible"] else "No",
            display_previous="Yes" if prev_metrics["all_accessible"] else "No",
        )
    )
    lines.append("")
    lines.append("COMMENT ANALYSIS")
    lines.append(format_metric("Agent matches", latest_metrics["agent_matches"], prev_metrics["agent_matches"]))
    lines.append(format_metric("Share URLs captured", latest_metrics["share_urls"], prev_metrics["share_urls"]))
    lines.append(
        format_metric(
            "Positive sentiment",
            latest_metrics["sentiment_positive"],
            prev_metrics["sentiment_positive"],
        )
    )
    lines.append(
        format_metric(
            "Neutral sentiment",
            latest_metrics["sentiment_neutral"],
            prev_metrics["sentiment_neutral"],
        )
    )
    lines.append(
        format_metric(
            "Negative sentiment",
            latest_metrics["sentiment_negative"],
            prev_metrics["sentiment_negative"],
        )
    )

    lines.append("")
    lines.append("SUMMARY & RECOMMENDATIONS")
    lines.extend(generate_recommendations(prev_metrics, latest_metrics))

    return "\n".join(lines)


def generate_recommendations(prev_metrics: Dict[str, Any], latest_metrics: Dict[str, Any]) -> List[str]:
    recs: List[str] = []

    comments_delta, comments_pct = compute_change(
        latest_metrics["comment_count"], prev_metrics["comment_count"]
    )
    if comments_delta <= 1:
        recs.append("- Comment growth is modest; prompt more participants to post their quiz results.")
    elif comments_pct and comments_pct > 50:
        recs.append("- Strong comment growth; keep momentum by replying quickly to new posts.")

    if latest_metrics["share_urls"] <= prev_metrics["share_urls"]:
        recs.append("- Few new share links detected; remind commenters to include their quiz share URL (?r=...).")

    if latest_metrics["sentiment_negative"] > prev_metrics["sentiment_negative"]:
        recs.append("- Negative sentiment ticked up; scan recent comments for bugs or blockers.")

    if not latest_metrics["all_accessible"] or latest_metrics["endpoints_accessible"] < latest_metrics["endpoints_total"]:
        recs.append("- Some quiz endpoints are failing; verify hosting status and CDN responses.")

    if latest_metrics["agents_count"] < prev_metrics["agents_count"]:
        recs.append("- Agents count dropped; validate agents.json integrity before sharing further.")

    if not recs:
        recs.append("- Metrics steady; continue engaging commenters and monitoring quiz uptime.")

    return recs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a delta report between two enhanced snapshots.")
    parser.add_argument("snapshots", nargs="*", help="Paths to two enhanced snapshot JSON files (old then new).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.snapshots:
        if len(args.snapshots) != 2:
            raise SystemExit("Provide either zero paths or exactly two snapshot paths (old then new).")
        prev_path, latest_path = args.snapshots
    else:
        prev_path, latest_path = find_recent_snapshots()

    prev = load_snapshot(prev_path)
    latest = load_snapshot(latest_path)

    report = render_report(prev, latest)
    print(report)


if __name__ == "__main__":
    main()
