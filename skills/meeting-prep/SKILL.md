---
name: meeting-prep
description: >-
  Automatically prepare for discovery calls with research, slides, and talking points.
  Use PROACTIVELY when user says "prep for meeting", "meeting prep", "discovery call",
  "prepare for call", "research this lead", "call prep", "upcoming meeting", "meeting
  tomorrow", "who am I meeting", or when a calendar event with "discovery" appears.
  Researches lead, company, recent news, LinkedIn posts, and creates agenda.
allowed-tools: Read Write Edit Bash Task WebSearch WebFetch
argument-hint: "[lead-name-or-company] (optional)"
disable-model-invocation: false
user-invocable: true
model: sonnet
license: Proprietary
metadata:
  author: yasmine-seidu
  version: "1.0.0"
  category: productivity
---

# Meeting Prep Automation 🎯
<!-- ultrathink -->

Automatically prepare for discovery calls with comprehensive research, slides, and talking points.

## What It Does

When a discovery call is booked on your calendar (with "discovery call" in the title), this skill automatically:

1. **🚀 Autobound Intelligence** (NEW!)
   - Real-time contact & company insights
   - Recent news & announcements
   - Hiring signals & growth trends
   - Tech stack & tools they use
   - LinkedIn activity & engagement
   - Funding rounds & investments
   - 350+ signal types monitored

2. **Researches the Lead**
   - Background & expertise
   - Current role & responsibilities
   - LinkedIn activity & posts
   - Twitter/X presence

3. **Researches the Company**
   - Company overview & business model
   - Recent news & achievements
   - Funding & leadership
   - Industry context & trends

4. **Creates Dedicated Folder** (Google Drive)
   - One folder per discovery call
   - All materials organized together
   - Format: "Discovery - Lead Name @ Company"

5. **Intelligence Doc** (Google Doc - using google-workspace skill)
   - Autobound real-time intelligence
   - Company overview & recent news
   - Lead background & social activity
   - Hiring signals & tech stack
   - Industry insights
   - **For your reference** (not shown to client)

6. **Talking Points Doc** (Google Doc - using google-workspace skill)
   - Personalized icebreakers
   - 50-minute meeting agenda
   - Key questions to ask
   - Talking points by category
   - Objection handling
   - Next steps template
   - **For your reference** (not shown to client)

7. **Client-Facing Presentation** (Gamma slides)
   - **What you screen-share DURING the call**
   - Professional 10-slide deck:
     - Welcome & agenda
     - About Smarterflo
     - What we learned about them
     - Common challenges we solve
     - Our approach
     - Success stories
     - Questions for them
     - Next steps
   - Shows you did your homework
   - Guides the conversation professionally

## Quick Start

### Manual Trigger
```bash
uv run scripts/meeting_prep_orchestrator.py "John Smith" "Acme Corp"
```

### With Meeting Date
```bash
uv run scripts/meeting_prep_orchestrator.py "Sarah Johnson" "TechStart Inc" --date "2026-01-20"
```

## What Gets Created

### 📂 Dedicated Folder
**Format:** `Discovery - Lead Name @ Company`
- One folder per discovery call in Google Drive
- All materials organized together
- Easy to find everything
- Room to add call transcript later

### 📄 Intelligence Doc (Your Reference - NOT for client)
**Google Doc created using google-workspace skill**

Contains all your research:
- 🚀 **Autobound Intelligence** - Real-time signals & insights
- 📊 **Company Overview** - Business model, industry, size
- 📰 **Recent News** - Latest announcements with sources
- 👤 **Lead Background** - Role, expertise, experience
- 💼 **LinkedIn Activity** - Recent posts & engagement
- 💻 **Tech Stack** - Tools they use
- 💰 **Funding Signals** - Investment activity
- 🏭 **Industry Context** - Trends and opportunities

**Use:** Open during the call for quick reference

