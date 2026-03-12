-- Migration 008: Maida Finance Infrastructure
-- Agent: Maida — Finance Manager
-- Purpose: Stripe sync, expenses, budgets, forecasts, reminders, reports, tax records
-- Created: 2026-02-23

-- 1. STRIPE SYNC LOG
CREATE TABLE stripe_sync_log (
    id BIGSERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    stripe_id VARCHAR(255),
    request_payload JSONB,
    response_payload JSONB,
    http_status INTEGER,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    duration_ms INTEGER,
    reconciled BOOLEAN DEFAULT false,
    reconciled_at TIMESTAMP,
    discrepancy_notes TEXT,
    synced_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stripe_sync_type ON stripe_sync_log(sync_type);
CREATE INDEX idx_stripe_sync_status ON stripe_sync_log(status);
CREATE INDEX idx_stripe_sync_date ON stripe_sync_log(synced_at DESC);

-- 2. EXPENSES
CREATE TABLE expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_date DATE NOT NULL,
    vendor VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    payment_method VARCHAR(50),
    payment_account VARCHAR(100),
    project_id BIGINT,
    client_id BIGINT,
    billable BOOLEAN DEFAULT false,
    reimbursed BOOLEAN DEFAULT false,
    status VARCHAR(50) DEFAULT 'pending',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    tax_deductible BOOLEAN DEFAULT true,
    tax_category VARCHAR(50),
    receipt_url TEXT,
    receipt_uploaded BOOLEAN DEFAULT false,
    stripe_charge_id VARCHAR(255),
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_expenses_date ON expenses(expense_date DESC);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_status ON expenses(status);

-- 3. BUDGETS
CREATE TABLE budgets (
    id BIGSERIAL PRIMARY KEY,
    period_type VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    budgeted_amount DECIMAL(12,2) NOT NULL,
    spent_amount DECIMAL(12,2) DEFAULT 0.00,
    remaining_amount DECIMAL(12,2),
    utilization_percentage DECIMAL(5,2),
    alert_threshold DECIMAL(5,2) DEFAULT 80.00,
    alert_triggered BOOLEAN DEFAULT false,
    alert_sent_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    description TEXT,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_budgets_period ON budgets(period_start, period_end);
CREATE INDEX idx_budgets_category ON budgets(category);

-- 4. REVENUE FORECASTS
CREATE TABLE revenue_forecasts (
    id BIGSERIAL PRIMARY KEY,
    forecast_month DATE NOT NULL,
    forecast_quarter VARCHAR(10),
    existing_mrr DECIMAL(12,2) DEFAULT 0.00,
    new_deals_expected DECIMAL(12,2) DEFAULT 0.00,
    renewals_expected DECIMAL(12,2) DEFAULT 0.00,
    churn_expected DECIMAL(12,2) DEFAULT 0.00,
    total_forecast DECIMAL(12,2),
    confidence_level VARCHAR(50),
    confidence_percentage DECIMAL(5,2),
    actual_revenue DECIMAL(12,2),
    variance DECIMAL(12,2),
    variance_percentage DECIMAL(5,2),
    pipeline_snapshot JSONB,
    assumptions JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    finalized_by VARCHAR(100),
    finalized_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_revenue_forecasts_month ON revenue_forecasts(forecast_month DESC);

-- 5. PAYMENT REMINDERS
CREATE TABLE payment_reminders (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT REFERENCES invoices(id),
    reminder_type VARCHAR(50) NOT NULL,
    reminder_number INTEGER,
    scheduled_for TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    sent_via VARCHAR(50),
    message_template VARCHAR(100),
    message_body TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    client_responded BOOLEAN DEFAULT false,
    client_response TEXT,
    automated BOOLEAN DEFAULT true,
    requires_manual_review BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payment_reminders_invoice ON payment_reminders(invoice_id);
CREATE INDEX idx_payment_reminders_scheduled ON payment_reminders(scheduled_for);

-- 6. FINANCIAL REPORTS
CREATE TABLE financial_reports (
    id BIGSERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    report_period_start DATE NOT NULL,
    report_period_end DATE NOT NULL,
    report_data JSONB NOT NULL,
    total_revenue DECIMAL(12,2),
    total_expenses DECIMAL(12,2),
    net_income DECIMAL(12,2),
    gross_margin_percentage DECIMAL(5,2),
    google_doc_url TEXT,
    pdf_url TEXT,
    spreadsheet_url TEXT,
    generated_by VARCHAR(100),
    generated_at TIMESTAMP NOT NULL,
    shared_with JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_financial_reports_type ON financial_reports(report_type);
CREATE INDEX idx_financial_reports_generated ON financial_reports(generated_at DESC);

-- 7. TAX RECORDS
CREATE TABLE tax_records (
    id BIGSERIAL PRIMARY KEY,
    tax_year INTEGER NOT NULL,
    tax_quarter INTEGER,
    record_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    category VARCHAR(100),
    source_type VARCHAR(50),
    source_id BIGINT,
    tax_form VARCHAR(50),
    tax_line_item VARCHAR(100),
    supporting_docs JSONB,
    receipt_url TEXT,
    reviewed BOOLEAN DEFAULT false,
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    included_in_filing BOOLEAN DEFAULT false,
    filing_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tax_records_year ON tax_records(tax_year DESC);

-- ENHANCE INVOICES
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS stripe_invoice_id VARCHAR(255);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_link TEXT;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS reminder_count INTEGER DEFAULT 0;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS last_reminder_sent TIMESTAMP;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS next_reminder_due TIMESTAMP;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS days_overdue INTEGER;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS collection_status VARCHAR(50);

CREATE INDEX IF NOT EXISTS idx_invoices_stripe_id ON invoices(stripe_invoice_id);

-- ENHANCE PAYMENTS
ALTER TABLE payments ADD COLUMN IF NOT EXISTS stripe_payment_id VARCHAR(255);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS payment_method_type VARCHAR(50);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS card_brand VARCHAR(50);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS card_last4 VARCHAR(4);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS failure_reason TEXT;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS refunded BOOLEAN DEFAULT false;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(12,2);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS refund_reason TEXT;

CREATE INDEX IF NOT EXISTS idx_payments_stripe_id ON payments(stripe_payment_id);
