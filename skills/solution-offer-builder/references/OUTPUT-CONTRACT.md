# Output Contract

Full schema definition and worked example for the Stage 4-ready JSON output.

---

## Schema

```json
{
  "niche": "string — passed through from Stage 2 input",
  "solutions": [
    {
      "pain_id": "string — matches id from Stage 2 pain_points",
      "cluster_name": "string or null — cluster this pain belongs to, if any",
      "solution_type": "one of: automation | consulting | software | template | training | audit",
      "smarterflo_service_category": "one of: AI Research Systems | AI Workflow Automation | Client Delivery Systems | AI Content Systems | AI Reporting & Analytics | AI Client Communication | Custom AI Agents | AI Integration Projects",
      "tech_used": ["string — specific tools or methods"],
      "outcomes": ["string — measurable: time saved, revenue gained, errors eliminated"],
      "investment_range": "string — e.g. '$3,500–$7,500'",
      "offer_angle": "string — one sentence positioning",
      "vs_competitor": "string — how this beats the competitor they're using (null if no competitors_mentioned)",
      "cold_offer_copy": {
        "subject_line": "string — 4-8 words, specific",
        "opener": "string — references their specific Reddit-voiced pain",
        "offer_statement": "string — what it is, what it delivers, for whom",
        "cta": "string — low-friction, specific, time-bound"
      },
      "offer_validation_score": "integer 0-10 — score from OFFER-VALIDATION.md rubric",
      "validation_warning": "string or null — populated when score is 5-6 (borderline)",
      "failed_validation": "boolean — true if offer scored < 5 after regeneration attempt"
    }
  ],
  "offer_matrix": [
    {
      "pain_cluster": "string — cluster_name from Stage 2",
      "entry_offer": "string — low friction, fast win, low price",
      "core_offer": "string — main service, primary revenue driver",
      "upsell": "string — premium or ongoing expansion"
    }
  ],
  "positioning_angles": [
    "string — top-level angles derived from competitor complaint themes"
  ],
  "under_served_pain_ids": [
    "string — pain_ids where fewer than 2 viable solutions were found"
  ],
  "warnings": [
    "string — any quality gate failures, missing fields, or flags"
  ],
  "google_doc_url": "string or null — populated if google-workspace skill creates a report",
  "timestamp": "string — ISO-8601 format"
}
```

---

## Field Notes

**`solutions[]`** — one entry per pain_id from Stage 2. If a pain_id maps to multiple solution types, emit multiple solution objects all sharing the same pain_id.

**`solutions[].smarterflo_service_category`** — maps this solution to one of Smarterflo's 8 service categories from SMARTERFLO-CONTEXT.md. Required. Never null. Use the category that most accurately describes the deliverable (e.g., CRM automation → "AI Workflow Automation"; outbound system → "AI Research Systems").

**`under_served_pain_ids[]`** — populated when fewer than 2 solution types could be identified for a pain point after broadening scope. Empty array if quality gate is fully met.

**`solutions[].offer_validation_score`** — Required. Every offer must be validated via the 5-dimension rubric in OFFER-VALIDATION.md before finalizing output. Minimum score 7 to pass without warning. Scores below 5 trigger regeneration.

**`warnings[]`** — non-blocking flags. Examples:
- "pain_id pp-003 has only 1 viable solution type — broadened scope applied, still under quality gate minimum"
- "Stage 2 input missing evidence_quotes for pp-005 — cold copy opener uses pain summary language only"

---

## Worked Example — Niche: Bootstrapped SaaS Founders

