-- =============================================================================
-- linkedin-studio: Complete PostgreSQL Schema
-- Database: Neon PostgreSQL (serverless)
-- Niche: AI consulting and implementation
-- Created: 2026-03-02
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- TABLE 1: topic_bank
-- Purpose: Content ideas and topic IDs — the central idea repository
-- =============================================================================
CREATE TABLE topic_bank (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title             TEXT        NOT NULL,
    hook_suggestion   TEXT,
    cta_suggestion    TEXT,
    post_idea         TEXT,
    -- Source of the topic idea
    source            VARCHAR(50) NOT NULL
                          CHECK (source IN ('google_trends', 'reddit', 'creator', 'manual')),
    niche             VARCHAR(100) DEFAULT 'AI consulting',
    -- 0-100 relevance/trending score
    trend_score       INTEGER      DEFAULT 0
                          CHECK (trend_score BETWEEN 0 AND 100),
    -- Which content pillar this topic serves
    content_pillar    VARCHAR(50)
                          CHECK (content_pillar IN ('thought_leadership', 'education', 'social_proof', 'cta')),
    status            VARCHAR(20)  DEFAULT 'new'
                          CHECK (status IN ('new', 'in_progress', 'used', 'archived')),
    tags              TEXT[],
    created_at        TIMESTAMPTZ  DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  DEFAULT NOW()
);

COMMENT ON TABLE  topic_bank                IS 'Central repository of content ideas sourced from trends, Reddit, creators, and manual entry';
COMMENT ON COLUMN topic_bank.source         IS 'Origin of the topic: google_trends | reddit | creator | manual';
COMMENT ON COLUMN topic_bank.trend_score    IS '0-100 relevance score; higher = more timely/trending';
COMMENT ON COLUMN topic_bank.content_pillar IS 'Which content strategy pillar this topic aligns with';
COMMENT ON COLUMN topic_bank.status         IS 'Lifecycle state: new → in_progress → used | archived';


-- =============================================================================
-- TABLE 2: hook_library
-- Purpose: Proven hooks database — learn from what works over time
-- =============================================================================
CREATE TABLE hook_library (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    hook_text         TEXT        NOT NULL,
    -- Classification of hook style
    hook_type         VARCHAR(30)
                          CHECK (hook_type IN ('question', 'stat', 'story', 'bold_claim', 'number')),
    -- 0-100 score derived from actual post performance metrics
    performance_score INTEGER      DEFAULT 50
                          CHECK (performance_score BETWEEN 0 AND 100),
    content_pillar    VARCHAR(50)
                          CHECK (content_pillar IN ('thought_leadership', 'education', 'social_proof', 'cta')),
    used_count        INTEGER      DEFAULT 0,
    created_at        TIMESTAMPTZ  DEFAULT NOW()
);

COMMENT ON TABLE  hook_library                   IS 'Library of proven hooks with performance scores updated from real post data';
COMMENT ON COLUMN hook_library.performance_score IS '0-100 score; updated when post_performance data is synced from Metricool';
COMMENT ON COLUMN hook_library.used_count        IS 'How many times this hook has been used in content_queue posts';


-- =============================================================================
-- TABLE 3: pain_points
-- Purpose: Reddit-sourced audience pain points for content ideation
-- =============================================================================
CREATE TABLE pain_points (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    subreddit        VARCHAR(100) NOT NULL,
    reddit_post_id   VARCHAR(50),
    pain_text        TEXT         NOT NULL,
    comment_context  TEXT,
    keyword_matches  TEXT[],
    upvotes          INTEGER      DEFAULT 0,
    comment_count    INTEGER      DEFAULT 0,
    -- Computed: upvotes + (comment_count * 3) — comments weighted higher
    engagement_score NUMERIC      GENERATED ALWAYS AS (upvotes + comment_count * 3) STORED,
    -- References topic_bank.id (stored as TEXT for flexibility; FK not enforced cross-source)
    content_id       TEXT,
    extracted_at     TIMESTAMPTZ  DEFAULT NOW(),
    used_in_post     BOOLEAN      DEFAULT FALSE
);

COMMENT ON TABLE  pain_points                  IS 'Reddit-sourced pain points that map to content opportunities';
COMMENT ON COLUMN pain_points.engagement_score IS 'Computed column: upvotes + (comment_count * 3); higher = more resonant pain point';
COMMENT ON COLUMN pain_points.content_id       IS 'Optional link to topic_bank.id when this pain point spawns a topic';


