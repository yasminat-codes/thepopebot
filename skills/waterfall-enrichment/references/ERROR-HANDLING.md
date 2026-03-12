# Error Handling Guide

Comprehensive error handling for the waterfall enrichment pipeline.

---

## Error Categories

### 1. Configuration Errors

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| `NO_API_KEY` | No API key for provider | Env var not set | Set the provider's env var |
| `NO_FINDERS` | No finder providers configured | No finder API keys set | Set at least one finder key (Tomba, Muraena, etc.) |
| `NO_VERIFIER` | No verifier configured | REOON_API_KEY not set | Set REOON_API_KEY — verification is mandatory |
| `INVALID_CONFIG` | Config file malformed | Bad JSON in config | Fix config.json syntax |
| `MISSING_INPUT` | No input file specified | Missing --input flag | Provide --input or inline lead |

### 2. Finder Errors

Errors from email finding providers (Tomba, Muraena, Icypeas, Voila Norbert, Nimbler, Anymailfinder, Findymail).

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| `RATE_LIMITED` | Rate limit exceeded | Too many requests | Auto-retry with exponential backoff |
| `AUTH_FAILED` | Authentication failed | Invalid API key | Check/rotate API key. Disable provider for this run. |
| `PROVIDER_DOWN` | Provider unreachable | API outage | Skip to next finder |
| `TIMEOUT` | Request timed out | Slow response | Skip after provider-specific timeout |
| `QUOTA_EXCEEDED` | Monthly quota hit | Plan limit reached | Disable provider, continue with remaining finders |
| `INVALID_RESPONSE` | Unexpected response format | API changed | Log full response, skip provider |

**Finder error = skip to next finder.** Never abort the lead because one finder fails.

### 3. Verifier Errors

Errors from Reoon (primary verifier) and Email Verify (catchall verifier).

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| `REOON_DOWN` | Reoon API unreachable | API outage | **Critical.** Pause batch. Retry after 60s. |
| `REOON_RATE_LIMIT` | Reoon rate limited | Too many requests | Back off (10 req/s limit). Slow batch pace. |
| `REOON_AUTH` | Reoon auth failed | Bad API key | **Critical.** Stop batch. Cannot verify without Reoon. |
| `EV_DOWN` | Email Verify unreachable | API outage | Skip catchall verification. Mark as RISKY (confidence 50). |
| `EV_AUTH` | Email Verify auth failed | Bad/missing key | Skip catchall verification. Mark as RISKY (confidence 50). |
| `EV_TIMEOUT` | Email Verify timeout | Slow response | Mark as RISKY, continue. |

**Reoon is mandatory.** If Reoon fails with auth error → stop the entire batch. Unverified emails cannot be used.

**Email Verify is optional.** If Email Verify fails → catchall emails stay at RISKY (confidence 50) instead of being resolved.

### 4. Data Errors

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| `INVALID_DOMAIN` | Domain has no MX records | Dead domain | Skip lead — no email possible |
| `PERSONAL_DOMAIN` | Personal email domain detected | gmail.com, yahoo.com, etc. | Skip lead — finders can't resolve personal domains |
| `INVALID_EMAIL` | Email format invalid | Finder returned bad syntax | Skip email, try next finder |
| `EMPTY_NAME` | Name field empty | Missing data | Skip lead |
| `DUPLICATE_LEAD` | Duplicate name+domain | Already processed | Skip duplicate |

### 5. System Errors

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| `FILE_NOT_FOUND` | Input file missing | Wrong path | Check file path |
| `WRITE_ERROR` | Cannot write output | Permissions | Check directory permissions |
| `BATCH_INTERRUPTED` | Batch stopped mid-run | Crash/interrupt | Resume from checkpoint |
| `MEMORY_ERROR` | Out of memory | CSV too large | Use split_csv.py to chunk input |

---

## Retry Strategy

### Exponential Backoff

```
Attempt 1: Wait {initial_delay}
Attempt 2: Wait {initial_delay × 2}
Attempt 3: Wait {initial_delay × 4}
(give up after max_retries)
```

### Per-Provider Retry Rules

**Finders:**

| Provider | Max Retries | Initial Delay | Max Delay | Timeout |
|----------|-------------|---------------|-----------|---------|
| Tomba | 3 | 3s | 15s | 30s |
| Muraena | 2 | 3s | 20s | 30s |
| Icypeas | 3 | 1s | 10s | 30s |
| Voila Norbert | 3 | 2s | 15s | 30s |
| Nimbler | 2 | 3s | 20s | 30s |
| Anymailfinder | 2 | 5s | 30s | 120s |
| Findymail | 3 | 2s | 15s | 30s |

**Verifiers:**

| Provider | Max Retries | Initial Delay | Max Delay | Timeout |
|----------|-------------|---------------|-----------|---------|
| Reoon | 5 | 0.5s | 10s | 30s |
| Email Verify | 3 | 1s | 10s | 30s |

**Reoon gets 5 retries** — it's critical. Losing Reoon means unverified emails.

### Non-Retryable Errors

