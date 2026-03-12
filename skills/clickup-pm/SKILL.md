---
name: clickup-pm
description: >-
  Manage ClickUp tasks, spaces, lists, and projects via API. Use PROACTIVELY when
  user says "clickup", "create task in clickup", "clickup project", "task board",
  "clickup list", "update clickup", "clickup status", "clickup workspace", "break
  down project", or "project management". Use when organizing work, tracking tasks,
  or creating project documentation in ClickUp. Requires CLICKUP_TOKEN env var.
allowed-tools: Read Write Edit Bash Task
argument-hint: "[task-or-project] (optional)"
disable-model-invocation: false
user-invocable: true
model: sonnet
license: Proprietary
metadata:
  author: yasmine-seidu
  version: "1.0.0"
  category: project-management
---

# ClickUp Project Manager

Your AI project manager that handles ClickUp for business/client work while keeping personal stuff in Todoist.

## Philosophy

- **ClickUp** = Business & client projects (billable, client-facing)
- **Todoist** = Personal tasks, habits, learning
- **Airtable** = Smarterflo CRM (Clients, Projects, Leads, Campaigns, ICP, Offers)
- **Google Drive** = Documentation, SOPs, research deliverables

---

## Core Capabilities

### 1. Smart Project Creation
Creates full project structures from 15+ templates with:
- Phases, tasks, subtasks with descriptions
- Time estimates and priorities
- Automatic research for research-type projects
- Google Doc creation for documentation tasks

### 2. Automated Research
For research templates, ACTUALLY DOES THE RESEARCH using:
- **Perplexity** - AI-synthesized answers with citations
- **Brave Search** - Web search results
- **Exa** - Neural search for deep context

Creates research documents automatically for:
- Market research
- Niche research
- Persona research
- Campaign research
- Industry insights
- Skool community research

### 3. Bi-Directional Sync

**ClickUp ↔ Todoist:**
- Business tasks sync to Todoist with `@clickup` label
- Completions sync both ways
- Personal tasks stay ONLY in Todoist

**ClickUp ↔ Airtable (Smarterflo CRM):**
- Clients → ClickUp Folders
- Projects → ClickUp Lists
- Status updates sync both ways
- Time tracked → Airtable hours

### 4. Task Breakdown
AI-powered breakdown that detects task type and generates:
- Intelligent subtasks
- Time estimates
- Priorities
- Step-by-step guidance

---

## Available Templates (15+)

### Client & Business
| Template | Use Case |
|----------|----------|
| `client_onboarding` | New client setup workflow |
| `offer_creation` | Create compelling service offers |
| `sales_process_build` | Design sales process |

### Development
| Template | Use Case |
|----------|----------|
| `ai_automation` | Build AI/automation projects |
| `web_app_development` | Full web application |
| `website_build` | Website/landing page |
| `integration_build` | System integrations |

### Marketing & Outreach
| Template | Use Case |
|----------|----------|
| `cold_email_campaign` | Cold email via Instantly |
| `linkedin_campaign` | LinkedIn via Heyreach |
| `content_strategy` | Content strategy development |
| `seo_audit` | Technical SEO audit |

### Research (Auto-Research Enabled) 🔍
| Template | Use Case |
|----------|----------|
| `market_research` | Comprehensive market analysis |
| `niche_research` | Deep dive into a niche |
| `persona_research` | Customer persona development |
| `campaign_research` | Full campaign research |
| `industry_insights` | Industry analysis report |
| `skool_community_research` | Skool community analysis |

### Meetings
| Template | Use Case |
|----------|----------|
| `meeting_prep` | Prepare for important meetings |

---

## Usage

### Natural Language Commands (via Lena)

**Project Creation:**
```
"Create client onboarding project for Acme Corp"
"Create niche research project for dental practices"
"Create cold email campaign for Q1 SaaS outreach"
"Create persona research for VP of Marketing"
```

**Research:**
```
"Research the dental industry"
"Do niche research on AI automation agencies"
"Research the persona: VP of Sales at mid-market SaaS"
"Do campaign research for targeting healthcare IT"
```

