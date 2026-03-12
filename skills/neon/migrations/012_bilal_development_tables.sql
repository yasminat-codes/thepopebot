-- Migration 012: Bilal (Code & Development) Tables
-- Domain: Code repositories, builds, deployments, monitoring, GitHub tracking, technical documentation
-- Agent: Bilal (@DevSmartCoderBot)
-- Created: 2025-01-27

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- 1. GitHub Trending Snapshots
CREATE TABLE IF NOT EXISTS github_trending_snapshots (
    id BIGSERIAL PRIMARY KEY,
    scanned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    repo_full_name TEXT NOT NULL,
    repo_url TEXT NOT NULL,
    stars INTEGER,
    forks INTEGER,
    language TEXT,
    description TEXT,
    trending_period TEXT CHECK (trending_period IN ('daily', 'weekly', 'monthly')),
    relevance_score INTEGER CHECK (relevance_score BETWEEN 1 AND 10),
    relevance_notes TEXT,
    opportunity_type TEXT CHECK (opportunity_type IN ('template', 'integration', 'feature_idea', 'stack_choice', 'none')),
    opportunity_description TEXT,
    doc_url TEXT,
    created_by TEXT DEFAULT 'bilal',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_github_trending_scanned ON github_trending_snapshots(scanned_at DESC);
CREATE INDEX idx_github_trending_opportunity ON github_trending_snapshots(opportunity_type, relevance_score DESC) WHERE opportunity_type != 'none';

COMMENT ON TABLE github_trending_snapshots IS 'Daily GitHub trending analysis for product opportunity mapping';

-- 2. Tech Stack Decisions
CREATE TABLE IF NOT EXISTS tech_stack_decisions (
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT NOT NULL,
    layer TEXT NOT NULL CHECK (layer IN ('frontend', 'backend', 'database', 'hosting', 'auth', 'storage', 'monitoring', 'other')),
    technology TEXT NOT NULL,
    alternatives_considered TEXT[],
    decision_rationale TEXT NOT NULL,
    research_links TEXT[],
    decided_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_by TEXT DEFAULT 'bilal',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'replaced')),
    replacement_id BIGINT REFERENCES tech_stack_decisions(id),
    notes TEXT
);

CREATE INDEX idx_tech_stack_project ON tech_stack_decisions(project_name, layer, status);
CREATE INDEX idx_tech_stack_technology ON tech_stack_decisions(technology, status);

COMMENT ON TABLE tech_stack_decisions IS 'Technology choices per project with research and rationale';

-- 3. Code Repositories
CREATE TABLE IF NOT EXISTS code_repositories (
    id BIGSERIAL PRIMARY KEY,
    repo_name TEXT NOT NULL UNIQUE,
    repo_url TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'github' CHECK (platform IN ('github', 'gitlab', 'bitbucket')),
    project_name TEXT,
    repo_type TEXT CHECK (repo_type IN ('product', 'internal_tool', 'template', 'client_project', 'experiment')),
    primary_language TEXT,
    tech_stack JSONB,
    description TEXT,
    is_private BOOLEAN DEFAULT TRUE,
    default_branch TEXT DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_commit_at TIMESTAMPTZ,
    last_deploy_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deprecated')),
    notes TEXT
);

CREATE INDEX idx_repos_project ON code_repositories(project_name, status);
CREATE INDEX idx_repos_type ON code_repositories(repo_type, status);

COMMENT ON TABLE code_repositories IS 'All Smarterflo code repositories';

-- 4. Build Tasks
CREATE TABLE IF NOT EXISTS build_tasks (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT REFERENCES code_repositories(id),
    task_type TEXT NOT NULL CHECK (task_type IN ('feature', 'bugfix', 'refactor', 'security', 'optimization', 'documentation', 'testing')),
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER CHECK (priority BETWEEN 1 AND 4),
    status TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'code_review', 'testing', 'blocked', 'completed', 'cancelled')),
    branch_name TEXT,
    github_issue_url TEXT,
    github_pr_url TEXT,
    blockers TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    assigned_to TEXT DEFAULT 'bilal',
    created_by TEXT DEFAULT 'bilal',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_build_tasks_repo ON build_tasks(repo_id, status);