-- =============================================================================
-- TABLE 4: trends
-- Purpose: Google Trends data with TTL expiry to keep data fresh
-- =============================================================================
CREATE TABLE trends (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword         TEXT         NOT NULL,
    -- 0-100 from Google Trends API
    trend_score     INTEGER      CHECK (trend_score BETWEEN 0 AND 100),
    niche           VARCHAR(100) DEFAULT 'AI consulting',
    -- ISO 3166-1 alpha-2 geo code
    geo             VARCHAR(10)  DEFAULT 'US',
    -- Related/rising queries as returned by the Trends API
    related_queries JSONB,
    source          VARCHAR(20)  DEFAULT 'google_trends',
    extracted_at    TIMESTAMPTZ  DEFAULT NOW(),
    -- Trend data expires after 7 days; cron job should refresh
    expires_at      TIMESTAMPTZ  DEFAULT (NOW() + INTERVAL '7 days')
);

COMMENT ON TABLE  trends            IS 'Google Trends keyword data; rows expire after 7 days and should be refreshed by cron';
COMMENT ON COLUMN trends.trend_score IS '0-100 interest score from Google Trends; 100 = peak search interest';
COMMENT ON COLUMN trends.expires_at  IS 'Soft expiry — trend data older than this should be re-fetched';


-- =============================================================================
-- TABLE 5: creator_posts_cache
-- Purpose: Cached LinkedIn creator post data for pattern extraction
-- =============================================================================
CREATE TABLE creator_posts_cache (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_url         TEXT          NOT NULL,
    creator_name        TEXT,
    post_text           TEXT          NOT NULL,
    post_url            TEXT,
    estimated_views     INTEGER,
    comment_count       INTEGER,
    reaction_count      INTEGER,
    -- (reactions + comments) / estimated_views * 100
    engagement_rate     NUMERIC(5,2),
    -- Extracted first line of the post
    hook_text           TEXT,
    -- Overall content structure classification
    post_structure      VARCHAR(50)
                            CHECK (post_structure IN ('story', 'list', 'insight', 'question')),
    -- JSON blob: hooks, CTAs, structures, patterns extracted by AI
    patterns_extracted  JSONB,
    scraped_at          TIMESTAMPTZ   DEFAULT NOW(),
    -- Prevent duplicate scraping of same post from same creator
    UNIQUE (creator_url, post_text)
);

COMMENT ON TABLE  creator_posts_cache                  IS 'Cached LinkedIn creator posts for pattern mining; deduped by creator_url + post_text';
COMMENT ON COLUMN creator_posts_cache.patterns_extracted IS 'AI-extracted patterns: hooks, CTAs, structures, pacing, emojis etc.';
COMMENT ON COLUMN creator_posts_cache.engagement_rate    IS 'Calculated engagement rate; null if estimated_views unavailable';


-- =============================================================================
-- TABLE 6: competitor_tracker
-- Purpose: Competitor profiles and aggregated content intelligence
-- =============================================================================
CREATE TABLE competitor_tracker (
    id                     UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_url            TEXT          NOT NULL UNIQUE,
    profile_name           TEXT,
    niche                  VARCHAR(100),
    avg_engagement_rate    NUMERIC(5,2),
    -- Qualitative frequency label
    posting_frequency      VARCHAR(30)
                               CHECK (posting_frequency IN ('daily', '2-3x/week', 'weekly', 'sporadic')),
    top_content_pillars    TEXT[],
    best_performing_hooks  TEXT[],
    last_analyzed          TIMESTAMPTZ,
    posts_analyzed         INTEGER       DEFAULT 0,
    -- Flexible JSON for additional insights (tone, CTA patterns, hashtags used)
    insights_json          JSONB,
    tracked_since          TIMESTAMPTZ   DEFAULT NOW()
);

COMMENT ON TABLE  competitor_tracker              IS 'Aggregated intelligence on competitor LinkedIn profiles';
COMMENT ON COLUMN competitor_tracker.insights_json IS 'Flexible JSON: tone analysis, CTA patterns, hashtag strategy, best posting times';


