-- Migration 020: Qamar A/B Tests v2 Schema Upgrade
-- Agent: Qamar — Cold Email Specialist
-- Purpose: Extend qamar_ab_tests with full lifecycle columns, Instantly integration, 5-step strategy support
-- Created: 2026-02-27

-- ============================================================================
-- ALTER EXISTING TABLE: qamar_ab_tests
-- ============================================================================

-- Natural key for human-readable test identification
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS test_id TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_qamar_ab_tests_test_id ON qamar_ab_tests(test_id);

-- Campaign linkage
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS campaign_id BIGINT REFERENCES campaigns(id);
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS campaign_name TEXT;

-- Test configuration
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS test_element TEXT;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS hypothesis TEXT;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS primary_metric TEXT DEFAULT 'reply_rate';
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS secondary_metrics JSONB DEFAULT '["open_rate","positive_reply_rate"]'::jsonb;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS min_sends_per_variant INT DEFAULT 100;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS confidence_threshold NUMERIC DEFAULT 0.95;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS variants JSONB;

-- Results
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS variant_results JSONB;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS winner_variant TEXT;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS winning_reason TEXT;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS winner_declared_at TIMESTAMPTZ;

-- Context
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS niche TEXT;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS icp TEXT;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS patterns_observed JSONB DEFAULT '[]'::jsonb;

-- Snapshots (timestamped metric snapshots array)
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS snapshots JSONB DEFAULT '[]'::jsonb;

-- 5-Step A/B Testing Strategy fields
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS test_priority TEXT;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS audience_segment TEXT;

-- Revenue attribution
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS positive_reply_count INT DEFAULT 0;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS booked_calls INT DEFAULT 0;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS closed_deals INT DEFAULT 0;

-- Instantly integration
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS instantly_campaign_id TEXT;

-- Analysis results
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS last_analysis JSONB;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS final_analysis JSONB;

-- Lifecycle timestamps
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS start_date DATE;
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS completed_date DATE;

-- Status field (ensure it exists)
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'setup';

-- Timestamps
ALTER TABLE qamar_ab_tests ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- ============================================================================
-- CHECK CONSTRAINTS
-- ============================================================================

-- Status constraint (drop if exists, then create)
DO $$
BEGIN
    ALTER TABLE qamar_ab_tests DROP CONSTRAINT IF EXISTS chk_qamar_ab_tests_status;
    ALTER TABLE qamar_ab_tests ADD CONSTRAINT chk_qamar_ab_tests_status
        CHECK (status IN ('setup', 'active', 'paused', 'completed', 'complete', 'invalidated'));
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not add status constraint: %', SQLERRM;
END;
$$;

-- Test element constraint
DO $$
BEGIN
    ALTER TABLE qamar_ab_tests DROP CONSTRAINT IF EXISTS chk_qamar_ab_tests_element;
    ALTER TABLE qamar_ab_tests ADD CONSTRAINT chk_qamar_ab_tests_element
        CHECK (test_element IS NULL OR test_element IN (
            'subject_line', 'body_copy', 'cta', 'send_time',
            'offer', 'follow_up', 'audience'
        ));
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not add element constraint: %', SQLERRM;
END;
$$;

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_qamar_ab_tests_campaign_status
    ON qamar_ab_tests(campaign_id, status);

CREATE INDEX IF NOT EXISTS idx_qamar_ab_tests_status
    ON qamar_ab_tests(status);

CREATE INDEX IF NOT EXISTS idx_qamar_ab_tests_niche
    ON qamar_ab_tests(niche);

CREATE INDEX IF NOT EXISTS idx_qamar_ab_tests_instantly
    ON qamar_ab_tests(instantly_campaign_id)
    WHERE instantly_campaign_id IS NOT NULL;

-- ============================================================================
-- END MIGRATION
-- ============================================================================
