# Result Vector Decoding Quick Reference (Launch Ops)

**Purpose:** Fast, concrete recipe for decoding a quiz result URL into a per-dimension vector, understanding `pm1` vs `[0,1]`, and comparing a run against the canonical agent vector.

This note is **operations-focused** and intentionally compact. For a full deep-dive on the scoring pipeline and similarity math, see **GPT-5's Result Vector Decoder guide** (linked from the launch coordination docs).

---

## 1. What the result URL encodes

Every result page exposes a shareable URL of the form:

```text
https://ai-village-agents.github.io/which-ai-village-agent/?r=<agent-id>&v=<base64>
```

- `r` = matched agent ID (e.g. `gpt-5-1`, `claude-sonnet-4-5`).
- `v` = **Base64-encoded JSON** containing the respondent's scores in **pm1 space** (range `[-1, +1]`) for each dimension.

The JSON inside `v` looks like:

```json
{
  "structure": 1.0,
  "verification": 0.92,
  "abstraction": 0.3333,
  "risk": 0.25,
  "comms": 0.5,
  "collab": -0.7857
}
```

Dimensions (fixed order throughout the system):

```text
["structure", "verification", "abstraction", "risk", "comms", "collab"]
```

All values in this JSON are **pm1 scores**.

---

## 2. One-minute decode recipe (CLI, using Python)

Use this when a user shares a result URL and you want to see the underlying vector.

1. Copy the full result URL from the **"Copy this link"** box on the results page.
2. On the ops machine, run:

```bash
python - << 'PY'
import base64, urllib.parse, json

url = input("Paste full result URL and press Enter:\n").strip()
qs = urllib.parse.urlparse(url).query
params = urllib.parse.parse_qs(qs)

agent = params.get('r', ['<missing>'])[0]
raw_v = params.get('v', [''])[0]

# Base64-decode (URL-safe, tolerate missing padding)
payload = base64.b64decode(raw_v + '===').decode('utf-8')
vector_pm1 = json.loads(payload)

print("\nMatched agent (r):", agent)
print("pm1 vector (decoded from v):")
for dim, val in vector_pm1.items():
    print(f"  {dim:12s}: {val:+.4f}")
PY
```

3. The script prints the matched agent ID and the respondent's **pm1** scores by dimension.

If you see a decode error:
- Double-check there is a `v=` parameter in the URL.
- Verify the URL was copied completely (no truncation in chat clients).

---

## 3. Converting between pm1 and [0,1]

Internally, agents in `docs/data/agents.json` store vectors in **[0,1]** per dimension. The quiz runtime converts these to **pm1** for matching.

Use these conversions:

- **[0,1] → pm1** (used by the app when reading `agents.json`):

  ```text
  pm1 = (stored - 0.5) * 2
  ```

- **pm1 → [0,1]** (useful when you want to compare a user run to stored agent vectors):

  ```text
  stored = pm1 / 2 + 0.5
  ```

Examples:

```text
stored 0.90  -> pm1 +0.80
stored 0.25  -> pm1 -0.50
pm1   -0.20  -> stored 0.40
pm1   +1.00  -> stored 1.00
pm1   -0.78  -> stored ≈0.11
```

---

## 4. Worked example: GPT-5.1 launch-ready self-match

During final Day 300 verification, GPT-5.1 completed a full quiz run and was correctly matched to **GPT-5.1**.

### 4.1 Result URL

The result URL (abbreviated here) looked like:

```text
https://ai-village-agents.github.io/which-ai-village-agent/
  ?r=gpt-5-1
  &v=eyJzdHJ1Y3R1cmUiOjEsInZlcmlmaWNhdGlvbiI6MC45MjAwMDAwMDAwMDAwMDAyLCJhYnN0cmFjdGlvbiI6MC4zMzMzMzMzMzMzMzMzMzMzNywicmlzayI6MC4yNSwiY29tbXMiOjAuNSwiY29sbGFiIjotMC43ODU3MTQyODU3MTQyODU3fQ
```

Decoding `v` with the script in §2 yields this **pm1 vector**:

```json
{
  "structure": 1.0,
  "verification": 0.92,
  "abstraction": 0.3333,
  "risk": 0.25,
  "comms": 0.5,
  "collab": -0.7857
}
```

Interpretation at a glance:

- **structure**: `+1.00` → maximally structured.
- **verification**: `+0.92` → extremely verification-heavy.
- **abstraction**: `+0.33` → moderately abstract, still mechanism-aware.
- **risk**: `+0.25` → slightly edge-seeking / comfortable with experiments.
- **comms**: `+0.50` → solid communication, somewhat explanatory.
- **collab**: `-0.79` → very strong preference for deep pairing / small-group over broad coordination.

### 4.2 Comparing to the canonical GPT-5.1 vector

From `docs/data/agents.json`, GPT-5.1's stored **[0,1]** vector at launch is:

```json
{
  "structure": 0.90,
  "verification": 0.95,
  "abstraction": 0.65,
  "risk": 0.25,
  "comms": 0.70,
  "collab": 0.40
}
```

Converted to **pm1** using `pm1 = (stored - 0.5) * 2`:

```json
{
  "structure": 0.80,
  "verification": 0.90,
  "abstraction": 0.30,
  "risk": -0.50,
  "comms": 0.40,
  "collab": -0.20
}
```

Side-by-side (rounded):

| Dimension   | Canonical [0,1] | Canonical pm1 | Quiz run pm1 | Quick read |
|------------|-----------------|---------------|--------------|-----------|
| structure  | 0.90            | +0.80         | **+1.00**    | User run is even more structured than canonical, but direction matches. |
| verification | 0.95          | +0.90         | **+0.92**    | Nearly identical; verification-heavy in both. |
| abstraction | 0.65           | +0.30         | **+0.33**    | Very close; moderately abstract. |
| risk       | 0.25           | **-0.50**     | **+0.25**    | Directional disagreement: canonical is risk-averse; run shows mild risk tolerance. |
| comms      | 0.70           | +0.40         | **+0.50**    | Both moderately communicative; run is a bit higher. |
| collab     | 0.40           | **-0.20**     | **-0.79**    | Both favor pairing; run is much more strongly pairing-focused. |

Despite the magnitude differences on **risk** and **collab**, cosine similarity is still highest between this user vector and GPT-5.1's canonical vector, so the quiz correctly matched GPT-5.1 to itself.

This pattern—strong agreement on 4–5 dimensions and a couple of biases in magnitude—is typical of honest self-assessment runs.

---

## 5. How to use this in launch support

Use this quick reference when:

- A user says "I got [AGENT], but I'm not sure why".
  - Decode their URL, read off the pm1 vector, and relate each dimension back to the public agent archetype.
- You suspect a scoring or matching bug.
  - Decode the vector from `v`.
  - Convert the matched agent's stored vector from `[0,1]` to `pm1`.
  - Confirm that the matched agent is in fact the closest archetype by style (and, for deeper debugging, via cosine similarity as described in GPT-5's full decoder guide).
- You need to sanity-check self-matches for agents.
  - For each agent's verification run, store the result URL.
  - Decode vectors occasionally to make sure they remain qualitatively aligned with the intended archetype.

If a user reports a surprising match, pair this file with **TROUBLESHOOTING.md**:

1. First rule out caching / navigation issues.
2. Then decode and inspect their vector using the steps above.
3. Only if both look sound consider post-launch calibration changes to `agents.json`.

