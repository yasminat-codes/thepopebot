---
name: solution-offer-builder
description: Build offer angles and outreach copy from Reddit pain points. PROACTIVELY use when: pain points have been extracted from Reddit and need to be turned into offers, cold outreach copy needs to be grounded in specific audience language, Stage 3 of Reddit research pipeline runs, or competitor weaknesses need to be turned into positioning angles. Maps pain clusters to solution types, builds 3-tier offer matrix (entry/core/upsell), generates cold copy openers using verbatim Reddit language.
model: claude-opus-4-6
context: fork
allowed-tools: Read, Bash, WebSearch, Task
---

# solution-offer-builder
<!-- ultrathink -->

Stage 3 of the Reddit Research Pipeline. Takes pain points and competitor data from Stage 2 (reddit-pain-extractor) and produces offer angles, positioning statements, and cold outreach copy grounded in real Reddit language.

---

## Quick Start

**Minimal invocation:**
```
/solution-offer-builder
```
Paste the Stage 2 JSON contract when prompted.

**With file path:**
```
/solution-offer-builder path/to/stage2-output.json
```

**With niche context:**
```
/solution-offer-builder niche="bootstrapped SaaS founders"
```

**Example input trigger:**
- "I have my pain points from Reddit, now build the offers"
- "Turn these pain clusters into cold outreach"
- "What's the offer angle for this pain?"

---

## What This Skill Does

Accepts Stage 2 output → builds a full offer strategy:

| Step | Output |
|------|--------|
| 1. Parse pain clusters | Which clusters are offer-ready vs under-served |
| 2. Map solutions | 2+ solution types per pain point |
| 3. Build offer matrix | Entry / Core / Upsell per cluster |
| 4. Position vs competitors | Angle based on complaint themes |
| 5. Write cold copy | 4 opener formats using verbatim Reddit language |
| 6. Assemble contract | Stage 4-ready JSON output |

---

## 3-Tier Offer Matrix

Every pain cluster maps to three offer tiers:

| Tier | Description | Purpose |
|------|-------------|---------|
| **Entry offer** | Low friction, fast win, low price | Get them in the door — solve one specific, acute pain |
| **Core offer** | Main service or product | The full solution, primary revenue driver |
| **Upsell** | Premium / ongoing / expanded | Retention, expansion, higher LTV |

**Cluster-to-matrix rule:** If average_intensity ≥ 80, the cluster supports a paid core offer immediately. If 60-79, lead with entry offer first. If <60, content-led approach only.

Full workflow: See [OFFER-BUILDING-WORKFLOW.md](references/OFFER-BUILDING-WORKFLOW.md)

---

## Competitor Positioning

Turn competitor complaint themes from Stage 2 into positioning angles.

**Core principle:** Never attack the competitor. Position toward what they're missing.

| Complaint theme | Positioning direction |
|----------------|----------------------|
| too expensive | Accessible / right-sized / ROI-first |
| too complex | Simple / done-for-you / no learning curve |
| bad support | White-glove / hands-on / personal |
| no automation | Fully automated / zero manual work |
| doesn't integrate | Plays well with your stack |

Full templates and combinations: See [COMPETITOR-POSITIONING.md](references/COMPETITOR-POSITIONING.md)

---

## Cold Copy Generation

**Non-negotiable rule:** Every opener references specific Reddit-voiced language — the exact words the prospect used, not a paraphrase of the generic pain.

**4 opener formats:**

| Format | When to use |
|--------|-------------|
| Pain-aware | intent_level = seeking-solution |
| Competitor-aware | competitors_mentioned in pain point |
| Outcome-focused | intent_level = purchase-ready |
| Content-led | intent_level = exploring |

Full templates, rules, and worked examples: See [COLD-COPY-GENERATION.md](references/COLD-COPY-GENERATION.md)

---

## Quality Gate

Before finalising output:

- [ ] Every pain point has **minimum 2 solution options** — if not, broaden to adjacent technologies
- [ ] Every solution has at least 2 measurable outcomes (time saved, revenue gained, errors eliminated, etc.)
- [ ] Every cold opener contains a verbatim phrase or direct echo of evidence_quotes from Stage 2
- [ ] Every cluster with competitors_mentioned has a vs_competitor field populated
- [ ] Under-served pain points (fewer than 2 viable solutions found) are flagged explicitly in output

**If quality gate fails:** Do not abort — flag the gap and document what additional info or scope would resolve it.

---

## Output

Produces Stage 4-ready JSON matching the output contract.

Key fields:
- `solutions[]` — one entry per pain_id, with offer_angle, vs_competitor, and cold_offer_copy
- `offer_matrix[]` — one entry per pain_cluster, three tiers
- `positioning_angles[]` — top-level list derived from competitor_map
- `google_doc_url` — null unless google-workspace skill is invoked to create a report
- `timestamp` — ISO-8601

Full schema with worked example (bootstrapped SaaS founders niche): See [OUTPUT-CONTRACT.md](references/OUTPUT-CONTRACT.md)

---

## Execution Path

```
0. PROVEN OFFER CHECK (Track B-1): Before generating new offers, check for proven offers:
   Run: psql $NEON_DATABASE_URL -c "SELECT offer_angle, cold_subject_line, offer_validation_score FROM rr_offers WHERE niche = '{niche}' AND is_proven = true ORDER BY offer_validation_score DESC LIMIT 5;"
   If proven offers exist: use them as reference examples when constructing new offers. Replicate the patterns from high-scoring dimensions. Do not copy verbatim — use as structural inspiration.
   If no proven offers exist: proceed normally.
0. Read SMARTERFLO-CONTEXT.md — Smarterflo positioning, service categories, voice rules
1. Read Stage 2 JSON (file path or stdin)
2. Read OFFER-BUILDING-WORKFLOW.md → follow step-by-step (Step 0 loads Smarterflo context)
3. For each cluster with competitors: Read COMPETITOR-POSITIONING.md
4. For cold copy generation: Read COLD-COPY-GENERATION.md (includes Smarterflo voice rules)
5. Validate against quality gate
6. Assemble and emit Stage 4 contract JSON
```

---

## References

| File | Load when |
|------|-----------|
| [SMARTERFLO-CONTEXT.md](references/SMARTERFLO-CONTEXT.md) | Always — load before anything else |
| [OFFER-BUILDING-WORKFLOW.md](references/OFFER-BUILDING-WORKFLOW.md) | Processing starts |
| [COMPETITOR-POSITIONING.md](references/COMPETITOR-POSITIONING.md) | competitor_map is non-empty |
| [COLD-COPY-GENERATION.md](references/COLD-COPY-GENERATION.md) | Writing cold_offer_copy |
| [OUTPUT-CONTRACT.md](references/OUTPUT-CONTRACT.md) | Assembling final JSON / verifying schema |
| [OFFER-VALIDATION.md](references/OFFER-VALIDATION.md) | Run after Step 10 (cold copy) — validate all offers before output assembly |
