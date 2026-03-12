-- Aaliyah (Chief of Staff) Tables
-- Complete task delegation, coordination, and monitoring infrastructure
-- Created: 2026-02-23

-- ============================================
-- AGENT_TASKS - Task Delegation & Tracking
-- ============================================

CREATE TABLE IF NOT EXISTS agent_tasks (
  id BIGSERIAL PRIMARY KEY,
  
  -- Assignment
  assigned_to TEXT NOT NULL, -- Agent name (e.g., 'Qamar', 'Laila', 'Jalila')
  assigned_by TEXT DEFAULT 'Aaliyah', -- Who delegated it
  
  -- Task details
  title TEXT NOT NULL,
  description TEXT,
  task_type TEXT, -- 'delegation', 'blocker', 'follow_up', 'escalation', 'reminder'
  priority TEXT DEFAULT 'normal', -- 'urgent', 'high', 'normal', 'low'
  
  -- Status
  status TEXT DEFAULT 'pending', -- 'pending', 'acknowledged', 'in_progress', 'blocked', 'completed', 'cancelled'
  blocker_reason TEXT,
  progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
  
  -- Related entities (optional - link to what this task is about)
  lead_id BIGINT REFERENCES leads(id) ON DELETE SET NULL,
  deal_id BIGINT REFERENCES deals(id) ON DELETE SET NULL,
  campaign_id BIGINT REFERENCES campaigns(id) ON DELETE SET NULL,
  client_id UUID REFERENCES clients(client_id) ON DELETE SET NULL,
  company_id BIGINT REFERENCES companies(id) ON DELETE SET NULL,
  content_id BIGINT REFERENCES content(id) ON DELETE SET NULL,
  
  -- Tracking
  due_date TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  acknowledged_at TIMESTAMPTZ,
  
  -- Performance metrics
  time_to_acknowledge INTERVAL GENERATED ALWAYS AS (acknowledged_at - created_at) STORED,
  time_to_complete INTERVAL GENERATED ALWAYS AS (completed_at - created_at) STORED,
  
  -- Context & result
  context JSONB, -- Full context needed to complete task
  result JSONB, -- Output when completed
  checklist JSONB, -- [{item: "text", completed: false}]
  
  -- Dependencies
  depends_on_task_id BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
  blocks_task_id BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
  
  -- External references
  todoist_task_id TEXT,
  telegram_message_id TEXT,
  
  -- Metadata
  tags TEXT[],
  notes TEXT,
  reminder_count INTEGER DEFAULT 0, -- How many times I've chased this
  last_reminder_at TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_tasks_assigned_to ON agent_tasks(assigned_to) WHERE status NOT IN ('completed', 'cancelled');
CREATE INDEX idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX idx_agent_tasks_priority ON agent_tasks(priority) WHERE status = 'pending';
CREATE INDEX idx_agent_tasks_due_date ON agent_tasks(due_date) WHERE status NOT IN ('completed', 'cancelled');
CREATE INDEX idx_agent_tasks_lead_id ON agent_tasks(lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_agent_tasks_deal_id ON agent_tasks(deal_id) WHERE deal_id IS NOT NULL;
CREATE INDEX idx_agent_tasks_campaign_id ON agent_tasks(campaign_id) WHERE campaign_id IS NOT NULL;
CREATE INDEX idx_agent_tasks_client_id ON agent_tasks(client_id) WHERE client_id IS NOT NULL;
CREATE INDEX idx_agent_tasks_created_at ON agent_tasks(created_at DESC);

-- ============================================
-- AGENT_ACTIVITY - Agent Accountability Log
-- ============================================

CREATE TABLE IF NOT EXISTS agent_activity (
  id BIGSERIAL PRIMARY KEY,
  
  -- Agent
  agent_name TEXT NOT NULL,
  
  -- Activity
  activity_type TEXT NOT NULL, -- 'task_completed', 'task_acknowledged', 'message_sent', 'query_run', 'file_created', 'delegation_received', 'session_start', 'session_end'
  activity_summary TEXT,
  
  -- Related work
  task_id BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
  entity_type TEXT, -- 'lead', 'deal', 'campaign', 'client', 'content', 'invoice', 'communication'
  entity_id BIGINT,
  
  -- Performance metrics
  execution_time_ms INTEGER, -- How long the action took
  tokens_used INTEGER, -- For LLM calls
  
  -- Context
  session_key TEXT,
  tool_used TEXT, -- Which tool/script/skill was used
  
  -- Metadata
  metadata JSONB,
  
  -- Timestamp
  activity_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_activity_agent_name ON agent_activity(agent_name);
CREATE INDEX idx_agent_activity_activity_at ON agent_activity(activity_at DESC);
CREATE INDEX idx_agent_activity_activity_type ON agent_activity(activity_type);
CREATE INDEX idx_agent_activity_task_id ON agent_activity(task_id) WHERE task_id IS NOT NULL;
CREATE INDEX idx_agent_activity_entity ON agent_activity(entity_type, entity_id) WHERE entity_type IS NOT NULL;

-- View: Last activity per agent
CREATE OR REPLACE VIEW agent_last_activity AS
SELECT DISTINCT ON (agent_name)
  agent_name,
  activity_type,
  activity_summary,
  activity_at,
  EXTRACT(EPOCH FROM (NOW() - activity_at)) / 3600 AS hours_since_activity
FROM agent_activity
ORDER BY agent_name, activity_at DESC;

-- ============================================
-- HANDOFFS - Cross-Agent Coordination
-- ============================================

CREATE TABLE IF NOT EXISTS handoffs (
  id BIGSERIAL PRIMARY KEY,
  
  -- Handoff details
  from_agent TEXT NOT NULL,
  to_agent TEXT NOT NULL,
  handoff_type TEXT DEFAULT 'delegation', -- 'delegation', 'escalation', 'collaboration', 'blocker', 'return'
  
  -- Context
  subject TEXT NOT NULL,
  description TEXT,
  context JSONB, -- Full context for the receiving agent
  expected_output TEXT, -- What should be delivered back
  
  -- Status
  status TEXT DEFAULT 'pending', -- 'pending', 'acknowledged', 'in_progress', 'completed', 'returned', 'stalled'
  stall_reason TEXT,
  
  -- Related work
  task_id BIGINT REFERENCES agent_tasks(id) ON DELETE CASCADE,
  parent_handoff_id BIGINT REFERENCES handoffs(id) ON DELETE SET NULL, -- If this is a return handoff
  
  -- Related entities
  lead_id BIGINT REFERENCES leads(id) ON DELETE SET NULL,
  deal_id BIGINT REFERENCES deals(id) ON DELETE SET NULL,
  campaign_id BIGINT REFERENCES campaigns(id) ON DELETE SET NULL,
  client_id UUID REFERENCES clients(client_id) ON DELETE SET NULL,
  
  -- Tracking
  acknowledged_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  
  -- Performance metrics
  time_to_acknowledge INTERVAL GENERATED ALWAYS AS (acknowledged_at - created_at) STORED,
  time_to_complete INTERVAL GENERATED ALWAYS AS (completed_at - created_at) STORED,
  
  -- Result
  result JSONB, -- Output from receiving agent
  quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5), -- How good was the handoff completion
  
  -- Metadata
  priority TEXT DEFAULT 'normal',
  tags TEXT[],
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_handoffs_to_agent ON handoffs(to_agent) WHERE status NOT IN ('completed', 'returned');
CREATE INDEX idx_handoffs_from_agent ON handoffs(from_agent);
CREATE INDEX idx_handoffs_status ON handoffs(status);
CREATE INDEX idx_handoffs_task_id ON handoffs(task_id) WHERE task_id IS NOT NULL;
CREATE INDEX idx_handoffs_lead_id ON handoffs(lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_handoffs_deal_id ON handoffs(deal_id) WHERE deal_id IS NOT NULL;
CREATE INDEX idx_handoffs_created_at ON handoffs(created_at DESC);

-- View: Pending handoffs by agent
CREATE OR REPLACE VIEW pending_handoffs_by_agent AS
SELECT 
  to_agent,
  COUNT(*) AS pending_count,
  COUNT(*) FILTER (WHERE handoff_type = 'blocker') AS blocker_count,
  COUNT(*) FILTER (WHERE created_at < NOW() - INTERVAL '4 hours') AS stale_count,
  MAX(created_at) AS newest_handoff,
  MIN(created_at) AS oldest_handoff
FROM handoffs
WHERE status IN ('pending', 'acknowledged', 'in_progress')
GROUP BY to_agent;

-- ============================================
-- MEETINGS - Calendar Prep & Tracking
-- ============================================

CREATE TABLE IF NOT EXISTS meetings (
  id BIGSERIAL PRIMARY KEY,
  
  -- Meeting details
  title TEXT NOT NULL,
  meeting_type TEXT NOT NULL, -- 'discovery', 'client_call', 'internal', 'demo', 'follow_up', 'strategy', 'check_in'
  description TEXT,
  agenda TEXT,
  
  -- Attendees
  host TEXT DEFAULT 'Yasmine',
  attendees JSONB NOT NULL, -- [{name, email, role, confirmed}]
  internal_attendees TEXT[], -- Which agents should join/be aware
  
  -- Related entities
  lead_id BIGINT REFERENCES leads(id) ON DELETE SET NULL,
  deal_id BIGINT REFERENCES deals(id) ON DELETE SET NULL,
  client_id UUID REFERENCES clients(client_id) ON DELETE SET NULL,
  campaign_id BIGINT REFERENCES campaigns(id) ON DELETE SET NULL,
  
  -- Scheduling
  scheduled_at TIMESTAMPTZ NOT NULL,
  duration_minutes INTEGER DEFAULT 30,
  timezone TEXT DEFAULT 'America/New_York',
  
  -- Links
  meeting_url TEXT, -- Google Meet, Zoom, Cal.com
  calendar_event_id TEXT,
  calendar_provider TEXT, -- 'google', 'cal.com'
  
  -- Prep
  prep_doc_url TEXT, -- Google Doc I create with talking points
  prep_status TEXT DEFAULT 'not_started', -- 'not_started', 'in_progress', 'ready', 'approved'
  prep_completed_at TIMESTAMPTZ,
  prep_assigned_to TEXT, -- Usually 'Aaliyah', can delegate to Nadia
  prep_notes JSONB, -- Key talking points, context
  
  -- Materials
  materials JSONB, -- [{type: 'doc', url: '...', title: '...'}]
  
  -- Outcome
  status TEXT DEFAULT 'scheduled', -- 'scheduled', 'completed', 'no_show', 'rescheduled', 'cancelled'
  outcome TEXT, -- How did it go
  outcome_notes TEXT,
  next_steps TEXT[],
  follow_up_required BOOLEAN DEFAULT FALSE,
  follow_up_date DATE,
  
  -- Recording
  recording_url TEXT,
  transcript_url TEXT,
  
  -- Reminders
  reminder_24h_sent BOOLEAN DEFAULT FALSE,
  reminder_24h_sent_at TIMESTAMPTZ,
  reminder_2h_sent BOOLEAN DEFAULT FALSE,
  reminder_2h_sent_at TIMESTAMPTZ,
  prep_reminder_sent BOOLEAN DEFAULT FALSE,
  
  -- Metadata
  tags TEXT[],
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_meetings_scheduled_at ON meetings(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_meetings_prep_status ON meetings(prep_status) WHERE status = 'scheduled' AND prep_status != 'ready';
CREATE INDEX idx_meetings_lead_id ON meetings(lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_meetings_deal_id ON meetings(deal_id) WHERE deal_id IS NOT NULL;
CREATE INDEX idx_meetings_client_id ON meetings(client_id) WHERE client_id IS NOT NULL;
CREATE INDEX idx_meetings_type ON meetings(meeting_type);
CREATE INDEX idx_meetings_created_at ON meetings(created_at DESC);

-- View: Upcoming meetings needing prep
CREATE OR REPLACE VIEW meetings_needing_prep AS
SELECT 
  id,
  title,
  meeting_type,
  scheduled_at,
  prep_status,
  EXTRACT(EPOCH FROM (scheduled_at - NOW())) / 3600 AS hours_until_meeting,
  lead_id,
  deal_id,
  client_id
FROM meetings
WHERE status = 'scheduled'
  AND prep_status != 'ready'
  AND scheduled_at > NOW()
  AND scheduled_at < NOW() + INTERVAL '48 hours'
ORDER BY scheduled_at;

-- ============================================
-- RECOMMENDATIONS - Strategic Tracking
-- ============================================

CREATE TABLE IF NOT EXISTS recommendations (
  id BIGSERIAL PRIMARY KEY,
  
  -- Recommendation
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  rationale TEXT, -- Why this matters
  implementation_plan TEXT, -- How to execute
  
  -- Category
  category TEXT NOT NULL, -- 'process', 'revenue', 'automation', 'agent', 'client', 'content', 'product', 'hiring'
  subcategory TEXT,
  
  -- Priority assessment
  impact TEXT NOT NULL, -- 'high', 'medium', 'low'
  effort TEXT NOT NULL, -- 'high', 'medium', 'low'
  urgency TEXT, -- 'immediate', 'this_week', 'this_month', 'this_quarter'
  
  -- Expected outcomes
  expected_roi JSONB, -- {revenue_increase: 5000, time_saved_hours: 10, cost_reduction: 200}
  success_metrics TEXT[], -- How we'll measure success
  
  -- Status
  status TEXT DEFAULT 'proposed', -- 'proposed', 'under_review', 'approved', 'implementing', 'completed', 'rejected', 'deferred'
  
  -- Yasmine's feedback
  yasmine_feedback TEXT,
  yasmine_decision TEXT, -- 'approve', 'reject', 'defer', 'needs_more_info'
  yasmine_decision_at TIMESTAMPTZ,
  
  -- Implementation
  implemented_at TIMESTAMPTZ,
  implemented_by TEXT,
  
  -- Actual outcome
  actual_roi JSONB, -- Actual results if implemented
  outcome_notes TEXT,
  lessons_learned TEXT,
  
  -- Follow-up
  review_date DATE, -- When to check on results
  reviewed BOOLEAN DEFAULT FALSE,
  
  -- Related entities
  related_to_type TEXT, -- 'agent', 'campaign', 'client', 'process'
  related_to_id TEXT,
  
  -- Metadata
  proposed_by TEXT DEFAULT 'Aaliyah',
  evidence JSONB, -- Data supporting this recommendation
  risks TEXT[], -- Potential downsides
  alternatives TEXT[], -- Other options considered
  
  tags TEXT[],
  
  -- Timestamps
  proposed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_recommendations_status ON recommendations(status);
CREATE INDEX idx_recommendations_category ON recommendations(category);
CREATE INDEX idx_recommendations_impact ON recommendations(impact);
CREATE INDEX idx_recommendations_proposed_at ON recommendations(proposed_at DESC);
CREATE INDEX idx_recommendations_yasmine_decision ON recommendations(yasmine_decision) WHERE yasmine_decision IS NOT NULL;

-- View: High-impact pending recommendations
CREATE OR REPLACE VIEW high_impact_recommendations AS
SELECT 
  id,
  title,
  category,
  impact,
  effort,
  status,
  proposed_at,
  EXTRACT(EPOCH FROM (NOW() - proposed_at)) / 86400 AS days_pending
FROM recommendations
WHERE status IN ('proposed', 'under_review')
  AND impact = 'high'
ORDER BY 
  CASE urgency 
    WHEN 'immediate' THEN 1
    WHEN 'this_week' THEN 2
    WHEN 'this_month' THEN 3
    ELSE 4
  END,
  proposed_at;

-- ============================================
-- HEARTBEAT_CHECKS - Monitoring Log
-- ============================================

CREATE TABLE IF NOT EXISTS heartbeat_checks (
  id BIGSERIAL PRIMARY KEY,
  
  -- Check details
  check_type TEXT NOT NULL, -- 'gmail', 'pipeline', 'tasks', 'meetings', 'agents', 'deadlines', 'client_health', 'content_calendar', 'revenue'
  status TEXT NOT NULL, -- 'ok', 'action_taken', 'alert_sent', 'error'
  
  -- Findings
  findings JSONB, -- What I found {emails_scanned: 10, archived: 5, flagged: 2}
  actions_taken JSONB, -- What I did about it [{action: "archived_junk", count: 5}, {action: "drafted_reply", count: 2}]
  
  -- Issues detected
  issues_found INTEGER DEFAULT 0,
  critical_issues INTEGER DEFAULT 0,
  
  -- Alerts
  alert_level TEXT, -- 'info', 'warning', 'critical'
  alert_message TEXT,
  alerted_to TEXT[], -- Who I notified
  
  -- Performance
  check_duration_ms INTEGER, -- How long the check took
  
  -- Related entities (if check was about specific item)
  entity_type TEXT,
  entity_id BIGINT,
  
  -- Metadata
  metadata JSONB,
  error_message TEXT,
  
  -- Timestamp
  checked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_heartbeat_checks_check_type ON heartbeat_checks(check_type);
CREATE INDEX idx_heartbeat_checks_checked_at ON heartbeat_checks(checked_at DESC);
CREATE INDEX idx_heartbeat_checks_status ON heartbeat_checks(status);
CREATE INDEX idx_heartbeat_checks_alert_level ON heartbeat_checks(alert_level) WHERE alert_level IN ('warning', 'critical');

-- View: Recent heartbeat summary
CREATE OR REPLACE VIEW heartbeat_summary_24h AS
SELECT 
  check_type,
  COUNT(*) AS check_count,
  COUNT(*) FILTER (WHERE status = 'ok') AS ok_count,
  COUNT(*) FILTER (WHERE status = 'action_taken') AS action_count,
  COUNT(*) FILTER (WHERE alert_level = 'critical') AS critical_count,
  SUM(issues_found) AS total_issues,
  AVG(check_duration_ms) AS avg_duration_ms,
  MAX(checked_at) AS last_check
FROM heartbeat_checks
WHERE checked_at > NOW() - INTERVAL '24 hours'
GROUP BY check_type
ORDER BY last_check DESC;

-- ============================================
-- EMAIL_TRIAGE - Gmail Management
-- ============================================

CREATE TABLE IF NOT EXISTS email_triage (
  id BIGSERIAL PRIMARY KEY,
  
  -- Email details
  message_id TEXT UNIQUE NOT NULL,
  thread_id TEXT,
  from_email TEXT NOT NULL,
  from_name TEXT,
  to_email TEXT,
  subject TEXT,
  snippet TEXT, -- First 200 chars
  body_preview TEXT, -- First 500 chars
  
  -- Classification
  category TEXT NOT NULL, -- 'urgent', 'client', 'lead', 'financial', 'junk', 'automated', 'newsletter', 'personal', 'requires_yasmine', 'routine'
  confidence_score DECIMAL(3,2), -- 0.00-1.00 confidence in classification
  
  -- Triage decision
  action_taken TEXT NOT NULL, -- 'archived', 'flagged', 'drafted_reply', 'delegated', 'escalated', 'no_action'
  archive_reason TEXT, -- Why it was archived
  
  -- Delegation
  delegated_to TEXT, -- Which agent
  delegation_task_id BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
  draft_reply TEXT,
  draft_reply_approved BOOLEAN,
  
  -- Related entities (auto-linked)
  lead_id BIGINT REFERENCES leads(id) ON DELETE SET NULL,
  client_id UUID REFERENCES clients(client_id) ON DELETE SET NULL,
  deal_id BIGINT REFERENCES deals(id) ON DELETE SET NULL,
  invoice_id BIGINT REFERENCES invoices(id) ON DELETE SET NULL,
  
  -- Status
  needs_yasmine BOOLEAN DEFAULT FALSE,
  yasmine_handled BOOLEAN DEFAULT FALSE,
  yasmine_handled_at TIMESTAMPTZ,
  
  -- Follow-up
  follow_up_required BOOLEAN DEFAULT FALSE,
  follow_up_date DATE,
  follow_up_notes TEXT,
  
  -- Metadata
  labels TEXT[],
  has_attachments BOOLEAN DEFAULT FALSE,
  attachment_count INTEGER DEFAULT 0,
  importance TEXT, -- 'high', 'normal', 'low'
  
  -- Timestamps
  received_at TIMESTAMPTZ NOT NULL,
  triaged_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ
);

CREATE INDEX idx_email_triage_message_id ON email_triage(message_id);
CREATE INDEX idx_email_triage_thread_id ON email_triage(thread_id);
CREATE INDEX idx_email_triage_from_email ON email_triage(from_email);
CREATE INDEX idx_email_triage_category ON email_triage(category);
CREATE INDEX idx_email_triage_action_taken ON email_triage(action_taken);
CREATE INDEX idx_email_triage_needs_yasmine ON email_triage(needs_yasmine) WHERE needs_yasmine = TRUE;
CREATE INDEX idx_email_triage_lead_id ON email_triage(lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_email_triage_client_id ON email_triage(client_id) WHERE client_id IS NOT NULL;
CREATE INDEX idx_email_triage_received_at ON email_triage(received_at DESC);
CREATE INDEX idx_email_triage_triaged_at ON email_triage(triaged_at DESC);

-- View: Daily email stats
CREATE OR REPLACE VIEW email_triage_daily_stats AS
SELECT 
  DATE(triaged_at) AS date,
  COUNT(*) AS total_emails,
  COUNT(*) FILTER (WHERE action_taken = 'archived') AS archived,
  COUNT(*) FILTER (WHERE action_taken = 'flagged') AS flagged,
  COUNT(*) FILTER (WHERE action_taken = 'drafted_reply') AS drafts_created,
  COUNT(*) FILTER (WHERE action_taken = 'delegated') AS delegated,
  COUNT(*) FILTER (WHERE needs_yasmine = TRUE) AS needs_yasmine,
  COUNT(*) FILTER (WHERE category = 'junk') AS junk_filtered,
  ROUND(100.0 * COUNT(*) FILTER (WHERE action_taken = 'archived') / COUNT(*), 1) AS archive_rate_pct
FROM email_triage
WHERE triaged_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(triaged_at)
ORDER BY date DESC;

-- ============================================
-- UPDATE TRIGGERS
-- ============================================

CREATE TRIGGER update_agent_tasks_updated_at BEFORE UPDATE ON agent_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_handoffs_updated_at BEFORE UPDATE ON handoffs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at BEFORE UPDATE ON meetings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at BEFORE UPDATE ON recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function: Check for overdue tasks
CREATE OR REPLACE FUNCTION get_overdue_tasks()
RETURNS TABLE (
  task_id BIGINT,
  assigned_to TEXT,
  title TEXT,
  due_date TIMESTAMPTZ,
  hours_overdue NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    id,
    agent_tasks.assigned_to,
    agent_tasks.title,
    agent_tasks.due_date,
    ROUND(EXTRACT(EPOCH FROM (NOW() - agent_tasks.due_date)) / 3600, 1)
  FROM agent_tasks
  WHERE agent_tasks.due_date < NOW()
    AND status NOT IN ('completed', 'cancelled')
  ORDER BY agent_tasks.due_date;
END;
$$ LANGUAGE plpgsql;

-- Function: Get agent idle time
CREATE OR REPLACE FUNCTION get_idle_agents(idle_hours INTEGER DEFAULT 4)
RETURNS TABLE (
  agent_name TEXT,
  last_activity_type TEXT,
  last_activity_at TIMESTAMPTZ,
  hours_idle NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    a.agent_name,
    a.activity_type,
    a.activity_at,
    ROUND(EXTRACT(EPOCH FROM (NOW() - a.activity_at)) / 3600, 1)
  FROM agent_last_activity a
  WHERE EXTRACT(EPOCH FROM (NOW() - a.activity_at)) / 3600 > idle_hours
  ORDER BY a.activity_at;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- SAMPLE QUERIES FOR AALIYAH'S DASHBOARD
-- ============================================

-- Active tasks by agent
-- SELECT assigned_to, COUNT(*) as active_tasks, 
--   COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_tasks
-- FROM agent_tasks 
-- WHERE status NOT IN ('completed', 'cancelled') 
-- GROUP BY assigned_to;

-- Pending handoffs
-- SELECT * FROM pending_handoffs_by_agent WHERE pending_count > 0;

-- Meetings needing prep in next 24h
-- SELECT * FROM meetings_needing_prep WHERE hours_until_meeting < 24;

-- Recent heartbeat issues
-- SELECT check_type, alert_level, alert_message, checked_at 
-- FROM heartbeat_checks 
-- WHERE alert_level IN ('warning', 'critical') 
-- AND checked_at > NOW() - INTERVAL '24 hours'
-- ORDER BY checked_at DESC;

-- Emails waiting for Yasmine
-- SELECT from_email, subject, category, received_at 
-- FROM email_triage 
-- WHERE needs_yasmine = TRUE AND yasmine_handled = FALSE 
-- ORDER BY received_at;

-- High-impact recommendations pending decision
-- SELECT * FROM high_impact_recommendations;
