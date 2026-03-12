-- Migration 014: Rahmah (Wellbeing Specialist) Tables
-- Domain: Mental health support, work-life balance, stress management, wellness tracking
-- Agent: Rahmah (@SageWellnessBot)
-- Created: 2025-01-27

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- 1. Wellness Check-ins
CREATE TABLE IF NOT EXISTS wellness_check_ins (
    id BIGSERIAL PRIMARY KEY,
    check_in_date DATE NOT NULL,
    check_in_type TEXT CHECK (check_in_type IN ('daily', 'weekly', 'monthly', 'on_demand', 'crisis')),
    mood_rating INTEGER CHECK (mood_rating BETWEEN 1 AND 10),
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 10),
    work_hours NUMERIC(4, 1),
    breaks_taken INTEGER,
    exercise_completed BOOLEAN DEFAULT FALSE,
    meals_quality INTEGER CHECK (meals_quality BETWEEN 1 AND 5),
    social_connection BOOLEAN DEFAULT FALSE,
    key_stressors TEXT[],
    wins_today TEXT[],
    gratitude_notes TEXT,
    self_care_activities TEXT[],
    support_needed TEXT,
    notes TEXT,
    google_doc_id TEXT,
    google_doc_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'rahmah'
);

CREATE INDEX idx_wellness_check_ins_date ON wellness_check_ins(check_in_date DESC);
CREATE INDEX idx_wellness_check_ins_type ON wellness_check_ins(check_in_type, check_in_date DESC);
CREATE INDEX idx_wellness_check_ins_stress ON wellness_check_ins(stress_level DESC, check_in_date DESC) WHERE stress_level >= 7;

COMMENT ON TABLE wellness_check_ins IS 'Regular wellness check-ins with mood, energy, stress tracking';

-- 2. Burnout Risk Assessments
CREATE TABLE IF NOT EXISTS burnout_risk_assessments (
    id BIGSERIAL PRIMARY KEY,
    assessment_date DATE NOT NULL,
    emotional_exhaustion_score INTEGER CHECK (emotional_exhaustion_score BETWEEN 1 AND 10),
    depersonalization_score INTEGER CHECK (depersonalization_score BETWEEN 1 AND 10),
    personal_accomplishment_score INTEGER CHECK (personal_accomplishment_score BETWEEN 1 AND 10),
    overall_burnout_score NUMERIC(4, 1),
    risk_level TEXT CHECK (risk_level IN ('low', 'moderate', 'high', 'critical')),
    contributing_factors TEXT[],
    protective_factors TEXT[],
    immediate_actions_needed TEXT[],
    recommended_interventions TEXT[],
    follow_up_date DATE,
    google_doc_url TEXT,
    assessed_by TEXT DEFAULT 'rahmah',
    notes TEXT
);

CREATE INDEX idx_burnout_assessments_date ON burnout_risk_assessments(assessment_date DESC);
CREATE INDEX idx_burnout_risk_level ON burnout_risk_assessments(risk_level, assessment_date DESC) WHERE risk_level IN ('high', 'critical');

COMMENT ON TABLE burnout_risk_assessments IS 'Periodic burnout risk evaluation';

-- 3. Wellness Goals
CREATE TABLE IF NOT EXISTS wellness_goals (
    id BIGSERIAL PRIMARY KEY,
    goal_category TEXT CHECK (goal_category IN ('sleep', 'exercise', 'nutrition', 'stress_management', 'work_life_balance', 'social_connection', 'mindfulness', 'boundaries', 'recovery', 'joy')),
    goal_title TEXT NOT NULL,
    goal_description TEXT NOT NULL,
    target_metric TEXT,
    target_value TEXT,
    current_baseline TEXT,
    start_date DATE NOT NULL,
    target_date DATE,
    frequency TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'on_hold', 'completed', 'abandoned')),
    progress_percentage INTEGER CHECK (progress_percentage BETWEEN 0 AND 100) DEFAULT 0,
    barriers TEXT[],
    supports TEXT[],
    celebration_plan TEXT,
    completed_at DATE,
    google_doc_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'rahmah',
    notes TEXT
);

