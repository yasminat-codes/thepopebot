# task-master — Implementation Design Rationale
Version: 1.0.0 | Last updated: 2026-03-02

This document explains the architectural decisions behind task-master's design.
It answers "why" questions that the SKILL.md (the navigation hub) does not.

---

## Why Tier 6 (Not Tier 5)

Plan-architect is Tier 5. task-master is Tier 6. The jump is deliberate.

Tier 5 requires: parallel research agents, memory system, circuit breaker, SKILL.md ≤ 600 lines,
all content in references/, hooks optional.

task-master hits all of those and then adds two more requirements that push it to Tier 6:

1. **Post-tool hook (required, not optional):** The hook validates every task file immediately
   after it's written. This is a hard quality gate — if the hook fires and finds a missing
   section, the skill halts. This isn't graceful degradation; it's a blocking validation step
   that changes how the skill operates. Tier 6 requires hooks as a structural element.

2. **Ten reference files (8 is the Tier 5 maximum):** The plan parsing logic, dependency engine,
   testing standards, context injection, pipeline contract, edge cases, quality gates, circuit
   breaker, and learning patterns each deserve their own reference file. Cramming them into 8
   or fewer files would require either merging unrelated concerns or burying content in SKILL.md
   itself (violating the navigation-hub-only rule). Tier 6 explicitly accommodates 10+ references.

The CSO score of 9/10 and health score of 95/100 reflect that task-master is near the top
of Tier 6 — complex enough to warrant the tier, not gratuitously over-engineered.

---

## Why Inline Context (Not Fork)

Some Tier 6 skills use a fork model where a separate orchestrator process manages state.
task-master uses inline context instead. Reason: task-master needs continuous access to
the user's current working context — specifically, which plan was just reviewed, what
corrections the user made in Phase 1, and what .env keys were detected in Phase 0.

If task-master ran as a forked subprocess, it would need to serialize and pass all of
that context explicitly. Instead, inline context keeps the full conversation history
available throughout all 5 phases. The tradeoff is that the main context window carries
all research output from Phase 2 — but research results are summarized (not raw), and
the task files themselves are written to disk, not held in memory.

The inline choice also makes the preview-approve-write loop in Phase 3 seamless. The user
sees the preview table, responds inline, and task-master immediately proceeds or modifies
based on that response without any state serialization step.

---

## Why Opus (Not Sonnet)

Task quality matters more than speed here. The tasks task-master generates are consumed
by specs-to-commit and by human engineers. A poorly structured task file — vague success
criteria, missing file paths, incomplete testing section — creates downstream rework that
costs more time than the savings from using a faster model.

Opus is used specifically for Phase 3 (dependency graph building and task decomposition)
and Phase 4 (task file generation). These are the phases where expert judgment matters:
correctly identifying that "Section 9" is actually two tasks, not one; writing test function
names that map precisely to the implementation requirements; knowing which files to list in
"Files to Read Before Starting" based on what the plan actually touches.

The research agents (Phase 2) intentionally use sonnet and haiku — speed matters there
because they're doing pattern-matching work, not expert synthesis.

---

## Why Parallel Research Agents (Not Sequential)

Two reasons: context window size management and wall-clock time.

**Context window management:** If a single agent did all research (codebase + GREP MCP),
it would accumulate all results in one response, which then lands in task-master's main
context. By separating into two agents with different scopes, each returns a focused,
summarized result set. task-master merges the summaries, not the raw output.

**Wall-clock time:** Codebase scanning with the Explore subagent takes ~20-30 seconds on
a medium project. GREP MCP pattern research takes ~15-25 seconds. Sequential: ~50 seconds.
Parallel: ~30 seconds. For a 10-task plan, that 20-second saving compounds.

The circuit breaker design reinforces this: if GREP MCP is flaky, the codebase-scanner
still runs to completion. The skill degrades gracefully to local-only research without
any change to the codebase-scanner agent or the main skill logic.

---

## The TASK-TEMPLATE Design: Why 10 Sections (Not More, Not Fewer)

The 10 required sections were arrived at by working backwards from the failure modes of
poorly-generated tasks:

1. **Header** (Status, BlockedBy, EstimatedContextWindow) — needed by specs-to-commit for
   pipeline orchestration. Without it, the consumer can't determine execution order.

2. **Summary** — engineers need a 1-sentence orientation before reading the full task.
   Without it, context-switching mid-pipeline is disorienting.

3. **Files to Read Before Starting** — prevents engineers from starting implementation
   without loading the relevant context first. This was added after observing that tasks
   without this section led to engineers discovering wrong patterns mid-implementation.

4. **Files to Modify or Create** — explicit path table prevents "hunting" for the right file.
   The table format (Action, Path, What Changes) mirrors how engineers mentally model changes.

5. **Implementation Checklist** — atomic, verifiable steps with Success criteria per item.
   Without this, "done" is undefined and tasks stall.

6. **Success Criteria** — the 5-criterion pattern (importable, unit tests pass, all tests pass,
   no lint errors, service-specific) provides a repeatable definition of done.

7. **Testing** — three subsections (Unit, Integration, Live API) cover the full testing pyramid.
   A missing Testing section is the most common quality defect in manually-written tasks.

8. **Task Management** — the mv commands for _pending → _in-progress → _completed are included
   literally to eliminate cognitive load during implementation.

9. **Definition of Done** — final checklist that catches items the Implementation Checklist
   might miss (no print() statements, secrets from get_settings(), task file moved).

10-section minimum prevents padding (no section should be added "just in case"). 10-section
maximum prevents over-specification (tasks should describe what to build, not how to build it
at a line-by-line level).

---

## The Dependency Engine Design: Topological Sort Over Plan Reading Order

Plan sections appear in a logical reading order that is NOT necessarily the correct build
order. Example: a plan might describe the API routes before the database models, because
explaining the API first gives the reader context. But the build order must be: models first.

Topological sort on the dependency graph ensures that task 001 is always a task with zero
dependencies, task 002 either has no dependencies or only depends on 001, and so on. This
means specs-to-commit can walk the task list top-to-bottom and never encounter a task whose
dependencies aren't yet complete.

Reading order from the plan is used only as a tiebreaker when two tasks have the same
dependency depth. This preserves the plan author's intent while enforcing correct build order.

---

## The Circuit Breaker Choice: Why 3 Failures Not 1

The GREP MCP tool talks to an external service (GitHub search API). Transient errors are
common: network blips, rate limits, brief service unavailability. A threshold of 1 failure
would cause the circuit breaker to open on the first transient error, degrading every
subsequent task-master run to local-only research until the breaker is manually reset.

At 3 failures (within a short window), the circuit breaker distinguishes between transient
errors (usually self-resolving after 1-2 attempts) and persistent failures (the service is
down, or a quota is exhausted). The 5-minute cooldown gives transient issues time to resolve.

The 3-failure threshold matches what Redis and Kubernetes use for their respective circuit
breaker and readiness probe defaults — a well-tested operational value for short-lived
network dependencies.
