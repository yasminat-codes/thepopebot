# Revamp Mode — Updating Existing Plans

> Activated when $ARGUMENTS points to an existing plan file or user says
> "revamp", "update", "improve", "revisit", or "redo" with a plan reference.
> Revamp mode is a focused, efficient update cycle — NOT a full rebuild.

---

## Revamp vs Create

| Aspect | CREATE mode | REVAMP mode |
|--------|-------------|-------------|
| Input | Feature idea / description | Existing plan file path |
| Interview | Full 3-round, 5-10 questions | Focused 1-2 rounds on what changed |
| Research | All 3 agents, broad search | Targeted agents on changed areas only |
| Output | New plan from scratch | Updated plan with version bump + diff |
| Archive | N/A | Old plan archived before overwrite |

---

## Revamp Phase Flow

### Phase 0R: Initialize Revamp

1. Read the existing plan file completely
2. Parse its metadata (version, date, complexity, status)
3. Create `plans/archive/{name}-v{N}.md` backup immediately
4. Build a section inventory:

```
Section Inventory:
| # | Section | Lines | Last Changed | Status |
|---|---------|-------|-------------|--------|
| 1 | System Overview | 45 | v1 original | ? |
| 2 | Architecture Design | 82 | v1 original | ? |
| ... | ... | ... | ... | ... |
```

Present the inventory to user via AskUserQuestion:
- "Which sections need updating?" (multiSelect: true)
- Options: each section name + "Add new section" + "Full rewrite"

If "Full rewrite" → switch to CREATE mode entirely.

### Phase 1R: Context Delta

Instead of scanning the entire codebase from scratch:

1. Read the plan's "Context Loading Suggestions" section — these are the files that matter
2. Check if those files have changed since the plan was written:
   ```bash
   git log --since="[plan-date]" --oneline -- [file-list]
   ```
3. Scan ONLY changed files for new patterns
4. Check if new files have been added that are relevant:
   ```bash
   git log --since="[plan-date]" --diff-filter=A --name-only
   ```
5. Read any new plans in plans/ that might affect this one

Output: A **delta report** — what's changed in the codebase since this plan was written.

### Phase 2R: Focused Interview

Instead of the full 3-round interview, ask targeted questions:

**Round 1: What Changed? (2-3 questions)**
Present the existing plan's summary, then ask:

AskUserQuestion:
- "What triggered this revamp?" (options: "Requirements changed", "Found issues during implementation", "New information/context", "Plan was incomplete")
- "What's the most important thing to fix/improve?" (free text)

**Round 2: Scope Check (1-2 questions)**
Based on the sections user selected for update:

AskUserQuestion:
- "Should the architecture change, or just the implementation details?"
- "Are there new integrations or services since the original plan?"

Skip Round 3 (edge cases) unless the architecture is changing.

### Phase 3R: Targeted Research

Only dispatch agents for the sections being updated:

| Section Being Updated | Agents to Dispatch |
|----------------------|-------------------|
| Architecture Design | Agent A (codebase) + Agent B (web) |
| Integration Map | Agent B (web) for API docs + Agent A (codebase) for new integrations |
| Resilience Strategy | Agent A (codebase) for new error patterns |
| Database Design | Agent A (codebase) for schema changes |
| Implementation Logic | Agent A (codebase) for new patterns |
| Any section | Agent C (MCP) always runs — check for new decisions |

If only 1-2 sections are updating, you may use 1-2 agents instead of all 3.
Agent C (MCP context) ALWAYS runs — past decisions affect revamps.

### Phase 4R: Diff Synthesis

For each section being updated:

1. Read the original section from the archived plan
2. Apply new research findings and interview answers
3. Generate the updated section
4. Create a semantic diff:

```markdown
## Section 3: Integration Map — CHANGES

### Added
+ Stripe webhook integration (new requirement from interview)
+ Rate limit for Google Drive API: 1000 req/100sec (from web research)

### Modified
~ Reddit API: Updated rate limit from 30/min to 60/min (web research)
~ OpenRouter: Added Gemini as 5th fallback provider (codebase change)

### Removed
- Removed Twilio integration (user confirmed no longer needed)

### Unchanged
= Slack integration (no changes needed)
= Database connection patterns (still valid)
```

### Phase 5R: Rebuild Plan

1. Start with the archived plan as the base
2. Replace only the updated sections
3. Keep unchanged sections exactly as they were
4. Bump the version number in metadata
5. Update the "Last Modified" date
6. Add a "Revision History" section at the bottom:

```markdown
## Revision History
| Version | Date | Changes |
|---------|------|---------|
| 1 | 2026-02-15 | Initial plan |
| 2 | 2026-03-01 | Updated integrations, revised resilience strategy |
```

### Phase 6R: Review with Diff

Present the plan WITH a clear diff view:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN REVAMP — {plan-name} v{N} → v{N+1}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sections updated: 3 of 10
Sections unchanged: 7 of 10
Complexity change: 3.2 → 3.8 (+0.6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Full diff per changed section]
```

AskUserQuestion:
- "Approve — Save updated plan"
- "Modify — I want changes to the revamp"
- "Revert — Keep the original plan"

### Phase 7R: Write Updated Plan

1. Write to the SAME filename (overwrite)
2. Verify the archived version exists in plans/archive/
3. Run scripts/validate-plan-output.sh — same validation as CREATE mode
4. The updated plan must pass ALL the same checks as a new plan

### Phase 8R: Handoff

Same as CREATE mode but also mention:
- "Previous version archived at plans/archive/{name}-v{N}.md"
- "To revert: copy the archive back to plans/{name}.md"

---

## Revamp Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Rewriting unchanged sections | Only touch what was selected for update |
| Skipping the archive step | ALWAYS archive before overwriting. Non-negotiable. |
| Not checking codebase delta | The codebase may have changed — always check git log |
| Ignoring the original plan's decisions | Read the Design Decisions section first — honor past choices unless explicitly overriding |
| Full rewrite disguised as revamp | If 7+ of 10 sections need changes, switch to CREATE mode |

---

## Revamp Interview Quick Reference

For speed, use these focused question templates:

**"What broke?"** → Points to implementation gaps, missing error handling, wrong assumptions
**"What's new?"** → New integrations, new requirements, new constraints
**"What's obsolete?"** → Removed features, deprecated APIs, changed architecture
**"What was wrong?"** → Incorrect assumptions, bad estimates, missing dependencies

Each answer maps directly to which plan sections need updating.
