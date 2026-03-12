# Troubleshooting — trends-scraper

Indexed by symptom. Fix first, investigate second.

---

## `ResponseError: 429` from pytrends

**Cause:** Google rate-limited the IP. Expected on busy VPS IPs.
**Fix:** The script handles this automatically — sleeps 60s, raises `PyTrendsRateLimitError`, escalates remaining keywords to SERP API.
**If it's not being caught:** Check pytrends version. Older versions raise a different exception class.

```bash
pip show pytrends  # should be >= 4.9.2
pip install --upgrade pytrends
```

---

## `interest_over_time()` returns empty DataFrame

**Cause:** Keyword has no measurable Google Trends signal in the requested period. Low-volume or brand-new terms.
**Fix:** Handled automatically — `df.empty` check returns `interest_score=0`, `direction='stable'`. Not an error.
**Action if unexpected:** Verify keyword spelling. Try it manually on trends.google.com.

---

## `related_queries()` returns None for a keyword

**Cause:** Keyword doesn't have enough search volume for Google to compute related queries. Normal for niche terms.
**Fix:** Handled automatically — returns `related_queries: []`. Not an error.

---

## `KeyError: SERP_API_KEY`

**Cause:** `SERP_API_KEY` not in `shared/.env`, or `.env` not loading correctly.
**Fix:**
```bash
grep SERP_API_KEY /home/clawdbot/shared/.env
```
If missing, add it. The script will log a clear error and attempt Tier 3 instead.

---

## `SERP API error: Your account credit balance is too low`

**Cause:** SERP API account out of credits.
**Fix:** Top up SERP API credits. In the meantime, the script logs the error and returns empty results — Tier 3 (Apify) will attempt if available.

---

## SERP API returns HTTP 401

**Cause:** Invalid or expired API key.
**Fix:** Check `SERP_API_KEY` value in `shared/.env`. Verify key is active at serpapi.com.

---

## `industry_trends` insert conflict (ON CONFLICT)

**Cause:** Same `(trend_name, week_of)` already exists from a previous run this week.
**Fix:** Not an error. The upsert updates `signal_strength`, `evidence`, `last_checked_date`, `run_id`. Check that the `ON CONFLICT (trend_name, week_of)` constraint exists on the table:

```sql
SELECT conname FROM pg_constraint WHERE conrelid = 'industry_trends'::regclass;
```

If the constraint doesn't exist, add it:
```sql
ALTER TABLE industry_trends ADD CONSTRAINT uq_trend_week UNIQUE (trend_name, week_of);
```

---

## All keywords score < 0.5 niche relevance

**Cause:** Usually one of: (a) analysis prompt file not loading correctly, (b) keywords too generic, (c) GPT-4o response parsed incorrectly.
**Fix:**
1. Check `ANALYSIS_PROMPT_PATH` file exists:
   ```bash
   ls -la /home/clawdbot/workspace-suwaida/skills/linkedin-content-intelligence/references/analysis-prompts-trends.md
   ```
2. Run with `--dry-run` and check log for "GPT-4o analysis complete: X keyword objects"
3. If X=0, GPT returned malformed JSON — check OPENROUTER_API_KEY is valid
4. If keywords are generic consumer terms, that's correct filter behavior

---

## pytrends returns NaN values

**Cause:** Partial data for the current period (`isPartial=True`), or keyword has sparse data.
**Fix:** Handled automatically — `.fillna(0)` applied before `.mean()`. NaN becomes 0.

---

## GPT-4o returns malformed JSON

**Cause:** Rare — model sometimes wraps response in markdown code blocks despite `json_object` format.
**Fix:** Check the raw response in logs (logged at ERROR level). If this happens repeatedly:
1. Add a pre-parse step to strip ```json ... ``` wrappers
2. Consider adding a retry with `temperature=0`

---

## Apify actor `epctex/google-trends-scraper` deprecated or not found

**Cause:** Actor removed from Apify Store or renamed.
**Fix:**
1. Search Apify Store for "google trends" — find current best actor
2. Update `actor_id` in `assets/config.json`
3. Test new actor input/output schema
4. Update `apify_client.py`'s `fetch_apify_trends()` parser for new schema
5. Update `references/apify-actors.md` with new findings

---

## `niche-keywords.json` missing

**Cause:** `workspace-suwaida/skills/linkedin-content-intelligence/assets/niche-keywords.json` doesn't exist yet.
**Fix:** Not a crash — the script logs a warning and proceeds with the base 10 keywords from `default-keywords.json`. Create the niche-keywords.json file when ready. See REQUIREMENTS.md for expected format.

---

## `OPENROUTER_API_KEY` not found

**Cause:** `OPENROUTER_API_KEY` is not set in `shared/.env`.
**Fix:**
```bash
grep OPENROUTER_API_KEY /home/clawdbot/shared/.env
```
GPT-4o analysis routes through OpenRouter. This key is required — the script will exit 1 without it.