**Task Breakdown:**
```
"Break down 'Build lead scraping automation'"
"How do I complete 'Set up Instantly campaign'?"
```

**Syncing:**
```
"Sync ClickUp with Todoist"
"Sync everything"
"What's out of sync?"
```

### Direct Script Usage

```bash
# List all templates
python scripts/orchestrator.py templates

# Create project
python scripts/orchestrator.py create client_onboarding --client "Acme Corp"
python scripts/orchestrator.py create niche_research --name "Dental Practices"

# Run research directly
python scripts/auto_research.py "dental practices" --type niche
python scripts/auto_research.py "VP of Marketing" --type persona
python scripts/auto_research.py "AI automation" --type market

# Break down tasks
python scripts/break_down_task.py "Build lead scraping automation"
python scripts/break_down_task.py "Set up cold email campaign" --create --list-id 12345

# Sync
python scripts/orchestrator.py sync --all
python scripts/sync_todoist.py --full
python scripts/sync_airtable.py --full

# Status
python scripts/orchestrator.py status
```

---

## Research Types

### Niche Research
Researches a specific niche/vertical:
- Market viability & size
- Common pain points
- Where they hang out online
- Competitors serving them
- Budget & buying behavior

### Persona Research
Deep customer persona development:
- Demographics & psychographics
- Pain points & goals
- Information sources
- Communities & networks
- Buying process

### Market Research
Comprehensive market analysis:
- Market size & growth
- Key players & competition
- Customer segments
- Trends & outlook

### Campaign Research
Full research for launching a campaign:
- Industry deep dive
- Decision maker profiles
- Pain points & aspirations
- Channels & communities
- Messaging angles

### Industry Insights
Industry analysis report:
- Overview & landscape
- Trends & technology
- Challenges & opportunities
- SWOT analysis

---

## Sync Rules

### What Goes Where

| Item | Primary | Syncs To |
|------|---------|----------|
| Client projects | ClickUp | Airtable (status), Todoist (milestones) |
| Personal tasks | Todoist only | — |
| Client/lead info | Airtable | — |
| Research docs | Google Drive | Linked in ClickUp |
| Time entries | ClickUp | Airtable (hours) |

### Airtable Integration (Smarterflo CRM)

**Base ID:** `appltifhwH4CpeX6u`

**Tables Used:**
- `Clients` - Client records
- `Projects` - Project tracking
- `Leads` - Lead management
- `Campaigns` - Campaign tracking
- `ICP` - Ideal Customer Profiles
- `Offers` - Offer library

---

## Configuration

**Credentials:** `~/.config/clickup/credentials.json`
**Full Schema:** `~/.config/clickup/schema.json`

```json
{
  "airtable_base_id": "appltifhwH4CpeX6u",
  "airtable_base_name": "Smarterflo CRM",
  "clickup_workspace_id": "9011535077",
  "clickup_member_id": "114117946",
  "todoist_sync": {
    "enabled": true,
    "project_name": "BUSINESS",
    "label": "clickup"
  }
}
```

---

## ClickUp Workspace Schema (MANDATORY REFERENCE)

**ALWAYS load `~/.config/clickup/schema.json` before creating tasks/projects.**

### Workspace Structure

| Space | ID | Purpose |
|-------|------|---------|
| GTD System | 90113987079 | Personal GTD workflow |
| Tasks Hub | 90113851264 | General tasks, client projects |
| Automation Builds | 90112316591 | Internal/client automations |
| SmarterFlo | 90113797722 | Agency operations |
| Strategy & Foundation | 90113858681 | Business strategy |

### Key Lists (use these IDs)

