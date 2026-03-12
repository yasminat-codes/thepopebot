-- Migration 007: Zahra Content Infrastructure
-- Agent: Zahra — Content Creator
-- Purpose: Content calendar, templates, performance tracking, brand voice, ideas, repurposing
-- Created: 2026-02-23

-- 1. CONTENT CALENDAR
CREATE TABLE content_calendar (
    id BIGSERIAL PRIMARY KEY,
    content_id BIGINT REFERENCES content(id),
    planned_publish_date DATE NOT NULL,
    actual_publish_date DATE,
    publish_time TIME,
    platform VARCHAR(50) NOT NULL,
    platform_specific_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'planned',
    approval_status VARCHAR(50) DEFAULT 'pending',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    revision_notes TEXT,
    content_type VARCHAR(50),
    topic VARCHAR(255),
    primary_cta VARCHAR(255),
    target_audience VARCHAR(100),
    target_impressions INTEGER,
    target_engagement_rate DECIMAL(5,2),
    target_conversions INTEGER,
    campaign_id BIGINT REFERENCES campaigns(id),
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_content_calendar_content ON content_calendar(content_id);
CREATE INDEX idx_content_calendar_date ON content_calendar(planned_publish_date);
CREATE INDEX idx_content_calendar_platform ON content_calendar(platform);
CREATE INDEX idx_content_calendar_status ON content_calendar(status);

-- 2. CONTENT TEMPLATES
CREATE TABLE content_templates (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    platform VARCHAR(50),
    structure JSONB,
    variables JSONB,
    template_text TEXT NOT NULL,
    character_count INTEGER,
    estimated_writing_time_minutes INTEGER,
    best_for JSONB,
    example_topics JSONB,
    dos_and_donts JSONB,
    times_used INTEGER DEFAULT 0,
    avg_engagement_rate DECIMAL(5,2),
    conversion_rate DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_content_templates_type ON content_templates(template_type);
CREATE INDEX idx_content_templates_platform ON content_templates(platform);

-- 3. CONTENT PERFORMANCE
CREATE TABLE content_performance (
    id BIGSERIAL PRIMARY KEY,
    content_id BIGINT REFERENCES content(id),
    content_calendar_id BIGINT REFERENCES content_calendar(id),
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    post_url TEXT,
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2),
    click_through_rate DECIMAL(5,2),
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2),
    top_demographics JSONB,
    top_industries JSONB,
    published_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP,
    measured_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_content_performance_content ON content_performance(content_id);
CREATE INDEX idx_content_performance_platform ON content_performance(platform);

-- 4. BRAND VOICE LIBRARY
CREATE TABLE brand_voice_library (
    id BIGSERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    category VARCHAR(50),
    use_when TEXT,
    avoid_when TEXT,
    better_alternative TEXT,
    good_examples JSONB,
    bad_examples JSONB,
    severity VARCHAR(50) DEFAULT 'warning',
    auto_flag BOOLEAN DEFAULT false,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_brand_voice_type ON brand_voice_library(item_type);

-- 5. CONTENT IDEAS
CREATE TABLE content_ideas (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    suggested_format VARCHAR(50),
    suggested_platforms JSONB,
    topic_category VARCHAR(100),
    target_audience VARCHAR(100),
    potential_hooks JSONB,
    key_takeaways JSONB,
    relevance_score INTEGER,
    timeliness_score INTEGER,
    uniqueness_score INTEGER,
    effort_required INTEGER,
    total_score INTEGER,
    status VARCHAR(50) DEFAULT 'backlog',
    assigned_to VARCHAR(100),
    scheduled_for DATE,
    idea_source VARCHAR(100),
    source_url TEXT,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_content_ideas_status ON content_ideas(status);
CREATE INDEX idx_content_ideas_score ON content_ideas(total_score DESC);

-- 6. CONTENT REPURPOSING LOG
CREATE TABLE content_repurposing_log (
    id BIGSERIAL PRIMARY KEY,
    original_content_id BIGINT REFERENCES content(id),
    original_platform VARCHAR(50),
    original_format VARCHAR(50),
    repurposed_content_id BIGINT REFERENCES content(id),
    repurposed_platform VARCHAR(50),
    repurposed_format VARCHAR(50),
    transformation_type VARCHAR(50),
    changes_made TEXT,
    effort_level VARCHAR(50),
    original_engagement_rate DECIMAL(5,2),
    repurposed_engagement_rate DECIMAL(5,2),
    performance_delta DECIMAL(5,2),
    repurposed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_repurposing_original ON content_repurposing_log(original_content_id);

-- ENHANCE CONTENT TABLE
ALTER TABLE content ADD COLUMN IF NOT EXISTS content_status VARCHAR(50) DEFAULT 'draft';
ALTER TABLE content ADD COLUMN IF NOT EXISTS template_id BIGINT REFERENCES content_templates(id);
ALTER TABLE content ADD COLUMN IF NOT EXISTS word_count INTEGER;
ALTER TABLE content ADD COLUMN IF NOT EXISTS character_count INTEGER;
ALTER TABLE content ADD COLUMN IF NOT EXISTS reading_time_minutes INTEGER;
ALTER TABLE content ADD COLUMN IF NOT EXISTS seo_keywords JSONB;
ALTER TABLE content ADD COLUMN IF NOT EXISTS target_audience VARCHAR(100);
ALTER TABLE content ADD COLUMN IF NOT EXISTS primary_cta TEXT;
ALTER TABLE content ADD COLUMN IF NOT EXISTS de_ai_fied BOOLEAN DEFAULT false;
ALTER TABLE content ADD COLUMN IF NOT EXISTS de_ai_fy_score INTEGER;

CREATE INDEX IF NOT EXISTS idx_content_status ON content(content_status);
