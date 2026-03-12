# CSS-SNIPPETS.md — Ready-to-Use Snippet Library

All snippets go in: `.obsidian/snippets/` inside the vault directory.
Install: Settings → Appearance → CSS Snippets → open folder → paste file → click reload icon → toggle on.

---

## 1. custom-callouts.css

Adds three custom callout types: `[!DECISION]`, `[!CLIENT]`, `[!INSIGHT]`.

```css
.callout[data-callout="decision"] {
  --callout-color: 38, 80%, 50%;
  --callout-icon: lucide-check-circle-2;
}
.callout[data-callout="client"] {
  --callout-color: 250, 75%, 58%;
  --callout-icon: lucide-user;
}
.callout[data-callout="insight"] {
  --callout-color: 175, 65%, 42%;
  --callout-icon: lucide-lightbulb;
}
```

---

## 2. colored-folders.css

Colors specific folders in the file explorer by name prefix.

```css
.nav-folder-title[data-path^="00-Dashboard"] { color: var(--color-base-60); }
.nav-folder-title[data-path^="01-Projects"]  { color: #4a9eff; }
.nav-folder-title[data-path^="02-Areas"]     { color: #52b788; }
.nav-folder-title[data-path^="03-Resources"] { color: #9b72cf; }
.nav-folder-title[data-path^="04-Archive"]   { color: var(--color-base-40); font-style: italic; }
.nav-folder-title[data-path^="05-Templates"] { color: #e9a84c; }
.nav-folder-title[data-path^="06-Inbox"]     { color: #e06c75; font-weight: 600; }
```

**Note:** `data-path^=` matches paths that start with the given string.

---

## 3. card-layout.css

Displays Dataview TABLE results as a card grid. Activate per-note via `cssclasses: cards`.

```css
.cards .dataview.table-view-table {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  border: none;
}
.cards .dataview.table-view-table thead { display: none; }
.cards .dataview.table-view-table tbody { display: contents; }
.cards .dataview.table-view-table tbody tr {
  display: flex;
  flex-direction: column;
  background: var(--color-base-10);
  border: 1px solid var(--color-base-25);
  border-radius: 8px;
  padding: 14px 16px;
  transition: box-shadow 0.15s ease;
}
.cards .dataview.table-view-table tbody tr:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
.cards .dataview.table-view-table tbody td {
  border: none;
  padding: 2px 0;
  font-size: 0.9em;
}
.cards .dataview.table-view-table tbody td:first-child {
  font-weight: 600;
  font-size: 1em;
  margin-bottom: 6px;
}
```

---

## 4. clean-tables.css

Minimal table styling with alternating row colors and no visible borders.

```css
.markdown-reading-view table,
.markdown-source-view .cm-embed-block table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.9em;
  border: none;
}
.markdown-reading-view th,
.markdown-source-view .cm-embed-block th {
  background: var(--color-base-20);
  font-weight: 600;
  text-align: left;
  padding: 8px 12px;
  border-bottom: 2px solid var(--color-base-30);
  border-top: none; border-left: none; border-right: none;
}
.markdown-reading-view td,
.markdown-source-view .cm-embed-block td {
  padding: 7px 12px;
  border: none;
  border-bottom: 1px solid var(--color-base-20);
}
.markdown-reading-view tr:nth-child(even) td,
.markdown-source-view .cm-embed-block tr:nth-child(even) td {
  background: var(--color-base-05);
}
.markdown-reading-view tr:hover td,
.markdown-source-view .cm-embed-block tr:hover td {
  background: var(--color-base-15);
}
```

---

## 5. hide-frontmatter.css

Hides raw frontmatter YAML in reading view. Properties panel (Obsidian 1.4+) still works.

```css
.markdown-reading-view .metadata-container {
  display: none;
}
```

---

## 6. custom-checkboxes.css

Styled checkbox variants: done `[x]`, canceled `[-]`, in-progress `[/]`, deferred `[>]`.

