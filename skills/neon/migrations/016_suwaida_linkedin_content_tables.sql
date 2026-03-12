-- Migration 016: Suwaida (LinkedIn Content Specialist) Tables
-- Domain: LinkedIn presence, content creation, engagement, Top Voice, warm lead generation
-- Agent: Suwaida (@SuwaidaLinkedInBot)
-- Created: 2025-01-27

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- 1. LinkedIn Posts
CREATE TABLE IF NOT EXISTS linkedin_posts (
    id BIGSERIAL PRIMARY KEY,
    post_date TIMESTAMPTZ NOT NULL,
    post_url TEXT UNIQUE,
    post_type TEXT CHECK (post_type IN ('text', 'image', 'carousel', 'video', 'poll', 'article', 'newsletter')),
    post_status TEXT NOT NULL DEFAULT 'draft' CHECK (post_status IN ('draft', 'approved', 'scheduled', 'published', 'deleted')),
    content_text TEXT NOT NULL,
    content_pillar TEXT CHECK (content_pillar IN ('ai_automation', 'small_business', 'case_study', 'personal_story', 'industry_insight', 'thought_leadership', 'how_to', 'behind_the_scenes')),
    hook_formula TEXT,
    cta_type TEXT CHECK (cta_type IN ('discovery_call', 'website_visit', 'dm', 'comment', 'like', 'share', 'none')),
    has_image BOOLEAN DEFAULT FALSE,
    has_carousel BOOLEAN DEFAULT FALSE,
    carousel_slides INTEGER,
    image_urls TEXT[],
    scheduled_for TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    impressions INTEGER DEFAULT 0,
    reactions INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    profile_views_24h INTEGER DEFAULT 0,
    engagement_rate NUMERIC(5, 2),
    warm_leads_generated INTEGER DEFAULT 0,
    de_ai_fy_passed BOOLEAN DEFAULT FALSE,
    yasmine_approved BOOLEAN DEFAULT FALSE,
    google_doc_url TEXT,
    metricool_id TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'suwaida'
);

CREATE INDEX idx_linkedin_posts_date ON linkedin_posts(post_date DESC);
CREATE INDEX idx_linkedin_posts_status ON linkedin_posts(post_status, scheduled_for) WHERE post_status IN ('approved', 'scheduled');
CREATE INDEX idx_linkedin_posts_pillar ON linkedin_posts(content_pillar, post_date DESC);
CREATE INDEX idx_linkedin_posts_performance ON linkedin_posts(engagement_rate DESC, post_date DESC) WHERE published_at IS NOT NULL;

COMMENT ON TABLE linkedin_posts IS 'All LinkedIn posts with performance tracking';

-- 2. LinkedIn Content Ideas
CREATE TABLE IF NOT EXISTS linkedin_content_ideas (
    id BIGSERIAL PRIMARY KEY,
    idea_title TEXT NOT NULL,
    idea_description TEXT NOT NULL,
    content_pillar TEXT CHECK (content_pillar IN ('ai_automation', 'small_business', 'case_study', 'personal_story', 'industry_insight', 'thought_leadership', 'how_to', 'behind_the_scenes')),
    suggested_format TEXT CHECK (suggested_format IN ('text', 'image', 'carousel', 'video', 'poll', 'newsletter')),
    hook_angle TEXT,
    target_audience TEXT,
    cta_suggestion TEXT,
    inspiration_sources TEXT[],
    priority INTEGER CHECK (priority BETWEEN 1 AND 4),
    status TEXT NOT NULL DEFAULT 'idea' CHECK (status IN ('idea', 'researching', 'drafting', 'completed', 'archived')),
    post_id BIGINT REFERENCES linkedin_posts(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'suwaida',
    notes TEXT
);

CREATE INDEX idx_linkedin_content_ideas_status ON linkedin_content_ideas(status, priority DESC) WHERE status IN ('idea', 'researching', 'drafting');
CREATE INDEX idx_linkedin_content_ideas_pillar ON linkedin_content_ideas(content_pillar, status);

COMMENT ON TABLE linkedin_content_ideas IS 'Content ideas bank with priority and status tracking';

-- 3. LinkedIn Newsletters
CREATE TABLE IF NOT EXISTS linkedin_newsletters (
    id BIGSERIAL PRIMARY KEY,
    newsletter_date DATE NOT NULL,
    edition_number INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    newsletter_url TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'published')),
    scheduled_for TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    subscribers_at_publish INTEGER,
    subscriber_growth INTEGER,
    opens INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    de_ai_fy_passed BOOLEAN DEFAULT FALSE,
    google_doc_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_newsletters_date ON linkedin_newsletters(newsletter_date DESC);
CREATE INDEX idx_newsletters_status ON linkedin_newsletters(status, scheduled_for) WHERE status IN ('draft', 'scheduled');

