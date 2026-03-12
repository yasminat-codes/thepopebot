-- Add Sales & Revenue Tables to Existing Schema
-- Complements existing memory/client tables with sales pipeline
-- Created: 2026-02-23

-- ============================================
-- LEADS / PROSPECTS
-- ============================================

CREATE TABLE IF NOT EXISTS leads (
  id BIGSERIAL PRIMARY KEY,
  
  -- Contact Info
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  company TEXT,
  title TEXT,
  linkedin_url TEXT,
  
  -- Lead Source
  source TEXT, -- 'linkedin', 'cold_email', 'referral', 'inbound', 'instantly', 'heyreach'
  source_campaign_id TEXT,
  source_url TEXT,
  
  -- Status & Scoring
  status TEXT DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'disqualified', 'client'
  score INTEGER DEFAULT 0, -- 0-100 lead score
  priority TEXT, -- 'low', 'medium', 'high', 'urgent'
  
  -- Enrichment Data
  enrichment_data JSONB, -- From Scrapling, Apollo, etc.
  tech_stack TEXT[],
  team_size INTEGER,
  estimated_revenue TEXT,
  pain_points TEXT[],
  
  -- Assignment
  assigned_to TEXT, -- Agent handling this lead
  assigned_at TIMESTAMPTZ,
  
  -- Tracking
  first_contacted_at TIMESTAMPTZ,
  last_contacted_at TIMESTAMPTZ,
  last_response_at TIMESTAMPTZ,
  contact_count INTEGER DEFAULT 0,
  
  -- Metadata
  tags TEXT[],
  notes TEXT,
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_leads_status ON leads(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_email ON leads(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_company ON leads(company) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_assigned_to ON leads(assigned_to) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX idx_leads_enrichment ON leads USING GIN (enrichment_data);

-- ============================================
-- COMPANIES
-- ============================================

CREATE TABLE IF NOT EXISTS companies (
  id BIGSERIAL PRIMARY KEY,
  
  -- Basic Info
  name TEXT NOT NULL,
  domain TEXT UNIQUE,
  industry TEXT,
  description TEXT,
  
  -- Size & Details
  employee_count INTEGER,
  estimated_revenue TEXT,
  founded_year INTEGER,
  location TEXT,
  
  -- Tech & Tools
  tech_stack TEXT[],
  tools_used TEXT[],
  
  -- Enrichment
  enrichment_data JSONB,
  linkedin_url TEXT,
  twitter_url TEXT,
  facebook_url TEXT,
  
  -- Relationship
  relationship_status TEXT, -- 'prospect', 'client', 'past_client', 'partner'
  
  -- Metadata
  tags TEXT[],
  notes TEXT,
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_companies_domain ON companies(domain) WHERE deleted_at IS NULL;
CREATE INDEX idx_companies_name ON companies(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_companies_status ON companies(relationship_status) WHERE deleted_at IS NULL;

-- Link leads to companies
ALTER TABLE leads ADD COLUMN IF NOT EXISTS company_id BIGINT REFERENCES companies(id);
CREATE INDEX idx_leads_company_id ON leads(company_id) WHERE deleted_at IS NULL;

-- ============================================
-- DEALS / PIPELINE
-- ============================================

CREATE TABLE IF NOT EXISTS deals (
  id BIGSERIAL PRIMARY KEY,
  
  -- Deal Info
  name TEXT NOT NULL,
  description TEXT,
  
  -- Relationships
  lead_id BIGINT REFERENCES leads(id),
  company_id BIGINT REFERENCES companies(id),
  client_id UUID REFERENCES clients(client_id), -- Link to existing clients table
  
  -- Pipeline Stage
  stage TEXT DEFAULT 'discovery', -- 'discovery', 'proposal', 'negotiation', 'closed_won', 'closed_lost'
  stage_changed_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Value
  value DECIMAL(10, 2),
  currency TEXT DEFAULT 'USD',
  probability INTEGER DEFAULT 50, -- 0-100%
  weighted_value DECIMAL(10, 2) GENERATED ALWAYS AS (value * probability / 100) STORED,
  
  -- Dates
  expected_close_date DATE,
  actual_close_date DATE,
  
  -- Assignment
  owner TEXT, -- Agent responsible
  assigned_to TEXT[], -- Multiple agents can work on it
  
  -- Source
  source TEXT, -- How did this deal originate
  source_campaign_id TEXT,
  
  -- External IDs
  ghl_deal_id TEXT,
  airtable_record_id TEXT,
  
  -- Metadata
  tags TEXT[],
  notes TEXT,
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_deals_stage ON deals(stage) WHERE deleted_at IS NULL;
CREATE INDEX idx_deals_owner ON deals(owner) WHERE deleted_at IS NULL;
CREATE INDEX idx_deals_expected_close ON deals(expected_close_date) WHERE deleted_at IS NULL;
CREATE INDEX idx_deals_value ON deals(value DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_deals_lead_id ON deals(lead_id);
CREATE INDEX idx_deals_company_id ON deals(company_id);

-- ============================================
-- CAMPAIGNS
-- ============================================

CREATE TABLE IF NOT EXISTS campaigns (
  id BIGSERIAL PRIMARY KEY,
  
  -- Campaign Info
  name TEXT NOT NULL,
  description TEXT,
  channel TEXT NOT NULL, -- 'email', 'linkedin', 'phone', 'ads'
  campaign_type TEXT, -- 'cold_outreach', 'warm_follow_up', 'nurture', 'reactivation'
  
  -- Status
  status TEXT DEFAULT 'draft', -- 'draft', 'active', 'paused', 'completed', 'archived'
  
  -- Targeting
  target_audience TEXT,
  target_count INTEGER,
  icp_criteria JSONB,
  
  -- Performance
  sent_count INTEGER DEFAULT 0,
  delivered_count INTEGER DEFAULT 0,
  opened_count INTEGER DEFAULT 0,
  replied_count INTEGER DEFAULT 0,
  clicked_count INTEGER DEFAULT 0,
  converted_count INTEGER DEFAULT 0,
  
  -- Dates
  start_date DATE,
  end_date DATE,
  
  -- Assignment
  owner TEXT,
  
  -- External IDs
  instantly_campaign_id TEXT,
  heyreach_campaign_id TEXT,
  
  -- A/B Testing
  ab_test_id BIGINT,
  variant TEXT, -- 'control', 'variant_a', 'variant_b'
  
  -- Metadata
  tags TEXT[],
  notes TEXT,
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_campaigns_status ON campaigns(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_campaigns_channel ON campaigns(channel) WHERE deleted_at IS NULL;
CREATE INDEX idx_campaigns_owner ON campaigns(owner) WHERE deleted_at IS NULL;

-- ============================================
-- COMMUNICATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS communications (
  id BIGSERIAL PRIMARY KEY,
  
  -- Relationships
  lead_id BIGINT REFERENCES leads(id),
  deal_id BIGINT REFERENCES deals(id),
  campaign_id BIGINT REFERENCES campaigns(id),
  
  -- Communication Details
  channel TEXT NOT NULL, -- 'email', 'linkedin', 'phone', 'sms'
  direction TEXT, -- 'inbound', 'outbound'
  
  -- Content
  subject TEXT,
  body TEXT,
  snippet TEXT, -- First 200 chars
  
  -- Status
  status TEXT, -- 'sent', 'delivered', 'opened', 'replied', 'bounced', 'failed'
  
  -- Engagement
  opened_at TIMESTAMPTZ,
  replied_at TIMESTAMPTZ,
  clicked_at TIMESTAMPTZ,
  
  -- External IDs
  message_id TEXT,
  thread_id TEXT,
  external_id TEXT,
  
  -- Metadata
  metadata JSONB,
  
  -- Timestamps
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_communications_lead_id ON communications(lead_id);
CREATE INDEX idx_communications_deal_id ON communications(deal_id);
CREATE INDEX idx_communications_campaign_id ON communications(campaign_id);
CREATE INDEX idx_communications_channel ON communications(channel);
CREATE INDEX idx_communications_sent_at ON communications(sent_at DESC);

-- ============================================
-- REVENUE / INVOICES
-- ============================================

CREATE TABLE IF NOT EXISTS invoices (
  id BIGSERIAL PRIMARY KEY,
  
  -- Relationships
  client_id UUID REFERENCES clients(client_id),
  deal_id BIGINT REFERENCES deals(id),
  
  -- Invoice Details
  invoice_number TEXT UNIQUE NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  currency TEXT DEFAULT 'USD',
  
  -- Status
  status TEXT DEFAULT 'draft', -- 'draft', 'sent', 'paid', 'overdue', 'cancelled'
  
  -- Dates
  issue_date DATE NOT NULL,
  due_date DATE NOT NULL,
  paid_at TIMESTAMPTZ,
  
  -- External IDs
  stripe_invoice_id TEXT,
  quickbooks_invoice_id TEXT,
  
  -- Metadata
  line_items JSONB,
  notes TEXT,
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_invoices_client_id ON invoices(client_id);
CREATE INDEX idx_invoices_status ON invoices(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_invoices_due_date ON invoices(due_date) WHERE deleted_at IS NULL AND status != 'paid';
CREATE INDEX idx_invoices_stripe_id ON invoices(stripe_invoice_id);

-- ============================================
-- PAYMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS payments (
  id BIGSERIAL PRIMARY KEY,
  
  -- Relationships
  invoice_id BIGINT REFERENCES invoices(id),
  client_id UUID REFERENCES clients(client_id),
  
  -- Payment Details
  amount DECIMAL(10, 2) NOT NULL,
  currency TEXT DEFAULT 'USD',
  payment_method TEXT, -- 'card', 'ach', 'wire', 'check'
  
  -- Status
  status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
  
  -- External IDs
  stripe_payment_id TEXT,
  stripe_charge_id TEXT,
  
  -- Metadata
  metadata JSONB,
  
  -- Timestamps
  paid_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_invoice_id ON payments(invoice_id);
CREATE INDEX idx_payments_client_id ON payments(client_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_paid_at ON payments(paid_at DESC);

-- ============================================
-- CONTENT
-- ============================================

CREATE TABLE IF NOT EXISTS content (
  id BIGSERIAL PRIMARY KEY,
  
  -- Content Info
  title TEXT NOT NULL,
  slug TEXT UNIQUE,
  type TEXT NOT NULL, -- 'blog_post', 'linkedin_post', 'twitter_post', 'newsletter', 'case_study'
  
  -- Content
  body TEXT,
  excerpt TEXT,
  
  -- Status
  status TEXT DEFAULT 'draft', -- 'draft', 'scheduled', 'published', 'archived'
  
  -- Publishing
  published_at TIMESTAMPTZ,
  scheduled_for TIMESTAMPTZ,
  
  -- Metadata
  author TEXT,
  tags TEXT[],
  category TEXT,
  seo_title TEXT,
  seo_description TEXT,
  
  -- Performance
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  
  -- External IDs
  linkedin_post_id TEXT,
  twitter_post_id TEXT,
  medium_post_id TEXT,
  
  -- Metadata
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_content_type ON content(type) WHERE deleted_at IS NULL;
CREATE INDEX idx_content_status ON content(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_content_published_at ON content(published_at DESC) WHERE status = 'published';
CREATE INDEX idx_content_author ON content(author) WHERE deleted_at IS NULL;

-- ============================================
-- A/B TESTS
-- ============================================

CREATE TABLE IF NOT EXISTS ab_tests (
  id BIGSERIAL PRIMARY KEY,
  
  -- Test Info
  name TEXT NOT NULL,
  description TEXT,
  hypothesis TEXT,
  
  -- Status
  status TEXT DEFAULT 'draft', -- 'draft', 'running', 'paused', 'completed'
  
  -- Configuration
  test_type TEXT, -- 'email_subject', 'email_body', 'cta', 'landing_page', 'ad_creative'
  variants JSONB, -- Array of variant configurations
  
  -- Results
  control_conversions INTEGER DEFAULT 0,
  control_total INTEGER DEFAULT 0,
  variant_conversions JSONB, -- {variant_a: X, variant_b: Y}
  variant_totals JSONB,
  
  -- Winner
  winning_variant TEXT,
  confidence_level DECIMAL(5, 2),
  
  -- Dates
  start_date DATE,
  end_date DATE,
  
  -- Metadata
  metadata JSONB,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ab_tests_status ON ab_tests(status);
CREATE INDEX idx_ab_tests_type ON ab_tests(test_type);

-- ============================================
-- UPDATE TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON deals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ab_tests_updated_at BEFORE UPDATE ON ab_tests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
