# Decision Trees — trends-scraper

## Which tier is running? [Medium freedom — log-guided]

```
Check logs for:
├─ "Batch X/Y complete — Z keywords via pytrends"  → Tier 1 active
├─ "pytrends 429 at batch X — escalating"          → Tier 2 activating
├─ "SERP API: 'keyword' → score=..."               → Tier 2 active
├─ "Apify Tier 3:"                                 → Tier 3 active
└─ "Apify Tier 3 failed: ..."                      → All tiers failed for some keywords
```

## Should I adjust the niche threshold? [High freedom — agent decision]

```
All keywords passing (>25/30)?
├─ Yes → threshold may be too low; raise to 0.6 or 0.7 for stricter quality
└─ No
   ├─ 10–20 passing → expected range; threshold is calibrated
   └─ <10 passing?
       ├─ Check keywords are AI-consulting-relevant (not generic)
       ├─ Verify GPT prompt is loading from correct path
       └─ Consider lowering to 0.4 temporarily and reviewing outputs
```

## Dry run shows unexpected results? [Low freedom — check config]

```
Unexpected output?
├─ Keywords missing → check niche-keywords.json path, check max cap
├─ All scores 0.0 → pytrends returned empty DataFrames; check IP rate limiting
├─ GPT output empty → OPENROUTER_API_KEY missing or malformed; check env
└─ Shelf life all 'evergreen' → GPT prompt may not be receiving trend data correctly
```

## Real-World Scenarios

### Scenario 1: Normal Monday Pipeline Run

**Input:** `pipeline.py` calls `trends_scraper.py --run-id abc-123 --week-of 2026-02-23`

**Process:**
1. Loads 10 base + 18 niche keywords = 28 total
2. 6 batches through pytrends (US + GB) — completes in ~20s with sleep intervals
3. GPT-4o scores all 28 keywords in one call — ~$0.03
4. 19 of 28 pass niche filter (threshold=0.5)
5. 19 rows upserted to `industry_trends`

**Output:** 19 rows for week_of=2026-02-23, run_id=abc-123. Log: `"source=pytrends | keywords=28 | passed_filter=19 | rows_written=19"`
**Cost:** pytrends (free), GPT-4o (~$0.03), Neon (connection only)

### Scenario 2: pytrends Rate-Limited at Batch 3

**Input:** Same as Scenario 1. Google 429s during batch 3 (keywords 11–15).

**Process:**
1. Batches 0–2 complete via pytrends (keywords 1–10 have data)
2. Batch 3 hits 429 → sleep(60) → `PyTrendsRateLimitError`
3. Remaining keywords (11–28) sent to SERP API — 18 keywords × 2 geos = 36 calls (~$0.18)
4. Results merged: 10 from pytrends + 18 from SERP API = 28 total
5. 17 of 28 pass filter and are written

**Output:** 17 rows. Log: `"source=pytrends+serp_api | keywords=28 | passed_filter=17 | rows_written=17"`
**Cost:** pytrends (2 batches), SERP API (~$0.18), GPT-4o (~$0.03)
