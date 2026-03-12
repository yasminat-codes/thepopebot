-- Migration 017: Suwaida Enhanced LinkedIn Content Tables
-- Domain: Creator scraping workflow, Metricool batching, strategy sessions, de-ai-fy tracking
-- Agent: Suwaida (@SuwaidaLinkedInBot)
-- Created: 2025-01-27

-- ============================================================================
-- NEW TABLES
-- ============================================================================

-- 1. Creator Research Sessions
CREATE TABLE IF NOT EXISTS creator_research_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_date DATE NOT NULL,
    session_type TEXT CHECK (session_type IN ('bi_weekly_scraping', 'competitive_analysis', 'trend_research', 'ad_hoc')),
    creators_analyzed TEXT[] NOT NULL,
    total_posts_reviewed INTEGER,
    key_insights TEXT NOT NULL,
    hooks_extracted INTEGER DEFAULT 0,
    ctas_extracted INTEGER DEFAULT 0,
    patterns_identified TEXT[],
    action_items TEXT[],
    google_doc_url TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'applied')),
    completed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_creator_sessions_date ON creator_research_sessions(session_date DESC);
CREATE INDEX idx_creator_sessions_status ON creator_research_sessions(status, session_date DESC);

COMMENT ON TABLE creator_research_sessions IS 'Bi-weekly creator scraping and analysis sessions';

-- 2. Creator Hooks Library
CREATE TABLE IF NOT EXISTS creator_hooks_library (
    id BIGSERIAL PRIMARY KEY,
    research_session_id BIGINT REFERENCES creator_research_sessions(id),
    creator_name TEXT NOT NULL,
    creator_profile_url TEXT,
    original_post_url TEXT,
    hook_text TEXT NOT NULL,
    hook_category TEXT CHECK (hook_category IN ('question', 'bold_statement', 'statistic', 'story_opener', 'contrarian', 'pattern_interrupt', 'curiosity_gap', 'personal_experience', 'industry_insight')),
    hook_pattern TEXT,
    engagement_estimate TEXT,
    why_it_works TEXT NOT NULL,
    adaptation_for_yasmine TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'testing', 'retired')),
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_hooks_category ON creator_hooks_library(hook_category, status);
CREATE INDEX idx_hooks_effectiveness ON creator_hooks_library(effectiveness_rating DESC, usage_count DESC) WHERE status = 'active';
CREATE INDEX idx_hooks_session ON creator_hooks_library(research_session_id);

COMMENT ON TABLE creator_hooks_library IS 'Extracted hooks from successful creator posts';

-- 3. Creator CTA Library
CREATE TABLE IF NOT EXISTS creator_cta_library (
    id BIGSERIAL PRIMARY KEY,
    research_session_id BIGINT REFERENCES creator_research_sessions(id),
    creator_name TEXT NOT NULL,
    creator_profile_url TEXT,
    original_post_url TEXT,
    cta_text TEXT NOT NULL,
    cta_type TEXT CHECK (cta_type IN ('discovery_call', 'website_visit', 'dm', 'comment_engagement', 'share', 'follow', 'download', 'tag_someone', 'newsletter_signup')),
    context_where_used TEXT NOT NULL,
    conversion_estimate TEXT,
    why_it_works TEXT NOT NULL,
    adaptation_for_yasmine TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'testing', 'retired')),
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_ctas_type ON creator_cta_library(cta_type, status);
CREATE INDEX idx_ctas_effectiveness ON creator_cta_library(effectiveness_rating DESC, usage_count DESC) WHERE status = 'active';
CREATE INDEX idx_ctas_session ON creator_cta_library(research_session_id);

COMMENT ON TABLE creator_cta_library IS 'Extracted CTAs from successful creator posts';

-- 4. Metricool Batches
CREATE TABLE IF NOT EXISTS metricool_batches (
    id BIGSERIAL PRIMARY KEY,
    batch_month TEXT NOT NULL,
    batch_year INTEGER NOT NULL,
    batch_name TEXT NOT NULL,
    total_posts_planned INTEGER NOT NULL,
    posts_drafted INTEGER DEFAULT 0,
    posts_deaified INTEGER DEFAULT 0,
    posts_approved INTEGER DEFAULT 0,
    posts_loaded_to_metricool INTEGER DEFAULT 0,
    batch_status TEXT NOT NULL DEFAULT 'planning' CHECK (batch_status IN ('planning', 'drafting', 'deaify_pass', 'yasmine_review', 'loaded', 'scheduled', 'published')),
    batch_strategy TEXT,
    content_pillars_mix JSONB,
    format_mix JSONB,
    optimal_times_set BOOLEAN DEFAULT FALSE,
    yasmine_approved BOOLEAN DEFAULT FALSE,
    google_doc_url TEXT,
    metricool_calendar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    loaded_at TIMESTAMPTZ,
    notes TEXT,
    UNIQUE(batch_year, batch_month)
);

