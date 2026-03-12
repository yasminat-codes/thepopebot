# Pipeline Modes Reference

## Available Modes

| Mode                   | Description                                                             | When to Use                                           |
|------------------------|-------------------------------------------------------------------------|-------------------------------------------------------|
| `full`                 | All 7 stages, starting from INPUT                                       | Creating new content from scratch                     |
| `partial`              | User selects which stages to run                                        | Some stages already completed; cherry-pick the rest   |
| `start-from:[stage]`   | Begin at a specific stage, run all remaining stages through SCHEDULE    | Content exists but needs processing from a known point |
| `resume:[post_id]`     | Load existing post from `ls_content_queue`, infer stage from status    | Pipeline was interrupted; continue where it left off  |

---

## Mode Details

### `full`

Runs all 7 stages in sequence:
```
INPUT → RESEARCH → WRITE → HUMANIZE → STRUCTURE → VISUAL → CALENDAR → SCHEDULE
```
Use when starting from a niche/keyword brief with no existing content.

---

### `partial`

User specifies an explicit list of stages to execute. Stages run in their natural order regardless of selection order.

Example invocation:
```
mode: partial
stages: [HUMANIZE, STRUCTURE, VISUAL]
```

The skill validates that the input contract for the first selected stage is satisfied before running.

---

### `start-from:[stage]`

Begins at the named stage and runs every subsequent stage through to SCHEDULE.

Valid stage names:
- `RESEARCH`
- `WRITE`
- `HUMANIZE`
- `STRUCTURE`
- `VISUAL`
- `CALENDAR`
- `SCHEDULE`

Example invocation:
```
mode: start-from:STRUCTURE
```

The skill validates that the STRUCTURE input contract fields (`humanized_content`, `post_id`, `ai_score`, `brand_voice_profile`) are present before proceeding.

---

### `resume:[post_id]`

Loads the post record from `ls_content_queue` using `post_id`, reads the `status` field, maps it to a stage, and continues from that stage.

**Status → Stage Mapping**

| `ls_content_queue` status | Resume from stage |
|---------------------------|-------------------|
| `draft`                   | WRITE             |
| `humanized`               | STRUCTURE         |
| `reviewed`                | VISUAL            |
| `visual_added`            | CALENDAR          |
| `approved`                | SCHEDULE          |

If status is `scheduled` or `published`, the post is already complete and should not be resumed.

Example invocation:
```
mode: resume:p_20260301_001
```

---

## Decision Tree — Choosing a Mode

```
Do you have any existing content?
|
+-- NO --> Use: full
|
+-- YES --> Has the content been humanized?
            |
            +-- NO --> Has anything been written at all?
            |          |
            |          +-- NO --> Use: full (or start-from:RESEARCH if topic is known)
            |          |
            |          +-- YES --> Use: start-from:HUMANIZE
            |
            +-- YES --> Has it been structurally reviewed?
                        |
                        +-- NO --> Use: start-from:STRUCTURE
                        |
                        +-- YES --> Has visual been added?
                                    |
                                    +-- NO --> Use: start-from:VISUAL
                                    |
                                    +-- YES --> Has it been calendar-slotted?
                                                |
                                                +-- NO --> Use: start-from:CALENDAR
                                                |
                                                +-- YES --> Use: start-from:SCHEDULE
```

---

## Was the pipeline interrupted?

If the post has a `post_id` and a status in `ls_content_queue`:

```
Use: resume:[post_id]
```

The skill reads the status, applies the Status → Stage mapping above, and continues automatically.

---

## Mode Validation Rules

| Mode                 | Pre-flight check required                                               |
|----------------------|-------------------------------------------------------------------------|
| `full`               | INPUT contract fields present (niche, keywords, content_pillars, etc.) |
| `partial`            | Input contract for the first selected stage is satisfied               |
| `start-from:[stage]` | Input contract for the named stage is satisfied                        |
| `resume:[post_id]`   | `post_id` exists in `ls_content_queue` and status is resumable        |

If a pre-flight check fails, the skill reports the missing fields and does not start the pipeline.
