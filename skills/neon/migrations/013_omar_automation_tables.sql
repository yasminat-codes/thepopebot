-- Migration 013: Omar (Automation Specialist) Tables
-- Domain: n8n workflows, API integrations, webhooks, automation strategy
-- Agent: Omar (@YasmineEli_Bot)
-- Created: 2025-01-27

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- 1. n8n Workflows
CREATE TABLE IF NOT EXISTS n8n_workflows (
    id BIGSERIAL PRIMARY KEY,
    workflow_id TEXT UNIQUE,
    workflow_name TEXT NOT NULL,
    workflow_type TEXT CHECK (workflow_type IN ('data_sync', 'notification', 'lead_enrichment', 'content_automation', 'crm_sync', 'reporting', 'monitoring', 'other')),
    description TEXT NOT NULL,
    trigger_type TEXT CHECK (trigger_type IN ('webhook', 'schedule', 'manual', 'queue', 'event')),
    trigger_config JSONB,
    nodes_count INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    owner_agent TEXT,
    use_case TEXT NOT NULL,
    integrations_used TEXT[],
    workflow_json JSONB,
    n8n_export_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_edited_at TIMESTAMPTZ,
    last_executed_at TIMESTAMPTZ,
    total_executions BIGINT DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'broken', 'archived')),
    notes TEXT
);

CREATE INDEX idx_n8n_workflows_owner ON n8n_workflows(owner_agent, status);
CREATE INDEX idx_n8n_workflows_type ON n8n_workflows(workflow_type, status);
CREATE INDEX idx_n8n_workflows_active ON n8n_workflows(is_active, last_executed_at DESC) WHERE is_active = TRUE;

COMMENT ON TABLE n8n_workflows IS 'All n8n workflows across the business';

-- 2. Workflow Executions
CREATE TABLE IF NOT EXISTS workflow_executions (
    id BIGSERIAL PRIMARY KEY,
    workflow_id BIGINT REFERENCES n8n_workflows(id),
    n8n_execution_id TEXT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    execution_status TEXT NOT NULL CHECK (execution_status IN ('success', 'error', 'warning', 'running', 'timeout')),
    execution_time_ms INTEGER,
    trigger_data JSONB,
    error_message TEXT,
    error_node TEXT,
    retry_count INTEGER DEFAULT 0,
    output_data JSONB,
    nodes_executed INTEGER,
    credits_used NUMERIC(10, 4)
);

CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id, executed_at DESC);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(execution_status, executed_at DESC) WHERE execution_status IN ('error', 'timeout');
CREATE INDEX idx_workflow_executions_recent ON workflow_executions(executed_at DESC);

COMMENT ON TABLE workflow_executions IS 'Execution logs for n8n workflows';

-- 3. API Connections
CREATE TABLE IF NOT EXISTS api_connections (
    id BIGSERIAL PRIMARY KEY,
    connection_name TEXT NOT NULL UNIQUE,
    service_name TEXT NOT NULL,
    service_category TEXT CHECK (service_category IN ('crm', 'email', 'messaging', 'database', 'storage', 'ai', 'payment', 'analytics', 'social', 'marketing', 'other')),
    auth_type TEXT NOT NULL CHECK (auth_type IN ('api_key', 'oauth2', 'jwt', 'basic_auth', 'bearer_token', 'custom')),
    credential_location TEXT NOT NULL,
    api_docs_url TEXT,
    rate_limits TEXT,
    cost_per_call NUMERIC(10, 6),
    monthly_quota INTEGER,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'testing', 'failing', 'deprecated')),
    last_health_check TIMESTAMPTZ,
    health_check_status TEXT CHECK (health_check_status IN ('healthy', 'degraded', 'down', 'unknown')),
    failure_count_24h INTEGER DEFAULT 0,
    used_by_workflows INTEGER DEFAULT 0,
    setup_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    setup_by TEXT DEFAULT 'omar',
    notes TEXT
);

CREATE INDEX idx_api_connections_service ON api_connections(service_name, status);
CREATE INDEX idx_api_connections_health ON api_connections(health_check_status, last_health_check DESC) WHERE health_check_status IN ('degraded', 'down');
CREATE INDEX idx_api_connections_failing ON api_connections(failure_count_24h DESC) WHERE failure_count_24h > 0;

COMMENT ON TABLE api_connections IS 'All API connections and credentials locations';

-- 4. Webhooks
CREATE TABLE IF NOT EXISTS webhooks (
    id BIGSERIAL PRIMARY KEY,
    webhook_url TEXT NOT NULL UNIQUE,
    webhook_name TEXT NOT NULL,
    webhook_type TEXT CHECK (webhook_type IN ('n8n', 'custom', 'third_party', 'zapier', 'make')),
    source_service TEXT NOT NULL,
    destination_workflow_id BIGINT REFERENCES n8n_workflows(id),
    authentication_method TEXT CHECK (authentication_method IN ('none', 'secret_token', 'hmac_signature', 'basic_auth', 'api_key')),
    secret_location TEXT,
    payload_schema JSONB,
    last_received_at TIMESTAMPTZ,
    total_received BIGINT DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'broken', 'testing')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'omar',
    notes TEXT
);

