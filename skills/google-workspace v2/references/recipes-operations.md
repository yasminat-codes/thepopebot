# Recipes — Operations (3)

## post-mortem-setup
**Services:** Docs, Calendar, Chat

```bash
# 1. Create post-mortem document
gws docs documents create \
  --json '{"title": "Post-Mortem: [Incident Name] - 2026-03-09"}'
# Note documentId

# 2. Add post-mortem template content
gws docs +write --doc-id "DOC_ID" \
  --content "# Post-Mortem\n\n## Summary\n\n## Timeline\n\n## Root Cause\n\n## Action Items\n"

# 3. Schedule review meeting
gws calendar +insert \
  --summary "Post-Mortem Review: [Incident]" \
  --start "2026-03-11T14:00:00" \
  --end "2026-03-11T15:00:00"

# 4. Notify team in Chat
gws chat spaces messages create \
  --params '{"parent":"spaces/SPACE_ID"}' \
  --json '{"text": "Post-mortem doc created for [incident]. Review meeting: Mar 11 2pm. Doc: [webViewLink]"}'
```

---

## create-classroom-course
**Services:** Classroom

```bash
# 1. Create course
gws classroom courses create \
  --json '{
    "name": "AI Automation Fundamentals",
    "section": "Cohort 1",
    "ownerId": "yasmine@smarterflo.com",
    "courseState": "ACTIVE"
  }'
# Note courseId

# 2. Invite students
gws classroom courses students create \
  --params '{"courseId":"COURSE_ID"}' \
  --json '{"userId": "student@example.com"}'

# 3. List enrolled students
gws classroom courses students list --params '{"courseId":"COURSE_ID"}'
```

---

## review-meet-participants
**Services:** Meet

```bash
# 1. List recent conferences
gws meet conferenceRecords list \
  --params '{"pageSize":10}' --format table

# 2. Get participants for a specific conference
gws meet conferenceRecords participants list \
  --params '{"parent":"conferenceRecords/RECORD_ID"}' --format table

# 3. Get join/leave times
gws meet conferenceRecords participants list \
  --params '{"parent":"conferenceRecords/RECORD_ID"}' \
  | jq '.participants[] | {displayName: .displayName, earliestStartTime: .earliestStartTime, latestEndTime: .latestEndTime}'
```
