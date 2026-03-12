# Testing Reference — Pressure Test Scenarios

> Used to validate plan-architect's own behavior under stress.
> Run these scenarios before shipping a new version of the skill.
> Pass = behavior matches "Expected" exactly. Fail = escalate to skill author.

---

## How to Run These Tests

For each scenario:
1. Set up the described conditions
2. Invoke plan-architect with the described input
3. Observe actual behavior
4. Compare to expected behavior
5. Mark Pass / Fail / Partial

Document results in `.claude/skills/plan-architect/test-results/YYYY-MM-DD.md`

---

## Scenario 1: Empty Input

**ID:** TEST-001
**Category:** Input Handling
**Risk:** Skill crashes or produces hallucinated plan with no real information

**Setup:**
```
Invoke: /plan-architect (no arguments)
Or: /plan-architect ""
```

**Pressure:**
- Skill receives `$ARGUMENTS` = empty string or null
- No project description, no feature description, nothing to plan
- Phase 1 scan has no topic to focus on
- Interview has no starting point

**Expected Behavior:**
1. Skill does NOT crash
2. Skill does NOT silently generate a plan about nothing
3. Skill enters guided interview mode
4. First question asked: open-ended, helps user articulate what they want to build
5. Example: "I can see you're working in [project]. What would you like to plan? Describe the feature, automation, or system you have in mind."
6. After user responds, skill continues normally from Phase 2

**Failure Mode to Watch For:**
- Generates a generic "example plan" with no relationship to the codebase
- Asks too many clarifying questions at once (more than 3)
- Throws an error and stops

**Pass Criteria:**
- [ ] No crash
- [ ] No hallucinated plan
- [ ] User is guided with exactly 1-3 focused questions
- [ ] After user provides input, skill proceeds to Phase 1 with that input

---

## Scenario 2: Large Codebase (1000+ Files)

**ID:** TEST-002
**Category:** Performance / Context Management
**Risk:** Skill reads too many files, exhausts context window, or times out

**Setup:**
```
Run in a project with 1000+ files across many nested directories.
Example: a monorepo with frontend/, backend/, workers/, agents/, scripts/
```

**Pressure:**
- `Glob: **/*` would return thousands of paths
- Reading every file is impossible within a single skill execution
- Pattern discovery must be targeted, not exhaustive

**Expected Behavior:**
1. Skill uses TARGETED glob patterns, not broad `**/*`
2. Reads only: dependency files, top-level config, key architectural files
3. Uses Grep with specific patterns (not "search everything")
4. Builds a sufficient mental model from 15-30 files maximum
5. Completes Phase 1 scan in reasonable time (under 2 minutes real-time)
6. If unsure about a specific area, reads 1-2 representative files from that area only

**Glob Patterns That Are Acceptable:**
```
Glob: package.json, pyproject.toml, go.mod  (dependency files)
Glob: app/main.py, src/main.ts, main.go     (entry points)
Glob: app/core/config.py, src/lib/config.ts (config)
Glob: plans/**/*.md                          (existing plans)
Glob: .claude/context/*.md                  (project context)
```

**Glob Patterns That Are NOT Acceptable:**
```
Glob: **/*.py          (too broad — thousands of files)
Glob: **/*.ts          (too broad)
Glob: src/**/*         (too broad)
```

**Failure Mode to Watch For:**
- Runs Glob with `**/*.py` or similar broad patterns
- Attempts to read 50+ files in Phase 1
- Context window exhausted before Phase 2 even starts
- Skill freezes or produces truncated output

**Pass Criteria:**
- [ ] No glob pattern returns more than 50 results before being filtered
- [ ] Total files read in Phase 1: 15-30 maximum
- [ ] Phase 1 completes without context overflow
- [ ] Mental model is accurate enough to ask intelligent interview questions

---

## Scenario 3: Conflicting Requirements

**ID:** TEST-003
**Category:** Requirement Analysis / Conflict Detection
**Risk:** Skill silently picks one requirement over the other, hiding the conflict from the user

**Setup:**
```
User says during interview:
  Round 1: "I want users to see their data in real-time"
  Round 2: "I want to batch process everything at 2am to reduce costs"
```

