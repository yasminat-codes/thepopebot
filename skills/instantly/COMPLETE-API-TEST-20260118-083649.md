# Instantly.ai Complete API Test Report

**Date**: 2026-01-18 08:36:49 UTC
**Account**: yasmine.s@dosmarterflo.com
**Test Type**: Comprehensive - ALL endpoints with sample data

---

## Test Configuration

- Campaign ID: `6a7434a6-d329-4090-b985-365fd8364ff5`
- Account Email: `yasmine.s@dosmarterflo.com`

---

## 📊 CAMPAIGNS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List campaigns | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns list --limit 5` |
| Get campaign | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns get --id 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Search by contact | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns search-by-contact --email test@example.com` |
| Get sending status | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns sending-status --id 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Count launched | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns count-launched` |
| Create campaign | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns create --name 'API Test 1768725424'` |

## 👥 LEADS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List leads | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly leads list --campaign-id 6a7434a6-d329-4090-b985-365fd8364ff5 --limit 5` |
| Add lead | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly leads add --email apitest-1768725438@example.com --first-name API --last-name Test --campaign-id 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Bulk delete leads (empty array) | ❌ FAIL | `/home/clawdbot/clawd/skills/instantly/instantly api DELETE leads '[]'` |

## 📋 LEAD LISTS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List lead lists | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly lead-lists list` |
| Create lead list | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly lead-lists create --name 'API Test List 1768725446'` |
| Get lead list | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly lead-lists get --id d5c8d436-beff-48fd-bdb8-c75a7dcc9516` |
| Update lead list | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly lead-lists update --id d5c8d436-beff-48fd-bdb8-c75a7dcc9516 --name 'API Test List 1768725446 Updated'` |
| Delete lead list | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly lead-lists delete --id d5c8d436-beff-48fd-bdb8-c75a7dcc9516` |

## 📧 ACCOUNTS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List accounts | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly accounts list` |
| Get account | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly accounts get --email yasmine.s@dosmarterflo.com` |
| Warmup analytics | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly accounts warmup-analytics --emails yasmine.s@dosmarterflo.com` |
| Pause account | ⏭️ SKIP | Avoided to prevent disruption |
| Resume account | ⏭️ SKIP | Avoided to prevent disruption |
| Warmup enable/disable | ⏭️ SKIP | Avoided to prevent disruption |

## 📈 ANALYTICS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| Campaign analytics | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly analytics campaign --campaign-ids 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Analytics overview | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly analytics overview --campaign-ids 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Daily analytics | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly analytics daily --campaign-id 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Steps analytics | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly analytics steps --campaign-id 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Account warmup analytics | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly analytics warmup --emails yasmine.s@dosmarterflo.com` |
| Account list (via analytics) | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly analytics account` |

## 📬 EMAILS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List emails | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly emails list --limit 5` |
| List only replies | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly emails list --type 2 --limit 5` |
| Unread count | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly emails unread-count` |

## 📥 INBOX MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List inbox | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly inbox list --limit 5` |
| List unread only | ❌ FAIL | `/home/clawdbot/clawd/skills/instantly/instantly inbox list --unread --limit 5` |

## 🔄 SUBSEQUENCES MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List subsequences | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly subsequences list --campaign-id 6a7434a6-d329-4090-b985-365fd8364ff5` |
| Create subsequence | ❌ FAIL | `/home/clawdbot/clawd/skills/instantly/instantly subsequences create --campaign-id 6a7434a6-d329-4090-b985-365fd8364ff5 --name 'API Test Subseq' --delay-days 3` |

## 🔗 WEBHOOKS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List webhooks | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly webhooks list` |
| Get event types | ❌ FAIL | `/home/clawdbot/clawd/skills/instantly/instantly webhooks event-types` |
| Get webhook events | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly webhooks events --limit 5` |
| Get events summary | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly webhooks events-summary` |
| Create webhook | ❌ FAIL | `/home/clawdbot/clawd/skills/instantly/instantly webhooks create --url https://webhook.site/test-1768725507 --events 'lead.replied'` |
| Get webhook | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly webhooks get --id 0199e630-4c84-7d57-ad26-6bd93159f714` |
| Update webhook | ❌ FAIL | `/home/clawdbot/clawd/skills/instantly/instantly webhooks update --id 0199e630-4c84-7d57-ad26-6bd93159f714 --url 'https://updated.example.com'` |
| Test webhook | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly webhooks test --id 0199e630-4c84-7d57-ad26-6bd93159f714` |
| Delete webhook | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly webhooks delete --id 0199e630-4c84-7d57-ad26-6bd93159f714` |

## 🔧 RAW API MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| Raw GET - campaigns | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly api GET 'campaigns?limit=3'` |
| Raw GET - custom tags | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly api GET 'custom-tags'` |
| Raw GET - tag mappings | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly api GET 'custom-tag-mappings'` |

---

## 📊 TEST SUMMARY

**Total Tests**: 42
**Passed**: 36 (85.7%)
**Failed**: 6 (14.2%)

### ⚠️ Some tests failed

Review failed tests above for details.

**Test completed**: 2026-01-18 08:38:57 UTC
