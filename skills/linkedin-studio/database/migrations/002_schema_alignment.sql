-- =============================================================================
-- Migration: 002_schema_alignment
-- Created: 2026-03-02
-- Plugin: linkedin-studio
-- Depends on: 001_initial
-- Description: Aligns schema with skill specifications.
--   - Renames all 10 tables to ls_ prefix for namespace isolation
--   - Adds missing columns to topic_bank, content_queue, brand_voice_profile
--   - Converts scalar TEXT columns to TEXT[] arrays in topic_bank
--   - Updates foreign keys, indexes, and triggers to match new table names
--
-- Tables renamed:
--   topic_bank           -> ls_topic_bank
--   hook_library         -> ls_hook_library
--   pain_points          -> ls_pain_points
--   trends               -> ls_trends
--   creator_posts_cache  -> ls_creator_posts_cache
--   competitor_tracker   -> ls_competitor_tracker
--   content_queue        -> ls_content_queue
--   ai_phrases_blocklist -> ls_ai_phrases_blocklist
--   post_performance     -> ls_post_performance
--   brand_voice_profile  -> ls_brand_voice_profile
--
-- Rollback: See bottom of file
-- =============================================================================

BEGIN;


-- ---------------------------------------------------------------------------
-- STEP 1: Drop existing triggers (must happen before table renames)
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_topic_bank_updated_at     ON topic_bank;
DROP TRIGGER IF EXISTS trg_content_queue_updated_at   ON content_queue;
DROP TRIGGER IF EXISTS trg_brand_voice_updated_at     ON brand_voice_profile;


-- ---------------------------------------------------------------------------
-- STEP 2: Drop existing indexes (cleaner to recreate with new names)
-- ---------------------------------------------------------------------------

-- topic_bank
DROP INDEX IF EXISTS idx_topic_bank_status;
DROP INDEX IF EXISTS idx_topic_bank_source;
DROP INDEX IF EXISTS idx_topic_bank_trend_score;
DROP INDEX IF EXISTS idx_topic_bank_pillar;

-- pain_points
DROP INDEX IF EXISTS idx_pain_points_subreddit;
DROP INDEX IF EXISTS idx_pain_points_engagement;
DROP INDEX IF EXISTS idx_pain_points_unused;

-- trends
DROP INDEX IF EXISTS idx_trends_expires;
DROP INDEX IF EXISTS idx_trends_keyword;
DROP INDEX IF EXISTS idx_trends_score;

-- content_queue
DROP INDEX IF EXISTS idx_content_queue_status;
DROP INDEX IF EXISTS idx_content_queue_scheduled;
DROP INDEX IF EXISTS idx_content_queue_topic;
DROP INDEX IF EXISTS idx_content_queue_ai_score;

-- post_performance
DROP INDEX IF EXISTS idx_post_performance_posted;
DROP INDEX IF EXISTS idx_post_performance_queue_id;
DROP INDEX IF EXISTS idx_post_performance_pillar;

-- hook_library
DROP INDEX IF EXISTS idx_hook_library_score;
DROP INDEX IF EXISTS idx_hook_library_type;

-- competitor_tracker
DROP INDEX IF EXISTS idx_competitor_last_analyzed;

-- brand_voice_profile
DROP INDEX IF EXISTS idx_brand_voice_active;


-- ---------------------------------------------------------------------------
-- STEP 3: Drop foreign keys before renaming referenced tables
-- ---------------------------------------------------------------------------

-- content_queue.source_topic_id -> topic_bank(id)
ALTER TABLE content_queue DROP CONSTRAINT IF EXISTS content_queue_source_topic_id_fkey;

-- post_performance.content_queue_id -> content_queue(id)
ALTER TABLE post_performance DROP CONSTRAINT IF EXISTS post_performance_content_queue_id_fkey;


-- ---------------------------------------------------------------------------
-- STEP 4: Rename all 10 tables to ls_ prefix
-- ---------------------------------------------------------------------------

