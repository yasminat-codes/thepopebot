# task-master — Troubleshooting Guide
Version: 1.0.0 | Last updated: 2026-03-02

---

## Quick Reference

| Symptom | Section |
|---------|---------|
| "No plans found" at startup | Issue 1 |
| "GREP MCP circuit breaker open" warning | Issue 2 |
| Task file missing a section | Issue 3 |
| validate-tasks.sh exits 1 for broken dependency | Issue 4 |
| Delivery report shows BLOCKED tests | Issue 5 |
| Tasks are too detailed or too vague | Issue 6 |

---

## Issue 1: "No plans found. Run /plan-architect first."

**What it means:** task-master scanned both `plan/` and `plans/` directories (relative to
the project root) and found zero `.md` files.

**Diagnostic steps:**

```bash
# Check if the directories exist
ls plan/ 2>/dev/null || echo "plan/ does not exist"
ls plans/ 2>/dev/null || echo "plans/ does not exist"

# Check if plan files are in an unexpected location
find . -name "*.md" -path "*/plan*" 2>/dev/null | head -20
```

**Common causes and fixes:**

| Cause | Fix |
|-------|-----|
| `/plan-architect` was never run | Run `/plan-architect <description>` first |
| Plan files are in `plan/archive/` (moved by plan-architect revamp) | Run `/plan-architect` again, or move the file back to `plan/` |
| Running task-master from a subdirectory | `cd` to project root (where `pyproject.toml` is), then re-run |
| Plan files have a non-`.md` extension | Rename to `.md` format |

**What plan-architect creates:**

- Single-file plans: `plans/feature-name.md`
- Folder plans (v1.2.0+): `plans/feature-name/PLAN.md` (plus `01-overview.md`, `02-database.md`, etc.)

If you have a folder plan, pass the path explicitly: `/task-master plans/niche-scout/PLAN.md`

---

## Issue 2: "GREP MCP circuit breaker open"

**What it means:** The GREP MCP external research agent has failed 3+ times recently.
task-master detected the open circuit breaker and skipped the grep-mcp-researcher agent.
Tasks will still be generated using local codebase research only.

**This is not a fatal error.** Tasks are still generated. The GREP MCP warning means
tasks may have slightly less battle-tested implementation context.

**How to reset the circuit breaker:**

```bash
# Check current state
cat .claude/circuit-breakers/grep-mcp.json

# Reset by deleting the state file
rm .claude/circuit-breakers/grep-mcp.json

# Re-run task-master — circuit breaker will start fresh (closed state)
```

**How the circuit breaker works:**

| State | Condition | Behavior |
|-------|-----------|----------|
| Closed (normal) | < 3 failures | Agent dispatched normally |
| Open | >= 3 failures, cooldown not expired | Agent skipped, local only |
| Half-open | cooldown expired | Agent retried once; success closes it, failure re-opens |

**If the breaker keeps re-opening:** The GREP MCP tool or network is having persistent issues.
Check MCP server availability. task-master will continue working without it — local research
using Grep and the codebase-scanner agent is sufficient for most plans.

---

## Issue 3: Task File Missing a Required Section

**What it means:** Either task-master generated an incomplete file (a bug), or you manually
edited a task file and accidentally deleted a section.

**The 10 required sections are:**

1. Header (Status, BlockedBy, EstimatedContextWindow)
2. Summary
3. Files to Read Before Starting
4. Files to Modify or Create
5. Implementation Checklist
6. Success Criteria
7. Testing
8. Task Management
9. Definition of Done

**How to identify which section is missing:**

```bash
bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending/
# Output will name the file and the missing section
```

**How to manually add a missing Testing section:**

```markdown
## Testing

### Unit Tests

File: `tests/unit/test_{name}.py`

- test_happy_path — nominal input produces correct output
- test_edge_case — empty input handled gracefully
- test_error_case — upstream failure raises appropriate exception

### Integration Tests

File: `tests/integration/test_{name}_integration.py`

- test_with_real_db — confirm DB state after write operations

### Live API Tests

No external API involved for this task.
```

After adding the section, re-run `validate-tasks.sh` to confirm it passes.

---

## Issue 4: validate-tasks.sh Exits 1 for Broken Dependency

**What it means:** A task file has `BlockedBy: [NNN]` where task NNN does not exist in
`tasks/_pending/`.

**Diagnostic:**

```bash
# See which task is broken
bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending/
# Look for: "FAIL [...] Broken dependency reference: NNN does not exist"
```

**Common causes:**

| Cause | Fix |
|-------|-----|
| You manually deleted a dependency task | Re-generate the missing task or update BlockedBy to remove the reference |
| task-master generated sub-tasks (009a, 009b) but BlockedBy references the parent (009) | Update BlockedBy to reference the correct sub-task number |
| You renamed a task file | Update the BlockedBy fields in all tasks that referenced the old number |

**How to fix task numbering:**

```bash
# Find all files that reference a broken dependency
grep -rn "BlockedBy.*\[009\]" tasks/_pending/

# Edit each file: change [009] to [009b] (the correct sub-task)
# Then re-run validate-tasks.sh to confirm fixed
```

**Prevention:** Do not manually rename task files after generation. If renaming is
necessary, use search-and-replace across all task files to update all BlockedBy references.

---

## Issue 5: Delivery Report Shows "BLOCKED live tests"

**What it means:** One or more task files contain `# BLOCKED: {KEY} not found in .env`.
This is expected and correct behavior when an API key is missing.

**The blocked tests are valid task content.** The task will still implement and the code
will still be testable — only the live API test is blocked until the key is added.

**How to unblock:**

1. Get the actual API key (from the service's developer console, team vault, etc.)
2. Add it to `.env`:
   ```bash
   echo "STRIPE_SECRET_KEY=sk_test_..." >> .env
   ```
3. Open the blocked task file and find the stubbed live test:
   ```python
   # BLOCKED: STRIPE_SECRET_KEY not found in .env
   # Uncomment and run manually once key is available.
   ```
4. Remove the `# BLOCKED` comment and uncomment the test body.
5. Run the live test:
   ```bash
   uv run pytest tests/live/test_stripe_live.py -v -m live
   ```

**Note:** You do NOT need to re-run task-master. Just edit the task file directly.
validate-tasks.sh accepts BLOCKED stubs as valid — they will not cause a validation failure.

---

## Issue 6: Tasks Are Too Detailed or Too Vague

**What it means:** task-master's default checklist depth does not match your preference.
This is a stylistic mismatch, not an error. All generated tasks are technically valid.

**To adjust for the current session:**

After the delivery report, tell task-master directly:
- "Too detailed" — saves `task_depth: lean` to memory
- "Too vague, I need more steps" — saves `task_depth: thorough` to memory

**To adjust permanently:**

```bash
# Edit the memory file directly
cat .claude/memory/task-master.md
# Find or add: task_depth: lean|thorough|default
```

**What each depth level means:**

| Depth | Checklist items per task | Success criteria per item |
|-------|--------------------------|--------------------------|
| `lean` | 4-5 items | Commands only, no explanatory text |
| `default` | 6-8 items | Commands + one-line explanation |
| `thorough` | 8-12 items | Commands + explanation + grep assertions |

**To reset to default:**

```bash
rm .claude/memory/task-master.md
# Next run starts fresh with no saved preferences
```