**Stage 2 Input (abbreviated):**
```json
{
  "niche": "bootstrapped SaaS founders",
  "pain_points": [
    {
      "id": "pp-001",
      "summary": "Manual CRM updates consuming 2-3 hours every day",
      "intensity_score": 88,
      "intent_level": "purchase-ready",
      "competitors_mentioned": ["HubSpot"],
      "evidence_quotes": [
        "I spend 2 hours a day just updating HubSpot. It's embarrassing.",
        "Our CRM is perfect for enterprise teams. We're 4 people."
      ]
    },
    {
      "id": "pp-002",
      "summary": "No consistent outbound — relies entirely on inbound and referrals",
      "intensity_score": 79,
      "intent_level": "seeking-solution",
      "competitors_mentioned": [],
      "evidence_quotes": [
        "We haven't figured out outbound. Every month I say I will and don't."
      ]
    }
  ],
  "pain_clusters": [
    {
      "cluster_name": "Manual workflow overhead",
      "pain_ids": ["pp-001"],
      "average_intensity": 88,
      "offer_hook": "Automate the ops that are eating your building time"
    },
    {
      "cluster_name": "Growth engine missing",
      "pain_ids": ["pp-002"],
      "average_intensity": 79,
      "offer_hook": "Build a repeatable outbound system that runs without you"
    }
  ],
  "competitor_map": [
    {
      "name": "HubSpot",
      "complaint_themes": ["too expensive", "built for enterprise not startups"],
      "mentions": 22
    }
  ]
}
```

**Stage 3 Output:**