These errors skip to the next provider immediately (no retry):
- `AUTH_FAILED` — Key is wrong, retrying won't help. **Disable provider for entire run.**
- `QUOTA_EXCEEDED` — Plan limit, retrying won't help. **Disable provider for entire run.**
- `INVALID_RESPONSE` — Parser issue, needs code fix

---

## Batch Recovery

### Checkpoint System

The enrichment script saves progress after every batch:

```json
{
  "input_file": "leads.csv",
  "output_file": "enriched.csv",
  "total_leads": 5000,
  "processed": 2300,
  "last_batch": 23,
  "found": 1840,
  "verified": 1656,
  "catchall": 184,
  "not_found": 460,
  "disabled_finders": ["nimbler"],
  "disabled_verifiers": [],
  "cost_estimate": 84.20,
  "timestamp": "2026-02-23T10:30:00Z"
}
```

### Resume from Checkpoint

```bash
python3 {baseDir}/scripts/enrich.py \
  --input leads.csv \
  --output enriched.csv \
  --resume
```

The `--resume` flag:
1. Reads the checkpoint file
2. Skips already-processed leads
3. Restores disabled provider list
4. Continues from where it left off
5. Appends to existing output file

### Forced Re-Run

```bash
python3 {baseDir}/scripts/enrich.py \
  --input leads.csv \
  --output enriched.csv \
  --no-resume
```

Ignores checkpoint, starts fresh. Overwrites output file.

---

## Logging

All errors are logged to stderr with structured format:

```
[2026-02-23 10:30:00] INFO  phase=find provider=tomba lead="John Doe" domain=example.com status=found email=john@example.com time=2.1s
[2026-02-23 10:30:02] INFO  phase=verify provider=reoon email=john@example.com status=valid catchall=false time=1.5s
[2026-02-23 10:30:04] INFO  phase=find provider=tomba lead="Jane Smith" domain=acme.com status=not_found time=3.2s
[2026-02-23 10:30:07] INFO  phase=find provider=muraena lead="Jane Smith" domain=acme.com status=found email=jane@acme.com time=4.1s
[2026-02-23 10:30:09] INFO  phase=verify provider=reoon email=jane@acme.com status=catchall time=2.0s
[2026-02-23 10:30:11] INFO  phase=catchall provider=emailverify email=jane@acme.com status=valid confidence=80 time=1.8s
[2026-02-23 10:30:11] WARN  phase=find provider=nimbler lead="Bob Jones" domain=foo.com error=RATE_LIMITED retry=1/2
[2026-02-23 10:30:14] ERROR phase=find provider=nimbler lead="Bob Jones" domain=foo.com error=RATE_LIMITED retry=2/2 action=skip
```

### Log Levels

| Level | When Used |
|-------|-----------|
| `ERROR` | Provider auth failure, verifier down, system error |
| `WARN` | Rate limit hit, retry happening, provider disabled |
| `INFO` | Email found, verification result, batch progress |
| `DEBUG` | API request/response details (--verbose) |

### Phase Tags

Every log line includes a `phase=` tag:

| Phase | What's Happening |
|-------|-----------------|
| `init` | Loading config, checking providers, validating input |
| `precheck` | MX check, personal domain filter, deduplication |
| `find` | Finder provider trying to locate email |
| `verify` | Reoon verifying found email |
| `catchall` | Email Verify resolving catchall result |
| `output` | Writing results to CSV/JSON |
| `checkpoint` | Saving batch progress |

---

## Graceful Degradation

When providers fail, the system degrades gracefully:

### Finder Failures
1. **Single finder fails:** Skip to next finder in cascade
2. **Multiple finders fail:** Continue with remaining finders
3. **All finders fail for a lead:** Mark as `not_found`, move to next lead
4. **Finder auth error:** Disable that finder for the entire run, continue with others
5. **All finders disabled:** Stop batch — no point continuing without any finders

### Verifier Failures
1. **Reoon rate limited:** Slow down batch pace, retry with backoff
2. **Reoon down temporarily:** Pause batch for 60s, retry 3 times, then stop
3. **Reoon auth failed:** **Stop batch immediately.** Cannot proceed without verification.
4. **Email Verify fails:** Continue — catchall emails marked RISKY (confidence 50) instead of resolved
5. **Email Verify not configured:** Normal operation — catchall stays RISKY

### Network Failures
1. **Intermittent:** Retry with backoff
2. **Persistent:** Save checkpoint, exit with resume instructions
3. **DNS failure:** Skip provider, try next

### Critical vs Non-Critical

| Failure | Severity | Action |
|---------|----------|--------|
| Reoon auth/down | **CRITICAL** | Stop batch. Cannot send unverified emails. |
| All finders disabled | **CRITICAL** | Stop batch. No way to find emails. |
| Single finder auth | Non-critical | Disable finder, continue with others |
| Email Verify down | Non-critical | Catchall → RISKY instead of resolved |
| Network blip | Non-critical | Retry with backoff |
| Input file issues | Non-critical | Log and skip bad rows |

The system never sends unverified emails. If Reoon fails, everything stops.
