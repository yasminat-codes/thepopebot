# task-master — Architecture Decision Records
Version: 1.0.0 | Last updated: 2026-03-02

Each ADR documents a choice made during design, the alternatives considered, and the
reasoning. Use this to understand constraints before proposing changes.

---

## ADR Table

| # | Decision Area | Option Chosen | Option Rejected | Status |
|---|--------------|---------------|----------------|--------|
| 1 | Task file line limit | Strict 100-line cap | Flexible / advisory | Accepted |
| 2 | Task file naming | `001` zero-padded numeric | UUID or sequential (1, 2, 3) | Accepted |
| 3 | TaskCreate timing | Inline at Phase 4 start per task | Separate task management phase | Accepted |
| 4 | TASK-LOG.md location | `tasks/` root | `tasks/_pending/` | Accepted |
| 5 | validate-tasks.sh | Separate standalone script | Inline check in Phase 5 | Accepted |

---

## ADR 1: Strict 100-Line Task Limit

**Decision:** Every generated task file is capped at approximately 100 lines (max 120).
If a task would exceed 100 lines, it is split into sub-tasks (NNNa, NNNb).

**Option rejected:** Flexible limit where task-master exercises judgment about whether a
longer task is appropriate for its complexity.

**Why strict:**

Context overflow is a silent failure mode. A 150-line task looks fine in a text editor
but will cause the LLM implementing it (in specs-to-commit or manually) to lose context
of the earlier sections by the time it reaches the testing section. The result: incomplete
implementations, missing test cases, or forgotten lint steps.

A strict limit forces task decomposition at authoring time, not implementation time.
The cost is a few extra task files. The benefit is that every task fits in a single
context window with room for the implementation code itself.

Flexible limits rely on judgment calls that are inconsistent across runs. "This task is
complex but coherent" is a rationalization, not a criterion. 100 lines is.

**Trade-offs accepted:** A few tasks will feel artificially split. The sub-task naming
(005a, 005b) adds minor overhead to the task list. Both are preferable to context overflow.

---

## ADR 2: Zero-Padded Numeric Naming (`001`)

**Decision:** Task files are named `001-kebab-title.md`, `002-kebab-title.md`, etc.
Numbers are zero-padded to 3 digits.

**Options rejected:**

- **UUID:** `7f3a9b2c-rate-limiter-service.md` — not human-readable, not sortable in
  filesystem explorers, cannot be communicated verbally ("I'm working on 7f3a9b2c" vs
  "I'm working on 007").

- **Sequential without padding (1, 2, 3):** Filesystem sort orders `10` before `2` in
  most shells and file explorers. Zero-padding to 3 digits (`001`, `002`, `010`) ensures
  alphabetical sort == dependency order.

**Why numeric:**

specs-to-commit reads `BlockedBy: [001, 005]` and resolves those to files by glob pattern.
A numeric namespace makes the glob trivial: `tasks/_pending/001-*.md`. UUIDs or arbitrary
strings would require an index file. 3-digit zero-padding handles up to 999 tasks — more
than any real plan will ever produce.

Sub-tasks (005a, 005b) sort correctly because `005a` < `005b` < `006` in ASCII order.

---

## ADR 3: TaskCreate Inline at Phase 4

**Decision:** TaskCreate is called at the start of generating each task in Phase 4,
immediately before writing the task file.

**Option rejected:** A dedicated task management phase (Phase 4.5 or Phase 6) that
creates all task records at once after all files are generated.

**Why inline:**

A separate phase would create a temporal gap between "task file exists on disk" and
"task record exists in task management system." If task-master halts mid-generation
(network error, user interrupt), the gap creates an inconsistent state: some files are
written but not recorded, or all records exist but only some files are written.

Inline TaskCreate keeps the file and record in sync: if the file write succeeds, the
record is created immediately after. If task-master halts before writing a file, neither
the file nor the record exists. Consistent failure modes are easier to recover from.

The inline approach also keeps the implementation simpler: no need for a reconciliation
step that checks which files exist vs which records exist.

---

## ADR 4: TASK-LOG.md at `tasks/` Root

**Decision:** TASK-LOG.md is written to `tasks/TASK-LOG.md`, not inside any subdirectory.

**Option rejected:** Writing TASK-LOG.md to `tasks/_pending/TASK-LOG.md`.

**Why root:**

TASK-LOG.md is a registry, not a task. It documents the provenance and metadata of all
generated tasks across the entire `tasks/` tree. Its scope spans `_pending/`,
`_in-progress/`, and `_completed/` — it would be semantically wrong to place it inside
one of those subdirectories.

Placing it in `_pending/` would also risk it being discovered as a task file by tools that
glob `tasks/_pending/*.md`. validate-tasks.sh and specs-to-commit both glob that directory.
A TASK-LOG.md that fails section validation would cause false validation failures.

At the root, TASK-LOG.md is unambiguously a registry artifact, not a work item.

---

## ADR 5: validate-tasks.sh as Separate Script

**Decision:** Task validation logic lives in `scripts/validate-tasks.sh`, a standalone
bash script callable independently of task-master.

**Option rejected:** Running validation as an inline Phase 5 check — a series of Grep
and Read calls within the skill itself.

**Why separate:**

Users need to run validation independently. After manually editing a task file, after
moving tasks between directories, after debugging a dependency issue — in all these cases,
the user wants to validate without re-running the entire task-master generation pipeline.

A standalone script can be run in a terminal with a single command. An inline skill phase
requires re-invoking the full skill, which takes 2-5 minutes and asks questions.

The script is also easier to test in isolation (see integration-tests.md Test I4). A skill
phase cannot be tested without invoking the full skill; a bash script can be called directly.

The separation also enforces that validate-tasks.sh has a well-defined, stable interface:
takes a directory path, exits 0 or 1, writes to stdout. Any change to that contract is
visible and deliberate. An inline check buried in Phase 5 has no such contract.
