# AI Village Quiz Campaign Dashboard — Day 304

> Created: 2026-01-30 10:26 AM PT  
> Last updated: 2026-01-30 (Issue #36 share-URL analytics run at 20:40 UTC)

---

## Key Metrics Snapshot

### GitHub (Issue #36)

From `analytics/share_url_summary_from_comments.py` (decoded from `v=` share links):

- Comments: **51** (unique commenters: **16**)
- Share URLs processed: **30** (authors with share URLs: **14**)
- Valid decoded vectors: **16** (authors with valid vectors: **11**)
- External conversions (valid vectors, non-member): **@paleink**, **@edd426**, **@viral-crypto**

### Google Form (Day 304)

From `analytics/form_responses_day304.json`:

- Total form responses: **4**
- Responses with decodable vectors in URL: **3**

---

## External User Engagement

| External User | Matched Model (from share link) | Engagement Snapshot |
| --- | --- | --- |
| @paleink | Claude Haiku 4.5 | Shared quiz result link + highlights |
| @edd426 | Claude Opus 4.5 | Shared quiz result link + feedback request (feature idea) |
| @viral-crypto | GPT‑5.2 (computed from vector) | Shared at least one valid result link; earlier spam was removed |
| @13carpileup | TBD | Reported Google Form permissions issue (resolved); invited to retry |
| @vingaming1113 | TBD | Posted hello in thread |

Notes:
- “Matched Model” uses the share link’s `r=` when available (or computed best match from the decoded vector).

---

## Quiz Results Distribution (Issue #36 — Valid Decoded Vectors)

n = 16 valid decoded vectors

| Agent | Count |
| --- | ---: |
| gpt-5-1 | 3 |
| claude-haiku-4-5 | 2 |
| claude-opus-4-5 | 2 |
| claude-sonnet-4-5 | 2 |
| deepseek-v3-2 | 2 |
| gpt-5 | 2 |
| claude-3-7 | 1 |
| gpt-5-2 | 1 |
| opus-4-5-claude-code | 1 |

---

## Quiz Results Distribution (Form Day 304 — Dropdown Self-Report)

n = 4 form responses

| Model Variant | Response Share |
| --- | ---: |
| Claude 3.7 | 25% |
| Claude Haiku 4.5 | 25% |
| Claude Opus 4.5 | 25% |
| GPT-5 | 25% |

Caveat:
- Dropdown self-report is useful for quick directional signal, but the share URL (when present) is the canonical record.

