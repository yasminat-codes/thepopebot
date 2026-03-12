# Interview Engine — Expert Question Bank & Probing Strategies

This file governs how plan-architect conducts multi-round expert interviews with users.
The goal is not to collect answers — it is to surface requirements the user hasn't
articulated, detect unstated constraints, and fill gaps with expert-level recommendations.

---

## ⛔ IRON RULE: Every Question Goes Through AskUserQuestion

**This rule overrides everything else in this file.**

Every question, probe, synthesis check, expert fill, and gap inquiry MUST be delivered
via the `AskUserQuestion` tool. No exceptions. No text questions. No "Does that work?"
typed in chat output. No "Let me make sure I have this right: ... Is that correct?" in text.

If a section below shows a question in quotes, that is the *content* to put inside an
AskUserQuestion option's `description` field — NOT text to type in chat.

| If you want to... | Do this | NOT this |
|---|---|---|
| Ask about architecture | `AskUserQuestion({ questions: [...] })` | Type "What triggers this?" in chat |
| Synthesize understanding | AskUserQuestion with summary in description + "Is this correct?" option | Type summary + "Sound right?" in chat |
| Fill a gap with expert opinion | AskUserQuestion with recommendation in description + confirm/reject options | Type recommendation + "Does that work?" in chat |
| Probe an edge case | AskUserQuestion with failure scenario in description + handling options | Type "What happens if X fails?" in chat |

**Self-check:** If your output contains a `?` anywhere in plain text, you are violating this rule.

---

## Core Principle: Interview Like a Senior Engineer

A junior engineer asks what the user requested.
A senior engineer asks what the user actually needs, then spots the gaps.

Three-layer interview model:
1. **Surface layer** — what the user explicitly said (what, why, who)
2. **Architecture layer** — constraints, integrations, volume, latency
3. **Risk layer** — failure modes, edge cases, things the user hasn't considered

Never skip to layer 3 without completing layers 1 and 2. Never complete all 3 layers
in one round. Pace matters — the user should feel understood, not interrogated.

---

## Interview Structure

### Round 1: The Setup (2-3 questions max)
Goal: Establish scope and motivation.

- "What does this do, and why does it need to exist?"
- "Who triggers it — a person, a schedule, or another system?"
- "What does success look like? If I build this and it works perfectly, what changes?"

### Round 2: The Architecture Deep-Dive (2-3 questions max)
Goal: Surface constraints and integrations.

Select questions from the domain-specific banks below based on Round 1 answers.
Never ask questions from a domain the user didn't mention.

### Round 3: The Synthesis Check (1-2 questions max)
Goal: Validate understanding and catch missed cases.

- "Let me make sure I have this right: [restate the problem in your own words]. Is that correct?"
- "You've described the happy path. What happens when [most likely failure scenario]?"

### Round 4: The Expert Fill (via AskUserQuestion with recommendations in descriptions)
Goal: Fill remaining gaps using expert judgment. Still uses AskUserQuestion — NEVER text.

Format: Present your expert recommendation inside the option `description`, then let the user confirm or reject.

```
AskUserQuestion([{
  question: "I have an expert recommendation for [gap area]. How should we handle it?",
  header: "Expert fill",
  options: [
    { label: "Use recommended approach", description: "Based on your codebase's [pattern], I'd handle [gap] with [specific approach]. Reason: [one sentence]." },
    { label: "Different approach", description: "If you have a preference that differs from the codebase pattern, select this to specify." }
  ]
}])
```

Example — reusing existing pattern:
```
AskUserQuestion([{
  question: "Your codebase already has a retry pattern. Should we reuse it here?",
  header: "Retry strategy",
  options: [
    { label: "Reuse existing pattern", description: "Your openrouter.py uses exponential backoff starting at 2s with max 3 attempts. I'd match that for consistency." },
    { label: "Custom retry logic", description: "Build a different retry strategy specific to this integration's needs." }
  ]
}])
```

**NEVER type "Does that work?" or "Any reason not to?" in chat text. Always through the tool.**

---

## Domain Question Banks

### Automation Domain

Use when: user describes something that runs on a schedule, processes data, or
orchestrates steps without real-time user interaction.

