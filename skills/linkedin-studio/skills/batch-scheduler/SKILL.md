---
name: ls:batch-scheduler
description: PROACTIVELY validates your approved content queue through 5 quality gates and batch-schedules posts to Metricool API — with circuit breaker protection, exponential backoff retries, and per-post Neon status updates — so you can schedule an entire week of LinkedIn content in one confirmed action.
model: sonnet
context: agent
allowed-tools: Read Write Bash WebFetch
metadata:
  version: "2.0.0"
---

# ls:batch-scheduler

Validates approved posts through 5 quality gates, presents a batch summary for user confirmation, then submits each post to Metricool with circuit breaker protection. Updates Neon `content_queue` with final status and Metricool post IDs.

---

## Metricool Scheduling API

**Endpoint:** `POST https://app.metricool.com/api/v2/social/metricool/post`
**Auth:** `Authorization: Bearer $METRICOOL_API_KEY`

**Payload:**
```json
{
  "content": "[post text]",
  "media_urls": ["[url1]", "[url2]"],
  "scheduled_at": "2026-03-05T08:00:00Z",
  "platform": "linkedin",
  "user_id": "[METRICOOL_USER_ID]"
}
```

**Response (success):**
```json
{
  "id": "[metricool_post_id]",
  "status": "scheduled",
  "scheduled_at": "..."
}
```

→ Full API reference: `references/METRICOOL-SCHEDULE-API.md`

---

## Circuit Breaker Configuration

| Setting | Value |
|---------|-------|
| Failure threshold | 3 consecutive failures |
| Cooldown period | 5 minutes |
| States | CLOSED → OPEN → HALF-OPEN → CLOSED |
| Half-open test | 1 request after cooldown |

**State behavior:**
- CLOSED: Normal operation. Track failures.
- OPEN: All requests blocked. Return error immediately. Wait for cooldown.
- HALF-OPEN: Send one test request. If success → CLOSED. If fail → OPEN again.

Track circuit state in memory during the session (not persisted).

---

## Retry Policy

| Attempt | Delay | Max |
|---------|-------|-----|
| 1 (initial) | — | — |
| 2 (retry 1) | 1 second | — |
| 3 (retry 2) | 2 seconds | — |
| 4 (retry 3) | 4 seconds | — |
| Give up | — | 3 retries total |

Retryable errors: 429 (rate limit), 500, 502, 503, 504.
Non-retryable errors: 400 (bad payload), 401/403 (auth), 422 (validation).

---

## 5 Quality Gates

All gates must pass before a post is included in the batch.

| Gate | Check | Fail Action |
|------|-------|-------------|
| G1: Length | 150–3000 characters | Block, show character count |
| G2: Hook | First line ≤ 20 words | Block, show word count |
| G3: CTA | Contains call-to-action signal | Warn (not block) |
| G4: Visual | media_urls present OR design_url set | Warn (not block) |
| G5: Schedule | scheduled_at is set AND in future | Block if missing or past |

**G3 CTA signals** (any one counts): "comment", "follow", "share", "DM", "link in bio", "reply", "book", "download", "check out", "learn more", question mark at end.

**Gate scoring:**
- Hard fails (G1, G2, G5): post excluded from batch
- Soft warns (G3, G4): post included but flagged in summary

---

## Pipeline

### Phase 1 — Load Approved Posts

```sql
SELECT
  id, topic, hook, humanized_content, media_urls,
  design_url, scheduled_at, content_pillar, quality_score
FROM content_queue
WHERE status = 'approved'
ORDER BY scheduled_at ASC NULLS LAST;
```

If no approved posts: show message, suggest running ls:structure-reviewer.

### Phase 2 — Run 5-Gate Validation

For each post, run all 5 gates. Collect:
- Pass/fail per gate
- Fail reasons
- Overall gate_status: PASS / WARN / FAIL

Posts with any FAIL gate: excluded from batch.
Posts with only WARN gates: included, flagged.

### Phase 3 — Display Batch Summary

```
╔══════════════════════════════════════════════════════════════╗
║  BATCH SCHEDULE SUMMARY                                      ║
╚══════════════════════════════════════════════════════════════╝

READY TO SCHEDULE (7 posts)
──────────────────────────────────────────────────────
#  Date/Time             Pillar  Topic                   Gates
─────────────────────────────────────────────────────────────
1  Tue 03 Mar 08:00 UTC  TL      [hook preview 40 chars] ✓✓✓✓✓
2  Wed 04 Mar 09:00 UTC  EDU     [hook preview]          ✓✓⚠✓✓
3  Thu 05 Mar 08:00 UTC  SP      [hook preview]          ✓✓✓⚠✓
...

BLOCKED (2 posts — gate failures)
──────────────────────────────────────────────────────
[post topic] — G1 FAIL: content is 87 chars (min 150)
[post topic] — G5 FAIL: scheduled_at not set

WARNINGS
──────────────────────────────────────────────────────
Post #2: G3 — No CTA detected. Engagement may be lower.
Post #3: G4 — No visual attached. Text-only post.

Proceed with scheduling 7 posts? [yes / no / fix-first]
```

### Phase 4 — User Confirmation

Wait for user input:
- `yes` → proceed to Phase 5
- `no` → abort, no changes made
- `fix-first` → return to caller with list of failed posts + issues

### Phase 5 — Submit to Metricool (with Circuit Breaker)

For each post in batch (in scheduled_at order):

1. Check circuit state. If OPEN → skip, log as deferred.
2. Build Metricool payload from post record.
3. POST to schedule endpoint.
4. On success: record as scheduled, reset failure counter.
5. On retryable error: apply retry policy (max 3).
6. On non-retryable error: mark as failed, log reason, continue to next post.
7. On 3 consecutive failures: open circuit, skip remaining posts, show warning.

Log each result as it completes:
```
[1/7] Scheduled ✓  — Metricool ID: mc_8ax3 — Tue 03 Mar 08:00
[2/7] Scheduled ✓  — Metricool ID: mc_9bx1 — Wed 04 Mar 09:00
[3/7] FAILED ✗     — 422 Validation Error: media_url unreachable
...
```

### Phase 6 — Update Neon content_queue

For each successfully scheduled post:
```sql
UPDATE content_queue
SET
  status = 'scheduled',
  metricool_id = '[metricool_post_id]',
  updated_at = NOW()
WHERE id = '[post_id]';
```

For failed posts: status remains 'approved'. Log failure reason.

### Phase 7 — Return Scheduling Report

```
SCHEDULING COMPLETE
────────────────────────────────────────
Successfully scheduled:  6 / 7 posts
Failed:                  1 post
Circuit breaker state:   CLOSED

SCHEDULED POSTS
  [list with Metricool IDs and dates]

FAILED POSTS
  [post topic] — 422: media_url returned 404
  Action: Fix media URL and re-run ls:batch-scheduler

content_queue updated: 6 posts → status: 'scheduled' ✓
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| METRICOOL_API_KEY missing | Halt immediately, show setup instructions |
| METRICOOL_USER_ID missing | Halt, show setup instructions |
| Circuit OPEN at start | Warn user, show cooldown time remaining |
| All posts fail gate | Show all failures, no confirmation step |
| Neon update fails | Log warning, scheduling succeeded but status not updated |
| scheduled_at in past | G5 hard fail (block from batch) |

---

## References

- `references/METRICOOL-SCHEDULE-API.md` — Full scheduling API reference
- `references/CIRCUIT-BREAKER.md` — Circuit breaker state machine detail
- `references/QUALITY-GATES.md` — Full gate definitions and edge cases
