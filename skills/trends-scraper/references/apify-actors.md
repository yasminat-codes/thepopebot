# Apify Actors — Google Trends

**Status:** ACTOR NOT YET VERIFIED — this file must be updated after pre-build research.

---

## Primary Candidate: epctex/google-trends-scraper

**Actor ID:** `epctex/google-trends-scraper`
**Apify Store URL:** https://apify.com/epctex/google-trends-scraper
**Verification status:** UNVERIFIED — check before building Tier 3

### Pre-Build Verification Checklist

Before using this actor in production:
1. Open https://apify.com/epctex/google-trends-scraper
2. Confirm actor still exists and was updated within the last 6 months
3. Check pricing: compute units per run, estimated cost for 30 keywords
4. Verify input schema matches the template below
5. Run a test with 3 keywords, inspect raw output schema
6. Update this file with confirmed findings and date researched

---

## Expected Input Schema (verify against actual)

```json
{
  "queries": ["AI consulting", "LLM deployment"],
  "geo": "US",
  "timeframe": "today 1-m",
  "maxItems": 100
}
```

Fields `queries`, `geo`, `timeframe` are standard — confirm exact field names against the actor's published input schema.

---

## Expected Output Schema (verify against actual)

Each result item expected to contain:

| Field | Expected Type | Notes |
|-------|--------------|-------|
| `query` or `keyword` | string | The keyword searched |
| `timelineData` or `interest_over_time` | array | Time-series data points |
| `risingRelatedQueries` | array | Rising related searches |

**Actual field names may differ** — inspect raw output from a test run and update `apify_client.py`'s `fetch_apify_trends()` parser accordingly.

---

## Alternative Actor: apify/google-trends-scraper

**Actor ID:** `apify/google-trends-scraper` (official Apify-maintained, if it exists)
**Apify Store URL:** https://apify.com/apify/google-trends-scraper
**Verification status:** UNVERIFIED — check if it exists; may be lower cost as official actor

**Selection criteria for any actor:**
- Updated within last 6 months
- Pay-per-result pricing preferred over flat compute units
- Under $0.005 per keyword in practice
- Input accepts keyword array (not single keyword only)

---

## Pricing Estimate (update after verification)

| Scenario | Actor | Est. Cost |
|----------|-------|-----------|
| 30 keywords, 1 run | epctex/google-trends-scraper | TBD |
| 30 keywords, 1 run | apify/google-trends-scraper | TBD |

**Budget constraint:** Tier 3 is a last resort. If any actor costs > $0.20/run, document clearly. Acceptable because Tier 3 should activate < once per month.

---

## Actor Selection Decision

Update this section after verification:
- **Chosen actor:** TBD
- **Date verified:** TBD
- **Verified by:** TBD
- **Test run ID:** TBD
- **Confirmed cost per 30-keyword run:** TBD
- **Input schema confirmed:** TBD
- **Output schema confirmed:** TBD

---

## Config Reference

The chosen actor ID is read from `assets/config.json`:
```json
{
  "apify": {
    "actor_id": "epctex/google-trends-scraper"
  }
}
```

Update `actor_id` in config.json after verification if a different actor is selected.
