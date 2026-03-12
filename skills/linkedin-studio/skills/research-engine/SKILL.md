---
name: ls:research-engine
description: >
  PROACTIVELY orchestrates multi-source topic research by simultaneously dispatching
  parallel searches across Google Trends, Reddit pain-point data, and LinkedIn creator
  post analysis to surface high-engagement content opportunities. Triggers on research
  briefs, niche discovery requests, content pillar planning, keyword expansion tasks,
  and trending topic identification for AI consulting and implementation audiences.
  Aggregates and deduplicates all signals, scores topics by engagement potential, and
  stores structured records in Neon topic_bank for downstream content generation.
model: opus
context: fork
allowed-tools: Bash Read Write Glob Grep Agent WebFetch WebSearch
hooks:
  PreToolUse:
    - validate_research_brief
  PostToolUse:
    - log_topic_scores
  Stop:
    - confirm_neon_write
metadata:
  version: "2.0.0"
---

# ls:research-engine

Master research orchestrator for the LinkedIn Studio plugin. Dispatches sub-research
in parallel across Google Trends, Reddit, and LinkedIn creators. Scores, deduplicates,
and stores all discovered topics in Neon `topic_bank`.

→ See references/NEON-SCHEMA.md for topic_bank table structure
→ See references/SCORING-MODEL.md for engagement scoring algorithm
→ See references/SCRAPING-STRATEGY.md for LinkedIn fallback chain
→ See strategy/AUDIENCE.md for ICP pain points and content angles
→ See strategy/TOPIC-ANGLES.md for evergreen seed topics by niche
→ See strategy/CONTENT-PILLARS.md for canonical pillar distribution

---

## Phase 1: Receive Research Brief

**Inputs required:**
- `niche` — Primary niche (e.g., "AI consulting", "process automation")
- `keywords` — 3–10 seed keywords (comma-separated or list)
- `content_pillars` — 2–5 strategic pillars (e.g., "thought leadership", "case studies")
- `time_range` — Lookback window (default: `last_30_days`)
- `max_topics` — Cap on topics returned (default: 25)

**Validation:**
- Niche must be non-empty
- At least 1 keyword required
- If content_pillars is empty, infer from niche using built-in taxonomy

**Strategy supplement:**
- If `keywords` list is sparse (fewer than 3), supplement with seed topics from `strategy/TOPIC-ANGLES.md` matching the provided niche
- If `content_pillars` is empty, load from `strategy/CONTENT-PILLARS.md` instead of built-in taxonomy
- Cross-reference `strategy/AUDIENCE.md` pain points for pain-point-weighted keywords

```bash
# Validate inputs before dispatching
if [ -z "$NICHE" ] || [ -z "$KEYWORDS" ]; then
  echo "ERROR: niche and keywords are required" >&2
  exit 1
fi
```

---

## Phase 2: Dispatch 3 Parallel Sub-Searches

Run all three sources simultaneously. Do not wait for one before starting another.
Each sub-search is independent and may fail gracefully without blocking the others.

### Source A — Google Trends (pytrends)
```python
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(keywords, timeframe='today 1-m', geo='US')
interest_df = pytrends.interest_over_time()
related = pytrends.related_queries()
```
- Extract: rising queries, top related topics, breakout keywords
- On failure: log warning, continue with empty Google Trends result set

→ See references/GOOGLE-TRENDS-PARAMS.md for full pytrends configuration

### Source B — Reddit (Pushshift + PRAW)
Delegate to `ls:pain-point-miner` for full Reddit extraction.
- Pass: `keywords`, `time_range`, subreddit list from plugin config
- Receive back: list of `{pain_point, upvotes, comments, subreddit, url}`

→ See references/REDDIT-INTEGRATION.md for API credentials and rate limits

### Source C — LinkedIn Creator Scraping
Delegate to `ls:creator-analyzer` for creator post extraction.
- Pass: `keywords`, `niche`, `max_creators: 10`
- Receive back: list of `{topic, hook, engagement_score, creator_url, post_url}`

→ See references/SCRAPING-STRATEGY.md for 3-fallback chain details

**Graceful degradation table:**

| Source Failed | Action |
|---|---|
| Google Trends | Skip; mark topics from other sources as `trend_unverified` |
| Reddit | Skip; reduce pain-point weighting in final score |
| LinkedIn creator | Skip; rely on trends + Reddit only |
| Two sources failed | Warn user; continue with single source if available |
| All three failed | Abort with actionable error message |

