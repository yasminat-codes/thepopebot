# Cost Optimization Guide

Strategies for minimizing enrichment costs while maximizing coverage.

---

## Cost Per Provider

### Finders (Cascade Order = Cost Order)

| # | Provider | Cost/Search | Why This Position |
|---|----------|------------|-------------------|
| 1 | Tomba | ~$0.01 | Cheapest finder, good hit rate |
| 2 | Muraena | ~$0.02 | Good coverage, reasonable cost |
| 3 | Icypeas | ~$0.01 | Cheap, supports bulk |
| 4 | Voila Norbert | ~$0.03 | Mid-range, reliable |
| 5 | Nimbler | ~$0.08 | Expensive but returns extra data |
| 6 | Anymailfinder | ~$0.05 | Thorough but slow |
| 7 | Findymail | ~$0.02 | Last resort |

### Verifiers

| Provider | Cost/Verification | When Called |
|----------|------------------|------------|
| Reoon | ~$0.003 | Every found email (mandatory) |
| Email Verify | ~$0.003 | Catchall results only (~20-30% of found) |

**Cascade order is optimized for cheapest-first.** Most leads are found by Tomba or Muraena, keeping average cost low.

---

## Cost Scenarios

### Per-Lead Estimates

| Scenario | What Happens | Cost |
|----------|-------------|------|
| Best case | Tomba finds + Reoon verifies | $0.013 |
| Common | 2 finders tried + Reoon | $0.033 |
| Average | 3 finders + Reoon + some EV | $0.044 |
| Hard lead | 5 finders + Reoon + EV | $0.153 |
| Worst case | All 7 finders + Reoon + EV | $0.226 |
| Not found | All 7 finders, no email | $0.220 (all finder costs, no verifier) |

### Batch Estimates

| Leads | Best Case | Average | Worst Case |
|-------|----------|---------|-----------|
| 500 | $7 | $22 | $113 |
| 1,000 | $13 | $44 | $226 |
| 5,000 | $65 | $220 | $1,130 |
| 10,000 | $130 | $440 | $2,260 |
| 20,000 | $260 | $880 | $4,520 |
| 50,000 | $650 | $2,200 | $11,300 |

---

## Optimization Strategies

### 1. Cascade Stops on First Find

The waterfall stops the moment any finder returns an email. If Tomba finds it (60% of the time for good B2B lists), you never pay for providers 2-7. This is the biggest cost saver by design.

### 2. Pre-Filter Dead Domains

Before entering the waterfall, check if the domain has MX records:

```bash
# Quick MX check
dig +short MX example.com
```

If no MX records → skip the entire waterfall for this lead. Dead domain = no email to find.
Saves the cost of hitting all 7 finders on an impossible lead.

### 3. Skip Known Personal Domains

Don't waste finder credits on gmail.com, yahoo.com, hotmail.com, etc. These are personal email providers — finders can't determine work email from a personal domain.

### 4. Deduplicate Before Enriching

Same person at same domain = same result. Deduplicate by `(first_name + last_name + domain)` before starting the waterfall. Duplicate leads = wasted credits.

### 5. Use Bulk Endpoints Where Available

Icypeas supports bulk search — cheaper per-lead than single API calls. When processing batches of 50+, use the bulk endpoint.

### 6. Configure Cost Limits

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

The enrichment script tracks estimated costs and stops when limits are approached.

### 7. Provider Rotation for Cost Control

If one provider is hitting rate limits frequently (slowing down the batch), temporarily skip it rather than waiting. The next provider may be more available.

### 8. Selective Re-Enrichment

Don't re-enrich leads that were already found. Only re-run the waterfall for:
- Leads where no email was found (status: not_found)
- Leads where email bounced in campaigns (may need fresh lookup)
- Leads older than 6 months (data freshness)

---

## Cost Tracking

The enrichment script tracks costs in real-time:

```
After each batch:
  - Provider call count per provider
  - Estimated cost per provider
  - Running total cost
  - Projected total cost for remaining leads
  - Cost per found email (total cost / emails found)
```

### Cost Report (from report.py)

```
COST BREAKDOWN:
  Tomba:          4,200 calls × $0.01  = $42.00  (found 2,520)
  Muraena:        1,680 calls × $0.02  = $33.60  (found 672)
  Icypeas:        1,008 calls × $0.01  = $10.08  (found 302)
  Voila Norbert:    706 calls × $0.03  = $21.18  (found 212)
  Nimbler:          494 calls × $0.08  = $39.52  (found 148)
  Anymailfinder:    346 calls × $0.05  = $17.30  (found 104)
  Findymail:        242 calls × $0.02  = $4.84   (found 48)
  Reoon:          4,006 calls × $0.003 = $12.02  (verifications)
  Email Verify:   1,202 calls × $0.003 = $3.61   (catchall checks)

  TOTAL: $184.15 for 5,000 leads
  Cost per lead: $0.037
  Cost per found email: $0.046
  Coverage: 80.1% (4,006 / 5,000)
```

---

## When to Optimize vs When to Spend

| Situation | Strategy |
|-----------|----------|
| Testing a new niche (< 500 leads) | Use all providers, optimize later |
| Scaling a proven niche (1,000+) | Track provider hit rates, disable low performers |
| Budget is tight | Reduce cascade to top 3-4 finders |
| Coverage is critical (high-value niche) | Use all 7 finders, accept higher cost |
| Re-enriching old leads | Only re-run not_found and bounced leads |
