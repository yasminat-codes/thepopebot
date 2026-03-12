-- Migration 009: Huda Client Success Infrastructure
-- Agent: Huda — Client Success Manager
-- Purpose: Health scores, onboarding, check-ins, milestones, renewals, issues, success plans, testimonials
-- Created: 2026-02-23

-- 1. CLIENT HEALTH SCORES
CREATE TABLE client_health_scores (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    score_date DATE NOT NULL,
    engagement_score INTEGER,
    satisfaction_score INTEGER,
    product_usage_score INTEGER,
    payment_health_score INTEGER,
    relationship_strength_score INTEGER,
    overall_health_score INTEGER,
    health_status VARCHAR(50),
    risk_factors JSONB,
    red_flags JSONB,
    upsell_potential VARCHAR(50),
    referral_potential VARCHAR(50),
    testimonial_ready BOOLEAN DEFAULT false,
    requires_attention BOOLEAN DEFAULT false,
    attention_reason TEXT,
    recommended_actions JSONB,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_client_health_client ON client_health_scores(client_id);
CREATE INDEX idx_client_health_date ON client_health_scores(score_date DESC);
CREATE INDEX idx_client_health_status ON client_health_scores(health_status);

-- 2. ONBOARDING CHECKLISTS
CREATE TABLE onboarding_checklists (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    handoff_id BIGINT REFERENCES client_handoffs(id),
    checklist_name VARCHAR(255) NOT NULL,
    total_steps INTEGER NOT NULL,
    completed_steps INTEGER DEFAULT 0,
    completion_percentage DECIMAL(5,2),
    steps JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'in_progress',
    blockers JSONB,
    target_completion_date DATE,
    actual_completion_date DATE,
    days_to_complete INTEGER,
    client_satisfaction VARCHAR(50),
    issues_encountered JSONB,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_onboarding_client ON onboarding_checklists(client_id);
CREATE INDEX idx_onboarding_status ON onboarding_checklists(status);

-- 3. CLIENT CHECK-INS
CREATE TABLE client_check_ins (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    project_id UUID,
    meeting_id BIGINT REFERENCES meetings(id),
    check_in_type VARCHAR(50) NOT NULL,
    check_in_date TIMESTAMP NOT NULL,
    attendees JSONB,
    huda_attended BOOLEAN DEFAULT true,
    yasmine_attended BOOLEAN DEFAULT false,
    topics_discussed JSONB,
    project_status VARCHAR(50),
    client_sentiment VARCHAR(50),
    action_items JSONB,
    huda_action_items JSONB,
    client_action_items JSONB,
    issues_raised JSONB,
    upsell_discussed BOOLEAN DEFAULT false,
    upsell_notes TEXT,
    referral_discussed BOOLEAN DEFAULT false,
    testimonial_requested BOOLEAN DEFAULT false,
    follow_up_needed BOOLEAN DEFAULT false,
    follow_up_due_date DATE,
    follow_up_completed BOOLEAN DEFAULT false,
    summary TEXT,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_check_ins_client ON client_check_ins(client_id);
CREATE INDEX idx_check_ins_date ON client_check_ins(check_in_date DESC);

-- 4. CLIENT MILESTONES
CREATE TABLE client_milestones (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    project_id UUID,
    milestone_name VARCHAR(255) NOT NULL,
    description TEXT,
    milestone_order INTEGER,
    status VARCHAR(50) DEFAULT 'not_started',
    target_date DATE,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    days_to_complete INTEGER,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    deliverables JSONB,
    blocked BOOLEAN DEFAULT false,
    blocker_description TEXT,
    blocker_owner VARCHAR(100),
    client_approved BOOLEAN DEFAULT false,
    approved_at TIMESTAMP,
    revision_count INTEGER DEFAULT 0,
    client_feedback TEXT,
    assigned_to VARCHAR(100),
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_milestones_client ON client_milestones(client_id);
CREATE INDEX idx_milestones_project ON client_milestones(project_id);
CREATE INDEX idx_milestones_status ON client_milestones(status);

-- 5. CLIENT RENEWALS
CREATE TABLE client_renewals (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    current_contract_value DECIMAL(12,2),
    current_contract_start DATE,
    current_contract_end DATE,
    renewal_date DATE NOT NULL,
    renewal_status VARCHAR(50) DEFAULT 'upcoming',
    days_until_renewal INTEGER,
    proposed_value DECIMAL(12,2),
    proposed_terms TEXT,
    expansion_included BOOLEAN DEFAULT false,
    expansion_details TEXT,
    negotiation_started BOOLEAN DEFAULT false,
    negotiation_notes TEXT,
    objections JSONB,
    renewed BOOLEAN,
    renewed_at TIMESTAMP,
    new_contract_value DECIMAL(12,2),
    new_contract_end DATE,
    churned BOOLEAN DEFAULT false,
    churn_reason TEXT,
    churn_date DATE,
    renewal_probability DECIMAL(5,2),
    risk_level VARCHAR(50),
    first_outreach_date DATE,
    last_contact_date DATE,
    contact_count INTEGER DEFAULT 0,
    owner VARCHAR(100) DEFAULT 'Huda',
    jalila_involved BOOLEAN DEFAULT false,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_renewals_client ON client_renewals(client_id);
CREATE INDEX idx_renewals_date ON client_renewals(renewal_date);
CREATE INDEX idx_renewals_status ON client_renewals(renewal_status);

-- 6. CLIENT ISSUES
CREATE TABLE client_issues (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    project_id UUID,
    issue_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    issue_type VARCHAR(50) NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium',
    severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'open',
    reported_date TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    time_to_resolve_hours INTEGER,
    assigned_to VARCHAR(100),
    escalated_to VARCHAR(100),
    resolution TEXT,
    resolution_type VARCHAR(50),
    client_satisfied BOOLEAN,
    updates JSONB,
    last_update_sent TIMESTAMP,
    client_impact VARCHAR(50),
    business_impact TEXT,
    follow_up_needed BOOLEAN DEFAULT false,
    follow_up_date DATE,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_client_issues_client ON client_issues(client_id);
CREATE INDEX idx_client_issues_status ON client_issues(status);
CREATE INDEX idx_client_issues_priority ON client_issues(priority);

-- 7. CLIENT SUCCESS PLANS
CREATE TABLE client_success_plans (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    plan_name VARCHAR(255) NOT NULL,
    plan_period_start DATE NOT NULL,
    plan_period_end DATE NOT NULL,
    client_goals JSONB NOT NULL,
    success_criteria JSONB,
    kpis JSONB,
    meeting_cadence VARCHAR(50),
    next_qbr_date DATE,
    identified_risks JSONB,
    mitigation_strategies JSONB,
    expansion_targets JSONB,
    upsell_timeline TEXT,
    plan_status VARCHAR(50) DEFAULT 'active',
    health_trend VARCHAR(50),
    last_reviewed_date DATE,
    next_review_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_success_plans_client ON client_success_plans(client_id);
CREATE INDEX idx_success_plans_status ON client_success_plans(plan_status);

-- 8. TESTIMONIALS
CREATE TABLE testimonials (
    id BIGSERIAL PRIMARY KEY,
    client_id UUID,
    testimonial_text TEXT NOT NULL,
    testimonial_type VARCHAR(50),
    project_context TEXT,
    results_achieved TEXT,
    specific_metrics TEXT,
    client_name VARCHAR(255),
    client_title VARCHAR(255),
    client_company VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft',
    requested_date DATE,
    received_date DATE,
    approved_date DATE,
    published_date DATE,
    approved_for_website BOOLEAN DEFAULT false,
    approved_for_social BOOLEAN DEFAULT false,
    approved_for_proposals BOOLEAN DEFAULT false,
    photo_url TEXT,
    video_url TEXT,
    case_study_url TEXT,
    times_used INTEGER DEFAULT 0,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_testimonials_client ON testimonials(client_id);
CREATE INDEX idx_testimonials_status ON testimonials(status);

-- ENHANCE CLIENT_PROJECTS
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS health_status VARCHAR(50) DEFAULT 'healthy';
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS last_update_sent TIMESTAMP;
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS next_update_due DATE;
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS days_since_last_update INTEGER;
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS milestone_count INTEGER DEFAULT 0;
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS milestones_completed INTEGER DEFAULT 0;
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS completion_percentage DECIMAL(5,2) DEFAULT 0.00;

CREATE INDEX IF NOT EXISTS idx_client_projects_health ON client_projects(health_status);