### 💬 Talking Points Doc (Your Reference - NOT for client)
**Google Doc created using google-workspace skill**

Your complete call guide:
- ❄️ **Icebreakers** - Personalized from real data
- 📋 **Meeting Agenda** - 50-min structured flow
- ❓ **Key Questions** - What to ask them
- 💬 **Talking Points** - Organized by category
- 🛡️ **Objection Handling** - Common objections + responses
- ✅ **Next Steps** - Follow-up template

**Use:** Review before call, have open as your script

### 🎨 Client-Facing Presentation (Screen-share DURING call)
**Gamma slides - what the client sees**

Professional 10-slide deck:
1. **Welcome** - Thank them, set expectations
2. **About Smarterflo** - Who we are, what we do
3. **Today's Agenda** - Clear structure
4. **What We Learned** - Show you did homework
5. **Common Challenges** - Relatable pain points
6. **Our Approach** - How we work (discovery → pilot → scale)
7. **Success Stories** - Social proof
8. **Questions for You** - Make it collaborative
9. **Next Steps** - Clear follow-up path
10. **Let's Talk!** - Open conversation

**Use:** Screen-share this during the discovery call. Guides the conversation professionally while showing them you're prepared.

### 📅 Calendar Event
All links added to your calendar event:
- Link to folder
- Link to intelligence doc
- Link to talking points doc
- Link to Gamma presentation
- Quick prep checklist
- After-call reminders

## Research Sources

**🚀 Autobound Intelligence (Primary):**
- 250M+ contacts monitored
- 50M+ companies tracked
- 350+ signal types:
  - SEC filings (10-K, 10-Q, 8-K)
  - Hiring trends & job postings
  - Tech stack changes
  - Funding rounds & investments
  - LinkedIn & Twitter activity
  - News & announcements
  - Product launches
  - Customer reviews
  - Competitor moves
  - GitHub activity
  - Website changes
  - And much more!

**Traditional Research (Backup):**
- Perplexity AI - Comprehensive overviews
- SERP API - News articles & press
- Tavily - Industry insights
- LinkedIn search - Profile & posts
- Twitter/X search - Recent activity
- Company website - Latest announcements

## Auto-Trigger (ACTIVE!)

**✅ Now running every 30 minutes!**

The skill automatically watches your calendar and preps discovery calls.

**How it works:**
1. Cron job runs every 30 minutes
2. Scans calendar for events with "discovery call" in title
3. Checks if already prepped (avoids duplicates)
4. Extracts lead email & company from attendees
5. Runs Autobound intelligence + traditional research
6. Creates beautiful Google Doc report
7. Adds report link to calendar event
8. Tracks prep history to avoid re-doing

**Setup auto-trigger:**
```bash
cd /home/clawdbot/clawd/skills/meeting-prep
bash install_cron.sh
```

**Test manually:**
```bash
# Dry run (see what would be prepped)
uv run scripts/auto_trigger.py --dry-run

# Actually run it
uv run scripts/auto_trigger.py

# Reset history (re-prep all meetings)
uv run scripts/auto_trigger.py --reset-history
```

**View logs:**
```bash
tail -f logs/auto_trigger.log
```

## Example Output

```
=================================================================================
🎯 MEETING PREP: Sarah Johnson @ TechStart Inc
=================================================================================

📚 PHASE 1: RESEARCH
   📊 Company overview...
   📰 Recent news...
   👤 Lead background...
   💼 LinkedIn presence...
   🐦 X/Twitter activity...
   🏭 Industry context...

📄 PHASE 2: CREATE REPORT
   ✅ Report created: https://docs.google.com/document/d/...

🎨 PHASE 3: CREATE PRESENTATION
   ✅ Gamma slides ready

📋 PHASE 4: CREATE AGENDA
   ✅ 50-minute agenda created

💬 PHASE 5: CREATE TALKING POINTS
   ✅ 4 categories of talking points

📧 PHASE 6: SEND SUMMARY
   ✅ Summary email ready

=================================================================================
✅ MEETING PREP COMPLETE!
=================================================================================
```

