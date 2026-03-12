# DEPENDENCY-ENGINE.md — Task Dependency Detection and Ordering

This document defines how task-master detects dependencies between tasks, expresses
them in task file frontmatter, builds the dependency graph, and assigns final task
numbers in the correct order.

---

## Section 1: Dependency Detection Rules

Apply these rules in order. The first matching rule wins. A task that matches
multiple rules gets all detected dependencies merged.

**Rule 1: Model/service creation dependency**
Task B depends on Task A when:
- Task B uses a Python class or function that Task A's checklist says it will create
- Signal: Task B's "Files to Read" or implementation steps reference a file listed
  in Task A's "Files to Create"

**Rule 2: Import dependency**
Task B depends on Task A when:
- Task B's implementation steps would produce `from app.X import Y`
- Task A's "Files to Create" includes `app/X.py` (the module being imported)

**Rule 3: "Add X to Y" dependency**
Task B depends on Task A when:
- Task B's summary reads "Add {feature} to {component}" or "Wire {service} into {router}"
- The component or router being modified is created (not just modified) in Task A

**Rule 4: Test task dependency**
Test tasks always depend on the implementation tasks they test:
- Any task whose title starts with "Test" or whose file is `tests/...` depends on
  all tasks that create the files under test
- Never number a test task before the implementation task it covers

**Rule 5: Integration dependency**
An integration task (one that wires multiple components together) depends on
all component tasks it references:
- Signal: Task B's "Files to Modify" lists files created in 2+ other tasks
- Result: Task B blockedBy all tasks that create those files

---

## Section 2: blockedBy Syntax

The `BlockedBy` field in task file frontmatter uses zero-padded 3-digit task numbers.

### Formats

No dependencies (canonical — matches wave_0 detection):
```
**BlockedBy:** —
```

Single dependency:
```
**BlockedBy:** [001]
```

Multiple dependencies:
```
**BlockedBy:** [001,003]
```

### Rules

- Always use task numbers, never task titles or file names
- Comma-separated with no space after the comma: `[001,003]` not `[001, 003]`
- The field must always be present — never omit it, even when empty
- Numbers refer to the final assigned task numbers, not plan section order
- If a dependency's task number is not yet assigned, use a placeholder like `[TBD-models]`
  and resolve it after the full graph is built

---

## Section 3: Dependency Graph Building Algorithm

Follow these steps in order. Do not skip ahead.

**Step 1: List all plan sections in reading order.**

Extract every section that passed the "Implementation Section" filter from PLAN-ANALYSIS.md.
Label each with a temporary ID based on its position: `S1`, `S2`, `S3`, etc.

**Step 2: For each section, identify what it creates and what it consumes.**

For every section `Si`, record:
- `creates(Si)`: list of files, classes, or symbols this section will produce
- `consumes(Si)`: list of files, classes, or symbols this section needs to already exist

**Step 3: Draw dependency edges.**

For each pair `(Si, Sj)`:
- If `consumes(Sj)` intersects `creates(Si)`: draw edge `Sj → Si` (Sj depends on Si)
- Collect all edges into a directed graph

**Step 4: Topological sort.**

Find the topological ordering of the graph:
1. Find all root nodes (nodes with no incoming edges = no dependencies)
2. These are layer 0. Remove them and repeat.
3. New root nodes are layer 1. Remove and repeat.
4. Continue until all nodes are assigned a layer.

If a cycle is detected: break it at the integration task (the task with the most
dependencies) and note the cycle in that task's "Files to Read" section as a comment.

**Step 5: Assign final task numbers.**

Assign numbers within each layer in plan reading order:
- Layer 0 tasks get the lowest numbers (001, 002, ...)
- Layer 1 tasks get the next numbers
- Layer N tasks get the highest numbers
- Test tasks always land in the final layer

---

## Section 4: Worked Example

**Scenario:** FastAPI project adding a new agent service with database persistence.

**Plan sections (reading order):**

```
S1: Data models (AgentRun, AgentResult)
S2: Database migration (add agent_runs table)
S3: AgentService class
S4: API routes for /agents/run
S5: Tests (unit + integration)
```

**creates/consumes analysis:**

```
S1 creates: app/models/agent.py, AgentRun, AgentResult
S1 consumes: app/models/base.py (already exists, no task dep)

S2 creates: alembic/versions/xxx_add_agent_runs.py
S2 consumes: AgentRun (from S1) — needs model to write migration

S3 creates: app/services/agent_service.py, AgentService
S3 consumes: AgentRun (from S1), AgentResult (from S1), DB session (exists)

S4 creates: routes wired in app/api/routes/agents.py
S4 consumes: AgentService (from S3)

S5 creates: tests/unit/test_agent_service.py, tests/integration/test_agent_routes.py
S5 consumes: AgentService (from S3), routes (from S4)
```

**Dependency edges:**

```
S2 → S1   (migration needs model)
S3 → S1   (service needs model)
S4 → S3   (routes need service)
S5 → S3   (tests need service)
S5 → S4   (integration tests need routes)
```

**Dependency graph (ASCII):**

```
S1 (models)
├── S2 (migration)
└── S3 (service)
    ├── S4 (routes)
    │   └── S5 (tests)
    └── S5 (tests)
```

**Topological layers:**

```
Layer 0: S1
Layer 1: S2, S3
Layer 2: S4
Layer 3: S5
```

**Final task number assignment:**

```
001-agent-models.md         BlockedBy: []
002-agent-migration.md      BlockedBy: [001]
003-agent-service.md        BlockedBy: [001,002]
004-agent-routes.md         BlockedBy: [003]
005-agent-tests.md          BlockedBy: [003,004]
```

**Full frontmatter for 003-agent-service.md:**

```markdown
# Task 003: Implement AgentService
**Status:** PENDING
**BlockedBy:** [001,002]
**EstimatedContextWindow:** medium
```

---

## Section 5: Ordering Rules

Apply these rules when the topological sort produces ties (two tasks at the same layer
with no dependency between them):

**Rule A: Infrastructure before logic.**
Tasks touching `app/config.py`, `app/models/`, `alembic/`, or `app/database.py` always
come before tasks touching `app/services/`, `app/api/`, or `app/workers/`.

**Rule B: Logic before routes.**
Tasks creating service classes come before tasks creating routes that import those services.

**Rule C: Routes before tests.**
Tasks creating or modifying API routes come before integration test tasks that call those routes.

**Rule D: Test tasks always last.**
Any task whose primary output is files under `tests/` gets the highest task numbers,
regardless of plan reading order.

**Rule E: When truly independent, preserve plan reading order.**
If two tasks share no dependency and neither is infrastructure/logic/routes/tests,
assign numbers in the order they appear in the plan.

**Summary of priority order for numbering:**

```
1. Infrastructure   (config, models, migrations, database)
2. Core logic       (services, agents, workers)
3. Integration      (routes, webhooks, schedulers)
4. Tests            (unit, integration, live)
```

Never number in plan reading order if doing so would violate a dependency — a task
numbered lower than its dependency is invalid and will cause implementation failures.
