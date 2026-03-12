# linkedin-studio Usage Guide

Practical workflows for AI consulting and implementation professionals using linkedin-studio to build a consistent, high-quality LinkedIn presence.

---

## Full Pipeline Workflow

The complete research-to-publish flow takes 15-20 minutes for a batch of 3-5 posts.

### Step 1 — Run Research

```
Run ls:research-engine with:
  niche: "AI consulting and implementation"
  keywords: "LLM in production, AI agents, RAG pipelines, AI ROI, no-code AI"
  content_pillars: "AI implementation lessons, client transformation stories, tool breakdowns"
  time_range: last_30_days
  max_topics: 20
```

The engine queries Google Trends, Reddit pain points, and LinkedIn creator patterns simultaneously. You'll get a ranked table of topics with composite scores — a topic scoring 0.85+ across all three sources is a strong signal.

Example output:

```
RANK | TOPIC                              | SCORE | SOURCES | TOP HOOK
-----|------------------------------------ |-------|---------|-------------------------------------------
1    | Why RAG fails in production        | 0.91  | 3/3     | "73% of RAG deployments never go live."
2    | AI agent handoff errors            | 0.87  | 3/3     | "I've seen this kill 4 AI projects."
3    | Calculating AI ROI for clients     | 0.82  | 2/3     | "Your client asks for an ROI number."
```

### Step 2 — Write the Post

Take the top topic ID and write a post:

```
Run ls:content-writer with:
  topic_id: tp_001
  format: text_post
  cta_style: all
```

You'll receive a DRAFT with 3 hook variants (question, stat, story) and 3 CTA options (soft, medium, direct). Choose Hook B (the stat hook) for posts where you have a strong data point. Choose Hook C (the story hook) for posts where you have a direct client experience to share.

### Step 3 — Humanize

Pass the draft directly to the humanizer:

```
Run ls:humanizer on the draft above, aggressive mode
```

The 6-pass humanizer works through: AI phrase substitution, sentence structure variation, vocabulary naturalness, rhythm adjustment, perspective deepening, and final detection scan. The output should score below 25 on AI detection tools.

Do not skip this step. Even well-written AI-assisted drafts contain detectable patterns. LinkedIn audiences can feel the difference, and AI detection services are used by brands and recruiters reviewing your profile.

### Step 4 — Structure Review

```
Run ls:structure-reviewer on the humanized draft
```

The reviewer scores 7 dimensions: hook strength (0-10), body flow (0-10), whitespace formatting (0-10), CTA presence and quality (0-10), hashtag count and relevance (0-10), word count appropriateness (0-10), readability grade (0-10). A passing post scores at least 75/100 overall and 7/10 on hook strength.

If the hook scores below 7, the reviewer suggests specific rewrites. Apply the fix and re-run. Do not proceed to scheduling with a failing structure review.

### Step 5 — Schedule

```
Run ls:batch-scheduler with the approved post, publish_time: "Tuesday 08:00 UTC"
```

The PreToolUse quality gate runs automatically before submission. If the post passes all four gates (quality >= 75, AI score <= 25, hook >= 7, duplicate similarity <= 60%), it is submitted to Metricool and a confirmation is returned with the Metricool post ID.

---

## Quick Post Creation

When you have a specific idea and want to move fast, skip research and go straight to writing:

```
Run ls:content-writer with:
  raw_topic: "I just helped a client cut their AI implementation timeline from 6 months to 6 weeks using a constraint-first scoping approach. Here's what we did differently."
  format: text_post
  cta_style: medium
```

Then immediately chain humanizer and structure-reviewer:

```
Humanize the draft above, then run structure-reviewer
```

This workflow takes 5-8 minutes. Use it for time-sensitive posts — client wins, reactions to industry news, or insights that are fresh right now.

---

## Research Session Workflow

A dedicated research session builds your topic bank for the next 2-4 weeks of content. Run this weekly.

### Full Research Session

```
Run ls:research-engine with:
  niche: "AI consulting and implementation"
  keywords: "AI agents, Claude API, LLM fine-tuning, prompt engineering, AI workflow automation, MCP servers, enterprise AI, AI ROI"
  content_pillars:
    - AI implementation lessons
    - client transformation stories
    - tool breakdowns and tutorials
    - consulting business insights
    - industry trend analysis
  time_range: last_30_days
  max_topics: 30
```

