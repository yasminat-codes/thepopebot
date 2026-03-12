# Plan Quality Guide — Good vs Bad Plans

> Used during Phase 5-6 to validate plan quality before presenting to user.
> Every characteristic here is a checklist item for the plan review.

---

## What Makes a GOOD Plan vs a BAD Plan

### GOOD Plan Characteristics

**Specificity over generality:**
Bad: "Create an API endpoint for the feature"
Good: "Create POST /api/v1/webhooks/slack in app/api/webhooks.py. Handler must verify X-Slack-Signature header using HMAC-SHA256 and return 200 within 3 seconds."

**Failure paths are documented:**
A good plan has as much detail about what happens when things go wrong as when they go right.
If the plan only describes the happy path, it's incomplete.

**References existing code:**
Good plans say "extend the existing rate_limiter.py" not "add rate limiting."
They reference specific files, functions, and patterns that already exist.

**Measurable success criteria:**
Every success criterion can be tested with a command or a manual step.
"The feature works" is not a success criterion.

**Phase dependencies are clear:**
Each phase has a gate — a specific condition that must be true before the next phase begins.

---

### BAD Plan Characteristics

**Vague technology choices:**
"Use Redis for caching" without saying what gets cached, what the key structure is, or what the TTL is.

**Missing error handling:**
The plan describes only what happens when everything succeeds.
No mention of timeouts, retries, or partial failures.

**Assuming code doesn't exist:**
The plan proposes building something that already exists in the codebase.
This is caught by the grep patterns section — include them.

**Tasks that are too large:**
A single task that would take 2+ days is not a task, it's a phase.
Break it down until each step takes under 2 hours.

**No testing strategy:**
Plans that don't specify what tests to write and what to mock are incomplete.
Tests are not an afterthought — they're part of every phase.

---

## Common Sections People Forget

1. **Idempotency** — Can this operation safely run twice? (critical for scheduled tasks and webhooks)
2. **Monitoring** — How will you know it's broken before a user reports it?
3. **Rollback** — If this goes wrong after deployment, how do you undo it?
4. **Local development** — Does this require a locally running dependency? How does a new dev set that up?
5. **Secrets management** — What new env vars are required? Where are they documented?
6. **Rate limits on YOUR system** — Not just on external APIs, but on your own API endpoints
7. **Migration backward compatibility** — Can old code run against the new schema during a rolling deploy?

---

## Plan Review Checklist

Before presenting plan in Phase 6, verify:

- [ ] Every section has specific file paths, not generic descriptions
- [ ] Every external call has error handling documented
- [ ] Every success criterion is measurable (number + threshold)
- [ ] Every phase has a gate condition
- [ ] Existing codebase patterns are referenced (not reinvented)
- [ ] Grep patterns section has 2+ useful patterns
- [ ] Complexity scores are assigned per section
- [ ] Resilience strategy covers at least the top 3 failure modes
- [ ] Testing strategy specifies what to mock
- [ ] Context loading suggestions list specific files
