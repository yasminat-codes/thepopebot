# Quick Start - Meeting Prep

## 🎯 What This Does

Automatically prepares you for discovery calls with **3 things:**

1. **📄 Intelligence Doc** - All research (your reference, NOT for client)
2. **💬 Talking Points Doc** - Your call script (your reference, NOT for client)  
3. **🎨 Gamma Presentation** - Professional slides (CLIENT SEES THIS during call)

## ⚡ Setup (5 minutes)

### 1. Get API Keys

**Autobound** (real-time intelligence - highly recommended):
```bash
# Get key at: https://app2.autobound.ai/settings/api-keys
export AUTOBOUND_API_KEY="your-key"
```

**Gamma** (client-facing presentations - required):
```bash
# Get key at: https://gamma.app/settings/api
export GAMMA_API_KEY="sk-gamma-xxx"
```

Add to your shell config to make permanent:
```bash
echo 'export AUTOBOUND_API_KEY="your-key"' >> ~/.bashrc
echo 'export GAMMA_API_KEY="sk-gamma-xxx"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Install Auto-Trigger

Watches calendar and auto-preps discovery calls:
```bash
cd /home/clawdbot/clawd/skills/meeting-prep
bash install_cron.sh
```

Now runs every 30 minutes automatically!

### 3. Test It

```bash
./test_v2.sh "Test Lead" "Test Company" [email protected] test.com
```

You should see:
- ✅ Folder created
- ✅ Intelligence doc created
- ✅ Talking points doc created
- ✅ Gamma slides created

## 📅 Usage

### Automatic (Recommended)

Just book calendar events with **"discovery call"** in the title.

Every 30 minutes, the skill:
1. Finds new discovery calls
2. Creates folder + docs + slides
3. Updates calendar with links

### Manual

Prep a specific meeting:
```bash
uv run scripts/meeting_prep_orchestrator_v2.py \
  "Sarah Johnson" "Acme Corp" \
  --email [email protected] \
  --domain acme.com \
  --event-id <calendar_event_id>
```

## 🎬 During the Call

### Setup
- **Screen-share:** Gamma Presentation (client sees this)
- **Your screen (not shared):** Talking Points Doc + Intelligence Doc

### Flow
1. Load Gamma presentation
2. Start screen-share
3. Walk through slides 1-10
4. Let slides guide conversation
5. Reference your docs (not shared) as needed

### What Client Sees
- Professional 10-slide Gamma presentation
- Shows you're prepared
- Guides natural conversation
- No boring "pitch deck"

### What You See (not shared)
- Talking Points Doc - Your script
- Intelligence Doc - Quick facts

## 📂 What Gets Created

```
Google Drive:
└── Discovery - Sarah Johnson @ Acme Corp/
    ├── Intelligence - Sarah Johnson @ Acme Corp.gdoc
    │   └── All research, Autobound insights, company intel
    │       (YOUR REFERENCE - keep open during call)
    │
    ├── Talking Points - Sarah Johnson @ Acme Corp.gdoc  
    │   └── Icebreakers, agenda, questions, objections
    │       (YOUR SCRIPT - review before + during call)
    │
    └── Gamma Presentation
        └── 10-slide client-facing deck
            (SCREEN-SHARE THIS during the call)
```

Plus: Calendar event updated with links to everything.

## 💡 Key Points

✅ **Gamma = Client-Facing**
- Professional presentation
- Screen-share during call
- Shows you're prepared

✅ **Docs = Your Reference**
- Intelligence Doc: Research & facts
- Talking Points Doc: Your script
- Never show these to client

✅ **Reuses Google Workspace Skill**
- Uses `beautiful_doc.py` from google-workspace
- Creates professional Google Docs
- Manages folders with `folder_manager.py`

✅ **Auto-Trigger**
- Runs every 30 minutes
- Preps discovery calls automatically
- Updates calendar

## 🔍 Monitor

View auto-trigger activity:
```bash
tail -f logs/auto_trigger.log
```

Test what would be prepped:
```bash
uv run scripts/auto_trigger.py --dry-run
```

## 🆘 Troubleshooting

**"GAMMA_API_KEY not set"**
```bash
echo $GAMMA_API_KEY  # Should show your key
export GAMMA_API_KEY="sk-gamma-xxx"
```

**"No discovery calls found"**
- Event title must contain "discovery call"
- Event must be within next 14 days
- Must have external attendee

**Cron not running**
```bash
crontab -l  # Should see auto_trigger.py entry
```

## 📖 More Info

- **SKILL.md** - Full documentation
- **USAGE.md** - Detailed usage guide  
- **CHANGELOG.md** - What's new in v2.0

---

**That's it!** Book a discovery call and watch it auto-prep. 🎯