COMMENT ON TABLE linkedin_newsletters IS 'Newsletter editions with subscriber growth tracking';

-- 4. Collaborative Articles
CREATE TABLE IF NOT EXISTS collaborative_articles (
    id BIGSERIAL PRIMARY KEY,
    article_url TEXT NOT NULL UNIQUE,
    article_title TEXT NOT NULL,
    article_topic TEXT,
    contribution_text TEXT NOT NULL,
    contributed_at TIMESTAMPTZ NOT NULL,
    upvotes INTEGER DEFAULT 0,
    selected_as_top_answer BOOLEAN DEFAULT FALSE,
    target_weekly_count INTEGER DEFAULT 3,
    notes TEXT
);

CREATE INDEX idx_collaborative_articles_date ON collaborative_articles(contributed_at DESC);
CREATE INDEX idx_collaborative_articles_top ON collaborative_articles(selected_as_top_answer, contributed_at DESC) WHERE selected_as_top_answer = TRUE;

COMMENT ON TABLE collaborative_articles IS 'LinkedIn Collaborative Article contributions (Top Voice badge)';

-- 5. Competitor Content Analysis
CREATE TABLE IF NOT EXISTS competitor_content_analysis (
    id BIGSERIAL PRIMARY KEY,
    competitor_name TEXT NOT NULL,
    competitor_profile_url TEXT NOT NULL,
    post_url TEXT NOT NULL UNIQUE,
    post_date TIMESTAMPTZ,
    post_type TEXT CHECK (post_type IN ('text', 'image', 'carousel', 'video', 'poll', 'article')),
    content_summary TEXT,
    hook_approach TEXT,
    engagement_estimate TEXT,
    what_worked TEXT,
    what_didnt TEXT,
    takeaway_for_us TEXT,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_competitor_analysis_competitor ON competitor_content_analysis(competitor_name, post_date DESC);
CREATE INDEX idx_competitor_analysis_date ON competitor_content_analysis(post_date DESC);

COMMENT ON TABLE competitor_content_analysis IS 'Competitor LinkedIn content tracking';

-- 6. LinkedIn Engagement Log
CREATE TABLE IF NOT EXISTS linkedin_engagement_log (
    id BIGSERIAL PRIMARY KEY,
    engagement_date DATE NOT NULL,
    activity_type TEXT CHECK (activity_type IN ('comment_reply', 'proactive_comment', 'dm_warm_lead', 'dm_conversation', 'post_share', 'profile_view')),
    target_profile_url TEXT,
    target_post_url TEXT,
    engagement_text TEXT,
    is_icp BOOLEAN DEFAULT FALSE,
    warm_lead_generated BOOLEAN DEFAULT FALSE,
    lead_handed_to_jalila BOOLEAN DEFAULT FALSE,
    notes TEXT,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_engagement_log_date ON linkedin_engagement_log(engagement_date DESC);
CREATE INDEX idx_engagement_log_leads ON linkedin_engagement_log(warm_lead_generated, engagement_date DESC) WHERE warm_lead_generated = TRUE;

COMMENT ON TABLE linkedin_engagement_log IS 'Daily engagement activity tracking';

-- 7. LinkedIn Profile Metrics
CREATE TABLE IF NOT EXISTS linkedin_profile_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_date DATE NOT NULL UNIQUE,
    followers_count INTEGER,
    follower_growth INTEGER,
    profile_views INTEGER,
    profile_view_growth INTEGER,
    post_impressions_total INTEGER,
    post_engagement_total INTEGER,
    avg_engagement_rate NUMERIC(5, 2),
    ssi_score INTEGER CHECK (ssi_score BETWEEN 0 AND 100),
    top_voice_badge BOOLEAN DEFAULT FALSE,
    warm_leads_generated INTEGER DEFAULT 0,
    discovery_calls_booked INTEGER DEFAULT 0,
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_profile_metrics_date ON linkedin_profile_metrics(metric_date DESC);

COMMENT ON TABLE linkedin_profile_metrics IS 'Yasmine''s LinkedIn profile KPIs over time';

-- 8. Content Performance Patterns
CREATE TABLE IF NOT EXISTS content_performance_patterns (
    id BIGSERIAL PRIMARY KEY,
    pattern_name TEXT NOT NULL UNIQUE,
    pattern_type TEXT CHECK (pattern_type IN ('hook', 'format', 'pillar', 'timing', 'cta', 'length', 'visual')),
    description TEXT NOT NULL,
    what_works TEXT NOT NULL,
    what_doesnt TEXT,
    supporting_data TEXT,
    confidence_level TEXT CHECK (confidence_level IN ('low', 'medium', 'high')),
    sample_size INTEGER,
    avg_engagement_boost NUMERIC(5, 1),
    recommendation TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'testing', 'deprecated')),
    identified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_validated_at TIMESTAMPTZ,
    notes TEXT
);

