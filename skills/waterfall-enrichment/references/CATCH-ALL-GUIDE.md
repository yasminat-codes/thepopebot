# Catch-All Domain Handling

How to handle catch-all (accept-all) domains in the waterfall enrichment pipeline.

---

## What Is a Catch-All Domain?

A catch-all domain accepts email to ANY address at that domain — even addresses that don't exist. This means:
- `john@example.com` → accepted
- `asdf1234@example.com` → also accepted
- You can't tell if a specific mailbox actually exists

**Risk:** Sending to a catch-all address that doesn't really exist often results in:
- Soft bounces (mail accepted but nobody reads it)
- Hard bounces after delay (some servers accept then bounce later)
- 5-15% bounce rate vs < 1% for verified addresses

---

## How Catch-Alls Flow Through the Waterfall

```
Finder finds email → Reoon verifies
                        │
                   ┌────┴────┐
                   │         │
                VALID    CATCHALL
                   │         │
                   ▼         ▼
                  DB    Email Verify
                        ┌────┴────┐
                        │         │
                     VALID     INVALID/RISKY
                        │         │
                        ▼         ▼
                    DB (flagged)  Risky list or discard
```

**Reoon detects catch-all via:** `is_catchall: true` in response.
**Email Verify resolves by:** Additional SMTP probing + pattern analysis.

---

## Detection Methods

### 1. Provider-Reported (Primary)

Each provider has different catch-all detection:

| Provider | Catch-All Field | How to Check |
|----------|----------------|-------------|
| Reoon | `is_catchall` | Boolean in response |
| Tomba | `verification.status` | "accept_all" |
| Icypeas | `status` | "catchall" |
| Anymailfinder | `email_class` | "catchall" |
| Email Verify | `catch_all` | Boolean in response |

### 2. SMTP Probe (What Reoon/Email Verify Do)

Verifiers send a probe to a random address at the domain (e.g., `xq3j7f@example.com`).
- If the server accepts it → catch-all domain
- If the server rejects it → not catch-all, individual mailbox check is reliable

---

## Confidence Scoring for Catch-All

| Scenario | Confidence | Bucket |
|----------|-----------|--------|
| Finder found + Reoon valid (not catchall) | 90-100 | VERIFIED |
| Finder found + Reoon catchall + Email Verify valid | 80-85 | CATCHALL-VERIFIED |
| Finder found + Reoon catchall + Email Verify risky | 55-65 | RISKY |
| Finder found + Reoon catchall + Email Verify invalid | 0 | DISCARD |
| Finder found + Reoon catchall + no Email Verify key | 50 | RISKY |
| Finder found + Reoon unknown | 50 | Treated as catchall |

---

## Campaign Strategy by Bucket

### VERIFIED (90-100) — Send Freely

- Import directly into Instantly campaigns
- Full volume, normal cadence
- Expected bounce: < 1%

### CATCHALL-VERIFIED (70-85) — Send with Monitoring

- Import into campaigns but flag as catchall
- Monitor bounce rate closely for first 100 sends
- If bounce > 5% from this segment: pause, review, tighten
- Expected bounce: 2-5%

### RISKY (50-69) — Drip with Caution

- Separate segment in Instantly
- Send at 20-30% of normal volume
- Monitor bounce rate aggressively
- If bounce > 8%: stop sending to this segment
- Consider: is it worth the risk?
- Expected bounce: 5-15%

### NOT VERIFIED (< 50) — Don't Send

- Don't import into campaigns
- Hold for manual verification or discard
- May attempt re-enrichment after 30 days (data freshens)

---

## Common Catch-All Domains

Some domains are well-known catch-alls:

- Many small businesses use catch-all (especially on Zoho, custom SMTP)
- Enterprise domains (100+ employees) are usually NOT catch-all
- Government domains (.gov) are almost never catch-all
- Education domains (.edu) sometimes are

**Pattern:** If catch-all rate is > 30% for a niche, the niche may use email hosting that defaults to catch-all. Adjust expectations.

---

## Bounce Rate Management

```
TARGET: < 3% overall bounce rate per campaign

CALCULATION:
  verified_bounce = verified_count × 0.005       (0.5%)
  catchall_verified_bounce = cv_count × 0.03     (3%)
  risky_bounce = risky_count × 0.10              (10%)

  total_bounce = (verified_bounce + cv_bounce + risky_bounce) / total_sends

EXAMPLE (1000 leads):
  700 verified (bounce ~3.5)
  200 catchall-verified (bounce ~6)
  100 risky (bounce ~10)
  Total bounce: 19.5 / 1000 = 1.95% ← acceptable

IF RISKY SEGMENT IS TOO LARGE:
  Drop risky leads. 3% bounce rate is the hard ceiling.
```

---

## When Email Verify Key Is Not Set

If `EMAILVERIFY_API_KEY` is not configured:

1. All catch-all results from Reoon go directly to RISKY bucket (confidence 50)
2. No second verification attempt
3. Coverage drops slightly, but safety is maintained
4. Recommendation: get Email Verify key for better catch-all resolution

---

## Re-Enrichment Strategy

For leads stuck in catch-all/risky:

1. Wait 30 days
2. Re-run through Reoon only (domains may have changed configuration)
3. Some catch-all domains become non-catch-all after admin changes
4. Some "unknown" results clear up with fresh data
5. Don't re-run more than once — if still catch-all after 2 attempts, accept it
