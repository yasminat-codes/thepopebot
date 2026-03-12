# Reporting & Metrics

Coverage reports and enrichment metrics for waterfall enrichment runs.

---

## Report Generation

After enrichment, generate a report:

```bash
python3 {baseDir}/scripts/report.py --input enriched.csv
```

### Sample Report Output

```
============================================
  WATERFALL ENRICHMENT REPORT
  Generated: 2026-02-23 10:30:00
============================================

COVERAGE SUMMARY
  Total leads:         5,000
  Emails found:        4,006 (80.1%)
  Verified (safe):     3,204 (64.1%)
  Catchall-verified:   562 (11.2%)
  Risky (catchall):    240 (4.8%)
  Not found:           994 (19.9%)

FINDER PERFORMANCE
  Provider          Searched  Found   Hit Rate  Avg Time  Cost Est
  ────────────────────────────────────────────────────────────────
  Tomba             5,000     2,520   50.4%     1.8s      $50.00
  Muraena           2,480     672     27.1%     4.2s      $49.60
  Icypeas           1,808     302     16.7%     2.1s      $18.08
  Voila Norbert     1,506     212     14.1%     5.3s      $45.18
  Nimbler           1,294     148     11.4%     3.1s      $103.52
  Anymailfinder     1,146     104     9.1%      18.5s     $57.30
  Findymail         1,042     48      4.6%      2.4s      $20.84
  ────────────────────────────────────────────────────────────────
  TOTAL FINDS                 4,006   80.1%               $344.52

VERIFIER PERFORMANCE
  Provider          Verified  Catchall  Invalid  Unknown  Cost Est
  ────────────────────────────────────────────────────────────────
  Reoon (primary)   3,204     562       200      40       $12.02
  Email Verify      562       —         120      80       $2.28
  ────────────────────────────────────────────────────────────────
  TOTAL VERIFICATIONS                                     $14.30

COST BREAKDOWN
  Finders total:     $344.52
  Verifiers total:   $14.30
  GRAND TOTAL:       $358.82
  Cost per lead:     $0.072
  Cost per found:    $0.090

CONFIDENCE DISTRIBUTION
  90-100 (verified):     3,204  (64.1%)
  70-89 (catchall-ok):   562    (11.2%)
  50-69 (risky):         240    (4.8%)
  0 (not found):         994    (19.9%)

TOP CATCHALL DOMAINS
  smallbiz.io           — 42 leads
  startup.co            — 28 leads
  agency.com            — 19 leads
  consulting.co         — 15 leads
  designs.io            — 12 leads

BOUNCE RISK ESTIMATE
  Verified segment:    ~0.5% bounce (3,204 leads)
  Catchall-verified:   ~3% bounce (562 leads)
  Risky segment:       ~10% bounce (240 leads)
  Blended estimate:    1.8% (target: <3%)
  Status:              WITHIN TARGET

============================================
```

---

## Metrics Tracked

### Per-Run Metrics

| Metric | Description |
|--------|-------------|
| `total_leads` | Total leads in input |
| `emails_found` | Leads where any finder returned an email |
| `verified_count` | Emails that Reoon confirmed as valid |
| `catchall_verified_count` | Catchall emails that Email Verify confirmed |
| `risky_count` | Catchall emails unresolved (no EV key or EV returned risky) |
| `not_found_count` | Leads where no finder found an email |
| `coverage_rate` | % of leads with email found |
| `verification_rate` | % of found emails that Reoon verified as valid |

### Per-Finder Metrics

| Metric | Description |
|--------|-------------|
| `searched` | Number of leads sent to this finder |
| `found` | Emails found by this finder |
| `hit_rate` | found / searched |
| `avg_response_time` | Average API response time |
| `error_count` | Number of errors from this finder |
| `cost_estimate` | Estimated cost (searched × cost_per_search) |

### Per-Verifier Metrics

| Metric | Description |
|--------|-------------|
| `verified` | Emails confirmed valid |
| `catchall` | Emails flagged as catchall |
| `invalid` | Emails rejected as invalid |
| `unknown` | Emails with unknown status |
| `cost_estimate` | Estimated cost (calls × cost_per_verify) |

### Cumulative Metrics (Cross-Run Trends)

Track across multiple runs to optimize:

| Metric | Why It Matters |
|--------|----------------|
| Finder hit rate trend | Identify declining finders — demote or disable |
| Cost per verified email trend | Optimize cascade order |
| Catchall rate by niche | Adjust expectations per ICP |
| Coverage by industry | Target high-coverage niches |
| Reoon rejection rate | Detect data quality issues upstream |
| Email Verify resolution rate | Evaluate if EV key is worth the cost |

---

## Output Formats

### CSV Output Columns

```csv
first_name,last_name,company,domain,email,confidence,finder_source,verification_status,catch_all,ev_status,status,enriched_at
John,Doe,Acme,acme.com,john@acme.com,95,tomba,valid,false,,verified,2026-02-23T10:30:00Z
Jane,Smith,Globex,globex.com,jane@globex.com,80,muraena,catchall,true,valid,catchall_verified,2026-02-23T10:30:01Z
Bob,Jones,FooCorp,foo.com,,0,,,,,,not_found,2026-02-23T10:30:15Z
Alice,Brown,StartUp,startup.io,alice@startup.io,50,icypeas,catchall,true,risky,risky,2026-02-23T10:30:18Z
```

**Column definitions:**

| Column | Description |
|--------|-------------|
| `finder_source` | Which finder found the email (tomba, muraena, icypeas, etc.) |
| `verification_status` | Reoon result: valid, invalid, catchall, unknown |
| `catch_all` | Whether Reoon flagged domain as catchall |
| `ev_status` | Email Verify result (only for catchall): valid, risky, invalid, unknown, empty |
| `status` | Final status: verified, catchall_verified, risky, not_found, invalid_input |
| `confidence` | Final confidence score (90-100 verified, 70-85 catchall-ok, 50-69 risky, 0 not found) |

### JSON Output Format

```json
{
  "metadata": {
    "run_id": "enrich-2026-02-23-103000",
    "total_leads": 5000,
    "coverage_rate": 0.801,
    "timestamp": "2026-02-23T10:30:00Z"
  },
  "results": [
    {
      "input": {"first_name": "John", "last_name": "Doe", "company": "Acme", "domain": "acme.com"},
      "email": "john@acme.com",
      "confidence": 95,
      "finder_source": "tomba",
      "verification_status": "valid",
      "catch_all": false,
      "ev_status": null,
      "status": "verified"
    }
  ],
  "report": {
    "finders": {
      "tomba": {"searched": 5000, "found": 2520, "hit_rate": 0.504, "cost": 50.00},
      "muraena": {"searched": 2480, "found": 672, "hit_rate": 0.271, "cost": 49.60}
    },
    "verifiers": {
      "reoon": {"verified": 3204, "catchall": 562, "invalid": 200, "cost": 12.02},
      "emailverify": {"verified": 562, "risky": 120, "invalid": 80, "cost": 2.28}
    },
    "cost_estimate": {"finders": 344.52, "verifiers": 14.30, "total": 358.82, "per_lead": 0.072}
  }
}
```

---

## Interpreting Results

### Coverage Rate Benchmarks

| Rate | Assessment | Action |
|------|------------|--------|
| 85%+ | Excellent | Ready for campaign |
| 70-84% | Good | Review not-found leads — bad domains? |
| 55-69% | Moderate | Check data quality, try additional sources manually |
| <55% | Poor | Data quality issue — wrong domains, bad names, or niche issue |

### Finder Efficiency

| Hit Rate | Assessment | Action |
|----------|------------|--------|
| >30% | Strong | Keep in cascade |
| 15-30% | Average | Monitor — may be redundant with earlier finders |
| 5-14% | Marginal | Consider cost vs marginal coverage gain |
| <5% | Weak | Consider disabling to save cost |

### Bounce Risk Assessment

| Estimated Bounce | Risk | Action |
|-----------------|------|--------|
| <1% | Very Low | Send all segments |
| 1-3% | Low | Send with monitoring |
| 3-5% | Moderate | Drop risky segment, send verified + catchall-verified only |
| >5% | High | Re-verify list. Drop catchall-verified if needed. |

### When to Optimize Cascade Order

Review after every 5,000+ leads enriched:
- If finder #3 has higher hit rate than finder #2 → swap them
- If a finder's hit rate drops below 5% → consider removing
- If a finder's cost per marginal email exceeds $0.20 → consider removing
- If Reoon rejection rate exceeds 15% → data quality issue upstream
