# Rules Injection Reference

This file defines how task-master discovers `.claude/rules/` files and intelligently
injects relevant rules into every generated task file.

---

## Section 1: Rules Discovery Protocol

Run during **Phase 0 Initialize**, before any task is generated.

### Step 1 — Discover project-scoped rules

```
Glob: .claude/rules/*.md          → project-scoped rules
Glob: .claude/rules/**/*.md       → nested rule subdirectories
```

### Step 2 — Discover global rules

```
Glob: ~/.claude/rules/*.md        → user-global rules (apply to all projects)
```

### Step 3 — Build rules map

For each file found, record:
- `path` — relative path for injection (e.g., `.claude/rules/code-quality.md`)
- `filename` — used for matching (e.g., `code-quality`)
- `keywords` — extracted from filename + first 3 headings (Grep first 20 lines)
- `scope` — `always` | `conditional` (see Section 2)

Store the rules map for use during Phase 4 task generation.

---

## Section 2: Rules Matching Matrix

### Always-include rules (scope: always)

These go into every task file regardless of content.

| Rule File                       | Reason always included                                         |
|---------------------------------|----------------------------------------------------------------|
| `.claude/rules/task-management.md` | Every task has a lifecycle: _pending → _in-progress → _completed |
| `.claude/rules/code-quality.md`    | Every task touches code: ruff, mypy, async I/O, 120 char limit |
| `.claude/rules/context-loading.md` | Every task must read before writing                            |
| `.claude/rules/self-healing.md`    | Every task logs mistakes to MISTAKES.md when bugs are found    |

If none of these files exist in `.claude/rules/`, skip gracefully (do not error).

### Conditional rules (scope: conditional)

Include based on task content matching the keywords column.

| Rule File                               | Include when task contains these signals                                                     |
|-----------------------------------------|----------------------------------------------------------------------------------------------|
| `.claude/rules/research-first.md`       | keywords: "new service", "integration", "client", "third-party", "new pattern", "new agent" |
| `.claude/rules/fastapi-coolify-rules.md`| keywords: "fastapi", "uvicorn", "Dockerfile", "backend", "app/main.py", "deploy"            |
| `.claude/rules/nextjs-coolify-rules.md` | keywords: "nextjs", "next.js", "frontend", "react", "typescript", "Dockerfile"              |
| `.claude/rules/coolify-deployment-rules.md` | keywords: "deploy", "Dockerfile", "container", "production", "coolify", "docker"        |
| any other rule file found               | Include if filename keywords appear in the task summary or file paths                        |

### Matching algorithm

```python
def should_include_rule(rule_path, task_summary, task_files):
    # Extract keywords from rule filename (hyphen → space split)
    rule_keywords = rule_path.stem.replace("-", " ").split()

    # Build search corpus from task content
    corpus = (task_summary + " " + " ".join(task_files)).lower()

    # Include if any keyword from rule filename matches
    return any(kw in corpus for kw in rule_keywords)
```

**When in doubt, include** — a false positive (extra rule included) costs 1 line.
A false negative (missing rule) causes quality defects in implementation.

---

## Section 3: Task File Injection Format

Add a `## Relevant Rules` section to every task file, immediately after
`## Files to Read Before Starting`.

### Format

```markdown
## Relevant Rules

<!-- Always include -->
- `.claude/rules/task-management.md` — task lifecycle: pending → in-progress → completed
- `.claude/rules/code-quality.md` — async I/O, ruff, mypy, 120 char limit, no print()
- `.claude/rules/context-loading.md` — read the file fully before editing; check MISTAKES.md

<!-- Conditional: include only if matched -->
- `.claude/rules/research-first.md` — search codebase + GREP MCP before writing new service
- `.claude/rules/fastapi-coolify-rules.md` — health endpoint, Pydantic Settings, Dockerfile pattern
```

### Rules to omit

- Do NOT include rules that have zero relevance to the task (e.g., `nextjs-coolify-rules.md`
  on a pure Python database migration task)
- Do NOT reproduce rule content inline — reference the file only
- Do NOT list more than 6 rules — if more match, include the 6 most specific

### When no `.claude/rules/` directory exists

Skip the section entirely. Do not include an empty `## Relevant Rules` heading.

---

## Section 4: Global Rules Handling

Rules found in `~/.claude/rules/` are user-global and apply to all projects.

Apply the same matching matrix from Section 2, but use the `~/.claude/rules/` path in the
reference. Example:

```markdown
- `~/.claude/rules/coolify-deployment-rules.md` — Coolify deployment checklist (non-negotiable)
```

Global rules that duplicate project-scoped rules: keep the project-scoped version only.

---

## Section 5: Validation

When `hooks/post-tool.sh` validates a generated task file, it checks:

1. If `.claude/rules/` directory exists → task file MUST have `## Relevant Rules` section
2. Always-include rules MUST be present if their files exist on disk
3. Conditional rules MUST be present if their keywords match the task summary

Failure mode: warn-only (same as all other hook checks). Do not block generation.
