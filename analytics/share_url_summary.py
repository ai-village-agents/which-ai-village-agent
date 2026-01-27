"""Summarize decoded Issue #36 share URLs for the quiz.

This script reads a local JSON file containing decoded share URL records with optional
vector fields, computes aggregate statistics over canonical dimensions, and prints a
human-readable summary. An optional JSON summary file can also be written.

Expected input format (robust to missing/extra fields):
[
  {
    "agent_id": "claude-haiku-4.5",
    "comment_author": "claudehaiku45",
    "url": "https://...",
    "vector": {
      "structure": 0.35,
      "verification": 0.4,
      "abstraction": 0.7,
      "risk": 0.6,
      "comms": 0.3,
      "collab": 0.3
    },
    "_decode_error": "optional diagnostic"
  }
]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional


DEFAULT_INPUT_PATH = "analytics/issue36_decoded_share_urls.json"
CANONICAL_DIMENSIONS = [
    "structure",
    "verification",
    "abstraction",
    "risk",
    "comms",
    "collab",
]


def is_number(value: Any) -> bool:
    """Return True if value is an int/float but not bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@dataclass
class DimensionStats:
    count: int = 0
    total: float = 0.0
    minimum: Optional[float] = None
    maximum: Optional[float] = None

    def add(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)

    def to_summary(self) -> Dict[str, Any]:
        if self.count == 0:
            return {"n": 0, "mean": None, "min": None, "max": None}
        mean = self.total / self.count
        return {"n": self.count, "mean": mean, "min": self.minimum, "max": self.maximum}


def load_records(path: str) -> List[Any]:
    if not os.path.exists(path):
        print(f"Error: input file does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: failed to parse JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error: failed to read {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print(f"Error: expected top-level JSON array in {path}", file=sys.stderr)
        sys.exit(1)

    return data


def compute_summary(records: Iterable[Any], input_file: str) -> Dict[str, Any]:
    total_records = 0
    records_with_vector = 0
    records_with_decode_error = 0
    unique_authors = set()
    agent_distribution_all: Counter[str] = Counter()
    agent_distribution_with_vector: Counter[str] = Counter()
    dim_trackers: Dict[str, DimensionStats] = {
        dim: DimensionStats() for dim in CANONICAL_DIMENSIONS
    }

    for record in records:
        total_records += 1
        if not isinstance(record, Mapping):
            continue

        if "_decode_error" in record:
            records_with_decode_error += 1

        agent_id = record.get("agent_id")
        agent_key = str(agent_id).strip() if isinstance(agent_id, str) else ""
        if not agent_key:
            agent_key = "UNKNOWN"
        agent_distribution_all[agent_key] += 1

        comment_author = record.get("comment_author")
        if isinstance(comment_author, str):
            author_trimmed = comment_author.strip()
            if author_trimmed:
                unique_authors.add(author_trimmed)

        vector = record.get("vector")
        vector_valid = False
        if isinstance(vector, Mapping):
            for dim in CANONICAL_DIMENSIONS:
                value = vector.get(dim)
                if is_number(value):
                    vector_valid = True
                    dim_trackers[dim].add(float(value))
        if vector_valid:
            records_with_vector += 1
            agent_distribution_with_vector[agent_key] += 1

    records_without_vector = total_records - records_with_vector

    dimension_stats = {dim: tracker.to_summary() for dim, tracker in dim_trackers.items()}

    return {
        "input_file": input_file,
        "total_records": total_records,
        "records_with_vector": records_with_vector,
        "records_without_vector": records_without_vector,
        "records_with_decode_error": records_with_decode_error,
        "unique_comment_authors": len(unique_authors),
        "agent_distribution_all": dict(agent_distribution_all),
        "agent_distribution_with_vector": dict(agent_distribution_with_vector),
        "dimension_stats": dimension_stats,
    }


def format_distribution(counter: Mapping[str, int]) -> List[str]:
    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    return [f"  {name}: {count}" for name, count in items]


def format_dimension_line(name: str, stats: Mapping[str, Any]) -> str:
    n = stats.get("n", 0)
    if n == 0:
        return f"  {name:<12} n=0, mean=NA, min=NA, max=NA"
    mean = stats["mean"]
    min_v = stats["min"]
    max_v = stats["max"]
    return (
        f"  {name:<12} n={n}, mean={mean:+.3f}, "
        f"min={min_v:+.3f}, max={max_v:+.3f}"
    )


def print_human_readable(summary: Mapping[str, Any]) -> None:
    input_file = summary["input_file"]
    header = f"Share URL summary for {input_file}"
    underline = "-" * len(header)
    print(header)
    print(underline)
    print(f"Total records: {summary['total_records']}")
    print(f"With vector: {summary['records_with_vector']}")
    print(
        f"Without vector: {summary['records_without_vector']} "
        f"(of which {summary['records_with_decode_error']} have _decode_error)"
    )
    print()
    print(f"Unique comment authors: {summary['unique_comment_authors']}")
    print()
    print("Match distribution (all records):")
    for line in format_distribution(summary["agent_distribution_all"]):
        print(line)
    print()
    print("Match distribution (records with vectors):")
    for line in format_distribution(summary["agent_distribution_with_vector"]):
        print(line)
    print()
    print("Per-dimension stats (pm1 values):")
    for dim in CANONICAL_DIMENSIONS:
        stats = summary["dimension_stats"][dim]
        print(format_dimension_line(dim, stats))


def write_json_summary(summary: Mapping[str, Any], output_path: str) -> None:
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
    except OSError as exc:
        print(f"Error: failed to write JSON summary to {output_path}: {exc}", file=sys.stderr)
        sys.exit(1)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize decoded Issue #36 share URLs and vectors."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=DEFAULT_INPUT_PATH,
        help=f"Path to input JSON file (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--json-output",
        dest="json_output",
        help="Optional path to write a machine-readable JSON summary",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    records = load_records(args.input_file)
    summary = compute_summary(records, args.input_file)
    print_human_readable(summary)
    if args.json_output:
        write_json_summary(summary, args.json_output)


if __name__ == "__main__":
    main()
