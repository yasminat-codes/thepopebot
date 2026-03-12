# Changelog

All notable changes to task-master are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-03-02

Initial release of task-master.

### Added

**Core Skill (`SKILL.md`)**
- 6-phase workflow: Initialize → Interview → Research → Analysis → Generation → Finalization
- Tier 6 skill with post-tool hook enforcing 10-section task file completeness
- Claude Opus 4-6 model for expert-level task decomposition
- Inline context mode for continuous access to conversation history across phases
- Phase 3 preview-approve gate: no files written until user approves task list
- Anti-Rationalization Table with 10 entries covering common skipping excuses

**Task File Standard (`references/TASK-TEMPLATE.md`)**
- 10-section non-negotiable template (Header, Summary, Files to Read, Files to Modify,
  Checklist, Success Criteria, Testing, Task Management, Definition of Done)
- 8 writing rules enforced per-task (success criteria format, live API test logic,
  100-line limit, relative paths, full test suite as criterion 3, type hints, no secrets,
  summary describes code not behavior)
- Complete worked example: Rate Limiter Service (task 003)
- Anti-patterns table: 5 defects with correct approaches

**Dependency Engine (`references/DEPENDENCY-ENGINE.md`)**
- Topological sort algorithm for dependency graph building
- `BlockedBy: [NNN, NNN]` syntax specification
- Plan reading order used as tiebreaker for same-depth tasks
- Sub-task numbering convention (005a, 005b) for split tasks

**Testing Standards (`references/TESTING-STANDARDS.md`)**
- Three-subsection format: Unit Tests, Integration Tests, Live API Tests
- .env key detection logic for live vs BLOCKED test decisions
- `@pytest.mark.live` convention for live API test marking
- `# BLOCKED: {KEY} not in .env` stub format

**Research Agents**
- `agents/codebase-scanner.md` — Explore/sonnet agent for parallel codebase research
- `agents/grep-mcp-researcher.md` — general-purpose/haiku agent for GREP MCP pattern research

**Circuit Breaker (`references/CIRCUIT-BREAKER.md`)**
- 3-failure threshold before circuit opens
- 5-minute cooldown between open → half-open transitions
- State file at `.claude/circuit-breakers/grep-mcp.json`
- Graceful degradation to local-only research when open

**Memory System (`references/LEARNING-PATTERNS.md`)**
- Preference persistence at `.claude/memory/task-master.md`
- `task_depth: lean | default | thorough` preference key
- Applied automatically on Phase 0 startup
- Saved when user gives "too detailed" or "too vague" feedback

**Quality Gates (`references/QUALITY-GATES.md`)**
- 6-phase gate table (each phase has a blocker gate before proceeding)
- `hooks/post-tool.sh` validates each task file immediately after write
- `scripts/validate-tasks.sh` validates full directory before Phase 5 completes

**Validation Script (`scripts/validate-tasks.sh`)**
- Standalone bash script, callable independently of task-master
- Checks: all 10 required sections present, BlockedBy syntax valid,
  all BlockedBy references resolve to existing files
- Exit 0 = clean, exit 1 = failures listed with file names and issue descriptions

**Fixtures and Tests**
- `tests/fixtures/sample-plan-simple/plan.md` — 3-section rate limiter plan for happy path testing
- `tests/fixtures/sample-plan-large/plan.md` — 20-section Niche Scout plan for large-plan pressure testing
- `tests/test-cases.md` — 5 pressure test scenarios (4 adversarial + 1 happy path)
- `tests/integration-tests.md` — 4 end-to-end integration tests

**Documentation**
- `docs/USAGE.md` — Quick start, invocation options, phase descriptions, common workflows
- `docs/EXAMPLES.md` — 2 worked examples (simple 3-task + large 22-task with sub-tasks)
- `docs/TROUBLESHOOTING.md` — 6 common issues with diagnostics and fixes
- `plans/IMPLEMENTATION.md` — Design rationale (tier choice, context mode, model, agents,
  template sections, dependency engine, circuit breaker threshold)
- `plans/DECISIONS.md` — 5 ADRs (line limit, naming, TaskCreate timing, TASK-LOG location,
  validate-tasks.sh as separate script)
- `README.md` — Skill overview, pipeline position, reference file table, version history

### Architecture

- 2 research agents (parallel dispatch in Phase 2)
- 10 reference files
- 1 post-tool hook
- 1 validation script
- Total: ~17 files, ~2,800 lines