```json
{
  "niche": "bootstrapped SaaS founders",
  "solutions": [
    {
      "pain_id": "pp-001",
      "cluster_name": "Manual workflow overhead",
      "solution_type": "automation",
      "smarterflo_service_category": "AI Workflow Automation",
      "tech_used": ["Make (Integromat)", "HubSpot API", "Zapier", "Notion"],
      "outcomes": [
        "Eliminate 10-15 hours/week of manual CRM data entry",
        "Zero deal updates missed — every call, email, and action logged automatically",
        "CRM adoption goes from 40% to 95% because the friction is gone"
      ],
      "investment_range": "$5,000–$12,000",
      "offer_angle": "Bootstrapped SaaS founders who are spending hours on CRM updates get a fully automated pipeline that logs itself — without replacing HubSpot or hiring an ops person.",
      "vs_competitor": "Unlike HubSpot's native automation which still requires manual triggers and $800+/month to unlock, this runs entirely on your existing HubSpot instance with zero ongoing cost — and zero manual work from your side.",
      "cold_offer_copy": {
        "subject_line": "CRM that updates itself while you work",
        "opener": "Spending 2 hours a day just updating HubSpot is the kind of thing that feels productive but isn't — you're doing data entry, not building.",
        "offer_statement": "I build CRM automation layers for bootstrapped SaaS founders that pull every call note, email, and deal update into HubSpot in real time — no manual input, ever.",
        "cta": "10-minute walkthrough this week — I'll show you the exact setup in your stack before you commit."
      },
      "offer_validation_score": 9,
      "validation_warning": null,
      "failed_validation": false
    },
    {
      "pain_id": "pp-001",
      "cluster_name": "Manual workflow overhead",
      "solution_type": "consulting",
      "smarterflo_service_category": "AI Workflow Automation",
      "tech_used": ["HubSpot", "Notion", "process mapping"],
      "outcomes": [
        "Identify which CRM workflows to eliminate vs automate vs keep manual",
        "Cut total CRM maintenance time by 60-80% within 30 days",
        "Team actually uses the CRM because the process makes sense"
      ],
      "investment_range": "$2,500–$5,000",
      "offer_angle": "A one-week ops audit that tells you exactly where your team's time is going and what to automate first.",
      "vs_competitor": "Where HubSpot's implementation partners charge $10,000+ for full setups, this is a focused audit that gets you to the same decision in one week for a fraction of the cost.",
      "cold_offer_copy": {
        "subject_line": "Where your team time actually goes",
        "opener": "\"Our CRM is perfect for enterprise teams. We're 4 people.\" — that framing nails why so many bootstrapped founders feel like their tools are working against them.",
        "offer_statement": "I run ops audits for early-stage SaaS founders that surface exactly which workflows are costing the most time and give you a clear automation priority order.",
        "cta": "Free 30-minute diagnostic call — I'll tell you where your biggest time leaks are before we discuss anything paid."
      },
      "offer_validation_score": 9,
      "validation_warning": null,
      "failed_validation": false
    },
    {
      "pain_id": "pp-002",
      "cluster_name": "Growth engine missing",
      "solution_type": "automation",
      "smarterflo_service_category": "AI Research Systems",
      "tech_used": ["Clay", "Instantly", "Apollo", "OpenAI API"],
      "outcomes": [
        "20-50 qualified outbound replies per week without any manual prospecting",
        "Consistent pipeline that doesn't depend on referrals or inbound luck",
        "Personalised sequences at scale — 500 contacts/week treated like 1-to-1 outreach"
      ],
      "investment_range": "$3,500–$7,500",
      "offer_angle": "Bootstrapped SaaS founders who've avoided outbound because it felt too manual get a fully automated prospecting system that runs in the background.",
      "vs_competitor": null,
      "cold_offer_copy": {
        "subject_line": "Outbound that runs without you thinking about it",
        "opener": "\"We haven't figured out outbound. Every month I say I will and don't.\" That's not a motivation problem — it's a system problem. Outbound without automation is a full-time job.",
        "offer_statement": "I build Clay + Instantly outbound systems for SaaS founders that prospect, personalise, and follow up automatically — founders I've set this up for see 20-50 qualified replies in the first month.",
        "cta": "30-minute call this week — I'll map out what your outbound system would look like before you commit to anything."
      },
      "offer_validation_score": 9,
      "validation_warning": null,
      "failed_validation": false
    },
    {
      "pain_id": "pp-002",
      "cluster_name": "Growth engine missing",
      "solution_type": "template",
      "smarterflo_service_category": "AI Research Systems",
      "tech_used": ["Clay", "Instantly", "Google Sheets", "Apollo"],
      "outcomes": [
        "Launch first outbound sequence in 48 hours instead of building from scratch",
        "Proven message templates that convert in the SaaS founder segment",
        "Reusable system you own — not a dependency on an agency"
      ],
      "investment_range": "$497–$997",
      "offer_angle": "A done-for-you outbound starter kit — sequences, templates, and the Clay workflow — so you can run your first campaign this week.",
      "vs_competitor": null,
      "cold_offer_copy": {
        "subject_line": "First outbound campaign running this week",
        "opener": "If outbound keeps getting pushed to next month, the issue is usually the blank page — not the intent. Starting from scratch every time is what kills the habit.",
        "offer_statement": "I sell a complete outbound starter kit for SaaS founders: proven message sequences, Clay workflow, and setup guide — everything you need to launch your first campaign in 48 hours.",
        "cta": "Kit is $597. Reply if you want to see what's included."
      },
      "offer_validation_score": 9,
      "validation_warning": null,
      "failed_validation": false
    }
  ],
  "offer_matrix": [
    {
      "pain_cluster": "Manual workflow overhead",
      "entry_offer": "Ops audit — 1-week diagnostic, identify top 3 automation wins, $2,500",
      "core_offer": "Full CRM automation build — end-to-end automated pipeline, no manual entry, $5,000–$12,000",
      "upsell": "Monthly ops retainer — ongoing automation expansion + maintenance, $1,500/month"
    },
    {
      "pain_cluster": "Growth engine missing",
      "entry_offer": "Outbound starter kit — templates, Clay workflow, setup guide, $597",
      "core_offer": "Outbound system build — Clay + Instantly setup, custom sequences, 30-day launch support, $3,500–$7,500",
      "upsell": "Outbound management — monthly prospecting, sequence refresh, performance reporting, $2,000/month"
    }
  ],
  "positioning_angles": [
    "Built for 4-person teams, not enterprise — right-sized pricing and scope",
    "Running in one week, not one quarter — no long implementations",
    "Works inside your existing HubSpot — no rip-and-replace"
  ],
  "under_served_pain_ids": [],
  "warnings": [],
  "google_doc_url": null,
  "timestamp": "2026-03-09T14:23:00Z"
}
```
