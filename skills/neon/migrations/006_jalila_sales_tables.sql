-- Migration 006: Jalila Sales Infrastructure
-- Agent: Jalila — Sales Specialist
-- Purpose: Complete sales lifecycle tracking - proposals, calls, transcripts, interactions, competitors, close plans, win/loss
-- Created: 2026-02-23

-- ============================================================================
-- NEW TABLES (13)
-- ============================================================================

-- 1. SALES PROPOSALS
-- Track proposals from creation to signature with version history
CREATE TABLE sales_proposals (
    id BIGSERIAL PRIMARY KEY,
    
    -- Deal association
    deal_id BIGINT REFERENCES deals(id),
    lead_id BIGINT REFERENCES leads(id),
    company_id BIGINT REFERENCES companies(id),
    
    -- Proposal identification
    proposal_number VARCHAR(50) UNIQUE, -- e.g., "PROP-2026-001"
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- PandaDoc integration
    pandadoc_document_id VARCHAR(255),
    pandadoc_status VARCHAR(50), -- draft, sent, viewed, completed, declined
    pandadoc_url TEXT,
    
    -- Proposal content
    service_lines JSONB, -- [{"service": "AI Automation", "price": 12000, "description": "..."}]
    total_value DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    payment_terms VARCHAR(50), -- upfront, 50-50, monthly
    delivery_timeline VARCHAR(255),
    
    -- Discount/negotiation
    original_value DECIMAL(12,2),
    discount_amount DECIMAL(12,2),
    discount_reason TEXT,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'draft', 
    -- draft, sent, viewed, under_review, negotiating, accepted, declined, expired
    
    sent_at TIMESTAMP,
    first_viewed_at TIMESTAMP,
    last_viewed_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    signed_at TIMESTAMP,
    declined_at TIMESTAMP,
    expired_at TIMESTAMP,
    
    -- Follow-up tracking
    follow_ups_sent INTEGER DEFAULT 0,
    last_followup_at TIMESTAMP,
    next_followup_due TIMESTAMP,
    
    -- Engagement
    time_to_first_view_hours INTEGER,
    time_to_signature_hours INTEGER,
    
    -- Version control
    version INTEGER DEFAULT 1,
    parent_proposal_id BIGINT REFERENCES sales_proposals(id),
    superseded_by_id BIGINT REFERENCES sales_proposals(id),
    
    -- Notes
    internal_notes TEXT,
    client_feedback TEXT,
    
    -- Files
    google_drive_folder_id VARCHAR(255),
    gamma_presentation_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_proposals_deal ON sales_proposals(deal_id);
CREATE INDEX idx_proposals_lead ON sales_proposals(lead_id);
CREATE INDEX idx_proposals_company ON sales_proposals(company_id);
CREATE INDEX idx_proposals_status ON sales_proposals(status);
CREATE INDEX idx_proposals_pandadoc_id ON sales_proposals(pandadoc_document_id);
CREATE INDEX idx_proposals_sent ON sales_proposals(sent_at DESC);
CREATE INDEX idx_proposals_followup_due ON sales_proposals(next_followup_due) WHERE next_followup_due IS NOT NULL;

COMMENT ON TABLE sales_proposals IS 'Sales proposals with PandaDoc integration and tracking';

-- ============================================================================

-- 2. SALES CALLS
-- Track discovery and sales calls with prep, notes, outcomes, and transcripts
CREATE TABLE sales_calls (
    id BIGSERIAL PRIMARY KEY,
    
    -- Deal/Lead association
    deal_id BIGINT REFERENCES deals(id),
    lead_id BIGINT REFERENCES leads(id),
    meeting_id BIGINT REFERENCES meetings(id),
    
    -- Call details
    call_type VARCHAR(50) NOT NULL, 
    -- discovery, demo, follow_up, negotiation, objection_handling, close
    
    call_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER,
    
    -- Attendees
    attendees JSONB, -- [{name, email, role, company}]
    decision_maker_present BOOLEAN DEFAULT false,
    
    -- Prep materials
    prep_doc_url TEXT,
    gamma_presentation_url TEXT,
    autobound_insights JSONB,
    
    -- Call outcome
    call_happened BOOLEAN DEFAULT true,
    no_show BOOLEAN DEFAULT false,
    rescheduled BOOLEAN DEFAULT false,
    reschedule_reason TEXT,
    
    -- Discovery insights (BANT)
    budget_discussed BOOLEAN DEFAULT false,
    budget_range VARCHAR(50),
    authority_identified BOOLEAN DEFAULT false,
    decision_maker_name VARCHAR(255),
    need_identified BOOLEAN DEFAULT false,
    pain_points JSONB,
    timeline_discussed BOOLEAN DEFAULT false,
    timeline_estimate VARCHAR(50),
    
    -- Competitor intelligence
    competitors_mentioned JSONB, -- [{competitor, context, why_considering, our_positioning}]
    
    -- Next steps
    next_steps TEXT,
    proposal_needed BOOLEAN DEFAULT false,
    demo_requested BOOLEAN DEFAULT false,
    follow_up_call_scheduled BOOLEAN DEFAULT false,
    
    -- Call notes
    call_notes TEXT,
    key_takeaways JSONB,
    objections_raised JSONB,
    action_items JSONB, -- [{item, owner, due_date, completed}]
    
    -- Scoring
    qualification_score INTEGER,
    interest_level VARCHAR(50),
    close_probability DECIMAL(5,2),
    
    -- Recording & transcript
    recording_url TEXT,
    transcript_url TEXT,
    transcript_text TEXT,
    ai_summary TEXT,
    
    -- Follow-up
    follow_up_sent BOOLEAN DEFAULT false,
    follow_up_sent_at TIMESTAMP,
    follow_up_promises JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_sales_calls_deal ON sales_calls(deal_id);
CREATE INDEX idx_sales_calls_lead ON sales_calls(lead_id);
CREATE INDEX idx_sales_calls_meeting ON sales_calls(meeting_id);
CREATE INDEX idx_sales_calls_type ON sales_calls(call_type);
CREATE INDEX idx_sales_calls_date ON sales_calls(call_date DESC);
CREATE INDEX idx_sales_calls_no_show ON sales_calls(no_show) WHERE no_show = true;
CREATE INDEX idx_sales_calls_qualification ON sales_calls(qualification_score DESC);
CREATE INDEX idx_sales_calls_followup_needed ON sales_calls(follow_up_sent) WHERE follow_up_sent = false AND call_happened = true;

COMMENT ON TABLE sales_calls IS 'Discovery and sales calls with prep, notes, outcomes, and transcripts';

-- ============================================================================

-- 3. OBJECTIONS LIBRARY
-- Track common objections and winning responses
CREATE TABLE objections_library (
    id BIGSERIAL PRIMARY KEY,
    
    objection_category VARCHAR(50) NOT NULL,
    objection_text TEXT NOT NULL,
    objection_frequency INTEGER DEFAULT 0,
    
    response_text TEXT NOT NULL,
    response_type VARCHAR(50),
    
    case_study_link TEXT,
    data_point TEXT,
    testimonial_quote TEXT,
    
    times_used INTEGER DEFAULT 0,
    times_successful INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    
    best_for_deal_size VARCHAR(50),
    best_for_industry JSONB,
    
    status VARCHAR(50) DEFAULT 'active',
    is_winning_response BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_objections_category ON objections_library(objection_category);
CREATE INDEX idx_objections_frequency ON objections_library(objection_frequency DESC);
CREATE INDEX idx_objections_success_rate ON objections_library(success_rate DESC);
CREATE INDEX idx_objections_status ON objections_library(status);
CREATE INDEX idx_objections_winning ON objections_library(is_winning_response) WHERE is_winning_response = true;

COMMENT ON TABLE objections_library IS 'Common sales objections and winning responses';

-- ============================================================================

-- 4. DEAL STAGES
-- Custom deal pipeline stages with conversion tracking
CREATE TABLE deal_stages (
    id BIGSERIAL PRIMARY KEY,
    
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    
    stage_order INTEGER NOT NULL,
    
    is_active BOOLEAN DEFAULT true,
    is_closed_won BOOLEAN DEFAULT false,
    is_closed_lost BOOLEAN DEFAULT false,
    
    required_actions JSONB,
    typical_duration_days INTEGER,
    
    deals_entered INTEGER DEFAULT 0,
    deals_exited INTEGER DEFAULT 0,
    deals_currently_in INTEGER DEFAULT 0,
    avg_days_in_stage DECIMAL(6,2),
    
    conversion_rate_to_next DECIMAL(5,2),
    drop_off_rate DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_deal_stages_order ON deal_stages(stage_order);
CREATE INDEX idx_deal_stages_active ON deal_stages(is_active) WHERE is_active = true;

COMMENT ON TABLE deal_stages IS 'Custom deal pipeline stages with conversion metrics';

-- ============================================================================

-- 5. DEAL STAGE HISTORY
-- Track when deals move between stages for velocity analysis
CREATE TABLE deal_stage_history (
    id BIGSERIAL PRIMARY KEY,
    
    deal_id BIGINT REFERENCES deals(id),
    
    from_stage_id BIGINT REFERENCES deal_stages(id),
    to_stage_id BIGINT REFERENCES deal_stages(id),
    
    from_stage_name VARCHAR(100),
    to_stage_name VARCHAR(100),
    
    entered_at TIMESTAMP NOT NULL,
    exited_at TIMESTAMP,
    duration_days DECIMAL(6,2),
    
    movement_reason VARCHAR(50),
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_deal_stage_history_deal ON deal_stage_history(deal_id);
CREATE INDEX idx_deal_stage_history_from ON deal_stage_history(from_stage_id);
CREATE INDEX idx_deal_stage_history_to ON deal_stage_history(to_stage_id);
CREATE INDEX idx_deal_stage_history_entered ON deal_stage_history(entered_at DESC);

COMMENT ON TABLE deal_stage_history IS 'Deal movement through pipeline stages';

-- ============================================================================

-- 6. CLIENT HANDOFFS
-- Track handoffs from Jalila (sales) to Huda (client success)
CREATE TABLE client_handoffs (
    id BIGSERIAL PRIMARY KEY,
    
    deal_id BIGINT REFERENCES deals(id),
    client_id BIGINT, -- Note: clients table uses UUID client_id, not BIGINT id
    
    handoff_date TIMESTAMP NOT NULL,
    from_agent VARCHAR(50) DEFAULT 'Jalila',
    to_agent VARCHAR(50) DEFAULT 'Huda',
    
    client_summary TEXT NOT NULL,
    promised_deliverables JSONB,
    timeline_expectations TEXT,
    special_requests JSONB,
    
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    decision_maker_name VARCHAR(255),
    
    pain_points_solved JSONB,
    objections_overcome JSONB,
    pricing_agreed DECIMAL(12,2),
    contract_terms TEXT,
    
    onboarding_doc_url TEXT,
    kick_off_call_scheduled BOOLEAN DEFAULT false,
    kick_off_date TIMESTAMP,
    
    things_to_know TEXT,
    red_flags TEXT,
    
    handoff_acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP,
    onboarding_started BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_client_handoffs_deal ON client_handoffs(deal_id);
CREATE INDEX idx_client_handoffs_client ON client_handoffs(client_id);
CREATE INDEX idx_client_handoffs_date ON client_handoffs(handoff_date DESC);
CREATE INDEX idx_client_handoffs_acknowledged ON client_handoffs(handoff_acknowledged) WHERE handoff_acknowledged = false;

COMMENT ON TABLE client_handoffs IS 'Sales-to-success handoffs with full context';

-- ============================================================================

-- 7. DEAL ACTIVITY LOG
-- Real-time activity feed for every deal (audit trail + timeline)
CREATE TABLE deal_activity_log (
    id BIGSERIAL PRIMARY KEY,
    
    deal_id BIGINT REFERENCES deals(id),
    
    activity_type VARCHAR(50) NOT NULL,
    activity_description TEXT NOT NULL,
    
    related_call_id BIGINT REFERENCES sales_calls(id),
    related_proposal_id BIGINT REFERENCES sales_proposals(id),
    related_communication_id BIGINT REFERENCES communications(id),
    
    actor VARCHAR(100),
    automated BOOLEAN DEFAULT false,
    
    deal_value_changed DECIMAL(12,2),
    stage_changed_from VARCHAR(100),
    stage_changed_to VARCHAR(100),
    close_probability_changed DECIMAL(5,2),
    
    activity_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_deal_activity_deal ON deal_activity_log(deal_id);
CREATE INDEX idx_deal_activity_type ON deal_activity_log(activity_type);
CREATE INDEX idx_deal_activity_date ON deal_activity_log(activity_at DESC);
CREATE INDEX idx_deal_activity_actor ON deal_activity_log(actor);

COMMENT ON TABLE deal_activity_log IS 'Complete activity timeline for every deal';

-- ============================================================================

-- 8. SALES INTERACTIONS
-- Track every touchpoint with clients/prospects (separate from existing client_interactions)
CREATE TABLE sales_interactions (
    id BIGSERIAL PRIMARY KEY,
    
    client_id BIGINT, -- Note: clients table uses UUID client_id, not BIGINT id
    lead_id BIGINT REFERENCES leads(id),
    deal_id BIGINT REFERENCES deals(id),
    
    interaction_type VARCHAR(50) NOT NULL,
    interaction_date TIMESTAMP NOT NULL,
    
    subject TEXT,
    summary TEXT NOT NULL,
    sentiment VARCHAR(50),
    
    value_type VARCHAR(50),
    value_description TEXT,
    
    action_items JSONB,
    promises_made JSONB,
    
    follow_up_needed BOOLEAN DEFAULT false,
    follow_up_due TIMESTAMP,
    follow_up_completed BOOLEAN DEFAULT false,
    
    communication_id BIGINT REFERENCES communications(id),
    call_id BIGINT REFERENCES sales_calls(id),
    
    handled_by VARCHAR(50) DEFAULT 'Jalila',
    
    internal_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sales_interactions_client ON sales_interactions(client_id);
CREATE INDEX idx_sales_interactions_lead ON sales_interactions(lead_id);
CREATE INDEX idx_sales_interactions_deal ON sales_interactions(deal_id);
CREATE INDEX idx_sales_interactions_type ON sales_interactions(interaction_type);
CREATE INDEX idx_sales_interactions_date ON sales_interactions(interaction_date DESC);
CREATE INDEX idx_sales_interactions_sentiment ON sales_interactions(sentiment);
CREATE INDEX idx_sales_interactions_followup ON sales_interactions(follow_up_needed) WHERE follow_up_needed = true;

COMMENT ON TABLE sales_interactions IS 'Every touchpoint with clients and prospects (Jalila)';

-- ============================================================================

-- 9. PAIN POINTS LIBRARY
-- Structured pain points by industry with solution mapping
CREATE TABLE pain_points_library (
    id BIGSERIAL PRIMARY KEY,
    
    pain_point TEXT NOT NULL,
    pain_category VARCHAR(50),
    
    common_in_industry JSONB,
    common_for_company_size VARCHAR(50),
    frequency_count INTEGER DEFAULT 0,
    
    severity VARCHAR(50),
    urgency VARCHAR(50),
    
    solved_by_service_line VARCHAR(100),
    solution_description TEXT,
    typical_roi VARCHAR(100),
    
    case_study_links JSONB,
    testimonial_quote TEXT,
    demo_script_url TEXT,
    
    times_addressed INTEGER DEFAULT 0,
    times_closed_deal INTEGER DEFAULT 0,
    close_rate DECIMAL(5,2),
    
    status VARCHAR(50) DEFAULT 'active',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pain_points_category ON pain_points_library(pain_category);
CREATE INDEX idx_pain_points_frequency ON pain_points_library(frequency_count DESC);
CREATE INDEX idx_pain_points_close_rate ON pain_points_library(close_rate DESC);
CREATE INDEX idx_pain_points_service_line ON pain_points_library(solved_by_service_line);

COMMENT ON TABLE pain_points_library IS 'Structured pain points with solution mapping';

-- ============================================================================

-- 10. COMPETITOR INTELLIGENCE
-- Track competitor mentions and how we position against them
CREATE TABLE competitor_intelligence (
    id BIGSERIAL PRIMARY KEY,
    
    competitor_name VARCHAR(255) NOT NULL,
    competitor_website TEXT,
    competitor_category VARCHAR(50),
    
    deal_id BIGINT REFERENCES deals(id),
    call_id BIGINT REFERENCES sales_calls(id),
    
    mentioned_date TIMESTAMP NOT NULL,
    mentioned_by VARCHAR(255),
    
    why_considering TEXT,
    what_they_like TEXT,
    what_concerns_them TEXT,
    
    their_pricing VARCHAR(255),
    their_strengths JSONB,
    their_weaknesses JSONB,
    
    how_we_positioned TEXT,
    positioning_worked BOOLEAN,
    
    won_against BOOLEAN,
    lost_to BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_competitor_intel_competitor ON competitor_intelligence(competitor_name);
CREATE INDEX idx_competitor_intel_deal ON competitor_intelligence(deal_id);
CREATE INDEX idx_competitor_intel_call ON competitor_intelligence(call_id);
CREATE INDEX idx_competitor_intel_date ON competitor_intelligence(mentioned_date DESC);

COMMENT ON TABLE competitor_intelligence IS 'Competitor mentions and positioning intelligence';

-- ============================================================================

-- 11. CLOSE PLANS
-- Multi-step close plans for deals in negotiation
CREATE TABLE close_plans (
    id BIGSERIAL PRIMARY KEY,
    
    deal_id BIGINT REFERENCES deals(id) UNIQUE,
    
    target_close_date DATE,
    confidence_level VARCHAR(50),
    
    steps_to_close JSONB,
    blockers JSONB,
    
    champions JSONB,
    decision_makers JSONB,
    
    budget_approval_process TEXT,
    budget_approved BOOLEAN DEFAULT false,
    budget_approval_date DATE,
    
    legal_review_needed BOOLEAN DEFAULT false,
    legal_review_complete BOOLEAN DEFAULT false,
    contract_redlines JSONB,
    
    risk_factors JSONB,
    
    plan_status VARCHAR(50) DEFAULT 'active',
    
    notes TEXT,
    last_updated_by VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_close_plans_deal ON close_plans(deal_id);
CREATE INDEX idx_close_plans_target_date ON close_plans(target_close_date);
CREATE INDEX idx_close_plans_status ON close_plans(plan_status);

COMMENT ON TABLE close_plans IS 'Detailed close plans for deals in negotiation';

-- ============================================================================

-- 12. WIN LOSS ANALYSIS
-- Capture why deals were won or lost
CREATE TABLE win_loss_analysis (
    id BIGSERIAL PRIMARY KEY,
    
    deal_id BIGINT REFERENCES deals(id) UNIQUE,
    
    outcome VARCHAR(50) NOT NULL,
    closed_date DATE NOT NULL,
    
    primary_win_reason VARCHAR(100),
    secondary_win_reasons JSONB,
    what_went_well TEXT,
    
    primary_loss_reason VARCHAR(100),
    secondary_loss_reasons JSONB,
    what_could_improve TEXT,
    
    competitor_chosen VARCHAR(255),
    why_competitor_won TEXT,
    
    prospect_feedback TEXT,
    would_consider_future BOOLEAN,
    
    deal_value_at_close DECIMAL(12,2),
    sales_cycle_days INTEGER,
    
    lessons_learned TEXT,
    process_improvements JSONB,
    
    referral_opportunity BOOLEAN DEFAULT false,
    case_study_candidate BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_win_loss_deal ON win_loss_analysis(deal_id);
CREATE INDEX idx_win_loss_outcome ON win_loss_analysis(outcome);
CREATE INDEX idx_win_loss_date ON win_loss_analysis(closed_date DESC);
CREATE INDEX idx_win_loss_primary_reason ON win_loss_analysis(primary_win_reason, primary_loss_reason);

COMMENT ON TABLE win_loss_analysis IS 'Win/loss analysis for closed deals';

-- ============================================================================

-- 13. MEETING PREP INTELLIGENCE
-- Store structured meeting prep data (Autobound, research, LinkedIn)
CREATE TABLE meeting_prep_intelligence (
    id BIGSERIAL PRIMARY KEY,
    
    meeting_id BIGINT REFERENCES meetings(id),
    lead_id BIGINT REFERENCES leads(id),
    company_id BIGINT REFERENCES companies(id),
    
    autobound_contact_data JSONB,
    autobound_company_data JSONB,
    autobound_signals JSONB,
    
    linkedin_recent_posts JSONB,
    linkedin_activity_summary TEXT,
    linkedin_connections_in_common JSONB,
    
    company_recent_news JSONB,
    funding_history JSONB,
    tech_stack JSONB,
    hiring_signals JSONB,
    
    icebreakers JSONB,
    pain_points_identified JSONB,
    value_propositions JSONB,
    
    prep_doc_url TEXT,
    gamma_presentation_url TEXT,
    
    prep_completeness_score INTEGER,
    
    researched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_meeting_prep_meeting ON meeting_prep_intelligence(meeting_id);
CREATE INDEX idx_meeting_prep_lead ON meeting_prep_intelligence(lead_id);
CREATE INDEX idx_meeting_prep_company ON meeting_prep_intelligence(company_id);
CREATE INDEX idx_meeting_prep_date ON meeting_prep_intelligence(researched_at DESC);

COMMENT ON TABLE meeting_prep_intelligence IS 'Structured meeting prep data from Autobound and research';

-- ============================================================================
-- MODIFY EXISTING TABLES
-- ============================================================================

-- DEALS table enhancements
ALTER TABLE deals ADD COLUMN IF NOT EXISTS current_stage_id BIGINT REFERENCES deal_stages(id);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS qualification_score INTEGER;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS close_probability DECIMAL(5,2);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS days_in_current_stage INTEGER;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS last_activity_date TIMESTAMP;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS next_action TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS next_action_due TIMESTAMP;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS objections_count INTEGER DEFAULT 0;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS proposal_sent BOOLEAN DEFAULT false;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS latest_proposal_id BIGINT REFERENCES sales_proposals(id);

CREATE INDEX IF NOT EXISTS idx_deals_current_stage ON deals(current_stage_id);
CREATE INDEX IF NOT EXISTS idx_deals_close_probability ON deals(close_probability DESC);
CREATE INDEX IF NOT EXISTS idx_deals_next_action_due ON deals(next_action_due);
CREATE INDEX IF NOT EXISTS idx_deals_last_activity ON deals(last_activity_date DESC);

COMMENT ON COLUMN deals.qualification_score IS 'BANT qualification score (0-100)';
COMMENT ON COLUMN deals.close_probability IS 'Estimated probability of closing (0-100%)';

-- ============================================================================

-- LEADS table enhancements
ALTER TABLE leads ADD COLUMN IF NOT EXISTS bant_budget BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS bant_authority BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS bant_need BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS bant_timeline BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS qualification_score INTEGER;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_sales_touchpoint TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS sales_call_count INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_leads_qualification ON leads(qualification_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_last_touchpoint ON leads(last_sales_touchpoint DESC);

COMMENT ON COLUMN leads.bant_budget IS 'BANT: Budget identified';
COMMENT ON COLUMN leads.bant_authority IS 'BANT: Decision maker identified';
COMMENT ON COLUMN leads.bant_need IS 'BANT: Need/pain confirmed';
COMMENT ON COLUMN leads.bant_timeline IS 'BANT: Timeline discussed';

-- ============================================================================

-- MEETINGS table enhancements
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS prep_completed BOOLEAN DEFAULT false;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS prep_doc_url TEXT;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS gamma_presentation_url TEXT;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS call_happened BOOLEAN;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS no_show BOOLEAN DEFAULT false;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS call_notes_url TEXT;

CREATE INDEX IF NOT EXISTS idx_meetings_prep_needed ON meetings(prep_completed) WHERE prep_completed = false;
CREATE INDEX IF NOT EXISTS idx_meetings_no_show ON meetings(no_show) WHERE no_show = true;

COMMENT ON COLUMN meetings.prep_completed IS 'Whether meeting prep doc and slides were created';
COMMENT ON COLUMN meetings.no_show IS 'Whether prospect was a no-show';

-- ============================================================================
-- SEED DATA: Default Deal Stages
-- ============================================================================

INSERT INTO deal_stages (name, description, stage_order, is_active, typical_duration_days) VALUES
('Discovery', 'Initial discovery call scheduled or completed', 1, true, 7),
('Qualification', 'Lead qualified via BANT, proposal needed', 2, true, 3),
('Proposal', 'Proposal sent, awaiting response', 3, true, 7),
('Negotiation', 'Discussing terms, addressing objections', 4, true, 10),
('Closed Won', 'Deal won, contract signed', 5, true, 0),
('Closed Lost', 'Deal lost or disqualified', 6, true, 0)
ON CONFLICT (name) DO NOTHING;

-- Mark closed stages
UPDATE deal_stages SET is_closed_won = true WHERE name = 'Closed Won';
UPDATE deal_stages SET is_closed_lost = true WHERE name = 'Closed Lost';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Get stale deals (no activity in 5+ days)
CREATE OR REPLACE FUNCTION get_stale_deals()
RETURNS TABLE (
    deal_id BIGINT,
    deal_name VARCHAR,
    current_stage VARCHAR,
    days_stale INTEGER,
    last_activity TIMESTAMP,
    next_action TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.name,
        ds.name AS current_stage,
        EXTRACT(DAY FROM NOW() - d.last_activity_date)::INTEGER AS days_stale,
        d.last_activity_date,
        d.next_action
    FROM deals d
    LEFT JOIN deal_stages ds ON d.current_stage_id = ds.id
    WHERE d.last_activity_date < NOW() - INTERVAL '5 days'
    AND d.stage NOT IN ('closed_won', 'closed_lost')
    AND d.deleted_at IS NULL
    ORDER BY d.last_activity_date ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_stale_deals IS 'Find deals with no activity in 5+ days';

-- ============================================================================

-- Get proposals needing follow-up
CREATE OR REPLACE FUNCTION get_proposals_needing_followup()
RETURNS TABLE (
    proposal_id BIGINT,
    proposal_number VARCHAR,
    deal_name VARCHAR,
    days_since_sent INTEGER,
    view_count INTEGER,
    last_followup TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sp.id,
        sp.proposal_number,
        d.name AS deal_name,
        EXTRACT(DAY FROM NOW() - sp.sent_at)::INTEGER AS days_since_sent,
        sp.view_count,
        sp.last_followup_at
    FROM sales_proposals sp
    JOIN deals d ON sp.deal_id = d.id
    WHERE sp.status IN ('sent', 'viewed', 'under_review')
    AND (sp.next_followup_due <= NOW() OR sp.next_followup_due IS NULL)
    AND sp.deleted_at IS NULL
    ORDER BY sp.sent_at ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_proposals_needing_followup IS 'Find proposals that need follow-up';

-- ============================================================================

-- Get meetings needing prep
CREATE OR REPLACE FUNCTION get_meetings_needing_prep()
RETURNS TABLE (
    meeting_id BIGINT,
    meeting_title VARCHAR,
    lead_name VARCHAR,
    company_name VARCHAR,
    meeting_date TIMESTAMP,
    hours_until_meeting NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id,
        m.title,
        l.name AS lead_name,
        c.name AS company_name,
        m.scheduled_at,
        EXTRACT(EPOCH FROM (m.scheduled_at - NOW())) / 3600 AS hours_until_meeting
    FROM meetings m
    LEFT JOIN leads l ON m.attendees::TEXT LIKE '%' || l.email || '%'
    LEFT JOIN companies c ON l.company_id = c.id
    WHERE m.prep_completed = false
    AND m.scheduled_at > NOW()
    AND m.scheduled_at < NOW() + INTERVAL '48 hours'
    AND m.deleted_at IS NULL
    ORDER BY m.scheduled_at ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_meetings_needing_prep IS 'Find upcoming meetings without prep completed';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Sales pipeline overview
CREATE OR REPLACE VIEW sales_pipeline_overview AS
SELECT 
    ds.name AS stage_name,
    ds.stage_order,
    COUNT(d.id) AS deal_count,
    SUM(d.value) AS total_value,
    AVG(d.close_probability) AS avg_close_probability,
    AVG(d.days_in_current_stage) AS avg_days_in_stage
FROM deal_stages ds
LEFT JOIN deals d ON ds.id = d.current_stage_id AND d.deleted_at IS NULL
WHERE ds.is_active = true
GROUP BY ds.id, ds.name, ds.stage_order
ORDER BY ds.stage_order;

COMMENT ON VIEW sales_pipeline_overview IS 'Sales pipeline summary by stage';

-- ============================================================================

-- Deals requiring attention
CREATE OR REPLACE VIEW deals_requiring_attention AS
SELECT 
    d.id AS deal_id,
    d.name AS deal_name,
    ds.name AS current_stage,
    d.value AS deal_value,
    d.last_activity_date,
    EXTRACT(DAY FROM NOW() - d.last_activity_date)::INTEGER AS days_stale,
    d.next_action,
    d.next_action_due,
    CASE 
        WHEN d.last_activity_date < NOW() - INTERVAL '5 days' THEN 'stale'
        WHEN d.next_action_due < NOW() THEN 'overdue_action'
        WHEN EXISTS (
            SELECT 1 FROM sales_proposals sp 
            WHERE sp.deal_id = d.id 
            AND sp.status = 'sent' 
            AND sp.next_followup_due <= NOW()
        ) THEN 'proposal_followup'
        ELSE 'ok'
    END AS attention_reason
FROM deals d
LEFT JOIN deal_stages ds ON d.current_stage_id = ds.id
WHERE d.stage NOT IN ('closed_won', 'closed_lost')
AND d.deleted_at IS NULL
AND (
    d.last_activity_date < NOW() - INTERVAL '5 days'
    OR d.next_action_due < NOW()
    OR EXISTS (
        SELECT 1 FROM sales_proposals sp 
        WHERE sp.deal_id = d.id 
        AND sp.status = 'sent' 
        AND sp.next_followup_due <= NOW()
    )
)
ORDER BY d.last_activity_date ASC;

COMMENT ON VIEW deals_requiring_attention IS 'Deals that need immediate action';

-- ============================================================================
-- END MIGRATION
-- ============================================================================

-- Migration complete: Jalila's complete sales infrastructure operational
-- 13 new tables created
-- 3 existing tables enhanced
-- 3 helper functions added
-- 2 views created
-- Default deal stages seeded
