# Recipes — Scheduling (7)

## find-free-time
**Services:** Calendar

```bash
# 1. Set dynamic date range (today 9am–5pm UTC)
TODAY=$(date -u +%Y-%m-%d)
TIME_MIN="${TODAY}T09:00:00Z"
TIME_MAX="${TODAY}T17:00:00Z"

# 2. Query free/busy for attendees
gws calendar freebusy query --json '{
  "timeMin": "'"$TIME_MIN"'",
  "timeMax": "'"$TIME_MAX"'",
  "items": [
    {"id": "yasmine@smarterflo.com"},
    {"id": "other@example.com"}
  ]
}' > /tmp/freebusy.json

# 3. Parse busy periods to identify free slots
# The response has calendars[email].busy = [{start, end}, ...]
# Free = times NOT in any busy array
cat /tmp/freebusy.json | jq '
  .calendars | to_entries[] |
  {
    email: .key,
    busy: .value.busy | map({
      start: .start,
      end: .end
    })
  }
'
# Overlapping free time = 9am–5pm MINUS union of all busy periods

# 4. Create the event in the identified free slot
gws calendar +insert \
  --summary "Meeting Title" \
  --start "${TODAY}T14:00:00" \
  --end "${TODAY}T15:00:00"
```

---

## schedule-recurring-event
**Services:** Calendar

```bash
# 1. Create recurring event (weekly every Monday)
gws calendar events insert --params '{"calendarId":"primary","sendUpdates":"all"}' \
  --json '{
    "summary": "Weekly Sync",
    "start": {"dateTime": "2026-03-16T10:00:00", "timeZone": "America/New_York"},
    "end": {"dateTime": "2026-03-16T11:00:00", "timeZone": "America/New_York"},
    "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO"],
    "attendees": [{"email": "attendee@example.com"}]
  }'

# 2. Verify with agenda
gws calendar +agenda
```

---

## reschedule-meeting
**Services:** Calendar

```bash
# 1. Find the event
gws calendar events list \
  --params '{"calendarId":"primary","q":"Meeting Title","singleEvents":true,"maxResults":5}'

# 2. Get full event details
gws calendar events get --params '{"calendarId":"primary","eventId":"EVENT_ID"}'

# 3. Patch with new times and notify attendees
gws calendar events patch \
  --params '{"calendarId":"primary","eventId":"EVENT_ID","sendUpdates":"all"}' \
  --json '{
    "start": {"dateTime": "2026-03-12T15:00:00", "timeZone": "America/New_York"},
    "end": {"dateTime": "2026-03-12T16:00:00", "timeZone": "America/New_York"}
  }'
```

---

## batch-invite-to-event
**Services:** Calendar

```bash
# 1. Get current attendees
gws calendar events get --params '{"calendarId":"primary","eventId":"EVENT_ID"}'

# 2. Patch with updated attendees list (include existing + new)
gws calendar events patch \
  --params '{"calendarId":"primary","eventId":"EVENT_ID","sendUpdates":"all"}' \
  --json '{
    "attendees": [
      {"email": "existing@example.com"},
      {"email": "new1@example.com"},
      {"email": "new2@example.com"}
    ]
  }'

# 3. Verify
gws calendar events get --params '{"calendarId":"primary","eventId":"EVENT_ID"}' \
  | jq '.attendees[] | .email'
```

---

## block-focus-time
**Services:** Calendar

```bash
# 1. Create recurring focus block (opaque = shows as busy)
gws calendar events insert --params '{"calendarId":"primary"}' \
  --json '{
    "summary": "Focus Time",
    "start": {"dateTime": "2026-03-17T09:00:00", "timeZone": "America/New_York"},
    "end": {"dateTime": "2026-03-17T11:00:00", "timeZone": "America/New_York"},
    "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=TU"],
    "transparency": "opaque",
    "visibility": "private"
  }'

# 2. Verify it shows as busy
gws calendar freebusy query --json '{
  "timeMin": "2026-03-17T09:00:00Z",
  "timeMax": "2026-03-17T11:00:00Z",
  "items": [{"id": "yasmine@smarterflo.com"}]
}'
```

---

## create-meet-space
**Services:** Meet, Gmail

```bash
# 1. Create an open meeting space
gws meet spaces create --json '{"config": {"accessType": "OPEN"}}'
# Note the meetingUri from the response

# 2. Email join link to team
gws gmail +send \
  --to "team@example.com" \
  --subject "Meeting Space Ready" \
  --body "Join here: https://meet.google.com/MEETING_CODE"
```

---

## plan-weekly-schedule
**Services:** Calendar

```bash
# 1. Set dynamic week range (Mon–Fri of current week)
WEEK_START=$(date -u -v-Mon +%Y-%m-%d)
WEEK_END=$(date -u -v+Fri +%Y-%m-%d)

# 2. Check current week's agenda
gws calendar events list \
  --params '{
    "calendarId": "primary",
    "timeMin": "'"${WEEK_START}"'T00:00:00Z",
    "timeMax": "'"${WEEK_END}"'T23:59:59Z",
    "singleEvents": true,
    "orderBy": "startTime"
  }' --format table

# 3. Query free/busy for the week
gws calendar freebusy query --json '{
  "timeMin": "'"${WEEK_START}"'T09:00:00Z",
  "timeMax": "'"${WEEK_END}"'T17:00:00Z",
  "items": [{"id": "yasmine@smarterflo.com"}]
}'

# 4. Add planned work blocks (use a specific day)
TUESDAY=$(date -u -v+Tue +%Y-%m-%d)
gws calendar +insert --summary "Deep Work: [Task]" \
  --start "${TUESDAY}T09:00:00" --end "${TUESDAY}T12:00:00"
```