CREATE INDEX idx_metricool_batches_date ON metricool_batches(batch_year DESC, batch_month DESC);
CREATE INDEX idx_metricool_batches_status ON metricool_batches(batch_status, created_at DESC);

COMMENT ON TABLE metricool_batches IS 'Monthly content batching for Metricool scheduling';

-- 5. Content Strategy Sessions
CREATE TABLE IF NOT EXISTS content_strategy_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_date DATE NOT NULL,
    session_type TEXT CHECK (session_type IN ('monthly_review', 'quarterly_planning', 'performance_analysis', 'strategy_pivot', 'goal_setting')),
    period_covered TEXT NOT NULL,
    key_metrics_reviewed JSONB,
    performance_summary TEXT NOT NULL,
    what_worked TEXT NOT NULL,
    what_didnt TEXT,
    patterns_identified TEXT[],
    strategy_adjustments TEXT[],
    goals_for_next_period TEXT[],
    action_items TEXT[],
    google_doc_url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'applied')),
    completed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_strategy_sessions_date ON content_strategy_sessions(session_date DESC);
CREATE INDEX idx_strategy_sessions_type ON content_strategy_sessions(session_type, session_date DESC);

COMMENT ON TABLE content_strategy_sessions IS 'Monthly/quarterly content strategy reviews';

