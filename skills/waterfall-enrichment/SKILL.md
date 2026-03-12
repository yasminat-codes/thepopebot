---
name: waterfall-enrichment
description: Multi-provider email finding and verification waterfall. Finds emails through 7 cascading finders, verifies with Reoon, handles catchalls with Email Verify. Handles batches from 100 to 50,000+ leads with rate limiting, checkpointing, and resume.
allowed-tools: Read Write Edit Bash(curl:*) Bash(jq:*) Bash(python3:*) Bash(cat:*) Bash(date:*) Bash(mkdir:*) Bash(wc:*) Bash(sort:*) Bash(head:*)
metadata: {"clawdbot":{"requires":{"env":["REOON_API_KEY"],"bins":["curl","jq","python3"]},"primaryEnv":"REOON_API_KEY"}}
context: fork
agent: general-purpose
---

# Waterfall Enrichment Skill

Multi-provider email finding and verification cascade. 7 email finders feed into a 2-stage verification pipeline (Reoon for primary verification, Email Verify for catchall resolution). Handles 100 to 50,000+ leads with rate limiting, batch processing, checkpointing, and resume-on-failure.

## Iron Law

```
ENRICHMENT PIPELINE:
1. FINDERS find emails (7 providers in cascade order)
2. REOON verifies every found email (primary verifier)
3. EMAIL VERIFY resolves catchall results (catchall verifier)
4. Valid emails go to the leads database
5. Invalid emails are discarded
6. Not-found leads cascade to the next finder

FINDERS ≠ VERIFIERS:
- Finders: Tomba, Muraena, Icypeas, Voila Norbert, Nimbler, Anymailfinder, Findymail
- Primary Verifier: Reoon (verifies ALL found emails)
- Catchall Verifier: Email Verify (resolves catchall results only)

NEVER send unverified emails to campaigns.
NEVER skip Reoon verification — even if a finder says "verified."
NEVER trust a single provider's verification — Reoon is the source of truth.
```

## Architecture

```
                        ┌─────────────────────────────────────┐
                        │         INPUT LEADS                  │
                        │   (name + company/domain)            │
                        └──────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │     FINDER CASCADE (stop on find)    │
                    │                                      │
                    │  1. Tomba          ─── found? ──┐    │
                    │  2. Muraena        ─── found? ──┤    │
                    │  3. Icypeas        ─── found? ──┤    │
                    │  4. Voila Norbert  ─── found? ──┤    │
                    │  5. Nimbler        ─── found? ──┤    │
                    │  6. Anymailfinder  ─── found? ──┤    │
                    │  7. Findymail      ─── found? ──┤    │
                    │                                  │    │
                    │  All exhausted → NOT FOUND ──┐   │    │
                    └──────────────────────────────┼───┼────┘
                                                   │   │
                              ┌─────────────────────   │
                              │                        ▼
                              │          ┌─────────────────────┐
                              │          │  REOON VERIFICATION  │
                              │          │  (primary verifier)   │
                              │          └─────┬───────┬───────┘
                              │                │       │
                              │          VALID │    CATCHALL
                              │                │       │
                              │                ▼       ▼
                              │          ┌──────┐ ┌──────────────────┐
                              │          │  DB  │ │  EMAIL VERIFY     │
                              │          └──────┘ │  (catchall only)  │
                              │                   └──┬──────┬────────┘
                              │                      │      │
                              │                VALID │   INVALID
                              │                      │      │
                              │                      ▼      ▼
                              │                ┌──────┐ ┌────────┐
                              │                │  DB  │ │DISCARD │
                              ▼                └──────┘ └────────┘
                        ┌───────────┐
                        │ NOT FOUND │
                        └───────────┘
```

## Environment Setup

```bash
source /home/clawdbot/shared/.env 2>/dev/null

# Base dir
WF_BASE="/home/clawdbot/shared/skills/waterfall-enrichment"
WF_SCRIPTS="$WF_BASE/scripts"

# === FINDERS (cascade order) ===
# TOMBA_API_KEY + TOMBA_SECRET
# MURAENA_API_KEY
# ICYPEAS_API_KEY + ICYPEAS_API_SECRET
# VOILANORBERT_API_KEY
# NIMBLER_API_KEY
# ANYMAILFINDER_API_KEY
# FINDYMAIL_API_KEY

# === VERIFIERS ===
# REOON_API_KEY         ← primary verifier (REQUIRED)
# EMAILVERIFY_API_KEY   ← catchall verifier
```

