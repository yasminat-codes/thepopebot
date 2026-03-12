---
name: ls:performance-feedback-loop
description: >
  PROACTIVELY syncs post performance data from Metricool, updates hook_library scores,
  identifies winning patterns, and feeds recommendations back into the content system.
  Triggers on 'sync performance', 'update hook scores', 'what's working', 'feedback loop',
  or 'analyze post results'.
model: sonnet
context: fork
allowed-tools: Bash Read Write WebFetch
metadata:
  version: "2.0.0"
---

# ls:performance-feedback-loop

Closes the feedback loop between published content and future content quality.

## Phase 1: Sync Performance Data from Metricool
1. Call Metricool analytics API: GET /analytics/linkedin?date_range=30d
2. For each post with a metricool_id in ls_content_queue:
   - Fetch impressions, reach, engagement_rate, clicks, likes, comments, shares
   - Insert/update into ls_post_performance
3. Report: X posts synced, Y new performance records

## Phase 2: Update Hook Library Scores
1. Join ls_post_performance with ls_content_queue to get hook text for each post
2. For each hook in ls_hook_library:
   - Calculate new performance_score: weighted avg of engagement_rate for posts using this hook
   - Update: `neon_exec "UPDATE ls_hook_library SET performance_score = $score, used_count = $count WHERE id = '$hook_id'"`
3. Report: X hooks updated, top 5 performing hooks shown

## Phase 3: Identify Winning Patterns
Analyze ls_post_performance to find:
- Best performing content_pillar (by avg engagement_rate)
- Best performing post_type (text, carousel, image, poll)
- Best performing day_of_week
- Best performing hour_of_day
- Hook types with highest engagement
Present findings as a structured report table

## Phase 4: Generate Recommendations
Based on patterns found:
- Suggest content pillar adjustments (if one pillar consistently outperforms)
- Suggest posting schedule adjustments (if certain days/times work better)
- Suggest hook type preferences (if certain hook types drive more engagement)
- Flag underperforming patterns to avoid

## Phase 5: Store Recommendations
Save recommendations to:
- Neon: update ls_brand_voice_profile posting_schedule and preferred_hook_types if user approves
- Local: write to a recommendations summary for reference

## Error Handling
| Error | Recovery |
|-------|---------|
| METRICOOL_API_KEY missing | Show setup instructions, skip sync |
| No published posts | Report "no data yet", suggest publishing first |
| Neon unavailable | Show report without DB updates |
