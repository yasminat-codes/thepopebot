# NEON-SCHEMA.md — LinkedIn Studio Shared Database Schema

## Connection Instructions

```bash
source database/neon-utils.sh

# Read query
neon_query "SELECT * FROM ls_topic_bank WHERE status = 'new' LIMIT 10;"

# Write query
neon_exec "UPDATE ls_topic_bank SET status = 'in_progress' WHERE id = '...'"
```

All tables use the `ls_` prefix. The Neon connection string is sourced from the environment variable
`NEON_DATABASE_URL` via `database/neon-utils.sh`.

---

## Table: ls_topic_bank

Stores research topics with scoring data, content suggestions, and lifecycle status.

### Full DDL (after migration 002)

```sql
CREATE TABLE IF NOT EXISTS ls_topic_bank (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               TEXT NOT NULL,
    raw_topic           TEXT NOT NULL,
    hook_suggestions    TEXT[],
    cta_suggestions     TEXT[],
    post_ideas          TEXT[],
    sources             TEXT[],
    niche               VARCHAR(100),
    trend_score         INTEGER CHECK (trend_score >= 0 AND trend_score <= 100),
    composite_score     NUMERIC(5, 2),
    pain_intensity      NUMERIC(5, 2),
    creator_engagement  NUMERIC(5, 2),
    content_pillar      VARCHAR(50) CHECK (content_pillar IN (
                            'thought_leadership', 'education', 'social_proof', 'cta'
                        )),
    status              VARCHAR(20) DEFAULT 'new' CHECK (status IN (
                            'new', 'in_progress', 'used', 'archived'
                        )),
    tags                TEXT[],
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
```

### Column Reference

| Column              | Type            | Notes                                              |
|---------------------|-----------------|----------------------------------------------------|
| id                  | UUID            | Primary key, auto-generated                        |
| title               | TEXT            | Short human-readable title                         |
| raw_topic           | TEXT            | Original topic string from research source         |
| hook_suggestions    | TEXT[]          | Array of generated hook options                    |
| cta_suggestions     | TEXT[]          | Array of generated CTA options                     |
| post_ideas          | TEXT[]          | Array of post angle ideas                          |
| sources             | TEXT[]          | Which sources found this topic (linkedin/google/reddit) |
| niche               | VARCHAR(100)    | Industry/niche tag                                 |
| trend_score         | INTEGER 0-100   | Google Trends normalized score                     |
| composite_score     | NUMERIC         | Weighted aggregate score (see SCORING-MODEL.md)    |
| pain_intensity      | NUMERIC         | Reddit/LinkedIn pain signal score 0-100            |
| creator_engagement  | NUMERIC         | LinkedIn engagement signal score 0-100             |
| content_pillar      | VARCHAR(50)     | thought_leadership / education / social_proof / cta |
| status              | VARCHAR(20)     | new / in_progress / used / archived                |
| tags                | TEXT[]          | Free-form tags for filtering                       |
| created_at          | TIMESTAMPTZ     | Auto-set on insert                                 |
| updated_at          | TIMESTAMPTZ     | Must be updated manually on each write             |

---

## Table: ls_brand_voice_profile

Stores the creator's brand voice configuration. Only one row should have `is_active = true` at a time.

### Full DDL

```sql
CREATE TABLE IF NOT EXISTS ls_brand_voice_profile (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_name            VARCHAR(100) NOT NULL,
    persona                 TEXT,
    writing_tone            VARCHAR(100),
    niche                   TEXT,
    target_audience         TEXT,
    signature_phrases       TEXT[],
    avoid_words             TEXT[],
    preferred_hook_types    TEXT[],
    avg_post_length         INTEGER,
    vocabulary_preferences  TEXT[],
    typical_sentence_length INTEGER,
    contraction_style       VARCHAR(20),
    content_pillars         JSONB,
    posting_schedule        JSONB,
    is_active               BOOLEAN DEFAULT false,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);
```

### Column Reference

| Column                  | Type         | Notes                                                |
|-------------------------|--------------|------------------------------------------------------|
| id                      | UUID         | Primary key                                          |
| profile_name            | VARCHAR(100) | Friendly name (e.g., "Yasmine - Growth Consultant")  |
| persona                 | TEXT         | Full persona description in plain English            |
| writing_tone            | VARCHAR(100) | e.g., "conversational", "authoritative", "punchy"    |
| niche                   | TEXT         | Creator's primary niche/industry                     |
| target_audience         | TEXT         | Who they write for                                   |
| signature_phrases       | TEXT[]       | Phrases to sprinkle in (brand fingerprint)           |
| avoid_words             | TEXT[]       | Words/phrases to never use                           |
| preferred_hook_types    | TEXT[]       | e.g., ["bold_claim", "question", "story"]            |
| avg_post_length         | INTEGER      | Target word count                                    |
| vocabulary_preferences  | TEXT[]       | Power words and preferred vocabulary                 |
| typical_sentence_length | INTEGER      | Average words per sentence                           |
| contraction_style       | VARCHAR(20)  | "always", "never", "sometimes"                       |
| content_pillars         | JSONB        | Pillar weights and descriptions                      |
| posting_schedule        | JSONB        | Days, times, frequency config                        |
| is_active               | BOOLEAN      | Only one active profile at a time                    |
| created_at              | TIMESTAMPTZ  | Auto-set on insert                                   |
| updated_at              | TIMESTAMPTZ  | Must be updated manually on each write               |

