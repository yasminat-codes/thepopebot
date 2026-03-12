# Offer Building Workflow

Step-by-step execution guide for solution-offer-builder.

---

## Step 0 — Load Smarterflo Context

Read [SMARTERFLO-CONTEXT.md](SMARTERFLO-CONTEXT.md) before doing anything else.

```
0.1 Read references/SMARTERFLO-CONTEXT.md
0.2 For each pain cluster in the incoming data: identify the matching Smarterflo service category
    using the Pain → Smarterflo Service Mapping table
0.3 Apply the offer construction formula:
    "We build [system] that [outcome] for [niche] — so you can [freedom/growth statement]."
0.4 Apply anti-positioning rules — no banned phrases in any output
0.5 Anchor outcomes to measurable results: time saved, clients handled, hours eliminated, revenue gained
```

This step is not optional. Smarterflo-aware positioning must be loaded before any offer is constructed.

---

## Step 1 — Receive Stage 2 Contract

Parse the incoming JSON. Validate required fields:

```
Required top-level keys: niche, pain_points, pain_clusters, competitor_map
Required per pain_point: id, summary, intensity_score, intent_level, evidence_quotes
Required per pain_cluster: cluster_name, pain_ids, average_intensity, offer_hook
```

If any required field is missing:
- Log what is missing
- Continue with available data
- Flag the gap in output under a `"warnings"` key

---

## Step 2 — Classify Pain Points by Offer Readiness

Before building solutions, score each pain point for offer readiness:

| Signal | Score boost |
|--------|------------|
| intensity_score ≥ 85 | +2 |
| intent_level = purchase-ready | +3 |
| intent_level = seeking-solution | +2 |
| intent_level = venting | 0 |
| intent_level = exploring | +1 |
| competitors_mentioned is non-empty | +1 |
| evidence_quotes has 2+ quotes | +1 |

**Offer readiness threshold:**
- Score 5+: Direct offer — lead with core offer
- Score 3-4: Warm — lead with entry offer
- Score 1-2: Cold — content-led approach only, flag in output

---

## Step 3 — Map Solutions Per Pain Point

For each pain_point, identify 2-3 solution types. The quality gate requires minimum 2.

**Step 3.0 — Map to Smarterflo service category first.**
Before identifying generic solution types, use the Pain → Smarterflo Service Mapping table in [SMARTERFLO-CONTEXT.md](SMARTERFLO-CONTEXT.md) to identify the primary service category for this pain. The service category determines which solution types are most likely to apply and shapes the offer angle language.

| Smarterflo Service Category | Typical solution types |
|-----------------------------|----------------------|
| AI Research Systems | automation, software |
| AI Workflow Automation | automation, consulting |
| Client Delivery Systems | automation, template, consulting |
| AI Content Systems | automation, template |
| AI Reporting and Analytics | automation, software |
| AI Client Communication | automation, template |
| Custom AI Agents | software, consulting |
| AI Integration Projects | automation, software |

**Solution type definitions:**

| Type | When to use |
|------|-------------|
| `automation` | Pain is a repetitive manual task (data entry, reporting, scheduling, syncing) |
| `consulting` | Pain is strategic confusion, wrong tool choice, or process design |
| `software` | Pain is a missing capability — something the prospect wishes existed |
| `template` | Pain is reinventing the wheel — they lack a starting point or framework |
| `training` | Pain is skill gap — they have the tools but don't know how to use them |
| `audit` | Pain is unknown problem — they know something is wrong but can't diagnose it |

Add a `smarterflo_service_category` field alongside `solution_type` in each solution object in the output. This field should match one of the eight categories from SMARTERFLO-CONTEXT.md.

