-- Migration 018: Omar Role Evolution - Systems Architect
-- Date: 2026-02-24
-- Changes:
--   - Add 7 new tables for Omar (Systems Architect role)
--   - Move 3 tables from Omar to Bilal (n8n_workflows, workflow_executions, automation_requests)
--   - Keep 6 shared tables (api_connections, webhooks, integration_mappings, automation_costs, automation_documentation, automation_templates)

-- ============================================================================
-- OMAR NEW TABLES (7)
-- ============================================================================

-- 1. System Architectures
CREATE TABLE IF NOT EXISTS system_architectures (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('client', 'internal')),
    description TEXT,
    diagram_url TEXT,
    status TEXT DEFAULT 'in_design' CHECK (status IN ('in_design', 'in_review', 'approved', 'implemented', 'deprecated')),
    client_id UUID REFERENCES clients(client_id),
    created_by TEXT NOT NULL,
    reviewed_by TEXT,
    approved_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    deprecated_at TIMESTAMPTZ
);

CREATE INDEX idx_system_architectures_status ON system_architectures(status);
CREATE INDEX idx_system_architectures_type ON system_architectures(type);
CREATE INDEX idx_system_architectures_client ON system_architectures(client_id);

-- 2. Process Maps
CREATE TABLE IF NOT EXISTS process_maps (
    id BIGSERIAL PRIMARY KEY,
    process_name TEXT NOT NULL,
    process_type TEXT NOT NULL CHECK (process_type IN ('sales', 'delivery', 'onboarding', 'handoff', 'support', 'internal', 'other')),
    description TEXT,
    owner TEXT NOT NULL,
    diagram_url TEXT,
    sop_url TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'in_review', 'active', 'archived')),
    version INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ
);

CREATE INDEX idx_process_maps_type ON process_maps(process_type);
CREATE INDEX idx_process_maps_status ON process_maps(status);
CREATE INDEX idx_process_maps_owner ON process_maps(owner);

-- 3. SOPs (Standard Operating Procedures)
CREATE TABLE IF NOT EXISTS sops (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    process_id BIGINT REFERENCES process_maps(id),
    document_url TEXT NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'in_review', 'active', 'archived')),
    owner TEXT NOT NULL,
    version INT DEFAULT 1,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_reviewed_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ
);

CREATE INDEX idx_sops_category ON sops(category);
CREATE INDEX idx_sops_status ON sops(status);
CREATE INDEX idx_sops_owner ON sops(owner);
CREATE INDEX idx_sops_process ON sops(process_id);

-- 4. Integration Standards
CREATE TABLE IF NOT EXISTS integration_standards (
    id BIGSERIAL PRIMARY KEY,
    standard_name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('error_handling', 'authentication', 'data_format', 'naming', 'testing', 'monitoring', 'other')),
    description TEXT NOT NULL,
    example_url TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'deprecated')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deprecated_at TIMESTAMPTZ
);

CREATE INDEX idx_integration_standards_category ON integration_standards(category);
CREATE INDEX idx_integration_standards_status ON integration_standards(status);

-- 5. System Reviews
CREATE TABLE IF NOT EXISTS system_reviews (
    id BIGSERIAL PRIMARY KEY,
    system_id BIGINT REFERENCES system_architectures(id),
    review_type TEXT NOT NULL CHECK (review_type IN ('architecture_audit', 'security_review', 'performance_review', 'quarterly_audit', 'incident_review', 'other')),
    findings TEXT NOT NULL,
    recommendations TEXT,
    reviewer TEXT NOT NULL,
    reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'closed')),
    follow_up_date DATE,
    closed_at TIMESTAMPTZ
);

CREATE INDEX idx_system_reviews_system ON system_reviews(system_id);
CREATE INDEX idx_system_reviews_type ON system_reviews(review_type);
CREATE INDEX idx_system_reviews_status ON system_reviews(status);
CREATE INDEX idx_system_reviews_reviewer ON system_reviews(reviewer);

-- 6. Tool Evaluations
CREATE TABLE IF NOT EXISTS tool_evaluations (
    id BIGSERIAL PRIMARY KEY,
    tool_name TEXT NOT NULL,
    use_case TEXT NOT NULL,
    evaluation_criteria TEXT,
    score INT CHECK (score BETWEEN 1 AND 10),
    decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected', 'deferred', 'trial')),
    rationale TEXT NOT NULL,
    alternatives_considered TEXT,
    decided_by TEXT NOT NULL,
    decided_at TIMESTAMPTZ DEFAULT NOW(),
    trial_end_date DATE,
    final_decision TEXT CHECK (final_decision IN ('approved', 'rejected', NULL))
);

CREATE INDEX idx_tool_evaluations_decision ON tool_evaluations(decision);
CREATE INDEX idx_tool_evaluations_decided_by ON tool_evaluations(decided_by);
CREATE INDEX idx_tool_evaluations_tool ON tool_evaluations(tool_name);