CREATE INDEX idx_build_tasks_status ON build_tasks(status, priority DESC) WHERE status IN ('todo', 'in_progress', 'blocked');
CREATE INDEX idx_build_tasks_type ON build_tasks(task_type, status);

COMMENT ON TABLE build_tasks IS 'Feature builds, bug fixes, refactors, technical tasks';

-- 5. Deployments
CREATE TABLE IF NOT EXISTS deployments (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT REFERENCES code_repositories(id),
    environment TEXT NOT NULL CHECK (environment IN ('production', 'staging', 'development', 'preview')),
    platform TEXT NOT NULL CHECK (platform IN ('coolify', 'railway', 'vercel', 'docker', 'other')),
    deploy_url TEXT,
    deploy_status TEXT NOT NULL CHECK (deploy_status IN ('pending', 'building', 'success', 'failed', 'rolled_back')),
    commit_sha TEXT,
    branch TEXT,
    triggered_by TEXT DEFAULT 'bilal',
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    deploy_duration_seconds INTEGER,
    error_message TEXT,
    build_logs_url TEXT,
    notes TEXT
);

CREATE INDEX idx_deployments_repo ON deployments(repo_id, environment, triggered_at DESC);
CREATE INDEX idx_deployments_status ON deployments(deploy_status, triggered_at DESC) WHERE deploy_status IN ('failed', 'pending', 'building');
CREATE INDEX idx_deployments_env ON deployments(environment, triggered_at DESC);

COMMENT ON TABLE deployments IS 'Production and staging deployment tracking';

-- 6. System Monitoring
CREATE TABLE IF NOT EXISTS system_monitoring (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT REFERENCES code_repositories(id),
    environment TEXT NOT NULL CHECK (environment IN ('production', 'staging', 'development')),
    check_type TEXT NOT NULL CHECK (check_type IN ('uptime', 'response_time', 'error_rate', 'cpu_usage', 'memory_usage', 'disk_usage', 'api_health')),
    metric_value NUMERIC,
    metric_unit TEXT,
    status TEXT NOT NULL CHECK (status IN ('healthy', 'warning', 'critical', 'down')),
    threshold_warning NUMERIC,
    threshold_critical NUMERIC,
    alert_sent BOOLEAN DEFAULT FALSE,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_monitoring_repo ON system_monitoring(repo_id, environment, checked_at DESC);
CREATE INDEX idx_monitoring_status ON system_monitoring(status, checked_at DESC) WHERE status IN ('warning', 'critical', 'down');
CREATE INDEX idx_monitoring_type ON system_monitoring(check_type, environment, checked_at DESC);

COMMENT ON TABLE system_monitoring IS 'System health checks, performance metrics, uptime tracking';

-- 7. Bugs and Issues
CREATE TABLE IF NOT EXISTS bugs_and_issues (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT REFERENCES code_repositories(id),
    issue_type TEXT NOT NULL CHECK (issue_type IN ('bug', 'tech_debt', 'security_vulnerability', 'performance_issue', 'design_flaw')),
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    title TEXT NOT NULL,
    description TEXT,
    reproduction_steps TEXT,
    error_logs TEXT,
    github_issue_url TEXT,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'wont_fix', 'duplicate')),
    fix_branch TEXT,
    fix_pr_url TEXT,
    reported_by TEXT,
    assigned_to TEXT DEFAULT 'bilal',
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT
);

CREATE INDEX idx_bugs_repo ON bugs_and_issues(repo_id, status, severity);
CREATE INDEX idx_bugs_status ON bugs_and_issues(status, severity) WHERE status IN ('open', 'in_progress');
CREATE INDEX idx_bugs_type ON bugs_and_issues(issue_type, severity);

COMMENT ON TABLE bugs_and_issues IS 'Bug tracking and technical debt log';

