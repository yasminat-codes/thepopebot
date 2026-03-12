# Search & Navigation

## Core Search Operators

Open core search: Cmd+Shift+F (or click the magnifying glass in sidebar).

| Operator | Syntax | Example |
|----------|--------|---------|
| File name | `file:name` | `file:client-brief` |
| Path | `path:folder/` | `path:03-Areas/clients/` |
| Tag | `tag:#tagname` | `tag:#status/active` |
| Content | `content:phrase` | `content:"follow up"` (default, can omit `content:`) |
| Same line | `line:("term1" "term2")` | `line:("Smarterflo" "proposal")` |
| Block | `block:term` | `block:revenue` |
| Exact phrase | `"exact phrase"` | `"AI implementation"` |
| Exclude | `-term` | `-archived` |
| Section | `section:heading` | `section:Next Actions` |

### Combining operators

Multiple operators are AND by default:
```
file:client tag:#status/active "follow up"
```
Finds notes with "client" in filename, tagged #status/active, containing "follow up".

Use `OR` explicitly:
```
tag:#status/active OR tag:#status/pending
```

---

## Omnisearch (Installed in Yasmine-OS)

Full-text search with fuzzy matching. Significantly faster and smarter than core search.

**Open:** Cmd+Shift+O (configure in hotkeys if different) or command palette → "Omnisearch"

**What it does that core search doesn't:**
- Fuzzy matching — finds "Smarterflo" when you type "smartflo"
- Searches inside PDFs and images (if OCR enabled in settings)
- Shows context snippet around the match — you see *where* in the note the term appears
- Ranks results by relevance, not just recurrence
- Much faster on large vaults

**Omnisearch vs core search:**

| Task | Use |
|------|-----|
| You know the exact note name | Quick Switcher (Cmd+O) |
| You remember content but not the file | Omnisearch |
| You need boolean/operator search | Core search |
| You want to search across file types | Omnisearch |
| You want to save a search | Core search |

---

## Quick Switcher

**Hotkey:** Cmd+O

The fastest way to open a note by name. Fuzzy matches — you don't need to type the full name.

- Type partial words: `cl prop` finds `Client-Proposal-Acme.md`
- Type initial letters: `sfp` finds `Smarterflo-Pricing.md`
- Create a new note: type the name you want → if no match → press Enter to create

**Quick Switcher++** (not installed — worth recommending):
- Adds: search by heading (navigate into a note section), alias search, recent files, starred files
- Install if Yasmine wants faster in-note navigation

---

## Regex Search

Enable: Settings → Search → Enable regular expression search

| Pattern | Finds |
|---------|-------|
| `\d{4}-\d{2}-\d{2}` | All dates in YYYY-MM-DD format |
| `\[!.+\]` | All callout blocks |
| `\[\[.+\]\]` | All wikilinks |
| `#[a-z]+\/[a-z]+` | All nested tags |
| `- \[.\]` | All checkboxes (any state) |
| `- \[ \]` | Unchecked checkboxes only |
| `\$\d+` | Dollar amounts |

Enable regex in core search by clicking the `.*` button in the search bar.

---

## Saved Searches

Bookmark a frequently-used search:
1. Run the search
2. Click the bookmark icon in the search panel
3. Named searches appear in the Search panel bookmark list

Useful for recurring searches like "overdue client items" or "untagged notes".

---

## Advanced URI (Installed in Yasmine-OS)

Advanced URI lets you open notes, run searches, and perform actions via URL. Useful for automation and cross-app linking.

### Common URI patterns

Open a note:
```
obsidian://advanced-uri?vault=Smarterflo&filepath=03-Areas/clients/Acme.md
```

Search and open search panel:
```
obsidian://advanced-uri?vault=Smarterflo&search=follow+up
```

Open daily note:
```
obsidian://advanced-uri?vault=Smarterflo&daily=true
```

Use from Claude or scripts to open specific notes programmatically.

---

## Search Workflow Quick Reference

| Task | Best tool | Syntax |
|------|-----------|--------|
| Open note by name | Quick Switcher | Cmd+O → fuzzy name |
| Find content you vaguely remember | Omnisearch | Cmd+Shift+O → keywords |
| Find notes with a specific tag | Core search | `tag:#your-tag` |
| Find tasks due this week | Tasks plugin query | `due this week` |
| Find notes in a folder | Core search | `path:folder-name/` |
| Find notes linking to a note | Backlinks panel | Click note → open backlinks |
| Find all untagged notes | Dataview | `WHERE length(tags) = 0` |
| Find text in a specific folder | Core search | `path:03-Areas/ "search term"` |
| Find all notes created this week | Dataview | `WHERE file.cday >= date(today) - dur(7 days)` |