## The Waterfall — Step by Step

### Phase 1: Input Processing

```
1. Accept input: CSV file, JSON array, or single lead
2. Required fields: first_name, last_name, domain (or company)
3. Normalize: trim whitespace, title-case names, extract domain from URL
4. Deduplicate: by domain + full_name pair
5. Validate: skip leads missing required fields
6. Split into batches (configurable, default 100/batch)
```

### Phase 2: Finder Cascade (Per Lead)

For each lead, try finders in order. Stop on first email found.

```
FINDER ORDER:
1. Tomba          → cheap, fast, good hit rate
2. Muraena        → good coverage, broad database
3. Icypeas        → enrichment + finding, supports bulk
4. Voila Norbert  → reliable search
5. Nimbler        → deep B2B data (50+ fields bonus)
6. Anymailfinder  → real-time SMTP + scraping (slower but thorough)
7. Findymail      → last resort

For each finder:
  1. Check API key exists → skip if not configured
  2. Check rate limit → wait if throttled
  3. Call finder API with (first_name, last_name, domain)
  4. If email returned → proceed to Phase 3 (Reoon verification)
  5. If not found → try next finder
  6. If API error → retry with backoff, then try next finder
  7. If ALL finders exhausted → mark as "not_found"
```

### Phase 3: Primary Verification (Reoon)

Every email found by ANY finder goes through Reoon:

```
REOON VERIFICATION (power mode):
  Input: email address from finder
  Output:
    "valid"       → confidence 90-100 → ADD TO DB
    "invalid"     → DISCARD (log reason)
    "catchall"    → proceed to Phase 4 (Email Verify)
    "unknown"     → treat as catchall → proceed to Phase 4
    "disposable"  → DISCARD (temporary email)
```

### Phase 4: Catchall Resolution (Email Verify)

Only emails flagged as catchall by Reoon go through Email Verify:

```
EMAIL VERIFY (catchall only):
  Input: email flagged as catchall by Reoon
  Output:
    "valid"    → confidence 70-85 → ADD TO DB (flag: catchall_verified)
    "risky"    → confidence 50-65 → ADD TO RISKY LIST
    "invalid"  → DISCARD
    "unknown"  → ADD TO RISKY LIST (confidence 40)
```

### Phase 5: Output

```
OUTPUT BUCKETS:
1. VERIFIED (90-100)          → Reoon valid. Safe to campaign.
2. CATCHALL-VERIFIED (70-85)  → Email Verify confirmed. Send with monitoring.
3. RISKY (50-69)              → Uncertain. Separate segment, drip-send, watch bounce.
4. NOT FOUND (0)              → No finder returned an email. Manual research needed.
5. INVALID (discarded)        → Bad emails. Don't send.
```

---

## Finder API Reference

### 1. Tomba (Primary Finder)

```bash
curl -s "https://api.tomba.io/v1/email-finder" \
  -H "X-Tomba-Key: $TOMBA_API_KEY" \
  -H "X-Tomba-Secret: $TOMBA_SECRET" \
  -G -d "domain=example.com&first_name=John&last_name=Doe"
```

| Field | Value |
|-------|-------|
| Cost | ~$0.01/search |
| Speed | 1-5s |
| Rate limit | 20 req/min (free), higher paid |
| Parse | `.data.email` from response |

### 2. Muraena

```bash
curl -s -X POST "https://api.muraena.ai/v1/email-finder" \
  -H "Authorization: Bearer $MURAENA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain":"example.com"}'
```

| Field | Value |
|-------|-------|
| Cost | ~$0.02/search |
| Speed | 2-10s |
| Rate limit | Plan-dependent |
| Parse | `.email` from response |
| Note | Business plan ($149+/month) |

### 3. Icypeas

```bash
curl -s -X POST "https://app.icypeas.com/api/email-search" \
  -H "Authorization: Bearer $ICYPEAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain_name":"example.com"}'
```

| Field | Value |
|-------|-------|
| Cost | ~$0.01/search |
| Speed | 1-5s |
| Rate limit | 10 req/s |
| Parse | `.email` from response |
| Bulk | `POST /api/bulk-search` for large batches |

