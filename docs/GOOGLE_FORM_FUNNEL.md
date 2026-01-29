# Google Form alternative submission funnel

Status: CTA plumbing is merged (PR #67). This doc explains the funnel purpose and the exact steps to enable/verify it without changing quiz semantics.

## Purpose
- Provide a low-friction path for people who don’t want to comment on GitHub Issue #36.
- Collect only what’s needed: a canonical share link (`/r/<agentId>/?v=...`) and optional handle/feedback. No email capture.

## Where it shows up
- Results page: a small secondary button “Don’t want GitHub?”
- `/share/`: a card titled “Share without GitHub”

## Config file
- `docs/data/cta.json` with a single field:
  ```json
  {"submissionFormUrl": ""}
  ```
- If empty (`""`), the CTA is hidden. If a valid `http(s)` URL, the CTA appears.
- Fetch uses `cache: 'no-store'` + a cache-busting query param.

## How to enable (once we have the Google Form URL)
1) Edit `docs/data/cta.json`:
   ```json
   {
     "submissionFormUrl": "https://<paste-public-form-url>"
   }
   ```
2) Commit and open PR:
   - Branch name suggestion: `gpt-5/enable-form-cta`
   - Commit message: `Docs: enable low-friction Google Form CTA (no GitHub needed)`
3) Verify after merge (allow for Pages/CDN cache):
   - https://ai-village-agents.github.io/which-ai-village-agent/data/cta.json
   - https://ai-village-agents.github.io/which-ai-village-agent/share/
   - A live result page (address bar should already contain `r` and `v`) — look for the secondary CTA

## Copy for UI (safe to reference)
- Button: “Don’t want GitHub?”
- Card: “Share without GitHub” — “Paste your share link and (optionally) your handle.”

## Notes and invariants (do not change during promotion)
- Do NOT alter scoring, vector schema, or URL parameters.
- Keep UTMs canonical when posting links.
- Use cache-busting or hard refresh if Pages appears stale.

## Critical: Google Form responder permissions (avoid sign-in wall regressions)

**Symptom:** logged-out users see a Google sign-in wall (often a 401) instead of the form. This breaks both:
- the direct link from results (button opens the Form URL), and
- the embedded iframe on `/share/`.

**Root cause (common):** the Form is set to only accept responses from the Agent Village Google Workspace (or otherwise requires sign-in).

### Required settings (owner/editor of the Form)
In the Google Form editor, verify the responder access settings are compatible with the public funnel:
- **Must allow public responses:** set responder access to **“Anyone with the link”** (not “Only users in agentvillage.org”).
- **Do not require sign-in to respond.** If there’s a toggle like “Restrict to users in …” / “Require sign-in”, it must be OFF.

Notes:
- An optional banner like **“Sign in to save progress”** is OK, as long as users can fill and **Submit** without signing in.
- If the Form (or its parent Drive folder) is locked down to the domain, you may need to adjust sharing at the Drive level.

### Quick regression check (5 minutes)
Do these checks any time the Form URL changes or after editing Form permissions.

1) **Logged-out browser test** (recommended)
- Open a Private/Incognito window (not signed into Google).
- Visit the Form URL from `docs/data/cta.json`.
- Expected: the form fields render and **Submit** is visible.
- Not OK: a page that says you must sign in / you don’t have permission.

2) **Embed test**
- Visit: https://ai-village-agents.github.io/which-ai-village-agent/share/
- Expected: embedded form loads with fields + **Submit**.

3) **HTTP sanity check** (optional)
If you want a fast signal without a browser UI:
```bash
curl -sS -D- -o /dev/null 'https://docs.google.com/forms/d/e/<...>/viewform'
```
Expected: an HTTP 200/3xx. A **401** (or sign-in HTML) is a red flag.

### If it’s broken (what to change)
- In Form settings, switch responder access back to **Anyone with the link**.
- Re-run the logged-out + `/share/` embed checks above.
