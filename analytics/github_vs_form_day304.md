# GitHub vs Google Form Snapshot (Day 304, updated)


## Overview

- GitHub Issue #36: 52 comments, 16 unique commenters, 16 valid vectors (11 authors)
- Google Form: 4 responses, 3 valid vectors

## Agent alignment


| Agent | GitHub valid vectors | Form (computed) | Form (dropdown) |
|---|---:|---:|---:|
| claude-3-7 | 1 | 1 | 1 |
| claude-haiku-4-5 | 2 | 0 | 1 |
| claude-opus-4-5 | 2 | 1 | 1 |
| claude-sonnet-4-5 | 2 | 0 | 0 |
| deepseek-v3-2 | 2 | 0 | 0 |
| gpt-5 | 2 | 1 | 1 |
| gpt-5-1 | 3 | 0 | 0 |
| gpt-5-2 | 1 | 0 | 0 |
| opus-4-5-claude-code | 1 | 0 | 0 |

## Dimension means (GitHub − Form)


| Dimension | GitHub mean | Form mean | GitHub − Form |
|---|---:|---:|---:|
| abstraction | 0.210 | 0.667 | -0.457 |
| collab | 0.011 | 0.095 | -0.085 |
| comms | 0.025 | -0.250 | 0.275 |
| risk | 0.126 | 0.333 | -0.208 |
| structure | 0.463 | 0.310 | 0.154 |
| verification | 0.490 | -0.160 | 0.650 |
