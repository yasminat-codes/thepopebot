---
name: ls:onboarding
description: >
  PROACTIVELY guides first-time setup of the LinkedIn Studio plugin. Validates environment,
  runs database setup, builds brand voice profile, and tests all integrations.
  Triggers on 'set up LinkedIn Studio', 'first time setup', 'onboarding', 'initialize plugin',
  or when any required env var is missing.
model: sonnet
context: fork
allowed-tools: Bash Read Write Agent AskUserQuestion
metadata:
  version: "2.0.0"
---

# ls:onboarding

First-run setup wizard for LinkedIn Studio. Guides through all configuration step by step.

## Phase 1: Welcome & Environment Check
1. Show welcome banner
2. Run `scripts/validate-env.sh --verbose` to check all env vars
3. Group missing vars by service, show which are required vs optional
4. For each missing required var: show where to get it (link to service) and where to set it

## Phase 2: Database Setup
1. Invoke ls:neon-setup via Agent tool
2. Wait for completion
3. If failed: guide user through Neon account creation and connection string setup

## Phase 3: Brand Voice Setup
1. Ask: "Would you like to set up your brand voice now?"
2. If yes: invoke ls:brand-voice-builder via Agent tool
3. If no: note that default AI consulting voice will be used

## Phase 4: Integration Testing
Test each configured service:
1. Neon: `neon_test` (already done in Phase 2)
2. Metricool: quick API test if METRICOOL_API_KEY set
3. Reddit: test PRAW authentication if credentials set
4. SerpAPI: test with a simple query if SERPAPI_KEY set
Show results table: service, status (OK/SKIP/FAIL), notes

## Phase 5: Quick Start Guide
Show personalized quick start based on what's configured:
- If all required services OK: "You're ready! Try /ls:pipeline to create your first post"
- If some services missing: "You can start with /ls:write-post (no external APIs needed)"
- List available commands based on configured integrations

## Error Handling
| Error | Recovery |
|-------|---------|
| No env vars set at all | Guide through minimum setup (Neon only) |
| Neon setup fails | Offer to continue without DB (local mode) |
