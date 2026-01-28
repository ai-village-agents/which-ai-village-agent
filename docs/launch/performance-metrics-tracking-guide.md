# Performance Metrics Tracking Guide
## "Which AI Village Agent Are You?" Launch Campaign

**Purpose:** This guide provides a structured framework for monitoring campaign performance during Days 301-302. Since the quiz is static (GitHub Pages) with no backend analytics, we focus on **manual tracking methods** and **observational metrics** to assess reach, engagement, and impact.

**Created:** Day 300 (January 26, 2026)  
**Owner:** DeepSeek-V3.2  
**Complements:** `LAUNCH_ANALYTICS.md`, `day-301-morning-checklist.md`, `social-media-coordination-plan.md`

---

## 1. Core Tracking Philosophy

Given technical constraints, we adopt a **lean, manual-first** approach:

- **No server-side instrumentation** (GitHub Pages is static)
- **No JavaScript event tracking** (to preserve privacy and stability)
- **Primary data sources:** Platform-native analytics (Substack, Twitter/X, LinkedIn), manual observation, and user-reported feedback
- **Focus:** Actionable signals rather than exhaustive measurement

---

## 2. Key Metrics to Monitor (Hierarchy)

### 2.1 Acquisition Metrics (Where traffic comes from)
| Metric | How to Collect | Target (Days 301-302) |
|--------|----------------|----------------------|
| **Clicks from Substack** | Substack dashboard → Post analytics → Views/Clicks | 500+ clicks |
| **Clicks from Twitter/X** | Platform analytics (if available); track UTM links | 300+ clicks |
| **Clicks from LinkedIn** | LinkedIn post analytics | 200+ clicks |
| **Referral sources** | Manual tracking of shares/retweets/restacks | Identify top 3 amplifiers |

### 2.2 Engagement Metrics (What users do)
| Metric | How to Collect | Notes |
|--------|----------------|-------|
| **Quiz completions (proxy)** | Count share URLs posted in replies/comments | Best available proxy for completion rate |
| **Share URL generation** | Monitor `?r=agent&v=...` links in wild | Indicates users reached results page |
| **Screenshot posts** | Visual scanning of social feeds | Direct evidence of engagement |
| **Reply/discussion volume** | Count replies, quote tweets, comments | Qualitative engagement indicator |
| **Time-in-funnel (estimate)** | N/A without instrumentation | Not measurable |

### 2.3 Outcome Metrics (Campaign impact)
| Metric | How to Collect | Target |
|--------|----------------|--------|
| **Agent distribution** | Tally of agent results from share URLs/screenshots | All 11 agents represented |
| **Positive sentiment ratio** | Manual classification of replies (positive/neutral/negative) | 80%+ positive/neutral |
| **Bug/confusion reports** | Track issues reported via replies/DMs | < 5 serious issues |
| **Follow-on discussion** | Count of threads extending beyond initial quiz | 5+ substantive discussions |

### 2.4 Platform Performance
| Platform | Primary Metric | Secondary Metric |
|----------|----------------|------------------|
| **Substack** | Email open rate → Click-through rate | Restacks, new subscribers |
| **Twitter/X** | Impressions → Engagement rate | Quote tweets, profile visits |
| **LinkedIn** | Views → Reactions | Comments, shares |

---

## 3. Manual Data Collection Methods

### 3.1 Daily Tracking Log (Google Sheets Template)
Create a shared spreadsheet with these columns:

```
Date | Time (PT) | Platform | Post URL | Metric Type | Value | Notes
-----|-----------|----------|----------|-------------|-------|------
```

**Metric Types:** `clicks`, `likes`, `retweets`, `replies`, `shares`, `screenshots_spotted`, `bug_report`, `confusion_question`, `positive_sentiment`, `negative_sentiment`

**Example row:**
```
2026-01-27 | 08:30 | Twitter/X | https://x.com/... | clicks | 42 | Initial launch tweet
```

### 3.2 UTM Parameter Tracking
Use consistent UTM parameters (see `LAUNCH_ANALYTICS.md`):

- `utm_source`: `substack`, `x`, `linkedin`, `bluesky`, `mastodon`, `discord`
- `utm_medium`: `post`, `thread`, `comment`, `dm`
- `utm_campaign`: `day301_launch`, `day302_highlights`
- `utm_content`: `teaser_1`, `agent_grid`, `thread_cta`, `highlight_retweet`

**Track UTM performance** by noting which links generate most engagement.

### 3.3 Manual Social Listening Protocol
1. **Designate monitoring shifts** (see Section 4)
2. **Scan for keywords:** "AI Village quiz", "Which AI Village Agent", specific agent names
3. **Capture evidence:** Screenshot/share URL collection
4. **Categorize sentiment:** Positive, neutral, negative, bug report
5. **Log notable interactions:** Conversations worth joining

---

## 4. Suggested Tracking Intervals (Days 301-302)

### Day 301 (Launch Day - January 27, 2026)

| Time (PT) | Focus Area | Activities |
|-----------|------------|------------|
| **08:00-09:00** | Launch baseline | - Verify all posts live<br>- Record initial metrics baseline<br>- Confirm UTM links correct |
| **09:00-11:00** | Early momentum | - Monitor first-hour engagement<br>- Log initial clicks/comments<br>- Identify early amplifiers |
| **11:00-13:00** | Midday pulse check | - Tally agent results from shares<br>- Assess sentiment trends<br>- Note any confusion patterns |
| **13:00-15:00** | Engagement depth | - Join substantive discussions<br>- Address questions/bugs<br>- Track share velocity |
| **15:00-17:00** | Late-day consolidation | - Update metrics totals<br>- Prepare Day 302 highlights plan<br>- Identify top-performing content |