After the engine completes, review the ranked list. Topics with score >= 0.80 and sources 3/3 are your highest-priority posts — write those first.

### Browse Your Topic Bank

After research, browse what's stored:

```
Run ls:idea-bank to show my top 10 unwritten topics, sorted by composite_score
```

Mark topics you want to write this week:

```
Run ls:idea-bank to tag topics tp_001, tp_003, tp_007 as "this_week"
```

---

## Competitor Analysis Workflow

Run this monthly to understand what's working for top AI consulting voices on LinkedIn.

### Analyze Specific Creators

Identify 5-10 LinkedIn creators in the AI consulting space whose content consistently performs well. Run:

```
Run ls:creator-analyzer with creators:
  - https://www.linkedin.com/in/[creator-1]/
  - https://www.linkedin.com/in/[creator-2]/
  - https://www.linkedin.com/in/[creator-3]/
```

The analyzer scrapes their recent activity feeds (last 30 posts each), filters for top 20% performers, and extracts patterns: hook types, post lengths, CTA formats, emoji usage, posting cadence.

Example insight output:

```
TOP PERFORMING HOOK TYPES (across 3 creators):
  1. stat_hook — 12 posts, avg engagement 847
  2. story_hook — 8 posts, avg engagement 631
  3. contrarian_hook — 5 posts, avg engagement 1204

TOP 3 HOOKS TO ADAPT:
  1. "I charged $4,000 for this. It took 2 hours." (engagement: 2,100)
  2. "Most AI implementations fail. Here's the pattern I keep seeing." (engagement: 1,847)
  3. "Clients don't want AI. They want the outcome AI enables." (engagement: 1,590)
```

The "hooks to adapt" section gives you adapted versions of high-performing hooks that fit your voice — not copies, but structurally similar patterns that have proven engagement.

### Run Competitor Tracker

For ongoing monitoring of a defined competitor list:

```
Run ls:competitor-tracker to check all monitored profiles
```

The tracker flags any competitor who posted more than twice in the past week, surfaces their top-engagement post from that period, and identifies any new topics they're covering that you haven't addressed.

---

## Batch Content Creation Session

Create 5 posts in a single focused session. This is the most efficient way to maintain a consistent posting schedule.

### Session Setup

Block 90 minutes. Start with research if you haven't run it this week:

```
Run ls:research-engine with niche "AI consulting", keywords "AI agents, LLM production, AI pricing, client education, prompt engineering", max_topics: 25
```

### Write All 5 Posts

Use the top 5 topics from the research output. Write each format differently to avoid a monotonous feed:

```
Post 1: Run ls:content-writer with topic_id: tp_001, format: text_post, cta_style: direct
Post 2: Run ls:content-writer with topic_id: tp_002, format: carousel_script, cta_style: medium
Post 3: Run ls:content-writer with topic_id: tp_003, format: text_post, cta_style: soft
Post 4: Run ls:content-writer with topic_id: tp_004, format: poll_post, cta_style: medium
Post 5: Run ls:content-writer with topic_id: tp_005, format: text_post, cta_style: direct
```

### Humanize and Review All 5

```
Run ls:humanizer on posts 1-5 sequentially
Run ls:structure-reviewer on all 5 humanized drafts
```

Fix any structure issues flagged by the reviewer. A common fix for the AI consulting niche: posts that use "leverage" or "utilize" will fail humanizer checks. The reviewer will flag these.

### Schedule the Batch

```
Run ls:batch-scheduler with posts 1-5:
  post_1: Tuesday 08:00 UTC
  post_2: Wednesday 12:00 UTC
  post_3: Thursday 08:00 UTC
  post_4: Tuesday 17:00 UTC (following week)
  post_5: Wednesday 08:00 UTC (following week)
```

The scheduler enforces a minimum 20-hour gap between posts and a maximum of 5 posts per week automatically.

---

## Content Calendar Management

### Generate a Weekly Calendar

```
Run ls:content-calendar for the week of March 10-14 2026 with:
  posts_per_week: 4
  pillars: ["AI implementation lessons", "client stories", "tool breakdowns", "consulting insights"]
  formats: ["text_post", "carousel_script", "text_post", "poll_post"]
```

