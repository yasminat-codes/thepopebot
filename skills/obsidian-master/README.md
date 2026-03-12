# obsidian-master

Complete Obsidian expert for Yasmine Seidu. Replaces obsidian v1.0.0 — all capabilities merged and superseded.

## Two Modes

**Vault Operator** — reads, writes, organizes, and scaffolds vault content directly via REST API, CLI, or file operations.

**Obsidian Expert** — answers questions, designs systems, recommends plugins, advises on structure and workflows.

Both modes share the same protocol: interview before acting, plan before executing.

## How to Invoke

Auto-triggers when you say: "obsidian", "vault", "note", "dataview", "template", "daily note", "MOC", "save to vault", "add to obsidian", "vault structure", "PARA", "backlink", or "Yasmine-OS".

Direct invocation: `/obsidian-master [action or topic]`

## Primary Vaults

| Vault | Purpose |
|-------|---------|
| Yasmine-OS | Personal OS vault — daily life, learning, personal projects. Being built from scratch. |
| Smarterflo | Business vault — clients, content, brand, LinkedIn, processes. Fully operational. |

6 vaults total. When vault is ambiguous, it always asks.

## What It Can Do

- Create and scaffold PARA folder structures from scratch
- Build Templater templates (Daily Note, Weekly Review, Meeting Note, Client Profile, etc.)
- Write Dataview and Dataview JS queries
- Create notes, MOCs, and linked note networks
- Read from and write to the vault via REST API (port 27123) or direct file operations
- Set up Periodic Notes (daily, weekly, monthly)
- Generate CSS snippets for theming
- Build plugin configurations (Tasks, Calendar, Templater, etc.)
- Route content to the correct vault folder based on PARA structure
- Save research, decisions, and AI output to the right location
- Run the 7 standard workflows (morning routine, capture, research, client work, content, weekly review, AI → vault)

## What It Cannot Do

- Publish content to external platforms directly (it routes to the right tool for that)
- Manage academic citation systems (Zotero, etc.)
- Develop custom Obsidian plugins (JavaScript plugin code)
- Sync or back up vaults to external services

## Skill Integrations

| Skill | When obsidian-master calls it |
|-------|-------------------------------|
| google-workspace | Long docs created in Obsidian that need external sharing |
| de-ai-fy | Any vault content going to LinkedIn, email, or clients — mandatory |
| densify | Long vault notes (>60 lines) being fed into LLM pipelines |
| task-master | Extracting action items from notes into the task system |

All integrations are offered explicitly before triggering — never silent.