-- 8. Code Templates
CREATE TABLE IF NOT EXISTS code_templates (
    id BIGSERIAL PRIMARY KEY,
    template_name TEXT NOT NULL UNIQUE,
    template_type TEXT NOT NULL CHECK (template_type IN ('landing_page', 'dashboard', 'auth_flow', 'api_boilerplate', 'component_library', 'database_schema', 'deployment_config', 'full_stack_app')),
    source_product TEXT,
    source_url TEXT,
    tech_stack JSONB,
    description TEXT NOT NULL,
    use_cases TEXT[],
    repo_url TEXT,
    demo_url TEXT,
    documentation_url TEXT,
    extraction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    extracted_by TEXT DEFAULT 'bilal',
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'outdated', 'deprecated')),
    notes TEXT
);

CREATE INDEX idx_templates_type ON code_templates(template_type, status);
CREATE INDEX idx_templates_usage ON code_templates(times_used DESC, last_used_at DESC);

COMMENT ON TABLE code_templates IS 'Extracted templates from successful products (boilerplates)';

-- 9. Technical Documentation
CREATE TABLE IF NOT EXISTS technical_documentation (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT REFERENCES code_repositories(id),
    doc_type TEXT NOT NULL CHECK (doc_type IN ('api_docs', 'setup_guide', 'architecture', 'deployment_guide', 'troubleshooting', 'runbook', 'changelog', 'other')),
    title TEXT NOT NULL,
    google_doc_id TEXT,
    google_doc_url TEXT,
    markdown_path TEXT,
    summary TEXT,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by TEXT DEFAULT 'bilal',
    version TEXT,
    status TEXT NOT NULL DEFAULT 'current' CHECK (status IN ('current', 'outdated', 'archived')),
    notes TEXT
);

CREATE INDEX idx_tech_docs_repo ON technical_documentation(repo_id, doc_type, status);
CREATE INDEX idx_tech_docs_type ON technical_documentation(doc_type, status);
CREATE INDEX idx_tech_docs_updated ON technical_documentation(last_updated_at DESC);

COMMENT ON TABLE technical_documentation IS 'API docs, setup guides, architecture diagrams, runbooks';

-- 10. API Integrations
CREATE TABLE IF NOT EXISTS api_integrations (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT REFERENCES code_repositories(id),
    integration_name TEXT NOT NULL,
    api_provider TEXT NOT NULL,
    api_docs_url TEXT,
    use_case TEXT NOT NULL,
    environment TEXT NOT NULL CHECK (environment IN ('production', 'staging', 'development', 'all')),
    auth_type TEXT CHECK (auth_type IN ('api_key', 'oauth2', 'jwt', 'basic_auth', 'none')),
    credentials_location TEXT,
    rate_limit_info TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'testing', 'inactive', 'deprecated')),
    integrated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    integrated_by TEXT DEFAULT 'bilal',
    last_health_check TIMESTAMPTZ,
    health_status TEXT CHECK (health_status IN ('healthy', 'degraded', 'down', 'unknown')),
    notes TEXT
);

CREATE INDEX idx_integrations_repo ON api_integrations(repo_id, status);
CREATE INDEX idx_integrations_health ON api_integrations(health_status, last_health_check DESC) WHERE health_status IN ('degraded', 'down');

COMMENT ON TABLE api_integrations IS 'Third-party API integration tracking';

