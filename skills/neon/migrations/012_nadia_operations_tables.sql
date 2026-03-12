-- Migration 012: Nadia Operations Infrastructure  
-- Agent: Nadia — Operations Manager
-- Purpose: SOPs, project templates, resource allocation, process improvements, WBS, checklists
-- Created: 2026-02-23

-- 1. SOPS
CREATE TABLE sops (
    id BIGSERIAL PRIMARY KEY,
    sop_title VARCHAR(255) NOT NULL,
    sop_number VARCHAR(50) UNIQUE,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    purpose TEXT,
    scope TEXT,
    steps JSONB NOT NULL,
    owner VARCHAR(100),
    last_reviewed_by VARCHAR(100),
    last_reviewed_date DATE,
    next_review_date DATE,
    version VARCHAR(20) DEFAULT '1.0',
    version_history JSONB,
    related_sops JSONB,
    prerequisites JSONB,
    times_referenced INTEGER DEFAULT 0,
    avg_completion_time_minutes INTEGER,
    compliance_required BOOLEAN DEFAULT false,
    quality_checkpoints JSONB,
    status VARCHAR(50) DEFAULT 'active',
    doc_url TEXT,
    video_url TEXT,
    template_urls JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sops_category ON sops(category);
CREATE INDEX idx_sops_status ON sops(status);

-- 2. PROJECT TEMPLATES
CREATE TABLE project_templates (
    id BIGSERIAL PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,
    project_type VARCHAR(100),
    phases JSONB NOT NULL,
    milestones JSONB,
    estimated_hours INTEGER,
    team_roles_needed JSONB,
    typical_duration_days INTEGER,
    base_price DECIMAL(12,2),
    pricing_model VARCHAR(50),
    tools_required JSONB,
    tech_stack JSONB,
    times_used INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_project_templates_type ON project_templates(project_type);
CREATE INDEX idx_project_templates_status ON project_templates(status);

-- 3. RESOURCE ALLOCATION
CREATE TABLE resource_allocation (
    id BIGSERIAL PRIMARY KEY,
    resource_name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    total_capacity_hours DECIMAL(5,2) DEFAULT 40.00,
    allocated_hours DECIMAL(5,2) DEFAULT 0.00,
    available_hours DECIMAL(5,2),
    utilization_percentage DECIMAL(5,2),
    allocations JSONB,
    overallocated BOOLEAN DEFAULT false,
    underutilized BOOLEAN DEFAULT false,
    scheduling_conflicts JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resource_allocation_name ON resource_allocation(resource_name);
CREATE INDEX idx_resource_allocation_week ON resource_allocation(week_start_date);

-- 4. PROCESS IMPROVEMENTS
CREATE TABLE process_improvements (
    id BIGSERIAL PRIMARY KEY,
    improvement_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    current_process TEXT,
    pain_points JSONB,
    proposed_solution TEXT NOT NULL,
    expected_benefits JSONB,
    time_savings_estimate VARCHAR(50),
    cost_savings_estimate DECIMAL(12,2),
    quality_improvement TEXT,
    implementation_steps JSONB,
    estimated_implementation_effort VARCHAR(50),
    required_resources TEXT,
    status VARCHAR(50) DEFAULT 'identified',
    proposed_by VARCHAR(100),
    approved_by VARCHAR(100),
    implemented_by VARCHAR(100),
    proposed_date DATE,
    approved_date DATE,
    implementation_date DATE,
    actual_benefits JSONB,
    lessons_learned TEXT,
    related_sop_id BIGINT REFERENCES sops(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_process_improvements_status ON process_improvements(status);

-- 5. WORK BREAKDOWN STRUCTURE
CREATE TABLE work_breakdown_structure (
    id BIGSERIAL PRIMARY KEY,
    project_id UUID,
    project_name VARCHAR(255),
    wbs_level INTEGER NOT NULL,
    parent_wbs_id BIGINT REFERENCES work_breakdown_structure(id),
    wbs_code VARCHAR(50),
    task_name VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to VARCHAR(100),
    role_required VARCHAR(100),
    estimated_hours DECIMAL(5,2),
    start_date DATE,
    end_date DATE,
    duration_days INTEGER,
    dependencies JSONB,
    status VARCHAR(50) DEFAULT 'not_started',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    actual_hours DECIMAL(5,2),
    completed_date DATE,
    deliverables JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_wbs_project ON work_breakdown_structure(project_id);
CREATE INDEX idx_wbs_status ON work_breakdown_structure(status);

-- 6. OPERATIONAL CHECKLISTS
CREATE TABLE operational_checklists (
    id BIGSERIAL PRIMARY KEY,
    checklist_name VARCHAR(255) NOT NULL,
    description TEXT,
    checklist_type VARCHAR(50),
    checklist_items JSONB NOT NULL,
    total_items INTEGER,
    frequency VARCHAR(50),
    estimated_completion_time_minutes INTEGER,
    related_sop_id BIGINT REFERENCES sops(id),
    status VARCHAR(50) DEFAULT 'active',
    template_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_checklists_type ON operational_checklists(checklist_type);

-- 7. CHECKLIST EXECUTIONS
CREATE TABLE checklist_executions (
    id BIGSERIAL PRIMARY KEY,
    checklist_id BIGINT REFERENCES operational_checklists(id),
    execution_date DATE NOT NULL,
    executed_by VARCHAR(100) NOT NULL,
    related_project_id UUID,
    related_client_id UUID,
    items_completed JSONB,
    completion_percentage DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'in_progress',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_minutes INTEGER,
    all_items_completed BOOLEAN DEFAULT false,
    skipped_items JSONB,
    issues_found JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_checklist_executions_checklist ON checklist_executions(checklist_id);
CREATE INDEX idx_checklist_executions_date ON checklist_executions(execution_date DESC);

-- ENHANCE AGENT_TASKS
ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS project_id UUID;
ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS wbs_id BIGINT REFERENCES work_breakdown_structure(id);
ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS sop_id BIGINT REFERENCES sops(id);
ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS estimated_hours DECIMAL(5,2);
ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS actual_hours DECIMAL(5,2);
ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS blocked BOOLEAN DEFAULT false;
ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS blocker_description TEXT;

CREATE INDEX IF NOT EXISTS idx_agent_tasks_project ON agent_tasks(project_id);
