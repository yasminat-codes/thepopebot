# Neon PostgreSQL Setup Guide

**Status:** Python dependencies installed ✅  
**Location:** `~/venvs/neon/`  
**Next:** Configure Neon credentials

---

## Step 1: Create Neon Project (if needed)

1. Go to https://console.neon.tech
2. Sign up or log in
3. Create a new project (or use existing)
4. Note your project name

---

## Step 2: Get Connection String

1. In Neon Console → Dashboard
2. Find "Connection string" section
3. Copy the connection string (looks like):
   ```
   postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

---

## Step 3: Enable Data API (Optional but Recommended)

1. In Neon Console → Data API (left sidebar)
2. Click "Enable Data API"
3. Choose authentication:
   - **Neon Auth** (simplest) - Check "Use Neon Auth"
   - **Custom** - Use your own auth provider
4. Check "Grant public schema access"
5. Click "Enable Data API"
6. Copy the **API URL** (looks like):
   ```
   https://ep-xxx.apirest.us-east-1.aws.neon.tech/neondb/rest/v1
   ```

---

## Step 4: Get JWT Token (for Data API)

### If using Neon Auth:

1. Find your Auth URL in Neon Console → Data API page
2. Open: `https://your-auth-url/reference`
3. Use the UI to sign up or sign in
4. Call `GET /get-session`
5. Copy JWT from `set-auth-jwt` header

### If using custom auth:
Get JWT from your auth provider (Auth0, Clerk, Firebase, etc.)

---

## Step 5: Get API Key (for Management API)

1. In Neon Console → Account Settings
2. Go to "API Keys" section
3. Click "Create API Key"
4. Copy the key (starts with `neon_api_`)

---

## Step 6: Get Project ID

1. In Neon Console → Dashboard
2. Look at the URL: `https://console.neon.tech/app/projects/{PROJECT_ID}`
3. Or find it in Project Settings

---

## Step 7: Add to Environment

Run this command (I'll do it for you once you provide the values):

```bash
cat >> ~/shared/.env << 'EOF'

# Neon PostgreSQL
NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
NEON_DATABASE_URL_POOLED=postgresql://username:password@ep-xxx-pooler.us-east-1.aws.neon.tech/neondb
NEON_DATA_API_URL=https://ep-xxx.apirest.us-east-1.aws.neon.tech/neondb/rest/v1
NEON_JWT_TOKEN=eyJhbGci...
NEON_API_KEY=neon_api_xxx
NEON_PROJECT_ID=ep-xxx
EOF
```

---

## Step 8: Test Connection

```bash
# Test direct SQL
~/shared/skills/neon/scripts/execute.py "SELECT version()"

# Test Data API (if enabled)
~/shared/skills/neon/scripts/query.py pg_tables --select "tablename" --limit 5

# Test Management API
~/shared/skills/neon/scripts/manage.py branches --list
```

---

## Quick Setup (if you have credentials)

Just provide me:
1. Connection string from Neon Console
2. Data API URL (if you enabled it)
3. JWT token (if using Data API)
4. API key (from Account Settings)
5. Project ID

I'll add everything to `shared/.env` and test the connection.

---

## Current Status

✅ Python dependencies installed (`~/venvs/neon/`)  
✅ Scripts configured to use venv  
⏳ Waiting for Neon credentials

**Need from you:**
- Do you already have a Neon project?
- If yes → provide credentials above
- If no → create one at https://console.neon.tech (free tier available)
