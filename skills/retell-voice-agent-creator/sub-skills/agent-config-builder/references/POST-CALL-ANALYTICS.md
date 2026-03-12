# Post-Call Analytics Reference

Auto-configuration of `post_call_analysis_data` by agent template. This reference
defines which analytics variables to add for each template type.

---

## Overview

Every agent gets post-call analysis through the `post_call_analysis_data` array
on the agent config. Each entry defines a variable that Retell extracts from the
call transcript after the call ends.

The analysis model (set via `post_call_analysis_model`) processes the transcript
and populates these variables. Recommended model: `gpt-4.1-mini` for cost
efficiency with good accuracy.

## Variable Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Free-text response | "Summarize the call in 2-3 sentences" |
| `boolean` | True/false answer | "Was an appointment booked?" |
| `number` | Numeric value | "Rate lead quality 1-10" |
| `enum` | One of specified options | "Sentiment: positive, neutral, negative" |

## Universal Variables (All Templates)

These are added to every agent regardless of template:

```json
[
  {
    "name": "call_summary",
    "type": "string",
    "description": "Summarize the call in 2-3 sentences. Include the caller's main request, the outcome, and any follow-up needed."
  },
  {
    "name": "user_sentiment",
    "type": "enum",
    "description": "Overall caller sentiment. Options: positive, neutral, negative. Base this on tone, word choice, and call outcome."
  }
]
```

## Template-Specific Variables

### appointment-setter

```json
[
  {
    "name": "appointment_booked",
    "type": "boolean",
    "description": "Was an appointment successfully booked during this call?"
  },
  {
    "name": "appointment_date",
    "type": "string",
    "description": "The date and time of the booked appointment. Return 'none' if no appointment was booked."
  },
  {
    "name": "appointment_type",
    "type": "string",
    "description": "The type of service or appointment requested (e.g., cleaning, consultation, follow-up)."
  }
]
```

### sales-outbound / sales-inbound

```json
[
  {
    "name": "did_express_interest",
    "type": "boolean",
    "description": "Did the prospect express interest in the product or service?"
  },
  {
    "name": "lead_score",
    "type": "number",
    "description": "Rate the lead quality from 1-10. 1 = not interested at all, 10 = ready to buy immediately."
  },
  {
    "name": "objections_raised",
    "type": "string",
    "description": "List any objections the prospect raised (price, timing, competitor, etc.). Return 'none' if no objections."
  },
  {
    "name": "next_steps",
    "type": "string",
    "description": "What follow-up actions are needed? (e.g., send proposal, schedule demo, call back on date)"
  }
]
```

### customer-support

```json
[
  {
    "name": "issue_resolved",
    "type": "boolean",
    "description": "Was the caller's issue fully resolved during this call?"
  },
  {
    "name": "issue_category",
    "type": "enum",
    "description": "Categorize the issue. Options: billing, technical, account, general, other."
  },
  {
    "name": "escalation_needed",
    "type": "boolean",
    "description": "Does this issue need escalation to a human agent or supervisor?"
  }
]
```

### lead-qualifier

```json
[
  {
    "name": "is_qualified",
    "type": "boolean",
    "description": "Does the lead meet the qualification criteria (budget, authority, need, timeline)?"
  },
  {
    "name": "budget_range",
    "type": "string",
    "description": "The stated or implied budget. Return 'not disclosed' if unknown."
  },
  {
    "name": "timeline",
    "type": "string",
    "description": "When does the prospect want to proceed? (e.g., immediately, this quarter, next year)"
  },
  {
    "name": "decision_maker",
    "type": "boolean",
    "description": "Is the caller the decision maker for this purchase?"
  }
]
```

### survey

```json
[
  {
    "name": "survey_completed",
    "type": "boolean",
    "description": "Did the caller complete all survey questions?"
  },
  {
    "name": "responses",
    "type": "string",
    "description": "Summarize all survey responses in a structured format."
  }
]
```

### reminder

```json
[
  {
    "name": "reminder_acknowledged",
    "type": "boolean",
    "description": "Did the caller confirm they received and acknowledged the reminder?"
  },
  {
    "name": "reschedule_requested",
    "type": "boolean",
    "description": "Did the caller request to reschedule the event being reminded about?"
  }
]
```

### receptionist

```json
[
  {
    "name": "call_purpose",
    "type": "string",
    "description": "Why did the caller call? Summarize in one sentence."
  },
  {
    "name": "transferred",
    "type": "boolean",
    "description": "Was the call transferred to another person or department?"
  },
  {
    "name": "message_taken",
    "type": "string",
    "description": "Any message the caller left for staff. Return 'none' if no message."
  }
]
```

### custom

For custom templates, only universal variables (call_summary, user_sentiment) are
added automatically. The user should define additional variables manually.

## Retell Assure (AI QA) — Launched Jan 2026

Automated call review with hallucination detection. Configure in dashboard under Analytics -> Assure.

**What It Detects:**
- Hallucinations (agent claims something not in knowledge base)
- Topic adherence violations (agent went off-script)
- Escalation accuracy (did agent escalate when it should have?)
- FDCPA/compliance violations (for debt collection agents)
- Resolution rate (did caller's issue get resolved?)

**Configuration:**
- Set hallucination sensitivity threshold (0-1)
- Define "on-topic" topics for your agent
- Configure escalation trigger phrases
- Set sampling rate (100% for new agents, 20% for stable agents)

**Integration with Post-Call Analysis:**
Retell Assure runs AFTER post_call_analysis_data extraction. Results appear in the call record under `assure_results`. Use alongside custom post-call analysis fields for full quality picture.
