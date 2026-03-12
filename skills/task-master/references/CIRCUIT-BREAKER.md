# CIRCUIT-BREAKER.md — GREP MCP Circuit Breaker for task-master

Governs when the `grep-mcp-researcher` sub-agent (Agent B) is dispatched during Phase 2.
When GREP MCP is consistently unavailable, the circuit opens and task-master degrades
gracefully to local-only research instead of failing completely.

---

## Section 1: State File Location and Format

### File path
```
.claude/circuit-breakers/grep-mcp.json
```

The directory `.claude/circuit-breakers/` is created on first write if it does not exist.
If the file does not exist at all, treat the circuit as `closed` (healthy first run).

### Schema
```json
{
  "state": "closed",
  "failures": 0,
  "last_failure": null,
  "cooldown_until": null,
  "last_success": "2026-03-02T01:00:00Z"
}
```

### Field definitions

| Field | Type | Description |
|-------|------|-------------|
| `state` | string | Current circuit state: `closed`, `open`, or `half-open` |
| `failures` | integer | Consecutive failure count since last successful request |
| `last_failure` | string or null | ISO timestamp of most recent failure |
| `cooldown_until` | string or null | ISO timestamp when the open state expires |
| `last_success` | string or null | ISO timestamp of most recent success |

### State definitions

- `closed` — Circuit is healthy. Dispatch Agent B normally.
- `open` — Too many recent failures. Cooldown is active. Skip Agent B.
- `half-open` — Cooldown has expired. Dispatch one test request to probe recovery.

---

## Section 2: Phase 2 Check Procedure

Before dispatching the `grep-mcp-researcher` agent, execute this decision sequence in order.

### Step 1: Load state file
```
Read .claude/circuit-breakers/grep-mcp.json
```
If the file does not exist: set in-memory state to `{state: "closed", failures: 0}` and
proceed to Step 4. Do not create the file yet (write only on state changes).

### Step 2: Evaluate state
```
if state == "open":
    if cooldown_until > now:
        → SKIP (go to fallback behavior in Section 4)
    else:
        → SET state = "half-open" in memory
        → WRITE updated state to file
        → proceed to Step 4 (dispatch one test query)

if state == "half-open":
    → proceed to Step 4 (dispatch one test query)

if state == "closed":
    → proceed to Step 4 (dispatch normally)
```

### Step 3: Never dispatch if open with active cooldown
When the circuit is open and cooldown has not expired, do not attempt a GREP MCP call.
Go directly to Section 4 (fallback behavior). Log this in the Phase 2 output:
```
[Circuit Breaker] GREP MCP state: OPEN — cooldown until {cooldown_until}. Using local research only.
```

### Step 4: Dispatch Agent B
Proceed with normal or half-open dispatch. Agent B result determines the next state update
(see Section 3).

---

## Section 3: Failure and Success Recording

### On Agent B failure (GREP MCP call fails, times out, or returns an error)

```
Read current state from .claude/circuit-breakers/grep-mcp.json (or in-memory state)
Increment failures by 1
Set last_failure = now (ISO UTC)

if failures >= 3:
    Set state = "open"
    Set cooldown_until = now + 60 seconds

Write updated state to .claude/circuit-breakers/grep-mcp.json
```

Extended cooldown for repeated reopening: if the circuit has opened 3 or more times within
the same task-master session, double the cooldown (120 seconds) to avoid hammering a
consistently unavailable service.

### On Agent B success (GREP MCP returns usable results)

```
Set state = "closed"
Set failures = 0
Set last_success = now (ISO UTC)
Set cooldown_until = null
Set last_failure = null

Write updated state to .claude/circuit-breakers/grep-mcp.json
```

A half-open success immediately closes the circuit. One successful test request is enough.

### Threshold summary

| Event | Result |
|-------|--------|
| 1st failure | failures = 1, state stays closed |
| 2nd failure | failures = 2, state stays closed |
| 3rd consecutive failure | state → open, cooldown = 60s |
| Cooldown expires | state → half-open |
| Half-open test succeeds | state → closed, failures reset |
| Half-open test fails | state → open, cooldown extended |

---

## Section 4: Fallback Behavior

When the circuit is open and Agent B is skipped, task-master continues without external
pattern research. This is a graceful degradation, not a failure.

### What changes when GREP MCP is unavailable

- Phase 2 runs only Agent A (codebase-scanner)
- Task files are still generated using local codebase patterns
- External usage examples are omitted from the "Files to Read" suggestions
- The task files themselves are not marked as incomplete

### Delivery report note

At the end of Phase 5, if GREP MCP was skipped for any task, append to the delivery report:

```
NOTE: GREP MCP circuit breaker was open during this run.
  External pattern research was skipped for all tasks.
  Local codebase research (Agent A) was used only.
  Impact: "Files to Read" suggestions are based on this codebase only,
          not validated against external production patterns.
  To reset: delete .claude/circuit-breakers/grep-mcp.json and rerun.
```

### What is never skipped

The entire Phase 2 research step is not skipped — only Agent B is skipped.
Agent A (codebase-scanner) always runs. Task generation always completes.