| List | ID | Use For |
|------|------|---------|
| GTD Inbox | 901112408966 | Quick capture |
| Projects List | 901112408969 | Active projects |
| Next Actions | 901112408968 | GTD next actions |
| Waiting For | 901112408970 | Blocked/waiting |
| Someday/Maybe | 901112408971 | Future ideas |
| Cold Outreach Pipeline | 901112408962 | Sales pipeline |
| Client Delivery | 901112408963 | Active client work |
| Sales Conversations | 901112408964 | Sales tracking |
| Business360.ai | 901112408965 | Business360 project |
| Agency SOPs | 901112408967 | SOPs & processes |
| Internal Builds | 901106769732 | Internal automation |

### Statuses (GTD lists)

`backlog` → `planning` → `in progress` → `at risk` → `update required` → `on hold` → `complete` → `cancelled`

### Tags (use for filtering)

`computer` | `systems` | `email` | `revenue-direct` | `high-energy` | `deep-work` | `writing` | `medium-energy` | `trainings`

### Priorities

| Value | Meaning |
|-------|---------|
| 1 | Urgent (red) |
| 2 | High (yellow) |
| 3 | Normal (blue) |
| 4 | Low (gray) |
| null | No priority |

---

## Custom Fields (ALWAYS POPULATE RELEVANT FIELDS)

When creating tasks, **think through which fields apply** and set them:

### Core Task Fields

| Field | ID | When to Use |
|-------|------|-------------|
| **Project** | 76a1b1f8-20aa-4a57-9adb-4c21a3db9081 | ALWAYS - categorize the work |
| **Context** | 905580f1-b437-4aa4-bfe0-96ee7b2fc55c | ALWAYS - where can this be done |
| **Energy Levels** | b9be72e1-1d61-4317-ae04-4c05e2a4d5c7 | ALWAYS - High/Medium/Low energy needed |
| **Time Needed** | 5a67015a-febb-40da-a183-51b0298e8ec3 | ALWAYS - estimate duration |

### Project Field Options
`Dev & Tech` | `Sales Process` | `Business360ai` | `Nursing` | `Personal Tasks` | `Dev Work` | `Learning` | `Personal Development` | `Agency SOPs` | `Cold Outreach` | `Automation` | `Client Work` | `Agency Building` | `Ollie-ai` | `Ollie Sales`

### Context Options
`Computer` | `Phone` | `Errands` | `Office` | `Home` | `Home Office` | `Anywhere`

### Time Needed Options
`5mins` | `15mins` | `30mins` | `45mins` | `1hr` | `1h 30mins` | `2hrs` | `3hrs+`

### Development/Tech Tasks

| Field | ID | When to Use |
|-------|------|-------------|
| **Tool/System** | 2ba40766-1ea6-4f20-8650-658e33d30f4e | Any tech task - which tool |
| **Feature/Module** | 8e3b878c-ebd3-435b-ae24-f235e20d997b | Dev work - which module |
| **Sprint** | 3b95b7ac-a738-423d-8d41-dcc18ea9fa87 | Sprint planning |
| **Story Points** | db760f23-48ff-46e1-a147-9fc1a40940ba | Agile estimation |
| **Github Url** | 262f1c80-febd-4e93-aae4-939d653ce945 | Link to repo/PR |
| **Plan by Agents** | 45b83c71-c97a-4f5d-a7e1-ad775924e709 | AI planning type needed |

### Tool/System Options
`n8n` | `ClickUp` | `GoHighLevel` | `Notion` | `Airtable` | `Google Suite` | `Deformity` | `PandaDoc` | `Claude Code` | `Claude`

### Feature/Module Options
`Research` | `Planning` | `Backlog` | `Backend Planning` | `Dashboard` | `User Management` | `Analytics` | `API Integration` | `UI/UX` | `Backend` | `Database`

### Sales/Client Tasks

| Field | ID | When to Use |
|-------|------|-------------|
| **Pipeline Stage** | 3b5fa1f7-3c33-4069-8c78-77fefcc1e7a7 | Lead/client status |
| **Lead Source** | c2caf70a-9edf-4a55-9428-78923e002498 | Where lead came from |
| **Deal Value** | 75834c7e-3b09-4b5b-ac46-28fb73c04645 | $ value |
| **Client/Prospect Name** | e4b9c30e-5496-4216-a45e-e790d451c6cc | Who |
| **Deliverable Type** | 80ad7910-026a-45a6-930b-418e2816d307 | What we're delivering |
| **Billable?** | 52f1d62b-91f9-4be3-a82d-1dc1d8722c98 | Is this billable |
| **Revenue Generating?** | 9642b90c-0ee9-40d9-88f2-f087e1b6879f | Direct revenue impact |