CREATE INDEX idx_webhooks_workflow ON webhooks(destination_workflow_id, status);
CREATE INDEX idx_webhooks_source ON webhooks(source_service, status);
CREATE INDEX idx_webhooks_recent ON webhooks(last_received_at DESC);

COMMENT ON TABLE webhooks IS 'Webhook endpoints configured for automations';

-- 5. Automation Requests
CREATE TABLE IF NOT EXISTS automation_requests (
    id BIGSERIAL PRIMARY KEY,
    requested_by TEXT NOT NULL,
    request_type TEXT CHECK (request_type IN ('new_workflow', 'enhancement', 'fix', 'integration', 'optimization')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    current_manual_process TEXT,
    desired_outcome TEXT NOT NULL,
    frequency_estimate TEXT,
    time_saved_estimate TEXT,
    priority INTEGER CHECK (priority BETWEEN 1 AND 4),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'reviewing', 'approved', 'in_progress', 'testing', 'completed', 'rejected')),
    workflow_id BIGINT REFERENCES n8n_workflows(id),
    google_doc_url TEXT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    assigned_to TEXT DEFAULT 'omar',
    rejection_reason TEXT,
    notes TEXT
);

CREATE INDEX idx_automation_requests_status ON automation_requests(status, priority DESC) WHERE status IN ('new', 'approved', 'in_progress');
CREATE INDEX idx_automation_requests_requester ON automation_requests(requested_by, status);

COMMENT ON TABLE automation_requests IS 'Requests from team for new automations';

-- 6. Integration Mappings
CREATE TABLE IF NOT EXISTS integration_mappings (
    id BIGSERIAL PRIMARY KEY,
    mapping_name TEXT NOT NULL UNIQUE,
    source_system TEXT NOT NULL,
    destination_system TEXT NOT NULL,
    mapping_type TEXT CHECK (mapping_type IN ('one_way', 'two_way', 'aggregation', 'transformation')),
    field_mappings JSONB NOT NULL,
    transformation_rules JSONB,
    sync_frequency TEXT,
    workflow_id BIGINT REFERENCES n8n_workflows(id),
    last_synced_at TIMESTAMPTZ,
    total_records_synced BIGINT DEFAULT 0,
    error_count_24h INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'broken')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'omar',
    notes TEXT
);

CREATE INDEX idx_integration_mappings_systems ON integration_mappings(source_system, destination_system, status);
CREATE INDEX idx_integration_mappings_workflow ON integration_mappings(workflow_id);
CREATE INDEX idx_integration_mappings_errors ON integration_mappings(error_count_24h DESC) WHERE error_count_24h > 0;

COMMENT ON TABLE integration_mappings IS 'Data field mappings between systems';

-- 7. Automation Templates
CREATE TABLE IF NOT EXISTS automation_templates (
    id BIGSERIAL PRIMARY KEY,
    template_name TEXT NOT NULL UNIQUE,
    template_category TEXT CHECK (template_category IN ('crm_sync', 'lead_routing', 'notification', 'data_enrichment', 'reporting', 'monitoring', 'content', 'other')),
    description TEXT NOT NULL,
    use_cases TEXT[],
    required_integrations TEXT[],
    n8n_template_url TEXT,
    workflow_json JSONB,
    google_doc_url TEXT,
    setup_time_estimate TEXT,
    difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    times_deployed INTEGER DEFAULT 0,
    last_deployed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'omar',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'draft')),
    notes TEXT
);

CREATE INDEX idx_automation_templates_category ON automation_templates(template_category, status);
CREATE INDEX idx_automation_templates_usage ON automation_templates(times_deployed DESC, last_deployed_at DESC);

COMMENT ON TABLE automation_templates IS 'Reusable automation patterns and templates';

-- 8. Automation Documentation
CREATE TABLE IF NOT EXISTS automation_documentation (
    id BIGSERIAL PRIMARY KEY,
    doc_type TEXT NOT NULL CHECK (doc_type IN ('setup_guide', 'troubleshooting', 'api_reference', 'workflow_diagram', 'integration_guide', 'changelog', 'best_practices')),
    title TEXT NOT NULL,
    workflow_id BIGINT REFERENCES n8n_workflows(id),
    api_connection_id BIGINT REFERENCES api_connections(id),
    google_doc_id TEXT,
    google_doc_url TEXT NOT NULL,
    summary TEXT,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by TEXT DEFAULT 'omar',
    version TEXT,
    status TEXT NOT NULL DEFAULT 'current' CHECK (status IN ('current', 'outdated', 'archived')),
    notes TEXT
);

