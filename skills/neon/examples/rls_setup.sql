-- Row-Level Security (RLS) Setup Examples
-- Secure tables accessed via Data API

-- ============================================
-- Example 1: User-owned records
-- ============================================

-- Enable RLS on leads table
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read all published leads
CREATE POLICY read_published_leads ON leads
FOR SELECT TO authenticated
USING (status IN ('published', 'qualified'));

-- Policy: Users can only modify their own leads
CREATE POLICY manage_own_leads ON leads
FOR ALL TO authenticated
USING (auth.user_id() = owner_id)
WITH CHECK (auth.user_id() = owner_id);

-- ============================================
-- Example 2: Team-based access
-- ============================================

-- Enable RLS on campaigns table
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read campaigns from their team
CREATE POLICY read_team_campaigns ON campaigns
FOR SELECT TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM user_teams 
    WHERE user_id = auth.user_id()
  )
);

-- Policy: Only campaign owners can modify
CREATE POLICY modify_own_campaigns ON campaigns
FOR ALL TO authenticated
USING (auth.user_id() = owner_id)
WITH CHECK (auth.user_id() = owner_id);

-- ============================================
-- Example 3: Role-based access
-- ============================================

-- Enable RLS on clients table
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Policy: Admins can see all clients
CREATE POLICY admin_all_clients ON clients
FOR ALL TO authenticated
USING (
  auth.jwt() ->> 'role' = 'admin'
);

-- Policy: Sales can see their assigned clients
CREATE POLICY sales_assigned_clients ON clients
FOR SELECT TO authenticated
USING (
  auth.jwt() ->> 'role' = 'sales'
  AND assigned_to = auth.user_id()
);

-- ============================================
-- Example 4: Public + Private data
-- ============================================

-- Enable RLS on posts table
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policy: Everyone can read published posts
CREATE POLICY read_published_posts ON posts
FOR SELECT TO authenticated
USING (is_published = true);

-- Policy: Authors can see their drafts
CREATE POLICY read_own_drafts ON posts
FOR SELECT TO authenticated
USING (
  NOT is_published 
  AND auth.user_id() = author_id
);

-- Policy: Authors can manage their own posts
CREATE POLICY manage_own_posts ON posts
FOR ALL TO authenticated
USING (auth.user_id() = author_id)
WITH CHECK (auth.user_id() = author_id);

-- ============================================
-- Example 5: Time-based access
-- ============================================

-- Enable RLS on meetings table
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;

-- Policy: Users can see past meetings they attended
CREATE POLICY read_attended_meetings ON meetings
FOR SELECT TO authenticated
USING (
  scheduled_at < NOW()
  AND (
    host_id = auth.user_id()
    OR guest_id = auth.user_id()
  )
);

-- Policy: Users can modify future meetings they host
CREATE POLICY modify_future_meetings ON meetings
FOR UPDATE TO authenticated
USING (
  scheduled_at > NOW()
  AND host_id = auth.user_id()
)
WITH CHECK (
  scheduled_at > NOW()
  AND host_id = auth.user_id()
);

-- ============================================
-- Helper functions
-- ============================================

-- Get user ID from JWT token
-- (Built-in with Neon Data API as auth.user_id())

-- Get user role from JWT token
CREATE OR REPLACE FUNCTION auth.jwt()
RETURNS jsonb
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN current_setting('request.jwt.claims', true)::jsonb;
END;
$$;

-- ============================================
-- Testing RLS policies
-- ============================================

-- Set JWT claims for testing (only works in Neon Data API context)
-- In real usage, JWT comes from authentication provider

-- Example: Test as user 123
-- SELECT set_config('request.jwt.claims', '{"sub": "123", "role": "sales"}', true);

-- Then query with RLS enforced:
-- SELECT * FROM leads; -- Only sees leads allowed by policies

-- ============================================
-- Disable RLS (if needed for admin operations)
-- ============================================

-- Temporarily disable RLS for a session (requires superuser)
-- SET row_security = off;

-- Permanently disable RLS on a table
-- ALTER TABLE leads DISABLE ROW LEVEL SECURITY;

-- Drop a policy
-- DROP POLICY read_published_leads ON leads;
