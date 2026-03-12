-- Migration 019: Content Intelligence Pipeline — Schema Alignment
-- Purpose: Align pain_point_research, industry_trends, linkedin_content_ideas,
--          creator_content_analysis, creator_hooks_library, creator_cta_library
--          with actual pipeline script writes. Create ci_pipeline_runs, ci_creators.
-- Pipeline: reddit_scraper.py, synthesizer.py, creator_scraper.py, pipeline.py
-- Created: 2026-02-26

-- ============================================================================
-- 1. pain_point_research — ADD COLUMNS to match reddit_scraper.py INSERT
-- ============================================================================

ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS thread_url TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS thread_title TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS full_post_text TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS top_comments JSONB;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS core_frustration TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS desired_outcome TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS current_attempts TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS language_used TEXT[];
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS emotional_state TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS pain_category TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS content_opportunity TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS urgency_score INTEGER;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS frequency_signal TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS mirror_language TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS upvotes INTEGER;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS week_of DATE;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS run_id TEXT;
ALTER TABLE pain_point_research ADD COLUMN IF NOT EXISTS signal_source TEXT DEFAULT 'reddit_scrape';

-- UNIQUE constraint on thread_url (skip if exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'pain_point_research'::regclass
          AND contype = 'u'
          AND conname = 'pain_point_research_thread_url_key'
    ) THEN
        ALTER TABLE pain_point_research ADD CONSTRAINT pain_point_research_thread_url_key UNIQUE (thread_url);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_pain_points_thread_url ON pain_point_research(thread_url);
CREATE INDEX IF NOT EXISTS idx_pain_points_week_of ON pain_point_research(week_of);
CREATE INDEX IF NOT EXISTS idx_pain_points_run_id ON pain_point_research(run_id);
CREATE INDEX IF NOT EXISTS idx_pain_points_pain_category ON pain_point_research(pain_category);
CREATE INDEX IF NOT EXISTS idx_pain_points_urgency ON pain_point_research(urgency_score DESC);

-- ============================================================================
-- 2. industry_trends — ADD week_of, run_id, UNIQUE(trend_name, week_of)
-- ============================================================================

ALTER TABLE industry_trends ADD COLUMN IF NOT EXISTS week_of DATE;
ALTER TABLE industry_trends ADD COLUMN IF NOT EXISTS run_id TEXT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'industry_trends'::regclass
          AND contype = 'u'
          AND conname = 'industry_trends_trend_name_week_of_key'
    ) THEN
        ALTER TABLE industry_trends ADD CONSTRAINT industry_trends_trend_name_week_of_key UNIQUE (trend_name, week_of);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_trends_week_of ON industry_trends(week_of);
CREATE INDEX IF NOT EXISTS idx_trends_run_id ON industry_trends(run_id);

-- ============================================================================
-- 3. linkedin_content_ideas — ADD COLUMNS to match synthesizer.py INSERT
-- ============================================================================

ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS core_idea TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS angle TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS why_this_will_work TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS emotional_hook TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS hook_text TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS hook_type TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS body_outline TEXT[];
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS post_structure JSONB;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS source_signals JSONB;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(4,2);
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS trend_urgency TEXT;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS niche_relevance NUMERIC(4,2);
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS week_of DATE;
ALTER TABLE linkedin_content_ideas ADD COLUMN IF NOT EXISTS run_id TEXT;

CREATE INDEX IF NOT EXISTS idx_content_ideas_week_of ON linkedin_content_ideas(week_of);
CREATE INDEX IF NOT EXISTS idx_content_ideas_run_id ON linkedin_content_ideas(run_id);
CREATE INDEX IF NOT EXISTS idx_content_ideas_confidence ON linkedin_content_ideas(confidence_score DESC);

