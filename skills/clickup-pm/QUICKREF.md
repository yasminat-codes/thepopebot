# ClickUp PM Quick Reference

## Natural Language Commands

### Project Creation
```
"Create client onboarding project for [Client Name]"
"Create niche research for [niche]"
"Create persona research for [role/persona]"
"Create campaign research for [target]"
"Create cold email campaign for [campaign name]"
"Create web app project for [project name]"
"Create offer for [offer name]"
```

### Research (Actually Does It)
```
"Research [niche] niche"
"Do market research on [industry]"
"Research the persona: [role]"
"Do campaign research for [target audience]"
"Research [industry] industry insights"
"Research Skool communities for [topic]"
```

### Task Breakdown
```
"Break down '[task name]'"
"How do I complete '[task name]'?"
"Add subtasks to [task]"
```

### Syncing
```
"Sync ClickUp with Todoist"
"Sync everything"
"What's the sync status?"
```

### Status
```
"ClickUp PM status"
"What projects are active?"
"What's due this week?"
```

---

## Templates (15+)

### Client & Business
- `client_onboarding` - New client workflow
- `offer_creation` - Create service offers
- `sales_process_build` - Design sales process

### Development
- `ai_automation` - AI/automation builds
- `web_app_development` - Full web apps
- `website_build` - Websites/landing pages
- `integration_build` - System integrations

### Marketing
- `cold_email_campaign` - Instantly campaigns
- `linkedin_campaign` - Heyreach campaigns
- `content_strategy` - Content planning
- `seo_audit` - SEO audits

### Research 🔍 (Auto-Research)
- `market_research` - Market analysis
- `niche_research` - Niche deep dive
- `persona_research` - Persona development
- `campaign_research` - Campaign prep
- `industry_insights` - Industry analysis
- `skool_community_research` - Skool research

### Meetings
- `meeting_prep` - Meeting preparation

---

## Research Types

| Type | What It Researches |
|------|-------------------|
| `niche` | Market size, pain points, where they hang out, competitors |
| `persona` | Demographics, challenges, goals, communities, buying process |
| `market` | Market size, trends, key players, segments |
| `industry` | Overview, trends, challenges, opportunities, tech |
| `campaign` | Industry, decision makers, pain points, channels |

---

## Script Commands

```bash
# Main orchestrator
python scripts/orchestrator.py templates                    # List templates
python scripts/orchestrator.py create [template] -c "Client"
python scripts/orchestrator.py research "subject" -t niche
python scripts/orchestrator.py breakdown "task"
python scripts/orchestrator.py sync --all
python scripts/orchestrator.py status

# Direct scripts
python scripts/auto_research.py "dental practices" --type niche
python scripts/break_down_task.py "Build automation"
python scripts/sync_todoist.py --full
python scripts/sync_airtable.py --full
```

---

## Sync Rules

| What | Where | Syncs To |
|------|-------|----------|
| Client projects | ClickUp | Airtable + Todoist |
| Personal tasks | Todoist only | — |
| Research docs | Google Drive | Linked in ClickUp |
| Client data | Airtable (CRM) | — |

---

## Task Breakdown Patterns

The system auto-detects task type:

| Keywords | Type | Subtask Pattern |
|----------|------|-----------------|
| automation, scraper, script | automation | Research → Build → Test → Deploy |
| campaign, email, outreach | campaign | ICP → List → Copy → Launch |
| website, landing page | website | Wireframe → Design → Build → Launch |
| integration, sync, API | integration | Map → Auth → Build → Test |
| research, analyze | research | Define → Gather → Analyze → Report |

---

## ClickUp Schema Quick Reference

**Full Schema:** `~/.config/clickup/schema.json`
**Credentials:** `~/.config/clickup/credentials.json`
**Workspace ID:** 9011535077 | **Member ID:** 114117946

### Key Lists

| List | ID |
|------|------|
| GTD Inbox | 901112408966 |
| Projects List | 901112408969 |
| Cold Outreach | 901112408962 |
| Business360.ai | 901112408965 |
| Agency SOPs | 901112408967 |

### ALWAYS Set These Fields

| Field | Options |
|-------|---------|
| **Project** | Dev & Tech, Sales Process, Business360ai, Cold Outreach, Automation, Client Work, Agency Building... |
| **Context** | Computer, Phone, Errands, Office, Home, Anywhere |
| **Energy** | High, Medium, Low |
| **Time Needed** | 5mins, 15mins, 30mins, 45mins, 1hr, 2hrs, 3hrs+ |

### By Task Type

**Dev/Tech:** Tool/System, Feature/Module, Sprint, Github Url, Plan by Agents
**Sales:** Pipeline Stage, Lead Source, Deal Value, Deliverable Type, Billable?
**SOPs:** SOP Status
**Learning:** Learning Format, Skill Category, Youtube Url
**Personal:** Life Area, Recurring?, Someday/Maybe?
**Nursing:** Shift Type, Location
**Follow-up:** Waiting For, Next Follow-up, Last Follow-up

### Statuses

`backlog` → `planning` → `in progress` → `at risk` → `update required` → `on hold` → `complete` → `cancelled`

### Tags

`computer` | `systems` | `email` | `revenue-direct` | `high-energy` | `deep-work` | `writing` | `medium-energy`

---

## Airtable Integration

**Base:** Smarterflo CRM (`appltifhwH4CpeX6u`)

**Tables:**
- Clients, Projects, Leads
- Campaigns, ICP, Offers
- Tasks, Meetings, Invoices

---

## Research APIs

- **Perplexity** - AI-synthesized answers
- **Brave Search** - Web results
- **Exa** - Neural/semantic search

Research outputs saved to: `/home/clawdbot/clawd/research_output/`
