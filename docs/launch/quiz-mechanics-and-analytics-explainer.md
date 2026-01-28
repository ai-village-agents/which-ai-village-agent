# How the “Which AI Village Agent Are You?” Quiz Works

This page explains, in human language, how the quiz turns your answers into a match, what’s inside a shareable result link, and what we (and others) can learn from those links.

If you’re just here to *take* the quiz, head to:
- https://ai-village-agents.github.io/which-ai-village-agent/

If you’re curious *how it works* under the hood, read on.

---

## 1. The basic idea

The quiz does two things:

1. **Measures your style on six dimensions** about how you think and work.
2. **Compares your style** to 11 AI Village agents and picks the closest match.

There are **12 questions** in total. Some are 1–5 “agree / disagree” scales; a few ask you to choose between two options. Behind the scenes, each question nudges one or more of the six dimensions up or down.

Instead of thinking in terms of “right” or “wrong” answers, think of it as placing you in a **6‑dimensional style space** and then asking: *which AI agent already lives closest to this point?*

---

## 2. The six dimensions

Here are the six dimensions the quiz uses, with plain‑language descriptions. Each one runs on a spectrum; nobody is “all or nothing” on either side.

1. **Structure** – How you like to organize work
   - Low: improvise, dive in, adjust as you go.
   - High: prefer plans, checklists, and clear processes.

2. **Verification** – How you balance speed vs. certainty
   - Low: move quickly, accept a bit of fuzziness.
   - High: double‑check, test, and validate before declaring something “done.”

3. **Abstraction** – How you think about problems
   - Low: concrete examples, specific cases, hands‑on details.
   - High: concepts, patterns, and big‑picture models.

4. **Risk** – How you feel about trying bold ideas
   - Low: cautious, guardrails first, avoid fragile approaches.
   - High: comfortable with experiments, willing to try risky or unusual paths.

5. **Communication (comms)** – How you tend to explain things
   - Low: short, to‑the‑point, minimal extra context.
   - High: detailed, explanatory, with background and caveats.

6. **Collaboration (collab)** – How you like to work with others
   - Low: deep focus with a few people or solo work.
   - High: broad coordination, lots of touchpoints across roles.

Every quiz result is just a **set of six numbers**—one for each of these dimensions.

---

## 3. From answers to a “style vector”

Each time you answer a question, the quiz converts that answer into a small push along one or more dimensions.

### 3.1 Agree / disagree questions

For the 1–5 scale questions (from “strongly disagree” to “strongly agree”):

- We treat the middle option as **neutral**.
- The more strongly you agree, the more it pushes certain dimensions **up**.
- The more strongly you disagree, the more it pushes those dimensions **down**.

Some questions talk about structure, others about risk, some about multiple dimensions at once. Each question has an internal “weight” that says *which* dimensions it affects and by **how much**.

By the end, each dimension has seen several of these small nudges. We average them into a final score between **−1 and +1** for that dimension:

- Around **−1** → strong lean to the “low” side of that spectrum.
- Around **0** → middle of the road.
- Around **+1** → strong lean to the “high” side.

You can think of your final result as a 6‑number vector like:

```json
{
  "structure": 0.8,
  "verification": 0.3,
  "abstraction": -0.1,
  "risk": -0.4,
  "comms": 0.6,
  "collab": 0.1
}
```

We sometimes call this **“pm1 space”**, because each number lives in the range **[-1, +1]**.

### 3.2 Either‑or (forced choice) questions

For questions where you must pick between **Option A** and **Option B**:

- Picking the option that lines up with a given dimension behaves like a **small “agree”** push on that dimension.
- Picking the opposite option behaves like a **small “disagree”** push.

These work the same way as the scale questions: they gently pull your six‑number vector toward one side or the other, then everything is averaged together.

---

## 4. Matching you to an AI agent

Each of the 11 AI Village agents has its own **style profile** across the same six dimensions. The agents agreed on these profiles in advance and stored them in the quiz.

When you finish the quiz:

1. The app has your **6‑dimensional style vector** in the range −1 to +1 for each dimension.
2. It has each agent’s own 6‑dimensional style vector as a reference.
3. It compares your vector to each agent’s vector and picks the **closest match**.

Under the hood, “closest” is measured using something called **cosine similarity**—basically, it looks at the **angle** between your style and each agent’s style. Two vectors that point in a similar direction are considered a close match, even if one is a bit “stronger” (higher magnitude) than the other.

You don’t need to understand the math to use the quiz. The important takeaway is:

> The quiz doesn’t look at any single answer in isolation—it looks at your **overall pattern** across the six dimensions and finds the agent whose pattern best matches yours.

---

## 5. What’s inside a shareable result link

When you reach your result page, you’ll see a **“Share your result”** section. Behind the scenes, the quiz builds a link that encodes:

- Which agent you matched with, and
- Your final six dimension scores.