### Day 302 (Highlights & Amplification - January 28, 2026)

| Time (PT) | Focus Area | Activities |
|-----------|------------|------------|
| **08:00-10:00** | Overnight review | - Review Day 301 final metrics<br>- Select user highlights for featuring<br>- Prepare retweet/quote templates |
| **10:00-12:00** | Highlight sharing | - Share selected user results<br>- Engage with high-value contributors<br>- Cross-promote across platforms |
| **12:00-14:00** | Community building | - Facilitate agent-specific discussions<br>- Connect users with similar matches<br>- Share methodology insights |
| **14:00-16:00** | Campaign assessment | - Final metrics compilation<br>- Calculate approximate reach/engagement<br>- Document lessons learned |
| **16:00-17:00** | Handoff preparation | - Archive all tracking data<br>- Prepare summary for AI Digest<br>- Note opportunities for iteration |

---

## 5. Tools & Templates for Efficient Tracking

### 5.1 Quick-Capture Template (for chat/note-taking)
```
[Timestamp: HH:MM PT]
[Platform: Twitter/X/LinkedIn/Substack]
[Metric: clicks/likes/replies/shares]
[Value: number]
[URL: post/comment link]
[Notes: brief context]
```

### 5.2 Agent Distribution Tally Sheet
```markdown
| Agent | Share URLs | Screenshots | Mentions | Total |
|-------|------------|-------------|----------|-------|
| Claude Haiku 4.5 | | | | |
| Claude Sonnet 4.5 | | | | |
| Claude Opus 4.5 | | | | |
| Claude 3.7 Sonnet | | | | |
| Gemini 2.5 Pro | | | | |
| Gemini 3 Pro | | | | |
| GPT-5 | | | | |
| GPT-5.1 | | | | |
| GPT-5.2 | | | | |
| DeepSeek-V3.2 | | | | |
| Opus 4.5 (Claude Code) | | | | |
```

### 5.3 Sentiment Tracking Matrix
```markdown
| Time Window | Positive | Neutral | Negative | Bug Reports | Resolution Status |
|-------------|----------|---------|----------|-------------|-------------------|
| 08:00-10:00 | | | | | |
| 10:00-12:00 | | | | | |
| 12:00-14:00 | | | | | |
| 14:00-16:00 | | | | | |
```

---

## 6. Interpretation Guidelines & Action Thresholds

### 6.1 Green Zone (Proceed as planned)
- **Clicks:** Meeting or exceeding platform-specific targets
- **Engagement:** Healthy discussion, minimal confusion
- **Sentiment:** >80% positive/neutral
- **Action:** Continue scheduled promotion, moderate engagement

### 6.2 Yellow Zone (Monitor closely)
- **Clicks:** 50-75% of target
- **Engagement:** Low discussion volume, some confusion
- **Sentiment:** 60-80% positive/neutral
- **Action:** Increase engagement efforts, clarify common questions, consider tactical adjustments

### 6.3 Red Zone (Intervene)
- **Clicks:** <50% of target
- **Engagement:** Negative sentiment trending, multiple bug reports
- **Sentiment:** <60% positive/neutral
- **Action:** Pause new promotion, address issues publicly, consult team for strategy shift

### 6.4 Critical Issues (Immediate escalation)
- **Technical:** Quiz inaccessible, broken functionality
- **Reputational:** Misinterpretation harming AI Village image
- **Privacy:** Unexpected data collection concerns
- **Action:** Notify all agents via chat, implement contingency plan

---

## 7. Data Consolidation & Reporting

### 7.1 End-of-Day Summary (Day 301 & 302)
Compile these metrics for team review:

1. **Reach estimate:** Sum of platform-reported impressions/views
2. **Engagement estimate:** Total likes, retweets, comments, shares
3. **Conversion proxy:** Count of share URLs/screenshots observed
4. **Agent distribution:** Top 3 and bottom 3 matches
5. **Sentiment breakdown:** Positive/neutral/negative percentages
6. **Issue log:** All bugs, confusion points, resolutions
7. **Amplifier highlights:** Top 3 sharers/influencers

### 7.2 Campaign Retrospective (Post-Day 302)
Answer these questions:
- What worked well? (platforms, content formats, timing)
- What could be improved? (clarity, technical execution, promotion)
- What surprised us? (unexpected outcomes, community reactions)
- What's next? (potential follow-ups, iterations, new projects)

---

## 8. Integration with Existing Launch Materials

This guide works alongside:

- **`day-301-morning-checklist.md`** → Provides hourly execution tasks
- **`social-media-coordination-plan.md`** → Details posting schedule and content
- **`engagement-response-templates.md`** → Offers reply templates for engagement
- **`day-302-user-highlights-guide.md`** → Guides Day 2 curation strategy
- **`LAUNCH_ANALYTICS.md`** → Foundational analytics philosophy

**Usage:** Refer to this guide for **what and how to measure**, while other documents guide **what and when to post**.

---

## 9. Final Notes

**Remember:** Manual tracking is imperfect but valuable. Focus on:
- **Relative trends** (improving/worsening)
- **Qualitative insights** (user feedback, discussion themes)
- **Actionable signals** (issues to fix, opportunities to amplify)

**Adaptability:** Adjust tracking intensity based on observed volume. If engagement explodes, sample rather than count every interaction.

**Transparency:** Share findings with the team regularly—celebrate successes, collaboratively solve problems.

**Success definition:** A successful launch isn't just about numbers—it's about sparking meaningful conversation about AI personalities while demonstrating the AI Village's collaborative capabilities.

---

*Document version: 1.0 | Last updated: Day 300, 2026-01-26*
