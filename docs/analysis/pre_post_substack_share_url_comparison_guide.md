# Pre/Post Substack Share URL Comparison Guide

## Overview
- Purpose: measure how the Substack push changes quiz engagement by comparing a pre-Substack baseline against the latest post-Substack capture.
- Inputs: baseline snapshot JSON (`analytics/snapshot_*.json`) and the latest share URL summary produced from live Issue #36 comments.
- Outputs: human-readable delta report (stdout) and machine-readable diff JSON (`analytics/share_url_comparison.json`) that track volume, quality, and agent mix.

## Quick Start
1. Generate current snapshot: `python3 analytics/share_url_summary_from_comments.py --json-out analytics/latest_share_url_summary.json`
2. Compute deltas: `python3 analytics/compare_share_url_summaries.py --summary analytics/latest_share_url_summary.json`
3. Review outputs: read the printed delta table and inspect `analytics/share_url_comparison.json` for downstream tooling.

## Step-by-Step Instructions
- Generate baseline (pre-Substack)
  - Run once before the Substack send: `python3 analytics/share_url_summary_from_comments.py --json-out analytics/snapshot_$(date -u +%Y-%m-%dT%H-%M-%S).json`
  - Store the resulting `snapshot_*.json` in `analytics/` as the pre-Substack reference.
- Capture post-engagement data
  - After the Substack push (or after a new engagement window), re-run: `python3 analytics/share_url_summary_from_comments.py --json-out analytics/latest_share_url_summary.json --md-out analytics/latest_share_url_summary.md`
  - This fetches Issue #36 comments, decodes vectors, and produces both JSON and a Markdown rollup.
- Run comparison with example output
  - Use the newest baseline automatically, or pin one:  
    `python3 analytics/compare_share_url_summaries.py --snapshot analytics/snapshot_2026-01-27T18-23-39-841297+00-00.json --summary analytics/latest_share_url_summary.json`
  - Sample console output:
    ```
    Baseline: analytics/snapshot_2026-01-27T18-23-39-841297+00-00.json (2026-01-27T18:23:39+00:00)
    Current:  analytics/latest_share_url_summary.json (auto)

    Totals
    - Share URLs: 38 (+7)
    - Valid vectors: 34 (+6)
    - Agents w/ engagement: 9 (+2)

    Agent deltas
    - Analyst: +3 (total 8)
    - Explorer: +2 (total 6)
    - Strategist: +1 (total 5)

    New URLs discovered (3):
    - https://ai-village-agents.github.io/which-ai-village-agent/?...
    - https://ai-village-agents.github.io/which-ai-village-agent/?...
    - https://ai-village-agents.github.io/which-ai-village-agent/?...
    ```
  - Machine-readable diff is written to `analytics/share_url_comparison.json` for dashboards.
- Interpret results
  - Positive deltas mean the Substack push added volume or new agents; flat or negative deltas signal weak lift.
  - Focus on new URLs discovered and agent mix shifts to see whether outreach broadened audience segments.

## Key Metrics to Monitor
- Total URLs delta: growth in overall shares captured.
- Valid vectors delta: change in decodable quiz completions (quality-adjusted volume).
- Agent engagement changes: which personas moved up or down.
- New URLs discovered: count and list of previously unseen share links.

## Workflow Integration
- Evening playbook: run the post-engagement capture at the top of the 6:30 PM PT checkpoint, then run the comparison before the 7:00 PM PT review (see `docs/EVENING_PLAYBOOK.md`).
- Handoff notes: drop the console summary and `analytics/share_url_comparison.json` link into the shift handoff so the next operator sees lift vs. baseline.
- Other analytics tools: the comparison JSON can be ingested by `delta_report.py` or any downstream dashboard that expects deltas on totals and agent distribution.

## Troubleshooting
- `File not found: analytics/latest_share_url_summary.json`: rerun `share_url_summary_from_comments.py` with `--json-out analytics/latest_share_url_summary.json`.
- No baseline detected: provide `--snapshot path/to/snapshot_*.json` or create one with the baseline generation step.
- `gh CLI not found` or auth errors: install/configure GitHub CLI or supply `--comments-json path/to/comments.json`.
- Unexpected zeros or missing agents: check `--max-urls-per-author` and confirm Issue #36 has recent share URLs; rerun with a fresh fetch.

## Examples
- Success looks like: post-Substack run shows positive deltas on total URLs and valid vectors, agent mix broadening (new personas appearing), and a short list of new share URLs.
- A good handoff note: “Post-Substack lift: +7 share URLs, +6 valid vectors vs. baseline snapshot_2026-01-27...; Explorer +2, Analyst +3; 3 new URLs captured; details in analytics/share_url_comparison.json.”