-- 11. Dev Insights Log
CREATE TABLE IF NOT EXISTS dev_insights_log (
    id BIGSERIAL PRIMARY KEY,
    insight_date DATE NOT NULL,
    insight_type TEXT NOT NULL CHECK (insight_type IN ('internal_tool_opportunity', 'github_trending_analysis', 'tech_debt_audit', 'security_audit', 'performance_optimization', 'stack_recommendation')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    google_doc_id TEXT,
    google_doc_url TEXT,
    action_items TEXT[],
    priority INTEGER CHECK (priority BETWEEN 1 AND 4),
    status TEXT NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed', 'approved', 'in_progress', 'completed', 'rejected')),
    created_by TEXT DEFAULT 'bilal',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    notes TEXT
);

CREATE INDEX idx_insights_date ON dev_insights_log(insight_date DESC);
CREATE INDEX idx_insights_type ON dev_insights_log(insight_type, status);
CREATE INDEX idx_insights_status ON dev_insights_log(status, priority DESC) WHERE status IN ('proposed', 'approved', 'in_progress');

COMMENT ON TABLE dev_insights_log IS 'Weekly internal tools audit and buildable product opportunities';

-- ============================================================================
-- ENHANCE EXISTING TABLES
-- ============================================================================

-- Add repo references to clients table
ALTER TABLE clients ADD COLUMN IF NOT EXISTS primary_repo_id BIGINT REFERENCES code_repositories(id);

-- Add technical specs to client_projects
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS repo_id BIGINT REFERENCES code_repositories(id);
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS tech_stack JSONB;
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS production_url TEXT;
ALTER TABLE client_projects ADD COLUMN IF NOT EXISTS staging_url TEXT;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- 1. Get Active Build Tasks
CREATE OR REPLACE FUNCTION get_active_build_tasks(p_repo_id BIGINT DEFAULT NULL)
RETURNS TABLE (
    repo_name TEXT,
    task_id BIGINT,
    task_type TEXT,
    title TEXT,
    status TEXT,
    priority INTEGER,
    days_in_status INTEGER,
    blockers TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cr.repo_name,
        bt.id,
        bt.task_type,
        bt.title,
        bt.status,
        bt.priority,
        EXTRACT(DAY FROM NOW() - COALESCE(bt.started_at, bt.created_at))::INTEGER,
        bt.blockers
    FROM build_tasks bt
    JOIN code_repositories cr ON bt.repo_id = cr.id
    WHERE bt.status IN ('todo', 'in_progress', 'blocked')
      AND (p_repo_id IS NULL OR bt.repo_id = p_repo_id)
    ORDER BY bt.priority DESC, bt.created_at ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_active_build_tasks IS 'Get current in-progress and blocked tasks per repo';

-- 2. Get System Health Alerts
CREATE OR REPLACE FUNCTION get_system_health_alerts()
RETURNS TABLE (
    repo_name TEXT,
    environment TEXT,
    check_type TEXT,
    status TEXT,
    metric_value NUMERIC,
    threshold TEXT,
    checked_minutes_ago INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cr.repo_name,
        sm.environment,
        sm.check_type,
        sm.status,
        sm.metric_value,
        CASE 
            WHEN sm.status = 'critical' THEN 'Critical: ' || sm.threshold_critical::TEXT
            WHEN sm.status = 'warning' THEN 'Warning: ' || sm.threshold_warning::TEXT
            ELSE NULL
        END,
        EXTRACT(EPOCH FROM (NOW() - sm.checked_at))::INTEGER / 60
    FROM system_monitoring sm
    JOIN code_repositories cr ON sm.repo_id = cr.id
    WHERE sm.status IN ('warning', 'critical', 'down')
      AND sm.checked_at > NOW() - INTERVAL '1 hour'
    ORDER BY 
        CASE sm.status 
            WHEN 'down' THEN 1
            WHEN 'critical' THEN 2
            WHEN 'warning' THEN 3
        END,
        sm.checked_at DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_system_health_alerts IS 'Get current warnings and critical alerts across all systems';

-- 3. Get Deployment Success Rate
CREATE OR REPLACE FUNCTION get_deployment_success_rate(
    p_days INTEGER DEFAULT 30,
    p_environment TEXT DEFAULT 'production'
)
RETURNS TABLE (
    repo_name TEXT,
    total_deploys BIGINT,
    successful_deploys BIGINT,
    failed_deploys BIGINT,
    success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cr.repo_name,
        COUNT(*)::BIGINT,
        COUNT(*) FILTER (WHERE d.deploy_status = 'success')::BIGINT,
        COUNT(*) FILTER (WHERE d.deploy_status = 'failed')::BIGINT,
        ROUND(
            (COUNT(*) FILTER (WHERE d.deploy_status = 'success')::NUMERIC / 
             NULLIF(COUNT(*), 0) * 100),
            1
        )
    FROM deployments d
    JOIN code_repositories cr ON d.repo_id = cr.id
    WHERE d.triggered_at > NOW() - (p_days || ' days')::INTERVAL
      AND d.environment = p_environment
    GROUP BY cr.repo_name
    ORDER BY success_rate ASC, total_deploys DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_deployment_success_rate IS 'Calculate deployment success rate per repo and environment';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- 1. Repository Health Summary
CREATE OR REPLACE VIEW v_repo_health_summary AS
SELECT 
    cr.id AS repo_id,
    cr.repo_name,
    cr.project_name,
    cr.status AS repo_status,
    COUNT(DISTINCT bt.id) FILTER (WHERE bt.status IN ('todo', 'in_progress')) AS active_tasks,
    COUNT(DISTINCT bt.id) FILTER (WHERE bt.status = 'blocked') AS blocked_tasks,
    COUNT(DISTINCT b.id) FILTER (WHERE b.status IN ('open', 'in_progress') AND b.severity IN ('critical', 'high')) AS critical_bugs,
    MAX(d.triggered_at) AS last_deploy,
    COUNT(DISTINCT d.id) FILTER (WHERE d.deploy_status = 'failed' AND d.triggered_at > NOW() - INTERVAL '7 days') AS recent_failed_deploys,
    COUNT(DISTINCT sm.id) FILTER (WHERE sm.status IN ('warning', 'critical', 'down') AND sm.checked_at > NOW() - INTERVAL '1 hour') AS current_alerts,
    cr.last_commit_at
FROM code_repositories cr
LEFT JOIN build_tasks bt ON cr.id = bt.repo_id
LEFT JOIN bugs_and_issues b ON cr.id = b.repo_id
LEFT JOIN deployments d ON cr.id = d.repo_id
LEFT JOIN system_monitoring sm ON cr.id = sm.repo_id
WHERE cr.status = 'active'
GROUP BY cr.id, cr.repo_name, cr.project_name, cr.status, cr.last_commit_at
ORDER BY current_alerts DESC, critical_bugs DESC, blocked_tasks DESC;

COMMENT ON VIEW v_repo_health_summary IS 'Overall health dashboard per repository';

-- 2. GitHub Opportunities
CREATE OR REPLACE VIEW v_github_opportunities AS
SELECT 
    gts.id,
    gts.repo_full_name,
    gts.repo_url,
    gts.stars,
    gts.language,
    gts.opportunity_type,
    gts.opportunity_description,
    gts.relevance_score,
    gts.scanned_at,
    gts.doc_url
FROM github_trending_snapshots gts
WHERE gts.opportunity_type != 'none'
  AND gts.relevance_score >= 7
  AND gts.scanned_at > NOW() - INTERVAL '30 days'
ORDER BY gts.relevance_score DESC, gts.stars DESC;

COMMENT ON VIEW v_github_opportunities IS 'High-value opportunities from GitHub trending analysis';

-- 3. Tech Debt Backlog
CREATE OR REPLACE VIEW v_tech_debt_backlog AS
SELECT 
    cr.repo_name,
    b.id AS issue_id,
    b.issue_type,
    b.severity,
    b.title,
    b.status,
    EXTRACT(DAY FROM NOW() - b.reported_at)::INTEGER AS days_open,
    b.assigned_to,
    b.github_issue_url
FROM bugs_and_issues b
JOIN code_repositories cr ON b.repo_id = cr.id
WHERE b.status IN ('open', 'in_progress')
  AND b.issue_type IN ('tech_debt', 'security_vulnerability', 'performance_issue')
ORDER BY 
    CASE b.severity 
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    days_open DESC;

COMMENT ON VIEW v_tech_debt_backlog IS 'Technical debt and open issues prioritized';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- - 11 new tables for code, builds, deployments, monitoring, GitHub tracking
-- - Enhanced 2 existing tables (clients, client_projects)
-- - 3 helper functions for build tasks, system health, deployment metrics
-- - 3 views for repo health, GitHub opportunities, tech debt backlog
-- Total tables in database: 114 (103 + 11 new)