## Files

```
meeting-prep/
├── SKILL.md (this file)
├── scripts/
│   ├── meeting_prep_orchestrator.py (main orchestrator)
│   ├── autobound_client.py (Autobound API integration)
│   ├── auto_trigger.py (calendar watcher - auto-preps discovery calls)
│   ├── lead_researcher.py (traditional research engine)
│   ├── calendar_integration.py (Google Calendar integration)
│   └── api_client.py (generic API helper)
├── config/
│   └── prep_history.json (track prepped meetings)
├── logs/
│   └── auto_trigger.log (auto-trigger activity log)
├── install_cron.sh (setup auto-trigger cron job)
└── test_autobound.sh (test Autobound integration)
```

## API Keys Required

```bash
# Required for Autobound intelligence (HIGHLY RECOMMENDED!)
export AUTOBOUND_API_KEY="your-autobound-key"  # Get at app2.autobound.ai/settings/api-keys

# Optional - for additional research
export SERP_API_KEY="your-serpapi-key"
export TAVILY_API_KEY="your-tavily-key"
export PERPLEXITY_API_KEY="your-perplexity-key"

# Future
# export GAMMA_API_KEY="your-gamma-key" (coming soon)
```

**Get Autobound API Key:**
1. Go to https://app2.autobound.ai/settings/api-keys
2. Create account (includes free credits)
3. Generate API key
4. Add to your environment

**Test Autobound:**
```bash
cd /home/clawdbot/clawd/skills/meeting-prep
./test_autobound.sh [email protected] example.com
```

## Use Cases

**Sales Discovery Calls:**
- Research prospect before first call
- Understand their business & challenges
- Prepare relevant talking points

**Partnership Meetings:**
- Learn about potential partner
- Find mutual interests
- Identify collaboration opportunities

**Investor Pitches:**
- Research investor background
- Understand their portfolio
- Tailor pitch to interests

**Job Interviews:**
- Research company culture
- Learn about interviewer
- Prepare intelligent questions

## How to Use During the Call

### Before the Call (10 min prep)
1. **Review Talking Points Doc** - Read icebreakers, questions, objections
2. **Open Intelligence Doc** - Have it ready for quick reference
3. **Load Gamma Presentation** - Ready to screen-share
4. **Test your setup** - Camera, mic, screen-share working

### During the Call
1. **Screen-share Gamma Presentation** - Client sees this
2. **Keep Talking Points Doc open** (not shared) - Your script
3. **Reference Intelligence Doc** (not shared) - For specific details
4. **Follow the Gamma slides** - Natural conversation flow
5. **Take notes in Talking Points Doc** - Capture key points

### Setup Recommendation
- **Main monitor:** Gamma presentation (screen-share)
- **Second monitor/window:** Talking Points Doc (your eyes only)
- **Background tab:** Intelligence Doc (quick reference)

### After the Call
1. **Add call transcript** to the folder
2. **Update Talking Points Doc** with notes
3. **Schedule follow-up** from Next Steps section
4. **Send personalized proposal** within 48 hours

## Pro Tips

1. **Run 24h before meeting** - Get freshest Autobound signals
2. **Customize Gamma slides** - Add their logo if you have it
3. **Reference recent news** - Use icebreakers from talking points
4. **Let them talk 70%** - You listen, ask questions
5. **Share Gamma after** - Send presentation link as follow-up

## Future Enhancements

- [ ] Automatic calendar triggering
- [ ] Gamma API integration for auto-slides
- [ ] CRM integration (add notes to GoHighLevel)
- [ ] Email follow-up templates
- [ ] Meeting recording analysis
- [ ] Post-meeting summary generator

---

**Built with Skill Builder** - Never go into a meeting unprepared again! 🎯

Version 1.0 - Research, report, slides, agenda, and talking points automated!