CREATE INDEX idx_automation_docs_workflow ON automation_documentation(workflow_id, doc_type, status);
CREATE INDEX idx_automation_docs_api ON automation_documentation(api_connection_id, doc_type, status);
CREATE INDEX idx_automation_docs_type ON automation_documentation(doc_type, status);

COMMENT ON TABLE automation_documentation IS 'Setup guides, troubleshooting docs, API references';

-- 9. Automation Costs
CREATE TABLE IF NOT EXISTS automation_costs (
    id BIGSERIAL PRIMARY KEY,
    cost_date DATE NOT NULL,
    service_name TEXT NOT NULL,
    cost_type TEXT CHECK (cost_type IN ('api_call', 'workflow_execution', 'subscription', 'storage', 'compute', 'data_transfer')),
    quantity INTEGER,
    unit_cost NUMERIC(10, 6),
    total_cost NUMERIC(10, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    workflow_id BIGINT REFERENCES n8n_workflows(id),
    api_connection_id BIGINT REFERENCES api_connections(id),
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_automation_costs_date ON automation_costs(cost_date DESC);
CREATE INDEX idx_automation_costs_service ON automation_costs(service_name, cost_date DESC);
CREATE INDEX idx_automation_costs_workflow ON automation_costs(workflow_id, cost_date DESC);

COMMENT ON TABLE automation_costs IS 'Track automation costs (API calls, credits, subscriptions)';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- 1. Get Failing Workflows
CREATE OR REPLACE FUNCTION get_failing_workflows()
RETURNS TABLE (
    workflow_name TEXT,
    workflow_id BIGINT,
    total_executions BIGINT,
    failed_executions BIGINT,
    failure_rate NUMERIC,
    last_error TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        nw.workflow_name,
        nw.id,
        COUNT(we.id)::BIGINT,
        COUNT(*) FILTER (WHERE we.execution_status IN ('error', 'timeout'))::BIGINT,
        ROUND(
            (COUNT(*) FILTER (WHERE we.execution_status IN ('error', 'timeout'))::NUMERIC / 
             NULLIF(COUNT(*), 0) * 100),
            1
        ),
        (SELECT we2.error_message 
         FROM workflow_executions we2 
         WHERE we2.workflow_id = nw.id 
           AND we2.execution_status = 'error' 
         ORDER BY we2.executed_at DESC 
         LIMIT 1)
    FROM n8n_workflows nw
    LEFT JOIN workflow_executions we ON nw.id = we.workflow_id 
        AND we.executed_at > NOW() - INTERVAL '24 hours'
    WHERE nw.status = 'active'
    GROUP BY nw.id, nw.workflow_name
    HAVING COUNT(*) FILTER (WHERE we.execution_status IN ('error', 'timeout')) > 0
    ORDER BY failure_rate DESC, failed_executions DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_failing_workflows IS 'Get workflows with errors in last 24h';

-- 2. Get API Health Report
CREATE OR REPLACE FUNCTION get_api_health_report()
RETURNS TABLE (
    service_name TEXT,
    connection_name TEXT,
    health_status TEXT,
    failure_count_24h INTEGER,
    hours_since_check INTEGER,
    used_by_workflows INTEGER,
    rate_limits TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ac.service_name,
        ac.connection_name,
        ac.health_check_status,
        ac.failure_count_24h,
        EXTRACT(EPOCH FROM (NOW() - ac.last_health_check))::INTEGER / 3600,
        ac.used_by_workflows,
        ac.rate_limits
    FROM api_connections ac
    WHERE ac.status != 'deprecated'
    ORDER BY 
        CASE ac.health_check_status
            WHEN 'down' THEN 1
            WHEN 'degraded' THEN 2
            WHEN 'unknown' THEN 3
            WHEN 'healthy' THEN 4
        END,
        ac.failure_count_24h DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_api_health_report IS 'Get health status of all API connections';

-- 3. Calculate Automation ROI
CREATE OR REPLACE FUNCTION calculate_automation_roi(p_workflow_id BIGINT)
RETURNS TABLE (
    workflow_name TEXT,
    total_executions BIGINT,
    estimated_time_saved_hours NUMERIC,
    total_cost NUMERIC,
    roi_ratio NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        nw.workflow_name,
        nw.total_executions,
        -- Estimate: each execution saves 5 minutes of manual work
        ROUND((nw.total_executions * 5.0 / 60), 2),
        COALESCE(SUM(ac.total_cost), 0),
        -- ROI: hours saved / (cost / $50 per hour)
        ROUND(
            (nw.total_executions * 5.0 / 60) / 
            NULLIF(COALESCE(SUM(ac.total_cost), 0) / 50, 0),
            2
        )
    FROM n8n_workflows nw
    LEFT JOIN automation_costs ac ON nw.id = ac.workflow_id
    WHERE nw.id = p_workflow_id
    GROUP BY nw.id, nw.workflow_name, nw.total_executions;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_automation_roi IS 'Calculate time/cost saved by automation';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- 1. Workflow Health Summary
CREATE OR REPLACE VIEW v_workflow_health_summary AS
WITH workflow_stats AS (
    SELECT 
        nw.id AS workflow_id,
        nw.workflow_name,
        nw.workflow_type,
        nw.is_active,
        nw.owner_agent,
        COUNT(DISTINCT we.id) FILTER (WHERE we.executed_at > NOW() - INTERVAL '24 hours') AS executions_24h,
        COUNT(DISTINCT we.id) FILTER (WHERE we.execution_status = 'error' AND we.executed_at > NOW() - INTERVAL '24 hours') AS errors_24h,
        ROUND(
            (COUNT(*) FILTER (WHERE we.execution_status = 'error' AND we.executed_at > NOW() - INTERVAL '24 hours')::NUMERIC / 
             NULLIF(COUNT(*) FILTER (WHERE we.executed_at > NOW() - INTERVAL '24 hours'), 0) * 100),
            1
        ) AS error_rate_24h,
        AVG(we.execution_time_ms) FILTER (WHERE we.executed_at > NOW() - INTERVAL '24 hours') AS avg_execution_time_ms,
        nw.last_executed_at,
        CASE 
            WHEN COUNT(*) FILTER (WHERE we.execution_status = 'error' AND we.executed_at > NOW() - INTERVAL '1 hour') > 5 THEN 'critical'
            WHEN COUNT(*) FILTER (WHERE we.execution_status = 'error' AND we.executed_at > NOW() - INTERVAL '24 hours') > 10 THEN 'warning'
            WHEN nw.is_active AND nw.last_executed_at < NOW() - INTERVAL '7 days' THEN 'stale'
            ELSE 'healthy'
        END AS health_status
    FROM n8n_workflows nw
    LEFT JOIN workflow_executions we ON nw.id = we.workflow_id
    WHERE nw.status = 'active'
    GROUP BY nw.id, nw.workflow_name, nw.workflow_type, nw.is_active, nw.owner_agent, nw.last_executed_at
)
SELECT *
FROM workflow_stats
ORDER BY 
    CASE health_status
        WHEN 'critical' THEN 1
        WHEN 'warning' THEN 2
        WHEN 'stale' THEN 3
        WHEN 'healthy' THEN 4
    END,
    error_rate_24h DESC;

COMMENT ON VIEW v_workflow_health_summary IS 'Overall health of all active workflows';

-- 2. Pending Automation Requests
CREATE OR REPLACE VIEW v_pending_automation_requests AS
SELECT 
    ar.id,
    ar.requested_by,
    ar.request_type,
    ar.title,
    ar.priority,
    ar.status,
    ar.time_saved_estimate,
    EXTRACT(DAY FROM NOW() - ar.requested_at)::INTEGER AS days_waiting,
    ar.requested_at
FROM automation_requests ar
WHERE ar.status IN ('new', 'reviewing', 'approved', 'in_progress')
ORDER BY 
    ar.priority DESC,
    ar.requested_at ASC;

COMMENT ON VIEW v_pending_automation_requests IS 'Open automation requests prioritized';

-- 3. Integration Health
CREATE OR REPLACE VIEW v_integration_health AS
WITH integration_stats AS (
    SELECT 
        im.id,
        im.mapping_name,
        im.source_system,
        im.destination_system,
        im.sync_frequency,
        im.last_synced_at,
        EXTRACT(EPOCH FROM (NOW() - im.last_synced_at))::INTEGER / 60 AS minutes_since_sync,
        im.total_records_synced,
        im.error_count_24h,
        CASE 
            WHEN im.error_count_24h > 50 THEN 'critical'
            WHEN im.error_count_24h > 10 THEN 'warning'
            WHEN im.last_synced_at < NOW() - INTERVAL '24 hours' THEN 'stale'
            ELSE 'healthy'
        END AS health_status
    FROM integration_mappings im
    WHERE im.status = 'active'
)
SELECT *
FROM integration_stats
ORDER BY 
    CASE health_status
        WHEN 'critical' THEN 1
        WHEN 'warning' THEN 2
        WHEN 'stale' THEN 3
        WHEN 'healthy' THEN 4
    END,
    error_count_24h DESC;

COMMENT ON VIEW v_integration_health IS 'Integration mapping health and sync status';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- - 9 new tables for automation workflows, API connections, webhooks, costs
-- - 3 helper functions for failing workflows, API health, ROI calculation
-- - 3 views for workflow health, pending requests, integration health
-- Total tables in database: 136 (127 + 9 new)