-- =============================================================================
-- TABLE 7: content_queue
-- Purpose: Posts ready for or scheduled to Metricool — the publishing pipeline
-- =============================================================================
CREATE TABLE content_queue (
    id                 UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    post_text          TEXT         NOT NULL,
    post_type          VARCHAR(30)  DEFAULT 'text'
                           CHECK (post_type IN ('text', 'carousel', 'image', 'poll')),
    content_pillar     VARCHAR(50)
                           CHECK (content_pillar IN ('thought_leadership', 'education', 'social_proof', 'cta')),
    -- Canva visual generation prompt and result
    visual_prompt_json JSONB,
    canva_design_id    TEXT,
    canva_design_url   TEXT,
    -- AI detection and quality scores (0-100)
    ai_score           INTEGER      CHECK (ai_score BETWEEN 0 AND 100),
    hook_score         INTEGER      CHECK (hook_score BETWEEN 0 AND 100),
    structure_score    INTEGER      CHECK (structure_score BETWEEN 0 AND 100),
    -- How many humanizer passes this post has been through
    humanizer_passes   INTEGER      DEFAULT 0,
    -- Full publishing lifecycle
    status             VARCHAR(30)  DEFAULT 'draft'
                           CHECK (status IN (
                               'draft', 'humanized', 'reviewed', 'visual_added',
                               'approved', 'scheduled', 'published', 'failed'
                           )),
    scheduled_at       TIMESTAMPTZ,
    published_at       TIMESTAMPTZ,
    -- Metricool post ID once scheduled/published
    metricool_id       TEXT,
    -- Traceability back to the originating topic
    source_topic_id    UUID         REFERENCES topic_bank(id) ON DELETE SET NULL,
    hashtags           TEXT[],
    created_at         TIMESTAMPTZ  DEFAULT NOW(),
    updated_at         TIMESTAMPTZ  DEFAULT NOW()
);

COMMENT ON TABLE  content_queue                  IS 'Full publishing pipeline: draft → humanized → reviewed → approved → scheduled → published';
COMMENT ON COLUMN content_queue.ai_score         IS '0-100 AI-likeness score; lower is better (less detectable as AI-written)';
COMMENT ON COLUMN content_queue.hook_score       IS '0-100 hook quality score; higher is better';
COMMENT ON COLUMN content_queue.humanizer_passes IS 'Number of times the humanizer agent has processed this post';
COMMENT ON COLUMN content_queue.source_topic_id  IS 'FK to topic_bank; nullable to allow manually created posts';


-- =============================================================================
-- TABLE 8: ai_phrases_blocklist
-- Purpose: Known AI-giveaway phrases to flag and replace during humanization
-- =============================================================================
CREATE TABLE ai_phrases_blocklist (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    phrase                  TEXT        NOT NULL UNIQUE,
    -- Classification of why this phrase is problematic
    category                VARCHAR(50)
                                CHECK (category IN ('transition', 'filler', 'corporate', 'conclusion', 'opener', 'intensifier', 'ai_tell')),
    severity                VARCHAR(10)  DEFAULT 'medium'
                                CHECK (severity IN ('low', 'medium', 'high')),
    -- Suggested human alternatives for this phrase
    replacement_suggestions TEXT[],
    added_at                TIMESTAMPTZ  DEFAULT NOW()
);

COMMENT ON TABLE  ai_phrases_blocklist                      IS 'Phrases that signal AI authorship; used by humanizer agent to detect and replace';
COMMENT ON COLUMN ai_phrases_blocklist.severity              IS 'high = immediate replacement required; medium = flag; low = style preference';
COMMENT ON COLUMN ai_phrases_blocklist.replacement_suggestions IS 'Array of human-sounding alternatives the humanizer can substitute';


-- =============================================================================
-- TABLE 9: post_performance
-- Purpose: Historical performance data synced from Metricool
-- =============================================================================
CREATE TABLE post_performance (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    content_queue_id  UUID         REFERENCES content_queue(id) ON DELETE SET NULL,
    metricool_post_id TEXT,
    platform          VARCHAR(30)  DEFAULT 'linkedin',
    impressions       INTEGER      DEFAULT 0,
    reach             INTEGER      DEFAULT 0,
    engagement_rate   NUMERIC(5,2),
    clicks            INTEGER      DEFAULT 0,
    likes             INTEGER      DEFAULT 0,
    comments          INTEGER      DEFAULT 0,
    shares            INTEGER      DEFAULT 0,
    content_pillar    VARCHAR(50),
    posted_at         TIMESTAMPTZ,
    -- Denormalized for fast time-of-day analysis
    day_of_week       VARCHAR(10),
    hour_of_day       INTEGER      CHECK (hour_of_day BETWEEN 0 AND 23),
    tracked_at        TIMESTAMPTZ  DEFAULT NOW()
);

COMMENT ON TABLE  post_performance              IS 'Metricool performance data synced after publishing; drives hook_library score updates';
COMMENT ON COLUMN post_performance.day_of_week  IS 'Denormalized day name (Monday–Sunday) for posting time analysis';
COMMENT ON COLUMN post_performance.hour_of_day  IS '0-23 UTC hour the post was published; for optimal time-of-day analysis';


