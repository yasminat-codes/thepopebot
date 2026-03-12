# Circuit Breaker Reference

## Overview

The circuit breaker prevents cascading failures when Metricool API calls repeatedly fail. It sits in front of every outbound request made by the `batch-scheduler` skill.

---

## States

| State     | Description                                          |
|-----------|------------------------------------------------------|
| CLOSED    | Normal operation — requests pass through             |
| OPEN      | Blocking — all requests rejected immediately         |
| HALF-OPEN | Testing — one probe request allowed through          |

---

## State Machine

```
          3 consecutive failures
  CLOSED ─────────────────────────> OPEN
    ^                                 |
    |                         5-min cooldown
    |                                 |
    |                                 v
    |          probe success     HALF-OPEN
    └────────────────────────────────/
           probe failure ──> OPEN (restart cooldown)
```

### CLOSED (Normal)

- All requests pass through to the Metricool API.
- Track consecutive failures internally (in-memory counter).
- On **3 consecutive failures**: transition to OPEN, log the event, reset the cooldown timer.
- A single success resets the consecutive failure counter to 0.

### OPEN (Blocking)

- Reject all requests immediately without calling the API.
- Return a structured error to the caller:
  ```json
  { "error": "circuit_open", "retry_after_seconds": 300 }
  ```
- After **5-minute cooldown** elapses: transition to HALF-OPEN, log the event.

### HALF-OPEN (Testing)

- Allow **exactly 1** probe request through to the API.
- If the probe **succeeds**: transition to CLOSED, reset failure counter to 0, log recovery.
- If the probe **fails**: transition back to OPEN, restart the 5-minute cooldown, log the event.

---

## Implementation Notes

- **State is in-memory only.** It is not persisted to disk or a database. Each new skill session starts with the circuit in CLOSED state and a failure counter of 0.
- This is intentional: a fresh session should attempt real requests rather than inherit a stale OPEN state from a previous run.

---

## Logging

All state transitions must be logged with the `[circuit-breaker]` prefix so they can be filtered in logs.

| Event                             | Log message example                                                        |
|-----------------------------------|----------------------------------------------------------------------------|
| Failure recorded                  | `[circuit-breaker] failure 2/3 recorded for POST /social/metricool/post`  |
| CLOSED → OPEN                     | `[circuit-breaker] OPEN — 3 consecutive failures, cooldown starts now`    |
| OPEN → HALF-OPEN                  | `[circuit-breaker] HALF-OPEN — cooldown elapsed, sending probe request`   |
| HALF-OPEN → CLOSED (success)      | `[circuit-breaker] CLOSED — probe succeeded, failure counter reset`       |
| HALF-OPEN → OPEN (failure)        | `[circuit-breaker] OPEN — probe failed, restarting 5-min cooldown`       |
| Request rejected (OPEN)           | `[circuit-breaker] request blocked — circuit is OPEN, retry_after=Xs`    |

---

## ASCII State Diagram

```
+------------------+
|                  |
|     CLOSED       |<--------------------------+
|  (normal ops)    |                           |
|                  |                           | probe success
+--------+---------+                           | (reset counter)
         |                                     |
         | 3 consecutive failures              |
         v                                     |
+------------------+      5-min cooldown  +----+----------+
|                  |--------------------->|               |
|      OPEN        |                      |  HALF-OPEN    |
|  (reject all)    |<---------------------|  (1 probe)    |
|                  |   probe failure      |               |
+------------------+   (restart cooldown) +---------------+
```
