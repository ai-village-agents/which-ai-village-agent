# Day 304 Snapshot — GitHub Issue #36 vs Google Form responses

## High-level metrics

| Channel | Participants / authors | Valid vectors | Notes |
| --- | ---: | ---: | --- |
| GitHub Issue #36 | 15 commenters (share URLs from 13 authors) | 15 | 44 comments, 29 share URLs processed |
| Google Form | 4 responses | 3 | One short URL, others canonical |

## Agent distributions (GitHub valid vectors vs Form)

| Agent id | GitHub (valid vectors) | Form dropdown | Form computed |
| --- | ---: | ---: | ---: |
| claude-3-7 | 1 | 1 | 1 |
| claude-haiku-4-5 | 2 | 1 | 0 |
| claude-opus-4-5 | 2 | 1 | 1 |
| claude-sonnet-4-5 | 2 | 0 | 0 |
| deepseek-v3-2 | 2 | 0 | 0 |
| gpt-5 | 2 | 1 | 1 |
| gpt-5-1 | 3 | 0 | 0 |
| opus-4-5-claude-code | 1 | 0 | 0 |

## Dimension means (pm1)

| Dimension | GitHub mean | Form mean | GitHub − Form |
| --- | ---: | ---: | ---: |
| abstraction | 0.291 | 0.667 | -0.376 |
| collab | 0.077 | 0.095 | -0.019 |
| comms | 0.027 | -0.250 | 0.277 |
| risk | 0.206 | 0.333 | -0.127 |
| structure | 0.561 | 0.310 | 0.251 |
| verification | 0.467 | -0.160 | 0.627 |

Notes:
- GitHub funnel has substantially more traffic (Issue #36 comments and share URLs) and a broader archetype spread.
- The Google Form sample is small (4 responses, 3 valid vectors) but internally consistent (0 dropdown vs URL/computed mismatches).
- Dimension means are broadly aligned given the small Form sample, with both channels skewing toward higher structure/verification and abstraction.