---

## Phase 3: Aggregate and Score All Topics

Collect results from all three sources into a unified topic list. Each topic entry:
```json
{
  "raw_topic": "string",
  "source": ["google_trends" | "reddit" | "linkedin_creator"],
  "signals": {
    "trend_score": 0.0,
    "pain_intensity": 0.0,
    "creator_engagement": 0.0
  },
  "composite_score": 0.0,
  "hook_suggestions": [],
  "cta_suggestions": [],
  "post_ideas": []
}
```

**Composite scoring formula:**
```
composite_score = (trend_score * 0.35) + (pain_intensity * 0.40) + (creator_engagement * 0.25)
```

Multi-source bonus: +10% if topic appears in 2+ sources, +20% if all 3 sources.

For each topic, generate:
- 2–3 hook suggestions (question hook, stat hook, contrarian hook)
- 1–2 CTA suggestions (comment prompt, DM offer, resource link)
- 2–4 post ideas with content angles

→ See references/SCORING-MODEL.md for full weighting rationale and normalization rules

---

## Phase 4: Deduplicate Against Existing Neon topic_bank

Before storing, check for duplicates using semantic similarity against stored topics.

```sql
SELECT topic_id, raw_topic, composite_score, created_at
FROM topic_bank
WHERE niche = $1
  AND created_at > NOW() - INTERVAL '30 days'
ORDER BY composite_score DESC;
```

Deduplication logic:
1. Exact string match → skip (already stored)
2. Cosine similarity > 0.85 (using stored embedding) → skip or update score if higher
3. No match → mark as new, proceed to Phase 5

Track counts: `new_topics`, `skipped_duplicates`, `updated_scores` for Phase 5 report.

→ See references/NEON-SCHEMA.md for topic_bank schema and embedding column details

---

## Phase 5: Store New Topics and Return Ranked List

**Write to Neon topic_bank:**
```sql
INSERT INTO topic_bank (
  topic_id, niche, raw_topic, composite_score,
  hook_suggestions, cta_suggestions, post_ideas,
  sources, trend_score, pain_intensity, creator_engagement,
  created_at, updated_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW())
ON CONFLICT (topic_id) DO UPDATE
  SET composite_score = EXCLUDED.composite_score,
      updated_at = NOW();
```

**Return ranked list** (sorted by composite_score descending):
```
RESEARCH COMPLETE — {N} new topics discovered

RANK | TOPIC_ID | RAW TOPIC | SCORE | SOURCES | TOP HOOK
-----|----------|-----------|-------|---------|----------
1    | tp_001   | ...       | 0.91  | 3/3     | "Why most..."
2    | tp_002   | ...       | 0.84  | 2/3     | "The truth..."
...

STORAGE: {new_topics} new, {skipped_duplicates} skipped, {updated_scores} updated
NEXT: Pass topic_id list to ls:content-pipeline or ls:idea-bank
```

---

## Error Handling Reference

| Error | Recovery |
|---|---|
| Neon connection refused | Retry 3x with exponential backoff (2s, 4s, 8s) |
| pytrends rate limit (429) | Wait 60s, retry once; skip on second failure |
| Reddit API timeout | Fall back to PRAW; if PRAW fails, skip Reddit |
| LinkedIn scrape blocked | Trigger creator-analyzer fallback chain |
| Embedding service down | Skip similarity check; store all new topics |

All errors logged to stdout with `[research-engine][ERROR]` prefix for Coolify log capture.

---

## References

- `references/NEON-SCHEMA.md` — topic_bank DDL, indexes, embedding column
- `references/SCORING-MODEL.md` — composite scoring weights and normalization
- `references/SCRAPING-STRATEGY.md` — LinkedIn 3-fallback chain
- `references/GOOGLE-TRENDS-PARAMS.md` — pytrends configuration
- `references/REDDIT-INTEGRATION.md` — Pushshift + PRAW credentials and limits
- `strategy/AUDIENCE.md` — ICP pain points for keyword supplementation
- `strategy/TOPIC-ANGLES.md` — Evergreen seed topics by validated niche
- `strategy/CONTENT-PILLARS.md` — Canonical pillar distribution
