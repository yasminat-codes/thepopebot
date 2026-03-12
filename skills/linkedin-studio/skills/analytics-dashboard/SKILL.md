---
name: ls:analytics-dashboard
description: PROACTIVELY pulls LinkedIn performance data from Metricool API and generates actionable reports — tracking impressions, reach, engagement rate, CTR, content pillar performance, and time-of-day patterns, then stores metrics in Neon post_performance and delivers concrete recommendations to improve your content strategy.
model: sonnet
context: agent
allowed-tools: Read Write Bash WebFetch
metadata:
  version: "2.0.0"
---

# ls:analytics-dashboard

Connects to Metricool API, pulls LinkedIn post performance, stores metrics in Neon, and returns a formatted dashboard with recommendations. Supports 30-day and 90-day analysis windows with period-over-period comparison.

---

## Metricool API Reference

**Base URL:** `https://app.metricool.com/api/v2`
**Auth header:** `Authorization: Bearer $METRICOOL_API_KEY`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/metrics/linkedin` | GET | Post-level performance data |
| `/analytics/summary` | GET | Account-level aggregates |
| `/posts` | GET | Published post list with IDs |

→ Full endpoint parameters: `references/METRICOOL-API.md`

---

## Neon Tables Used

| Table | Purpose |
|-------|---------|
| `post_performance` | Stores per-post metrics over time |
| `content_queue` | Source of post metadata (pillar, topic) |

---

## Pipeline

### Phase 1 — Connect to Metricool API

Verify `METRICOOL_API_KEY` environment variable exists. If missing, halt with:
```
Error: METRICOOL_API_KEY not set. Add to environment variables.
```

Test connection:
```
GET /api/v2/analytics/summary?platform=linkedin&days=1
```

If auth fails (401/403): halt with credential error message.

### Phase 2 — Pull Post Performance Data

Ask user: **30 days** or **90 days**?

Fetch post-level data:
```
GET /api/v2/metrics/linkedin?
  date_from=[start_date]&
  date_to=[today]&
  metrics=impressions,reach,engagements,clicks,engagement_rate,shares,comments,likes
```

Also fetch previous period (same duration) for comparison.

Parse response into structured records per post:
```
{
  metricool_post_id, post_text_preview (50 chars),
  published_at, impressions, reach, engagements,
  clicks, likes, comments, shares, engagement_rate
}
```

### Phase 3 — Calculate Metrics

**Engagement rate per post:**
```
engagement_rate = (likes + comments + shares) / impressions * 100
```

**Pillar performance averages:**
Join with `content_queue` on `metricool_id` to get content pillar per post.

```sql
SELECT
  cq.content_pillar,
  AVG(pp.engagement_rate) as avg_engagement,
  AVG(pp.impressions) as avg_impressions,
  COUNT(*) as post_count
FROM post_performance pp
JOIN content_queue cq ON cq.metricool_id = pp.metricool_post_id
WHERE pp.recorded_at >= NOW() - INTERVAL '[period] days'
GROUP BY cq.content_pillar;
```

**Time-of-day analysis:**
Group posts by `EXTRACT(HOUR FROM published_at)`, average engagement_rate per hour bucket.

**Period comparison:**
```
change_pct = (current_period_avg - previous_period_avg) / previous_period_avg * 100
```

### Phase 4 — Compare Against Previous Period

Show deltas for key metrics:

| Metric | Current | Previous | Change |
|--------|---------|----------|--------|
| Avg impressions | 1,240 | 980 | +26.5% ↑ |
| Avg engagement rate | 4.2% | 3.8% | +10.5% ↑ |
| Total reach | 18,400 | 14,200 | +29.6% ↑ |
| Avg CTR | 1.8% | 2.1% | -14.3% ↓ |

Flag significant drops (>15% decrease) with ⚠.

### Phase 5 — Generate Insights

**Top 5 posts** (by engagement rate):
```
1. [hook preview] — 7.8% ER — Thought Leadership — Tue 8AM
2. [hook preview] — 6.4% ER — Education — Wed 9AM
...
```

**Best posting time** (top 3 hour buckets by avg engagement rate):
```
Best times for your account:
  1. Tuesday 8–9 AM   → avg 5.9% ER
  2. Wednesday 9–10 AM → avg 5.3% ER
  3. Thursday 8–9 AM  → avg 4.8% ER
```

**Underperforming pillars** (avg ER < 3%):
```
⚠ Social Proof posts averaging 2.1% ER (below 3% threshold)
  → Consider: more specific results, shorter format, add proof elements
```

**Recommendations block** (always generate 3–5):
- Derived from pillar ER data
- Derived from time-of-day analysis
- Derived from top post patterns (format, length, hook type)

→ Recommendation generation logic: `references/INSIGHT-RULES.md`

### Phase 6 — Store in Neon post_performance

Upsert per-post metrics:
```sql
INSERT INTO post_performance (
  metricool_post_id, recorded_at,
  impressions, reach, engagements, clicks,
  likes, comments, shares, engagement_rate
)
VALUES (...)
ON CONFLICT (metricool_post_id, recorded_at::date)
DO UPDATE SET
  impressions = EXCLUDED.impressions,
  engagement_rate = EXCLUDED.engagement_rate,
  updated_at = NOW();
```

Log: "Stored metrics for [N] posts."

### Phase 7 — Return Dashboard Report

Output format:

```
╔══════════════════════════════════════════════════════════════╗
║  LINKEDIN ANALYTICS DASHBOARD                                ║
║  Period: [start] → [end]  |  [N] posts analyzed             ║
╚══════════════════════════════════════════════════════════════╝

ACCOUNT OVERVIEW
────────────────────────────────────
Total Impressions:     18,400  (+26.5% vs prev period)
Avg Engagement Rate:    4.2%   (+10.5%)
Total Clicks:             892   (-14.3% ⚠)
New Followers:             34   (+13.3%)

TOP 5 POSTS
────────────────────────────────────
[ranked list]

PILLAR PERFORMANCE
────────────────────────────────────
[table with avg ER per pillar]

BEST POSTING TIMES
────────────────────────────────────
[top 3 time slots]

RECOMMENDATIONS
────────────────────────────────────
1. [recommendation]
2. [recommendation]
3. [recommendation]

Metrics stored in Neon post_performance ✓
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| METRICOOL_API_KEY missing | Halt with setup instructions |
| API 401/403 | Halt with re-auth instructions |
| API rate limit (429) | Wait 60s, retry once |
| No posts in Neon content_queue | Skip pillar join, note in output |
| Neon write fails | Continue, report dashboard, log write failure |
| <5 posts in period | Note low sample size in all averages |

---

## References

- `references/METRICOOL-API.md` — Full endpoint reference and response schemas
- `references/INSIGHT-RULES.md` — Recommendation generation logic and thresholds
- `references/METRICS-SCHEMA.md` — post_performance Neon table schema
