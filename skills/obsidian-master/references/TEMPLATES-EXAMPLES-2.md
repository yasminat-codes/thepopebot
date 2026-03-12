← See TEMPLATES-EXAMPLES.md for Templates 1–4

---

## 5. Research Note

Save as: `10-Templates/research-note.md`
Folder trigger: `04-Knowledge/`

```markdown
<%*
const topic = await tp.system.prompt("Research topic");
if (!topic) return;
await tp.file.rename(topic);

const parentChoice = await tp.system.suggester(
  ["Consulting Process", "Clients area", "Campaigns", "Knowledge MOC", "Decisions Log", "None"],
  ["03-Areas/smarterflo/processes/Consulting-Process", "03-Areas/smarterflo/clients", "02-Projects/business/campaigns", "04-Knowledge/_MOC-Knowledge", "00-Command-Center/Business-Decisions-Log", "None"]
);
const parentLink = parentChoice !== "None" ? `[[${parentChoice}]]` : "[[04-Knowledge/_MOC-Knowledge]]";

const statusVal = await tp.system.suggester(
  ["Raw", "Processed", "Synthesised"],
  ["raw", "processed", "synthesised"]
);
-%>
---
topic: <% topic %>
source:
source_url:
date_researched: <% tp.date.now("YYYY-MM-DD") %>
type: research
status: <% statusVal %>
parent: <% parentLink %>
tags: [research]
---

# <% topic %>

**Source:**
**URL:**
**Researched:** <% tp.date.now("MMMM D, YYYY") %>
**Parent:** <% parentLink %>

---

## Key Findings

-
-
-

---

## Quotes Worth Keeping

>

---

## My Analysis

**What this means for Smarterflo:**

**What this changes:**

**Questions this raises:**

---

## Connections

- [[04-Knowledge/_MOC-Knowledge]]
<% parentChoice !== "None" && parentChoice !== "04-Knowledge/_MOC-Knowledge" ? `- ${parentLink}` : "" %>
-

---

## Raw Notes

```

---

## 6. Decision Log Entry

Save as: `10-Templates/decision-log.md`
Folder trigger: `00-Command-Center/decisions/`

```markdown
<%*
const decision = await tp.system.prompt("Short description of the decision");
if (!decision) return;
const date = tp.date.now("YYYY-MM-DD");
await tp.file.rename(date + " " + decision);

const statusVal = await tp.system.suggester(
  ["Pending", "Made", "Revisiting", "Reversed"],
  ["pending", "made", "revisiting", "reversed"]
);
const areaVal = await tp.system.suggester(
  ["Business", "Product", "Operations", "Clients", "Content", "Personal"],
  ["business", "product", "operations", "clients", "content", "personal"]
);
-%>
---
decision: <% decision %>
date: <% tp.date.now("YYYY-MM-DD") %>
status: <% statusVal %>
area: <% areaVal %>
owner: Yasmine
type: decision
tags: [decision]
---

# Decision: <% decision %>

**Date:** <% tp.date.now("MMMM D, YYYY") %>
**Area:** `= this.area`
**Status:** `= this.status`
**Log:** [[00-Command-Center/Business-Decisions-Log]]

---

## Context

What situation or problem triggered this decision:

---

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
|        |      |      |
|        |      |      |
|        |      |      |

---

## Decision Made

**Chosen option:**

**Rationale:**

---

## Next Steps

- [ ]
- [ ]

---

## Outcome (fill in later)

**What happened:**

**Would I make the same call again:**

---

*Logged in [[00-Command-Center/Business-Decisions-Log]]*
```

---

## 7. Weekly Review

Save as: `10-Templates/weekly-review.md`
Folder trigger: `00-Daily-Notes/weekly/`

```markdown
<%*
const weekNum = tp.date.now("YYYY-[W]WW");
await tp.file.rename(weekNum + " Weekly Review");
const weekStart = tp.date.now("YYYY-MM-DD", 1 - parseInt(tp.date.now("d") || "1"));
-%>
---
week: <% weekNum %>
week_start: <% weekStart %>
type: weekly-review
tags: [weekly-review]
---

# Weekly Review — <% weekNum %>

**Week of:** <% weekStart %>
**Hub:** [[00-Command-Center/Hub]]

---

## Last Week's Wins

What got done that mattered:
-
-
-

---

## What Didn't Go Well

Be honest — what slipped, stalled, or went sideways:
-

---

## Lessons

What to do differently:
-

---

## This Week's Priorities

Top 3 that move the needle:
1.
2.
3.

**Other things to get done:**
-
-

---

## Energy & Health Check-In

**Energy this past week (1–10):**
**Sleep:**
**Exercise:**
**What's draining me:**
**What's energising me:**

---

## Habit Review

| Habit | M | T | W | T | F | S | S |
|-------|---|---|---|---|---|---|---|
| Morning routine | | | | | | | |
| Deep work block | | | | | | | |
| Inbox zero | | | | | | | |

---

## Open Loops

Decisions needed, waiting on others:
-

---

## Orphan Audit

Notes with no inbound or outbound links — fix before next week:

```dataview
LIST
FROM ""
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
SORT file.mtime DESC
```

---

## Notes

```

---

## 8. Content Idea

Save as: `10-Templates/content-idea.md`
Folder trigger: `15-Smarterflo/LinkedIn-Strategy/ideas/`

```markdown
<%*
const hook = await tp.system.prompt("Hook or angle (short)");
if (!hook) return;
const date = tp.date.now("YYYY-MM-DD");
await tp.file.rename(date + " " + hook);

const platformVal = await tp.system.suggester(
  ["LinkedIn", "Instagram", "Threads", "X", "Newsletter", "YouTube"],
  ["linkedin", "instagram", "threads", "x", "newsletter", "youtube"]
);
const contentTypeVal = await tp.system.suggester(
  ["Post", "Carousel", "Video", "Newsletter", "Thread", "Article"],
  ["post", "carousel", "video", "newsletter", "thread", "article"]
);
const statusVal = await tp.system.suggester(
  ["Idea", "Outline", "Draft", "Ready", "Scheduled", "Published"],
  ["idea", "outline", "draft", "ready", "scheduled", "published"]
);
const pillarVal = await tp.system.suggester(
  ["Authority", "Story", "Education", "Social Proof", "Offer"],
  ["authority", "story", "education", "social-proof", "offer"]
);
-%>
---
hook: <% hook %>
platform: <% platformVal %>
content_type: <% contentTypeVal %>
status: <% statusVal %>
target_audience:
publish_date:
pillar: <% pillarVal %>
date_created: <% tp.date.now("YYYY-MM-DD") %>
type: content
tags: [content]
---

# <% hook %>

**Platform:** `= this.platform`
**Type:** `= this.content_type`
**Status:** `= this.status`
**Pillar:** `= this.pillar`
**MOC:** [[15-Smarterflo/LinkedIn-Strategy/_Content-MOC]]

---

## Hook / Opening Line

(The first sentence that makes someone stop scrolling)

---

## Key Points

1.
2.
3.

---

## Target Audience

Who this is for and what their pain or goal is:

---

## Call to Action

What I want them to do after reading:

---

## Supporting Evidence / Story

Data, client example, personal story, or case study:

---

## Draft

(Write the actual content here — run through de-ai-fy before publishing)

---

## Notes

*Tracked in [[15-Smarterflo/LinkedIn-Strategy/_Content-MOC]]*
```
