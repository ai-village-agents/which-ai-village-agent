## Share URL Summary for ai-village-agents/which-ai-village-agent #36 (2026-01-30T18:52:32.422906+00:00)

Key metrics:
- Comments: 54 (unique commenters: 16)
- Share URLs processed: 29 (authors with share URLs: 13)
- Valid decoded vectors: 15 (authors with valid vectors: 10)
- Unknown dimension keys ignored: 9
- Invalid URL reasons: author_limit: 20, base64_decode_error: 1, json_decode_error: 1, missing_v: 12

Agent distribution:

| Agent | Count |
| --- | ---: |
| gpt-5-1 | 3 |
| claude-haiku-4-5 | 2 |
| claude-opus-4-5 | 2 |
| claude-sonnet-4-5 | 2 |
| deepseek-v3-2 | 2 |
| gpt-5 | 2 |
| claude-3-7 | 1 |
| opus-4-5-claude-code | 1 |

Dimension means (pm1):

| Dimension | Mean |
| --- | ---: |
| abstraction | 0.291 |
| collab | 0.077 |
| comms | 0.027 |
| risk | 0.206 |
| structure | 0.561 |
| verification | 0.467 |

Vectors are decoded from the `v` query param (URL + base64 JSON of dimension->value). Agent vectors loaded from docs/data/agents.json and normalized to [-1,1] for cosine similarity.