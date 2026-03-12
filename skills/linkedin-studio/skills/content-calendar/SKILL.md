---
name: ls:content-calendar
description: PROACTIVELY plans and manages your LinkedIn content schedule — loading the full content_queue from Neon, displaying week/month views with content pillar balance, flagging schedule gaps and overloaded days, and enabling direct rescheduling and status updates with optimal posting time recommendations for the AI consulting niche.
model: sonnet
context: agent
allowed-tools: Read Write Bash Grep Glob
metadata:
  version: "2.0.0"
---

# ls:content-calendar

Plan and manage your LinkedIn content schedule. View posts by week or month, track content pillar balance, flag scheduling issues, and update post dates and statuses — all backed by the Neon `content_queue` table.

## Content Pillar Targets

> Canonical source: `strategy/CONTENT-PILLARS.md`

| Pillar | Target % | Purpose |
|--------|----------|---------|
| Thought Leadership | 35% | Authority building, opinions, predictions |
| Education | 25% | How-tos, frameworks, explainers |
| Social Proof | 25% | Case studies, results, testimonials |
| CTA | 15% | Offers, bookings, lead gen |

---

## Post Status Lifecycle

```
draft → humanized → reviewed → visual → approved → scheduled → published
```

---

## Pipeline

### Phase 1 — Load content_queue from Neon

```sql
SELECT
  id, topic, hook, content_pillar, status,
  scheduled_at, created_at, quality_score,
  metricool_id
FROM content_queue
WHERE status != 'archived'
ORDER BY scheduled_at ASC NULLS LAST;
```

Group results by:
- Scheduled week (Mon–Sun)
- Content pillar
- Status

### Phase 2 — View Selection

Ask user: **week view** or **month view**?

**Week view** — show 7-day grid:
```
MON 03 Feb    TUE 04 Feb    WED 05 Feb ...
─────────────────────────────────────────
[post hook]   [post hook]   (empty)
status: draft scheduled     ← GAP FLAGGED
pillar: TL    EDU
```

**Month view** — condensed table, one row per week, post count per day.

### Phase 3 — Content Pillar Balance Chart

Text-based distribution chart:

```
CONTENT PILLAR DISTRIBUTION
────────────────────────────────────
Thought Leadership  ████████████░░░░  36% (target: 35%) ✓
Education           ████████░░░░░░░░  24% (target: 25%) ✓
Social Proof        ████████░░░░░░░░  27% (target: 25%) ✓
CTA                 ████░░░░░░░░░░░░  13% (target: 15%) ✓
────────────────────────────────────
Total scheduled: 11 posts
```

Flags:
- ✓ Within 5% of target
- ⚠ 5–15% off target
- ✗ >15% off target (show recommended action)

### Phase 4 — Flag Issues

Scan scheduled content and surface:

| Issue | Definition | Action Shown |
|-------|-----------|--------------|
| Gap | No posts for 3+ consecutive days | "Add post on [date]?" |
| Overloaded | 2+ posts on same day | "Move one to [suggested date]?" |
| Pillar imbalance | Any pillar >15% from target | "Need X more [pillar] posts" |
| Stale drafts | Draft status, scheduled_at in past | "Reschedule or archive?" |
| Unscheduled | Status = reviewed/visual/approved, no date | "Schedule this post?" |

Display as a prioritized action list after the calendar view.

### Phase 5 — Reschedule and Status Updates

**Reschedule a post:**
User provides post ID or selects from list + new date/time.

```sql
UPDATE content_queue
SET scheduled_at = '[new_datetime]', updated_at = NOW()
WHERE id = '[post_id]';
```

Confirm: show updated calendar slot.

**Change status:**
User selects post + new status. Validate allowed transitions:

```
draft → humanized      (manual mark after humanizing)
humanized → reviewed   (manual mark after review)
reviewed → visual      (after design attached)
visual → approved      (final sign-off)
approved → scheduled   (after batch-scheduler runs)
scheduled → published  (after Metricool confirms)
any → archived         (remove from active calendar)
```

Block invalid transitions with explanation.

### Phase 6 — Optimal Posting Time Suggestions

Best days/times for AI consulting niche on LinkedIn:

| Priority | Day | Time (user local) | Why |
|----------|-----|-------------------|-----|
| 1 | Tuesday | 8:00–9:00 AM | Morning commute, high intent |
| 2 | Wednesday | 9:00–10:00 AM | Mid-week engagement peak |
| 3 | Thursday | 8:00–9:00 AM | Second peak day |
| 4 | Monday | 9:00–10:00 AM | Week-start planning mindset |
| 5 | Friday | 8:00–9:00 AM | Lower volume, less competition |

Avoid: weekends, after 6 PM on any day, Monday before 9 AM.

When flagging unscheduled posts, suggest next available optimal slot.

→ Slot availability logic: `references/SCHEDULING-LOGIC.md`

---

## Calendar Notation Legend

```
[TL] = Thought Leadership    [EDU] = Education
[SP] = Social Proof          [CTA] = CTA
● = scheduled   ◐ = draft   ○ = approved   ✓ = published
```

---

## Summary Footer

Always append after calendar view:

```
SUMMARY
────────────────────────────────
Published this month:    [N]
Scheduled (upcoming):    [N]
In progress (drafts):    [N]
Needs attention:         [N] items flagged
Next post due:           [date] — [hook preview]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Neon connection fails | Show error, suggest checking `DATABASE_URL` env |
| Empty content_queue | Show empty calendar, prompt to run ls:content-writer |
| Invalid status transition | Block with message showing allowed transitions |
| No scheduled_at set | Show in "Unscheduled" section at bottom of calendar |

---

## References

- `references/SCHEDULING-LOGIC.md` — Optimal slot algorithm and conflict resolution
- `references/PILLAR-BALANCE.md` — Pillar calculation and rebalancing recommendations
- `strategy/CONTENT-PILLARS.md` — Canonical pillar distribution (single source of truth)
- `strategy/AUTHORITY-PLAYBOOK.md` — Stage-based pillar overrides and weekly content arc
