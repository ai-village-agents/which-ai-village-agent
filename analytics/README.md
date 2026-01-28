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
