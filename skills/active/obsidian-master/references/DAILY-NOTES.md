# Daily Notes & Periodic Notes

## Core Daily Notes Setup

Settings → Core Plugins → Daily Notes → Enable

| Setting | Recommended value | Why |
|---------|------------------|-----|
| Date format | `YYYY-MM-DD` | ISO standard, sorts chronologically |
| New file location | `00-Dashboard/Daily/` | Keeps root clean |
| Template file | `10-Templates/Daily Note` | Auto-populates on creation |
| Open on startup | Optional | Useful if daily note is your home base |

Open today's note: Cmd+Shift+D (default hotkey) or click date in Calendar sidebar.

---

## Periodic Notes Plugin (Recommended — Not Installed)

Extends Daily Notes to weekly, monthly, quarterly, yearly cycles. Each level has its own format, folder, and template.

| Period | Date format | Example | Suggested folder |
|--------|------------|---------|-----------------|
| Daily | `YYYY-MM-DD` | `2024-01-15` | `00-Dashboard/Daily/` |
| Weekly | `YYYY-[W]WW` | `2024-W03` | `00-Dashboard/Weekly/` |
| Monthly | `YYYY-MM` | `2024-01` | `00-Dashboard/Monthly/` |
| Quarterly | `YYYY-[Q]Q` | `2024-Q1` | `00-Dashboard/Quarterly/` |
| Yearly | `YYYY` | `2024` | `00-Dashboard/Yearly/` |

Install: Settings → Community Plugins → Browse → "Periodic Notes"

---

## Calendar Plugin (Installed in Yasmine-OS)

Right-sidebar calendar view. Works with both Daily Notes and Periodic Notes.

- Click any date → opens that day's note (creates it if missing)
- Click week number → opens weekly note (requires Periodic Notes)
- Dots on dates = activity indicator (more dots = more content)
- Toggle week numbers: Calendar settings → Show week numbers

The Calendar plugin is the fastest way to navigate to any past or future note by date.

---

## Recommended Folder Structure

```
00-Dashboard/
├── Daily/
│   ├── 2024-01-14.md
│   └── 2024-01-15.md
├── Weekly/
│   └── 2024-W03.md
└── Monthly/
    └── 2024-01.md
```

---

## Journal Workflows

### Morning routine (5-10 min)
1. Open today's daily note (Cmd+Shift+D)
2. Set 1-3 intentions for the day
3. Review tasks due today (Tasks query auto-populates from template)
4. Note one thing to move forward on a current project

### Evening routine (5 min)
1. Log what actually happened — brief bullets, not prose
2. Check off completed tasks
3. Capture anything that surfaced during the day to `06-Inbox/Capture.md`
4. Jot tomorrow's must-dos at the bottom

### Weekly review (20-30 min, suggest Sunday or Monday)
Open your weekly note and work through:
- What did I complete this week? (Tasks query: `done this week`)
- What's still open from last week that matters?
- What are the most important moves for next week?
- Any patterns in what's blocking me?

---

## Rolling Up Notes with Dataview

### All daily notes from this week

````markdown
```dataview
LIST
FROM "00-Dashboard/Daily"
WHERE file.day >= date(today) - dur(7 days)
SORT file.day DESC
```
````

### Tasks completed this week

````markdown
```tasks
done this week
sort by done
```
````

### Habit tracking rollup (if using frontmatter)

Add to daily note frontmatter:
```yaml
---
mood: 7
exercise: true
deep_work_hours: 3
---
```

Then query with Dataview:
````markdown
```dataview
TABLE mood, exercise, deep_work_hours AS "Deep Work"
FROM "00-Dashboard/Daily"
WHERE file.day >= date(today) - dur(7 days)
SORT file.day DESC
```
````

---

## Daily Note Template (Suggested)

Save as `10-Templates/Daily Note.md`:

```markdown
---
date: {{date:YYYY-MM-DD}}
week: {{date:YYYY-[W]WW}}
---

## Intentions

-

## Today's Tasks

` ` `tasks
not done
scheduled today
sort by priority
` ` `

## Overdue

` ` `tasks
not done
due before today
` ` `

## Log

-

## Captures

-
```

(Remove spaces from inside backtick fences — shown here to avoid rendering)
