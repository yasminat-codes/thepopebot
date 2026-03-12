# Instantly.ai Complete API Test Report

**Date**: 2026-01-18 08:35:32 UTC
**Account**: yasmine.s@dosmarterflo.com
**Test Type**: Comprehensive - ALL endpoints with sample data

---

## Test Configuration

- Campaign ID: `f088b6e4-4e82-4ab4-ba83-a6973cfb6105`
- Account Email: `yasmine.s@dosmarterflo.com`

---

## 📊 CAMPAIGNS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List campaigns | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns list --limit 5` |
| Get campaign | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns get --id f088b6e4-4e82-4ab4-ba83-a6973cfb6105` |
| Search by contact | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns search-by-contact --email test@example.com` |
| Get sending status | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns sending-status --id f088b6e4-4e82-4ab4-ba83-a6973cfb6105` |
| Count launched | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns count-launched` |
| Create campaign | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly campaigns create --name 'API Test 1768725350'` |

## 👥 LEADS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List leads | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly leads list --campaign-id f088b6e4-4e82-4ab4-ba83-a6973cfb6105 --limit 5` |
| Add lead | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly leads add --email apitest-1768725357@example.com --first-name API --last-name Test --campaign-id f088b6e4-4e82-4ab4-ba83-a6973cfb6105` |
| Bulk delete leads (empty array) | ❌ FAIL | `/home/clawdbot/clawd/skills/instantly/instantly api DELETE leads '[]'` |

## 📋 LEAD LISTS MODULE

| Endpoint | Status | Command |
|----------|--------|---------|
| List lead lists | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly lead-lists list` |
| Create lead list | ✅ PASS | `/home/clawdbot/clawd/skills/instantly/instantly lead-lists create --name 'API Test List 1768725366'` |