The calendar balances pillars across the week and assigns optimal publish times (Tuesday/Wednesday/Thursday, 07:00-08:00 or 12:00 UTC tend to perform best for the B2B AI audience).

### Generate a Monthly Calendar

```
Run ls:content-calendar for March 2026 with:
  posts_per_week: 4
  include_research_sessions: true
  include_competitor_checks: true
```

The monthly view shows which weeks to run research sessions (weeks 1 and 3) and competitor checks (week 1 of each month), alongside the publishing schedule.

### Review Calendar Status

```
Run ls:content-calendar to show current month status
```

This shows each scheduled post: planned date, status (DRAFT / APPROVED / SCHEDULED / PUBLISHED), quality scores, and topic.

---

## Visual Content Creation Workflow

Visuals increase carousel and document post reach significantly. Use this workflow for any carousel or document post.

### Step 1 — Generate AI Image Prompts

After a post passes structure review, generate visual prompts:

```
Run ls:visual-prompter with:
  post: [paste approved post text]
  format: carousel_slide
  platform: dalle3
```

For a 7-slide carousel, you'll receive 7 JSON prompt objects — one per slide — plus Midjourney variations for each.

Example output for one slide:

```json
{
  "platform": "dalle3",
  "format": "carousel_slide",
  "slide_number": 2,
  "dimensions": "1080x1080",
  "style": "clean professional minimal",
  "background": "#1a1a2e",
  "text_overlay": "RAG fails when context windows lie",
  "visual_description": "Abstract visualization of a document retrieval system with broken connection lines between a query node and a knowledge base, rendered in dark blue and white. Clean geometric shapes. No people.",
  "brand_colors": ["#0A66C2", "#FFFFFF", "#F5F5F5"],
  "font_style": "modern sans-serif",
  "mood": "authoritative yet approachable",
  "negative_prompt": "stock photo, generic, clipart, busy, cluttered, cartoon"
}
```

### Step 2 — Generate Images

Copy each JSON prompt into the OpenAI API playground or your n8n/Make workflow. DALL-E 3 produces clean, minimal visuals that work well for professional LinkedIn carousels.

For Midjourney, the output includes ready-to-paste `/imagine` commands with `--v 6 --ar 1:1 --style raw` flags.

### Step 3 — Create Canva Design (Optional)

If you prefer Canva's templating system over AI-generated images:

```
Run ls:canva-designer with:
  post: [approved post text]
  format: carousel
  slides: 7
```

The Canva MCP integration creates a new design using your connected brand kit — applying your colors, fonts, and layout templates automatically. You receive a Canva link to review and publish.

---

## Analytics Review Workflow

Run this weekly to understand what's working and adjust your content strategy.

### Weekly Performance Pull

```
Run ls:analytics-dashboard for the past 7 days
```

The dashboard pulls from Metricool and returns:

- Top 3 posts by engagement rate (reactions + comments + shares / impressions)
- Average engagement rate for the week vs. 30-day baseline
- Best performing post format (text, carousel, poll, document)
- Best performing hook type (question, stat, story, contrarian)
- Best performing content pillar
- Posts that underperformed (below 1% engagement rate) with analysis

### Monthly Deep Dive

```
Run ls:analytics-dashboard for February 2026 with include_recommendations: true
```

The monthly report adds: posting frequency analysis, optimal day/time confirmation against your actual data, content pillar performance breakdown, and 3 specific recommendations for the next month.

### Apply Insights to Research

Use analytics findings to tune your next research session:

```
Run ls:research-engine with niche "AI consulting",
  keywords from top_performing_posts: ["RAG in production", "AI agent errors", "client ROI"],
  boost_pillar: "AI implementation lessons"
```

Boosting a high-performing pillar in the research engine increases its weighting in the composite score, surfacing more topics in that area.

---

## AI Consulting Niche — Tips and Patterns

### Topics That Consistently Perform

Based on the AI consulting and implementation audience on LinkedIn:

**High-engagement angles:**
- Implementation failures you've witnessed or corrected (real specificity beats general advice)
- Pricing and ROI conversations — clients asking "what will this cost/return?" is universal pain
- The gap between AI demos and production reality — audiences are skeptical and you validate that skepticism
- Framework breakdowns — step-by-step how you scope, price, or deliver a project
- Prediction corrections — "I said X last year, here's what actually happened"