**Trigger & Scheduling:**
- What triggers this automation? Time-based (cron), event-based (webhook/queue message), or user-triggered (manual API call)?
- If time-based: what's the schedule? Twice daily, hourly, weekly? Timezone matters.
- If event-based: what generates the event? An external service, another part of your codebase, or a user action?
- What happens if two instances run simultaneously — is that safe, or do you need a distributed lock?
- What happens if the trigger fires but the previous run hasn't finished?

**Input:**
- What is the input? Raw data (files, API responses, DB rows) or a command (job parameters, config)?
- Where does the input come from? External API, database query, file system, message queue?
- What format? JSON, CSV, XML, binary, structured DB records?
- How large is the input? 10 records per run or 10,000? This determines batching strategy.
- Is the input guaranteed to be present? What happens if the source is empty or unavailable?

**Processing Logic:**
- What transformations happen? Filtering, enrichment, aggregation, classification, generation?
- Is there business logic that determines which records to process?
- Are there operations that must happen in sequence vs. operations that can be parallelized?
- Does the processing call external APIs or LLMs? How many calls per run, approximately?
- What's the expected runtime? Under 1 minute, under 10 minutes, or potentially hours?

**Output & Storage:**
- What's the output? Database rows, files, API calls, notifications?
- Where does it go? Same database, external service, S3, Slack, email?
- What's the data retention policy? Keep forever, 90 days, overwrite each run?
- Do downstream systems depend on the output being fresh by a certain time?

**Volume & Frequency:**
- How often does this run? Per-hour vs per-week determines whether you need a queue, a cron, or both.
- What's the data volume? 10 records/day vs 10,000/hour changes the architecture entirely.
- Is volume predictable or does it spike? (Black Friday, end-of-month, viral events)
- What's the growth trajectory? Will 10x volume in 6 months break this design?

**Latency Requirements:**
- Real-time (under 1 second), near-real-time (under 30 seconds), or batch (minutes to hours)?
- If someone triggers this manually, how long are they willing to wait before they assume it's broken?
- Do downstream systems have SLA requirements that this automation must meet?

---

### Integration Domain

Use when: user describes connecting to an external API, webhook, or third-party service.

**Service Identification:**
- Which specific API/service is this? (Be precise — Stripe vs PayPal vs Braintree have different patterns.)
- Are you using their official SDK or calling the REST API directly?
- Is this a well-documented API or a scrape/reverse-engineered endpoint? (Latter needs fallback plan.)
- Do you already have API credentials, or is obtaining them part of the scope?

**Authentication:**
- What auth method? API key in header, OAuth 2.0 (which flow?), webhook signature verification, mTLS?
- How are credentials managed? Environment variables, secrets manager, database?
- Do tokens expire? What's the rotation strategy?
- If OAuth: who is the resource owner — your app or individual users?

**Rate Limits:**
- What are the documented rate limits for this API? (Requests per second, per minute, per day)
- Are rate limits per-endpoint or global across all endpoints?
- Does the API return Retry-After headers when rate-limited?
- Is there a burst limit separate from the sustained rate limit?

**Data Contract:**
- What format does the API return? JSON, XML, CSV, binary?
- Is the response schema versioned? Will it change without notice?
- What's the maximum payload size you'd receive in a single response?
- Does the API use pagination? Cursor-based, offset-based, or link-header-based?

