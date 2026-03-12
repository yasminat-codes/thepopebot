---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
version: {{VERSION}}
author: {{AUTHOR}}
category: {{CATEGORY}}
allowed-tools: {{TOOLS}} Read Glob Grep Write
---

# {{SKILL_NAME}}

{{DESCRIPTION}}

## Overview

This skill is interview-first. It asks structured questions across multiple rounds before
producing any output. The questions are opinionated — they reveal the right answer through
careful dialogue rather than accepting vague input. Rushing through the interview produces
worse output than investing time in it.

**Interview rounds:** 3 (core, refinement, confirmation)
**Time investment:** 10-20 minutes of dialogue
**Output produced after:** Final round confirmed
**Defaults:** Strong and opinionated — explicitly stated so users can override

---

## Interview Philosophy

- Ask one block of related questions at a time (3-5 per round)
- Offer concrete defaults for every question — reduce cognitive load
- Show "why this matters" for each question — don't just request data
- Listen for implied constraints in answers (not just explicit ones)
- Push back on answers that will produce poor results
- Confirm your interpretation before acting on it

---

## Pre-Interview: Context Gathering

Before asking the user anything, silently gather context from the current environment.
This allows the interview to be pre-populated with sensible defaults.

```bash
# Silent context gathering — do not output to user
pwd
ls -la 2>/dev/null | head -30
cat package.json 2>/dev/null | head -20
cat pyproject.toml 2>/dev/null | head -20
git log --oneline -5 2>/dev/null
git remote -v 2>/dev/null | head -5
```

Use these findings to:
- Pre-fill obvious answers the user shouldn't have to type
- Set smarter defaults based on existing patterns
- Skip questions whose answers are already unambiguous
- Flag contradictions between stated goals and existing state

---

## Round 1: Core Requirements

{{PHASES}}

Ask these questions as a single block. Do not proceed to Round 2 until all are answered.

```
I need to understand what you're trying to accomplish before I can help effectively.
Please answer these questions — I've included my best guess in brackets for each.
Override any that don't apply.

1. **What is the primary goal?**
   What should exist or be different when this is complete?
   (My guess based on context: {auto-detected guess})

2. **Who is this for?**
   Who will use or be affected by the output — yourself, your team, end users, automated systems?
   (Default: yourself, working in this project)

3. **What constraints are non-negotiable?**
   Technology stack, timeline, budget, team size, existing patterns to follow.
   (Detected: {auto-detected stack/constraints})

4. **What does success look like?**
   Specific, measurable criteria. "It works" is not enough — what exactly should work?
   (Suggested: {context-derived suggestion})

5. **What have you already tried or decided?**
   Anything I should not re-suggest or re-examine?
   (None detected)
```

**After receiving Round 1 answers:**

Interpret the answers. Note any ambiguities. Note any answers that will lead to problems.
Before proceeding to Round 2, briefly confirm your interpretation:

```
Based on your answers, here's what I understand:
- Goal: {interpreted goal}
- Audience: {interpreted audience}
- Hard constraints: {list}
- Success criteria: {measurable outcomes}
- Off the table: {list}

One concern before I continue: {surface any red flag here, or omit if none}

Is this accurate? Any corrections before I go deeper?
```

Wait for confirmation. If corrected, update the interpretation and re-confirm.

---

## Round 2: Refinement and Trade-offs

Drill into the areas that most affect the output quality. Customize these questions based
on Round 1 answers. The questions below are a template — adapt them.

