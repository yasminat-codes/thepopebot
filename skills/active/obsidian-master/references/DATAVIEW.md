# Dataview — Core Reference

## 1. Setup

**Enable Dataview plugin:**
Settings → Community Plugins → Dataview → Enable

**Required for DataviewJS and inline queries:**
Settings → Community Plugins → Dataview → Options
- Enable "Enable JavaScript Queries"
- Enable "Enable Inline Queries"
- Set "Inline Query Prefix" to `=` (default)

---

## 2. Query Types

All queries use fenced code blocks with language `dataview` or `dataviewjs`.

### LIST

Renders a bullet list of matching notes.

````markdown
```dataview
LIST
FROM "03-Areas/smarterflo/clients"
WHERE status = "active"
```
````

### TABLE

Renders a column-based table. First column is always the file link.

````markdown
```dataview
TABLE status, deadline, owner
FROM "01-Projects"
WHERE status != "completed"
SORT deadline ASC
```
````

`TABLE WITHOUT ID` removes the default file link column — useful when showing a field as the first column instead:

````markdown
```dataview
TABLE WITHOUT ID file.link AS "Note", status AS "Status"
FROM #client
```
````

### TASK

Renders checklist items from matching notes.

````markdown
```dataview
TASK
FROM "01-Projects"
WHERE !completed
SORT file.mtime DESC
```
````

**Tasks plugin compatibility note:** Dataview TASK queries read raw markdown checkboxes (`- [ ]`). If you use the Tasks plugin, use Tasks plugin syntax (`due::`, `scheduled::`) for task queries — Dataview cannot read Tasks plugin metadata. For due dates in Dataview, use inline fields: `Due:: 2026-03-10`.

### CALENDAR

Renders a calendar view. Requires a date field in the note.

````markdown
```dataview
CALENDAR date
FROM "00-Daily-Notes"
```
````

The field used must resolve to a valid date. Use ISO format: `YYYY-MM-DD`.

---

## 3. Metadata Sources

### Frontmatter YAML

```yaml
---
status: active
client: Synthex
deadline: 2026-04-01
tags: [client, active]
---
```

Reference in queries: `WHERE status = "active"`

### Inline Fields

Written anywhere in the note body:

```markdown
Status:: active
Client:: Synthex
Due:: 2026-03-15
```

Reference in queries: `WHERE Status = "active"` (case-insensitive in Dataview)

### Implicit Fields (always available — no setup required)

| Field | Value |
|-------|-------|
| `file.name` | Note filename without extension |
| `file.path` | Full vault path |
| `file.folder` | Folder path |
| `file.ctime` | Created timestamp |
| `file.mtime` | Last modified timestamp |
| `file.size` | File size in bytes |
| `file.tags` | Array of all tags |
| `file.link` | Wikilink to the note |
| `file.day` | Date extracted from filename (if date-based name) |

---

## 4. Core Clauses

### FROM — source selection

```dataview
FROM "folder/path"             -- all notes in folder (recursive)
FROM #tag                      -- notes with this tag
FROM [[Note Name]]             -- notes linked FROM this note
FROM -"folder"                 -- exclude folder
FROM "01-Projects" OR #active  -- combine sources
FROM "01-Projects" AND #urgent -- intersection
```

### WHERE — filter conditions

```dataview
WHERE status = "active"
WHERE deadline <= date(today)
WHERE contains(file.tags, "#client")
WHERE status != "completed"
WHERE deadline AND deadline < date(today)   -- field exists AND condition
WHERE !completed                            -- tasks only: not completed
```

**Date comparisons:**

```dataview
WHERE file.mtime >= date(today) - dur(7 days)
WHERE deadline = date(today)
WHERE file.ctime >= date("2026-01-01")
```

### SORT — ordering

```dataview
SORT file.mtime DESC           -- newest first
SORT deadline ASC              -- earliest deadline first
SORT status ASC, deadline DESC -- multi-column sort
```

### LIMIT — max results

```dataview
LIMIT 10
```

---

## 5. Ready-to-Use Queries for Yasmine's Vaults

### All notes modified today

````markdown
```dataview
LIST
WHERE file.mtime >= date(today)
SORT file.mtime DESC
```
````

### Tasks due this week

````markdown
```dataview
TASK
WHERE Due >= date(today) AND Due <= date(today) + dur(7 days)
WHERE !completed
SORT Due ASC
```
````

### Notes in a specific folder as a table

````markdown
```dataview
TABLE status AS "Status", file.mtime AS "Last Modified"
FROM "02-Projects/business"
SORT file.mtime DESC
```
````

### All notes with a specific tag

````markdown
```dataview
LIST
FROM #client
SORT file.name ASC
```
````

### Client profiles table (Smarterflo vault)

````markdown
```dataview
TABLE company AS "Company", status AS "Status", contact AS "Contact", next_action AS "Next Action"
FROM "03-Areas/smarterflo/clients"
WHERE file.name != "_client-template"
SORT status ASC, file.name ASC
```
````

### Inbox count (notes in 06-Inbox/)

````markdown
```dataview
TABLE file.ctime AS "Added"
FROM "06-Inbox"
SORT file.ctime ASC
```
````

### Recent notes — last 7 days

````markdown
```dataview
TABLE file.folder AS "Folder", file.mtime AS "Modified"
WHERE file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
LIMIT 20
```
````

### Unresolved decisions (status:: pending)

````markdown
```dataview
TABLE decision AS "Decision", date AS "Date", owner AS "Owner"
FROM "00-Command-Center"
WHERE status = "pending"
SORT date DESC
```
````

### All MOC notes

````markdown
```dataview
LIST
FROM #moc
SORT file.name ASC
```
````

### Content queue by status

````markdown
```dataview
TABLE platform AS "Platform", content_type AS "Type", status AS "Status", publish_date AS "Publish Date"
FROM "15-Smarterflo/LinkedIn-Strategy"
WHERE file.name != "_template"
SORT status ASC, publish_date ASC
```
````

---

## 6. Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Query returns nothing | Wrong folder path | Check exact path with capital/lowercase — Dataview paths are case-sensitive on some systems |
| `date is not a function` | Old Dataview version | Update Dataview plugin |
| Field not found / returns null | Field not in frontmatter or wrong spelling | Check exact field name; Dataview is case-insensitive but the field must exist |
| Wrong date format | Date stored as string, not `YYYY-MM-DD` | Use ISO format in frontmatter: `deadline: 2026-03-15` |
| Missing FROM returns everything | No FROM clause — intentional behavior | Add FROM clause to scope the query |
| Inline query shows raw text | Inline queries not enabled | Settings → Dataview → Enable Inline Queries |
| Tasks not showing | Tasks plugin metadata not readable | Use inline fields (`Due::`) instead of Tasks plugin fields for Dataview |
| Calendar shows no dots | Date field missing or wrong name | Confirm the field name in the query matches exactly what's in the notes |