```css
li[data-task="x"] .task-list-item-checkbox,
li[data-task="X"] .task-list-item-checkbox { background-color: #52b788; border-color: #52b788; }
li[data-task="x"], li[data-task="X"] { color: var(--color-base-40); text-decoration: line-through; }

li[data-task="-"] .task-list-item-checkbox { background-color: #e06c75; border-color: #e06c75; }
li[data-task="-"] { color: var(--color-base-35); text-decoration: line-through; opacity: 0.6; }

li[data-task="/"] .task-list-item-checkbox {
  background: linear-gradient(135deg, #e9a84c 50%, var(--color-base-20) 50%);
  border-color: #e9a84c;
}
li[data-task="/"] { font-style: italic; }

li[data-task=">"] .task-list-item-checkbox { background-color: var(--color-base-30); border-color: var(--color-base-40); }
li[data-task=">"] { color: var(--color-base-50); }
```

---

## 7. minimal-scrollbar.css

Thin, unobtrusive scrollbar for editor and sidebars.

```css
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--color-base-30); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--color-base-45); }
.nav-files-container::-webkit-scrollbar,
.outline::-webkit-scrollbar { width: 3px; }
```

---

## 8. focus-mode.css

Centers content for distraction-free writing. Activate via `cssclasses: focus`.

```css
.focus .markdown-source-view.mod-cm6 .cm-scroller,
.focus .markdown-reading-view .markdown-preview-sizer {
  max-width: 680px;
  margin: 0 auto;
  padding: 40px 24px;
}
.focus .markdown-source-view { background: var(--color-base-00); }
.focus .markdown-source-view .cm-content { font-size: 1.05em; line-height: 1.8; }
```

**Tip:** pair with Zen mode (Cmd/Ctrl + Shift + Z) for full distraction-free writing.

---

## 9. rainbow-folders.css

Assigns distinct colors to numbered PARA folders (00–15). Each prefix gets its own color using `data-path^=` matching on both the folder title and child file paths.

```css
.nav-folder-title[data-path^="00"], .nav-file-title[data-path^="00"] { color: #94a3b8; }  /* slate */
.nav-folder-title[data-path^="02"], .nav-file-title[data-path^="02"] { color: #4a9eff; }  /* blue */
.nav-folder-title[data-path^="03"], .nav-file-title[data-path^="03"] { color: #52b788; }  /* green */
.nav-folder-title[data-path^="04"], .nav-file-title[data-path^="04"] { color: #9b72cf; }  /* purple */
.nav-folder-title[data-path^="05"], .nav-file-title[data-path^="05"] { color: #e9a84c; }  /* amber */
.nav-folder-title[data-path^="10"], .nav-file-title[data-path^="10"] { color: #fb923c; }  /* orange */
.nav-folder-title[data-path^="15"], .nav-file-title[data-path^="15"] { color: #2dd4bf; }  /* teal */
```

**Note:** Use one of `colored-folders.css` or `rainbow-folders.css` — not both.

---

## 10. callout-icons.css

Custom callout types for Yasmine's Smarterflo workflow. Overrides icon and background color for four business-specific callout types.

```css
/* [!smarterflo] — teal, building icon */
.callout[data-callout="smarterflo"] {
  --callout-color: 172, 65%, 50%;
  --callout-icon: lucide-building-2;
  background-color: rgba(45, 212, 191, 0.1);
  border-left-color: #2dd4bf;
}

/* [!client] — warm orange, users icon */
.callout[data-callout="client"] {
  --callout-color: 24, 93%, 58%;
  --callout-icon: lucide-users;
  background-color: rgba(249, 115, 22, 0.1);
  border-left-color: #f97316;
}

/* [!decision] — purple, check-circle icon */
.callout[data-callout="decision"] {
  --callout-color: 271, 81%, 60%;
  --callout-icon: lucide-check-circle;
  background-color: rgba(168, 85, 247, 0.1);
  border-left-color: #a855f7;
}

/* [!process] — blue, workflow icon */
.callout[data-callout="process"] {
  --callout-color: 217, 91%, 60%;
  --callout-icon: lucide-git-branch;
  background-color: rgba(59, 130, 246, 0.1);
  border-left-color: #3b82f6;
}
```

