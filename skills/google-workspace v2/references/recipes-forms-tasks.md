# Recipes — Forms & Tasks (4)

## collect-form-responses
**Services:** Forms

```bash
# 1. Find forms in Drive
gws drive files list \
  --params '{"q":"mimeType='\''application/vnd.google-apps.form'\''","pageSize":10}'

# 2. Get form structure
gws forms forms get --params '{"formId":"FORM_ID"}'

# 3. Get all responses
gws forms forms responses list \
  --params '{"formId":"FORM_ID"}' \
  --page-all

# 4. Format as table
gws forms forms responses list \
  --params '{"formId":"FORM_ID"}' --format table
```

---

## create-feedback-form
**Services:** Forms, Gmail

```bash
# 1. Create form
gws forms forms create \
  --json '{"info":{"title":"Session Feedback","documentTitle":"Session Feedback Form"}}'
# Note formId

# 2. Add rating question
gws forms forms batchUpdate \
  --params '{"formId":"FORM_ID"}' \
  --json '{
    "requests": [{
      "createItem": {
        "item": {
          "title": "How would you rate this session?",
          "questionItem": {
            "question": {
              "required": true,
              "scaleQuestion": {"low": 1, "high": 5, "lowLabel": "Poor", "highLabel": "Excellent"}
            }
          }
        },
        "location": {"index": 0}
      }
    }]
  }'

# 3. Get responder URI
gws forms forms get --params '{"formId":"FORM_ID"}' | jq '.responderUri'

# 4. Email form link to attendees
gws gmail +send \
  --to "attendees@example.com" \
  --subject "Please share your feedback" \
  --body "We would love your feedback: [responderUri]"
```

---

## create-task-list
**Services:** Tasks

```bash
# 1. Create task list
gws tasks tasklists insert \
  --json '{"title": "Q1 Action Items"}'
# Note tasklist ID

# 2. Add tasks with due dates
gws tasks tasks insert \
  --params '{"tasklist":"TASKLIST_ID"}' \
  --json '{
    "title": "Send client proposal",
    "notes": "Use the Acme template",
    "due": "2026-03-15T00:00:00.000Z"
  }'

gws tasks tasks insert \
  --params '{"tasklist":"TASKLIST_ID"}' \
  --json '{
    "title": "Schedule follow-up call",
    "due": "2026-03-17T00:00:00.000Z"
  }'

# 3. Verify
gws tasks tasks list --params '{"tasklist":"TASKLIST_ID"}' --format table
```

---

## review-overdue-tasks
**Services:** Tasks

```bash
# 1. List all task lists
gws tasks tasklists list

# 2. Get overdue tasks (dueMax = now)
gws tasks tasks list \
  --params '{
    "tasklist": "@default",
    "showCompleted": "false",
    "dueMax": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }' --format table

# 3. Reschedule or mark complete
gws tasks tasks patch \
  --params '{"tasklist":"@default","task":"TASK_ID"}' \
  --json '{"due": "2026-03-20T00:00:00.000Z"}'
```
