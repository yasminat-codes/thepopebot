# Recipes — Sheets (7)

## backup-sheet-as-csv
**Services:** Sheets, Drive

```bash
# Method 1: Export via Drive
gws drive files export \
  --params '{"fileId":"SPREADSHEET_ID","mimeType":"text/csv"}' \
  -o /tmp/backup.csv

# Method 2: Read values as CSV
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"SPREADSHEET_ID","range":"Sheet1"}' \
  --format csv > /tmp/backup.csv
```

---

## compare-sheet-tabs
**Services:** Sheets

```bash
# 1. Export both tabs as JSON arrays
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"SPREADSHEET_ID","range":"January!A:Z"}' \
  | jq '.values' > /tmp/jan.json

gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"SPREADSHEET_ID","range":"February!A:Z"}' \
  | jq '.values' > /tmp/feb.json

# 2. Rows in January but NOT in February (exact row match)
jq -n --slurpfile jan /tmp/jan.json --slurpfile feb /tmp/feb.json \
  '$jan[0] - $feb[0]'

# 3. Rows in February but NOT in January
jq -n --slurpfile jan /tmp/jan.json --slurpfile feb /tmp/feb.json \
  '$feb[0] - $jan[0]'

# 4. Show rows where first column matches but row differs (changed rows)
# Assumes column A is a unique key
jq -n --slurpfile jan /tmp/jan.json --slurpfile feb /tmp/feb.json '
  ($jan[0] | map({key: .[0], value: .}) | from_entries) as $jan_map |
  ($feb[0] | map({key: .[0], value: .}) | from_entries) as $feb_map |
  ($jan_map | keys[]) as $key |
  select($jan_map[$key] != $feb_map[$key]) |
  {key: $key, january: $jan_map[$key], february: $feb_map[$key]}
'
```

---

## copy-sheet-for-new-month
**Services:** Sheets

```bash
# 1. Find sheet IDs
gws sheets spreadsheets get --params '{"spreadsheetId":"SPREADSHEET_ID"}' \
  | jq '.sheets[] | {title: .properties.title, sheetId: .properties.sheetId}'

# 2. Copy sheet to same spreadsheet
gws sheets spreadsheets sheets copyTo \
  --params '{"spreadsheetId":"SPREADSHEET_ID","sheetId":SHEET_ID}' \
  --json '{"destinationSpreadsheetId":"SPREADSHEET_ID"}'
# Note new sheet ID

# 3. Rename the copied sheet
gws sheets spreadsheets batchUpdate \
  --params '{"spreadsheetId":"SPREADSHEET_ID"}' \
  --json '{
    "requests": [{
      "updateSheetProperties": {
        "properties": {"sheetId": NEW_SHEET_ID, "title": "March 2026"},
        "fields": "title"
      }
    }]
  }'
```

---

## create-expense-tracker
**Services:** Sheets, Drive

```bash
# 1. Create spreadsheet
gws sheets spreadsheets create \
  --json '{"properties": {"title": "Expense Tracker 2026"}}'

# 2. Add headers
gws sheets +append \
  --spreadsheet-id "SPREADSHEET_ID" \
  --range "Sheet1" \
  --json '[["Date","Description","Category","Amount","Receipt URL"]]'

# 3. Add sample entry
gws sheets +append \
  --spreadsheet-id "SPREADSHEET_ID" \
  --range "Sheet1" \
  --json '[["2026-03-09","Coffee meeting","Meals",12.50,""]]'

# 4. Share with manager
gws drive permissions create \
  --params '{"fileId":"SPREADSHEET_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"writer","type":"user","emailAddress":"manager@example.com"}'
```

---

## create-events-from-sheet
**Services:** Sheets, Calendar

```bash
# 1. Read event data from sheet
# Expected columns: Summary | Date | StartTime | EndTime | Description
gws sheets +read \
  --spreadsheet-id "SPREADSHEET_ID" \
  --range "Events!A2:E"

# 2. For each row, create a calendar event
gws calendar events insert \
  --params '{"calendarId":"primary","sendUpdates":"all"}' \
  --json '{
    "summary": "Event Name",
    "start": {"dateTime": "2026-03-15T10:00:00", "timeZone": "America/New_York"},
    "end": {"dateTime": "2026-03-15T11:00:00", "timeZone": "America/New_York"},
    "description": "Event description"
  }'
```

---

## generate-report-from-sheet
**Services:** Sheets, Docs, Drive

```bash
# 1. Read sheet data
gws sheets +read --spreadsheet-id "SPREADSHEET_ID" --range "Data!A1:F100"

# 2. Create report doc
gws docs documents create --json '{"title": "Weekly Report - March 9, 2026"}'

# 3. Write report content
gws docs +write --doc-id "DOC_ID" \
  --content "# Weekly Report\n\n## Summary\n[analysis]\n\n## Data\n[table]"

# 4. Share with stakeholders
gws drive permissions create \
  --params '{"fileId":"DOC_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"reader","type":"user","emailAddress":"stakeholder@example.com"}'
```

---

## log-deal-update
**Services:** Sheets, Drive

```bash
# 1. Find the tracking sheet
gws drive files list \
  --params '{"q":"name='\''Deal Tracker'\''","mimeType":"application/vnd.google-apps.spreadsheet"}' \
  | jq -r '.files[0].id'

# 2. Optional: verify current data
gws sheets +read --spreadsheet-id "SPREADSHEET_ID" --range "Deals!A:A"

# 3. Append new deal row
gws sheets +append \
  --spreadsheet-id "SPREADSHEET_ID" \
  --range "Deals" \
  --json '[["2026-03-09","Acme Corp","Proposal Sent","$50,000","Enterprise AI","Follow up Fri"]]'
```

---

## sync-contacts-to-sheet
**Services:** People, Sheets

```bash
# 1. List directory contacts
gws people people listDirectoryPeople \
  --params '{"readMask":"names,emailAddresses,phoneNumbers,organizations","pageSize":100}' \
  --page-all

# 2. Create spreadsheet
gws sheets spreadsheets create --json '{"properties":{"title":"Directory Contacts"}}'

# 3. Add headers
gws sheets +append \
  --spreadsheet-id "SPREADSHEET_ID" \
  --range "Sheet1" \
  --json '[["Name","Email","Phone","Organization"]]'

# 4. Append contact rows (one per person from step 1)
gws sheets +append \
  --spreadsheet-id "SPREADSHEET_ID" \
  --range "Sheet1" \
  --json '[["Jane Smith","jane@example.com","555-1234","Acme Corp"]]'
```