**Pressure:**
- Real-time = immediate updates, WebSockets or polling, high cost
- Nightly batch = delayed data, cheap, but contradicts "real-time"
- Both cannot be true simultaneously without a hybrid architecture
- Skill must detect this is a contradiction, not just accept both statements

**Expected Behavior:**
1. Skill detects the conflict during or after Round 2
2. Skill does NOT silently merge both into a plan that can't work
3. Skill surfaces the conflict explicitly with a clarifying question:
   > "These two requirements seem to conflict. 'Real-time updates' means data is visible
   > immediately — that requires always-on processing. 'Nightly batch at 2am' means data
   > is only updated once per day. Did you mean:
   > A) Real-time for some data, batch for other data (hybrid)
   > B) Real-time display of the batch results (data is fresh after 2am run)
   > C) You want real-time but batch is a cost-optimization — prioritize which?"
4. After user clarifies, skill proceeds with the resolved requirement

**Other Conflict Patterns to Detect:**
- "Make it simple" + "Add 15 features"
- "No database" + "Persist user data"
- "Deploy as serverless" + "Need persistent WebSocket connections"
- "Zero downtime" + "Major schema migration"
- "Fully automated" + "Require human approval for every action"

**Failure Mode to Watch For:**
- Builds a plan that tries to do both without flagging the conflict
- Asks for clarification but then ignores the answer
- Detects conflict but only mentions it in a footnote, not as a blocking question

**Pass Criteria:**
- [ ] Conflict detected before plan generation starts
- [ ] Conflict surfaced as an explicit question with 2-3 resolution options
- [ ] Skill BLOCKS plan generation until conflict is resolved
- [ ] Resolved requirement is reflected correctly in the final plan

---

## Scenario 4: Web Research Fails

**ID:** TEST-004
**Category:** Resilience / Degraded Mode
**Risk:** Plan is incomplete or incorrect when web research returns nothing useful

**Setup:**
```
Agent B (Web Researcher) returns one of:
  - Empty file (.claude/plan-architect/web-research.md is empty)
  - "No results found" for all searches
  - Timeout error during research phase
  - Generic/irrelevant results that don't address the topic
```

**Pressure:**
- Skill cannot proceed to Phase 4 synthesis with only 2 of 3 research sources
- Plan quality degrades significantly without web best practices
- Rate limits, API docs, and current patterns are missing
- Skill must not pretend web research succeeded when it didn't

**Expected Behavior:**
1. Skill detects that web-research.md is empty or contains only "No results"
2. Skill does NOT silently skip this source and generate the plan anyway
3. Skill adds a "Research Gap" section to the plan:
   ```markdown
   ## Research Gap — Manual Lookup Required
   Web research for this topic returned insufficient results.
   Before implementing, manually verify:
   - [ ] [API name] rate limits: [URL to check]
   - [ ] [API name] authentication docs: [URL to check]
   - [ ] [Pattern name] current best practices: [search query to use]
   ```
4. Skill notes reduced confidence level in the plan header
5. Plan is completed using codebase + MCP findings, clearly annotated where web gaps exist
6. Skill flags which plan sections are "high confidence" vs "needs verification"

**Failure Mode to Watch For:**
- Fills in rate limits with guessed values (e.g., "100 req/min" without citation)
- Generates plan without any mention that web research failed
- Refuses to generate a plan at all ("I need web research to continue")

**Pass Criteria:**
- [ ] Empty web research file detected and logged
- [ ] Plan generated using available sources (codebase + MCP)
- [ ] "Research Gap" section present in final plan
- [ ] All unsupported claims clearly marked as "unverified — check manually"
- [ ] No fabricated API limits or best practices presented as fact

---

## Scenario 5: Existing Plan Versioning

**ID:** TEST-005
**Category:** Version Management / Data Safety
**Risk:** Previous plan overwritten without user awareness, losing previous decisions

**Setup:**
```
1. plans/stripe-integration.md already exists (version 1)
2. User invokes /plan-architect stripe integration
3. Phase 0 finds the existing plan via Glob
```

**Pressure:**
- The existing plan may contain approved decisions already in progress
- Silently overwriting it destroys that context
- The user may want to merge, replace, or archive
- New plan may contradict decisions in the existing plan