-- =============================================================================
-- TABLE 10: brand_voice_profile
-- Purpose: User's writing persona and preferences — single source of truth for tone
-- =============================================================================
CREATE TABLE brand_voice_profile (
    id                   UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_name         VARCHAR(100)  DEFAULT 'default',
    persona_description  TEXT,
    -- Natural language tone descriptor
    writing_tone         VARCHAR(100),
    niche                TEXT          DEFAULT 'AI consulting and implementation',
    target_audience      TEXT,
    -- Phrases that are authentically "you"
    signature_phrases    TEXT[],
    -- Words to never use
    avoid_words          TEXT[],
    -- Ordered preference list
    preferred_hook_types TEXT[],
    -- Target word count per post
    avg_post_length      INTEGER       DEFAULT 220,
    -- e.g. {"thought_leadership": 40, "education": 30, "social_proof": 20, "cta": 10}
    content_pillars      JSONB,
    -- e.g. {"Tuesday": "08:00", "Thursday": "08:00", "Saturday": "10:00"}
    posting_schedule     JSONB,
    -- Only one profile active at a time
    is_active            BOOLEAN       DEFAULT TRUE,
    created_at           TIMESTAMPTZ   DEFAULT NOW(),
    updated_at           TIMESTAMPTZ   DEFAULT NOW()
);

COMMENT ON TABLE  brand_voice_profile                  IS 'Single source of truth for the user brand voice; agents read this before generating content';
COMMENT ON COLUMN brand_voice_profile.content_pillars   IS 'JSON map of pillar → target percentage, e.g. {"thought_leadership": 40}';
COMMENT ON COLUMN brand_voice_profile.posting_schedule  IS 'JSON map of day → optimal time, e.g. {"Tuesday": "08:00"}';
COMMENT ON COLUMN brand_voice_profile.is_active         IS 'Only one profile should be active; application enforces single-active constraint';


-- =============================================================================
-- INDEXES
-- =============================================================================

-- topic_bank
CREATE INDEX idx_topic_bank_status       ON topic_bank(status);
CREATE INDEX idx_topic_bank_source       ON topic_bank(source);
CREATE INDEX idx_topic_bank_trend_score  ON topic_bank(trend_score DESC);
CREATE INDEX idx_topic_bank_pillar       ON topic_bank(content_pillar);

-- pain_points
CREATE INDEX idx_pain_points_subreddit   ON pain_points(subreddit);
CREATE INDEX idx_pain_points_engagement  ON pain_points(engagement_score DESC);
CREATE INDEX idx_pain_points_unused      ON pain_points(used_in_post) WHERE used_in_post = FALSE;

-- trends
CREATE INDEX idx_trends_expires          ON trends(expires_at);
CREATE INDEX idx_trends_keyword          ON trends(keyword);
CREATE INDEX idx_trends_score            ON trends(trend_score DESC);

-- content_queue
CREATE INDEX idx_content_queue_status    ON content_queue(status);
CREATE INDEX idx_content_queue_scheduled ON content_queue(scheduled_at);
CREATE INDEX idx_content_queue_topic     ON content_queue(source_topic_id);
CREATE INDEX idx_content_queue_ai_score  ON content_queue(ai_score);

-- post_performance
CREATE INDEX idx_post_performance_posted   ON post_performance(posted_at DESC);
CREATE INDEX idx_post_performance_queue_id ON post_performance(content_queue_id);
CREATE INDEX idx_post_performance_pillar   ON post_performance(content_pillar);

-- hook_library
CREATE INDEX idx_hook_library_score      ON hook_library(performance_score DESC);
CREATE INDEX idx_hook_library_type       ON hook_library(hook_type);

-- competitor_tracker
CREATE INDEX idx_competitor_last_analyzed ON competitor_tracker(last_analyzed DESC);

-- brand_voice_profile
CREATE INDEX idx_brand_voice_active       ON brand_voice_profile(is_active) WHERE is_active = TRUE;


-- =============================================================================
-- UPDATED_AT TRIGGERS
-- Automatically maintain updated_at timestamps on mutable tables
-- =============================================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_topic_bank_updated_at
    BEFORE UPDATE ON topic_bank
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_content_queue_updated_at
    BEFORE UPDATE ON content_queue
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_brand_voice_updated_at
    BEFORE UPDATE ON brand_voice_profile
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
