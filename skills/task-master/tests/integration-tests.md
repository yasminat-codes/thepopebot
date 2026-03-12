# task-master — Integration Tests
Version: 1.0.0 | Last updated: 2026-03-02

End-to-end tests that verify task-master works correctly as part of the full pipeline.
These tests require a real project environment (not unit-isolated).

---

## Test I1: Full Pipeline Run

**Type:** End-to-end
**Scope:** task-master invocation → task file output → validate-tasks.sh
**Priority:** P0 (must pass before any release)

### Setup

```bash
# Place the sample plan in the fixtures location
cp tests/fixtures/sample-plan-simple/plan.md plan/rate-limiter.md

# Ensure tasks directories exist
mkdir -p tasks/_pending tasks/_in-progress tasks/_completed
```

### Steps

1. Confirm fixture plan exists at `tests/fixtures/sample-plan-simple/plan.md`
2. Invoke task-master with that plan:
   ```
   /task-master plan/rate-limiter.md
   ```
3. At Phase 3 preview: select "Proceed" when shown the task list
4. Wait for Phase 5 to complete
5. Run validate-tasks.sh:
   ```bash
   bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending/
   ```
6. Confirm TASK-LOG.md written:
   ```bash
   cat tasks/TASK-LOG.md
   ```

### Expected Output

```
tasks/_pending/
├── 001-rate-limiter-models.md
├── 002-rate-limiter-service.md
└── 003-rate-limiter-tests.md

tasks/TASK-LOG.md   (written)
```

### Pass Criteria

- [ ] `validate-tasks.sh` exits 0
- [ ] `tasks/TASK-LOG.md` exists and contains all 3 task entries
- [ ] Task 002 `BlockedBy` field contains `[001]`
- [ ] Task 003 `BlockedBy` field contains `[002]`
- [ ] Delivery report shown in terminal includes "Pipeline validation: PASS"

### Teardown

```bash
rm -f plan/rate-limiter.md
rm -rf tasks/_pending/ tasks/_in-progress/ tasks/_completed/ tasks/TASK-LOG.md
mkdir -p tasks/_pending tasks/_in-progress tasks/_completed
```

---

## Test I2: Memory Persistence

**Type:** State persistence
**Scope:** Memory save → preference load → applied output
**Priority:** P1

### Purpose

Verify that task-master saves user corrections to `.claude/memory/task-master.md` and
applies them automatically on subsequent runs.

### Steps

1. Run task-master on the sample plan (accept all defaults):
   ```
   /task-master tests/fixtures/sample-plan-simple/plan.md
   ```

2. After delivery report, simulate user feedback via follow-up message:
   ```
   The tasks are too detailed. Keep the checklists lean — 4 items max per task.
   ```

3. Verify memory was saved:
   ```bash
   grep "task_depth" .claude/memory/task-master.md
   ```
   Expected: `task_depth: lean` or equivalent preference notation.

4. Delete the generated task files:
   ```bash
   rm tasks/_pending/*.md
   ```

5. Run task-master again on the same plan:
   ```
   /task-master tests/fixtures/sample-plan-simple/plan.md
   ```

6. Count checklist items in the re-generated tasks:
   ```bash
   grep -c "^\- \[ \]" tasks/_pending/002-rate-limiter-service.md
   ```

### Expected Output

Second run produces tasks with 4 or fewer checklist items per task file.
Delivery report on second run includes a note such as:
```
Applied saved preference: task_depth=lean
```

### Pass Criteria

- [ ] `.claude/memory/task-master.md` exists after first run + feedback
- [ ] File contains a `task_depth` preference key
- [ ] Second run delivery report references the saved preference
- [ ] Second-run tasks have fewer checklist items than first-run tasks
- [ ] `validate-tasks.sh` still exits 0 on second run (lean tasks are still valid)

---

## Test I3: Circuit Breaker Simulation

**Type:** Resilience / degraded-mode
**Scope:** Circuit breaker state → agent dispatch → fallback behavior
**Priority:** P1

### Purpose

Verify that when the GREP MCP circuit breaker is open, task-master degrades gracefully
(uses local research only) instead of halting or producing broken output.

### Setup

```bash
# Create circuit breaker state directory if missing
mkdir -p .claude/circuit-breakers

# Write an open circuit breaker state
cat > .claude/circuit-breakers/grep-mcp.json << 'EOF'
{
  "state": "open",
  "failures": 3,
  "last_failure": "2026-03-02T10:00:00Z",
  "cooldown_until": "2099-12-31T23:59:59Z"
}
EOF
```

### Steps

1. Write the open circuit breaker state (see setup above)
2. Run task-master on the sample plan:
   ```
   /task-master tests/fixtures/sample-plan-simple/plan.md
   ```
3. Observe Phase 2 output — grep-mcp-researcher agent should NOT be dispatched
4. Confirm tasks are generated despite the breaker being open
5. Check delivery report for circuit breaker warning

### Expected Behavior

