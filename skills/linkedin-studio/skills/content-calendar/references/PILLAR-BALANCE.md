# Pillar Balance Reference

> Pillar distribution calculation and rebalancing recommendations. References `strategy/CONTENT-PILLARS.md` as canonical source of truth.

---

## Canonical Source

**All pillar targets are defined in `strategy/CONTENT-PILLARS.md`.** This file handles calculation and rebalancing logic only. Never hardcode percentages here.

Current targets (from canonical source):

| Pillar | Code | Target % |
|---|---|---|
| Thought Leadership | TL | 35% |
| Education | EDU | 25% |
| Social Proof | SP | 25% |
| CTA / Conversion | CTA | 15% |

**Note:** During Authority Stage 1 (Unknown), `strategy/AUTHORITY-PLAYBOOK.md` temporarily overrides to TL 40%, EDU 30%, SP 20%, CTA 10%. This override takes precedence until Stage 2 transition.

---

## Calculation Method

### Per-Week Calculation
```
pillar_percentage = (posts_in_pillar / total_posts_this_week) * 100
deviation = abs(pillar_percentage - target_percentage)
```

### Per-Month Calculation (rolling 30 days)
```sql
SELECT
  content_pillar,
  COUNT(*) as post_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as actual_pct
FROM ls_content_queue
WHERE status IN ('scheduled', 'published')
  AND scheduled_at >= NOW() - INTERVAL '30 days'
GROUP BY content_pillar;
```

Compare `actual_pct` against target for each pillar.

---

## Deviation Thresholds

| Deviation | Status | Icon | Action |
|---|---|---|---|
| 0-5% | OK | ✓ | No action needed |
| 5-15% | Warning | ⚠ | Flag in calendar view. Suggest adjusting next 2-3 posts. |
| >15% | Critical | ✗ | Show recommended rebalancing action. Prioritize underrepresented pillar in next scheduled post. |

---

## Rebalancing Recommendations

When a pillar is **over target (>5% deviation):**
- Reduce scheduling of that pillar for next 1-2 weeks
- Replace with the most underrepresented pillar

When a pillar is **under target (>5% deviation):**
- Prioritize this pillar for the next 2-3 post slots
- Suggest specific angles from `strategy/TOPIC-ANGLES.md` for the underrepresented pillar
- If under-representation is in SP: check `strategy/STORY-BANK.md` for available client stories

**Example rebalancing output:**
```
PILLAR REBALANCE NEEDED
────────────────────────────────────────
TL:  42% (target: 35%)  ⚠ +7%  → schedule fewer TL posts next week
EDU: 25% (target: 25%)  ✓       → on target
SP:  17% (target: 25%)  ✗ -8%  → add 2 SP posts next week
CTA: 17% (target: 15%)  ✓       → on target

SUGGESTED ACTION: Replace 1 planned TL post with a Social Proof post.
See strategy/STORY-BANK.md for available client stories (S-008, S-009, S-010).
```

---

## Integration with Content Calendar

`ls:content-calendar` Phase 3 uses this reference to:
1. Calculate current distribution from ls_content_queue
2. Compare against targets from `strategy/CONTENT-PILLARS.md`
3. Apply deviation thresholds
4. Generate the pillar balance chart with status icons
5. Include rebalancing suggestions in the Phase 4 action list
