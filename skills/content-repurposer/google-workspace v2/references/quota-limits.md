# Google Workspace — Quota & Rate Limits

## Gmail

| Limit | Value | Notes |
|-------|-------|-------|
| Daily send limit (free workspace) | 500 messages/day | Resets at midnight Pacific |
| Daily send limit (Google Workspace) | 2,000 messages/day | Per user |
| Recipients per message | 500 total (To + Cc + Bcc) | |
| Message size | 25 MB (sending), 50 MB (receiving) | Includes attachments |
| Max attachment size | 25 MB per email | Use Drive link for larger files |
| Labels per user | 500 | Includes system labels |
| Filters per user | 1,000 | |
| API read requests | 250 quota units/user/second | Per Google Cloud project |
| messages.send | 100 quota units per call | |
| messages.list | 5 quota units per call | |

**Bulk send check:**
```bash
# Check remaining daily send quota via Admin Reports
gws admin userUsageReport get \
  --params '{"userKey":"yasmine@smarterflo.com","date":"'$(date -u -v-1d +%Y-%m-%d)'","parameters":"gmail:num_emails_sent"}'
```

---

## Google Calendar

| Limit | Value | Notes |
|-------|-------|-------|
| Event creation rate | 10,000 events/day per user | |
| Attendees per event | 20,000 | Hard limit |
| Recurring event occurrences | 730 (2 years) | For UNTIL or COUNT rules |
| Calendars per user | No hard limit (practical: ~25) | |
| API requests | 1,000,000 requests/day per project | |
| Per-user rate | 1,000 requests/100 seconds | Shared across project |
| freebusy query items | 50 calendars per query | |

---

## Google Drive

| Limit | Value | Notes |
|-------|-------|-------|
| Storage (Workspace Business Starter) | 30 GB per user | |
| Storage (Workspace Business Standard) | 2 TB pooled | |
| Upload size per file | 5 TB | |
| Export size (Docs/Sheets as PDF) | 10 MB | Larger docs may fail |
| Sheets export (as CSV) | 100 MB | |
| Shared drives per org | 1,000 | |
| Members per shared drive | 600 | |
| API requests | 1,000,000,000 queries/day per project | |
| Files.list calls | 12,000 requests/minute per user | |
| Permissions create/delete | 1,000 requests/100 seconds | |

**Check storage usage:**
```bash
gws drive about get --params '{"fields":"storageQuota"}'
```

---

## Google Sheets

| Limit | Value | Notes |
|-------|-------|-------|
| Cells per spreadsheet | 10,000,000 | Across all tabs |
| Columns per sheet | 18,278 (column ZZZ) | |
| Rows | No hard limit (practical ~5M) | Performance degrades |
| Import file size | 100 MB | |
| CSV export size | 100 MB | |
| API requests (read) | 300 per minute per project | |
| API requests (write) | 300 per minute per project | |
| batchUpdate requests | 300 per minute per project | |
| Values per batchUpdate | 2,000,000 cells | |

---

## Google Docs / Slides

| Limit | Value | Notes |
|-------|-------|-------|
| Document size | 1.02 million characters | ~50,000 words |
| Presentation slides | 2,048 slides | Hard limit |
| Image size | 50 MB per image | |
| batchUpdate operations per call | 40 requests | |

---

## General API Rate Limits

| Behavior | Detail |
|----------|--------|
| Per-second burst | Each API has per-user per-second limits (varies by service) |
| 429 Too Many Requests | Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s, then fail |
| 403 rateLimitExceeded | Same as 429 — treat identically |
| Retry-After header | Honor it when present |
| Quota resets | Most daily quotas reset at midnight Pacific (UTC-8) |

**Recommended retry pattern for gws commands:**
```bash
# Wrap any bulk loop with backoff
for ID in $IDS; do
  gws gmail users messages get --params '{"userId":"me","id":"'"$ID"'"}' \
    || { sleep 2; gws gmail users messages get --params '{"userId":"me","id":"'"$ID"'"}'; }
done
```

---

## Checking Current Quota Usage

```bash
# Gmail usage (previous day — API only reports with 1-day lag)
gws admin userUsageReport get \
  --params '{"userKey":"yasmine@smarterflo.com","date":"'$(date -u -v-1d +%Y-%m-%d)'","parameters":"gmail:num_emails_sent,gmail:num_emails_received"}'

# Drive storage
gws drive about get --params '{"fields":"storageQuota,user"}'

# View Google Cloud API quota usage:
# https://console.cloud.google.com/apis/dashboard (project: clawdbot-484604)
```

---

## Bulk Operation Safety Rules

Before any bulk operation (>20 items):

1. Run a --dry-run or list-only step first to count items
2. Check quota via Admin Reports if sending emails
3. Add sleep between iterations for >100 items
4. Log each operation result before moving to next
5. For Drive permissions changes: always list current permissions first
