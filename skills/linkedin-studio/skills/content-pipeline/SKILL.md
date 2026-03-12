---
name: ls:content-pipeline
description: PROACTIVELY runs the complete LinkedIn content studio pipeline end-to-end — from research through writing, humanizing, structure review, visual creation, calendar placement, and Metricool scheduling — in a single orchestrated command with configurable stage selection, mandatory gate enforcement, and clear failure recovery at every step.
model: opus
context: fork
allowed-tools: Read Write Bash Agent Glob Grep WebFetch WebSearch AskUserQuestion
metadata:
  version: "2.0.0"
---

# ls:content-pipeline

THE MASTER ORCHESTRATOR. Executes the full LinkedIn content studio workflow in sequence. Run all 7 stages or start from any stage. Every mandatory gate is enforced — pipeline halts on failure until the user fixes or explicitly overrides.

---

## Pipeline Stages

| # | Stage | Skill | Mandatory |
|---|-------|-------|-----------|
| 1 | RESEARCH | `ls:research-engine` | No — skip if topic provided |
| 2 | WRITE | `ls:content-writer` | Yes (if no content provided) |
| 3 | HUMANIZE | `ls:humanizer` | YES — cannot skip |
| 4 | STRUCTURE | `ls:structure-reviewer` | YES — cannot skip |
| 5 | VISUAL | `ls:visual-prompter` and/or `ls:canva-designer` | No |
| 6 | CALENDAR | `ls:content-calendar` | No |
| 7 | SCHEDULE | `ls:batch-scheduler` | No — or save as draft |

**Mandatory stages (3 and 4) cannot be skipped under any circumstances.**

---

## Pipeline Modes

| Mode | Description |
|------|-------------|
| `full` | Run all 7 stages from scratch |
| `partial` | User selects which stages to include |
| `start-from:[stage]` | Begin at a specific stage (content already exists) |
| `resume:[post_id]` | Resume a specific post from its current status |

---

## Phase 1 — Input and Pipeline Configuration

### 1.1 Collect Input

Ask:
1. **Mode:** full / partial / start-from / resume?
2. **Topic or content:**
   - If mode = full or partial starting at RESEARCH: topic keyword or brief
   - If mode = start-from:WRITE or later: paste existing content or provide post ID
   - If mode = resume: provide post ID from content_queue
3. **Visual preference:** none / ai-prompts (visual-prompter) / canva / both
4. **Scheduling:** schedule now / add to calendar only / save as draft

### 1.2 Resolve Resume Mode

If mode = `resume:[post_id]`:
```sql
SELECT id, status, humanized_content, hook, content_pillar, media_urls
FROM content_queue WHERE id = '[post_id]';
```

Map current status → starting stage:
```
draft       → start at WRITE (or HUMANIZE if content present)
humanized   → start at STRUCTURE
reviewed    → start at VISUAL
visual      → start at CALENDAR or SCHEDULE
approved    → start at SCHEDULE
```

### 1.3 Display Pipeline Plan

Show confirmed plan before executing:

```
PIPELINE PLAN
──────────────────────────────────────────────────────────────
Mode: full  |  Topic: "AI consulting project failures"
──────────────────────────────────────────────────────────────
  [1] RESEARCH    → ls:research-engine          will run
  [2] WRITE       → ls:content-writer           will run
  [3] HUMANIZE    → ls:humanizer                MANDATORY
  [4] STRUCTURE   → ls:structure-reviewer       MANDATORY
  [5] VISUAL      → ls:canva-designer           will run
  [6] CALENDAR    → ls:content-calendar         will run
  [7] SCHEDULE    → ls:batch-scheduler          save as draft
──────────────────────────────────────────────────────────────
Proceed? [yes / adjust / cancel]
```

---

## Phase 2 — Stage Execution Engine

Execute each active stage in sequence. After each stage:
1. Show stage output summary
2. Run gate check
3. On gate pass: proceed
4. On gate fail: HALT (see Phase 4)

### Progress Display

```
PIPELINE PROGRESS
──────────────────────────────────────────────────────────────
✓ [1] RESEARCH    complete  (3 angles found)
✓ [2] WRITE       complete  (847 chars, TL pillar)
● [3] HUMANIZE    running...
  [4] STRUCTURE   pending
  [5] VISUAL      pending
  [6] CALENDAR    pending
  [7] SCHEDULE    pending
──────────────────────────────────────────────────────────────
```

---

## Phase 3 — Stage Gate Results

After each stage completes, evaluate gates.

### Stage Gates Reference

| Stage | Gate | Pass Condition | Type |
|-------|------|---------------|------|
| RESEARCH | G-R1 | At least 1 topic angle returned | Hard |
| WRITE | G-W1 | Content 150–3000 chars | Hard |
| WRITE | G-W2 | Hook ≤ 20 words | Hard |
| WRITE | G-W3 | Content pillar assigned | Hard |
| HUMANIZE | G-H1 | AI score reduced (if scored) | Soft |
| HUMANIZE | G-H2 | Brand vocabulary present | Soft |
| HUMANIZE | G-H3 | Avoid-words absent | Hard |
| STRUCTURE | G-S1 | Quality score ≥ 70/100 | Hard |
| STRUCTURE | G-S2 | Hook strength ≥ 7/10 | Hard |
| STRUCTURE | G-S3 | CTA present | Soft |
| VISUAL | G-V1 | At least 1 prompt or design URL returned | Soft |
| CALENDAR | G-C1 | scheduled_at set in future | Soft |
| SCHEDULE | G-SC1 | Metricool submission 200 OK | Hard |

**Hard gate fail = pipeline HALT.**
**Soft gate fail = warning shown, pipeline continues.**

