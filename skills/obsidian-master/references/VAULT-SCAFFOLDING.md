# Vault Scaffolding Reference

Instructions for the `/obsidian-master:setup` mode. Use when a user asks to set up, build from scratch, scaffold, or create structure in a vault.

---

## 1. When to Use This Reference

Trigger on phrases like:
- "set up my vault"
- "build my vault from scratch"
- "scaffold [vault name]"
- "create the folder structure"
- "initialize Yasmine-OS"
- "I want to start fresh"

Do not run scaffolding without completing the intake interview first.

---

## 2. Intake Interview (3 Questions Before Any Work)

Use AskUserQuestion for each. Do not ask all at once.

**Question 1 — Which vault?**

```
Which vault are we setting up?

Options:
  A) Yasmine-OS (personal OS — life, learning, systems)
  B) Smarterflo (business vault)
  C) A different vault — I'll specify
```

**Question 2 — Methodology?**

```
What organizational methodology do you want to use?

Options:
  A) PARA (recommended — already your system in Smarterflo)
  B) Zettelkasten (atomic notes, heavy linking)
  C) Johnny.Decimal (numbered areas)
  D) Custom structure — I'll describe it
```

**Question 3 — Primary purpose?**

```
What's the primary purpose of this vault?

Options:
  A) Personal OS — life, habits, learning, projects
  B) Business — client work, content, decisions
  C) Mixed — both personal and professional
  D) Specialized — just for [topic] (I'll describe)
```

Only proceed after all 3 questions are answered.

---

## 3. PARA Structure for Obsidian

This is Yasmine's proven system. Recommend PARA unless she explicitly chooses otherwise.

```
00-Dashboard/           ← Home note, quick capture, navigation hub
01-Projects/            ← Active projects with defined end dates
02-Areas/               ← Ongoing responsibilities (no end date)
03-Resources/           ← Reference material organized by topic
04-Archive/             ← Completed or inactive items
05-Templates/           ← Reusable templates for notes and projects
06-Inbox/               ← Unprocessed captures — review daily
```

### Folder Naming Convention

Prefix with numbers to force consistent sidebar order. Use two-digit prefixes (`00-`, `01-`) for top-level folders. Subdirectories do not need number prefixes unless ordering matters.

---

## 4. Core Files to Create on Setup

### 00-Dashboard/Home.md

The vault homepage. Should be set as the Homepage plugin target.

```markdown
# Yasmine-OS

> Last updated: {{date}}

## Today

```dataview
TASK
WHERE !completed
AND due = date(today)
SORT due ASC
```

## Inbox

```dataview
LIST
FROM "06-Inbox"
SORT file.mtime DESC
LIMIT 10
```

## Recent Notes

```dataview
TABLE file.mtime AS "Modified"
WHERE file.folder != "05-Templates"
SORT file.mtime DESC
LIMIT 15
```
```

### 00-Dashboard/Capture.md

Fast capture note. Keep it open in a sidebar pane.

```markdown
# Quick Capture

Dump anything here. Process weekly.

---

-
```

### 06-Inbox/README.md

Processing instructions for the inbox.

```markdown
# Inbox Processing

Review daily or weekly. For each note:

1. Is it a project? → Move to `01-Projects/`
2. Is it an ongoing responsibility? → Move to `02-Areas/`
3. Is it reference material? → Move to `03-Resources/`
4. Is it done or irrelevant? → Move to `04-Archive/` or delete
5. Is it a template? → Move to `05-Templates/`

**Processing rule:** Empty the inbox before the end of the week.
```

---

## 5. Bash Commands to Create the Structure

Replace `VAULT_PATH` with the target vault base path.

```bash
VAULT_PATH="/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS"

mkdir -p "$VAULT_PATH/00-Dashboard"
mkdir -p "$VAULT_PATH/01-Projects"
mkdir -p "$VAULT_PATH/02-Areas"
mkdir -p "$VAULT_PATH/03-Resources"
mkdir -p "$VAULT_PATH/04-Archive"
mkdir -p "$VAULT_PATH/05-Templates"
mkdir -p "$VAULT_PATH/06-Inbox"

echo "Folders created:"
ls "$VAULT_PATH"
```

Create the core files after the directories exist using the REST API (PUT) or Write tool.

---

## 6. Post-Setup Checklist

After scaffolding, walk Yasmine through these manual steps in Obsidian:

- [ ] Settings → Files & Links → Default location for new notes → set to `06-Inbox`
- [ ] Settings → Core Plugins → Templates → set Templates folder to `05-Templates`
- [ ] Settings → Community Plugins → Homepage → set to `00-Dashboard/Home.md`
- [ ] Settings → Community Plugins → Templater → set template folder to `05-Templates`
- [ ] Settings → Editor → Default view mode → Reading (optional preference)
- [ ] Open `00-Dashboard/Home.md` and verify Dataview queries render correctly
- [ ] Pin `00-Dashboard/Capture.md` in a sidebar pane for fast capture

---

## 7. Starter Dataview Dashboard for Home.md

Copy this block into `00-Dashboard/Home.md` after setup. Requires the Dataview plugin (installed in Yasmine-OS).

```markdown
## Tasks Due Today

```dataview
TASK
WHERE !completed
AND due = date(today)
SORT due ASC
```

## Overdue

```dataview
TASK
WHERE !completed
AND due < date(today)
SORT due ASC
```

## Inbox Count

```dataview
TABLE rows.file.name AS "Notes"
FROM "06-Inbox"
WHERE file.name != "README"
GROUP BY "Inbox (" + length(rows) + " notes)"
```

## Recently Modified

```dataview
TABLE file.mtime AS "Last Modified", file.folder AS "Location"
WHERE file.folder != "05-Templates"
AND file.name != "Home"
SORT file.mtime DESC
LIMIT 20
```
```
