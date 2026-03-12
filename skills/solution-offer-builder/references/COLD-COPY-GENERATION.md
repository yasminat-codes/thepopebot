# Cold Copy Generation

How to write cold outreach openers grounded in Reddit pain language.

---

## The Core Rule

**Use their exact words back to them.**

Cold copy fails when it sounds like it could have been sent to 10,000 people. It works when it sounds like you specifically noticed them.

The Stage 2 `evidence_quotes` field contains verbatim language from Reddit posts. Those words are gold. Use them.

| Approach | Example |
|----------|---------|
| BAD — generic | "Are you struggling with content marketing?" |
| BAD — paraphrase | "I know content creation takes a lot of time" |
| GOOD — verbatim echo | "I noticed someone describing spending '8 hours every Sunday writing content that gets 3 likes' — that was painful to read." |

**Even if you don't have their exact post:** Use the vocabulary, the specificity, the numbers, the frustration tone from evidence_quotes. Sound like you read their posts.

---

## 4 Opener Formats

### Format 1 — Pain-Aware Opener

**Use when:** `intent_level = seeking-solution`

The prospect knows they have a problem and is actively looking for a fix. Lead with validation, then bridge quickly to solution.

**Structure:**
1. Name the specific pain using their language
2. Validate it — acknowledge why it's hard, not just that it exists
3. Bridge to the outcome they'd want
4. One-line offer
5. Low-friction CTA (not "book a call" — make it smaller)

**Template:**
```
Subject: [specific pain in 5-8 words]

[Pain named in their language]. Most [their role/situation] I talk to [normalise — others have it too].

The reason it keeps happening is [root cause framing — make them feel understood, not sold to].

I've built [specific thing] that [outcome in their language]. [One concrete result].

Worth a quick [5-min read / 10-min chat / short demo]?

[Name]
```

**Worked example — pain: "manual CRM updates eating 3 hours every day":**

Subject: CRM that updates itself while you're in calls

Spending 3 hours on CRM updates every day is the kind of thing that looks fine on paper until you realise you're doing the work of a data entry person on top of your actual job.

Most founders I talk to have the same setup: great CRM, terrible adoption because updating it is just... more work.

I built an automation layer that pulls every call note, email, and deal update into your CRM in real time. No manual entry. Founders I've worked with reclaim 10-15 hours a week.

Worth a 10-minute walkthrough?

---

### Format 2 — Competitor-Aware Opener

**Use when:** `competitors_mentioned` is non-empty in the pain point

The prospect has a tool and is frustrated with it. Do NOT attack the competitor. Position from the angle of "what they wish their current tool did."

**Structure:**
1. Reference the tool without attacking it
2. Name the specific frustration with that tool (use their language)
3. State what they actually wanted from it
4. Introduce your offer as the thing that does what they wanted
5. CTA

**Template:**
```
Subject: [Tool name] for [the thing they actually wanted]

[Tool] is great for [what it's actually good at]. But [specific complaint theme] is a real problem — especially when [their specific situation].

What most people who switch to us say they actually wanted was [what the competitor promised but didn't deliver].

[Your offer] does [that thing]. [Specific result].

Would a quick [comparison / walkthrough / example] be useful?
```

**Worked example — HubSpot: "too expensive" + "too complex" for early-stage startup:**

Subject: HubSpot-level pipeline without the HubSpot overhead

HubSpot is genuinely powerful. But at $800/month before you've even hired a second salesperson, and a setup process that needs a specialist — it's a lot.

What most early-stage founders actually need is automated deal tracking, follow-up sequences, and a dashboard they can read in 30 seconds. Not a CRM platform they need to learn.

I set up a fully-configured sales system for [segment] — automated, simple to use, running inside your existing tools. Under $500 total.

Want to see what it looks like in practice?

---

### Format 3 — Outcome-Focused Opener

**Use when:** `intent_level = purchase-ready`

The prospect is ready to buy. They're not looking for education — they're comparing options. Skip the empathy preamble. Lead with the result.

