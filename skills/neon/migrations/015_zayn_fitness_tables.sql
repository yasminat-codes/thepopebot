-- Migration 015: Zayn (Fitness Coach) Tables
-- Domain: Workout planning, exercise guidance, nutrition advice, progress tracking
-- Agent: Zayn (@ZaynFitnessBot)
-- Created: 2025-01-27

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- 1. Fitness Goals
CREATE TABLE IF NOT EXISTS fitness_goals (
    id BIGSERIAL PRIMARY KEY,
    goal_category TEXT CHECK (goal_category IN ('weight_loss', 'muscle_gain', 'strength', 'endurance', 'body_composition', 'flexibility', 'consistency', 'performance', 'general_health')),
    goal_title TEXT NOT NULL,
    goal_description TEXT NOT NULL,
    target_metric TEXT,
    starting_value NUMERIC(10, 2),
    target_value NUMERIC(10, 2),
    current_value NUMERIC(10, 2),
    unit TEXT,
    start_date DATE NOT NULL,
    target_date DATE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'abandoned')),
    progress_percentage INTEGER CHECK (progress_percentage BETWEEN 0 AND 100) DEFAULT 0,
    milestones TEXT[],
    barriers TEXT[],
    completed_at DATE,
    google_doc_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'zayn',
    notes TEXT
);

CREATE INDEX idx_fitness_goals_status ON fitness_goals(status, goal_category);
CREATE INDEX idx_fitness_goals_dates ON fitness_goals(target_date, status) WHERE status = 'active';

COMMENT ON TABLE fitness_goals IS 'Fitness objectives and targets';

-- 2. Workout Programs
CREATE TABLE IF NOT EXISTS workout_programs (
    id BIGSERIAL PRIMARY KEY,
    program_name TEXT NOT NULL UNIQUE,
    program_type TEXT CHECK (program_type IN ('strength', 'hypertrophy', 'endurance', 'weight_loss', 'general_fitness', 'sport_specific', 'rehabilitation')),
    description TEXT NOT NULL,
    duration_weeks INTEGER,
    frequency_per_week INTEGER,
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    equipment_needed TEXT[],
    prerequisites TEXT[],
    target_goals TEXT[],
    google_doc_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'zayn',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    notes TEXT
);

CREATE INDEX idx_workout_programs_type ON workout_programs(program_type, status);
CREATE INDEX idx_workout_programs_difficulty ON workout_programs(difficulty_level, status);

COMMENT ON TABLE workout_programs IS 'Structured workout programs';

-- 3. Workout Sessions
CREATE TABLE IF NOT EXISTS workout_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_date DATE NOT NULL,
    program_id BIGINT REFERENCES workout_programs(id),
    session_type TEXT CHECK (session_type IN ('strength', 'cardio', 'flexibility', 'mobility', 'hiit', 'active_recovery', 'sport', 'other')),
    session_title TEXT NOT NULL,
    planned_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    completion_percentage INTEGER CHECK (completion_percentage BETWEEN 0 AND 100),
    intensity_level INTEGER CHECK (intensity_level BETWEEN 1 AND 10),
    energy_level_before INTEGER CHECK (energy_level_before BETWEEN 1 AND 10),
    energy_level_after INTEGER CHECK (energy_level_after BETWEEN 1 AND 10),
    perceived_exertion INTEGER CHECK (perceived_exertion BETWEEN 1 AND 10),
    how_felt TEXT,
    google_doc_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    notes TEXT
);

CREATE INDEX idx_workout_sessions_date ON workout_sessions(session_date DESC);
CREATE INDEX idx_workout_sessions_type ON workout_sessions(session_type, session_date DESC);
CREATE INDEX idx_workout_sessions_completed ON workout_sessions(completed, session_date DESC);

COMMENT ON TABLE workout_sessions IS 'Individual workout sessions';