ALTER TABLE topic_bank           RENAME TO ls_topic_bank;
ALTER TABLE hook_library         RENAME TO ls_hook_library;
ALTER TABLE pain_points          RENAME TO ls_pain_points;
ALTER TABLE trends               RENAME TO ls_trends;
ALTER TABLE creator_posts_cache  RENAME TO ls_creator_posts_cache;
ALTER TABLE competitor_tracker   RENAME TO ls_competitor_tracker;
ALTER TABLE content_queue        RENAME TO ls_content_queue;
ALTER TABLE ai_phrases_blocklist RENAME TO ls_ai_phrases_blocklist;
ALTER TABLE post_performance     RENAME TO ls_post_performance;
ALTER TABLE brand_voice_profile  RENAME TO ls_brand_voice_profile;


-- ---------------------------------------------------------------------------
-- STEP 5: Restore foreign keys with new table names
-- ---------------------------------------------------------------------------

ALTER TABLE ls_content_queue
    ADD CONSTRAINT ls_content_queue_source_topic_id_fkey
    FOREIGN KEY (source_topic_id) REFERENCES ls_topic_bank(id) ON DELETE SET NULL;

ALTER TABLE ls_post_performance
    ADD CONSTRAINT ls_post_performance_content_queue_id_fkey
    FOREIGN KEY (content_queue_id) REFERENCES ls_content_queue(id) ON DELETE SET NULL;


-- ---------------------------------------------------------------------------
-- STEP 6: topic_bank schema changes — new columns
-- ---------------------------------------------------------------------------

-- 6a. Add raw_topic, populated from existing title column
ALTER TABLE ls_topic_bank ADD COLUMN raw_topic TEXT;
UPDATE ls_topic_bank SET raw_topic = title WHERE raw_topic IS NULL;

-- 6b. Add scoring columns
ALTER TABLE ls_topic_bank ADD COLUMN composite_score    NUMERIC DEFAULT 0;
ALTER TABLE ls_topic_bank ADD COLUMN pain_intensity     NUMERIC DEFAULT 0;
ALTER TABLE ls_topic_bank ADD COLUMN creator_engagement NUMERIC DEFAULT 0;


-- ---------------------------------------------------------------------------
-- STEP 7: topic_bank schema changes — TEXT -> TEXT[] conversions
-- ---------------------------------------------------------------------------

-- 7a. hook_suggestion TEXT -> hook_suggestions TEXT[]
ALTER TABLE ls_topic_bank ADD COLUMN hook_suggestions TEXT[];
UPDATE ls_topic_bank
    SET hook_suggestions = ARRAY[hook_suggestion]
    WHERE hook_suggestion IS NOT NULL;
ALTER TABLE ls_topic_bank DROP COLUMN hook_suggestion;

-- 7b. cta_suggestion TEXT -> cta_suggestions TEXT[]
ALTER TABLE ls_topic_bank ADD COLUMN cta_suggestions TEXT[];
UPDATE ls_topic_bank
    SET cta_suggestions = ARRAY[cta_suggestion]
    WHERE cta_suggestion IS NOT NULL;
ALTER TABLE ls_topic_bank DROP COLUMN cta_suggestion;

-- 7c. post_idea TEXT -> post_ideas TEXT[]
ALTER TABLE ls_topic_bank ADD COLUMN post_ideas TEXT[];
UPDATE ls_topic_bank
    SET post_ideas = ARRAY[post_idea]
    WHERE post_idea IS NOT NULL;
ALTER TABLE ls_topic_bank DROP COLUMN post_idea;

-- 7d. source VARCHAR(50) -> sources TEXT[]
--     Note: dropping the CHECK constraint by dropping the column.
--     The new array column has no CHECK; validation moves to application layer.
ALTER TABLE ls_topic_bank ADD COLUMN sources TEXT[];
UPDATE ls_topic_bank
    SET sources = ARRAY[source::TEXT]
    WHERE source IS NOT NULL;
ALTER TABLE ls_topic_bank DROP COLUMN source;


-- ---------------------------------------------------------------------------
-- STEP 8: content_queue schema changes — new columns
-- ---------------------------------------------------------------------------