Phase 2 message: "GREP MCP circuit breaker is open. Using local research only."
grep-mcp-researcher agent is NOT dispatched (no `Task` call for it).
codebase-scanner agent IS dispatched (local research proceeds normally).
All 3 task files are generated and valid.
Delivery report includes a warning line about the open circuit breaker.

### Pass Criteria

- [ ] 3 task files generated in `tasks/_pending/` (tasks not halted)
- [ ] `validate-tasks.sh` exits 0
- [ ] Delivery report contains text indicating circuit breaker was open
- [ ] No grep-mcp-researcher agent invoked (check conversation for Task tool calls)

### Teardown

```bash
rm .claude/circuit-breakers/grep-mcp.json
```

---

## Test I4: validate-tasks.sh on Invalid Files

**Type:** Validation script correctness
**Scope:** validate-tasks.sh error detection
**Priority:** P0 (script must catch real problems)

### Purpose

Verify that `validate-tasks.sh` correctly identifies and reports malformed task files.
This test validates the validator, not task-master itself.

### Setup

```bash
mkdir -p tasks/_pending

# File 1: Missing Testing section
cat > tasks/_pending/010-missing-testing.md << 'EOF'
# Task 010: Missing Testing
**Status:** PENDING
**BlockedBy:** []
**EstimatedContextWindow:** small

## Summary
This task is missing its Testing section.

## Files to Read Before Starting
- app/config.py

## Files to Modify or Create
| Action | Path | What Changes |
|--------|------|--------------|
| CREATE | app/services/foo.py | New service |

## Implementation Checklist
- [ ] Step 1
      — Success: command exits 0

## Success Criteria
1. Service importable: exits 0
2. Unit tests pass: exits 0
3. All tests pass: exits 0
4. No lint errors: exits 0
5. Service-specific criterion

## Task Management
At task start: mv tasks/_pending/010-missing-testing.md tasks/_in-progress/010-missing-testing.md
At task complete: mv tasks/_in-progress/010-missing-testing.md tasks/_completed/010-missing-testing.md

## Definition of Done
- [ ] All checklist items checked
EOF

# File 2: Invalid BlockedBy syntax
cat > tasks/_pending/011-bad-blockedby.md << 'EOF'
# Task 011: Bad BlockedBy
**Status:** PENDING
**BlockedBy:** 001 002
**EstimatedContextWindow:** small

## Summary
This task has invalid BlockedBy syntax (missing brackets).

## Files to Read Before Starting
- app/config.py

## Files to Modify or Create
| Action | Path | What Changes |
|--------|------|--------------|
| CREATE | app/services/bar.py | New service |

## Implementation Checklist
- [ ] Step 1
      — Success: exits 0

## Success Criteria
1. Importable: exits 0
2. Unit tests pass: exits 0
3. All tests pass: exits 0
4. No lint errors: exits 0
5. Specific criterion

## Testing

### Unit Tests
- test_nominal

## Task Management
At task start: mv tasks/_pending/011-bad-blockedby.md tasks/_in-progress/011-bad-blockedby.md

## Definition of Done
- [ ] All checklist items checked
EOF

# File 3: Broken dependency reference
cat > tasks/_pending/012-broken-dep.md << 'EOF'
# Task 012: Broken Dependency
**Status:** PENDING
**BlockedBy:** [099]
**EstimatedContextWindow:** small

## Summary
This task references dependency 099, which does not exist.

## Files to Read Before Starting
- app/config.py

## Files to Modify or Create
| Action | Path | What Changes |
|--------|------|--------------|
| CREATE | app/services/baz.py | New service |

## Implementation Checklist
- [ ] Step 1
      — Success: exits 0

## Success Criteria
1. Importable: exits 0
2. Unit tests pass: exits 0
3. All tests pass: exits 0
4. No lint errors: exits 0
5. Specific criterion

## Testing

### Unit Tests
- test_nominal

## Task Management
At task start: mv tasks/_pending/012-broken-dep.md tasks/_in-progress/012-broken-dep.md

## Definition of Done
- [ ] All checklist items checked
EOF
```

### Steps

```bash
bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending/
echo "Exit code: $?"
```

### Expected Output

```
FAIL [010-missing-testing.md] Missing required section: Testing
FAIL [011-bad-blockedby.md] Invalid BlockedBy syntax: must be [] or [NNN, NNN]
FAIL [012-broken-dep.md] Broken dependency reference: 099 does not exist in tasks/_pending/

3 errors found. Fix task files before proceeding.
```

Exit code: 1

### Pass Criteria

- [ ] `validate-tasks.sh` exits 1 (not 0)
- [ ] Output contains exactly 3 failure lines
- [ ] Each failure line names the specific file
- [ ] Each failure line names the specific issue
- [ ] Output includes summary count: "3 errors found"

### Teardown

```bash
rm -f tasks/_pending/010-missing-testing.md
rm -f tasks/_pending/011-bad-blockedby.md
rm -f tasks/_pending/012-broken-dep.md
```
