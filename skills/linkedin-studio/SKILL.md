# LinkedIn Studio Skill Context

> Loaded automatically on every skill invocation. Single source of truth for skill architecture, database layout, conventions, and skill routing.

## Overview

LinkedIn Studio (`ls:`) is a 15-skill content production system for LinkedIn, built for AI consulting and implementation professionals. It automates the full research-to-publish pipeline: trend mining, pain point extraction, competitor analysis, content writing, humanization, structural review, visual design, scheduling, and performance analytics.

**Niche:** AI consulting and implementation
**Platform:** LinkedIn
**Namespace:** `ls`
**Database:** Neon PostgreSQL (serverless)
**Scheduling/Analytics:** Metricool API

---

## Architecture

```
Layer 1: INTELLIGENCE (Research & Signals)
├── ls:research-engine        [Tier 5]  Multi-source topic research orchestrator
├── ls:creator-analyzer       [Tier 4]  LinkedIn creator post scraping + pattern extraction
├── ls:pain-point-miner       [Tier 4]  Reddit pain point extraction (Pushshift + PRAW)
└── ls:competitor-tracker     [Tier 4]  Competitor profile monitoring + insight aggregation

Layer 2: CREATION (Writing & Transformation)
├── ls:content-writer         [Tier 4]  Post generation from research data + brand voice
├── ls:humanizer              [Tier 4]  6-pass AI phrase removal and voice naturalization
├── ls:repurposer             [Tier 3]  Long-form content → LinkedIn post formats
└── ls:structure-reviewer     [Tier 3]  Hook/CTA/whitespace/hashtag compliance scoring

Layer 3: VISUAL (Design & Imagery)
├── ls:visual-prompter        [Tier 3]  AI image prompt generation (DALL-E / Imagen / MJ)
└── ls:canva-designer         [Tier 4]  Canva MCP carousel and image design

Layer 4: MANAGEMENT (Planning & Storage)
├── ls:content-calendar       [Tier 4]  Weekly/monthly content schedule planning
├── ls:idea-bank              [Tier 3]  Topic bank and brand voice CRUD via Neon
└── ls:analytics-dashboard    [Tier 4]  Metricool performance reports + recommendations

Layer 5: DISTRIBUTION (Scheduling & Publishing)
├── ls:batch-scheduler        [Tier 4]  Quality-gated batch submission to Metricool
└── ls:content-pipeline       [Tier 6]  Master orchestrator: research → publish
```

---

## Database Tables (Neon PostgreSQL)

All tables use the `ls_` logical prefix in application code. Schema lives in `database/schema.sql`.

| # | Table                  | Purpose                                              | Key Columns                              |
|---|------------------------|------------------------------------------------------|------------------------------------------|
| 1 | `ls_topic_bank`        | Central idea repository                              | title, raw_topic, composite_score, status|
| 2 | `ls_hook_library`      | Proven hooks with performance scores                 | hook_text, hook_type, performance_score   |
| 3 | `ls_pain_points`       | Reddit-sourced audience pain points                  | pain_text, subreddit, engagement_score   |
| 4 | `ls_trends`            | Google Trends data with 7-day TTL                    | keyword, trend_score, expires_at         |
| 5 | `ls_creator_posts_cache`| Cached LinkedIn creator posts for pattern mining    | post_text, creator_url, engagement_rate  |
| 6 | `ls_competitor_tracker` | Competitor profiles and aggregated insights         | profile_url, avg_engagement_rate         |
| 7 | `ls_content_queue`     | Publishing pipeline: draft to published              | post_text, status, ai_score, hook_score  |
| 8 | `ls_ai_phrases_blocklist`| AI-giveaway phrases for humanizer detection        | phrase, category, severity               |
| 9 | `ls_post_performance`  | Metricool performance data post-publish              | impressions, engagement_rate, posted_at  |
|10 | `ls_brand_voice_profile`| User writing persona and preferences                | persona, signature_phrases               |

---

## Key Conventions

### Naming
- All skill names: `ls:<skill-name>` (lowercase, hyphenated)
- All slash commands: `/ls:<command-name>`
- Database tables: `ls_` prefix in SQL (e.g., `ls_topic_bank`, `ls_content_queue`)
- Use `source database/neon-utils.sh` then `neon_query`/`neon_exec` for all DB access

### Status Flows
- **topic_bank:** `new` -> `in_progress` -> `used` | `archived`
- **content_queue:** `draft` -> `humanized` -> `reviewed` -> `visual_added` -> `approved` -> `scheduled` -> `published` | `failed`

### Quality Thresholds (enforced by PreToolUse hook)
- Post quality score: >= 75/100
- AI detection score: <= 25/100
- Hook strength score: >= 7/10
- Duplicate similarity: <= 60%

### Content Pillars

> Canonical source: `strategy/CONTENT-PILLARS.md`

- Thought Leadership: 35%
- Education: 25%
- Social Proof: 25%
- CTA/Conversion: 15%

---

## Skill Routing — What to Use When

| Task                                    | Skill                    |
|-----------------------------------------|--------------------------|
| Research trending topics                | `ls:research-engine`     |
| Analyze what top creators are posting   | `ls:creator-analyzer`    |
| Find audience pain points on Reddit     | `ls:pain-point-miner`    |
| Monitor a competitor's LinkedIn         | `ls:competitor-tracker`  |
| Write a LinkedIn post from scratch      | `ls:content-writer`      |
| Remove AI-sounding phrases from a draft | `ls:humanizer`           |
| Turn an article into LinkedIn posts     | `ls:repurposer`          |
| Check post structure and compliance     | `ls:structure-reviewer`  |
| Generate an image prompt for a post     | `ls:visual-prompter`     |
| Create a Canva carousel design          | `ls:canva-designer`      |
| Plan this week's content schedule       | `ls:content-calendar`    |
| Browse or manage saved topic ideas      | `ls:idea-bank`           |
| View post performance analytics         | `ls:analytics-dashboard` |
| Schedule a batch of approved posts      | `ls:batch-scheduler`     |
| Run the full research-to-publish flow   | `ls:content-pipeline`    |

---

## Common Workflows

### Full Pipeline (research to publish)
```
/ls:pipeline → ls:content-pipeline orchestrates all stages automatically
  1. ls:research-engine      — surface topics
  2. ls:content-writer       — generate drafts
  3. ls:humanizer            — strip AI patterns
  4. ls:structure-reviewer   — validate compliance
  5. ls:visual-prompter      — create image prompts
  6. ls:batch-scheduler      — schedule via Metricool
```

### Quick Post (idea already known)
```
/ls:write-post "topic" → ls:content-writer
/ls:humanize            → ls:humanizer
/ls:review-structure    → ls:structure-reviewer
/ls:schedule-batch      → ls:batch-scheduler
```

### Research Only (no publishing)
```
/ls:research "AI agents" → ls:research-engine
/ls:track-competitor URL → ls:competitor-tracker
/ls:analytics            → ls:analytics-dashboard
```

### Schedule Batch (pre-written content)
```
/ls:calendar            → ls:content-calendar (plan slots)
/ls:schedule-batch      → ls:batch-scheduler (submit to Metricool)
```