### Pipeline Stage Options
`Lead` → `Prospect` → `Qualified` → `In Discussion` → `Meeting Booked` → `Meeting Completed` → `Proposal Sent` → `Negotiating` → `Won` | `Lost` | `Project Started`

### Lead Source Options
`Linkedin` | `Cold Email` | `Referral` | `Skool` | `Website` | `Facebook` | `Youtube` | `Other`

### Deliverable Type Options
`Automation` | `Strategy Call` | `Monthly Retainer` | `One-off Project` | `Consulting` | `Web App` | `Desktop App` | `Mobile App` | `Website`

### Follow-up & Waiting

| Field | ID | When to Use |
|-------|------|-------------|
| **Waiting For** | bbe8b28a-e7f9-459d-9afb-75cda9f6fd1a | Who/what are we waiting on |
| **Next Follow-up** | 0d305c30-d629-4b73-8d4b-12d4a442078b | When to follow up |
| **Last Follow-up** | 5188f6ea-256c-4567-81db-abba9ccbc6a8 | When we last reached out |

### SOPs & Documentation

| Field | ID | When to Use |
|-------|------|-------------|
| **SOP Status** | 09b2e45b-39df-4733-aaa4-17f99f90382a | SOP creation tasks |

### SOP Status Options
`Needs Creating` | `In Progress` | `Drafted` | `Under review` | `Finalized` | `Need Updating`

### Learning Tasks

| Field | ID | When to Use |
|-------|------|-------------|
| **Learning Format** | dbc78342-b670-48c8-bcbf-e94d51a0734d | Learning tasks |
| **Skill Category** | bcbf0d37-5bfe-4eee-b3ad-2a70b5f561a3 | What skill area |
| **Youtube Url** | e12b3867-544c-4ec4-948e-27fe3520d8a3 | Video link |

### Learning Format Options
`Course` | `Book` | `Video` | `Coding` | `Practice Project` | `Mentorship` | `Workshop` | `Youtube`

### Skill Category Options
`Technical` | `Business` | `Marketing` | `Sales` | `Personal Growth` | `Leadership`

### Personal/Life Tasks

| Field | ID | When to Use |
|-------|------|-------------|
| **Life Area** | e59bbce3-be83-4aad-9c4b-12e97798ce6b | Personal tasks |
| **Recurring?** | a9abd0e1-9c64-46c2-8d1d-b9d64a31b05e | Repeating tasks |
| **Someday/Maybe?** | af58e005-3e50-46c0-ab98-659f28a9ff73 | Future ideas |

### Life Area Options
`Health` | `Family` | `Home` | `Finance` | `Social` | `Recreation` | `Work`

### Nursing Tasks

| Field | ID | When to Use |
|-------|------|-------------|
| **Shift Type** | cb95e2ab-6732-48b9-a963-b5c0bb51bb3d | Nursing shifts |
| **Location** | 4fcfc97b-1640-4f79-aab5-7d629123c0e5 | Where |

### Shift Type Options
`Day Shift` | `Night Shift` | `Training` | `Meeting` | `On-Call`

### Meetings

| Field | ID | When to Use |
|-------|------|-------------|
| **Prep Completed?** | 0aa52d81-e67c-469f-9521-b103336ea3f5 | Meeting prep tasks |

---

## Task Creation Checklist

Before creating ANY task, think through:

1. **Which list?** → Use appropriate list ID
2. **Status?** → Usually start at `backlog` or `planning`
3. **Priority?** → 1-4 based on urgency
4. **Project field?** → ALWAYS set this
5. **Context?** → Where can this be done
6. **Energy Level?** → High/Medium/Low
7. **Time Needed?** → Estimate duration
8. **Tags?** → Add relevant tags
9. **Custom fields?** → Based on task type (dev, sales, learning, etc.)
10. **Due date?** → If time-sensitive
11. **Assignee?** → 114117946 (Yasmine)