**Error Contract:**
- What HTTP status codes does this API use for errors? (Not all APIs follow REST conventions.)
- Does the API have a standard error response format or does it vary by endpoint?
- Which errors are transient (retry-able) vs. permanent (don't retry, alert)?
- Does the API distinguish between "your request was bad" and "our server is having trouble"?

**Webhooks (if applicable):**
- What events does the webhook deliver?
- How does the API sign webhook payloads? (HMAC-SHA256 is common, but implementation varies.)
- Are webhooks guaranteed-once or at-least-once delivery?
- What's the timeout window for your endpoint to respond before the webhook is retried?
- Is there a webhook event log or replay capability?

---

### Data Pipeline Domain

Use when: user describes moving, transforming, or storing data at scale.

**Data Model:**
- What are the core entities? What are their relationships (one-to-many, many-to-many)?
- Is there a concept of "ownership" — does each record belong to a user, org, or tenant?
- Are there soft deletes, or do records get hard-deleted?
- Is this append-only (event log) or mutable (update records in place)?

**Storage Strategy:**
- What's the primary storage? PostgreSQL, MySQL, MongoDB, DynamoDB?
- Is there a caching layer? Redis, Memcached, in-memory?
- Are there files or blobs? S3, GCS, local disk?
- Should data be replicated anywhere? Read replicas, cross-region backups?

**Query Patterns:**
- What are the 3 most common read queries this data will serve?
- Is this read-heavy (10:1 read/write ratio) or write-heavy?
- Are there time-range queries? (Date filtering heavily influences index strategy.)
- Are there full-text searches, or just exact-match lookups?
- What joins are required? (Deeply nested joins at scale = pain.)

**Retention & Archival:**
- How long should data be kept in the hot (queryable) store?
- Is there a cold storage / archival strategy after the retention window?
- Are there legal compliance requirements (GDPR, HIPAA) that govern deletion?
- Is there an audit log requirement — track who changed what and when?

**Validation:**
- What makes a record valid? (Required fields, format constraints, business rules)
- Should validation happen at the API layer, the service layer, or the DB layer (constraints)?
- What happens to invalid records — reject, quarantine, or store with a flag?

---

### Feature Domain

Use when: user describes a product feature that end users will interact with.

**User & Workflow:**
- Who is the primary user? Internal team, external customers, or both?
- Walk me through the workflow: what does the user do step by step?
- What problem are they solving? What are they doing today without this feature?
- What's the emotional outcome — what does it feel like when this works vs. when it doesn't?

**Acceptance Criteria:**
- How will you know this feature is done? What does a passing demo look like?
- Are there explicit acceptance tests / user stories already written?
- Who has sign-off authority on this feature?

**Scope:**
- What's the MVP? If we ship in 2 weeks, what gets cut?
- What's explicitly out of scope for this phase?
- Is there a Phase 2 already planned? (Knowing this prevents over-engineering or under-engineering.)

**Integration with Existing System:**
- What existing features does this touch or depend on?
- Is there existing UI this extends, or is it greenfield?
- Are there existing API contracts this must be compatible with?
- Does this affect any existing permissions or authorization rules?

**Rollout:**
- Is this behind a feature flag, or does it go live for everyone at launch?
- Is there a rollback plan if something goes wrong after launch?
- Are there A/B tests or gradual rollouts planned?

---

## Probing Strategies

These are applied at the end of each round — they are follow-up probes, not standalone
questions. Pick 1-2 maximum per round. **ALL probes use AskUserQuestion.**

### The "What If" Probe
After every substantive answer, surface the failure mode via AskUserQuestion:

```
AskUserQuestion([{
  question: "How should the system handle [failure scenario]?",
  header: "Failure mode",
  options: [
    { label: "Retry with backoff", description: "If Reddit is down or rate-limiting, retry 3 times with exponential backoff before marking the run as failed." },
    { label: "Skip and continue", description: "Log the failure and continue processing remaining items. Report partial results." },
    { label: "Halt and alert", description: "Stop the entire run and send a Slack alert. Manual intervention required." }
  ]
}])
```

The "What If" probe surfaces the error handling requirements the user forgot to mention.

### The "Already Have" Probe
Scan the codebase and reference what already exists via AskUserQuestion:

```
AskUserQuestion([{
  question: "Your codebase already has a relevant pattern. Should we reuse it?",
  header: "Reuse pattern",
  options: [
    { label: "Reuse existing", description: "Your app/services/openrouter.py already has retry logic with exponential backoff. Reusing it keeps the codebase consistent." },
    { label: "Extend existing", description: "Use the existing module as a base but add features specific to this integration." },
    { label: "Build new", description: "Create a separate implementation. Useful if the requirements diverge significantly from the existing pattern." }
  ]
}])
```

This probe prevents duplicate implementations and encourages reuse of battle-tested patterns.

### The "Missing Piece" Probe
Identify what the user described vs. what a complete implementation requires.
Focus on: error handling, monitoring, testing, security, documentation.

```
AskUserQuestion([{
  question: "You haven't mentioned [missing area]. How should we handle it?",
  header: "Gap found",
  options: [
    { label: "I have a preference", description: "Select this to specify how you want [missing area] handled." },
    { label: "Use your recommendation", description: "Based on the codebase pattern in [file], I'd suggest [approach]. Reason: [one sentence]." }
  ]
}])
```

### The "Expert Fill" Probe
When the user says "I don't know" or "whatever you think is best," present your
expert recommendation via AskUserQuestion with the recommendation in the description:

```
AskUserQuestion([{
  question: "I have a recommendation based on your codebase. Does this work?",
  header: "Expert rec",
  options: [
    { label: "Use recommendation", description: "Based on your existing rate_limiter.py, I'd use a sliding-window Redis key with a 60-second window. Consistent with what you have." },
    { label: "Different approach", description: "If you want something different from the codebase pattern, select this to specify." }
  ]
}])
```

**NEVER type recommendations as text followed by "Does that work?" — always through AskUserQuestion.**

---

## Gap-Filling Intelligence

When the user describes a feature, check for these gaps before writing the plan.
If any are missing, address them either via a probing question or an expert fill.

| User describes... | Check for... |
|-------------------|-------------|
| Input source | Error handling when source is unavailable |
| External API call | Rate limit handling, retry strategy |
| Webhook receiver | Signature verification, idempotency |
| LLM call | JSON parsing failures, token budget management |
| Database write | Transaction handling, rollback on failure |
| Data flow | What gets persisted at each step |
| Automation run | Duplicate run prevention (distributed lock) |
| Scheduling (cron) | What happens if a run is missed |
| Slack/email delivery | What happens if delivery fails |
| File output | Cleanup of temp files on failure |
| User-triggered action | Authorization / permissions check |
| Feature with multiple users | Multi-tenancy / data isolation |

**NEVER fill gaps silently.** Even if the solution seems obvious from the codebase,
ASK the user via AskUserQuestion. Put your expert recommendation in the option description
so the user can confirm or override. Silent assumptions are how plans diverge from user intent.

For small gaps: use a single AskUserQuestion with your recommendation as the default option.
For large gaps: dedicate a full round to exploring them.

---

## Question Selection Logic

### Step 1: Classify the request
After Round 1, classify the request into 1-3 domains:
- Automation (runs on its own, processes data)
- Integration (calls external APIs or receives webhooks)
- Data Pipeline (stores, queries, transforms data at scale)
- Feature (user-facing product capability)

Most requests span 2 domains. Classify all that apply.

### Step 2: Select 2-3 questions per domain
From each applicable domain bank, select the questions most relevant to what the user
hasn't yet answered. Avoid questions whose answers are already known from prior rounds.

### Step 3: Prioritize unknowns that would change the architecture
Certain unknowns change everything. Ask these before any other domain-specific questions:
- Volume (10/day vs 10,000/hour → sync vs queue)
- Latency requirement (real-time vs batch → different architecture)
- Auth method for integrations (determines security posture)
- Whether similar code already exists (prevents reinvention)

### Step 4: Never ask more than 3 questions per AskUserQuestion call
Group questions logically. If you have 6 questions, make 2 calls.
Batch by theme (e.g., all "input source" questions together, all "error handling" together).

### Step 5: After Round 2, synthesize via AskUserQuestion
Always follow Round 2 with a synthesis check delivered through AskUserQuestion:
```
AskUserQuestion([{
  question: "Let me confirm my understanding before we go deeper.",
  header: "Synthesis check",
  options: [
    { label: "That's correct", description: "[2-3 sentence summary of what you've gathered so far]. If this accurately captures your requirements, select this." },
    { label: "Needs correction", description: "Select this if I've misunderstood something or missed a key detail." }
  ]
}])
```
**NEVER type the synthesis summary as chat text followed by "Sound right?" — use the tool.**

### Step 6: Final round is edge cases only
Round 3 (or 4) questions are specifically about failure modes, edge cases, and
"things you haven't considered." Never ask basic feature questions in Round 3.

---

## When to Stop Interviewing

Stop when:
1. You can describe the full data flow from input to output without ambiguity.
2. You know how every external dependency can fail and what the recovery is.
3. You know what goes in the database and the schema is clear.
4. You've confirmed that no existing codebase module already solves this.
5. You have measurable success criteria.

Do NOT stop interviewing if:
- You're guessing at the volume/frequency.
- You don't know which existing modules this touches.
- The error handling strategy is undefined.
- The scope boundary is fuzzy ("maybe Phase 2 will also include X").

When in doubt, one more targeted question is better than building a plan with a wrong assumption.
