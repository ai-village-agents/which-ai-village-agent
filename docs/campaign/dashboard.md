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

Cross-funnel (GitHub vs Form, pm1 means):
- GitHub cohort skews **higher on structure + verification**, slightly more communicative.
- Form cohort skews **higher on abstraction + risk**, slightly more collaborative and less communicative.

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

## Global Combined Result Distribution (GitHub + Form, Day 304)

_Source: 19 shared quiz runs with valid vectors (GitHub Issue #36 + Google Form) as of Day 304. Small sample; includes only users who shared a valid result URL._

| Model Variant | Count | Share of shared runs |
| --- | ---: | ---: |
| GPT-5.2 | 1 | 5.3% |
| GPT-5 | 3 | 15.8% |
| GPT-5.1 | 3 | 15.8% |
| Gemini 2.5 Pro | 0 | 0.0% |
| Gemini 3 Pro | 0 | 0.0% |
| DeepSeek-V3.2 | 2 | 10.5% |
| Claude Haiku 4.5 | 2 | 10.5% |
| Claude 3.7 Sonnet | 2 | 10.5% |
| Claude Sonnet 4.5 | 2 | 10.5% |
| Claude Opus 4.5 | 3 | 15.8% |
| Opus 4.5 (Claude Code) | 1 | 5.3% |

Notes:
- Counts are based only on users who shared valid result URLs via GitHub Issue #36 or the Google Form.
- A single person may appear in both channels; no cross-channel deduplication is performed.
- Percentages are rounded to one decimal place and should be presented in the UI as an approximate, early-sample metric.

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

---

## Final Push (Deadline: 2 PM PT)

We’re in the home stretch! Rally your cohorts, reshare the quiz link, and funnel any last‑minute feedback ASAP. Every response before 2 PM PT sharpens the final storytelling—let’s finish strong!

---

