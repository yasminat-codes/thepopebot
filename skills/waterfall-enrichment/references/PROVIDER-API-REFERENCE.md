# Provider API Reference

Complete API documentation for all 9 providers in the waterfall enrichment system.

**Two roles:**
- **Finders** (7): Find email addresses from name + domain
- **Verifiers** (2): Verify found emails are valid and deliverable

---

## FINDERS (Cascade Order)

### 1. Tomba (Primary Finder)

**Purpose:** Email finder by name + domain. Fast, cheap, good hit rate.

**Authentication:**
```bash
# Two keys required
X-Tomba-Key: $TOMBA_API_KEY
X-Tomba-Secret: $TOMBA_SECRET
```

**Find Email:**
```bash
curl -s "https://api.tomba.io/v1/email-finder" \
  -H "X-Tomba-Key: $TOMBA_API_KEY" \
  -H "X-Tomba-Secret: $TOMBA_SECRET" \
  -G -d "domain=example.com&first_name=John&last_name=Doe"
```

**Response:**
```json
{
  "data": {
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "score": 90,
    "verification": {
      "status": "valid",
      "date": "2026-02-23"
    },
    "sources": [...]
  }
}
```

**Parse:** `.data.email` — ignore `.data.verification.status` (use Reoon instead)

| Spec | Value |
|------|-------|
| Cost | ~$0.01/search |
| Speed | 1-5s |
| Rate limit | 20 req/min (free tier), 50 req/min (paid) |
| Min delay | 3s between calls |
| Error codes | 401 (bad key), 429 (rate limit), 404 (not found) |

**Domain Search (bonus — find all emails at a domain):**
```bash
curl -s "https://api.tomba.io/v1/domain-search?domain=example.com" \
  -H "X-Tomba-Key: $TOMBA_API_KEY" \
  -H "X-Tomba-Secret: $TOMBA_SECRET"
```

---

### 2. Muraena

**Purpose:** Email finder with broad database coverage.

**Authentication:**
```bash
Authorization: Bearer $MURAENA_API_KEY
```

**Find Email:**
```bash
curl -s -X POST "https://api.muraena.ai/v1/email-finder" \
  -H "Authorization: Bearer $MURAENA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain":"example.com"}'
```

**Response:**
```json
{
  "email": "john.doe@example.com",
  "confidence": 85,
  "sources": ["linkedin", "website"]
}
```

**Parse:** `.email`

| Spec | Value |
|------|-------|
| Cost | ~$0.02/search |
| Speed | 2-10s |
| Rate limit | Plan-dependent |
| Min delay | 3s between calls |
| Note | Business plan required ($149+/month) |

---

### 3. Icypeas

**Purpose:** Lead enrichment + email finding. Supports bulk mode.

**Authentication:**
```bash
Authorization: Bearer $ICYPEAS_API_KEY
# Some endpoints also need: X-API-Secret: $ICYPEAS_API_SECRET
```

**Single Search:**
```bash
curl -s -X POST "https://app.icypeas.com/api/email-search" \
  -H "Authorization: Bearer $ICYPEAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain_name":"example.com"}'
```

**Bulk Search (for batches of 50+):**
```bash
curl -s -X POST "https://app.icypeas.com/api/bulk-search" \
  -H "Authorization: Bearer $ICYPEAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [
      {"first_name":"John","last_name":"Doe","domain_name":"example.com"},
      {"first_name":"Jane","last_name":"Smith","domain_name":"acme.com"}
    ]
  }'
```

**Response (single):**
```json
{
  "email": "john.doe@example.com",
  "status": "found",
  "domain_type": "corporate"
}
```

**Parse:** `.email`

| Spec | Value |
|------|-------|
| Cost | ~$0.01/search |
| Speed | 1-5s (single), async (bulk) |
| Rate limit | 10 req/s (single), 1 req/s (bulk) |
| Min delay | 1s between calls |
| Bulk | Use bulk endpoint for 50+ leads in a batch |

---

### 4. Voila Norbert

**Purpose:** Email search with good accuracy.

**Authentication:** HTTP Basic Auth (API key as username, empty password)
```bash
-u "$VOILANORBERT_API_KEY:"
```

**Find Email:**
```bash
curl -s -X POST "https://api.voilanorbert.com/2018-01-08/search/name" \
  -u "$VOILANORBERT_API_KEY:" \
  -d "name=John Doe&domain=example.com"
```

**Response:**
```json
{
  "email": {
    "email": "john.doe@example.com",
    "score": 85
  },
  "searching": false
}
```

**Parse:** `.email.email`
**Note:** If `searching: true`, the search is async. Poll again after 10s.

| Spec | Value |
|------|-------|
| Cost | ~$0.03/search |
| Speed | 1-10s (may be async) |
| Rate limit | Plan-dependent |
| Min delay | 2s between calls |
| Async | Check `searching` field — poll if true |

---

### 5. Nimbler

**Purpose:** Deep B2B contact enrichment. Returns 50+ data fields beyond email.

**Authentication:**
```bash
Authorization: Bearer $NIMBLER_API_KEY
```

**Enrich Contact:**
```bash
curl -s -X POST "https://api.nimbler.com/v1/enrich" \
  -H "Authorization: Bearer $NIMBLER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","company_domain":"example.com"}'
```

