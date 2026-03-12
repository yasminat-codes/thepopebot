-- Migration 011: Zayd Strategy Infrastructure
-- Agent: Zayd — Business Strategist
-- Purpose: OKRs, strategic initiatives, business metrics, decisions, positioning, opportunities
-- Created: 2026-02-23

-- 1. OKRS
CREATE TABLE okrs (
    id BIGSERIAL PRIMARY KEY,
    period_type VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    objective TEXT NOT NULL,
    objective_category VARCHAR(100),
    owner VARCHAR(100),
    key_results JSONB NOT NULL,
    overall_progress DECIMAL(5,2) DEFAULT 0.00,
    on_track BOOLEAN DEFAULT true,
    at_risk BOOLEAN DEFAULT false,
    risk_description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    last_update_date DATE,
    update_frequency VARCHAR(50) DEFAULT 'weekly',
    business_impact VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_okrs_period ON okrs(year, quarter);
CREATE INDEX idx_okrs_status ON okrs(status);

-- 2. STRATEGIC INITIATIVES
CREATE TABLE strategic_initiatives (
    id BIGSERIAL PRIMARY KEY,
    initiative_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    initiative_type VARCHAR(50),
    strategic_pillar VARCHAR(100),
    scope TEXT,
    success_criteria JSONB,
    executive_sponsor VARCHAR(100),
    initiative_lead VARCHAR(100),
    team_members JSONB,
    target_start_date DATE,
    target_completion_date DATE,
    actual_start_date DATE,
    actual_completion_date DATE,
    status VARCHAR(50) DEFAULT 'planning',
    health_status VARCHAR(50) DEFAULT 'healthy',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    milestones JSONB,
    estimated_budget DECIMAL(12,2),
    actual_spend DECIMAL(12,2),
    resource_requirements TEXT,
    expected_roi TEXT,
    expected_impact TEXT,
    actual_impact TEXT,
    risks JSONB,
    dependencies JSONB,
    last_status_update DATE,
    next_review_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_initiatives_status ON strategic_initiatives(status);
CREATE INDEX idx_initiatives_health ON strategic_initiatives(health_status);

-- 3. BUSINESS METRICS
CREATE TABLE business_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_category VARCHAR(100) NOT NULL,
    period_type VARCHAR(50) NOT NULL,
    period_date DATE NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    unit VARCHAR(50),
    target_value DECIMAL(15,2),
    target_met BOOLEAN,
    variance DECIMAL(15,2),
    variance_percentage DECIMAL(5,2),
    previous_period_value DECIMAL(15,2),
    period_over_period_change DECIMAL(15,2),
    period_over_period_percentage DECIMAL(5,2),
    data_source VARCHAR(100),
    calculation_method TEXT,
    status VARCHAR(50) DEFAULT 'final',
    notes TEXT,
    measured_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_metrics_name ON business_metrics(metric_name);
CREATE INDEX idx_metrics_category ON business_metrics(metric_category);
CREATE INDEX idx_metrics_period ON business_metrics(period_date DESC);

-- 4. STRATEGIC DECISIONS
CREATE TABLE strategic_decisions (
    id BIGSERIAL PRIMARY KEY,
    decision_title VARCHAR(255) NOT NULL,
    decision_description TEXT NOT NULL,
    decision_type VARCHAR(50),
    decision_importance VARCHAR(50),
    decision_date DATE NOT NULL,
    decided_by VARCHAR(100),
    input_from JSONB,
    options_evaluated JSONB,
    chosen_option TEXT NOT NULL,
    rationale TEXT NOT NULL,
    expected_outcomes JSONB,
    success_metrics JSONB,
    actual_outcomes JSONB,
    outcome_assessment TEXT,
    lessons_learned TEXT,
    implementation_plan TEXT,
    implementation_owner VARCHAR(100),
    implementation_date DATE,
    reversible BOOLEAN DEFAULT true,
    reversal_cost TEXT,
    related_okr_id BIGINT REFERENCES okrs(id),
    related_initiative_id BIGINT REFERENCES strategic_initiatives(id),
    review_scheduled BOOLEAN DEFAULT false,
    review_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_decisions_date ON strategic_decisions(decision_date DESC);
CREATE INDEX idx_decisions_type ON strategic_decisions(decision_type);

-- 5. MARKET POSITIONING
CREATE TABLE market_positioning (
    id BIGSERIAL PRIMARY KEY,
    version INTEGER NOT NULL,
    effective_date DATE NOT NULL,
    positioning_statement TEXT NOT NULL,
    tagline VARCHAR(255),
    target_audience TEXT NOT NULL,
    icp_definition TEXT,
    primary_value_prop TEXT NOT NULL,
    secondary_value_props JSONB,
    key_differentiators JSONB NOT NULL,
    competitive_advantages JSONB,
    core_messages JSONB,
    proof_points JSONB,
    vs_competitor_a TEXT,
    vs_competitor_b TEXT,
    vs_competitor_c TEXT,
    category_definition TEXT,
    category_positioning VARCHAR(50),
    status VARCHAR(50) DEFAULT 'draft',
    effectiveness_rating INTEGER,
    market_response TEXT,
    last_reviewed_date DATE,
    next_review_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_positioning_version ON market_positioning(version DESC);
CREATE INDEX idx_positioning_status ON market_positioning(status);

-- 6. STRATEGIC OPPORTUNITIES
CREATE TABLE strategic_opportunities (
    id BIGSERIAL PRIMARY KEY,
    opportunity_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    opportunity_type VARCHAR(50),
    potential_revenue DECIMAL(12,2),
    potential_customers INTEGER,
    market_size_estimate VARCHAR(100),
    time_to_realize VARCHAR(50),
    strategic_fit_score INTEGER,
    revenue_potential_score INTEGER,
    feasibility_score INTEGER,
    competitive_advantage_score INTEGER,
    total_score INTEGER,
    strengths JSONB,
    weaknesses JSONB,
    risks JSONB,
    required_investment DECIMAL(12,2),
    required_resources TEXT,
    required_capabilities TEXT,
    status VARCHAR(50) DEFAULT 'identified',
    decision VARCHAR(50),
    decision_date DATE,
    decision_rationale TEXT,
    initiative_id BIGINT REFERENCES strategic_initiatives(id),
    owner VARCHAR(100),
    discovered_by VARCHAR(100),
    discovered_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_opportunities_status ON strategic_opportunities(status);
CREATE INDEX idx_opportunities_score ON strategic_opportunities(total_score DESC);

-- ENHANCE RECOMMENDATIONS
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS recommendation_type VARCHAR(50);
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS strategic_pillar VARCHAR(100);
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS expected_impact TEXT;
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS implementation_effort VARCHAR(50);
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS decision_made BOOLEAN DEFAULT false;
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS decision_id BIGINT REFERENCES strategic_decisions(id);

CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations(recommendation_type);
