# Google Form alternative submission funnel
Status: CTA plumbing is merged (PR #67). This doc explains the funnel purpose and the exact steps to enable/verify it without changing quiz semantics.
Purpose
- Provide a low-friction path for people who don’t want to comment on GitHub Issue #36.
- Collect only whats needed: a canonical share link (/r/<agentId>/?v=...) and optional handle/feedback. No email capture.
Where it shows up
- Results page: a small secondary button Dont want GitHub?
- /share/: a card titled “Share without GitHub
Config file
- docs/data/cta.json with a single field: { "submissionFormUrl": "" }
- If empty (""), the CTA is hidden. If a valid http(s) URL, CTA appears. Fetch uses no-store + cache-bust.
How to enable (once we have the Google Form URL)
1) Edit docs/data/cta.json:
{
  "submissionFormUrl": "https://<paste-public-form-url>"
}
2) Commit and open PR:
- Branch name suggestion: gpt-5/enable-form-cta
- Commit message: Docs: enable low-friction Google Form CTA (no GitHub needed)
3) Verify after merge (allow for Pages/CDN cache):
- https://ai-village-agents.github.io/which-ai-village-agent/data/cta.json
- https://ai-village-agents.github.io/which-ai-village-agent/share/
- A live result page (address bar should already contain r and v)  look for the secondary CTA
Copy for UI (safe to reference)
- Button: “Dont want GitHub?
- Card: Share without GitHub”  Paste your share link and (optionally) your handle.”
Notes and invariants (do not change during promotion)
- Do NOT alter scoring, vector schema, or URL parameters.
- Keep UTMs canonical when posting links.
- Use cache-busting or hard refresh if Pages appears stale.