CREATE INDEX idx_wellness_goals_status ON wellness_goals(status, goal_category);
CREATE INDEX idx_wellness_goals_dates ON wellness_goals(target_date, status) WHERE status = 'active';

COMMENT ON TABLE wellness_goals IS 'Personal wellness goals and targets';

-- 4. Wellness Interventions
CREATE TABLE IF NOT EXISTS wellness_interventions (
    id BIGSERIAL PRIMARY KEY,
    intervention_date DATE NOT NULL,
    trigger_signal TEXT NOT NULL,
    intervention_type TEXT CHECK (intervention_type IN ('break_reminder', 'boundary_setting', 'stress_relief', 'energy_boost', 'sleep_hygiene', 'social_support', 'professional_help', 'time_off', 'workload_adjustment', 'mindfulness_practice')),
    intervention_title TEXT NOT NULL,
    intervention_description TEXT NOT NULL,
    urgency TEXT CHECK (urgency IN ('routine', 'elevated', 'urgent', 'crisis')),
    implementation_status TEXT NOT NULL DEFAULT 'suggested' CHECK (implementation_status IN ('suggested', 'accepted', 'in_progress', 'completed', 'declined', 'deferred')),
    implemented_at TIMESTAMPTZ,
    outcome TEXT,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    follow_up_needed BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    google_doc_url TEXT,
    created_by TEXT DEFAULT 'rahmah',
    notes TEXT
);

CREATE INDEX idx_wellness_interventions_date ON wellness_interventions(intervention_date DESC);
CREATE INDEX idx_wellness_interventions_status ON wellness_interventions(implementation_status, urgency);
CREATE INDEX idx_wellness_interventions_type ON wellness_interventions(intervention_type, intervention_date DESC);

COMMENT ON TABLE wellness_interventions IS 'Suggested and implemented wellness interventions';

-- 5. Stress Signals
CREATE TABLE IF NOT EXISTS stress_signals (
    id BIGSERIAL PRIMARY KEY,
    signal_date DATE NOT NULL,
    signal_type TEXT CHECK (signal_type IN ('physical', 'emotional', 'behavioral', 'cognitive', 'work_pattern', 'communication_change')),
    signal_description TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('mild', 'moderate', 'significant', 'severe')),
    frequency TEXT CHECK (frequency IN ('isolated', 'occasional', 'frequent', 'persistent')),
    duration TEXT,
    context TEXT,
    related_stressors TEXT[],
    action_taken TEXT,
    resolution_status TEXT CHECK (resolution_status IN ('monitoring', 'intervened', 'resolved', 'escalated')),
    resolved_at DATE,
    detected_by TEXT DEFAULT 'rahmah',
    notes TEXT
);

CREATE INDEX idx_stress_signals_date ON stress_signals(signal_date DESC);
CREATE INDEX idx_stress_signals_severity ON stress_signals(severity, resolution_status) WHERE resolution_status IN ('monitoring', 'intervened');
CREATE INDEX idx_stress_signals_type ON stress_signals(signal_type, signal_date DESC);

COMMENT ON TABLE stress_signals IS 'Early warning signals for stress and burnout';

-- 6. Self-Care Activities
CREATE TABLE IF NOT EXISTS self_care_activities (
    id BIGSERIAL PRIMARY KEY,
    activity_name TEXT NOT NULL UNIQUE,
    activity_category TEXT CHECK (activity_category IN ('physical', 'emotional', 'mental', 'social', 'spiritual', 'creative', 'rest', 'joy')),
    description TEXT NOT NULL,
    time_required TEXT,
    energy_level_needed TEXT CHECK (energy_level_needed IN ('low', 'medium', 'high', 'any')),
    best_for TEXT[],
    instructions TEXT,
    tips TEXT[],
    google_doc_url TEXT,
    times_suggested INTEGER DEFAULT 0,
    times_completed INTEGER DEFAULT 0,
    avg_effectiveness NUMERIC(3, 1),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'rahmah'
);

