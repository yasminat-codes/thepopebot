# Note Output Template

The AI is instructed to produce comprehensive, in-depth learning notes in this exact format. The prompt in `fetch_and_learn.py` references this structure.

---

## Template

```markdown
# {Video Title}

**Channel:** {channel} | **Published:** {date} | **Duration:** {duration}
**URL:** {url}

---

## TL;DR
{3-5 sentences capturing the core argument, what the video actually teaches, and who it's for. Be opinionated — state the conclusion, not just the topic.}

## Key Takeaways
- {specific, factual takeaway — numbers, names, frameworks where present}
- {specific takeaway 2}
- {specific takeaway 3}
- {specific takeaway 4}
- {specific takeaway 5}
- {add more if the content warrants it — aim for 6-10 for longer videos}

## Full Breakdown

### {Section or Topic Name}
{Detailed explanation, 4-8 sentences. Cover: what it is, how it works, why it matters, any nuances or caveats the speaker raised. This is the main substance of the notes — be thorough.}

### {Section or Topic Name 2}
{Detailed explanation. Include examples given in the video, step-by-step processes described, comparisons made, problems solved.}

### {Section or Topic Name 3}
{Continue for every major section of the video. For a 60-minute video expect 6-10 sections. Each section should be dense enough to stand alone as a reference.}

## Core Concepts & Definitions

### {Term or Framework Name}
**What it is:** {definition in 1-2 sentences}
**Why it matters:** {practical significance}
**How it works:** {mechanism or process, as described in the video}

### {Term or Framework Name 2}
**What it is:** {definition}
**Why it matters:** {significance}
**How it works:** {mechanism}

{Repeat for every concept, tool, framework, or term introduced in the video that a reader might not know.}

## Step-by-Step Processes
{Include this section only if the video walks through a process, tutorial, setup, or workflow.}

1. **{Step name}** — {what to do and why}
2. **{Step name}** — {what to do and why}
3. **{Step name}** — {continue for all steps}

## Actionable Insights
- {Specific thing to do, grounded in the video. "The speaker recommends X because Y" not generic "Consider doing X"}
- {Another concrete, immediately applicable action}
- {Tool, technique, or approach worth trying}
- {Pitfall to avoid, based on what was said}
- {Aim for 5-8 actionable items for longer videos}

## Memorable Quotes
> "{exact or near-exact quote that crystallizes a key point}"
— {speaker name if known}

> "{another quote worth preserving}"

## Connections & Context
{How does this relate to other concepts, tools, or ideas? What prior knowledge does it build on? What does it contradict or update? 3-5 sentences placing the video in broader context.}

## Questions This Raises
- {Open question worth researching further — specific, not generic}
- {Tension or contradiction the video surfaces}
- {Something the speaker didn't address that seems important}
- {Follow-up: what would change your mind on this?}

## Tags
#{topic} #{subtopic} #{format}
```

---

## Rules for the AI

1. **Depth over brevity** — these notes replace watching the video. A reader should come away understanding the content as well as if they watched it. Aim for 600-1200 words of note body.
2. **Full Breakdown is mandatory** — this is the core section. Cover every major topic the video addresses. For a 30-60 minute video, expect 5-10 subsections.
3. **TL;DR must be opinionated** — not "this video covers X", but "the speaker argues X because Y, and the key insight is Z".
4. **Takeaways must be specific** — not "AI is useful" but "the speaker claims GPT-4 completes their research workflow 3x faster by handling the first draft".
5. **Core Concepts** — define every non-obvious term, tool, or framework introduced. Don't assume the reader knows what was explained in the video.
6. **Step-by-Step** — if the video is a tutorial or walkthrough, reproduce the steps faithfully. These notes should be usable as a reference guide.
7. **Actionable Insights** — minimum 4 items. Ground each in what was actually said. Avoid generic advice.
8. **Quotes** — pull lines that crystallize the point or are memorable enough to repeat. Omit only if truly none stand out.
9. **Connections** — place the video in context. What does it relate to? What prior knowledge unlocks it?
10. **Questions** — surface genuine follow-up threads, not throwaway observations.
11. **Output only the markdown note** — no preamble, no meta-commentary, no "here are your notes:".
