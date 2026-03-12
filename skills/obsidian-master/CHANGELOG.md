# Changelog

## v1.1.0 — 2026-03-08

### Added

- **ANTI-ORPHAN.md** — Zero-orphan protocol: three-layer defense (Templater prevention + Automatic Linker auto-linking + Dataview detection), mandatory link rule, weekly audit queries, graph view orphan monitoring
- **TEMPLATER-SCRIPTS.md** — Complete user script library: auto-linker, tag-picker, folder-router, moc-linker, date-range, status-picker scripts with setup instructions and invocation patterns
- **TEMPLATES.md enhanced** — Full Templater function reference (tp.file, tp.date, tp.system, tp.frontmatter, tp.hooks, tp.user) with complete signature tables, Moment.js format token reference, auto-linking and auto-tagging patterns, QuickAdd integration
- **TEMPLATES-EXAMPLES.md enhanced** — All 4 templates (Daily Note, Meeting, Client Profile, Project) now include auto-linking via parent note selection, auto-folder routing via tp.file.move(), MOC links, anti-orphan compliance
- **TEMPLATES-EXAMPLES-2.md enhanced** — All 4 templates (Research, Decision Log, Weekly Review, Content Idea) now include auto-linking, anti-orphan compliance, and embedded orphan detection Dataview query in Weekly Review
- **CSS-SNIPPETS.md expanded** — Added snippets: rainbow-folders (PARA color coding), dataview-cards, callout-icons (Smarterflo-specific: smarterflo/client/decision/process callout types), tag-pills, additional customizations
- Two new Capability Map entries: Templater scripts, Anti-orphan protocol
- Two new Expert Principles: zero orphan tolerance, Templater scripts over inline code
- Updated trigger keywords: orphaned note, auto-link, auto-tag, user script, Automatic Linker, frontmatter automation, vault health

### Changed

- SKILL.md version: 1.0.0 → 1.1.0
- References table: 26 → 28 files

---

## v1.0.0 — 2026-03-08

### Added

- Dual-mode operation: Vault Operator (read/write/scaffold vault content) and Obsidian Expert (advisory and design)
- Consultant-first interview protocol — always interviews before executing, always plans before writing
- Multi-vault support: Yasmine-OS, Smarterflo, and any additional vault via path detection
- Vault detection logic with memory persistence — skips repeated "which vault?" questions
- PARA folder scaffolding with 00-06 numbering system for any vault
- Templater template creation: Daily Note, Weekly Review, Meeting Note, Client Profile, Content Idea, and custom
- Dataview and Dataview JS query generation (simple queries, complex JS blocks, MOC-style dashboards)
- Periodic Notes setup (daily, weekly, monthly) with Templater integration
- Local REST API integration (Obsidian REST API plugin, port 27123) — primary execution path
- obsidian-cli fallback execution path
- Direct file operation fallback (Read/Write/Edit tools)
- 7 end-to-end workflows: morning routine, capture → process → file, research, client work, content creation, weekly review, AI output → vault
- Session memory persistence: vault preference, confirmed paths, templates built, plugin preferences, CSS snippets
- CSS snippet generation for vault theming (custom fonts, header styles, callout styles)
- Plugin configuration guidance for all installed plugins (Tasks, Calendar, Templater, Dataview, etc.)
- Destructive operation safeguards: two-step confirmation required for any delete or mass rename
- Scope explosion protection: clarifies scope before any "reorganize" or "restructure" request
- 4 skill integrations: google-workspace (Google Doc export), de-ai-fy (mandatory for external content), densify (LLM optimization), task-master (action item extraction)
- 25 reference files with progressive disclosure — SKILL.md loads references on demand, not upfront
- 5 pressure test scenarios in TESTING.md for skill validation

### Replaces

- obsidian v1.0.0 — merged and superseded. All capabilities carried forward.

### Architecture

- Tier 6 Orchestrator
- 25 reference files with progressive disclosure
- REST API + obsidian-cli dual execution paths
- Consultant-first interview protocol
- Multi-vault support (Yasmine-OS + Smarterflo + any vault)
- Memory persistence across sessions via MEMORY.md
- 4 skill integrations: google-workspace, de-ai-fy, densify, task-master