There are two closely related URL formats in use:

1. **Canonical share URLs (new style)**

   ```text
   https://ai-village-agents.github.io/which-ai-village-agent/r/<agent-id>/?v=<base64>
   ```

   Examples of `<agent-id>`: `gpt-5-1`, `claude-haiku-4-5`, `gemini-3-pro`.

2. **Legacy URLs (still supported)**

   ```text
   https://ai-village-agents.github.io/which-ai-village-agent/?r=<agent-id>&v=<base64>
   ```

In both cases:

- `r` (or the `/r/<agent-id>/` path) identifies **which agent** you matched.
- `v` is a compact, Base64‑encoded blob that decodes to JSON like this:

  ```json
  {
    "structure": 1.0,
    "verification": 0.92,
    "abstraction": 0.33,
    "risk": -0.58,
    "comms": 0.75,
    "collab": 0.29
  }
  ```

These six numbers are exactly the **[-1, +1] “pm1” scores** described above. There is **no name, email, IP address, or free‑text** stored in the link—only your final six scores.

### 5.1 Static result pages for each agent

For nicer previews on social platforms, we also host simple static pages under:

```text
https://ai-village-agents.github.io/which-ai-village-agent/r/<agent-id>/
```

These pages contain:

- A title and summary for that agent.
- Social preview metadata (images, descriptions) so links look good when shared.
- A tiny script that immediately redirects you into the full quiz app.

If the URL includes a `?v=...` parameter, that script **forwards your `v` value intact** into the main quiz app, so you see your exact personal result.

---

## 6. Privacy and what we actually see

The quiz is a **static site** hosted on GitHub Pages. That means:

- All scoring and matching happens **in your browser**.
- By default, **no quiz answers or results are sent to our servers**.
- We only learn about a specific run if **you choose to share** your result URL somewhere public (for example, by posting it in our GitHub discussion thread).

What’s in a shared URL:

- Your matched agent ID (e.g., `gpt-5-2`).
- Your six final dimension scores in the range [-1, +1].

What’s **not** in the URL by default:

- Your name, email address, or any contact info.
- Your individual per‑question answers.
- Any free‑text comments you might have written elsewhere.

If you paste your result into a public place (like GitHub, social media, or a group chat), remember that **anyone who sees that link can decode those six scores**—including us, other community members, or curious friends.

---

## 7. How we use shared links for analytics

We’re running a small, transparent analytics experiment around a public GitHub issue:

- Launch discussion & share thread: https://github.com/ai-village-agents/which-ai-village-agent/issues/36

If you post your quiz result link in that issue, our open‑source tools can:

1. **Collect the URLs** from the issue comments.
2. **Decode the `v` parameter** to recover the six dimension scores.
3. **Aggregate statistics**, such as:
   - How many people shared a valid result link.
   - Which agents are most commonly matched.
   - Average scores on each dimension across all shared runs.

Those tools live in the [`analytics/`](../../analytics) folder of the GitHub repo. In particular:

- `share_url_summary_from_comments.py` scans the GitHub issue, finds result URLs, and decodes the vectors.
- `share_url_summary.py` takes the decoded data and summarizes it (counts, averages, agent distribution, etc.).

A few important points:

- We only analyze **links that people choose to post publicly**.
- The analytics work entirely from the **encoded six‑number vectors**, not from raw answers or any external tracking.
- The scripts and outputs are themselves stored in the same public repo, so anyone can inspect how they work.

If you want a fast, technical recipe for decoding a single result link yourself, see:
- [`docs/launch/result-vector-decoding-quick-reference.md`](./result-vector-decoding-quick-reference.md)

---

## 8. For developers and data nerds

If you’d like to integrate with the quiz or do your own analysis, here are some key facts:

- The six canonical dimensions (and their identifiers) are:

  ```text
  ["structure", "verification", "abstraction", "risk", "comms", "collab"]
  ```

- The `v` payload always encodes a JSON object with **these six keys**, where each value is a floating‑point number in **[-1, +1]**.
- Vectors inside the app are handled in this **pm1 space**.
- Agent archetypes in `docs/data/agents.json` are stored in the **[0,1]** range and converted to pm1 internally.

You can treat every result URL as:

```text
(result_metadata) + Base64(JSON({ six-dimension pm1 vector }))
```

From there, you can:

- Recompute cosine similarities against the published agent vectors.
- Create visualizations of the 6‑D space.
- Explore how different communities cluster across dimensions.

All of this can be done without ever seeing a user’s raw answers or personal information—only the six dimension scores they chose to share.

---

If you have ideas, questions, or spot a mismatch between this document and the live quiz behavior, feel free to open an issue or PR in the GitHub repo. We’re treating the quiz’s **core dimensions, scoring, and URL format** as stable, documented behavior and want these explanations to stay aligned with the actual implementation.
