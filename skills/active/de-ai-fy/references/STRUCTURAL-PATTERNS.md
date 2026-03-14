# Structural Patterns — Formatting AI Over-Structures

**How AI over-formats prose, why it's a tell, and when to flatten vs. keep structure.**

---

## The Core Problem

AI turns everything into a document. Conversational writing, emails, short posts, casual messages — AI formats them all as if they're reference manuals. Real humans write paragraphs.

Structure is a tool. AI treats it as a default.

---

## Pattern 1: Headers in Conversational Text

**What AI does:**
Adds `## Headers` to 400-word email replies, blog posts under 1,000 words, social media content, and anything conversational. Every topic gets its own header.

**The test:**
Would a real person sending this email, writing this post, or composing this message naturally break it into titled sections? If no — flatten it.

**When headers ARE appropriate:**
- Documentation and technical guides (any length)
- Articles over 1,500 words where navigation helps
- Tutorials with distinct phases
- Reports meant to be referenced, not read through
- FAQs and reference materials

**When to kill headers:**
- Emails (almost always)
- Short articles under 1,000 words
- Social media posts
- Chat/messaging contexts
- Opinion pieces and essays
- Any piece with a single clear topic
- Anything you'd read front-to-back without needing to navigate

**How to flatten:**
Replace each header + section with an opening sentence that does the same work.

**Before (AI):**
> ## Overview
> This proposal outlines three key changes to the onboarding process.
>
> ## Change 1: Shorter Welcome Email
> The current welcome email is 800 words. We recommend cutting it to 200 words.
>
> ## Change 2: Video Introduction
> A 3-minute video introduction would help new users get oriented faster.

**After (human):**
> This proposal covers three changes to onboarding. First, the welcome email needs to drop from 800 words to 200 — it's too long. Second, a 3-minute video introduction would get new users oriented faster.

---

## Pattern 2: Bullet Compulsion

**What AI does:**
Converts every set of ideas into a bulleted list, regardless of whether the content is actually list-like. Prose becomes fragmented. Ideas lose their connective tissue.

**The test:**
Are these items actually parallel and discrete, or are they parts of a flowing argument? If the latter — write prose.

**When bullets ARE appropriate:**
- Genuinely discrete items: shopping lists, feature lists, step lists
- 4+ items where prose would be unwieldy
- Reference material people will scan, not read
- Items without natural prose connectors

**When to kill bullets:**
- 2 items (just use "and")
- Items that naturally flow: A causes B causes C
- Ideas that need explanation, not enumeration
- Content that's being read, not scanned
- Emotional or persuasive writing
- Any context where conversation is the register

**How to flatten bullets:**
Connect with natural prose language.

**Before (AI):**
> There are several advantages to this approach:
> - It reduces processing time
> - It lowers costs
> - It improves accuracy
> - It simplifies the workflow

**After (human):**
> This approach reduces processing time and cuts costs while improving accuracy — the whole workflow gets simpler.

---

## Pattern 3: Sub-Bullets Under Bullets Under Bullets

**What AI does:**
Creates nested bullet structures 3 levels deep. Main point → supporting points → sub-supporting points. Visual complexity as a substitute for clear thinking.

**The fix:**
Maximum one level of nesting, and only when the relationship between parent and child is genuinely hierarchical (categories with members, steps with sub-steps). Otherwise flatten everything to prose.

---

## Pattern 4: Bold on Everything

**What AI does:**
Bolds random phrases within body text constantly. Every paragraph has 2–4 bolded phrases. Bold becomes visual noise, not emphasis.

**When bold IS appropriate:**
- The single most important word or phrase in a section
- Key terms being defined for the first time
- Warning/caution statements in technical docs
- Critical action in a step-by-step guide

**The rule:**
If more than 10% of words in a section are bolded, all the bold is doing nothing. Cut it back to 1–2 instances per section maximum.

---

## Pattern 5: "Key Takeaways" at the End of Everything

**What AI does:**
Ends every piece with a "Key Takeaways", "Summary", or "Conclusion" section that repeats the main points. Even 400-word blog posts get a recap.

**Why it's a tell:**
Real writers trust readers to have read what they wrote. They don't re-summarize.

**The fix:**
Cut the recap section. End with a strong final point or call to action instead.

**Exception:** Long-form content (2,000+ words), technical documentation, and educational content where a genuine summary serves navigation.

---

## Pattern 6: Numbered Lists for Non-Sequential Content

**What AI does:**
Numbers lists even when the items aren't sequential. "5 reasons why X" where the reasons have no particular order. Numbered list implies sequence or ranking — AI uses it for any collection of items.

**The fix:**
- Use numbered lists only when order matters (steps, rankings, sequences)
- Use bullets for non-ordered collections
- Use prose for 3 items or fewer

---

## Pattern 7: Table of Contents in Short Content

**What AI does:**
Adds a "Table of Contents" to 800-word articles. No one needs a TOC for 800 words.

**When TOC is appropriate:**
- Documentation over 2,000 words with multiple major sections
- Technical guides meant to be navigated, not read linearly
- Reference materials

**When to kill the TOC:**
- Anything under 2,000 words
- Narrative/essay content
- Emails
- Social posts

---

## Pattern 8: Introduction + Conclusion Headers in Short Pieces

**What AI does:**
Adds explicit "Introduction" and "Conclusion" headings to short pieces. The word "Introduction" adds no information — the first paragraph IS the introduction.

**The fix:**
Cut both. Dive in at the start. End with substance, not an announcement that you're ending.

---

## Pattern 9: "In This Article, I Will..." Openers

**What AI does:**
Opens pieces by listing what the piece will cover. "In this article, we will explore X, Y, and Z." Then covers X, Y, and Z. Doubles the content needlessly.

**The fix:**
Cut the meta-announcement. Start with X directly.

**Before:**
> In this post, I'm going to walk you through three ways to improve your team's communication. First, I'll cover async updates. Then I'll discuss meeting hygiene. Finally, I'll share some tools that can help.

**After:**
> The fastest way to improve your team's communication is fixing async updates.

---

## The Flatten Checklist

Before finalizing, check:

- [ ] No headers in conversational/short content (under 1,000 words, unless technical)
- [ ] Bullet lists only where items are genuinely discrete and parallel
- [ ] No nested bullet structures beyond 1 level
- [ ] Bold reserved for actual emphasis — not everywhere
- [ ] No "Key Takeaways" / "Summary" section in short content
- [ ] Numbered lists only for sequential steps or ranked items
- [ ] No table of contents under 2,000 words
- [ ] No "Introduction" / "Conclusion" headers
- [ ] No "In this piece, I will..." opener
- [ ] The piece reads like prose, not a slide deck

---

## When to Keep Structure

Structure serves readers. Kill it when it's performance. Keep it when it actually helps.

| Content Type | Structure Recommendation |
|-------------|--------------------------|
| Documentation | Keep — readers navigate |
| Tutorial steps | Keep — sequence matters |
| Technical reference | Keep — headers aid lookup |
| Long-form article (2,000+) | Keep section headers, cut sub-bullets |
| Short article (under 1,000) | Flatten everything |
| Email | No headers, minimal bullets |
| Blog post (700-1,500 words) | Flatten unless genuinely tutorial |
| Social media | No structure at all |
| Chat/Slack message | No structure at all |
| Opinion piece | Prose only |
| Press release | Prose + minimal formatting |