-- 6. Content Campaigns
CREATE TABLE IF NOT EXISTS content_campaigns (
    id BIGSERIAL PRIMARY KEY,
    campaign_name TEXT NOT NULL UNIQUE,
    campaign_theme TEXT NOT NULL,
    campaign_goal TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    target_posts_count INTEGER,
    actual_posts_count INTEGER DEFAULT 0,
    content_pillars TEXT[],
    hashtags TEXT[],
    target_cta TEXT,
    campaign_status TEXT NOT NULL DEFAULT 'planning' CHECK (campaign_status IN ('planning', 'active', 'completed', 'paused', 'cancelled')),
    total_impressions INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    avg_engagement_rate NUMERIC(5, 2),
    warm_leads_generated INTEGER DEFAULT 0,
    google_doc_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_content_campaigns_status ON content_campaigns(campaign_status, start_date DESC);
CREATE INDEX idx_content_campaigns_dates ON content_campaigns(start_date DESC, end_date DESC);

COMMENT ON TABLE content_campaigns IS 'Themed content series and campaigns';

-- 7. Deaiify Runs
CREATE TABLE IF NOT EXISTS deaiify_runs (
    id BIGSERIAL PRIMARY KEY,
    linkedin_post_id BIGINT REFERENCES linkedin_posts(id),
    run_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version TEXT,
    layer1_generic_openers BOOLEAN DEFAULT FALSE,
    layer2_corporate_jargon BOOLEAN DEFAULT FALSE,
    layer3_list_fatigue BOOLEAN DEFAULT FALSE,
    layer4_empty_emphasis BOOLEAN DEFAULT FALSE,
    layer5_ai_tells BOOLEAN DEFAULT FALSE,
    layer6_filler_phrases BOOLEAN DEFAULT FALSE,
    layer7_banned_words BOOLEAN DEFAULT FALSE,
    zero_point_protocol BOOLEAN DEFAULT FALSE,
    issues_found TEXT[],
    fixes_applied TEXT[],
    before_text TEXT,
    after_text TEXT,
    pass_status TEXT NOT NULL CHECK (pass_status IN ('passed', 'failed', 'needs_revision')),
    revision_notes TEXT,
    run_by TEXT DEFAULT 'suwaida'
);

CREATE INDEX idx_deaiify_post ON deaiify_runs(linkedin_post_id, run_date DESC);
CREATE INDEX idx_deaiify_status ON deaiify_runs(pass_status, run_date DESC);

COMMENT ON TABLE deaiify_runs IS 'De-ai-fy process tracking with 7-layer validation';

-- ============================================================================
-- ENHANCE EXISTING TABLES
-- ============================================================================

-- Enhance linkedin_posts with new columns
ALTER TABLE linkedin_posts ADD COLUMN IF NOT EXISTS metricool_batch_id BIGINT REFERENCES metricool_batches(id);
ALTER TABLE linkedin_posts ADD COLUMN IF NOT EXISTS optimal_publish_time TEXT CHECK (optimal_publish_time IN ('morning_8_10', 'midday_12_13', 'evening_17_19', 'other'));
ALTER TABLE linkedin_posts ADD COLUMN IF NOT EXISTS carousel_structure TEXT;
ALTER TABLE linkedin_posts ADD COLUMN IF NOT EXISTS visual_style TEXT;
ALTER TABLE linkedin_posts ADD COLUMN IF NOT EXISTS text_length INTEGER;
ALTER TABLE linkedin_posts ADD COLUMN IF NOT EXISTS structure_type TEXT CHECK (structure_type IN ('story', 'how_to', 'list', 'case_study', 'insight', 'question', 'personal'));
ALTER TABLE linkedin_posts ADD COLUMN IF NOT EXISTS campaign_id BIGINT REFERENCES content_campaigns(id);

-- Rename competitor_content_analysis to creator_content_analysis
ALTER TABLE competitor_content_analysis RENAME TO creator_content_analysis;
ALTER TABLE creator_content_analysis RENAME COLUMN competitor_name TO creator_name;
ALTER TABLE creator_content_analysis RENAME COLUMN competitor_profile_url TO creator_profile_url;
ALTER TABLE creator_content_analysis ADD COLUMN IF NOT EXISTS research_session_id BIGINT REFERENCES creator_research_sessions(id);

-- Drop old indexes and create new ones with updated names
DROP INDEX IF EXISTS idx_competitor_analysis_competitor;
DROP INDEX IF EXISTS idx_competitor_analysis_date;
CREATE INDEX IF NOT EXISTS idx_creator_analysis_creator ON creator_content_analysis(creator_name, post_date DESC);
CREATE INDEX IF NOT EXISTS idx_creator_analysis_date ON creator_content_analysis(post_date DESC);
CREATE INDEX IF NOT EXISTS idx_creator_analysis_session ON creator_content_analysis(research_session_id);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- 1. Get Creator Insights Summary
CREATE OR REPLACE FUNCTION get_creator_insights_summary(p_session_id BIGINT DEFAULT NULL)
RETURNS TABLE (
    session_date DATE,
    creators_analyzed INTEGER,
    posts_reviewed INTEGER,
    hooks_extracted INTEGER,
    ctas_extracted INTEGER,
    top_patterns TEXT[],
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        crs.session_date,
        ARRAY_LENGTH(crs.creators_analyzed, 1)::INTEGER,
        crs.total_posts_reviewed,
        crs.hooks_extracted,
        crs.ctas_extracted,
        crs.patterns_identified,
        crs.status
    FROM creator_research_sessions crs
    WHERE (p_session_id IS NULL OR crs.id = p_session_id)
    ORDER BY crs.session_date DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_creator_insights_summary IS 'Summary of creator research sessions';

-- 2. Get Metricool Batch Progress
CREATE OR REPLACE FUNCTION get_metricool_batch_progress(p_batch_id BIGINT)
RETURNS TABLE (
    batch_name TEXT,
    total_planned INTEGER,
    drafted INTEGER,
    deaified INTEGER,
    approved INTEGER,
    loaded INTEGER,
    progress_percentage INTEGER,
    next_step TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mb.batch_name,
        mb.total_posts_planned,
        mb.posts_drafted,
        mb.posts_deaified,
        mb.posts_approved,
        mb.posts_loaded_to_metricool,
        ROUND((mb.posts_loaded_to_metricool::NUMERIC / NULLIF(mb.total_posts_planned, 0) * 100))::INTEGER,
        CASE 
            WHEN mb.batch_status = 'planning' THEN 'Start drafting'
            WHEN mb.batch_status = 'drafting' THEN 'Complete drafts'
            WHEN mb.batch_status = 'deaify_pass' THEN 'Run de-ai-fy on all posts'
            WHEN mb.batch_status = 'yasmine_review' THEN 'Waiting for Yasmine approval'
            WHEN mb.batch_status = 'loaded' THEN 'Set optimal publish times'
            WHEN mb.batch_status = 'scheduled' THEN 'All set - scheduled in Metricool'
            ELSE 'Unknown'
        END
    FROM metricool_batches mb
    WHERE mb.id = p_batch_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_metricool_batch_progress IS 'Track monthly batch workflow progress';

-- 3. Get Campaign Performance Summary
CREATE OR REPLACE FUNCTION get_campaign_performance_summary(p_campaign_id BIGINT)
RETURNS TABLE (
    campaign_name TEXT,
    posts_published INTEGER,
    avg_engagement_rate NUMERIC,
    total_impressions INTEGER,
    warm_leads INTEGER,
    days_active INTEGER,
    performance_vs_baseline NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH campaign_posts AS (
        SELECT 
            cc.campaign_name,
            COUNT(lp.id)::INTEGER AS posts_count,
            AVG(lp.engagement_rate) AS avg_eng,
            SUM(lp.impressions)::INTEGER AS total_imp,
            SUM(lp.warm_leads_generated)::INTEGER AS warm_leads,
            (CURRENT_DATE - cc.start_date)::INTEGER AS days_active
        FROM content_campaigns cc
        LEFT JOIN linkedin_posts lp ON cc.id = lp.campaign_id
        WHERE cc.id = p_campaign_id
          AND lp.published_at IS NOT NULL
        GROUP BY cc.campaign_name, cc.start_date
    ),
    baseline AS (
        SELECT AVG(engagement_rate) AS baseline_eng
        FROM linkedin_posts
        WHERE published_at > NOW() - INTERVAL '90 days'
          AND campaign_id IS NULL
    )
    SELECT 
        cp.campaign_name,
        cp.posts_count,
        ROUND(cp.avg_eng, 2),
        cp.total_imp,
        cp.warm_leads,
        cp.days_active,
        ROUND(((cp.avg_eng - (SELECT baseline_eng FROM baseline)) / NULLIF((SELECT baseline_eng FROM baseline), 0) * 100), 1)
    FROM campaign_posts cp;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_campaign_performance_summary IS 'Campaign performance vs baseline';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- 1. Metricool Batch Status
CREATE OR REPLACE VIEW v_metricool_batch_status AS
SELECT 
    mb.id,
    mb.batch_name,
    mb.batch_month,
    mb.batch_year,
    mb.batch_status,
    mb.total_posts_planned,
    mb.posts_loaded_to_metricool,
    ROUND((mb.posts_loaded_to_metricool::NUMERIC / NULLIF(mb.total_posts_planned, 0) * 100))::INTEGER AS progress_percentage,
    mb.yasmine_approved,
    COUNT(lp.id) AS posts_in_batch
FROM metricool_batches mb
LEFT JOIN linkedin_posts lp ON mb.id = lp.metricool_batch_id
GROUP BY mb.id, mb.batch_name, mb.batch_month, mb.batch_year, mb.batch_status, 
         mb.total_posts_planned, mb.posts_loaded_to_metricool, mb.yasmine_approved
ORDER BY mb.batch_year DESC, mb.batch_month DESC;

COMMENT ON VIEW v_metricool_batch_status IS 'Current batch preparation status';

-- 2. Active Campaigns Dashboard
CREATE OR REPLACE VIEW v_active_campaigns_dashboard AS
SELECT 
    cc.id,
    cc.campaign_name,
    cc.campaign_theme,
    cc.start_date,
    cc.end_date,
    cc.campaign_status,
    cc.actual_posts_count,
    cc.target_posts_count,
    ROUND((cc.actual_posts_count::NUMERIC / NULLIF(cc.target_posts_count, 0) * 100))::INTEGER AS completion_percentage,
    cc.avg_engagement_rate,
    cc.warm_leads_generated,
    (CURRENT_DATE - cc.start_date)::INTEGER AS days_running
FROM content_campaigns cc
WHERE cc.campaign_status IN ('planning', 'active')
ORDER BY cc.start_date DESC;

COMMENT ON VIEW v_active_campaigns_dashboard IS 'Active content campaigns overview';

-- 3. Creator Library Stats
CREATE OR REPLACE VIEW v_creator_library_stats AS
SELECT 
    'Hooks' AS library_type,
    COUNT(*)::INTEGER AS total_items,
    COUNT(*) FILTER (WHERE status = 'active')::INTEGER AS active_items,
    ROUND(AVG(effectiveness_rating), 1) AS avg_effectiveness,
    SUM(usage_count)::INTEGER AS total_usage
FROM creator_hooks_library

UNION ALL

SELECT 
    'CTAs' AS library_type,
    COUNT(*)::INTEGER,
    COUNT(*) FILTER (WHERE status = 'active')::INTEGER,
    ROUND(AVG(effectiveness_rating), 1),
    SUM(usage_count)::INTEGER
FROM creator_cta_library;

COMMENT ON VIEW v_creator_library_stats IS 'Creator hooks and CTAs library overview';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- - 7 new tables for creator research, Metricool batching, strategy, campaigns, de-ai-fy tracking
-- - Enhanced 2 existing tables (linkedin_posts with 7 new columns, renamed competitor → creator)
-- - 3 new helper functions for insights summary, batch progress, campaign performance
-- - 3 new views for batch status, campaigns, creator library stats
-- Total tables in database: 168 (161 + 7 new)