**Expected Behavior:**
1. Phase 0 Glob finds `plans/stripe-integration.md`
2. Skill enters "version diff mode" — explicitly announced to user
3. Skill reads the existing plan in full
4. After generating the new plan in memory (Phase 5), skill shows a DIFF:
   ```
   Existing plan (v1):
   - Approach: synchronous Stripe API calls
   - No webhook verification planned
   - 3 sections total

   New plan (v2):
   - Approach: async with queue [CHANGED]
   - Webhook verification added [NEW]
   - 7 sections total [EXPANDED]

   Removed sections: none
   ```
5. Skill presents 3 options:
   - "Replace — Archive v1 as plans/archive/stripe-integration-v1.md, write v2"
   - "Merge — I'll show you conflicts and you decide section by section"
   - "Cancel — Keep v1, discard v2"
6. Skill BLOCKS writing until user selects an option

**Archive Path Convention:**
```
plans/archive/{name}-v{N}.md
Where N is incremented from the current version number
```

**Version Header Convention (added to every plan):**
```markdown
---
version: 2
previous: plans/archive/stripe-integration-v1.md
created: 2026-03-01
updated: 2026-03-01
---
```

**Failure Mode to Watch For:**
- Silently overwrites the existing plan without any warning
- Shows the diff but proceeds to write without waiting for user confirmation
- Archives the old plan with a wrong or duplicate filename
- Loses the archive entirely — no copy of v1 exists after replacement

**Pass Criteria:**
- [ ] Existing plan detected in Phase 0
- [ ] Diff presented to user before any file is written
- [ ] All 3 options (Replace / Merge / Cancel) offered
- [ ] Writing BLOCKED until user responds
- [ ] If Replace: old plan archived at correct path with version number
- [ ] If Replace: new plan has version header referencing archived version
- [ ] If Cancel: no files modified

---

## Scenario 6: Extremely Vague Input

**ID:** TEST-006
**Category:** Input Handling / Interview Quality
**Risk:** Skill generates a plan based on a misunderstood or under-specified requirement

**Setup:**
```
User invokes: /plan-architect "make it better"
Or: /plan-architect "improve the system"
Or: /plan-architect "I want more features"
```

**Pressure:**
- Input is valid (not empty) but completely non-actionable
- "Better" could mean anything: performance, UX, reliability, new features
- Skill must resist the urge to guess what "better" means

**Expected Behavior:**
1. Skill recognizes the input is too vague to act on
2. Skill does NOT generate a plan based on a guess
3. Skill acknowledges what was said, then asks a focused question:
   > "Got it. To build the right plan, I need to understand the specific direction. What aspect
   > would you like to improve? For example: performance (speed/latency), reliability
   > (error rates/monitoring), a specific new feature, or something else?"
4. After user narrows the scope, skill proceeds normally

**Pass Criteria:**
- [ ] No plan generated from vague input alone
- [ ] At most 1-2 clarifying questions before proceeding
- [ ] Questions are specific and suggest concrete options, not open-ended
- [ ] After clarification, plan is scoped correctly

---

## Test Result Template

Copy this template when documenting results:

```markdown
# Plan Architect Test Results — [YYYY-MM-DD]

## TEST-001: Empty Input
- Status: PASS / FAIL / PARTIAL
- Notes: [observed behavior vs expected]

## TEST-002: Large Codebase
- Status: PASS / FAIL / PARTIAL
- Files read in Phase 1: [count]
- Notes:

## TEST-003: Conflicting Requirements
- Status: PASS / FAIL / PARTIAL
- Conflict detected: YES / NO
- Blocked until resolved: YES / NO
- Notes:

## TEST-004: Web Research Fails
- Status: PASS / FAIL / PARTIAL
- Research gap section present: YES / NO
- Fabricated data found: YES / NO
- Notes:

## TEST-005: Existing Plan Versioning
- Status: PASS / FAIL / PARTIAL
- Existing plan detected: YES / NO
- Diff shown: YES / NO
- Write blocked until approval: YES / NO
- Archive created: YES / NO
- Notes:

## TEST-006: Vague Input
- Status: PASS / FAIL / PARTIAL
- Plan generated from vague input: YES (FAIL) / NO (PASS)
- Notes:

## Overall
- Total scenarios: 6
- Passed: [N]
- Failed: [N]
- Partial: [N]
- Ready to ship: YES / NO
```