```
Good. Now I need to understand the trade-offs and preferences.

6. **Scale and growth: where do you expect to be in 12 months?**
   This affects whether we optimize for simplicity now or build to scale immediately.
   - Option A: Keep it simple now, refactor later (recommended for most situations)
   - Option B: Build for 10x scale from the start (higher upfront cost)
   - Option C: Unsure — help me think through this
   (My recommendation given your constraints: Option {A|B|C})

7. **Team dynamics: who else will work on this?**
   Solo, small team (2-5), or larger team?
   - Solo → optimize for your own speed and preferences
   - Small team → prioritize conventions and documentation
   - Larger team → strict standards, automated enforcement
   (Detected team indicators: {git log author count or "solo"})

8. **Maintenance burden: how much ongoing attention can this get?**
   This affects technology choices significantly.
   - High-maintenance OK → cutting-edge tools, more power
   - Low-maintenance required → proven boring tech, less power
   (Suggested given stated constraints: {suggestion})

9. **Existing codebase: how does this relate to what already exists?**
   - Greenfield: starting fresh, no legacy to worry about
   - Extension: adding to existing codebase, must match patterns
   - Replacement: replacing existing component, must maintain compatibility
   (Detected: {based on directory contents})

10. **Risk tolerance: what happens if this fails?**
    - Low stakes: experiment freely, iterate fast
    - Medium stakes: basic safety nets needed
    - High stakes: need formal validation, rollback, monitoring
    (Suggested given context: {suggestion})
```

**After receiving Round 2 answers:**

Surface any trade-offs the user should know they are making:

```
I want to flag a few trade-offs you're implicitly accepting with these choices:

Trade-off 1: {option chosen} gives you {benefit} but costs {cost}.
Is that acceptable?

Trade-off 2: {option chosen} and {other option} are in tension —
you typically can't have both. Which matters more?

If those trade-offs are acceptable, I'm ready to finalize. If not, let's revisit {question N}.
```

---

## Round 3: Confirmation and Final Details

This is the last round before output generation. Get the final specifics and confirm
the plan before executing.

```
Almost there. A few final details:

11. **Output format preference?**
    How would you like to receive the result?
    - Option A: Single comprehensive document
    - Option B: Multiple focused files
    - Option C: Inline code with explanations
    - Option D: Executive summary + detailed appendix
    (Recommended for your stated goal: Option {A|B|C|D})

12. **Level of detail?**
    - Brief: key decisions and rationale only
    - Standard: full explanation with examples (recommended)
    - Exhaustive: every detail, every edge case, every alternative considered

13. **Anything else I should know?**
    Open field — anything relevant that the questions above didn't capture.
```

**Final confirmation before output:**

```
I'm ready to produce the output. Here's the final plan:

## What I'll produce:
{list of outputs}

## Key decisions made:
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {topic} | {choice} | {why} |
| {topic} | {choice} | {why} |

## Assumptions I'm making:
- {assumption 1}
- {assumption 2}

## What's explicitly out of scope:
- {item}
- {item}

Type "go" to proceed, or correct anything above.
```

---

## Output Generation

{{QUALITY_GATES}}

Only after "go" (or equivalent affirmation) — generate the output.

Apply all answers from all three rounds. Do not output a generic result —
every decision should be traceable to a specific interview answer.

### Output Quality Standards

- [ ] Every major section traces to at least one interview answer
- [ ] No placeholders or "fill this in" sections in the final output
- [ ] Trade-offs are acknowledged, not hidden
- [ ] Assumptions are explicit, not buried
- [ ] Format matches the stated preference from Question 11
- [ ] Detail level matches the stated preference from Question 12

---

## Opinionated Defaults Reference

When users don't specify, use these defaults. State them explicitly so users can override:

| Topic | Default | Reason |
|-------|---------|--------|
| Scale | Simple now | Premature optimization is the enemy |
| Documentation | Inline comments + README | Lowest friction for maintainability |
| Error handling | Fail loudly | Silent failures are harder to debug |
| Testing | Cover happy path + top 3 error cases | 80/20 value |
| Dependencies | Minimal and well-maintained | Less surface area = less risk |
| File structure | Follow existing project conventions | Consistency beats correctness |

---

## References

{{REFERENCES}}

---

*Tier 4-5 interview-heavy skill. Front-loads requirements gathering to back-load quality
output. For single-shot analysis without interview, see advanced-multi-tool template.*
