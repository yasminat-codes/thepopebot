# NOTES.md — Note Types, Naming, and Structure Reference

## 1. Atomic Notes Principle

One idea per note. Self-contained. Linkable.

An atomic note is not a dump of everything you know about a topic — it is one distilled, standalone idea that could be understood without reading any other note. It should be specific enough to link precisely, and complete enough to stand alone.

**Signs a note is not atomic:**
- It has multiple `##` headings covering unrelated ideas
- You can't describe it in one sentence
- Linking to it requires a header anchor because different parts are relevant in different contexts

**Signs it is atomic:**
- You can link to the whole note, not a section
- It expresses one argument, observation, or fact
- It connects naturally to 3–7 other notes

---

## 2. Note Types

| Type | Purpose | Naming | Template |
|------|---------|--------|----------|
| **Fleeting** | Quick capture; process within 24h | `[date]-[brief topic]` | None needed |
| **Literature** | Summary of what you read/watched, in your own words | `[Source title] — notes` | Literature note template |
| **Permanent** | Your original thinking; fully formed idea | Descriptive title (the idea itself) | Permanent note template |
| **Project** | Tracks a specific project; links to tasks and resources | `[Project name]` | Project note template |
| **Hub / MOC** | Index of related notes; no original content | `_MOC-[Topic]` | MOC template |
| **Daily** | Daily log, tasks, reflections | `YYYY-MM-DD` | Daily note template |
| **Reference** | Factual information, definitions, how-to | `[Topic] — reference` | Reference template |

### Fleeting notes
Lived in `06-Inbox/`. Raw capture — voice memo transcription, quick thought, meeting jotting. Not polished. **Must be processed within 24h** or they become noise. Process = decide: keep and promote, delete, or file as-is.

### Literature notes
Summarize what a source says in **your own words**. Do not copy-paste. One note per source or per key concept from the source. Include: source title, author, date, URL/location, and your summary.

### Permanent notes
Your original thinking. Formed from processing fleeting and literature notes. Should express a single idea in your own voice, link to evidence (literature notes) and related ideas (other permanent notes). These are the core of the vault.

### Project notes
One note per project. Tracks: goal, deadline, tasks, related notes, status. Lives in `01-Projects/[Project-Name]/`. Not atomic — it's a hub note for a specific project.

### Hub / MOC notes
No original content. Pure navigation. Links to related notes organized by sub-topic. Lives in `00-Dashboard/` (vault-wide) or inside a project/area folder (topic-specific).

### Daily notes
Created by Periodic Notes plugin. Date-stamped. Captures: what happened, tasks done, tasks due, thoughts worth keeping. Reviewed weekly — anything worth keeping gets extracted and promoted.

### Reference notes
Factual lookups. API docs summary, plugin configuration, how a tool works. Not your thinking — documented facts. Lives in `03-Resources/`.

---

## 3. File Naming Conventions

**Principle: human-readable names over cryptic IDs.**

| Rule | Example |
|------|---------|
| Use the idea as the title | `Compounding is asymmetric.md` |
| Title case for permanent notes | `The Problem With Busy Work.md` |
| Lowercase with hyphens for daily notes | `2026-03-08.md` |
| Date prefix only for daily/periodic notes | `2026-W10.md` (weekly) |
| No special characters except hyphens and underscores | Avoid `?`, `*`, `:`, `|` |
| MOC prefix underscore | `_MOC-AI-Strategy.md` |
| Short and specific over long and vague | `Neon DB connection pooling.md` not `Database notes.md` |

**Avoid:**
- Zettelkasten-style IDs (e.g. `202601081234-note.md`) unless you specifically want that system
- Generic names like `Notes.md`, `Untitled.md`, `Thoughts.md`
- Folder name repeated in file name: `01-Projects/Smarterflo/Smarterflo-notes.md` → just `01-Projects/Smarterflo/Overview.md`

---

## 4. Frontmatter Standards for Yasmine's Vaults

Apply this frontmatter to all notes. Templater handles auto-population when templates are used.

```yaml
---
created: YYYY-MM-DD
modified: YYYY-MM-DD
type: note/project/moc/daily/reference/literature
status: active/archived/draft
tags: []
aliases: []
---
```

| Field | Values | Notes |
|-------|--------|-------|
| `created` | `YYYY-MM-DD` | Set once; never change |
| `modified` | `YYYY-MM-DD` | Update when content changes |
| `type` | `note`, `project`, `moc`, `daily`, `reference`, `literature` | Used in Dataview filters |
| `status` | `active`, `draft`, `archived` | Drives monthly review |
| `tags` | Array of strings | Use `#type/`, `#status/`, `#area/` hierarchy |
| `aliases` | Array of strings | Alternative names for wikilink matching |

**Dataview example using frontmatter:**
```dataview
TABLE status, modified
FROM "01-Projects"
WHERE type = "project" AND status = "active"
SORT modified DESC
```

---

## 5. When to Split a Note

Split when you can extract a section that:
- Stands alone as its own idea
- Could be linked to from a completely different context
- Would be useful without the rest of the parent note

**Signal:** you find yourself writing `[[Note#Heading]]` to link to a section — that section probably deserves its own note.

---

## 6. When to Merge Notes

Merge when:
- Two notes are always linked together and never referenced independently
- One note is a stub that grew into an extension of another
- You have multiple notes covering the same idea from slightly different angles and it creates confusion

**Signal:** every time you open Note A, you immediately open Note B next. They want to be one note.