**Hook patterns that outperform for this niche:**
- Stat hooks with specific numbers you've collected from your own work ("Reviewed 40 AI proposals this year. 28 had this fatal flaw.")
- Story hooks with a named client scenario (anonymous is fine — "A $50M logistics company hired me to fix their AI implementation.")
- Contrarian hooks against popular AI hype ("Agents won't replace your workforce. Here's what they actually replace.")

**Formats that work:**
- Carousel scripts for frameworks and step-by-step breakdowns (7 slides is optimal)
- Text posts for stories, lessons, and observations (250-400 words)
- Poll posts for validation questions your clients ask (generates comments + data)

### Common Mistakes That Hurt AI Consulting Posts

**Too much jargon density.** Avoid stacking technical terms in the hook. "Leveraging agentic RAG with multi-hop retrieval to optimize LLM inference latency" is invisible. "Most AI demos work. Most AI deployments don't." is visible.

**The teaching trap.** Posts that explain everything you know rarely outperform posts that share one specific insight from a real situation. The structure-reviewer will flag posts over 900 words — this is usually a sign you're teaching a course instead of sharing a story.

**Generic CTAs.** "Drop your thoughts below" gets nothing for this audience. They need permission and a specific prompt. "What's the most common AI objection you hear from clients?" gets comments.

**AI voice leakage.** Words like "leverage," "delve," "it's important to note," "game-changer," and "in today's rapidly evolving landscape" are instant credibility killers for a technical audience. The humanizer's word blocklist targets these specifically. Run humanizer even on posts you wrote manually.

### Brand Voice for AI Consulting

The default brand voice in settings is calibrated for this niche:

```json
{
  "tone": "authoritative yet approachable",
  "pov": "practitioner",
  "style": "direct, no fluff",
  "avoid": ["we", "our team", "leverage", "synergy", "game-changer", "delve", "it's important to note"]
}
```

Write from the practitioner's perspective ("I built this," "I've seen this fail," "my client told me"). The AI consulting audience trusts people who have been in the room — not consultants who describe what should happen in theory.

---

## LinkedIn Best Practices in 2026

### Formatting

- One idea per paragraph. Blank line between every paragraph.
- No markdown headers inside posts (LinkedIn renders them oddly).
- No bullet walls. If you have 5+ items to list, turn them into numbered prose or a carousel.
- First 2 lines of a text post appear before the "see more" truncation — this is your hook. Make it earn the click.

### Posting Cadence

Optimal for the B2B AI consulting audience: 3-5 posts per week, never more than once per day. The plugin enforces a 20-hour minimum gap between posts and a 5-post weekly maximum.

Best days: Tuesday, Wednesday, Thursday. Avoid Monday (inbox clear-out day) and Friday (wind-down day).

Best times UTC: 07:00-08:00 (catches US East Coast morning + Europe afternoon), 12:00 (US East Coast lunch), 17:00 (US West Coast morning).

### Hashtags

Use 3-5 hashtags per post. Mix:
- 2 niche hashtags with under 100K followers (e.g., `#AIconsulting`, `#LLMimplementation`) — these put you in front of highly relevant, smaller audiences
- 2 reach hashtags with 500K-2M followers (e.g., `#ArtificialIntelligence`, `#Leadership`)
- 1 community hashtag specific to your audience (e.g., `#AIstrategy`, `#TechConsulting`)

Avoid hashtags with 5M+ followers — your post will be buried instantly.

### Engagement Timing

Comment on posts from others in your niche within the first hour of their post going live. This is the window when LinkedIn's algorithm surfaces your comment to the widest audience. Use the competitor tracker to monitor when your key connections are posting.

Reply to every comment on your posts within 2 hours of the post going live. This signals activity to LinkedIn's algorithm and extends the post's reach window.

### Carousel Performance

Carousels consistently outperform text posts in impressions (LinkedIn promotes the format). For AI consulting, the best-performing carousel structures are:

- **Problem → Root Cause → Solution** (7 slides: hook, problem statement, 3 root causes, your framework, CTA)
- **Common Misconception → Reality** (5 slides: hook, misconception, why it's wrong, reality, CTA)
- **Step-by-Step Framework** (8 slides: hook, context, steps 1-5, result, CTA)

The content-writer generates carousel scripts in these structures automatically based on the topic's content pillar.
