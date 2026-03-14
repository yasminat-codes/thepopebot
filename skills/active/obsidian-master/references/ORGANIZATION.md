# ORGANIZATION.md — Vault Organization Reference

## 1. Folder Structure Methodologies

| Method | Structure | Best for | Trade-off |
|--------|-----------|----------|-----------|
| **PARA** | 4 top-level folders by actionability | Yasmine — action-oriented, project-driven | Requires periodic review to keep folders clean |
| **Zettelkasten** | Flat vault, numeric IDs (e.g. `202501081234`) | Researchers, idea-heavy writers | No inherent folder org; relies entirely on links |
| **Johnny.Decimal** | Strict `AC.ID` numbering (e.g. `12.03`) | People who want rigid, predictable locations | Inflexible — adding categories breaks the system |
| **Flat vault** | No folders; everything in root with tags | Power taggers; search-first users | Scales poorly; no visual hierarchy |

**Recommendation for Yasmine:** PARA. It maps directly to how you already think about work — actionability over topic. You don't file by subject; you file by "what do I do with this?"

---

## 2. PARA in Obsidian — Yasmine's Numbering Convention

```
00-Dashboard/       Hub notes, MOCs, quick-access index
01-Projects/        Has a defined end date and goal
02-Areas/           Ongoing responsibility, no end date
03-Resources/       Topics useful someday, no active need
04-Archive/         Inactive projects and resources
05-Templates/       Note templates only — nothing else
06-Inbox/           Capture first, process later
```

### Decision Guide

```
"Am I actively working toward a specific outcome?" → 01-Projects/
"Is this something I maintain indefinitely?"       → 02-Areas/
"Is this interesting but not actionable yet?"      → 03-Resources/
"Is this done / no longer relevant?"               → 04-Archive/
"Did I just capture this and haven't processed it?"→ 06-Inbox/
```

### What goes where — examples

| Content | Folder |
|---------|--------|
| Smarterflo brand redesign | 01-Projects/ |
| Health — nutrition and fitness | 02-Areas/ |
| AI tools research | 03-Resources/ |
| Old freelance client | 04-Archive/ |
| Meeting note from 5 minutes ago | 06-Inbox/ |
| Daily note template | 05-Templates/ |

### Naming sub-folders inside Projects and Areas

Use a short descriptor, no spaces:
```
01-Projects/
├── Smarterflo-Website-Relaunch/
├── Yasmine-OS-Build/
└── LinkedIn-Blitz-Q1/
```

---

## 3. Maps of Content (MOCs)

MOCs are index notes. They link to related notes by topic — no original content, just organized navigation.

**When to create a MOC:** when you have 5 or more notes on a related topic and navigating them becomes cognitive overhead.

**MOC template:**

```markdown
---
type: moc
created: YYYY-MM-DD
tags: [type/moc]
---

# [Topic] MOC

Brief description of what this MOC covers.

## [Sub-topic A]
- [[Note 1]]
- [[Note 2]]

## [Sub-topic B]
- [[Note 3]]

## All related notes

```dataview
LIST
FROM [[]]
SORT file.mtime DESC
```
```

**Naming conventions:**

| Convention | Example | Use |
|------------|---------|-----|
| Underscore prefix | `_MOC-AI-Strategy.md` | Sorts to top in file explorer |
| Suffix | `AI Strategy MOC.md` | Natural language, no sorting trick |
| Folder-level MOC | `_INDEX.md` inside a folder | Acts as folder readme |

**Where to put MOCs:** `00-Dashboard/` for vault-wide MOCs. Inside a project/area folder for topic-specific MOCs.

---

## 4. Tag Strategy

Use tags for cross-cutting concerns — things that don't fit cleanly into one folder.

**What tags are for:**
- Status (active, draft, archived)
- Note type (atomic, moc, daily, reference)
- Format (video, article, podcast)
- Project or area label when a note spans multiple

**What tags are NOT for:** replacing folder structure.

### Tag hierarchy (use nested tags)

```
#status/active
#status/archived
#status/draft

#type/atomic
#type/moc
#type/daily
#type/reference
#type/project

#format/video
#format/article
#format/podcast

#area/health
#area/finance
#area/smarterflo
```

### Recommended tags for Yasmine

| Tag | When to apply |
|-----|--------------|
| `#status/active` | Note you're currently working with |
| `#status/draft` | Incomplete, not ready |
| `#status/archived` | Done, kept for reference |
| `#type/atomic` | One idea, permanent note |
| `#type/moc` | Index/navigation note |
| `#type/daily` | Daily note |
| `#type/reference` | Factual reference, not your thinking |
| `#area/smarterflo` | Business content |
| `#area/personal` | Personal OS content |
| `#capture/inbox` | Hasn't been processed yet |

**Plugin:** Tag Wrangler — bulk rename, merge, or delete tags across the vault. Essential for keeping tags clean as the vault grows.

---

## 5. Archiving Workflow

**Rule: never delete — archive.** Archived notes are searchable, linkable, and recoverable.

**Monthly review (15 minutes):**
1. Open `01-Projects/` — move completed or stalled projects to `04-Archive/Projects/`
2. Open `06-Inbox/` — process every note: move, delete fleeting notes, or promote to permanent
3. Update status tags on notes that have changed state

**Archive folder structure** mirrors active folders:
```
04-Archive/
├── Projects/
│   └── Smarterflo-Website-Relaunch/
└── Areas/
    └── Old-Gym-Routine/
```

**Archive frontmatter addition:** add `archived: YYYY-MM-DD` and change `status: active` → `status: archived`.

---

## 6. Bookmarks Panel

Use Obsidian's built-in Bookmarks panel (star icon in left sidebar) for:
- Frequently accessed MOCs and hub notes
- Saved searches (e.g. "all draft notes", "inbox items")
- Current active project note
- Vault `00-Dashboard/` index

Keep bookmarks to under 10 items — if everything is bookmarked, nothing is.

---

## 7. File Explorer Sorting

**Recommended:** Sort by modified time (most recently edited at top).

Set in File Explorer panel menu → Sort order → Modified time (new to old).

This surfaces your active work automatically without manual reordering.

**Tip:** Prefix MOC and index notes with `_` (underscore) — they sort to the top alphabetically even with time-based sorting disabled.