ALTER TABLE ls_content_queue ADD COLUMN hook              TEXT;
ALTER TABLE ls_content_queue ADD COLUMN humanized_content TEXT;
ALTER TABLE ls_content_queue ADD COLUMN media_urls        JSONB DEFAULT '[]'::jsonb;
ALTER TABLE ls_content_queue ADD COLUMN quality_score     INTEGER
    CHECK (quality_score BETWEEN 0 AND 100);
ALTER TABLE ls_content_queue ADD COLUMN topic             TEXT;


-- ---------------------------------------------------------------------------
-- STEP 9: brand_voice_profile schema changes
-- ---------------------------------------------------------------------------

-- 9a. Rename persona_description -> persona
ALTER TABLE ls_brand_voice_profile RENAME COLUMN persona_description TO persona;

-- 9b. Add new columns
ALTER TABLE ls_brand_voice_profile ADD COLUMN vocabulary_preferences  TEXT[];
ALTER TABLE ls_brand_voice_profile ADD COLUMN typical_sentence_length INTEGER;
ALTER TABLE ls_brand_voice_profile ADD COLUMN contraction_style       VARCHAR(20) DEFAULT 'high'
    CHECK (contraction_style IN ('high', 'medium', 'low'));


-- ---------------------------------------------------------------------------
-- STEP 10: Recreate indexes on renamed tables
-- ---------------------------------------------------------------------------

-- ls_topic_bank
CREATE INDEX idx_ls_topic_bank_status      ON ls_topic_bank(status);
CREATE INDEX idx_ls_topic_bank_trend_score ON ls_topic_bank(trend_score DESC);
CREATE INDEX idx_ls_topic_bank_pillar      ON ls_topic_bank(content_pillar);

-- ls_pain_points
CREATE INDEX idx_ls_pain_points_subreddit  ON ls_pain_points(subreddit);
CREATE INDEX idx_ls_pain_points_engagement ON ls_pain_points(engagement_score DESC);
CREATE INDEX idx_ls_pain_points_unused     ON ls_pain_points(used_in_post) WHERE used_in_post = FALSE;

-- ls_trends
CREATE INDEX idx_ls_trends_expires         ON ls_trends(expires_at);
CREATE INDEX idx_ls_trends_keyword         ON ls_trends(keyword);
CREATE INDEX idx_ls_trends_score           ON ls_trends(trend_score DESC);

-- ls_content_queue
CREATE INDEX idx_ls_content_queue_status    ON ls_content_queue(status);
CREATE INDEX idx_ls_content_queue_scheduled ON ls_content_queue(scheduled_at);
CREATE INDEX idx_ls_content_queue_topic     ON ls_content_queue(source_topic_id);
CREATE INDEX idx_ls_content_queue_ai_score  ON ls_content_queue(ai_score);

-- ls_post_performance
CREATE INDEX idx_ls_post_performance_posted   ON ls_post_performance(posted_at DESC);
CREATE INDEX idx_ls_post_performance_queue_id ON ls_post_performance(content_queue_id);
CREATE INDEX idx_ls_post_performance_pillar   ON ls_post_performance(content_pillar);

-- ls_hook_library
CREATE INDEX idx_ls_hook_library_score     ON ls_hook_library(performance_score DESC);
CREATE INDEX idx_ls_hook_library_type      ON ls_hook_library(hook_type);

-- ls_competitor_tracker
CREATE INDEX idx_ls_competitor_last_analyzed ON ls_competitor_tracker(last_analyzed DESC);

-- ls_brand_voice_profile
CREATE INDEX idx_ls_brand_voice_active     ON ls_brand_voice_profile(is_active) WHERE is_active = TRUE;


-- ---------------------------------------------------------------------------
-- STEP 11: Recreate triggers on renamed tables
-- ---------------------------------------------------------------------------

CREATE TRIGGER trg_ls_topic_bank_updated_at
    BEFORE UPDATE ON ls_topic_bank
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_ls_content_queue_updated_at
    BEFORE UPDATE ON ls_content_queue
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_ls_brand_voice_updated_at
    BEFORE UPDATE ON ls_brand_voice_profile
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ---------------------------------------------------------------------------
-- STEP 12: Update table and column comments
-- ---------------------------------------------------------------------------

