-- Migration 005: Laila LinkedIn Outreach Infrastructure
-- Agent: Laila — LinkedIn Outreach & Lead Gen Specialist
-- Purpose: LinkedIn profiles, connection requests, sequences, templates, HeyReach sync, analytics
-- Created: 2026-02-23

-- ============================================================================
-- NEW TABLES (6)
-- ============================================================================

-- 1. LINKEDIN PROFILES
-- Enriched LinkedIn profile data from research
CREATE TABLE linkedin_profiles (
    id BIGSERIAL PRIMARY KEY,
    
    -- Lead association
    lead_id BIGINT REFERENCES leads(id),
    
    -- Profile identification
    linkedin_url TEXT NOT NULL UNIQUE,
    linkedin_id VARCHAR(255), -- LinkedIn's internal ID
    public_id VARCHAR(255), -- vanity URL (e.g., "johndoe")
    
    -- Basic info
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    headline TEXT,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    industry VARCHAR(100),
    
    -- Profile data
    bio TEXT,
    profile_photo_url TEXT,
    banner_image_url TEXT,
    follower_count INTEGER,
    connection_count INTEGER,
    
    -- Engagement signals
    recent_posts JSONB, -- Last 5-10 posts with engagement data
    top_post_topics JSONB, -- [{"topic": "AI automation", "count": 3}]
    post_frequency VARCHAR(50), -- daily, weekly, monthly, rare
    avg_engagement_score INTEGER, -- 0-100
    
    -- Mutual connections
    mutual_connection_count INTEGER DEFAULT 0,
    mutual_connections JSONB, -- [{name, title, company, linkedin_url}]
    
    -- Company context
    company_size VARCHAR(50), -- 1-10, 11-50, 51-200, etc.
    company_industry VARCHAR(100),
    company_description TEXT,
    
    -- Personalization angle
    personalization_angle VARCHAR(50), -- recent_post, mutual_connection, company_news, industry_trend, general
    personalization_notes TEXT, -- Why this angle was chosen
    best_talking_point TEXT, -- Strongest hook from research
    
    -- Research quality
    research_quality_score INTEGER, -- 0-100
    research_completeness VARCHAR(50), -- full, partial, minimal
    
    -- Scraping metadata
    scraped_at TIMESTAMP,
    scraper_source VARCHAR(50), -- heyreach, apify, phantombuster
    scrape_success BOOLEAN DEFAULT true,
    scrape_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_linkedin_profiles_lead ON linkedin_profiles(lead_id);
CREATE INDEX idx_linkedin_profiles_url ON linkedin_profiles(linkedin_url);
CREATE INDEX idx_linkedin_profiles_company ON linkedin_profiles(company);
CREATE INDEX idx_linkedin_profiles_title ON linkedin_profiles(title);
CREATE INDEX idx_linkedin_profiles_research_quality ON linkedin_profiles(research_quality_score DESC);
CREATE INDEX idx_linkedin_profiles_scraped ON linkedin_profiles(scraped_at DESC);

COMMENT ON TABLE linkedin_profiles IS 'Enriched LinkedIn profile data from prospect research';

-- ============================================================================

-- 2. LINKEDIN CONNECTION REQUESTS
-- Track connection requests sent via HeyReach with status
CREATE TABLE linkedin_connection_requests (
    id BIGSERIAL PRIMARY KEY,
    
    -- Lead/Profile association
    lead_id BIGINT REFERENCES leads(id),
    profile_id BIGINT REFERENCES linkedin_profiles(id),
    campaign_id BIGINT REFERENCES campaigns(id),
    
    -- Message content
    connection_message TEXT NOT NULL,
    personalization_used TEXT, -- What specific detail we personalized on
    message_template_id BIGINT, -- If generated from template
    
    -- HeyReach integration
    heyreach_request_id VARCHAR(255),
    heyreach_campaign_id VARCHAR(255),
    heyreach_contact_id VARCHAR(255),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending', 
    -- pending, sent, accepted, declined, withdrawn, expired
    
    sent_at TIMESTAMP,
    accepted_at TIMESTAMP,
    declined_at TIMESTAMP,
    
    -- Response tracking
    responded BOOLEAN DEFAULT false,
    first_response_at TIMESTAMP,
    response_time_hours INTEGER, -- Hours from sent to first response
    
    -- Follow-up
    follow_up_needed BOOLEAN DEFAULT false,
    follow_up_sent BOOLEAN DEFAULT false,
    follow_up_sequence_id BIGINT,
    
    -- Qualification
    qualified BOOLEAN DEFAULT false,
    qualification_score INTEGER, -- 0-100 based on response quality
    handed_to_jalila BOOLEAN DEFAULT false,
    handoff_date TIMESTAMP,
    
    -- Performance metrics
    engagement_level VARCHAR(50), -- cold, warm, hot
    conversion_potential VARCHAR(50), -- low, medium, high
    
    -- Notes
    internal_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_linkedin_conn_lead ON linkedin_connection_requests(lead_id);
CREATE INDEX idx_linkedin_conn_profile ON linkedin_connection_requests(profile_id);
CREATE INDEX idx_linkedin_conn_campaign ON linkedin_connection_requests(campaign_id);
CREATE INDEX idx_linkedin_conn_status ON linkedin_connection_requests(status);
CREATE INDEX idx_linkedin_conn_heyreach_id ON linkedin_connection_requests(heyreach_request_id);
CREATE INDEX idx_linkedin_conn_responded ON linkedin_connection_requests(responded) WHERE responded = true;
CREATE INDEX idx_linkedin_conn_qualified ON linkedin_connection_requests(qualified) WHERE qualified = true;
CREATE INDEX idx_linkedin_conn_sent ON linkedin_connection_requests(sent_at DESC);

COMMENT ON TABLE linkedin_connection_requests IS 'LinkedIn connection requests sent via HeyReach';

-- ============================================================================

-- 3. LINKEDIN SEQUENCES
-- Multi-step LinkedIn message sequences (connection → follow-ups)
CREATE TABLE linkedin_sequences (
    id BIGSERIAL PRIMARY KEY,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Sequence structure
    total_steps INTEGER NOT NULL,
    delay_pattern JSONB, -- e.g., [3, 7, 14] days between steps after connection
    
    -- Campaign association
    campaign_id BIGINT REFERENCES campaigns(id),
    
    -- Target criteria
    target_title JSONB, -- ["VP Sales", "CTO"]
    target_industry JSONB,
    target_company_size VARCHAR(50),
    
    -- Performance
    total_sent INTEGER DEFAULT 0,
    total_accepted INTEGER DEFAULT 0,
    total_responded INTEGER DEFAULT 0,
    total_qualified INTEGER DEFAULT 0,
    
    -- Metrics
    acceptance_rate DECIMAL(5,2),
    response_rate DECIMAL(5,2),
    qualification_rate DECIMAL(5,2),
    avg_response_time_hours INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, paused, archived
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_linkedin_sequences_campaign ON linkedin_sequences(campaign_id);
CREATE INDEX idx_linkedin_sequences_status ON linkedin_sequences(status);
CREATE INDEX idx_linkedin_sequences_response_rate ON linkedin_sequences(response_rate DESC);

COMMENT ON TABLE linkedin_sequences IS 'Multi-step LinkedIn outreach sequences';

-- ============================================================================

-- 4. LINKEDIN MESSAGE TEMPLATES
-- Reusable LinkedIn message templates with personalization variables
CREATE TABLE linkedin_message_templates (
    id BIGSERIAL PRIMARY KEY,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Template type
    template_type VARCHAR(50) NOT NULL, 
    -- connection_request, first_followup, second_followup, value_share, meeting_request
    
    -- Personalization strategy
    personalization_angle VARCHAR(50), 
    -- recent_post, mutual_connection, company_news, shared_interest, industry_trend
    
    -- Message content
    message_template TEXT NOT NULL,
    personalization_variables JSONB, 
    -- [{var: "post_topic", required: true, example: "AI automation"}, ...]
    
    -- Usage context
    best_for_title JSONB, -- Job titles this works well for
    best_for_industry JSONB, -- Industries this resonates with
    
    -- Performance tracking
    times_used INTEGER DEFAULT 0,
    times_accepted INTEGER DEFAULT 0,
    times_responded INTEGER DEFAULT 0,
    
    -- Metrics
    acceptance_rate DECIMAL(5,2),
    response_rate DECIMAL(5,2),
    
    -- A/B testing
    is_variant BOOLEAN DEFAULT false,
    parent_template_id BIGINT REFERENCES linkedin_message_templates(id),
    variant_name VARCHAR(100),
    is_winner BOOLEAN DEFAULT false,
    winner_declared_at TIMESTAMP,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, testing, active, winner, archived
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_linkedin_templates_type ON linkedin_message_templates(template_type);
CREATE INDEX idx_linkedin_templates_angle ON linkedin_message_templates(personalization_angle);
CREATE INDEX idx_linkedin_templates_response_rate ON linkedin_message_templates(response_rate DESC);
CREATE INDEX idx_linkedin_templates_status ON linkedin_message_templates(status);
CREATE INDEX idx_linkedin_templates_winner ON linkedin_message_templates(is_winner) WHERE is_winner = true;

COMMENT ON TABLE linkedin_message_templates IS 'LinkedIn message templates with personalization';

-- ============================================================================

-- 5. HEYREACH SYNC LOG
-- Track API sync with HeyReach for debugging and monitoring
CREATE TABLE heyreach_sync_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- Sync details
    sync_type VARCHAR(50) NOT NULL, 
    -- contact_upload, campaign_create, response_fetch, connection_status, profile_scrape
    entity_type VARCHAR(50), -- campaign, contact, message, connection
    entity_id BIGINT, -- local ID
    heyreach_id VARCHAR(255), -- HeyReach ID
    
    -- Request/Response
    request_payload JSONB,
    response_payload JSONB,
    http_status INTEGER,
    
    -- Status
    status VARCHAR(50) NOT NULL, -- success, failed, partial, rate_limited
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Performance
    duration_ms INTEGER,
    
    -- Timestamps
    synced_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_heyreach_sync_type ON heyreach_sync_log(sync_type);
CREATE INDEX idx_heyreach_sync_status ON heyreach_sync_log(status);
CREATE INDEX idx_heyreach_sync_entity ON heyreach_sync_log(entity_type, entity_id);
CREATE INDEX idx_heyreach_sync_date ON heyreach_sync_log(synced_at DESC);

COMMENT ON TABLE heyreach_sync_log IS 'HeyReach API sync log for debugging';

-- ============================================================================

-- 6. LINKEDIN CAMPAIGN ANALYTICS
-- Daily snapshots of LinkedIn campaign performance
CREATE TABLE linkedin_campaign_analytics (
    id BIGSERIAL PRIMARY KEY,
    
    -- Campaign
    campaign_id BIGINT REFERENCES campaigns(id),
    campaign_name VARCHAR(255),
    
    -- Daily metrics
    date DATE NOT NULL,
    connections_sent INTEGER DEFAULT 0,
    connections_accepted INTEGER DEFAULT 0,
    connections_declined INTEGER DEFAULT 0,
    connections_pending INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    messages_replied INTEGER DEFAULT 0,
    
    -- Rates
    acceptance_rate DECIMAL(5,2),
    response_rate DECIMAL(5,2),
    qualified_lead_rate DECIMAL(5,2),
    
    -- Lead quality
    qualified_leads INTEGER DEFAULT 0,
    meetings_booked INTEGER DEFAULT 0,
    
    -- Engagement
    avg_response_time_hours INTEGER,
    engagement_score INTEGER, -- 0-100
    
    -- Cumulative totals
    cumulative_sent INTEGER,
    cumulative_accepted INTEGER,
    cumulative_qualified INTEGER,
    
    -- Timestamps
    snapshot_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_linkedin_analytics_campaign ON linkedin_campaign_analytics(campaign_id);
CREATE INDEX idx_linkedin_analytics_date ON linkedin_campaign_analytics(date DESC);
CREATE UNIQUE INDEX idx_linkedin_analytics_unique ON linkedin_campaign_analytics(campaign_id, date);

COMMENT ON TABLE linkedin_campaign_analytics IS 'Daily LinkedIn campaign performance snapshots';

-- ============================================================================
-- MODIFY EXISTING TABLES
-- ============================================================================

-- LEADS table enhancements
ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_url TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_profile_id BIGINT REFERENCES linkedin_profiles(id);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS heyreach_contact_id VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS connection_status VARCHAR(50); -- not_sent, pending, accepted, declined
ALTER TABLE leads ADD COLUMN IF NOT EXISTS connection_date TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_linkedin_interaction TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_response_count INTEGER DEFAULT 0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_engagement_level VARCHAR(50); -- cold, warm, hot

CREATE INDEX IF NOT EXISTS idx_leads_linkedin_url ON leads(linkedin_url);
CREATE INDEX IF NOT EXISTS idx_leads_linkedin_profile ON leads(linkedin_profile_id);
CREATE INDEX IF NOT EXISTS idx_leads_heyreach_id ON leads(heyreach_contact_id);
CREATE INDEX IF NOT EXISTS idx_leads_connection_status ON leads(connection_status);

COMMENT ON COLUMN leads.linkedin_url IS 'LinkedIn profile URL';
COMMENT ON COLUMN leads.heyreach_contact_id IS 'HeyReach contact ID for sync';
COMMENT ON COLUMN leads.connection_status IS 'LinkedIn connection request status';

-- ============================================================================

-- CAMPAIGNS table enhancements
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS heyreach_campaign_id VARCHAR(255);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS linkedin_sequence_id BIGINT REFERENCES linkedin_sequences(id);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS daily_connection_limit INTEGER DEFAULT 25;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS target_acceptance_rate DECIMAL(5,2) DEFAULT 40.00;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS target_response_rate DECIMAL(5,2) DEFAULT 20.00;

CREATE INDEX IF NOT EXISTS idx_campaigns_heyreach_id ON campaigns(heyreach_campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_linkedin_sequence ON campaigns(linkedin_sequence_id);

COMMENT ON COLUMN campaigns.heyreach_campaign_id IS 'HeyReach campaign ID for sync';
COMMENT ON COLUMN campaigns.linkedin_sequence_id IS 'LinkedIn sequence used in this campaign';

-- ============================================================================

-- COMMUNICATIONS table enhancements
ALTER TABLE communications ADD COLUMN IF NOT EXISTS heyreach_message_id VARCHAR(255);
ALTER TABLE communications ADD COLUMN IF NOT EXISTS linkedin_thread_url TEXT;
ALTER TABLE communications ADD COLUMN IF NOT EXISTS is_connection_request BOOLEAN DEFAULT false;
ALTER TABLE communications ADD COLUMN IF NOT EXISTS connection_accepted BOOLEAN DEFAULT false;
ALTER TABLE communications ADD COLUMN IF NOT EXISTS linkedin_template_id BIGINT REFERENCES linkedin_message_templates(id);
ALTER TABLE communications ADD COLUMN IF NOT EXISTS personalization_source TEXT; -- What detail we personalized on

CREATE INDEX IF NOT EXISTS idx_communications_heyreach_id ON communications(heyreach_message_id);
CREATE INDEX IF NOT EXISTS idx_communications_connection_req ON communications(is_connection_request) WHERE is_connection_request = true;
CREATE INDEX IF NOT EXISTS idx_communications_linkedin_template ON communications(linkedin_template_id);

COMMENT ON COLUMN communications.heyreach_message_id IS 'HeyReach message ID for sync';
COMMENT ON COLUMN communications.is_connection_request IS 'Whether this was the initial connection request';
COMMENT ON COLUMN communications.personalization_source IS 'What specific detail was used for personalization';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Get pending connection requests older than X days (needs follow-up)
CREATE OR REPLACE FUNCTION get_stale_connection_requests(days_threshold INTEGER DEFAULT 7)
RETURNS TABLE (
    request_id BIGINT,
    lead_name VARCHAR,
    linkedin_url TEXT,
    sent_at TIMESTAMP,
    days_pending INTEGER,
    campaign_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lcr.id,
        l.name,
        lp.linkedin_url,
        lcr.sent_at,
        EXTRACT(DAY FROM NOW() - lcr.sent_at)::INTEGER AS days_pending,
        c.name
    FROM linkedin_connection_requests lcr
    JOIN leads l ON lcr.lead_id = l.id
    JOIN linkedin_profiles lp ON lcr.profile_id = lp.id
    LEFT JOIN campaigns c ON lcr.campaign_id = c.id
    WHERE lcr.status = 'pending'
    AND lcr.sent_at < NOW() - (days_threshold || ' days')::INTERVAL
    AND lcr.follow_up_sent = false
    ORDER BY lcr.sent_at ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_stale_connection_requests IS 'Find pending connection requests older than threshold that need follow-up';

-- ============================================================================

-- Get qualified LinkedIn leads ready for Jalila handoff
CREATE OR REPLACE FUNCTION get_linkedin_qualified_leads()
RETURNS TABLE (
    lead_id BIGINT,
    lead_name VARCHAR,
    company VARCHAR,
    title VARCHAR,
    linkedin_url TEXT,
    qualification_score INTEGER,
    response_snippet TEXT,
    accepted_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.id,
        l.name,
        lp.company,
        lp.title,
        lp.linkedin_url,
        lcr.qualification_score,
        LEFT(lcr.internal_notes, 200) AS response_snippet,
        lcr.accepted_at
    FROM linkedin_connection_requests lcr
    JOIN leads l ON lcr.lead_id = l.id
    JOIN linkedin_profiles lp ON lcr.profile_id = lp.id
    WHERE lcr.qualified = true
    AND lcr.handed_to_jalila = false
    AND lcr.deleted_at IS NULL
    ORDER BY lcr.qualification_score DESC, lcr.first_response_at DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_linkedin_qualified_leads IS 'Get qualified LinkedIn leads ready for sales handoff';

-- ============================================================================

-- Get top performing LinkedIn templates
CREATE OR REPLACE FUNCTION get_top_linkedin_templates(min_uses INTEGER DEFAULT 10)
RETURNS TABLE (
    template_id BIGINT,
    template_name VARCHAR,
    template_type VARCHAR,
    times_used INTEGER,
    acceptance_rate DECIMAL,
    response_rate DECIMAL,
    is_winner BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        name,
        template_type,
        times_used,
        acceptance_rate,
        response_rate,
        is_winner
    FROM linkedin_message_templates
    WHERE times_used >= min_uses
    AND status IN ('active', 'winner')
    AND deleted_at IS NULL
    ORDER BY response_rate DESC, acceptance_rate DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_top_linkedin_templates IS 'Get best performing LinkedIn message templates';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- LinkedIn outreach pipeline overview
CREATE OR REPLACE VIEW linkedin_outreach_pipeline AS
SELECT 
    c.id AS campaign_id,
    c.name AS campaign_name,
    c.status AS campaign_status,
    ls.name AS sequence_name,
    COUNT(DISTINCT lcr.id) AS total_connections_sent,
    COUNT(DISTINCT CASE WHEN lcr.status = 'accepted' THEN lcr.id END) AS connections_accepted,
    COUNT(DISTINCT CASE WHEN lcr.status = 'pending' THEN lcr.id END) AS connections_pending,
    COUNT(DISTINCT CASE WHEN lcr.responded = true THEN lcr.id END) AS leads_responded,
    COUNT(DISTINCT CASE WHEN lcr.qualified = true THEN lcr.id END) AS leads_qualified,
    ROUND(AVG(CASE WHEN lcr.status = 'accepted' THEN 1.0 ELSE 0.0 END) * 100, 2) AS acceptance_rate,
    ROUND(AVG(CASE WHEN lcr.responded = true THEN 1.0 ELSE 0.0 END) * 100, 2) AS response_rate,
    AVG(lcr.response_time_hours) AS avg_response_time_hours
FROM campaigns c
LEFT JOIN linkedin_sequences ls ON c.linkedin_sequence_id = ls.id
LEFT JOIN linkedin_connection_requests lcr ON c.id = lcr.campaign_id
WHERE c.deleted_at IS NULL
GROUP BY c.id, c.name, c.status, ls.name;

COMMENT ON VIEW linkedin_outreach_pipeline IS 'LinkedIn campaign performance overview';

-- ============================================================================

-- LinkedIn leads needing attention
CREATE OR REPLACE VIEW linkedin_leads_needing_attention AS
SELECT 
    l.id AS lead_id,
    l.name AS lead_name,
    lp.company,
    lp.title,
    lp.linkedin_url,
    lcr.status AS connection_status,
    lcr.sent_at,
    EXTRACT(DAY FROM NOW() - lcr.sent_at)::INTEGER AS days_since_sent,
    lcr.responded,
    lcr.qualified,
    lcr.follow_up_needed,
    lcr.follow_up_sent,
    CASE 
        WHEN lcr.status = 'pending' AND lcr.sent_at < NOW() - INTERVAL '7 days' AND lcr.follow_up_sent = false 
            THEN 'stale_connection'
        WHEN lcr.responded = true AND lcr.qualified = false 
            THEN 'needs_qualification'
        WHEN lcr.qualified = true AND lcr.handed_to_jalila = false 
            THEN 'ready_for_handoff'
        WHEN lcr.follow_up_needed = true AND lcr.follow_up_sent = false 
            THEN 'needs_followup'
        ELSE 'ok'
    END AS attention_type
FROM leads l
JOIN linkedin_profiles lp ON l.linkedin_profile_id = lp.id
JOIN linkedin_connection_requests lcr ON l.id = lcr.lead_id
WHERE lcr.deleted_at IS NULL
AND (
    (lcr.status = 'pending' AND lcr.sent_at < NOW() - INTERVAL '7 days' AND lcr.follow_up_sent = false)
    OR (lcr.responded = true AND lcr.qualified = false)
    OR (lcr.qualified = true AND lcr.handed_to_jalila = false)
    OR (lcr.follow_up_needed = true AND lcr.follow_up_sent = false)
);

COMMENT ON VIEW linkedin_leads_needing_attention IS 'LinkedIn leads requiring action or follow-up';

-- ============================================================================
-- END MIGRATION
-- ============================================================================

-- Migration complete: Laila's LinkedIn outreach infrastructure operational
-- 6 new tables created
-- 3 existing tables enhanced
-- 3 helper functions added
-- 2 views created