-- 4. Exercises
CREATE TABLE IF NOT EXISTS exercises (
    id BIGSERIAL PRIMARY KEY,
    exercise_name TEXT NOT NULL UNIQUE,
    exercise_category TEXT CHECK (exercise_category IN ('compound', 'isolation', 'cardio', 'plyometric', 'flexibility', 'mobility', 'core', 'bodyweight', 'machine', 'free_weight')),
    primary_muscle_group TEXT NOT NULL,
    secondary_muscle_groups TEXT[],
    equipment_required TEXT[],
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    description TEXT NOT NULL,
    instructions TEXT,
    form_cues TEXT[],
    common_mistakes TEXT[],
    modifications TEXT[],
    progressions TEXT[],
    video_url TEXT,
    google_doc_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'zayn',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived'))
);

CREATE INDEX idx_exercises_category ON exercises(exercise_category, status);
CREATE INDEX idx_exercises_muscle ON exercises(primary_muscle_group, status);

COMMENT ON TABLE exercises IS 'Exercise library with descriptions and instructions';

-- 5. Workout Exercises
CREATE TABLE IF NOT EXISTS workout_exercises (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT REFERENCES workout_sessions(id),
    exercise_id BIGINT REFERENCES exercises(id),
    exercise_order INTEGER NOT NULL,
    sets_planned INTEGER,
    sets_completed INTEGER DEFAULT 0,
    reps_target TEXT,
    reps_actual TEXT,
    weight_target NUMERIC(6, 2),
    weight_actual NUMERIC(6, 2),
    weight_unit TEXT DEFAULT 'lbs',
    rest_seconds INTEGER,
    tempo TEXT,
    notes TEXT,
    completed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_workout_exercises_session ON workout_exercises(session_id, exercise_order);
CREATE INDEX idx_workout_exercises_exercise ON workout_exercises(exercise_id);

COMMENT ON TABLE workout_exercises IS 'Exercises within a specific workout session';

-- 6. Progress Measurements
CREATE TABLE IF NOT EXISTS progress_measurements (
    id BIGSERIAL PRIMARY KEY,
    measurement_date DATE NOT NULL,
    weight NUMERIC(6, 2),
    weight_unit TEXT DEFAULT 'lbs',
    body_fat_percentage NUMERIC(4, 1),
    chest_inches NUMERIC(5, 2),
    waist_inches NUMERIC(5, 2),
    hips_inches NUMERIC(5, 2),
    thigh_left_inches NUMERIC(5, 2),
    thigh_right_inches NUMERIC(5, 2),
    arm_left_inches NUMERIC(5, 2),
    arm_right_inches NUMERIC(5, 2),
    neck_inches NUMERIC(5, 2),
    photos_urls TEXT[],
    mood TEXT,
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    google_doc_url TEXT,
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_progress_measurements_date ON progress_measurements(measurement_date DESC);

COMMENT ON TABLE progress_measurements IS 'Body measurements and fitness metrics over time';

-- 7. Personal Records
CREATE TABLE IF NOT EXISTS personal_records (
    id BIGSERIAL PRIMARY KEY,
    exercise_id BIGINT REFERENCES exercises(id),
    record_type TEXT CHECK (record_type IN ('1rm', '3rm', '5rm', 'max_reps', 'max_time', 'max_distance', 'fastest_time')),
    record_value NUMERIC(10, 2) NOT NULL,
    record_unit TEXT,
    achieved_date DATE NOT NULL,
    workout_session_id BIGINT REFERENCES workout_sessions(id),
    previous_record NUMERIC(10, 2),
    improvement_percentage NUMERIC(5, 1),
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_personal_records_exercise ON personal_records(exercise_id, achieved_date DESC);
CREATE INDEX idx_personal_records_type ON personal_records(record_type, achieved_date DESC);

COMMENT ON TABLE personal_records IS 'Track personal bests for exercises';

-- 8. Nutrition Plans
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id BIGSERIAL PRIMARY KEY,
    plan_name TEXT NOT NULL,
    plan_type TEXT CHECK (plan_type IN ('weight_loss', 'muscle_gain', 'maintenance', 'performance', 'general_health')),
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    daily_calorie_target INTEGER,
    protein_grams_target INTEGER,
    carbs_grams_target INTEGER,
    fat_grams_target INTEGER,
    meals_per_day INTEGER,
    hydration_ounces_target INTEGER,
    restrictions TEXT[],
    preferences TEXT[],
    google_doc_url TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'zayn',
    notes TEXT
);

CREATE INDEX idx_nutrition_plans_dates ON nutrition_plans(start_date DESC, status);
CREATE INDEX idx_nutrition_plans_type ON nutrition_plans(plan_type, status);

COMMENT ON TABLE nutrition_plans IS 'Meal plans and nutrition protocols';

-- 9. Daily Nutrition Logs
CREATE TABLE IF NOT EXISTS daily_nutrition_logs (
    id BIGSERIAL PRIMARY KEY,
    log_date DATE NOT NULL,
    nutrition_plan_id BIGINT REFERENCES nutrition_plans(id),
    total_calories INTEGER,
    protein_grams INTEGER,
    carbs_grams INTEGER,
    fat_grams INTEGER,
    hydration_ounces INTEGER,
    meals_logged INTEGER,
    adherence_percentage INTEGER CHECK (adherence_percentage BETWEEN 0 AND 100),
    hunger_levels TEXT,
    energy_levels TEXT,
    cravings TEXT,
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_daily_nutrition_logs_date ON daily_nutrition_logs(log_date DESC);
CREATE INDEX idx_daily_nutrition_logs_plan ON daily_nutrition_logs(nutrition_plan_id, log_date DESC);

COMMENT ON TABLE daily_nutrition_logs IS 'Daily food and hydration tracking';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- 1. Get Current Fitness Summary
CREATE OR REPLACE FUNCTION get_current_fitness_summary()
RETURNS TABLE (
    active_goals INTEGER,
    avg_workouts_per_week NUMERIC,
    last_workout_date DATE,
    days_since_workout INTEGER,
    current_weight NUMERIC,
    weight_change_30d NUMERIC,
    avg_nutrition_adherence NUMERIC,
    recent_prs INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*)::INTEGER FROM fitness_goals WHERE status = 'active'),
        (SELECT ROUND(COUNT(*)::NUMERIC / 4, 1) 
         FROM workout_sessions 
         WHERE session_date > CURRENT_DATE - INTERVAL '28 days' AND completed = TRUE),
        (SELECT MAX(session_date) FROM workout_sessions WHERE completed = TRUE),
        (SELECT (CURRENT_DATE - MAX(session_date))::INTEGER 
         FROM workout_sessions 
         WHERE completed = TRUE),
        (SELECT weight FROM progress_measurements ORDER BY measurement_date DESC LIMIT 1),
        (SELECT 
            (SELECT weight FROM progress_measurements ORDER BY measurement_date DESC LIMIT 1) -
            (SELECT weight FROM progress_measurements WHERE measurement_date <= CURRENT_DATE - INTERVAL '30 days' ORDER BY measurement_date DESC LIMIT 1)
        ),
        (SELECT ROUND(AVG(adherence_percentage), 1) 
         FROM daily_nutrition_logs 
         WHERE log_date > CURRENT_DATE - INTERVAL '7 days'),
        (SELECT COUNT(*)::INTEGER 
         FROM personal_records 
         WHERE achieved_date > CURRENT_DATE - INTERVAL '30 days');
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_current_fitness_summary IS 'Get current fitness status and progress';

-- 2. Get Exercise Progress
CREATE OR REPLACE FUNCTION get_exercise_progress(p_exercise_id BIGINT, p_days INTEGER DEFAULT 90)
RETURNS TABLE (
    session_date DATE,
    sets_completed INTEGER,
    avg_reps NUMERIC,
    max_weight NUMERIC,
    total_volume NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ws.session_date,
        we.sets_completed,
        ROUND(AVG(
            CASE 
                WHEN we.reps_actual ~ '^[0-9]+$' THEN we.reps_actual::NUMERIC
                ELSE NULL
            END
        ), 1),
        MAX(we.weight_actual),
        SUM(
            we.sets_completed * 
            CASE 
                WHEN we.reps_actual ~ '^[0-9]+$' THEN we.reps_actual::NUMERIC
                ELSE 0
            END * 
            COALESCE(we.weight_actual, 0)
        )
    FROM workout_exercises we
    JOIN workout_sessions ws ON we.session_id = ws.id
    WHERE we.exercise_id = p_exercise_id
      AND ws.session_date > CURRENT_DATE - (p_days || ' days')::INTERVAL
      AND ws.completed = TRUE
    GROUP BY ws.session_date, we.sets_completed
    ORDER BY ws.session_date ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_exercise_progress IS 'Track progress on a specific exercise over time';

-- 3. Calculate Workout Consistency
CREATE OR REPLACE FUNCTION calculate_workout_consistency(p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    total_workouts INTEGER,
    completed_workouts INTEGER,
    completion_rate NUMERIC,
    avg_duration_minutes NUMERIC,
    most_common_type TEXT,
    current_streak_days INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER,
        COUNT(*) FILTER (WHERE ws.completed = TRUE)::INTEGER,
        ROUND((COUNT(*) FILTER (WHERE ws.completed = TRUE)::NUMERIC / NULLIF(COUNT(*), 0) * 100), 1),
        ROUND(AVG(ws.actual_duration_minutes), 1),
        (SELECT ws2.session_type 
         FROM workout_sessions ws2 
         WHERE ws2.session_date > CURRENT_DATE - (p_days || ' days')::INTERVAL 
           AND ws2.completed = TRUE
         GROUP BY ws2.session_type 
         ORDER BY COUNT(*) DESC 
         LIMIT 1),
        0::INTEGER -- Placeholder for streak calculation
    FROM workout_sessions ws
    WHERE ws.session_date > CURRENT_DATE - (p_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_workout_consistency IS 'Calculate workout frequency and consistency stats';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- 1. Fitness Dashboard
CREATE OR REPLACE VIEW v_fitness_dashboard AS
SELECT 
    (SELECT COUNT(*) FROM fitness_goals WHERE status = 'active') AS active_goals,
    (SELECT COUNT(*) FROM workout_sessions WHERE session_date > CURRENT_DATE - INTERVAL '7 days' AND completed = TRUE) AS workouts_this_week,
    (SELECT MAX(session_date) FROM workout_sessions WHERE completed = TRUE) AS last_workout_date,
    (SELECT weight FROM progress_measurements ORDER BY measurement_date DESC LIMIT 1) AS current_weight,
    (SELECT body_fat_percentage FROM progress_measurements ORDER BY measurement_date DESC LIMIT 1) AS current_body_fat,
    (SELECT ROUND(AVG(adherence_percentage), 1) FROM daily_nutrition_logs WHERE log_date > CURRENT_DATE - INTERVAL '7 days') AS nutrition_adherence_7d,
    (SELECT COUNT(*) FROM personal_records WHERE achieved_date > CURRENT_DATE - INTERVAL '30 days') AS prs_last_30d;

COMMENT ON VIEW v_fitness_dashboard IS 'Current fitness snapshot';

-- 2. Active Fitness Goals
CREATE OR REPLACE VIEW v_active_fitness_goals AS
SELECT 
    fg.id,
    fg.goal_category,
    fg.goal_title,
    fg.starting_value,
    fg.target_value,
    fg.current_value,
    fg.unit,
    fg.target_date,
    fg.progress_percentage,
    (fg.target_date - CURRENT_DATE)::INTEGER AS days_remaining,
    fg.barriers
FROM fitness_goals fg
WHERE fg.status = 'active'
ORDER BY fg.target_date ASC NULLS LAST;

COMMENT ON VIEW v_active_fitness_goals IS 'Current fitness goals with progress';

-- 3. Recent Personal Records
CREATE OR REPLACE VIEW v_recent_personal_records AS
SELECT 
    pr.id,
    e.exercise_name,
    pr.record_type,
    pr.record_value,
    pr.record_unit,
    pr.achieved_date,
    pr.previous_record,
    pr.improvement_percentage
FROM personal_records pr
JOIN exercises e ON pr.exercise_id = e.id
WHERE pr.achieved_date > CURRENT_DATE - INTERVAL '90 days'
ORDER BY pr.achieved_date DESC;

COMMENT ON VIEW v_recent_personal_records IS 'Recent PRs across all exercises';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- - 9 new tables for fitness goals, workouts, exercises, nutrition tracking
-- - 3 helper functions for fitness summary, exercise progress, consistency
-- - 3 views for fitness dashboard, active goals, recent PRs
-- Total tables in database: 153 (144 + 9 new)
