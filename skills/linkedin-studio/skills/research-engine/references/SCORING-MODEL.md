# SCORING-MODEL.md — Research Engine Composite Scoring Algorithm

## Overview

Each topic in `ls_topic_bank` receives a `composite_score` that combines three signals:
trend momentum, audience pain intensity, and creator engagement proof. This score
determines which topics surface first for content generation.

---

## Core Formula

```
composite_score = (trend_score * 0.35) + (pain_intensity * 0.40) + (creator_engagement * 0.25)
```

### Weight Rationale

| Component          | Weight | Source                          | Why This Weight                            |
|--------------------|--------|---------------------------------|--------------------------------------------|
| trend_score        | 35%    | Google Trends                   | Recency signal — riding wave beats being early |
| pain_intensity     | 40%    | Reddit discussions / LinkedIn   | Pain drives clicks — highest weight       |
| creator_engagement | 25%    | LinkedIn post engagement data   | Proof of content market fit                |

---

## Input Scale Normalization

All three inputs must be on a **0–100 scale** before the formula is applied.

### trend_score normalization

Google Trends returns values 0–100 natively. Use the peak value from `interest_over_time()`
for the primary keyword. If multiple related queries are found, average the top 3.

```python
# Raw pytrends output is already 0-100
trend_score = int(interest_df['query_keyword'].max())
```

### pain_intensity normalization

Reddit score based on upvote count, comment count, and pain language detection:

```python
# Raw signals
upvote_ratio     = post.score / max_upvotes_in_batch   # 0.0 - 1.0
comment_ratio    = post.num_comments / max_comments_in_batch
pain_keywords    = count_pain_words(post.title + post.selftext) / 20  # cap at 1.0

# Combine
raw_pain = (upvote_ratio * 0.4) + (comment_ratio * 0.3) + (pain_keywords * 0.3)
pain_intensity = round(raw_pain * 100, 2)  # 0-100
```

Pain keywords to detect: "struggling", "frustrated", "problem", "help", "anyone else",
"how do I", "failing", "can't figure out", "stuck", "overwhelmed", "burning out",
"nobody talks about", "myth", "truth about".

### creator_engagement normalization

LinkedIn engagement score based on reactions, comments, and shares on similar posts:

```python
# Raw signals from scraped LinkedIn posts on the same topic
avg_reactions    = mean([p.reactions for p in similar_posts])
avg_comments     = mean([p.comments for p in similar_posts])
avg_shares       = mean([p.shares for p in similar_posts])

# Normalize against observed maximums in this scrape batch
reaction_ratio   = min(avg_reactions / 500, 1.0)   # cap at 500 reactions
comment_ratio    = min(avg_comments / 100, 1.0)    # cap at 100 comments
share_ratio      = min(avg_shares / 50, 1.0)       # cap at 50 shares

raw_engagement   = (reaction_ratio * 0.5) + (comment_ratio * 0.3) + (share_ratio * 0.2)
creator_engagement = round(raw_engagement * 100, 2)
```

---

## Multi-Source Bonus

When a topic is validated by multiple research sources, confidence increases.
Apply a multiplier **after** the base composite score is calculated:

| Sources Found         | Bonus    | Multiplier |
|-----------------------|----------|------------|
| 1 source              | None     | × 1.00     |
| 2 sources             | +10%     | × 1.10     |
| All 3 sources         | +20%     | × 1.20     |

Sources are: `linkedin`, `google_trends`, `reddit`.

```python
source_count = len(set(topic['sources']))
if source_count == 3:
    bonus_multiplier = 1.20
elif source_count == 2:
    bonus_multiplier = 1.10
else:
    bonus_multiplier = 1.00

final_score = min(base_composite * bonus_multiplier, 100.0)
```

The bonus is capped so composite_score never exceeds 100.

---

## Score Interpretation

| Score Range | Label        | Action                                              |
|-------------|--------------|-----------------------------------------------------|
| 80–100      | Excellent    | Prioritize immediately — write this week            |
| 60–79       | Good         | Queue for next 2 weeks                              |
| 40–59       | Moderate     | Hold in bank — revisit if trend increases           |
| Below 40    | Low Priority | Archive unless niche is very specific               |

---

## Worked Example

**Topic:** "Why most solopreneurs fail at content consistency"

| Component          | Raw Signal                                      | Normalized Score |
|--------------------|-------------------------------------------------|------------------|
| trend_score        | Google Trends peak = 74 (already 0-100)         | 74               |
| pain_intensity     | Reddit: 0.6 upvote ratio, 0.5 comment ratio, 8 pain words → raw 0.61 × 100 | 61.0 |
| creator_engagement | LinkedIn avg: 310 reactions, 42 comments, 18 shares → raw 0.54 × 100 | 54.0 |

**Base composite score:**
```
composite_score = (74 * 0.35) + (61.0 * 0.40) + (54.0 * 0.25)
               = 25.90 + 24.40 + 13.50
               = 63.80
```

**Sources found:** linkedin + google_trends + reddit = all 3 → × 1.20

```
final_score = 63.80 * 1.20 = 76.56
```

**Result:** Score 76.56 → Good. Queue for the next 2 weeks.

---

## Database Storage

The composite score is stored as `NUMERIC(5, 2)` in `ls_topic_bank.composite_score`.

### Insert with composite score

```bash
source database/neon-utils.sh

neon_exec "
    INSERT INTO ls_topic_bank (
        title, raw_topic, trend_score, pain_intensity, creator_engagement,
        composite_score, sources, status
    ) VALUES (
        'Why most solopreneurs fail at content consistency',
        'solopreneurs content consistency failure',
        74,
        61.0,
        54.0,
        76.56,
        ARRAY['linkedin', 'google_trends', 'reddit'],
        'new'
    );
"
```

### Update composite score after re-scoring

```bash
source database/neon-utils.sh

neon_exec "
    UPDATE ls_topic_bank
    SET composite_score = 76.56,
        trend_score     = 74,
        pain_intensity  = 61.0,
        creator_engagement = 54.0,
        updated_at      = NOW()
    WHERE id = '<uuid-here>';
"
```

### Fetch top topics by composite score

```bash
source database/neon-utils.sh

neon_query "
    SELECT id, title, composite_score, content_pillar, sources
    FROM ls_topic_bank
    WHERE status = 'new'
    ORDER BY composite_score DESC
    LIMIT 10;
"
```