**Structure:**
1. State the outcome directly in their language
2. One line of credibility (how you deliver it / who else you've done it for)
3. One-line offer statement
4. Clear, specific CTA

**Template:**
```
Subject: [Specific outcome in their language]

[Specific result] for [their situation/role] — that's what [your offer] does.

[Credibility: how long it takes / who you've done it for / what it uses].

[Offer in one sentence with investment range].

[Direct CTA — specific and time-bound].
```

**Worked example — pain: "need to start getting consistent outbound leads," intensity 91:**

Subject: 40 qualified outbound leads/week, automated

Consistent outbound at scale for bootstrapped SaaS founders — built and running in two weeks.

I use Clay + Instantly to build hyper-targeted lists, write personalised sequences grounded in real pain language, and run them on autopilot. The founders I've set this up for see 15-40 replies per week within the first month.

Full setup is $3,500. Ongoing management available.

Free audit call this week — I'll tell you exactly what your outbound setup is missing before you commit.

---

### Format 4 — Content-Led Opener

**Use when:** `intent_level = exploring`

The prospect is browsing — aware they might have a problem but not actively seeking a fix. A direct pitch will be ignored or feel off. Lead with something useful instead.

**Structure:**
1. Reference the pain without mentioning your offer
2. Share a useful insight, resource, or example relevant to their situation
3. Soft bridge to your offer — "this is what I do" not "buy this"
4. Optional: low-friction CTA (reply, not book)

**Template:**
```
Subject: [Useful thing, not a pitch]

I've been looking at [their topic] recently and noticed [pattern / insight from your research].

[Share the useful thing — short framework, a result, a resource, an observation].

This is actually the core of what I work on with [segment]. Happy to share more if useful — just reply.

[Name]
```

**Worked example — pain: "not sure if we need to hire or automate," exploring intent:**

Subject: Hire vs automate — quick heuristic

Been looking at how early-stage SaaS teams decide when to hire ops vs automate, and there's a pattern:

If a task takes >2 hours/week, happens >3x/week, and follows a consistent pattern — it's automatable. If it requires judgment, escalation, or relationship context — hire.

Most teams automate when they should hire, and hire when they should automate. The overlap zone (repetitive but judgment-light) is usually the quickest win.

This is the framework I use with founders before building anything. Happy to run through it for your specific situation if useful.

---

## Cold Copy Fields Reference

Each solution in the output contract requires these four fields:

**`subject_line`**
- 4-8 words max
- Specific, not clever
- References the outcome or the pain — never the solution type
- No "Re:" tricks

**`opener`**
- First 1-2 sentences
- Must contain a specific reference to Reddit-voiced pain
- If evidence_quotes exists: echo exact words or numbers
- If not: use the vocabulary and framing from the pain summary

**`offer_statement`**
- One sentence
- What it is + what it delivers + for whom
- No adjectives like "powerful" or "comprehensive" — use specifics

**`cta`**
- Action + timeframe
- Smaller = better for cold outreach (10-minute call > 45-minute demo)
- Specific > vague ("free audit this week" > "let me know if interested")

---

## Smarterflo Voice Rules

When writing cold copy for Smarterflo specifically, these rules override the general templates above.

**Person and voice:**

Yasmine is the face of Smarterflo. Cold copy is written as Yasmine, not as a company.

- Use: "I built..." "I help..." "I set this up for..." "I've worked with..."
- Do not use: "Our team specialises in..." "We offer..." "At Smarterflo..."
- The one exception: the offer formula "We build [system]..." is used only in the positioning statement, not in conversational copy

**Pain reference rule:**

Reference the exact Reddit post or thread pain in the first line. If the evidence_quotes field has verbatim text, use it or echo it closely. Do not paraphrase down to a vague problem statement.

**Offer specificity rule:**

Name the exact type of system Smarterflo would build. Do not say "automate your workflows." Say "automated client reporting system" or "prospect research pipeline." The system name must match the Smarterflo service category identified in Step 0.

**Banned phrases (Smarterflo-specific additions):**

In addition to the general quality check list, never use:
- "AI automation"
- "AI-powered"
- "automate your workflows"
- "leverage AI"
- "streamline your operations"
- "cutting-edge"
- "transform your business"

**CTA standard:**

End every Smarterflo cold email with: "Open to a quick 15-min call to see if it's a fit?" or a close variant. Do not use "book a demo," "schedule time," or "let me know if interested."

---

## Worked Example — Smarterflo Voice

**Context:** Pain point from a Reddit post about manual weekly reporting. Service category: AI Reporting and Analytics.

**Subject:** re: your post about manual reporting

**Body:**

Saw your post in r/agency about spending every Friday pulling data from five tools and building the same spreadsheet.

I built a system that generates that report automatically — pulls from your tools, runs the numbers, and drops the formatted report in Slack every Monday morning. Set it up for a content agency last month — they got 4 hours back every week.

Not sure if it's a fit for what you're dealing with — open to a quick 15-min call to find out?

Yasmine

---

**Why this is correct:**

- Subject references the exact pain (Friday manual reporting) without being clever
- Opener echoes the verbatim Reddit language ("every Friday", "five tools", "same spreadsheet")
- Offer names the exact Smarterflo system (AI Reporting and Analytics) without using the category label
- One concrete result (4 hours/week, Monday morning, Slack delivery)
- First person throughout — Yasmine, not "our team"
- CTA is low-friction, no assumed intent
- No buzzwords

---

## Quality Checks for Cold Copy

Before finalising any cold_offer_copy block:

- [ ] Subject line is specific, not generic
- [ ] Opener references a specific detail from evidence_quotes or pain summary
- [ ] Offer statement names a concrete result (with a number or timeframe if possible)
- [ ] CTA is low-friction and specific
- [ ] Total copy reads as written to one person, not a mass list
- [ ] No AI giveaways: "I hope this finds you well", "I wanted to reach out", "leverage", "streamline", "pain points"
- [ ] Copy is written in first person (Yasmine's voice) — no "our team" or corporate language
- [ ] System named in offer statement is specific — matches Smarterflo service category
- [ ] No banned Smarterflo phrases appear anywhere in the copy
