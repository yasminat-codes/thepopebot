# Scheduling Logic Reference

> Optimal slot algorithm for LinkedIn posting in the AI consulting niche. Referenced by `ls:content-calendar` Phase 6.

---

## Day Ranking

| Priority | Day | Rationale |
|---|---|---|
| 1 | Tuesday | Highest professional engagement. Decision-makers are settled into the week. |
| 2 | Wednesday | Mid-week peak. Good for educational content. |
| 3 | Thursday | Second-best engagement day. Strong for thought leadership. |
| 4 | Monday | Week-start planning mindset. Good for frameworks and bold takes. |
| 5 | Friday | Lower volume = less competition, but also lower engagement. |

---

## Time Ranking (EST)

| Priority | Time Slot | Rationale |
|---|---|---|
| 1 | 8:00-9:00 AM | Morning commute, high intent, decision-makers check LinkedIn |
| 2 | 9:00-10:00 AM | Extended morning window, still strong |
| 3 | 12:00-1:00 PM | Lunch break engagement |
| 4 | 5:00-6:00 PM | End of day wind-down |

**Avoid:** After 6 PM any day, weekends (unless testing), Monday before 9 AM.

---

## Scheduling Constraints

| Constraint | Rule |
|---|---|
| Minimum gap | 20 hours between posts (no same-day posts unless testing) |
| Maximum per week | 5 posts (Stage 1: 4-5, Stage 2+: 3-5) |
| Weekend cap | Max 1 post on Saturday or Sunday combined |
| CTA spacing | Never schedule 2 CTA-pillar posts within 48 hours |
| Pillar adjacency | No more than 2 consecutive posts from the same pillar |

---

## Optimal Slot Algorithm

When scheduling a new post, find the best available slot:

```
1. Get all scheduled posts for the target week
2. For each day (Tue > Wed > Thu > Mon > Fri):
   a. Check: is there already a post on this day?
      - If yes: skip (minimum gap rule)
      - If no: this day is a candidate
   b. Check: does this post's pillar match the previous day's post pillar?
      - If same pillar 2x in a row: prefer a different day
   c. Check: is this a CTA post within 48hr of another CTA?
      - If yes: skip this slot
3. From candidates, pick the highest-priority day
4. Assign the highest-priority time slot for that day
5. Return: suggested datetime
```

---

## Conflict Resolution

| Conflict | Resolution |
|---|---|
| Two posts want the same day | Move the lower-priority post to next available day |
| Week is full (5 posts) | Queue for next week, suggest best slot |
| No weekday slots available | Offer Saturday 9 AM as fallback (weekend cap check) |
| CTA too close to another CTA | Move CTA to next available slot 48+ hours away |

---

## Gap Detection

Flag a gap when:
- 3+ consecutive days have no posts scheduled
- A week has fewer than 3 posts (Stage 1 target: 4-5)
- A weekday has no post and it's a Tue/Wed/Thu (high-priority days)

Suggest filling gaps with the most underrepresented pillar from `strategy/CONTENT-PILLARS.md`.