-- ============================================================================
-- 4. creator_content_analysis — ADD COLUMNS to match creator_scraper.py INSERT
-- ============================================================================

ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS creator_id BIGINT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS post_full_text TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS post_format TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS images JSONB;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS video_url TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS carousel_slides JSONB;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS likes_count INTEGER;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS comments_count INTEGER;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS shares_count INTEGER;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS impressions_count INTEGER;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS clicks_count INTEGER;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS engagement_rate NUMERIC(10,6);
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS post_idea TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS hook_text TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS hook_analysis TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS cta_text TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS cta_analysis TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS post_structure TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS content_angle TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS emotional_trigger TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS shareability_reason TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS replication_notes TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS week_of DATE;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS run_id TEXT;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS partial BOOLEAN DEFAULT FALSE;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS analysis_failed BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_creator_analysis_creator_id ON creator_content_analysis(creator_id);
CREATE INDEX IF NOT EXISTS idx_creator_analysis_week_of ON creator_content_analysis(week_of);
CREATE INDEX IF NOT EXISTS idx_creator_analysis_run_id ON creator_content_analysis(run_id);
CREATE INDEX IF NOT EXISTS idx_creator_analysis_engagement ON creator_content_analysis(engagement_rate DESC);
CREATE INDEX IF NOT EXISTS idx_creator_analysis_partial ON creator_content_analysis(partial) WHERE partial = TRUE;

-- ============================================================================
-- 5. ci_pipeline_runs — CREATE (pipeline.py orchestration tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_pipeline_runs (
    id TEXT PRIMARY KEY,
    run_date TIMESTAMPTZ,
    week_of DATE,
    status TEXT DEFAULT 'running',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    steps_completed TEXT[],
    reddit_threads_scraped INTEGER DEFAULT 0,
    trends_keywords_scraped INTEGER DEFAULT 0,
    ideas_generated INTEGER DEFAULT 0,
    error_log TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ci_runs_status ON ci_pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_ci_runs_week_of ON ci_pipeline_runs(week_of);
CREATE INDEX IF NOT EXISTS idx_ci_runs_run_date ON ci_pipeline_runs(run_date DESC);

COMMENT ON TABLE ci_pipeline_runs IS 'Content Intelligence pipeline execution tracking';

-- ============================================================================
-- 6. ci_creators — CREATE (creator_scraper.py creator roster)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_creators (
    id BIGSERIAL PRIMARY KEY,
    linkedin_url TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    headline TEXT,
    follower_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMPTZ,
    avg_engagement NUMERIC(10,6),
    total_posts_seen INTEGER DEFAULT 0,
    niche_tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ci_creators_active ON ci_creators(active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_ci_creators_url ON ci_creators(linkedin_url);
CREATE INDEX IF NOT EXISTS idx_ci_creators_last_scraped ON ci_creators(last_scraped DESC);

COMMENT ON TABLE ci_creators IS 'LinkedIn creators tracked by Content Intelligence pipeline';

-- ============================================================================
-- 7. creator_hooks_library — ADD UNIQUE on hook_text
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'creator_hooks_library'::regclass
          AND contype = 'u'
          AND conname = 'creator_hooks_library_hook_text_key'
    ) THEN
        ALTER TABLE creator_hooks_library ADD CONSTRAINT creator_hooks_library_hook_text_key UNIQUE (hook_text);
    END IF;
END $$;

-- ============================================================================
-- 8. creator_cta_library — ADD UNIQUE on cta_text
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'creator_cta_library'::regclass
          AND contype = 'u'
          AND conname = 'creator_cta_library_cta_text_key'
    ) THEN
        ALTER TABLE creator_cta_library ADD CONSTRAINT creator_cta_library_cta_text_key UNIQUE (cta_text);
    END IF;
END $$;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- - pain_point_research: +18 columns (reddit_scraper.py alignment), UNIQUE(thread_url)
-- - industry_trends: +2 columns, UNIQUE(trend_name, week_of)
-- - linkedin_content_ideas: +15 columns (synthesizer.py alignment)
-- - creator_content_analysis: +26 columns (creator_scraper.py alignment)
-- - ci_pipeline_runs: NEW table (pipeline orchestration)
-- - ci_creators: NEW table (creator roster)
-- - creator_hooks_library: UNIQUE(hook_text)
-- - creator_cta_library: UNIQUE(cta_text)