CREATE INDEX idx_self_care_category ON self_care_activities(activity_category, status);
CREATE INDEX idx_self_care_effectiveness ON self_care_activities(avg_effectiveness DESC, times_completed DESC) WHERE status = 'active';

COMMENT ON TABLE self_care_activities IS 'Library of self-care practices and resources';

-- 7. Habit Tracking
CREATE TABLE IF NOT EXISTS habit_tracking (
    id BIGSERIAL PRIMARY KEY,
    tracking_date DATE NOT NULL,
    habit_name TEXT NOT NULL,
    habit_category TEXT CHECK (habit_category IN ('morning_routine', 'evening_routine', 'exercise', 'mindfulness', 'nutrition', 'sleep_hygiene', 'breaks', 'boundaries', 'social', 'joy')),
    completed BOOLEAN NOT NULL,
    quality_rating INTEGER CHECK (quality_rating BETWEEN 1 AND 5),
    time_spent_minutes INTEGER,
    barriers TEXT,
    notes TEXT,
    streak_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_habit_tracking_date ON habit_tracking(tracking_date DESC, habit_name);
CREATE INDEX idx_habit_tracking_habit ON habit_tracking(habit_name, tracking_date DESC);
CREATE INDEX idx_habit_tracking_completed ON habit_tracking(completed, tracking_date DESC);

COMMENT ON TABLE habit_tracking IS 'Daily habit tracking for wellness routines';

-- 8. Wellness Resources
CREATE TABLE IF NOT EXISTS wellness_resources (
    id BIGSERIAL PRIMARY KEY,
    resource_type TEXT CHECK (resource_type IN ('article', 'video', 'podcast', 'book', 'app', 'technique', 'worksheet', 'hotline', 'professional_service', 'community')),
    resource_title TEXT NOT NULL,
    resource_category TEXT CHECK (resource_category IN ('stress_management', 'anxiety', 'depression', 'burnout', 'sleep', 'mindfulness', 'boundaries', 'work_life_balance', 'self_compassion', 'crisis_support')),
    description TEXT NOT NULL,
    url TEXT,
    access_info TEXT,
    recommended_for TEXT[],
    time_commitment TEXT,
    cost TEXT,
    effectiveness_notes TEXT,
    times_shared INTEGER DEFAULT 0,
    last_shared_at TIMESTAMPTZ,
    google_doc_url TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'outdated')),
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    added_by TEXT DEFAULT 'rahmah'
);

CREATE INDEX idx_wellness_resources_category ON wellness_resources(resource_category, status);
CREATE INDEX idx_wellness_resources_type ON wellness_resources(resource_type, status);
CREATE INDEX idx_wellness_resources_shared ON wellness_resources(times_shared DESC, last_shared_at DESC);

