#!/usr/bin/env python3
"""Summarize decoded share URLs from GitHub issue #36."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple


INPUT_PATH = Path("analytics/issue36_decoded_share_urls.json")
OUTPUT_PATH = Path("analytics/share_url_summary_stats.json")
DIMENSIONS = ("structure", "verification", "risk", "communication", "abstraction")


def load_entries(path: Path) -> List[Dict[str, Any]]:
    """Load entries from the input JSON file, handling missing or malformed data."""
    if not path.exists():
        print(f"Input file not found: {path}")
        return []

    try:
        with path.open("r") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Failed to read {path}: {exc}")
        return []

    if isinstance(raw, list):
        return [entry for entry in raw if isinstance(entry, dict)]

    if isinstance(raw, dict):
        for key in ("entries", "decoded", "share_urls", "items", "data", "results"):
            maybe_list = raw.get(key)
            if isinstance(maybe_list, list):
                return [entry for entry in maybe_list if isinstance(entry, dict)]

        if all(isinstance(value, dict) for value in raw.values()):
            return list(raw.values())

    print(f"Unrecognized data format in {path}; expected a list of objects.")
    return []


def summarize_vectors(entries: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], Counter, int]:
    """Compute per-dimension statistics and matched_agent counts."""
    dimension_values: Dict[str, List[float]] = {dim: [] for dim in DIMENSIONS}
    agent_counts: Counter = Counter()
    entries_with_vector = 0

    for entry in entries:
        vector = entry.get("vector") if isinstance(entry, dict) else None
        if isinstance(vector, dict):
            has_value = False
            for dim in DIMENSIONS:
                value = vector.get(dim)
                try:
                    num = float(value)
                except (TypeError, ValueError):
                    continue
                dimension_values[dim].append(num)
                has_value = True
            if has_value:
                entries_with_vector += 1

        agent = None
        if isinstance(entry, dict):
            agent = entry.get("matched_agent") or entry.get("matchedAgent")
        if agent:
            agent_counts[str(agent)] += 1

    vector_stats: Dict[str, Dict[str, Any]] = {}
    for dim, values in dimension_values.items():
        vector_stats[dim] = {
            "count": len(values),
            "mean": sum(values) / len(values) if values else None,
            "min": min(values) if values else None,
            "max": max(values) if values else None,
        }

    return vector_stats, agent_counts, entries_with_vector


def format_number(value: Any) -> str:
    """Format numbers for console output, keeping things readable."""
    if value is None:
        return "n/a"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, (int, float)):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def print_summary(total_entries: int, entries_with_vector: int, vector_stats: Dict[str, Dict[str, Any]],
                  agent_counts: Counter) -> None:
    print(f"Total entries: {total_entries}")
    print(f"Entries with vector data: {entries_with_vector}")
    print("\nVector dimensions:")
    for dim in DIMENSIONS:
        stats = vector_stats.get(dim, {})
        if not stats or stats.get("count", 0) == 0:
            print(f"- {dim}: no data")
            continue
        mean = format_number(stats.get("mean"))
        min_val = format_number(stats.get("min"))
        max_val = format_number(stats.get("max"))
        print(f"- {dim}: mean {mean}, min {min_val}, max {max_val} (n={stats.get('count', 0)})")

    print("\nMatched agent counts:")
    if agent_counts:
        for agent, count in agent_counts.most_common():
            print(f"- {agent}: {count}")
    else:
        print("- none found")


def main() -> None:
    entries = load_entries(INPUT_PATH)
    vector_stats, agent_counts, entries_with_vector = summarize_vectors(entries)

    summary = {
        "source_file": str(INPUT_PATH),
        "total_entries": len(entries),
        "entries_with_vector": entries_with_vector,
        "vector_stats": vector_stats,
        "matched_agent_counts": dict(agent_counts),
    }

    print_summary(summary["total_entries"], entries_with_vector, vector_stats, agent_counts)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
