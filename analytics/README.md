# Day 302 Revised Analytics Pipeline

## Overview
This directory contains scripts for tracking quiz engagement sourced from GitHub Issue #36. It focuses on extracting "share URL" data from the issue discussion and producing engagement summaries for PM1 monitoring.

## Core Pipeline
- **Component 1 (Fetcher) — `share_url_summary_from_comments.py`**: Upstream step that fetches comments from Issue #36, parses the embedded share URLs, decodes the vectors, and writes the results as a JSON list.
- **Component 2 (Summarizer) — `share_url_summary.py`**: Downstream step that reads the fetcher’s JSON output and calculates PM1 stats, including agent distributions and dimension breakdowns.

## Usage
Run the components in sequence from the repository root:

```bash
# 1. Fetch & Decode
python3 analytics/share_url_summary_from_comments.py > analytics/current_data.json

# 2. Summarize
python3 analytics/share_url_summary.py analytics/current_data.json
```

## Other Tools
- `capture_enhanced.py` — auxiliary monitoring/collection helper.
- `delta_report.py` — auxiliary tool for change tracking and reporting.


## Day 304: Post-spam Issue #36 diagnostics

To keep our campaign dashboard stable while still documenting the late spam/chatter on Issue #36, we treat **two different snapshots** separately:

- **Canonical snapshot (44 comments, pre-spam)** — `analytics/latest_share_url_summary.json` + `.md`
  - This is the authoritative basis for Day 304 metrics and `docs/campaign/dashboard.md`.
- **Full-thread diagnostic snapshot (including spam)** — added in this PR:
  - `analytics/share_url_summary_issue36_full.json` / `.md` — current full-thread snapshot (including the viral-crypto spam wave).
  - `analytics/share_url_summary_issue36_diff.json` — structured comparison vs `latest_share_url_summary.json`.

Key finding from the diagnostics:

- **No change** in `share_urls_processed`, `valid_vectors`, archetype distribution, or dimension means.
- Only raw volume fields (`comments`, `unique_commenters`) and `invalid_reasons.author_limit` increased.

As a result, **`latest_share_url_summary.*` remains the canonical Issue #36 snapshot**; the `*_issue36_full*` files are preserved here purely for historical and diagnostic reference.
