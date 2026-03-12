# Obsidian Task Management

## Core Checkbox Syntax

Works natively in Obsidian — no plugins required:

```markdown
- [ ] Todo item
- [x] Completed item
- [/] In progress (some themes render this)
- [-] Cancelled (some themes render this)
```

---

## Tasks Plugin (installed in Yasmine-OS)

Extends native checkboxes with dates, priorities, recurrence, and querying.

### Date Fields

| Field | Emoji syntax | Text syntax | Meaning |
|-------|-------------|-------------|---------|
| Due | `🗓️ 2024-01-15` | `due: 2024-01-15` | Must be done by this date |
| Scheduled | `⏳ 2024-01-14` | `scheduled: 2024-01-14` | Planned to work on this day |
| Start | `🛫 2024-01-13` | `start: 2024-01-13` | Not visible before this date |
| Done | `✅ 2024-01-15` | Auto-added when checked off | Completion timestamp |
| Created | `➕ 2024-01-10` | Auto-added if enabled | When task was created |

Full task example:
```markdown
- [ ] Submit client proposal 🔺 🗓️ 2024-01-20 ⏳ 2024-01-18 🔁 every month
```

### Priority Flags

| Emoji | Priority | Use for |
|-------|----------|---------|
| `🔺` | Highest | Urgent + important, blocks others |
| `⏫` | High | Important, do today |
| `🔼` | Medium | Normal priority |
| `🔽` | Low | Nice to have |
| `⏬` | Lowest | Someday/maybe |

### Recurrence

```markdown
🔁 every day
🔁 every week
🔁 every month
🔁 every weekday
🔁 every 2 weeks
🔁 every year
🔁 every Monday
```

When a recurring task is checked off, a new instance is created with the next due date.

---

## Querying Tasks

Tasks plugin renders live task queries anywhere in the vault.

### Basic query block

````markdown
```tasks
not done
due today
sort by priority
```
````

### Common filters

| Filter | What it shows |
|--------|--------------|
| `not done` | Incomplete tasks only |
| `done` | Completed tasks |
| `due today` | Due on today's date |
| `due before tomorrow` | Overdue + today |
| `due this week` | Due within 7 days |
| `has due date` | Tasks with any due date |
| `no due date` | Tasks without due dates |
| `priority is high` | High priority only |
| `priority is highest` | Highest priority only |
| `scheduled today` | Scheduled for today |
| `tags include #project/client` | Tagged tasks |
| `path includes Projects/` | From a specific folder |

### Combining filters

````markdown
```tasks
not done
due before tomorrow
priority is high
sort by due
limit 10
```
````

### Display options

````markdown
```tasks
not done
group by due
sort by priority
hide due date
show urgency
```
````

---

## GTD Workflow in Obsidian

### 5-step GTD cycle

| Step | Action | Where in vault |
|------|--------|---------------|
| **Capture** | Dump everything, don't filter | `06-Inbox/Capture.md` |
| **Clarify** | Is it actionable? What's the next action? | Process inline in inbox |
| **Organize** | File to the right bucket | Projects, Areas, Someday |
| **Reflect** | Weekly review — what's stale, what's next | Weekly note |
| **Engage** | Work from today's filtered task list | Daily note query |

### Inbox processing questions
- Is it actionable? If no → reference or trash
- Does it take <2 min? Do it now
- Is it a project (multiple steps)? Create a project note
- What is the very next physical action?

### Recommended file locations

```
01-Projects/          # Active, has next actions
02-Areas/             # Ongoing responsibilities
03-Resources/         # Reference material
04-Archive/           # Done or inactive
06-Inbox/Capture.md   # Unprocessed capture
```

---

## Recommended Daily Task Dashboard

Paste in your daily note template — combines Dataview + Tasks:

````markdown
## Today's Tasks

```tasks
not done
scheduled today
sort by priority
```

## Overdue

```tasks
not done
due before today
sort by due
```

## Due This Week

```tasks
not done
due after today
due before in 7 days
sort by due
```
````

---

## Plugins Not Currently Installed (Worth Recommending)

**Kanban** — visual task boards in markdown:
- Lists = columns: `## Backlog`, `## In Progress`, `## Done`
- Cards = list items with metadata
- Suggest install if Yasmine wants a visual board view

**Projects** — table/board/calendar/gallery views of a folder's notes:
- Multi-view project management
- Suggest if she wants spreadsheet-style task tracking

Both available under Settings → Community Plugins → Browse.