-- topic_bank comments
COMMENT ON TABLE  ls_topic_bank                    IS 'Central repository of content ideas sourced from trends, Reddit, creators, and manual entry';
COMMENT ON COLUMN ls_topic_bank.raw_topic          IS 'Unprocessed topic text; initially populated from the original title column';
COMMENT ON COLUMN ls_topic_bank.composite_score    IS 'Weighted composite of trend_score, pain_intensity, and creator_engagement';
COMMENT ON COLUMN ls_topic_bank.pain_intensity     IS 'How strongly this topic maps to audience pain points (0 = none, higher = stronger)';
COMMENT ON COLUMN ls_topic_bank.creator_engagement IS 'Engagement signal from creator post analysis (0 = none, higher = stronger)';
COMMENT ON COLUMN ls_topic_bank.hook_suggestions   IS 'Array of suggested hooks for this topic (migrated from scalar hook_suggestion)';
COMMENT ON COLUMN ls_topic_bank.cta_suggestions    IS 'Array of suggested CTAs for this topic (migrated from scalar cta_suggestion)';
COMMENT ON COLUMN ls_topic_bank.post_ideas         IS 'Array of post ideas derived from this topic (migrated from scalar post_idea)';
COMMENT ON COLUMN ls_topic_bank.sources            IS 'Array of origin labels: google_trends, reddit, creator, manual (migrated from scalar source)';
COMMENT ON COLUMN ls_topic_bank.trend_score        IS '0-100 relevance score; higher = more timely/trending';
COMMENT ON COLUMN ls_topic_bank.content_pillar     IS 'Which content strategy pillar this topic aligns with';
COMMENT ON COLUMN ls_topic_bank.status             IS 'Lifecycle state: new -> in_progress -> used | archived';

-- content_queue new column comments
COMMENT ON COLUMN ls_content_queue.hook              IS 'The hook line extracted or chosen for this post';
COMMENT ON COLUMN ls_content_queue.humanized_content IS 'Post text after humanizer processing; original kept in post_text';
COMMENT ON COLUMN ls_content_queue.media_urls        IS 'JSON array of media URLs (images, carousels) attached to this post';
COMMENT ON COLUMN ls_content_queue.quality_score     IS '0-100 overall quality score combining ai_score, hook_score, and structure_score';
COMMENT ON COLUMN ls_content_queue.topic             IS 'Human-readable topic label for this post (denormalized from topic_bank)';

-- brand_voice_profile comments
COMMENT ON COLUMN ls_brand_voice_profile.persona                  IS 'Full persona description for content generation (renamed from persona_description)';
COMMENT ON COLUMN ls_brand_voice_profile.vocabulary_preferences   IS 'Array of preferred vocabulary words/phrases that reflect the brand voice';
COMMENT ON COLUMN ls_brand_voice_profile.typical_sentence_length  IS 'Target average sentence length in words; guides rhythm and readability';
COMMENT ON COLUMN ls_brand_voice_profile.contraction_style        IS 'How often to use contractions: high (always), medium (sometimes), low (rarely)';


COMMIT;