---

## Setup Checklist

- [x] Airtable configured (Smarterflo CRM)
- [x] ClickUp credentials configured (`~/.config/clickup/credentials.json`)
- [x] ClickUp schema captured (`~/.config/clickup/schema.json`)
- [x] Todoist configured
- [x] Perplexity API configured
- [x] Brave Search API configured
- [x] Exa API configured
- [ ] Google Drive folder IDs configured
- [ ] Create `@clickup` label in Todoist

---

## Smart Task System (NEW)

### 1. Smart Task Creation
Auto-detects task type and applies relevant fields:

```bash
# Analyze what fields would be applied (dry run)
python3 scripts/smart_task_create.py "Build lead scraping automation" --analyze

# Create task with auto-fields
python3 scripts/smart_task_create.py "Build lead scraping automation"

# Override list if needed
python3 scripts/smart_task_create.py "Call mom" --list personal
```

**Detection Patterns:**
| Keywords | Type | List | Fields Applied |
|----------|------|------|----------------|
| build, code, api, deploy | dev | internal_builds | tool_system, feature_module |
| business360, agent, niche | business360 | business360ai | feature_module, sprint |
| lead, outreach, campaign | sales | cold_outreach | pipeline_stage, lead_source |
| sop, document, process | sop | agency_sops | sop_status |
| learn, course, watch, skool | learning | someday_maybe | learning_format, skill_category |
| call, family, errand | personal | inbox | life_area |

### 2. Inbox Processor (Daily Cron)
Runs at 6:30 AM EST daily - analyzes GTD Inbox and suggests categorization:

```bash
# Generate triage report
python3 scripts/inbox_processor.py --report

# See what would be organized (dry run)
python3 scripts/inbox_processor.py --organize --dry-run

# Actually organize tasks
python3 scripts/inbox_processor.py --organize
```

**Cron ID:** `96ae2cb0-5e5c-493a-bb1f-eed0105e50dc`

### 3. Natural Language Queries
Ask about your tasks naturally:

```bash
python3 scripts/task_queries.py "what's on my plate today"
python3 scripts/task_queries.py "what's blocking"
python3 scripts/task_queries.py "quick wins"
python3 scripts/task_queries.py "deep work"
python3 scripts/task_queries.py "revenue tasks"
python3 scripts/task_queries.py "overdue"
python3 scripts/task_queries.py "this week"
python3 scripts/task_queries.py "stale tasks"
```

**Via Lena:**
- "What's on my plate today?" → Today's tasks + overdue
- "What's blocking?" → Waiting For items
- "Quick wins" → Low energy / short duration
- "Revenue tasks" → Sales pipeline + billable
- "What's stale?" → Planning 7+ days, no updates 14+ days

---

## File Structure

```
skills/clickup-pm/
├── SKILL.md                    # This file
├── QUICKREF.md                 # Quick reference
├── config.json                 # Configuration
├── scripts/
│   ├── orchestrator.py         # Main entry point
│   ├── create_project.py       # Project creation
│   ├── break_down_task.py      # Task breakdown
│   ├── auto_research.py        # Automated research
│   ├── smart_task_create.py    # NEW: Smart task creation with auto-fields
│   ├── inbox_processor.py      # NEW: Inbox triage and auto-organize
│   ├── task_queries.py         # NEW: Natural language task queries
│   ├── sync_todoist.py         # Todoist sync
│   └── sync_airtable.py        # Airtable sync
└── templates/
    └── projects.json           # All project templates
```

---

## Next Steps to Complete Setup

1. **ClickUp Token** - Provide your ClickUp API token
2. **ClickUp Workspace** - Share your workspace structure
3. **Google Drive Folders** - Set up research output folder
4. **Todoist Label** - Create `@clickup` label if not exists