### 4. Voila Norbert

```bash
curl -s -X POST "https://api.voilanorbert.com/2018-01-08/search/name" \
  -u "$VOILANORBERT_API_KEY:" \
  -d "name=John Doe&domain=example.com"
```

| Field | Value |
|-------|-------|
| Cost | ~$0.03/search |
| Speed | 1-10s |
| Rate limit | Plan-dependent |
| Auth | HTTP Basic (key as username, empty password) |
| Parse | `.email.email` from response |

### 5. Nimbler

```bash
curl -s -X POST "https://api.nimbler.com/v1/enrich" \
  -H "Authorization: Bearer $NIMBLER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","company_domain":"example.com"}'
```

| Field | Value |
|-------|-------|
| Cost | ~$0.08/search |
| Speed | 2-5s |
| Rate limit | Plan-dependent |
| Parse | `.work_email` from response |
| Bonus | Also returns phone, social, company data |

### 6. Anymailfinder

```bash
curl -s -X POST "https://api.anymailfinder.com/v5.1/find-email/person" \
  -H "Authorization: Bearer $ANYMAILFINDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain":"example.com"}'
```

| Field | Value |
|-------|-------|
| Cost | ~$0.05/search |
| Speed | 2-120s (real-time scraping) |
| Rate limit | Queue-based |
| Parse | `.email` from response |
| Note | Can be slow — does real-time SMTP probing |

### 7. Findymail (Last Resort)

```bash
curl -s -X POST "https://app.findymail.com/api/search/name" \
  -H "Authorization: Bearer $FINDYMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain":"example.com"}'
```

| Field | Value |
|-------|-------|
| Cost | ~$0.02/search |
| Speed | 1-5s |
| Rate limit | Plan-dependent |
| Parse | `.email` from response |

---

## Verifier API Reference

### Reoon (Primary Verifier — REQUIRED)

```bash
# Power mode — full SMTP + MX + syntax check
curl -s "https://emailverifier.reoon.com/api/v1/verify\
?email=john@example.com&key=$REOON_API_KEY&mode=power"
```

| Field | Value |
|-------|-------|
| Cost | ~$0.003/verification |
| Speed | 2-10s (power mode) |
| Rate limit | 10 req/s |
| Parse | `.status` → valid/invalid/catch_all/disposable/unknown |
| Always use | `mode=power` (quick mode misses too much) |

### Email Verify (Catchall Verifier)

```bash
curl -s "https://api.email-verify.com/api/verify\
?email=john@example.com&key=$EMAILVERIFY_API_KEY"
```

| Field | Value |
|-------|-------|
| Cost | ~$0.003/verification |
| Speed | 1-5s |
| Rate limit | Plan-dependent |
| Parse | `.status` → valid/invalid/risky/unknown |
| Only called for | Catchall results from Reoon |

---

## Rate Limiting & Large Batches

### Per-Provider Delays

| Provider | Min Delay Between Calls | Max Retries |
|----------|------------------------|-------------|
| Tomba | 3s | 3 |
| Muraena | 3s | 2 |
| Icypeas | 1s | 3 |
| Voila Norbert | 2s | 3 |
| Nimbler | 3s | 2 |
| Anymailfinder | 5s | 2 |
| Findymail | 2s | 3 |
| Reoon | 0.5s | 3 |
| Email Verify | 1s | 3 |

### Retry Strategy

```
HTTP 429 (Rate Limited):
  Attempt 1: wait 1s
  Attempt 2: wait 2s
  Attempt 3: wait 4s
  Then: skip provider for this lead

HTTP 5xx (Server Error):
  Retry up to 3 times with exponential backoff
  Then: skip provider for this lead

HTTP 401/403 (Auth Error):
  Do NOT retry
  DISABLE provider for rest of batch
  Log: "Provider [X] auth failed — check API key"
```

### Batch Sizing Guide

| List Size | Batch Size | Batch Delay | Estimated Time | Notes |
|-----------|-----------|-------------|---------------|-------|
| 1-100 | 100 | 2s | 5-20 min | No batching needed |
| 100-1,000 | 100 | 2s | 30-120 min | Standard run |
| 1,000-10,000 | 100 | 3s | 2-8 hours | Checkpoint every batch |
| 10,000-50,000 | 50 | 5s | 8-40 hours | Overnight, split files |