**Response:**
```json
{
  "work_email": "john.doe@example.com",
  "personal_email": "john.d@gmail.com",
  "phone": "+1-555-0123",
  "title": "VP of Sales",
  "linkedin_url": "linkedin.com/in/johndoe",
  "company": {
    "name": "Example Corp",
    "industry": "SaaS",
    "size": "50-200",
    "revenue": "$10M-$50M"
  }
}
```

**Parse:** `.work_email` (prefer work email, fall back to personal_email)
**Bonus:** Save extra fields (phone, title, company data) for enrichment even if we already have email from an earlier finder.

| Spec | Value |
|------|-------|
| Cost | ~$0.08/search (most expensive finder) |
| Speed | 2-5s |
| Rate limit | Plan-dependent |
| Min delay | 3s between calls |
| Extra data | Phone, social, company details |

---

### 6. Anymailfinder

**Purpose:** Email discovery via real-time scraping + SMTP probing.

**Authentication:**
```bash
Authorization: Bearer $ANYMAILFINDER_API_KEY
```

**Find Email:**
```bash
curl -s -X POST "https://api.anymailfinder.com/v5.1/find-email/person" \
  -H "Authorization: Bearer $ANYMAILFINDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain":"example.com"}'
```

**Response:**
```json
{
  "email": "john.doe@example.com",
  "email_class": "verified",
  "alternatives": ["j.doe@example.com"]
}
```

**Parse:** `.email`
**Note:** `email_class` can be "verified", "catchall", "guessed" — but still verify with Reoon.

| Spec | Value |
|------|-------|
| Cost | ~$0.05/search |
| Speed | 2-120s (real-time scraping can be slow) |
| Rate limit | Queue-based (no hard per-second limit) |
| Min delay | 5s between calls |
| Timeout | Set 120s timeout for this provider |

---

### 7. Findymail (Last Resort)

**Purpose:** Email finding service.

**Authentication:**
```bash
Authorization: Bearer $FINDYMAIL_API_KEY
```

**Find Email:**
```bash
curl -s -X POST "https://app.findymail.com/api/search/name" \
  -H "Authorization: Bearer $FINDYMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","domain":"example.com"}'
```

**Response:**
```json
{
  "email": "john.doe@example.com",
  "confidence": 80
}
```

**Parse:** `.email`

| Spec | Value |
|------|-------|
| Cost | ~$0.02/search |
| Speed | 1-5s |
| Rate limit | Plan-dependent |
| Min delay | 2s between calls |

---

## VERIFIERS

### Reoon Email Verifier (Primary — REQUIRED)

**Purpose:** Verifies every email found by any finder. Source of truth for validity.

**Authentication:** API key as query parameter

**Verify Email (Power Mode):**
```bash
curl -s "https://emailverifier.reoon.com/api/v1/verify\
?email=john@example.com&key=$REOON_API_KEY&mode=power"
```

**Response:**
```json
{
  "status": "valid",
  "is_catchall": false,
  "mx_found": true,
  "smtp_check": true,
  "is_disposable": false,
  "is_role_account": false,
  "reason": "Mailbox exists"
}
```

**Status Mapping:**

| Reoon Status | Action | Confidence |
|-------------|--------|-----------|
| `valid` | Add to DB | 90-100 |
| `invalid` | Discard | 0 |
| `catch_all` | Send to Email Verify | Pending |
| `disposable` | Discard | 0 |
| `unknown` | Treat as catchall → Email Verify | Pending |

**Modes:**
- `quick` — Syntax + MX only. Fast but misses a lot. Don't use for enrichment.
- `power` — Full SMTP probe. Slower but accurate. **Always use this.**

| Spec | Value |
|------|-------|
| Cost | ~$0.003/verification |
| Speed | 0.5s (quick), 2-10s (power) |
| Rate limit | 10 req/s |
| Min delay | 0.5s between calls |

---

### Email Verify (Catchall Verifier)

**Purpose:** Second-opinion verification for catchall domains. Only called when Reoon returns catchall/unknown.

**Verify Email:**
```bash
curl -s "https://api.email-verify.com/api/verify\
?email=john@example.com&key=$EMAILVERIFY_API_KEY"
```

**Response:**
```json
{
  "status": "valid",
  "catch_all": true,
  "disposable": false,
  "free_email": false
}
```

**Status Mapping:**

| Email Verify Status | Action | Confidence |
|--------------------|--------|-----------|
| `valid` | Add to DB (catchall-verified) | 70-85 |
| `risky` | Add to risky list | 50-65 |
| `invalid` | Discard | 0 |
| `unknown` | Add to risky list | 40 |

| Spec | Value |
|------|-------|
| Cost | ~$0.003/verification |
| Speed | 1-5s |
| Rate limit | Plan-dependent |
| Min delay | 1s between calls |

---

## Environment Variables Summary

```bash
# FINDERS (at least 1 required, more = better coverage)
TOMBA_API_KEY=
TOMBA_SECRET=
MURAENA_API_KEY=
ICYPEAS_API_KEY=
ICYPEAS_API_SECRET=
VOILANORBERT_API_KEY=
NIMBLER_API_KEY=
ANYMAILFINDER_API_KEY=
FINDYMAIL_API_KEY=

# VERIFIERS (Reoon required, Email Verify recommended)
REOON_API_KEY=          # REQUIRED — primary verifier
EMAILVERIFY_API_KEY=    # Recommended — catchall resolver
```