-- 7. Implementation Roadmaps
CREATE TABLE IF NOT EXISTS implementation_roadmaps (
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT NOT NULL,
    client_id UUID REFERENCES clients(client_id),
    system_id BIGINT REFERENCES system_architectures(id),
    phase INT NOT NULL,
    deliverable TEXT NOT NULL,
    status TEXT DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'blocked', 'completed', 'cancelled')),
    due_date DATE,
    dependencies TEXT,
    owner TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    blocked_reason TEXT
);

CREATE INDEX idx_implementation_roadmaps_client ON implementation_roadmaps(client_id);
CREATE INDEX idx_implementation_roadmaps_system ON implementation_roadmaps(system_id);
CREATE INDEX idx_implementation_roadmaps_status ON implementation_roadmaps(status);
CREATE INDEX idx_implementation_roadmaps_owner ON implementation_roadmaps(owner);

-- ============================================================================
-- BILAL NEW TABLES (3) - Moved from Omar
-- ============================================================================

-- Note: These tables already exist in Bilal's schema from migration 012
-- No changes needed - just documenting the transfer

-- n8n_workflows - Already exists under Bilal
-- workflow_executions - Already exists under Bilal  
-- automation_requests - Already exists under Bilal

-- ============================================================================
-- HELPER FUNCTIONS FOR OMAR
-- ============================================================================

-- Get systems needing review (not reviewed in 90 days)
CREATE OR REPLACE FUNCTION get_systems_needing_review()
RETURNS TABLE (
    id BIGINT,
    name TEXT,
    type TEXT,
    last_review_date DATE,
    days_since_review INT
) AS $$
BEGIN
    RETURN QUERY
    WITH latest_reviews AS (
        SELECT 
            sr.system_id,
            MAX(sr.reviewed_at::DATE) as last_review
        FROM system_reviews sr
        GROUP BY sr.system_id
    )
    SELECT 
        sa.id,
        sa.name,
        sa.type,
        lr.last_review,
        COALESCE((CURRENT_DATE - lr.last_review)::INT, 999) as days_since
    FROM system_architectures sa
    LEFT JOIN latest_reviews lr ON sa.id = lr.system_id
    WHERE sa.status IN ('approved', 'implemented')
    AND (lr.last_review IS NULL OR (CURRENT_DATE - lr.last_review) > 90)
    ORDER BY days_since DESC;
END;
$$ LANGUAGE plpgsql;

-- Get SOPs by category
CREATE OR REPLACE FUNCTION get_sops_by_category(p_category TEXT)
RETURNS TABLE (
    id BIGINT,
    title TEXT,
    document_url TEXT,
    owner TEXT,
    version INT,
    status TEXT,
    last_updated DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.title,
        s.document_url,
        s.owner,
        s.version,
        s.status,
        s.updated_at::DATE
    FROM sops s
    WHERE s.category = p_category
    AND s.status = 'active'
    ORDER BY s.title;
END;
$$ LANGUAGE plpgsql;

-- Get integration health report
CREATE OR REPLACE FUNCTION get_integration_health_report()
RETURNS TABLE (
    api_name TEXT,
    total_connections INT,
    active_connections INT,
    failing_connections INT,
    last_check DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ac.api_name,
        COUNT(*)::INT as total,
        SUM(CASE WHEN ac.status = 'active' THEN 1 ELSE 0 END)::INT as active,
        SUM(CASE WHEN ac.status = 'failing' THEN 1 ELSE 0 END)::INT as failing,
        MAX(ac.last_health_check::DATE) as last_check
    FROM api_connections ac
    GROUP BY ac.api_name
    ORDER BY failing DESC, api_name;
END;
$$ LANGUAGE plpgsql;

-- Get tool evaluation history
CREATE OR REPLACE FUNCTION get_tool_decisions()
RETURNS TABLE (
    tool_name TEXT,
    use_case TEXT,
    decision TEXT,
    score INT,
    decided_date DATE,
    decided_by TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        te.tool_name,
        te.use_case,
        COALESCE(te.final_decision, te.decision) as decision,
        te.score,
        te.decided_at::DATE,
        te.decided_by
    FROM tool_evaluations te
    ORDER BY te.decided_at DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE system_architectures IS 'Omar: System designs for clients and internal operations';
COMMENT ON TABLE process_maps IS 'Omar: Business process documentation and workflow diagrams';
COMMENT ON TABLE sops IS 'Omar: Standard Operating Procedures library';
COMMENT ON TABLE integration_standards IS 'Omar: Integration patterns and best practices';
COMMENT ON TABLE system_reviews IS 'Omar: Architecture reviews and system audits';
COMMENT ON TABLE tool_evaluations IS 'Omar: Tool selection decisions and rationale';
COMMENT ON TABLE implementation_roadmaps IS 'Omar: Project implementation plans and phases';

-- Migration complete