### Checkpoint & Resume

```bash
# Start large batch
python3 $WF_SCRIPTS/enrich.py --input 20k_leads.csv --output enriched.csv \
  --batch-size 50 --batch-delay 5

# If interrupted, resume from where it left off
python3 $WF_SCRIPTS/enrich.py --input 20k_leads.csv --output enriched.csv \
  --batch-size 50 --batch-delay 5 --resume

# Split very large files first
python3 $WF_SCRIPTS/split_csv.py --input 50k_leads.csv --chunk-size 10000
# Creates: chunk_001.csv, chunk_002.csv, ... chunk_005.csv
```

Checkpoint saved after every batch to `enrichment_checkpoint_{filename}.json`.

---

## Confidence Scoring

| Score | Label | How It Got There | Campaign Action |
|-------|-------|-----------------|-----------------|
| 95-100 | Verified | Finder found + Reoon valid | Send freely |
| 90-94 | High | Finder found + Reoon valid (minor flags) | Send freely |
| 80-89 | Catchall-verified | Reoon catchall + Email Verify valid | Send, monitor bounce |
| 70-79 | Catchall-likely | Reoon catchall + Email Verify risky | Drip-send, watch |
| 50-69 | Risky | Catchall unresolved or uncertain | Separate segment |
| 1-49 | Low | Partial verification only | Don't send |
| 0 | Not found | No email found | Manual research |

**Target: 90%+ of enriched leads at confidence 70+.**
**Bounce rate target: < 3% on verified + catchall-verified combined.**

---

## Cost Management

### Per-Lead Cost Estimate

```
Best case (Tomba finds, Reoon verifies):
  $0.01 + $0.003 = $0.013

Typical (2 finders tried, Reoon + some Email Verify):
  $0.01 + $0.02 + $0.003 + ($0.003 × 30%) = ~$0.034

Worst case (all 7 finders, Reoon + Email Verify):
  $0.01+0.02+0.01+0.03+0.08+0.05+0.02+0.003+0.003 = ~$0.226
```

### Cost Controls (config.json)

```json
{
  "cost_limits": {
    "max_per_lead": 0.50,
    "max_per_batch": 500,
    "max_monthly": 2000,
    "warn_at_percent": 80
  }
}
```

---

## Memory Integration

```
BEFORE:
  Read memory/campaigns.md  → which campaigns need leads?
  Read memory/issues.md     → any provider issues logged?

AFTER:
  Update memory/campaigns.md → "[date] enriched X leads, Y% coverage via waterfall"
  Log issues to memory/issues.md → if provider failures, low coverage, high bounce
  Update memory/patterns.md → coverage patterns ("Tomba finds 65% of SaaS leads")
```

---

## Cross-Skill Integration

| Skill | How It Connects |
|-------|----------------|
| Lead Builder / Muraena | Exports raw leads → waterfall enriches with verified emails |
| Instantly | Enriched leads (confidence 70+) imported into campaigns |
| Reporting | Coverage rate + provider stats feed into weekly/monthly reports |
| Niche Scout | New niches need enriched lead lists; coverage rate informs viability |
| A/B Testing | List quality from enrichment affects test validity |

---

## File Structure

```
waterfall-enrichment/
├── SKILL.md                           # This file
├── README.md                          # Quick start
├── references/
│   ├── PROVIDER-API-REFERENCE.md      # Full API docs (9 providers)
│   ├── CATCH-ALL-GUIDE.md             # Catchall handling strategy
│   ├── COST-OPTIMIZATION.md           # Cost structure + optimization
│   ├── ERROR-HANDLING.md              # Errors, retries, recovery
│   └── REPORTING.md                   # Reports and metrics
├── scripts/
│   ├── enrich.py                      # Main enrichment engine
│   ├── enrich_emails.py               # Enrich leads in Google Sheets by finding missing emails
│   ├── report.py                      # Coverage report generator
│   └── split_csv.py                   # Split large CSVs
├── assets/
│   ├── config.json                    # Configuration
│   └── schemas/
│       ├── lead-schema.json           # Input schema
│       └── enriched-lead-schema.json  # Output schema
└── examples/
    └── sample-enrichment.md           # Usage examples
```
