---
name: ls:idea-bank
description: PROACTIVELY browses, filters, and curates your Neon topic_bank — sorting ideas by trend score, filtering by content pillar, promoting ideas to content_queue, and managing your brand_voice_profile (persona, tone, vocabulary, avoid-words) so every post stays on-brand before writing begins.
model: sonnet
context: agent
allowed-tools: Read Write Bash Grep Glob
metadata:
  version: "2.0.0"
---

# ls:idea-bank

Browse and manage your content idea library and brand voice settings. Two modes: **BROWSE** (explore and act on ideas) and **BRAND VOICE** (update persona and vocabulary).

---

## Neon Tables Used

| Table | Purpose |
|-------|---------|
| `topic_bank` | All content ideas, trend scores, pillar tags |
| `brand_voice_profile` | Persona, tone, vocabulary, avoid-words |
| `content_queue` | Target for promoted ideas |

---

## Pipeline

### Phase 1 — Mode Selection

Present two modes:

```
What would you like to do?

  [1] BROWSE IDEAS      — explore, tag, archive, promote ideas
  [2] BRAND VOICE       — view/update persona and vocabulary
```

---

## Mode 1: BROWSE IDEAS

### Step 1.1 — Load topic_bank

```sql
SELECT
  id, topic, hook_angle, content_pillar, source,
  trend_score, status, tags, created_at
FROM topic_bank
WHERE status != 'archived'
ORDER BY trend_score DESC;
```

### Step 1.2 — Filter Options

Offer filter controls:

```
FILTERS (press Enter to skip any)
──────────────────────────────────
Content Pillar:  [all | TL | EDU | SP | CTA]
Source:          [all | manual | research-engine | pain-point-miner | competitor-tracker]
Status:          [all | new | tagged | queued | used]
Min trend score: [0–100, default: 0]
Tag:             [free text]
```

Apply filters in SQL WHERE clause.

### Step 1.3 — Display Ideas

Show as numbered list:

```
IDEAS (sorted by trend score)
──────────────────────────────────────────────────────────────
#  Score  Pillar  Topic / Hook Angle                    Status  Source
──────────────────────────────────────────────────────────────
1   94     TL     "Why most AI consulting projects fail  new     research
                   in week 1 (and how to fix it)"
2   87     EDU    "The 5-step AI readiness audit I run   tagged  manual
                   before every engagement"
3   81     SP     "We saved a client 40h/week — here's   new     pain-point
                   the exact workflow"
...
──────────────────────────────────────────────────────────────
Showing 12 of 34 ideas (status: all, pillar: all)
```

### Step 1.4 — Actions on Ideas

After displaying list, offer actions:

| Action | Command | Description |
|--------|---------|-------------|
| Tag | `tag [id] [tag]` | Add tag to idea |
| Archive | `archive [id]` | Set status = 'archived' |
| Promote | `promote [id]` | Move to content_queue |
| Add new | `add` | Add a custom idea |
| View detail | `view [id]` | Show full idea record |
| Score refresh | `score [id]` | Re-evaluate trend score |

**Tag an idea:**
```sql
UPDATE topic_bank
SET tags = array_append(tags, '[tag]'), updated_at = NOW()
WHERE id = '[id]';
```

**Archive an idea:**
```sql
UPDATE topic_bank
SET status = 'archived', updated_at = NOW()
WHERE id = '[id]';
```

**Promote to content_queue:**
```sql
INSERT INTO content_queue (topic, hook, content_pillar, source_idea_id, status, created_at)
VALUES ('[topic]', '[hook_angle]', '[pillar]', '[idea_id]', 'draft', NOW());

UPDATE topic_bank
SET status = 'queued', updated_at = NOW()
WHERE id = '[idea_id]';
```

Confirm: "Idea promoted to content_queue. Run ls:content-writer to draft this post?"

**Add custom idea:**
```sql
INSERT INTO topic_bank (topic, hook_angle, content_pillar, source, trend_score, status, created_at)
VALUES ('[user input]', '[user input]', '[pillar]', 'manual', 50, 'new', NOW());
```

### Step 1.5 — Trend Score Rubric

Score range 0–100. Factors:

| Factor | Weight | Signal |
|--------|--------|--------|
| Recency | 30% | Topic appeared in last 30 days |
| Engagement potential | 25% | Emotional hook strength |
| Pillar gap | 20% | Needed for pillar balance |
| Audience fit | 15% | Relevance to AI consulting niche |
| Originality | 10% | Novel angle vs. common takes |

→ Scoring detail: `references/TREND-SCORING.md`

---

## Mode 2: BRAND VOICE

### Step 2.1 — Load brand_voice_profile

```sql
SELECT * FROM brand_voice_profile LIMIT 1;
```

Display current profile:

```
BRAND VOICE PROFILE
──────────────────────────────────────────────────────────────
Persona:      [value]
Tone:         [value]
Writing style:[value]

Vocabulary (always use):
  [word1], [word2], [word3] ...

Avoid words:
  [word1], [word2], [word3] ...

POV:          [first person / third person]
Emoji use:    [never / sparingly / frequent]
──────────────────────────────────────────────────────────────
```

### Step 2.2 — Update Options

Offer update actions:

| Action | Field |
|--------|-------|
| Update persona | `persona` text field |
| Update tone | `tone` text field |
| Update writing style | `writing_style` text field |
| Add vocabulary word | Append to `vocabulary` array |
| Remove vocabulary word | Remove from `vocabulary` array |
| Add avoid-word | Append to `avoid_words` array |
| Remove avoid-word | Remove from `avoid_words` array |
| Set POV | `pov` field |
| Set emoji policy | `emoji_use` field |

**Add vocabulary word:**
```sql
UPDATE brand_voice_profile
SET vocabulary = array_append(vocabulary, '[word]'), updated_at = NOW();
```

**Remove vocabulary word:**
```sql
UPDATE brand_voice_profile
SET vocabulary = array_remove(vocabulary, '[word]'), updated_at = NOW();
```

Same pattern for `avoid_words`.

**Update text fields:**
```sql
UPDATE brand_voice_profile
SET [field] = '[value]', updated_at = NOW();
```

Confirm all changes. Show updated profile after save.

---

## Error Handling

| Condition | Action |
|-----------|--------|
| topic_bank empty | Show empty state, offer to run ls:research-engine |
| brand_voice_profile missing | Offer to create default profile |
| Promote fails (content_queue insert error) | Show SQL error, do not archive source idea |
| Neon unavailable | Show connection error, all writes blocked |

---

## References

- `references/TREND-SCORING.md` — Trend score calculation rubric
- `references/BRAND-VOICE-SCHEMA.md` — Full brand_voice_profile table schema