CREATE INDEX idx_linkedin_patterns_type ON content_performance_patterns(pattern_type, status);
CREATE INDEX idx_linkedin_patterns_confidence ON content_performance_patterns(confidence_level, avg_engagement_boost DESC) WHERE status = 'active';

COMMENT ON TABLE content_performance_patterns IS 'Identified patterns from post performance analysis';

-- ============================================================================
-- ENHANCE EXISTING TABLES
-- ============================================================================

-- Add LinkedIn references to content table (from Zahra's tables)
ALTER TABLE content ADD COLUMN IF NOT EXISTS linkedin_post_id BIGINT REFERENCES linkedin_posts(id);
ALTER TABLE content ADD COLUMN IF NOT EXISTS linkedin_newsletter_id BIGINT REFERENCES linkedin_newsletters(id);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- 1. Get LinkedIn Performance Summary
CREATE OR REPLACE FUNCTION get_linkedin_performance_summary(p_days INTEGER DEFAULT 7)
RETURNS TABLE (
    posts_published INTEGER,
    avg_engagement_rate NUMERIC,
    total_impressions INTEGER,
    total_reactions INTEGER,
    warm_leads_generated INTEGER,
    top_performing_pillar TEXT,
    avg_engagement_by_format JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER,
        ROUND(AVG(lp.engagement_rate), 2),
        SUM(lp.impressions)::INTEGER,
        SUM(lp.reactions)::INTEGER,
        SUM(lp.warm_leads_generated)::INTEGER,
        (SELECT lp2.content_pillar 
         FROM linkedin_posts lp2 
         WHERE lp2.published_at > NOW() - (p_days || ' days')::INTERVAL
         GROUP BY lp2.content_pillar 
         ORDER BY AVG(lp2.engagement_rate) DESC 
         LIMIT 1),
        (SELECT jsonb_object_agg(lp3.post_type, ROUND(AVG(lp3.engagement_rate), 2))
         FROM linkedin_posts lp3
         WHERE lp3.published_at > NOW() - (p_days || ' days')::INTERVAL
         GROUP BY lp3.post_type)
    FROM linkedin_posts lp
    WHERE lp.published_at > NOW() - (p_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_linkedin_performance_summary IS 'Weekly performance snapshot';

-- 2. Get Content Calendar Status
CREATE OR REPLACE FUNCTION get_content_calendar_status()
RETURNS TABLE (
    week_starting DATE,
    posts_scheduled INTEGER,
    posts_in_draft INTEGER,
    posts_published INTEGER,
    gaps INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH weeks AS (
        SELECT generate_series(
            DATE_TRUNC('week', CURRENT_DATE),
            DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '14 days',
            INTERVAL '1 week'
        )::DATE AS week_start
    )
    SELECT 
        w.week_start,
        COUNT(*) FILTER (WHERE lp.post_status = 'scheduled' AND lp.scheduled_for >= w.week_start AND lp.scheduled_for < w.week_start + INTERVAL '7 days')::INTEGER,
        COUNT(*) FILTER (WHERE lp.post_status = 'draft')::INTEGER,
        COUNT(*) FILTER (WHERE lp.post_status = 'published' AND lp.published_at >= w.week_start AND lp.published_at < w.week_start + INTERVAL '7 days')::INTEGER,
        (5 - COUNT(*) FILTER (WHERE (lp.post_status = 'scheduled' OR lp.post_status = 'published') AND ((lp.scheduled_for >= w.week_start AND lp.scheduled_for < w.week_start + INTERVAL '7 days') OR (lp.published_at >= w.week_start AND lp.published_at < w.week_start + INTERVAL '7 days'))))::INTEGER AS gaps
    FROM weeks w
    LEFT JOIN linkedin_posts lp ON 
        (lp.scheduled_for >= w.week_start AND lp.scheduled_for < w.week_start + INTERVAL '7 days') OR
        (lp.published_at >= w.week_start AND lp.published_at < w.week_start + INTERVAL '7 days')
    GROUP BY w.week_start
    ORDER BY w.week_start;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_content_calendar_status IS 'Next 2 weeks content status';

-- 3. Identify Winning Content Patterns
CREATE OR REPLACE FUNCTION identify_winning_content_patterns()
RETURNS TABLE (
    pattern_category TEXT,
    pattern_value TEXT,
    post_count BIGINT,
    avg_engagement NUMERIC,
    above_baseline NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH baseline AS (
        SELECT AVG(engagement_rate) AS baseline_engagement
        FROM linkedin_posts
        WHERE published_at > NOW() - INTERVAL '90 days'
          AND engagement_rate IS NOT NULL
    )
    SELECT 
        'Content Pillar'::TEXT,
        lp.content_pillar,
        COUNT(*),
        ROUND(AVG(lp.engagement_rate), 2),
        ROUND((AVG(lp.engagement_rate) - (SELECT baseline_engagement FROM baseline)) / (SELECT baseline_engagement FROM baseline) * 100, 1)
    FROM linkedin_posts lp
    WHERE lp.published_at > NOW() - INTERVAL '90 days'
      AND lp.engagement_rate IS NOT NULL
      AND lp.content_pillar IS NOT NULL
    GROUP BY lp.content_pillar
    HAVING AVG(lp.engagement_rate) > (SELECT baseline_engagement FROM baseline)
    
    UNION ALL
    
    SELECT 
        'Post Format'::TEXT,
        lp.post_type,
        COUNT(*),
        ROUND(AVG(lp.engagement_rate), 2),
        ROUND((AVG(lp.engagement_rate) - (SELECT baseline_engagement FROM baseline)) / (SELECT baseline_engagement FROM baseline) * 100, 1)
    FROM linkedin_posts lp
    WHERE lp.published_at > NOW() - INTERVAL '90 days'
      AND lp.engagement_rate IS NOT NULL
      AND lp.post_type IS NOT NULL
    GROUP BY lp.post_type
    HAVING AVG(lp.engagement_rate) > (SELECT baseline_engagement FROM baseline)
    
    ORDER BY avg_engagement DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION identify_winning_content_patterns IS 'Find what''s working based on data';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- 1. LinkedIn Dashboard
CREATE OR REPLACE VIEW v_linkedin_dashboard AS
SELECT 
    (SELECT followers_count FROM linkedin_profile_metrics ORDER BY metric_date DESC LIMIT 1) AS current_followers,
    (SELECT follower_growth FROM linkedin_profile_metrics ORDER BY metric_date DESC LIMIT 1) AS follower_growth_today,
    (SELECT COUNT(*) FROM linkedin_posts WHERE published_at > NOW() - INTERVAL '7 days') AS posts_last_7d,
    (SELECT ROUND(AVG(engagement_rate), 2) FROM linkedin_posts WHERE published_at > NOW() - INTERVAL '7 days') AS avg_engagement_7d,
    (SELECT SUM(warm_leads_generated) FROM linkedin_posts WHERE published_at > NOW() - INTERVAL '7 days') AS warm_leads_7d,
    (SELECT COUNT(*) FROM linkedin_posts WHERE post_status = 'scheduled' AND scheduled_for > NOW()) AS posts_scheduled,
    (SELECT COUNT(*) FROM linkedin_content_ideas WHERE status IN ('idea', 'researching', 'drafting')) AS ideas_in_pipeline,
    (SELECT ssi_score FROM linkedin_profile_metrics ORDER BY metric_date DESC LIMIT 1) AS current_ssi;

COMMENT ON VIEW v_linkedin_dashboard IS 'Current performance snapshot';

-- 2. Top Performing Posts
CREATE OR REPLACE VIEW v_top_performing_posts AS
SELECT 
    lp.id,
    lp.post_date,
    lp.post_type,
    lp.content_pillar,
    lp.engagement_rate,
    lp.impressions,
    lp.reactions,
    lp.comments,
    lp.warm_leads_generated,
    lp.post_url
FROM linkedin_posts lp
WHERE lp.published_at > NOW() - INTERVAL '90 days'
  AND lp.engagement_rate IS NOT NULL
ORDER BY lp.engagement_rate DESC
LIMIT 20;

COMMENT ON VIEW v_top_performing_posts IS 'Best performers in last 90 days';

-- 3. Content Calendar Gaps
CREATE OR REPLACE VIEW v_content_calendar_gaps AS
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE,
        CURRENT_DATE + INTERVAL '14 days',
        INTERVAL '1 day'
    )::DATE AS calendar_date
),
daily_posts AS (
    SELECT 
        ds.calendar_date,
        COUNT(lp.id) AS posts_count
    FROM date_series ds
    LEFT JOIN linkedin_posts lp ON 
        DATE(lp.scheduled_for) = ds.calendar_date OR
        DATE(lp.published_at) = ds.calendar_date
    WHERE lp.post_status IN ('scheduled', 'published')
    GROUP BY ds.calendar_date
)
SELECT 
    calendar_date,
    posts_count,
    CASE 
        WHEN posts_count = 0 THEN 'No posts'
        WHEN posts_count < 1 THEN 'Below target'
        ELSE 'On track'
    END AS status
FROM daily_posts
WHERE posts_count < 1
ORDER BY calendar_date;

COMMENT ON VIEW v_content_calendar_gaps IS 'Identify scheduling gaps';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- - 8 new tables for LinkedIn content, engagement, performance tracking
-- - Enhanced 1 existing table (content)
-- - 3 helper functions for performance summary, calendar status, pattern detection
-- - 3 views for dashboard, top posts, calendar gaps
-- Total tables in database: 161 (153 + 8 new)
