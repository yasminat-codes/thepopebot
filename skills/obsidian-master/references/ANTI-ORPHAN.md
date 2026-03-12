# ANTI-ORPHAN.md — Zero-Orphan-Note Protocol

Every note in Yasmine's vaults must be connected to the knowledge graph. An orphaned note is a failure state. This reference covers what orphans are, why they happen, and the three-layer system that prevents and repairs them.

---

## 1. What Is an Orphan Note

**Definition:** A note with zero outbound wikilinks AND zero inbound backlinks. It exists in the vault but has no connections to anything else.

A note with outbound links but no inbound links is a **semi-orphan** — better than fully orphaned, but still a gap to address.

### Why orphans are a failure state

| Problem | Impact |
|---------|--------|
| Not discoverable via graph | You won't find it while browsing related notes |
| Skipped by Dataview queries | Queries that start `FROM` a folder still miss it if nothing references it |
| Knowledge decay | Insights captured but never revisited decay to zero value |
| Graph health | Many orphans = a fragmented vault that doesn't surface connections |
| Search ≠ network | Omnisearch finds it, but you only search for things you already know to search for |

### Common causes

- **Quick capture** — idea saved to inbox without linking to anything
- **Pasted content** — dumped research or notes without a parent
- **Forgotten MOC update** — note created in a folder but never added to the area's MOC
- **Renamed note** — the old links now point to nowhere, leaving the renamed note without inbound links
- **Template skipped** — new note created without using the Templater template (no parent link field filled in)

---

## 2. Three-Layer Defense System

### Layer 1 — Prevention (Templater)

Every template must include a `parent:` frontmatter field and a parent link in the body. When a new note is created from a template, Templater prompts for the parent note before the note is saved. This guarantees at least one outbound link exists from the moment the note is created.

**Templater snippet — parent note selector:**

```javascript
<%*
const parent = await tp.system.suggester(
  item => item.basename,
  tp.app.vault.getMarkdownFiles(),
  false,
  "Link to parent note..."
);
if (parent) tR += `\n- [[${parent.basename}]]`;
-%>
```

**How to use it in a template:**

```markdown
---
parent: <% tp.file.title %>
created: <% tp.date.now("YYYY-MM-DD") %>
tags:
---

## Parent

<%*
const parent = await tp.system.suggester(
  item => item.basename,
  tp.app.vault.getMarkdownFiles(),
  false,
  "Link to parent note..."
);
if (parent) tR += `- [[${parent.basename}]]`;
-%>

## Notes

```

**Setup in Templater:**

1. Settings → Community Plugins → Templater → Settings
2. Enable "Trigger Templater on new file creation"
3. Enable "Folder Templates"
4. Map each PARA folder to its template (see table below)

| Folder | Template |
|--------|----------|
| `03-Areas/smarterflo/clients/` | `10-Templates/_client-template.md` |
| `04-Knowledge/competitors/` | `10-Templates/_competitor-template.md` |
| `05-Dev-Context/self-healing/patterns/` | `10-Templates/self-healing-pattern.md` |
| `02-Projects/business/campaigns/` | `10-Templates/_campaign-template.md` |
| `04-Knowledge/` | `10-Templates/_knowledge-template.md` |

Every template file in `10-Templates/` must include the parent selector snippet above.

---

### Layer 2 — Auto-linking (Automatic Linker Plugin)

The Automatic Linker community plugin scans note content on every save. When it finds plain text that matches the exact title of another note in the vault, it converts that text to a wikilink automatically.

**Install:**

1. Settings → Community Plugins → Browse
2. Search: `Automatic Linker`
3. Install → Enable

**Settings to configure after install:**

| Setting | Value | Reason |
|---------|-------|--------|
| Link on save | Enabled | Runs automatically — no manual trigger needed |
| Excluded folders | `10-Templates/, .obsidian/` | Templates should not auto-link their placeholder text |
| Minimum word length | 3 | Avoids linking very short common words |
| Case sensitivity | Disabled | Matches "Smarterflo" and "smarterflo" equally |

**Limitation:** Automatic Linker only matches exact note titles. If a note is titled "Client Onboarding Process" but the text says "client onboarding", it will not match. Fix this by adding aliases to the note's frontmatter:

```yaml
---
aliases:
  - client onboarding
  - onboarding process
---
```

Aliases are recognized by both Automatic Linker and Obsidian's own unlinked mentions detection.

**What it does not do:**

- It does not add the current note to another note's content (that would require editing another file)
- It does not create inbound backlinks — it only creates outbound links from the note being saved
- It does not link to headings or blocks — only to note titles

Use Layer 1 (Templater) for inbound links. Use Layer 2 (Automatic Linker) to catch plain-text references you forgot to wikilink while writing.

---

### Layer 3 — Detection and Repair (Dataview)

Run these queries in a dedicated "Orphan Audit" section of the weekly review note or in the `00-Command-Center/` hub note.

**Full orphan report (table with link counts):**

```dataview
TABLE file.inlinks as "Inbound", file.outlinks as "Outbound"
FROM ""
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
SORT file.mtime DESC
```

**Simple list (faster to scan):**

```dataview
LIST
FROM ""
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
SORT file.mtime DESC
```

**Semi-orphans (outbound links but nothing points to them):**

```dataview
LIST
FROM ""
WHERE length(file.inlinks) = 0 AND length(file.outlinks) > 0
SORT file.mtime DESC
```

**Notes tagged #needs-linking (repair queue):**

```dataview
LIST
FROM #needs-linking
SORT file.mtime DESC
```

**Exclude templates and system folders** by scoping the FROM clause:

```dataview
LIST
FROM "" AND -"10-Templates" AND -".obsidian"
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
SORT file.mtime DESC
```

---

## 3. MOC (Map of Content) Strategy

Every PARA area in both vaults has one MOC note. The MOC is the hub — it lists all notes in the area and receives a backlink from each of them. New notes link to their area MOC via the Templater parent selector, and the MOC uses a Dataview query to dynamically include new notes without manual updates.

### MOC structure

```markdown
---
type: moc
area: smarterflo-clients
tags: moc, smarterflo
---

# Smarterflo Clients — MOC

[[00-Command-Center/Hub]]

## All Clients

​```dataview
TABLE status, next_action
FROM "03-Areas/smarterflo/clients"
SORT file.mtime DESC
​```

## Active Clients

​```dataview
TABLE status, next_action
FROM "03-Areas/smarterflo/clients"
WHERE status = "active"
SORT file.mtime DESC
​```
```

### MOC per vault area

| Area | MOC location |
|------|-------------|
| Smarterflo clients | `03-Areas/smarterflo/clients/_MOC-Clients.md` |
| Competitors | `04-Knowledge/competitors/_MOC-Competitors.md` |
| Dev patterns | `05-Dev-Context/self-healing/_MOC-Self-Healing.md` |
| Brand strategy | `15-Smarterflo/Brand-Strategy/_MOC-Brand.md` |
| LinkedIn | `15-Smarterflo/LinkedIn-Strategy/_MOC-LinkedIn.md` |
| Active campaigns | `02-Projects/business/campaigns/_MOC-Campaigns.md` |

### Smarterflo clients MOC — Dataview examples

```dataview
TABLE status, next_action
FROM "03-Areas/smarterflo/clients"
SORT file.mtime DESC
```

```dataview
TABLE company, engagement_type, start_date
FROM "03-Areas/smarterflo/clients"
WHERE status = "active"
SORT start_date DESC
```

### Linking rule for MOC notes

Every MOC note must link up to the area it belongs to or to the vault hub. Example: `_MOC-Clients.md` links to `[[00-Command-Center/Hub]]`. The hub note is the one note that aggregates all MOCs — it should never be an orphan and should have the most inbound backlinks in the vault.

---

## 4. Rules for Every Template

Every template in `10-Templates/` must include all three of the following. No exceptions.

| Requirement | Why |
|-------------|-----|
| `parent:` frontmatter field (Templater-populated) | Creates the outbound link record |
| At least one `[[wikilink]]` in the body | Actual graph connection — frontmatter alone does not register in the graph |
| `tags:` frontmatter field with at least one tag | Enables Dataview FROM queries and graph color groups |

