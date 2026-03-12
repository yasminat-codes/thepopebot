-- Migration 004: Qamar Cold Email Infrastructure
-- Agent: Qamar — Cold Email Specialist
-- Purpose: Email sequences, templates, Instantly.ai sync, deliverability tracking, niche scouting, enrichment, analytics
-- Created: 2026-02-23

-- ============================================================================
-- NEW TABLES (9)
-- ============================================================================

-- 1. EMAIL SEQUENCES
-- Multi-step email sequences with performance tracking
CREATE TABLE email_sequences (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Sequence structure
    total_steps INTEGER NOT NULL,
    delay_pattern JSONB, -- e.g., [1, 3, 7, 14] days between steps
    
    -- Campaign association
    campaign_id BIGINT REFERENCES campaigns(id),
    
    -- Performance
    total_sent INTEGER DEFAULT 0,
    total_opened INTEGER DEFAULT 0,
    total_replied INTEGER DEFAULT 0,
    total_bounced INTEGER DEFAULT 0,
    total_unsubscribed INTEGER DEFAULT 0,
    
    -- Metrics
    open_rate DECIMAL(5,2),
    reply_rate DECIMAL(5,2),
    bounce_rate DECIMAL(5,2),
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, paused, archived
    instantly_sequence_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_sync_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_email_sequences_campaign ON email_sequences(campaign_id);
CREATE INDEX idx_email_sequences_status ON email_sequences(status);
CREATE INDEX idx_email_sequences_reply_rate ON email_sequences(reply_rate DESC);

COMMENT ON TABLE email_sequences IS 'Multi-step email sequences for cold email campaigns';

-- ============================================================================

-- 2. EMAIL TEMPLATES
-- Reusable email copy with A/B variants and performance tracking
CREATE TABLE email_templates (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Template type
    template_type VARCHAR(50) NOT NULL, -- cold_intro, follow_up_1, follow_up_2, reply, breakup
    niche VARCHAR(100), -- recruiting, dental, ecommerce, etc.
    
    -- Email content
    subject_line TEXT NOT NULL,
    body TEXT NOT NULL,
    
    -- Personalization
    has_personalization BOOLEAN DEFAULT false,
    personalization_fields JSONB, -- [{field: "company", required: true}, ...]
    
    -- Variants (A/B testing)
    is_variant BOOLEAN DEFAULT false,
    parent_template_id BIGINT REFERENCES email_templates(id),
    variant_name VARCHAR(100), -- "subject_a", "subject_b", "cta_soft", "cta_hard"
    
    -- Performance tracking
    times_sent INTEGER DEFAULT 0,
    times_opened INTEGER DEFAULT 0,
    times_replied INTEGER DEFAULT 0,
    times_bounced INTEGER DEFAULT 0,
    
    -- Metrics
    open_rate DECIMAL(5,2),
    reply_rate DECIMAL(5,2),
    bounce_rate DECIMAL(5,2),
    
    -- Winner tracking
    is_winner BOOLEAN DEFAULT false,
    winner_declared_at TIMESTAMP,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, testing, active, winner, archived
    
    -- De-AI-fy tracking
    de_ai_fied BOOLEAN DEFAULT false,
    de_ai_fy_score INTEGER, -- 0-100, higher = more human
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_email_templates_type ON email_templates(template_type);
CREATE INDEX idx_email_templates_niche ON email_templates(niche);
CREATE INDEX idx_email_templates_reply_rate ON email_templates(reply_rate DESC);
CREATE INDEX idx_email_templates_status ON email_templates(status);
CREATE INDEX idx_email_templates_winner ON email_templates(is_winner) WHERE is_winner = true;

COMMENT ON TABLE email_templates IS 'Reusable email templates with A/B variants and performance tracking';

-- ============================================================================

-- 3. INSTANTLY SYNC LOG
-- Track API sync with Instantly.ai for debugging and monitoring
CREATE TABLE instantly_sync_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- Sync details
    sync_type VARCHAR(50) NOT NULL, -- campaign_create, lead_upload, reply_fetch, analytics_pull, warmup_status
    entity_type VARCHAR(50), -- campaign, lead, email, account
    entity_id BIGINT, -- local ID (campaign_id, lead_id, etc.)
    instantly_id VARCHAR(255), -- Instantly.ai ID
    
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

CREATE INDEX idx_instantly_sync_type ON instantly_sync_log(sync_type);
CREATE INDEX idx_instantly_sync_status ON instantly_sync_log(status);
CREATE INDEX idx_instantly_sync_entity ON instantly_sync_log(entity_type, entity_id);
CREATE INDEX idx_instantly_sync_date ON instantly_sync_log(synced_at DESC);

COMMENT ON TABLE instantly_sync_log IS 'API sync log with Instantly.ai for debugging and monitoring';

-- ============================================================================

-- 4. DELIVERABILITY METRICS
-- Domain health, sender reputation, and deliverability tracking
CREATE TABLE deliverability_metrics (
    id BIGSERIAL PRIMARY KEY,
    
    -- Domain/Account
    email_account VARCHAR(255) NOT NULL, -- sending email address
    domain VARCHAR(255) NOT NULL,
    instantly_account_id VARCHAR(255),
    
    -- Deliverability metrics
    bounce_rate DECIMAL(5,2),
    spam_complaint_rate DECIMAL(5,2),
    unsubscribe_rate DECIMAL(5,2),
    
    -- Sending health
    daily_send_limit INTEGER,
    current_daily_sends INTEGER DEFAULT 0,
    warmup_enabled BOOLEAN DEFAULT true,
    warmup_stage VARCHAR(50), -- new, warming, warm, hot
    
    -- Reputation scores
    sender_score INTEGER, -- 0-100
    domain_reputation VARCHAR(50), -- excellent, good, fair, poor
    ip_reputation VARCHAR(50),
    
    -- Issues
    blacklisted BOOLEAN DEFAULT false,
    blacklist_sources JSONB, -- ["spamhaus", "barracuda"]
    last_blacklist_check TIMESTAMP,
    
    -- Monitoring alerts
    alert_level VARCHAR(50) DEFAULT 'normal', -- normal, warning, critical
    alert_reason TEXT,
    
    -- Timestamps
    measured_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_deliverability_email ON deliverability_metrics(email_account);
CREATE INDEX idx_deliverability_domain ON deliverability_metrics(domain);
CREATE INDEX idx_deliverability_alert ON deliverability_metrics(alert_level);
CREATE INDEX idx_deliverability_date ON deliverability_metrics(measured_at DESC);
CREATE INDEX idx_deliverability_blacklisted ON deliverability_metrics(blacklisted) WHERE blacklisted = true;

COMMENT ON TABLE deliverability_metrics IS 'Domain health and sender reputation tracking';

-- ============================================================================

-- 5. NICHE RESEARCH
-- Full niche lifecycle tracking with 6-factor viability scoring
CREATE TABLE niche_research (
    id BIGSERIAL PRIMARY KEY,
    
    -- Niche identification
    niche_name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL, -- URL-safe identifier (e.g., "dental-medspas")
    niche_category VARCHAR(100), -- b2b_saas, ecommerce, healthcare, finance, etc.
    
    -- Discovery metadata
    discovered_date DATE NOT NULL,
    discovery_mode VARCHAR(50), -- daily_scan, deep_scout, manual
    last_scanned_at TIMESTAMP,
    scan_frequency VARCHAR(50) DEFAULT 'daily', -- daily, weekly, monthly, retired
    
    -- 6-Factor Viability Scoring (detailed breakdown)
    market_size_score DECIMAL(3,1), -- 1.0-10.0
    pain_severity_score DECIMAL(3,1), -- 1.0-10.0
    competition_score DECIMAL(3,1), -- 1.0-10.0 (inverse - higher = less competition)
    accessibility_score DECIMAL(3,1), -- 1.0-10.0
    offer_fit_score DECIMAL(3,1), -- 1.0-10.0
    timing_score DECIMAL(3,1), -- 1.0-10.0
    
    -- Overall viability
    viability_score DECIMAL(3,1), -- Weighted average of above 6 factors (1.0-10.0)
    viability_last_calculated TIMESTAMP,
    campaign_history_bonus DECIMAL(3,2) DEFAULT 0.00, -- -0.5 to +0.5 based on similar niche performance
    
    -- Market data (evidence-backed)
    market_size_estimate VARCHAR(100), -- "50k+ businesses", "$1B+ TAM"
    market_size_evidence TEXT, -- Source URL or description
    competition_level VARCHAR(50), -- low, medium, high, saturated
    competition_count INTEGER, -- # of agencies/competitors found
    competition_evidence TEXT,
    
    -- Pain analysis
    pain_summary TEXT, -- One-line summary of top pains
    pain_points JSONB, -- [{pain: "...", severity: "high", intensity: 8, source_url: "...", quote: "..."}, ...]
    underserved_segments JSONB,
    
    -- Target ICP (for waterfall-enrichment)
    ideal_title JSONB, -- ["VP Sales", "Director of Marketing"]
    ideal_company_size VARCHAR(50), -- "10-50 employees"
    ideal_industry JSONB,
    estimated_list_size INTEGER,
    list_sources JSONB, -- ["LinkedIn Sales Navigator", "Apollo", "industry directory"]
    email_findability VARCHAR(50), -- high, medium, low
    
    -- Reddit tracking
    tracked_subreddits JSONB, -- ["r/dentistry", "r/MedSpa"]
    
    -- Research sources
    research_sources JSONB, -- [{source: "reddit", url: "...", date: "...", type: "pain_thread"}, ...]
    research_folder_path VARCHAR(500), -- e.g., "research/dental-medspas/"
    
    -- Lifecycle management
    lifecycle_stage VARCHAR(50) NOT NULL DEFAULT 'discovered', 
    -- discovered → researching → campaign_prep → active_campaign → mature → retired
    stage_changed_at TIMESTAMP,
    
    -- Campaign linkage
    ready_for_campaign BOOLEAN DEFAULT false,
    campaign_created BOOLEAN DEFAULT false,
    first_campaign_id BIGINT REFERENCES campaigns(id),
    
    -- Performance tracking (from live campaigns)
    campaigns_launched INTEGER DEFAULT 0,
    total_leads_generated INTEGER DEFAULT 0,
    total_emails_sent INTEGER DEFAULT 0,
    total_replies INTEGER DEFAULT 0,
    avg_reply_rate DECIMAL(5,2),
    avg_booking_rate DECIMAL(5,2),
    last_campaign_performance_update TIMESTAMP,
    
    -- Retirement tracking
    retired BOOLEAN DEFAULT false,
    retirement_reason VARCHAR(100), -- low_reply_rate, high_bounce, saturated, manual
    retirement_date DATE,
    retirement_notes TEXT,
    
    -- Alert status
    alert_level VARCHAR(50) DEFAULT 'normal', -- normal, attention_needed, high_viability, declining, saturated
    alert_reason TEXT,
    last_alert_sent TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_niche_slug ON niche_research(slug);
CREATE INDEX idx_niche_name ON niche_research(niche_name);
CREATE INDEX idx_niche_category ON niche_research(niche_category);
CREATE INDEX idx_niche_viability ON niche_research(viability_score DESC);
CREATE INDEX idx_niche_lifecycle ON niche_research(lifecycle_stage);
CREATE INDEX idx_niche_ready ON niche_research(ready_for_campaign) WHERE ready_for_campaign = true;
CREATE INDEX idx_niche_retired ON niche_research(retired) WHERE retired = true;
CREATE INDEX idx_niche_alert ON niche_research(alert_level) WHERE alert_level != 'normal';
CREATE INDEX idx_niche_last_scanned ON niche_research(last_scanned_at DESC);

COMMENT ON TABLE niche_research IS 'Niche scouting with lifecycle tracking and 6-factor viability scoring';

-- ============================================================================

-- 6. NICHE SIGNALS
-- Individual signals (pain threads, buying signals, etc.) with decay tracking
CREATE TABLE niche_signals (
    id BIGSERIAL PRIMARY KEY,
    
    -- Niche association
    niche_id BIGINT REFERENCES niche_research(id) ON DELETE CASCADE,
    niche_slug VARCHAR(255) NOT NULL,
    
    -- Signal identification
    signal_type VARCHAR(50) NOT NULL, 
    -- pain_thread, buying_signal, hiring_signal, trigger_event, competitor_move, market_shift, campaign_feedback
    source VARCHAR(100) NOT NULL, -- r/dentistry, Indeed, TechCrunch, Instantly.ai, etc.
    source_url TEXT,
    
    -- Signal content
    summary TEXT NOT NULL, -- One-line description
    quote TEXT, -- Direct quote if applicable
    evidence TEXT, -- Full context
    
    -- Quality scoring
    quality_score INTEGER NOT NULL CHECK (quality_score BETWEEN 1 AND 5), -- 1=weak, 5=direct buying signal
    impact_level VARCHAR(50) NOT NULL, -- high, medium, low
    
    -- Signal decay tracking
    detected_at TIMESTAMP NOT NULL, -- When signal was found
    
    -- Campaign impact
    influenced_campaign_id BIGINT REFERENCES campaigns(id), -- If this signal led to a campaign
    confirmed_in_campaign BOOLEAN DEFAULT false, -- If campaign validated this pain
    
    -- Deduplication
    fingerprint VARCHAR(255), -- Hash of (source_url + summary) for dedup
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_niche_signals_niche ON niche_signals(niche_id);
CREATE INDEX idx_niche_signals_slug ON niche_signals(niche_slug);
CREATE INDEX idx_niche_signals_type ON niche_signals(signal_type);
CREATE INDEX idx_niche_signals_quality ON niche_signals(quality_score DESC);
CREATE INDEX idx_niche_signals_detected ON niche_signals(detected_at DESC);
CREATE INDEX idx_niche_signals_fingerprint ON niche_signals(fingerprint);
CREATE UNIQUE INDEX idx_niche_signals_dedup ON niche_signals(niche_id, fingerprint);

COMMENT ON TABLE niche_signals IS 'Individual niche signals with decay tracking (calculated via view/function)';

-- ============================================================================

-- 7. NICHE SCAN LOG
-- Daily/weekly scan performance logging
CREATE TABLE niche_scan_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- Scan metadata
    scan_date DATE NOT NULL,
    scan_mode VARCHAR(50) NOT NULL, -- daily_scan, deep_scout
    duration_minutes INTEGER,
    
    -- Scan scope
    niches_scanned JSONB, -- ["dental-medspas", "ecommerce-dtc"]
    niches_count INTEGER,
    
    -- Discovery results
    new_niches_discovered INTEGER DEFAULT 0,
    new_signals_found INTEGER DEFAULT 0,
    high_viability_alerts INTEGER DEFAULT 0,
    
    -- Detailed results
    discoveries JSONB, 
    -- [{niche: "new-niche", viability: 8.2, action: "campaign_prep"}, ...]
    
    signals_summary JSONB,
    -- [{niche: "dental-medspas", signal_type: "pain_thread", quality: 4, impact: "medium"}, ...]
    
    campaign_cross_ref JSONB,
    -- [{niche: "dental-medspas", reply_rate: 4.2, status: "healthy"}, ...]
    
    -- Alerts generated
    alerts_sent JSONB,
    -- [{niche: "...", alert_type: "high_viability", message: "..."}, ...]
    
    -- Performance
    search_queries_executed INTEGER,
    reddit_threads_analyzed INTEGER,
    sources_checked JSONB, -- ["Brave", "Perplexity", "Reddit", "Indeed"]
    
    -- Status
    status VARCHAR(50) DEFAULT 'completed', -- completed, failed, partial
    errors JSONB,
    
    -- Report output
    report_doc_id VARCHAR(255), -- Google Doc ID if report generated
    report_url TEXT,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_niche_scan_date ON niche_scan_log(scan_date DESC);
CREATE INDEX idx_niche_scan_mode ON niche_scan_log(scan_mode);
CREATE INDEX idx_niche_scan_status ON niche_scan_log(status);
CREATE INDEX idx_niche_scan_discoveries ON niche_scan_log(new_niches_discovered) WHERE new_niches_discovered > 0;

COMMENT ON TABLE niche_scan_log IS 'Daily and weekly niche scouting scan logs';

-- ============================================================================

-- 8. LEAD ENRICHMENT LOG
-- Waterfall enrichment tracking (7 providers: Reoon→Tomba→AnyMailFinder→Icypeas→VoilaNorbert→Nimbler→Muraena)
CREATE TABLE lead_enrichment_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- Lead identification
    lead_id BIGINT REFERENCES leads(id),
    company_name VARCHAR(255),
    person_name VARCHAR(255),
    linkedin_url TEXT,
    
    -- Enrichment cascade
    providers_attempted JSONB, -- ["reoon", "tomba", "anymailfinder"]
    successful_provider VARCHAR(50), -- which provider found the email
    cascade_depth INTEGER, -- how many providers tried before success (1-7)
    
    -- Results
    email_found VARCHAR(255),
    phone_found VARCHAR(50),
    additional_data JSONB, -- job title, company size, tech stack, etc.
    
    -- Verification
    email_verified BOOLEAN,
    verification_score INTEGER, -- 0-100
    verification_provider VARCHAR(50),
    
    -- Performance
    total_duration_ms INTEGER,
    cost_credits DECIMAL(10,4), -- cost in API credits
    
    -- Status
    status VARCHAR(50) NOT NULL, -- success, partial, failed, skipped
    failure_reason TEXT,
    
    -- Timestamps
    enriched_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lead_enrichment_lead ON lead_enrichment_log(lead_id);
CREATE INDEX idx_lead_enrichment_provider ON lead_enrichment_log(successful_provider);
CREATE INDEX idx_lead_enrichment_status ON lead_enrichment_log(status);
CREATE INDEX idx_lead_enrichment_date ON lead_enrichment_log(enriched_at DESC);

COMMENT ON TABLE lead_enrichment_log IS 'Waterfall email enrichment tracking across 7 providers';

-- ============================================================================

-- 9. CAMPAIGN ANALYTICS SNAPSHOT
-- Daily snapshots of campaign performance for trend analysis
CREATE TABLE campaign_analytics_snapshot (
    id BIGSERIAL PRIMARY KEY,
    
    -- Campaign
    campaign_id BIGINT REFERENCES campaigns(id),
    campaign_name VARCHAR(255),
    
    -- Daily metrics
    date DATE NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    emails_delivered INTEGER DEFAULT 0,
    emails_opened INTEGER DEFAULT 0,
    emails_replied INTEGER DEFAULT 0,
    emails_bounced INTEGER DEFAULT 0,
    emails_unsubscribed INTEGER DEFAULT 0,
    
    -- Rates
    delivery_rate DECIMAL(5,2),
    open_rate DECIMAL(5,2),
    reply_rate DECIMAL(5,2),
    bounce_rate DECIMAL(5,2),
    unsubscribe_rate DECIMAL(5,2),
    
    -- Lead quality
    qualified_leads INTEGER DEFAULT 0,
    meetings_booked INTEGER DEFAULT 0,
    
    -- Cost tracking
    cost_per_send DECIMAL(10,4),
    cost_per_reply DECIMAL(10,4),
    cost_per_meeting DECIMAL(10,4),
    
    -- Cumulative totals
    cumulative_sent INTEGER,
    cumulative_replies INTEGER,
    cumulative_meetings INTEGER,
    
    -- Timestamps
    snapshot_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_campaign_analytics_campaign ON campaign_analytics_snapshot(campaign_id);
CREATE INDEX idx_campaign_analytics_date ON campaign_analytics_snapshot(date DESC);
CREATE UNIQUE INDEX idx_campaign_analytics_unique ON campaign_analytics_snapshot(campaign_id, date);

COMMENT ON TABLE campaign_analytics_snapshot IS 'Daily campaign performance snapshots for trend analysis';

-- ============================================================================
-- MODIFY EXISTING TABLES
-- ============================================================================

-- LEADS table enhancements
ALTER TABLE leads ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS instantly_lead_id VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS warmup_status VARCHAR(50); -- new, contacted, replied, qualified, dead
ALTER TABLE leads ADD COLUMN IF NOT EXISTS enrichment_provider VARCHAR(50); -- reoon, tomba, etc.
ALTER TABLE leads ADD COLUMN IF NOT EXISTS enrichment_date TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_contacted_at TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS reply_count INTEGER DEFAULT 0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS bounce_reason TEXT;

CREATE INDEX IF NOT EXISTS idx_leads_email_verified ON leads(email_verified);
CREATE INDEX IF NOT EXISTS idx_leads_warmup_status ON leads(warmup_status);
CREATE INDEX IF NOT EXISTS idx_leads_instantly_id ON leads(instantly_lead_id);

COMMENT ON COLUMN leads.email_verified IS 'Email verification status from enrichment';
COMMENT ON COLUMN leads.instantly_lead_id IS 'Instantly.ai lead ID for sync';
COMMENT ON COLUMN leads.warmup_status IS 'Lead engagement stage in cold email sequence';
COMMENT ON COLUMN leads.enrichment_provider IS 'Which provider found the email';

-- ============================================================================

-- CAMPAIGNS table enhancements
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS instantly_campaign_id VARCHAR(255);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS daily_send_limit INTEGER DEFAULT 50;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS warmup_enabled BOOLEAN DEFAULT true;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS sequence_id BIGINT REFERENCES email_sequences(id);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS niche_id BIGINT REFERENCES niche_research(id);
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS target_reply_rate DECIMAL(5,2); -- goal
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS auto_optimize BOOLEAN DEFAULT false;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS optimization_rules JSONB; -- [{condition: "reply_rate < 2", action: "pause"}, ...]

CREATE INDEX IF NOT EXISTS idx_campaigns_instantly_id ON campaigns(instantly_campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_sequence ON campaigns(sequence_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_niche ON campaigns(niche_id);

COMMENT ON COLUMN campaigns.instantly_campaign_id IS 'Instantly.ai campaign ID for sync';
COMMENT ON COLUMN campaigns.sequence_id IS 'Email sequence used in this campaign';
COMMENT ON COLUMN campaigns.niche_id IS 'Niche research this campaign targets';
COMMENT ON COLUMN campaigns.auto_optimize IS 'Whether campaign self-optimizes based on rules';

-- ============================================================================

-- COMMUNICATIONS table enhancements
ALTER TABLE communications ADD COLUMN IF NOT EXISTS instantly_message_id VARCHAR(255);
ALTER TABLE communications ADD COLUMN IF NOT EXISTS bounce_type VARCHAR(50); -- hard, soft, complaint
ALTER TABLE communications ADD COLUMN IF NOT EXISTS spam_score DECIMAL(5,2);
ALTER TABLE communications ADD COLUMN IF NOT EXISTS email_opened BOOLEAN DEFAULT false;
ALTER TABLE communications ADD COLUMN IF NOT EXISTS opened_at TIMESTAMP;
ALTER TABLE communications ADD COLUMN IF NOT EXISTS replied BOOLEAN DEFAULT false;
ALTER TABLE communications ADD COLUMN IF NOT EXISTS replied_at TIMESTAMP;
ALTER TABLE communications ADD COLUMN IF NOT EXISTS reply_sentiment VARCHAR(50); -- positive, neutral, negative, qualified
ALTER TABLE communications ADD COLUMN IF NOT EXISTS template_id BIGINT REFERENCES email_templates(id);
ALTER TABLE communications ADD COLUMN IF NOT EXISTS sequence_step INTEGER; -- which step in sequence (1, 2, 3, etc.)

CREATE INDEX IF NOT EXISTS idx_communications_instantly_id ON communications(instantly_message_id);
CREATE INDEX IF NOT EXISTS idx_communications_template ON communications(template_id);
CREATE INDEX IF NOT EXISTS idx_communications_opened ON communications(email_opened);
CREATE INDEX IF NOT EXISTS idx_communications_replied ON communications(replied);

COMMENT ON COLUMN communications.instantly_message_id IS 'Instantly.ai message ID for sync';
COMMENT ON COLUMN communications.template_id IS 'Email template used for this message';
COMMENT ON COLUMN communications.reply_sentiment IS 'Sentiment analysis of reply (if received)';
COMMENT ON COLUMN communications.sequence_step IS 'Which step in email sequence this message represents';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Get active campaigns with low reply rates (needs attention)
CREATE OR REPLACE FUNCTION get_low_performing_campaigns(threshold DECIMAL DEFAULT 2.0)
RETURNS TABLE (
    campaign_id BIGINT,
    campaign_name VARCHAR,
    reply_rate DECIMAL,
    emails_sent INTEGER,
    niche_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        es.reply_rate,
        es.total_sent,
        nr.niche_name
    FROM campaigns c
    LEFT JOIN email_sequences es ON c.sequence_id = es.id
    LEFT JOIN niche_research nr ON c.niche_id = nr.id
    WHERE c.status = 'active'
    AND es.reply_rate < threshold
    AND es.total_sent > 100
    ORDER BY es.reply_rate ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_low_performing_campaigns IS 'Find active campaigns with reply rates below threshold';

-- ============================================================================

-- Get niches ready for campaign prep (high viability, not yet launched)
CREATE OR REPLACE FUNCTION get_campaign_ready_niches()
RETURNS TABLE (
    niche_id BIGINT,
    niche_name VARCHAR,
    viability_score DECIMAL,
    pain_summary TEXT,
    estimated_list_size INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        niche_name,
        viability_score,
        pain_summary,
        estimated_list_size
    FROM niche_research
    WHERE ready_for_campaign = true
    AND campaign_created = false
    AND retired = false
    AND viability_score >= 8.0
    ORDER BY viability_score DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_campaign_ready_niches IS 'Get high-viability niches ready for campaign creation';

-- ============================================================================

-- Get fresh signals for a niche (not stale, quality 3+)
CREATE OR REPLACE FUNCTION get_fresh_signals(niche_slug_param VARCHAR)
RETURNS TABLE (
    signal_id BIGINT,
    signal_type VARCHAR,
    summary TEXT,
    quality_score INTEGER,
    detected_at TIMESTAMP,
    age_days NUMERIC,
    decay_weight NUMERIC,
    stale BOOLEAN,
    source_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ns.id,
        ns.signal_type,
        ns.summary,
        ns.quality_score,
        ns.detected_at,
        EXTRACT(EPOCH FROM (NOW() - ns.detected_at)) / 86400 AS age_days,
        CASE 
            WHEN EXTRACT(EPOCH FROM (NOW() - ns.detected_at)) / 86400 <= 7 THEN 1.00
            WHEN EXTRACT(EPOCH FROM (NOW() - ns.detected_at)) / 86400 <= 30 THEN 0.75
            WHEN EXTRACT(EPOCH FROM (NOW() - ns.detected_at)) / 86400 <= 90 THEN 0.50
            ELSE 0.25
        END AS decay_weight,
        EXTRACT(EPOCH FROM (NOW() - ns.detected_at)) / 86400 > 90 AS stale,
        ns.source_url
    FROM niche_signals ns
    WHERE ns.niche_slug = niche_slug_param
    AND EXTRACT(EPOCH FROM (NOW() - ns.detected_at)) / 86400 <= 90
    AND ns.quality_score >= 3
    ORDER BY ns.quality_score DESC, ns.detected_at DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_fresh_signals IS 'Get fresh (non-stale), high-quality signals with calculated decay for a niche';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Niche signals with decay calculation
CREATE OR REPLACE VIEW niche_signals_with_decay AS
SELECT 
    id,
    niche_id,
    niche_slug,
    signal_type,
    source,
    source_url,
    summary,
    quote,
    evidence,
    quality_score,
    impact_level,
    detected_at,
    EXTRACT(EPOCH FROM (NOW() - detected_at)) / 86400 AS age_days,
    CASE 
        WHEN EXTRACT(EPOCH FROM (NOW() - detected_at)) / 86400 <= 7 THEN 1.00
        WHEN EXTRACT(EPOCH FROM (NOW() - detected_at)) / 86400 <= 30 THEN 0.75
        WHEN EXTRACT(EPOCH FROM (NOW() - detected_at)) / 86400 <= 90 THEN 0.50
        ELSE 0.25
    END AS decay_weight,
    EXTRACT(EPOCH FROM (NOW() - detected_at)) / 86400 > 90 AS stale,
    influenced_campaign_id,
    confirmed_in_campaign,
    fingerprint,
    created_at,
    updated_at
FROM niche_signals;

COMMENT ON VIEW niche_signals_with_decay IS 'Niche signals with calculated age, decay weight, and stale status';

-- ============================================================================

-- Campaign performance summary view
CREATE OR REPLACE VIEW campaign_performance_summary AS
SELECT 
    c.id AS campaign_id,
    c.name AS campaign_name,
    c.status,
    es.reply_rate,
    es.open_rate,
    es.bounce_rate,
    es.total_sent,
    es.total_replied,
    nr.niche_name,
    nr.viability_score AS niche_viability,
    CASE 
        WHEN es.reply_rate >= c.target_reply_rate THEN 'meeting_goal'
        WHEN es.reply_rate >= (c.target_reply_rate * 0.75) THEN 'near_goal'
        WHEN es.reply_rate < 1.0 THEN 'critical'
        ELSE 'needs_attention'
    END AS performance_status
FROM campaigns c
LEFT JOIN email_sequences es ON c.sequence_id = es.id
LEFT JOIN niche_research nr ON c.niche_id = nr.id
WHERE c.deleted_at IS NULL;

COMMENT ON VIEW campaign_performance_summary IS 'Campaign performance overview with goal tracking';

-- ============================================================================

-- Deliverability health dashboard
CREATE OR REPLACE VIEW deliverability_health_dashboard AS
SELECT 
    email_account,
    domain,
    warmup_stage,
    bounce_rate,
    spam_complaint_rate,
    sender_score,
    domain_reputation,
    blacklisted,
    alert_level,
    measured_at
FROM deliverability_metrics
WHERE measured_at >= NOW() - INTERVAL '7 days'
ORDER BY alert_level DESC, measured_at DESC;

COMMENT ON VIEW deliverability_health_dashboard IS 'Recent deliverability health across all sending accounts';

-- ============================================================================

-- Niche pipeline overview
CREATE OR REPLACE VIEW niche_pipeline_overview AS
SELECT 
    lifecycle_stage,
    COUNT(*) AS niche_count,
    AVG(viability_score) AS avg_viability,
    SUM(CASE WHEN alert_level != 'normal' THEN 1 ELSE 0 END) AS niches_with_alerts,
    SUM(campaigns_launched) AS total_campaigns,
    AVG(avg_reply_rate) AS avg_reply_rate
FROM niche_research
WHERE retired = false
AND deleted_at IS NULL
GROUP BY lifecycle_stage
ORDER BY 
    CASE lifecycle_stage
        WHEN 'active_campaign' THEN 1
        WHEN 'campaign_prep' THEN 2
        WHEN 'researching' THEN 3
        WHEN 'discovered' THEN 4
        WHEN 'mature' THEN 5
        ELSE 6
    END;

COMMENT ON VIEW niche_pipeline_overview IS 'Niche research pipeline summary by lifecycle stage';

-- ============================================================================
-- END MIGRATION
-- ============================================================================

-- Migration complete: Qamar's cold email infrastructure operational
-- 9 new tables created
-- 3 existing tables enhanced
-- 3 helper functions added
-- 3 views created