**Note:** Conflicts with `custom-callouts.css` on `[!client]` and `[!decision]`. Disable one or merge.

---

## 11. dataview-cards.css

Makes all Dataview TABLE results render as cards globally (no cssclass needed). Pairs well with `card-layout.css` if you want opt-in per note instead.

```css
.dataview.table-view-table {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  border: none;
  width: 100%;
}
.dataview.table-view-table thead { display: none; }
.dataview.table-view-table tbody { display: contents; }
.dataview.table-view-table tbody tr {
  display: flex;
  flex-direction: column;
  background: var(--color-base-10);
  border: 1px solid var(--color-base-25);
  border-radius: 8px;
  padding: 12px 14px;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}
.dataview.table-view-table tbody tr:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}
.dataview.table-view-table tbody td {
  border: none;
  padding: 2px 0;
  font-size: 0.875em;
}
.dataview.table-view-table tbody td:first-child {
  font-weight: 600;
  font-size: 0.95em;
  margin-bottom: 4px;
}
```

**Note:** Applies globally. Use `card-layout.css` (snippet 3) with `cssclasses: cards` for per-note opt-in instead. Do not enable both.

---

## 12. tag-pills.css

Renders inline tags as colored pill badges instead of plain `#tag` text.

```css
.tag {
  background-color: var(--color-base-20);
  color: var(--text-muted);
  border: 1px solid var(--color-base-30);
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 0.78em;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  line-height: 1.6;
}
.tag:hover {
  background-color: var(--color-accent);
  color: var(--color-base-00);
  border-color: var(--color-accent);
}

/* Specific tag colors — add your own */
.tag[href="#smarterflo"] { background-color: rgba(45, 212, 191, 0.2); border-color: #2dd4bf; color: #0d9488; }
.tag[href="#client"]     { background-color: rgba(249, 115, 22, 0.15); border-color: #f97316; color: #c2410c; }
.tag[href="#urgent"]     { background-color: rgba(239, 68, 68, 0.15); border-color: #ef4444; color: #b91c1c; }
```

**Theme compatibility:** Works with default theme and Minimal. May conflict with themes that already style `.tag`.

---

## 13. heading-dividers.css

Subtle separator line after H2 only. H1 stays clean for title use; H3+ unchanged.

```css
.markdown-reading-view h2,
.markdown-source-view .cm-header-2 {
  border-bottom: 1px solid var(--color-base-25);
  padding-bottom: 4px;
  margin-bottom: 12px;
}
```

---

## 14. active-line-highlight.css

Subtle background tint on the current cursor line in edit mode. Reading view unaffected.

```css
.cm-editor .cm-activeLine { background-color: var(--color-base-15) !important; border-radius: 3px; }
.cm-editor .cm-activeLineGutter { background-color: var(--color-base-15); }
```

---

## 15. image-zoom.css

Images scale up on hover in reading mode. Reduce to `scale(1.1)` for full-width images.

```css
.markdown-reading-view img {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: zoom-in;
  border-radius: 4px;
}
.markdown-reading-view img:hover {
  transform: scale(1.5);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 100;
}
```

---

## 16. progress-bar.css

Style layer for `[progress:: 0.75]` Dataview inline fields. For reliable rendering, pair with the Meta Bind plugin — pure CSS `attr()` width has limited support in Obsidian's Electron version.

```css
.dataview.inline-field[data-field-key="progress"] .dataview.inline-field-value::before {
  content: '';
  display: block;
  height: 6px;
  width: 100%;
  background: var(--color-base-25);
  border-radius: 999px;
  margin-top: 4px;
}
.dataview.inline-field[data-field-key="progress"] .dataview.inline-field-value::after {
  content: '';
  display: block;
  height: 6px;
  background: var(--color-accent);
  border-radius: 999px;
  margin-top: -6px;
}
```
