-- Migration 010: Noor Research Infrastructure
-- Agent: Noor — Research Specialist
-- Purpose: Research requests, competitor profiles, market reports, trends, pain points, sources
-- Created: 2026-02-23

-- 1. RESEARCH REQUESTS
CREATE TABLE research_requests (
    id BIGSERIAL PRIMARY KEY,
    request_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    research_type VARCHAR(50) NOT NULL,
    requested_by VARCHAR(100) NOT NULL,
    requested_for VARCHAR(100),
    priority VARCHAR(50) DEFAULT 'medium',
    urgency VARCHAR(50),
    scope_detail TEXT,
    specific_questions JSONB,
    deliverable_format VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    assigned_to VARCHAR(100) DEFAULT 'Noor',
    requested_date DATE NOT NULL,
    due_date DATE,
    estimated_hours INTEGER,
    actual_hours INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    output_doc_url TEXT,
    key_findings JSONB,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_research_requests_status ON research_requests(status);
CREATE INDEX idx_research_requests_type ON research_requests(research_type);
CREATE INDEX idx_research_requests_priority ON research_requests(priority);

-- 2. COMPETITOR PROFILES
CREATE TABLE competitor_profiles (
    id BIGSERIAL PRIMARY KEY,
    competitor_name VARCHAR(255) NOT NULL UNIQUE,
    company_id BIGINT REFERENCES companies(id),
    website TEXT,
    competitor_tier VARCHAR(50),
    threat_level VARCHAR(50),
    headquarters_location VARCHAR(255),
    founded_year INTEGER,
    company_size VARCHAR(50),
    funding_stage VARCHAR(50),
    total_funding DECIMAL(12,2),
    estimated_revenue VARCHAR(100),
    estimated_customers INTEGER,
    market_share_estimate DECIMAL(5,2),
    product_offerings JSONB,
    target_market VARCHAR(255),
    icp_overlap DECIMAL(5,2),
    value_proposition TEXT,
    key_differentiators JSONB,
    pricing_model TEXT,
    pricing_details JSONB,
    strengths JSONB,
    weaknesses JSONB,
    our_advantages_vs_them JSONB,
    recent_news JSONB,
    recent_hires_signals JSONB,
    tech_stack JSONB,
    website_traffic_estimate INTEGER,
    seo_performance VARCHAR(50),
    social_following JSONB,
    last_researched_date DATE,
    research_completeness VARCHAR(50),
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_competitors_name ON competitor_profiles(competitor_name);
CREATE INDEX idx_competitors_tier ON competitor_profiles(competitor_tier);
CREATE INDEX idx_competitors_threat ON competitor_profiles(threat_level);

-- 3. MARKET RESEARCH REPORTS
CREATE TABLE market_research_reports (
    id BIGSERIAL PRIMARY KEY,
    report_title VARCHAR(255) NOT NULL,
    market_name VARCHAR(255) NOT NULL,
    market_size_tam DECIMAL(12,2),
    market_size_sam DECIMAL(12,2),
    market_size_som DECIMAL(12,2),
    currency VARCHAR(10) DEFAULT 'USD',
    growth_rate DECIMAL(5,2),
    maturity_stage VARCHAR(50),
    opportunity_score INTEGER,
    attractiveness VARCHAR(50),
    entry_barriers JSONB,
    target_segments JSONB,
    ideal_customer_profile TEXT,
    competitive_intensity VARCHAR(50),
    key_players JSONB,
    key_trends JSONB,
    drivers JSONB,
    challenges JSONB,
    recommendations JSONB,
    go_to_market_notes TEXT,
    sources JSONB,
    research_methodology TEXT,
    report_doc_url TEXT,
    executive_summary TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    research_date DATE NOT NULL,
    valid_until DATE,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_market_reports_market ON market_research_reports(market_name);
CREATE INDEX idx_market_reports_opportunity ON market_research_reports(opportunity_score DESC);

-- 4. INDUSTRY TRENDS
CREATE TABLE industry_trends (
    id BIGSERIAL PRIMARY KEY,
    trend_name VARCHAR(255) NOT NULL,
    trend_category VARCHAR(100),
    description TEXT NOT NULL,
    impact_on_business VARCHAR(50),
    impact_description TEXT,
    emergence_stage VARCHAR(50),
    time_to_impact VARCHAR(50),
    evidence JSONB,
    signal_strength VARCHAR(50),
    opportunity_or_threat VARCHAR(50),
    strategic_implications TEXT,
    recommended_actions JSONB,
    monitoring_status VARCHAR(50) DEFAULT 'active',
    last_checked_date DATE,
    check_frequency VARCHAR(50),
    related_trends JSONB,
    affected_markets JSONB,
    internal_notes TEXT,
    detected_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trends_category ON industry_trends(trend_category);
CREATE INDEX idx_trends_impact ON industry_trends(impact_on_business);
CREATE INDEX idx_trends_stage ON industry_trends(emergence_stage);

-- 5. PAIN POINT RESEARCH
CREATE TABLE pain_point_research (
    id BIGSERIAL PRIMARY KEY,
    pain_point_title VARCHAR(255) NOT NULL,
    detailed_description TEXT NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    personas_affected JSONB,
    pain_severity VARCHAR(50),
    frequency VARCHAR(50),
    evidence_sources JSONB,
    quote_examples JSONB,
    frequency_count INTEGER,
    business_impact TEXT,
    cost_of_inaction TEXT,
    current_solutions JSONB,
    solution_gaps TEXT,
    how_we_solve TEXT,
    solved_by_service VARCHAR(100),
    value_delivered TEXT,
    roi_estimate TEXT,
    objections_related JSONB,
    case_studies JSONB,
    testimonials JSONB,
    research_method VARCHAR(50),
    confidence_level VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    internal_notes TEXT,
    discovered_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pain_points_industry ON pain_point_research(industry);
CREATE INDEX idx_pain_points_severity ON pain_point_research(pain_severity);
CREATE INDEX idx_pain_points_service ON pain_point_research(solved_by_service);

-- 6. RESEARCH SOURCES
CREATE TABLE research_sources (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL,
    source_url TEXT,
    source_type VARCHAR(50),
    credibility_rating INTEGER,
    reliability_rating INTEGER,
    timeliness_rating INTEGER,
    times_cited INTEGER DEFAULT 0,
    last_used_date DATE,
    topics_covered JSONB,
    geographic_coverage JSONB,
    access_type VARCHAR(50),
    subscription_cost DECIMAL(10,2),
    access_notes TEXT,
    strengths TEXT,
    limitations TEXT,
    status VARCHAR(50) DEFAULT 'active',
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sources_name ON research_sources(source_name);
CREATE INDEX idx_sources_type ON research_sources(source_type);
CREATE INDEX idx_sources_credibility ON research_sources(credibility_rating DESC);

-- ENHANCE KNOWLEDGE_DOCUMENTS
ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS research_type VARCHAR(50);
ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS research_request_id BIGINT REFERENCES research_requests(id);
ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS freshness_date DATE;
ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS stale_after_days INTEGER DEFAULT 180;
ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS source_quality_score INTEGER;
ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS citations_count INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_knowledge_research_type ON knowledge_documents(research_type);

-- ENHANCE COMPANIES
ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_competitor BOOLEAN DEFAULT false;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS competitor_profile_id BIGINT REFERENCES competitor_profiles(id);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS competitive_threat_level VARCHAR(50);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS last_competitive_analysis DATE;

CREATE INDEX IF NOT EXISTS idx_companies_competitor ON companies(is_competitor) WHERE is_competitor = true;