Show after each stage:
```
STAGE 4 — STRUCTURE REVIEWER
────────────────────────────
G-S1 Quality score:  82/100  ✓ PASS
G-S2 Hook strength:   9/10  ✓ PASS
G-S3 CTA present:      yes  ✓ PASS

Stage 4 PASSED — proceeding to Visual
```

---

## Phase 4 — Failure Handling

When a hard gate fails, pipeline HALTS immediately.

```
PIPELINE HALTED
──────────────────────────────────────────────────────────────
Stage: STRUCTURE REVIEWER
Failed gate: G-S1 — Quality score: 58/100 (minimum: 70)

Issue: Hook too long (28 words), weak value proposition.

OPTIONS:
  [1] Fix now    — Re-run structure-reviewer with revised content
  [2] Edit post  — Paste corrected content and retry this stage
  [3] Override   — Accept below-minimum score and continue
                   (adds [QUALITY-OVERRIDE] flag to post record)
  [4] Abort      — Stop pipeline, save post as draft in current state

Choose option:
```

**Override behavior:**
- Allowed on soft gate fails only (G-H1, G-H2, G-V1, G-C1, G-S3)
- Hard gates (G-W1, G-W2, G-H3, G-S1, G-S2, G-SC1) CANNOT be overridden
- Override adds tag to content_queue record: `override_gates: ['G-S3']`

**Abort behavior:**
- Save current post state to content_queue with status matching last passed stage
- Return post ID so user can resume later with `resume:[post_id]`

---

## Phase 5 — Stage Invocation Details

Each stage is invoked as a sub-agent (via SDK fork). Pass context forward between stages.

### RESEARCH → WRITE handoff
Pass: `topic`, `research_angles[]`, `competitor_gaps[]`, `content_pillar_suggestion`, `strategy_context`

`strategy_context` includes:
- `relevant_stories[]` — Story IDs from strategy/STORY-BANK.md matching the topic
- `audience_segment` — ICP segment from strategy/AUDIENCE.md
- `positioning_angle` — Competitive moat angle from strategy/POSITIONING.md
- `voice_markers[]` — Relevant Yasmine voice markers from strategy/BRAND-VOICE.md

### WRITE → HUMANIZE handoff
Pass: `post_content`, `hook`, `content_pillar`, `post_id`

### HUMANIZE → STRUCTURE handoff
Pass: `humanized_content`, `post_id`, `brand_voice_profile` (loaded once, passed forward)

### STRUCTURE → VISUAL handoff
Pass: `reviewed_content`, `hook`, `key_points[]`, `content_pillar`, `post_id`, `quality_score`

### VISUAL → CALENDAR handoff
Pass: `final_content`, `media_urls[]` or `ai_prompts[]`, `post_id`, `visual_type`

### CALENDAR → SCHEDULE handoff
Pass: `post_id`, `scheduled_at`

→ Full handoff schemas: `references/STAGE-HANDOFFS.md`

---

## Phase 6 — Pipeline Summary

On completion (all active stages done):

```
PIPELINE COMPLETE
══════════════════════════════════════════════════════════════
Post: "Why most AI consulting projects fail in week 1"
Pillar: Thought Leadership
Quality score: 82/100
──────────────────────────────────────────────────────────────
✓ [1] RESEARCH    3 angles researched
✓ [2] WRITE       851 chars drafted
✓ [3] HUMANIZE    AI score reduced, brand voice applied
✓ [4] STRUCTURE   82/100 — hook 9/10 — CTA ✓
✓ [5] VISUAL      Canva design created (5 carousel slides)
✓ [6] CALENDAR    Scheduled: Tue 03 Mar 08:00 UTC
✓ [7] SCHEDULE    Metricool ID: mc_8ax3

Post ID: [uuid] | Status: scheduled
══════════════════════════════════════════════════════════════
```

On partial completion (some stages skipped or saved as draft):

```
POST SAVED AS DRAFT
──────────────────────────────────────────────────────────────
Post ID: [uuid] | Status: reviewed
Completed stages: RESEARCH, WRITE, HUMANIZE, STRUCTURE
Remaining stages: VISUAL, CALENDAR, SCHEDULE

Resume with: ls:content-pipeline → mode: resume:[post_id]
```

---

## State Persistence

After every completed stage, update Neon immediately:
```sql
UPDATE content_queue
SET status = '[stage_status]', updated_at = NOW()
WHERE id = '[post_id]';
```

Stage → status mapping:
```
WRITE complete     → 'draft'
HUMANIZE complete  → 'humanized'
STRUCTURE pass     → 'reviewed'
VISUAL complete    → 'visual'
CALENDAR placed    → 'visual' (scheduled_at updated)
SCHEDULE success   → 'scheduled'
```

This ensures pipeline can always be resumed from the correct stage.

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Sub-skill invocation fails | Show error, offer retry or skip |
| Neon unavailable | Warn, continue pipeline in memory only, save all at end |
| METRICOOL_API_KEY missing at SCHEDULE | Skip schedule, save as approved |
| User aborts mid-pipeline | Save current state, return post_id for resume |
| All hard gates pass but soft warns exist | Show warning summary, continue |

---

## References

- `references/STAGE-HANDOFFS.md` — Inter-stage context schemas
- `references/GATE-DEFINITIONS.md` — Full gate rules, thresholds, and override rules
- `references/PIPELINE-MODES.md` — Mode selection decision tree
- `strategy/CONTENT-PILLARS.md` — Canonical pillar distribution
- `strategy/STORY-BANK.md` — Real stories for content grounding
- `strategy/BRAND-VOICE.md` — Yasmine-specific voice and vocabulary
- `strategy/AUDIENCE.md` — ICP segments and buying journey
- `strategy/POSITIONING.md` — Competitive moat angles
- `strategy/AUTHORITY-PLAYBOOK.md` — Stage-based posting strategy