COMMENT ON TABLE wellness_resources IS 'Curated mental health and wellness resources';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- 1. Get Current Wellness Summary
CREATE OR REPLACE FUNCTION get_current_wellness_summary()
RETURNS TABLE (
    avg_mood_7d NUMERIC,
    avg_energy_7d NUMERIC,
    avg_stress_7d NUMERIC,
    avg_sleep_7d NUMERIC,
    high_stress_days INTEGER,
    burnout_risk_level TEXT,
    active_goals INTEGER,
    pending_interventions INTEGER,
    unresolved_signals INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ROUND(AVG(wci.mood_rating), 1),
        ROUND(AVG(wci.energy_level), 1),
        ROUND(AVG(wci.stress_level), 1),
        ROUND(AVG(wci.sleep_quality), 1),
        COUNT(*) FILTER (WHERE wci.stress_level >= 7)::INTEGER,
        (SELECT bra.risk_level 
         FROM burnout_risk_assessments bra 
         ORDER BY bra.assessment_date DESC 
         LIMIT 1),
        (SELECT COUNT(*)::INTEGER 
         FROM wellness_goals wg 
         WHERE wg.status = 'active'),
        (SELECT COUNT(*)::INTEGER 
         FROM wellness_interventions wi 
         WHERE wi.implementation_status IN ('suggested', 'accepted', 'in_progress')),
        (SELECT COUNT(*)::INTEGER 
         FROM stress_signals ss 
         WHERE ss.resolution_status IN ('monitoring', 'intervened'))
    FROM wellness_check_ins wci
    WHERE wci.check_in_date > CURRENT_DATE - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_current_wellness_summary IS 'Get current wellness status with trends';

-- 2. Get Habit Streaks
CREATE OR REPLACE FUNCTION get_habit_streaks()
RETURNS TABLE (
    habit_name TEXT,
    current_streak INTEGER,
    longest_streak INTEGER,
    completion_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH habit_days AS (
        SELECT 
            ht.habit_name,
            ht.tracking_date,
            ht.completed,
            ROW_NUMBER() OVER (PARTITION BY ht.habit_name ORDER BY ht.tracking_date) -
            ROW_NUMBER() OVER (PARTITION BY ht.habit_name, ht.completed ORDER BY ht.tracking_date) AS streak_group
        FROM habit_tracking ht
        WHERE ht.tracking_date > CURRENT_DATE - INTERVAL '90 days'
    ),
    streaks AS (
        SELECT 
            hd.habit_name,
            hd.completed,
            COUNT(*) AS streak_length,
            MAX(hd.tracking_date) AS streak_end
        FROM habit_days hd
        WHERE hd.completed = TRUE
        GROUP BY hd.habit_name, hd.streak_group, hd.completed
    )
    SELECT 
        ht.habit_name,
        COALESCE(MAX(s.streak_length) FILTER (WHERE s.streak_end = MAX(ht.tracking_date)), 0)::INTEGER,
        COALESCE(MAX(s.streak_length), 0)::INTEGER,
        ROUND((COUNT(*) FILTER (WHERE ht.completed = TRUE)::NUMERIC / NULLIF(COUNT(*), 0) * 100), 1)
    FROM habit_tracking ht
    LEFT JOIN streaks s ON ht.habit_name = s.habit_name
    WHERE ht.tracking_date > CURRENT_DATE - INTERVAL '30 days'
    GROUP BY ht.habit_name
    ORDER BY MAX(ht.tracking_date) DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_habit_streaks IS 'Calculate current streaks for all tracked habits';

-- 3. Detect Wellness Patterns
CREATE OR REPLACE FUNCTION detect_wellness_patterns()
RETURNS TABLE (
    pattern_type TEXT,
    pattern_description TEXT,
    confidence TEXT,
    recommendation TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH recent_data AS (
        SELECT 
            wci.check_in_date,
            wci.mood_rating,
            wci.energy_level,
            wci.stress_level,
            wci.sleep_quality,
            wci.work_hours,
            wci.exercise_completed
        FROM wellness_check_ins wci
        WHERE wci.check_in_date > CURRENT_DATE - INTERVAL '30 days'
    )
    SELECT 
        'High work hours correlate with high stress'::TEXT,
        'Days with 10+ work hours show 2x higher stress levels'::TEXT,
        'High'::TEXT,
        'Consider setting a 9-hour daily work limit'::TEXT
    WHERE (SELECT AVG(rd.stress_level) FROM recent_data rd WHERE rd.work_hours > 10) > 
          (SELECT AVG(rd.stress_level) FROM recent_data rd WHERE rd.work_hours <= 10) * 1.5
    
    UNION ALL
    
    SELECT 
        'Exercise improves mood'::TEXT,
        'Days with exercise show +2 point average mood boost'::TEXT,
        'High'::TEXT,
        'Prioritize daily movement, even 15 minutes'::TEXT
    WHERE (SELECT AVG(rd.mood_rating) FROM recent_data rd WHERE rd.exercise_completed = TRUE) > 
          (SELECT AVG(rd.mood_rating) FROM recent_data rd WHERE rd.exercise_completed = FALSE) + 1.5
    
    UNION ALL
    
    SELECT 
        'Sleep quality affects energy'::TEXT,
        'Poor sleep (<6 rating) predicts low energy next day'::TEXT,
        'High'::TEXT,
        'Focus on sleep hygiene improvements'::TEXT
    WHERE (SELECT AVG(rd.energy_level) FROM recent_data rd WHERE rd.sleep_quality < 6) < 
          (SELECT AVG(rd.energy_level) FROM recent_data rd WHERE rd.sleep_quality >= 6) - 2;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION detect_wellness_patterns IS 'Identify patterns and correlations in wellness data';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- 1. Wellness Dashboard
CREATE OR REPLACE VIEW v_wellness_dashboard AS
SELECT 
    ROUND(AVG(wci.mood_rating), 1) AS avg_mood_7d,
    ROUND(AVG(wci.energy_level), 1) AS avg_energy_7d,
    ROUND(AVG(wci.stress_level), 1) AS avg_stress_7d,
    ROUND(AVG(wci.sleep_quality), 1) AS avg_sleep_7d,
    ROUND(AVG(wci.work_hours), 1) AS avg_work_hours_7d,
    COUNT(*) FILTER (WHERE wci.stress_level >= 7) AS high_stress_days,
    COUNT(*) FILTER (WHERE wci.exercise_completed = TRUE) AS exercise_days,
    (SELECT bra.risk_level 
     FROM burnout_risk_assessments bra 
     ORDER BY bra.assessment_date DESC 
     LIMIT 1) AS current_burnout_risk
FROM wellness_check_ins wci
WHERE wci.check_in_date > CURRENT_DATE - INTERVAL '7 days';

COMMENT ON VIEW v_wellness_dashboard IS '7-day wellness snapshot';

-- 2. Active Wellness Goals
CREATE OR REPLACE VIEW v_active_wellness_goals AS
SELECT 
    wg.id,
    wg.goal_category,
    wg.goal_title,
    wg.target_date,
    wg.progress_percentage,
    (wg.target_date - CURRENT_DATE)::INTEGER AS days_remaining,
    wg.barriers,
    wg.supports
FROM wellness_goals wg
WHERE wg.status = 'active'
ORDER BY wg.target_date ASC NULLS LAST;

COMMENT ON VIEW v_active_wellness_goals IS 'Current wellness goals with progress';

-- 3. Stress Alert Summary
CREATE OR REPLACE VIEW v_stress_alert_summary AS
SELECT 
    ss.id,
    ss.signal_date,
    ss.signal_type,
    ss.signal_description,
    ss.severity,
    ss.frequency,
    ss.resolution_status,
    (CURRENT_DATE - ss.signal_date)::INTEGER AS days_active
FROM stress_signals ss
WHERE ss.resolution_status IN ('monitoring', 'intervened')
  AND ss.signal_date > CURRENT_DATE - INTERVAL '30 days'
ORDER BY 
    CASE ss.severity
        WHEN 'severe' THEN 1
        WHEN 'significant' THEN 2
        WHEN 'moderate' THEN 3
        WHEN 'mild' THEN 4
    END,
    ss.signal_date ASC;

COMMENT ON VIEW v_stress_alert_summary IS 'Active stress signals needing attention';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- - 8 new tables for wellness tracking, burnout assessment, goal setting
-- - 3 helper functions for wellness summary, habit streaks, pattern detection
-- - 3 views for wellness dashboard, active goals, stress alerts
-- Total tables in database: 144 (136 + 8 new)