-- =============================================================================
-- ROLLBACK SCRIPT
-- Run this manually to reverse migration 002. Restores original table names,
-- columns, and constraints to match the 001_initial schema.
--
-- WARNING: Array-to-scalar conversions take only the FIRST array element.
--          Data in additional array elements will be lost.
--
-- BEGIN;
--
-- -- Drop triggers on ls_ tables
-- DROP TRIGGER IF EXISTS trg_ls_topic_bank_updated_at   ON ls_topic_bank;
-- DROP TRIGGER IF EXISTS trg_ls_content_queue_updated_at ON ls_content_queue;
-- DROP TRIGGER IF EXISTS trg_ls_brand_voice_updated_at  ON ls_brand_voice_profile;
--
-- -- Drop indexes on ls_ tables
-- DROP INDEX IF EXISTS idx_ls_topic_bank_status;
-- DROP INDEX IF EXISTS idx_ls_topic_bank_trend_score;
-- DROP INDEX IF EXISTS idx_ls_topic_bank_pillar;
-- DROP INDEX IF EXISTS idx_ls_pain_points_subreddit;
-- DROP INDEX IF EXISTS idx_ls_pain_points_engagement;
-- DROP INDEX IF EXISTS idx_ls_pain_points_unused;
-- DROP INDEX IF EXISTS idx_ls_trends_expires;
-- DROP INDEX IF EXISTS idx_ls_trends_keyword;
-- DROP INDEX IF EXISTS idx_ls_trends_score;
-- DROP INDEX IF EXISTS idx_ls_content_queue_status;
-- DROP INDEX IF EXISTS idx_ls_content_queue_scheduled;
-- DROP INDEX IF EXISTS idx_ls_content_queue_topic;
-- DROP INDEX IF EXISTS idx_ls_content_queue_ai_score;
-- DROP INDEX IF EXISTS idx_ls_post_performance_posted;
-- DROP INDEX IF EXISTS idx_ls_post_performance_queue_id;
-- DROP INDEX IF EXISTS idx_ls_post_performance_pillar;
-- DROP INDEX IF EXISTS idx_ls_hook_library_score;
-- DROP INDEX IF EXISTS idx_ls_hook_library_type;
-- DROP INDEX IF EXISTS idx_ls_competitor_last_analyzed;
-- DROP INDEX IF EXISTS idx_ls_brand_voice_active;
--
-- -- Drop foreign keys
-- ALTER TABLE ls_content_queue    DROP CONSTRAINT IF EXISTS ls_content_queue_source_topic_id_fkey;
-- ALTER TABLE ls_post_performance DROP CONSTRAINT IF EXISTS ls_post_performance_content_queue_id_fkey;
--
-- -- Reverse brand_voice_profile changes
-- ALTER TABLE ls_brand_voice_profile DROP COLUMN IF EXISTS contraction_style;
-- ALTER TABLE ls_brand_voice_profile DROP COLUMN IF EXISTS typical_sentence_length;
-- ALTER TABLE ls_brand_voice_profile DROP COLUMN IF EXISTS vocabulary_preferences;
-- ALTER TABLE ls_brand_voice_profile RENAME COLUMN persona TO persona_description;
--
-- -- Reverse content_queue changes
-- ALTER TABLE ls_content_queue DROP COLUMN IF EXISTS topic;
-- ALTER TABLE ls_content_queue DROP COLUMN IF EXISTS quality_score;
-- ALTER TABLE ls_content_queue DROP COLUMN IF EXISTS media_urls;
-- ALTER TABLE ls_content_queue DROP COLUMN IF EXISTS humanized_content;
-- ALTER TABLE ls_content_queue DROP COLUMN IF EXISTS hook;
--
-- -- Reverse topic_bank TEXT[] -> TEXT (take first element)
-- ALTER TABLE ls_topic_bank ADD COLUMN source VARCHAR(50);
-- UPDATE ls_topic_bank SET source = sources[1];
-- ALTER TABLE ls_topic_bank ALTER COLUMN source SET NOT NULL;
-- ALTER TABLE ls_topic_bank ADD CONSTRAINT chk_topic_bank_source
--     CHECK (source IN ('google_trends', 'reddit', 'creator', 'manual'));
-- ALTER TABLE ls_topic_bank DROP COLUMN sources;
--
-- ALTER TABLE ls_topic_bank ADD COLUMN post_idea TEXT;
-- UPDATE ls_topic_bank SET post_idea = post_ideas[1];
-- ALTER TABLE ls_topic_bank DROP COLUMN post_ideas;
--
-- ALTER TABLE ls_topic_bank ADD COLUMN cta_suggestion TEXT;
-- UPDATE ls_topic_bank SET cta_suggestion = cta_suggestions[1];
-- ALTER TABLE ls_topic_bank DROP COLUMN cta_suggestions;
--
-- ALTER TABLE ls_topic_bank ADD COLUMN hook_suggestion TEXT;
-- UPDATE ls_topic_bank SET hook_suggestion = hook_suggestions[1];
-- ALTER TABLE ls_topic_bank DROP COLUMN hook_suggestions;
--
-- -- Drop new topic_bank columns
-- ALTER TABLE ls_topic_bank DROP COLUMN IF EXISTS creator_engagement;
-- ALTER TABLE ls_topic_bank DROP COLUMN IF EXISTS pain_intensity;
-- ALTER TABLE ls_topic_bank DROP COLUMN IF EXISTS composite_score;
-- ALTER TABLE ls_topic_bank DROP COLUMN IF EXISTS raw_topic;
--
-- -- Rename tables back to original names
-- ALTER TABLE ls_topic_bank           RENAME TO topic_bank;
-- ALTER TABLE ls_hook_library         RENAME TO hook_library;
-- ALTER TABLE ls_pain_points          RENAME TO pain_points;
-- ALTER TABLE ls_trends               RENAME TO trends;
-- ALTER TABLE ls_creator_posts_cache  RENAME TO creator_posts_cache;
-- ALTER TABLE ls_competitor_tracker   RENAME TO competitor_tracker;
-- ALTER TABLE ls_content_queue        RENAME TO content_queue;
-- ALTER TABLE ls_ai_phrases_blocklist RENAME TO ai_phrases_blocklist;
-- ALTER TABLE ls_post_performance     RENAME TO post_performance;
-- ALTER TABLE ls_brand_voice_profile  RENAME TO brand_voice_profile;
--
-- -- Restore foreign keys with original names
-- ALTER TABLE content_queue
--     ADD CONSTRAINT content_queue_source_topic_id_fkey
--     FOREIGN KEY (source_topic_id) REFERENCES topic_bank(id) ON DELETE SET NULL;
-- ALTER TABLE post_performance
--     ADD CONSTRAINT post_performance_content_queue_id_fkey
--     FOREIGN KEY (content_queue_id) REFERENCES content_queue(id) ON DELETE SET NULL;
--
-- -- Restore original indexes
-- CREATE INDEX idx_topic_bank_status      ON topic_bank(status);
-- CREATE INDEX idx_topic_bank_source      ON topic_bank(source);
-- CREATE INDEX idx_topic_bank_trend_score ON topic_bank(trend_score DESC);
-- CREATE INDEX idx_topic_bank_pillar      ON topic_bank(content_pillar);
-- CREATE INDEX idx_pain_points_subreddit  ON pain_points(subreddit);
-- CREATE INDEX idx_pain_points_engagement ON pain_points(engagement_score DESC);
-- CREATE INDEX idx_pain_points_unused     ON pain_points(used_in_post) WHERE used_in_post = FALSE;
-- CREATE INDEX idx_trends_expires         ON trends(expires_at);
-- CREATE INDEX idx_trends_keyword         ON trends(keyword);
-- CREATE INDEX idx_trends_score           ON trends(trend_score DESC);
-- CREATE INDEX idx_content_queue_status    ON content_queue(status);
-- CREATE INDEX idx_content_queue_scheduled ON content_queue(scheduled_at);
-- CREATE INDEX idx_content_queue_topic     ON content_queue(source_topic_id);
-- CREATE INDEX idx_content_queue_ai_score  ON content_queue(ai_score);
-- CREATE INDEX idx_post_performance_posted   ON post_performance(posted_at DESC);
-- CREATE INDEX idx_post_performance_queue_id ON post_performance(content_queue_id);
-- CREATE INDEX idx_post_performance_pillar   ON post_performance(content_pillar);
-- CREATE INDEX idx_hook_library_score      ON hook_library(performance_score DESC);
-- CREATE INDEX idx_hook_library_type       ON hook_library(hook_type);
-- CREATE INDEX idx_competitor_last_analyzed ON competitor_tracker(last_analyzed DESC);
-- CREATE INDEX idx_brand_voice_active      ON brand_voice_profile(is_active) WHERE is_active = TRUE;
--
-- -- Restore original triggers
-- CREATE TRIGGER trg_topic_bank_updated_at
--     BEFORE UPDATE ON topic_bank
--     FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- CREATE TRIGGER trg_content_queue_updated_at
--     BEFORE UPDATE ON content_queue
--     FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- CREATE TRIGGER trg_brand_voice_updated_at
--     BEFORE UPDATE ON brand_voice_profile
--     FOR EACH ROW EXECUTE FUNCTION set_updated_at();
--
-- COMMIT;
-- =============================================================================