**If fewer than 2 solution types fit the pain natively:**
Broaden scope:
1. Look at the pain cluster — does the cluster suggest adjacent solution types?
2. Consider adjacent technologies (e.g. pain is "manual Salesforce data entry" → solutions: automation + template + consulting)
3. Check if a lighter version of a solution type applies (e.g. a "mini-audit" if full audit doesn't fit)
4. If still under 2: flag as under-served, note what additional info would unlock more solutions

---

## Step 4 — Define Tech Stack Per Solution

For each solution, list the specific tools or methods that would solve the pain.

**Tech stack selection heuristics:**

| Pain pattern | Likely tech |
|--------------|-------------|
| "data lives in multiple places" | Zapier, Make, n8n, Airtable, Notion |
| "takes hours every week manually" | RPA (UIPath, Playwright), Python scripts, Zapier |
| "CRM is a mess" | HubSpot, Close, Pipedrive, Clay |
| "can't track / no visibility" | Notion, Airtable, Google Sheets + Looker Studio |
| "emails taking too long" | Clay + Instantly, Apollo, Lemlist |
| "AI content feels generic" | Custom Claude workflows, fine-tuned prompts, brand voice docs |
| "onboarding is chaos" | Notion SOPs, Loom, Trainual, ChurnZero |
| "reporting takes forever" | Looker Studio, Metabase, custom dashboards |
| "our stack doesn't talk to each other" | Make/Zapier middleware, custom API integrations |

If the pain is niche and no tech maps clearly: use WebSearch to research what solutions exist in market.

---

## Step 5 — Define Outcomes

For each solution, list 2+ measurable outcomes. Generic outcomes are disqualified.

**Good outcomes:**
- "Save 6-8 hours/week on manual reporting"
- "Reduce lead response time from 2 days to 15 minutes"
- "Eliminate 100% of manual data entry between CRM and billing"
- "Cut onboarding time from 3 weeks to 5 days"
- "Generate 3x more qualified replies from cold outreach"

**Bad outcomes (too vague — do not use):**
- "Improve efficiency"
- "Save time"
- "Grow revenue"

Derive outcomes from the evidence_quotes in the pain point — the prospect described the pain in measurable terms. Mirror that language.

---

## Step 6 — Estimate Investment Range

Base investment range on two factors: intensity_score and solution type.

| Solution type | Low intensity (<70) | Medium (70-84) | High (≥85) |
|--------------|--------------------|--------------------|-----------|
| template | $47-$197 | $197-$497 | $497-$997 |
| training | $297-$997 | $997-$2,500 | $2,500-$5,000 |
| audit | $500-$1,500 | $1,500-$3,500 | $3,500-$7,500 |
| automation | $1,500-$5,000 | $5,000-$15,000 | $15,000-$40,000 |
| consulting | $2,000-$7,500 | $7,500-$20,000 | $20,000-$60,000 |
| software | $3,000-$15,000 | $15,000-$50,000 | $50,000-$150,000+ |

These are ballpark guides — adjust based on:
- Market segment (SMB vs enterprise)
- Evidence quotes suggesting budget awareness ("can't afford" vs "have budget approved")
- Competitor pricing from competitor_map

---

## Step 7 — Build 3-Tier Offer Matrix Per Cluster

For each pain_cluster, build an entry / core / upsell stack:

**Entry offer criteria:**
- Solves ONE specific acute pain from the cluster
- Delivers a result in ≤2 weeks
- Low price, low commitment
- Examples: 1-day audit, template kit, mini-automation, 1-hour strategy call

**Core offer criteria:**
- Solves the cluster comprehensively
- Delivers the outcome the prospect is actually buying
- This is the revenue driver

**Upsell criteria:**
- Extends or maintains the core offer result
- Higher price, longer engagement
- Examples: monthly retainer, ongoing optimisation, expanded scope, team training

---

## Step 8 — Generate Offer Angle

Offer angle = one-sentence positioning statement.

Formula: `[Who] who [situation] get [outcome] without [obstacle]`

Example:
- "Bootstrapped SaaS founders who are drowning in manual CRM updates get a fully automated pipeline without hiring an ops person or learning new software."

Derive the "obstacle" from the competitor weaknesses or the specific friction named in evidence_quotes.

---

## Step 9 — Build Competitor Positioning

Load [COMPETITOR-POSITIONING.md](COMPETITOR-POSITIONING.md) and apply the template for each competitor in competitors_mentioned.

---

## Step 10 — Write Cold Copy

Load [COLD-COPY-GENERATION.md](COLD-COPY-GENERATION.md) and generate one opener per pain point, matched to the appropriate format based on intent_level.

---

## Step 10.5 — Validate Each Offer (REQUIRED)

Before assembling the output contract, score every offer against the 5-dimension rubric.

1. Read [OFFER-VALIDATION.md](OFFER-VALIDATION.md)
2. For each solution object constructed so far: score all 5 dimensions (0-2 each)
3. Apply the gate:
   - Score ≥ 7: Include in output, set offer_validation_score = total score
   - Score 5-6: Include with validation_warning flag
   - Score < 5: Attempt regeneration. If still < 5 after one attempt: set failed_validation = true, include reasoning
4. Before v5.0: check rr_offers WHERE niche = current_niche AND is_proven = true
   - If proven offers exist for this niche, reference them as examples for the regeneration
   - Proven offer patterns: which dimensions scored highest → replicate those patterns

Full rubric and worked example: [OFFER-VALIDATION.md](OFFER-VALIDATION.md)

---

## Step 11 — Assemble Output Contract

Load [OUTPUT-CONTRACT.md](OUTPUT-CONTRACT.md) for the full schema.

Final checks before emitting:
1. Every pain_id in input has a corresponding solution entry in output
2. Every cluster has an offer_matrix entry
3. positioning_angles list is populated (at least one angle per competitor)
4. Timestamp added in ISO-8601
5. Quality gate checklist passed (or failures documented)