---

## Table: ls_content_queue

Stores generated posts through the full content lifecycle from draft to published.

### Full DDL

```sql
CREATE TABLE IF NOT EXISTS ls_content_queue (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_text           TEXT,
    post_type           VARCHAR(30),
    content_pillar      VARCHAR(50),
    visual_prompt_json  JSONB,
    canva_design_id     TEXT,
    canva_design_url    TEXT,
    ai_score            INTEGER,
    hook_score          INTEGER,
    structure_score     INTEGER,
    humanizer_passes    INTEGER DEFAULT 0,
    status              VARCHAR(30) DEFAULT 'draft' CHECK (status IN (
                            'draft', 'humanized', 'reviewed', 'visual_added',
                            'approved', 'scheduled', 'published', 'failed'
                        )),
    scheduled_at        TIMESTAMPTZ,
    published_at        TIMESTAMPTZ,
    metricool_id        TEXT,
    source_topic_id     UUID REFERENCES ls_topic_bank(id) ON DELETE SET NULL,
    hashtags            TEXT[],
    hook                TEXT,
    humanized_content   TEXT,
    media_urls          JSONB,
    quality_score       INTEGER,
    topic               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
```

### Column Reference

| Column             | Type         | Notes                                                    |
|--------------------|--------------|----------------------------------------------------------|
| id                 | UUID         | Primary key                                              |
| post_text          | TEXT         | Raw AI-generated post text                               |
| post_type          | VARCHAR(30)  | e.g., "text_only", "carousel", "document", "video"       |
| content_pillar     | VARCHAR(50)  | Inherited from source topic                              |
| visual_prompt_json | JSONB        | Canva or image generation prompt payload                 |
| canva_design_id    | TEXT         | Canva design ID after visual creation                    |
| canva_design_url   | TEXT         | Shareable Canva URL                                      |
| ai_score           | INTEGER      | Overall AI quality score 0-100                           |
| hook_score         | INTEGER      | Hook quality score 0-100                                 |
| structure_score    | INTEGER      | Post structure quality score 0-100                       |
| humanizer_passes   | INTEGER      | How many times humanizer has run on this post            |
| status             | VARCHAR(30)  | Lifecycle stage (see status flow below)                  |
| scheduled_at       | TIMESTAMPTZ  | When it is scheduled to publish                          |
| published_at       | TIMESTAMPTZ  | When it actually published (set by Metricool callback)   |
| metricool_id       | TEXT         | Metricool post ID after scheduling                       |
| source_topic_id    | UUID FK      | Links back to ls_topic_bank                              |
| hashtags           | TEXT[]       | Final hashtag set                                        |
| hook               | TEXT         | Final chosen hook line                                   |
| humanized_content  | TEXT         | Post text after humanizer passes                         |
| media_urls         | JSONB        | URLs of attached images/videos                           |
| quality_score      | INTEGER      | Final human-reviewed quality score                       |
| topic              | TEXT         | Topic title (denormalized for quick display)             |
| created_at         | TIMESTAMPTZ  | Auto-set on insert                                       |
| updated_at         | TIMESTAMPTZ  | Must be updated manually on each write                   |

### Status Flow

```
draft → humanized → reviewed → visual_added → approved → scheduled → published
                                                                    ↘ failed
```

---

## Example Queries

### Select new topics ordered by composite score

```bash
source database/neon-utils.sh

neon_query "
    SELECT id, title, composite_score, content_pillar, sources
    FROM ls_topic_bank
    WHERE status = 'new'
    ORDER BY composite_score DESC
    LIMIT 20;
"
```

### Insert a new topic

```bash
source database/neon-utils.sh

neon_exec "
    INSERT INTO ls_topic_bank (
        title, raw_topic, niche, trend_score, pain_intensity,
        creator_engagement, composite_score, sources, content_pillar, status
    ) VALUES (
        'AI replacing junior devs by 2027',
        'ai replacing developers jobs automation',
        'technology',
        82,
        75.0,
        68.0,
        75.95,
        ARRAY['google_trends', 'reddit'],
        'thought_leadership',
        'new'
    );
"
```

### Update topic status

```bash
source database/neon-utils.sh

neon_exec "
    UPDATE ls_topic_bank
    SET status = 'in_progress', updated_at = NOW()
    WHERE id = '<uuid-here>';
"
```

### Get active brand voice profile

```bash
source database/neon-utils.sh

neon_query "
    SELECT *
    FROM ls_brand_voice_profile
    WHERE is_active = true
    LIMIT 1;
"
```

### Get content queue items ready for scheduling

```bash
source database/neon-utils.sh

neon_query "
    SELECT id, topic, hook, status, quality_score, scheduled_at
    FROM ls_content_queue
    WHERE status = 'approved'
    ORDER BY created_at ASC;
"
```