**Minimal compliant template:**

```markdown
---
parent:
created: <% tp.date.now("YYYY-MM-DD") %>
tags:
---

## Parent

<%*
const parent = await tp.system.suggester(
  item => item.basename,
  tp.app.vault.getMarkdownFiles(),
  false,
  "Link to parent note..."
);
if (parent) tR += `- [[${parent.basename}]]`;
-%>

```

**Non-compliant template (fix these):** A template with no parent link field, no body wikilinks, and no tags will produce orphans on every use. Apply the minimal compliant template above as the baseline for any template that needs correction.

---

## 5. Weekly Orphan Audit

Run this every week during the review in `00-Command-Center/`.

**Where to embed the audit query:** in the weekly review template, under a "Vault Health" section.

**Weekly review vault health block:**

```markdown
## Vault Health

### Orphan Notes (action required)

​```dataview
LIST
FROM "" AND -"10-Templates" AND -".obsidian"
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
SORT file.mtime DESC
​```

### Needs Linking Queue

​```dataview
LIST
FROM #needs-linking
SORT file.mtime DESC
​```
```

**What to do with found orphans:**

| Type | Action |
|------|--------|
| Useful note, just unconnected | Open it, add `[[Parent MOC]]` link in the body, add to the relevant MOC |
| Useful note, wrong folder | Move it to the correct folder, then link it |
| Duplicate of another note | Merge content into the canonical note, delete the orphan |
| Quick capture, fully processed | Delete it — the information is already integrated elsewhere |
| Genuinely unclear | Tag `#needs-linking` and revisit next week |

**Target:** zero fully orphaned notes after the weekly audit. Semi-orphans (outbound but no inbound) are acceptable if the note is new — allow one week before flagging.

---

## 6. Graph View Settings for Orphan Monitoring

Use the graph view as a visual health check, not as a primary audit tool (Dataview is faster and more precise). Open with Cmd+G (macOS).

**Settings to configure:**

| Setting | Value |
|---------|-------|
| Settings → Graph → Show orphans | Enabled |
| Filters → Search | `-path:10-Templates` to hide template clutter |
| Groups → Add group | Query: `tag:#needs-linking`, Color: orange |
| Groups → Add group | Query: `tag:moc`, Color: blue |

**Finding orphans in graph view:**

1. Open graph with Cmd+G
2. In the filter bar, type: `line:(0)` — this filters to nodes with zero connections
3. Nodes that appear are fully orphaned — click to open and fix

**Local graph for individual notes:**

Open any note → three-dot menu → "Open local graph" (or Cmd+click the note in main graph). Depth 1 shows direct connections only. If the local graph shows a single isolated node, that note is an orphan.

---

## 7. The Mandatory Link Rule

**Protocol: before closing any new note, verify the following.**

| Check | Pass condition |
|-------|---------------|
| At least one outbound wikilink | `[[Something]]` exists in the note body |
| Appears in at least one MOC | MOC Dataview query will include this note, OR you have manually added a link to it from the MOC |
| Tags are set | At least one tag in frontmatter |

**If any check fails:**

1. If you have time: fix it immediately — add the wikilink, update the MOC, add the tag.
2. If you do not have time: add `#needs-linking` as a tag. This queues it for the weekly audit. Do not leave a note without even this fallback.

**What not to do:** Do not create a note, skip the Templater parent prompt, and close Obsidian. Even if time is short, add `#needs-linking` as a minimum fallback. Never use a template that omits the parent selector.

**The one-sentence rule:** Every note earns its place in the vault by being connected. A disconnected note is not a note — it is noise.

---

## Quick Reference

| Layer | Tool | Trigger |
|-------|------|---------|
| 1 — Prevention | Templater parent selector | On note creation |
| 2 — Auto-linking | Automatic Linker plugin | On every save |
| 3 — Detection | Dataview orphan queries | Weekly audit |

| Signal | Action |
|--------|--------|
| Dataview orphan list | Add `[[Parent MOC]]` link and update MOC |
| `#needs-linking` tag | Fix during weekly review |
| Isolated node in graph | Same as Dataview finding |
| Templater prompt skipped | Add link manually before closing |
