# NEON-SCHEMA.md — Content Writer Database Reference

All tables use `ls_` prefix. Access via `source database/neon-utils.sh`.

---

## Tables Used by content-writer

### ls_topic_bank
Source of truth for approved topics. Read-only from content-writer.

| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key |
| raw_topic | text | Original topic as submitted |
| hook_suggestions | jsonb | Array of pre-generated hook options |
| cta_suggestions | jsonb | Array of pre-generated CTA options |
| post_ideas | jsonb | Angle and framing ideas for the topic |
| composite_score | float | Relevance/resonance score (0.0–10.0) |
| sources | jsonb | Supporting links and references |
| pain_intensity | int | Audience pain level 1–10 |
| content_pillar | text | Primary content pillar this topic belongs to |

---

### ls_brand_voice_profile
Single active row per account. Load once at session start.

| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key |
| persona | text | Core persona identity label |
| writing_tone | text | e.g., "direct", "conversational", "authoritative" |
| vocabulary_preferences | jsonb | Words/phrases to prefer |
| avoid_words | jsonb | Words/phrases to never use |
| signature_phrases | jsonb | Phrases to work in naturally |
| typical_sentence_length | int | Target avg words per sentence |
| content_pillars | jsonb | Array of primary topic domains |
| contraction_style | text | "always", "sometimes", "never" |
| is_active | boolean | Only one row should be true |

---

### ls_content_queue
Write destination for all drafts produced by content-writer.

| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key (auto-generated) |
| post_text | text | Full post body |
| hook | text | Extracted hook line |
| topic | text | Topic label |
| post_type | text | text_post / carousel_script / poll_post / document_post |
| content_pillar | text | Assigned content pillar |
| status | text | Always 'draft' on insert |
| source_topic_id | uuid | FK → ls_topic_bank.id (nullable) |
| created_at | timestamptz | Auto-set |
| word_count | int | Calculated before insert |

---

## Example Queries

### Load topic by ID
```bash
source database/neon-utils.sh

neon_query "
  SELECT id, raw_topic, hook_suggestions, cta_suggestions,
         post_ideas, composite_score, pain_intensity, content_pillar
  FROM ls_topic_bank
  WHERE id = '$TOPIC_ID'
  LIMIT 1;
"
```

### Load active brand voice
```bash
source database/neon-utils.sh

neon_query "
  SELECT persona, writing_tone, vocabulary_preferences,
         avoid_words, signature_phrases, typical_sentence_length,
         content_pillars, contraction_style
  FROM ls_brand_voice_profile
  WHERE is_active = true
  LIMIT 1;
"
```

### Insert new draft
```bash
source database/neon-utils.sh

neon_query "
  INSERT INTO ls_content_queue
    (post_text, hook, topic, post_type, content_pillar,
     status, source_topic_id, word_count)
  VALUES
    ('$POST_TEXT', '$HOOK', '$TOPIC', '$POST_TYPE',
     '$CONTENT_PILLAR', 'draft', '$SOURCE_TOPIC_ID', $WORD_COUNT)
  RETURNING id;
"
```

---

## Notes

- Always check `ls_brand_voice_profile.is_active = true` — never load an inactive profile
- `hook_suggestions` and `cta_suggestions` are JSONB arrays; parse with `jq` after query
- `source_topic_id` is nullable — set to NULL if writing from free-form input, not from topic bank
- Word count must be calculated before insert — do not rely on DB triggers
