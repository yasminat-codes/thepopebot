# Meeting Prep - Quick Setup

Never go into a discovery call unprepared! 🎯

## 1. Get Autobound API Key (REQUIRED)

Autobound provides real-time intelligence on 250M+ contacts and 50M+ companies.

1. Go to https://app2.autobound.ai/settings/api-keys
2. Sign up (free credits included)
3. Generate API key
4. Add to environment:

```bash
export AUTOBOUND_API_KEY="your-key-here"
```

Or add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export AUTOBOUND_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## 2. Test Autobound Integration

```bash
cd /home/clawdbot/clawd/skills/meeting-prep
./test_autobound.sh [email protected] example.com
```

You should see insights like:
- Contact title & LinkedIn
- Company description & industry
- Recent news & announcements
- Hiring signals
- Tech stack
- LinkedIn activity

## 3. Setup Auto-Trigger

This makes it fully automatic! Runs every 30 minutes.

```bash
cd /home/clawdbot/clawd/skills/meeting-prep
bash install_cron.sh
```

Now whenever you book a discovery call (with "discovery call" in the title), it will automatically:
1. Detect the new meeting
2. Extract lead email & company
3. Run Autobound intelligence
4. Create beautiful Google Doc
5. Add doc link to calendar event

## 4. Test Manual Prep

Without waiting for auto-trigger:

```bash
uv run scripts/meeting_prep_orchestrator.py "John Smith" "Acme Corp" --event-id "calendar_event_123"
```

## 5. Monitor Auto-Trigger

Watch the logs to see it working:

```bash
tail -f logs/auto_trigger.log
```

## Usage

### Automatic (Recommended)
Just book discovery calls with "discovery call" in the title. The skill handles the rest!

### Manual Trigger
```bash
# Test what would be prepped (dry run)
uv run scripts/auto_trigger.py --dry-run

# Force run now
uv run scripts/auto_trigger.py

# Reset history (re-prep everything)
uv run scripts/auto_trigger.py --reset-history
```

### Manual Prep Specific Meeting
```bash
uv run scripts/meeting_prep_orchestrator.py "Jane Doe" "TechCorp Inc"
```

## Calendar Event Requirements

For auto-trigger to work, your discovery call events need:
- Title containing "discovery call" (case-insensitive)
- At least one external attendee (not @smarterflo.com)
- Event in the next 14 days
- At least 2 hours before meeting starts

## What You Get

For each discovery call:
- 📄 **Google Doc Report** with:
  - Autobound real-time intelligence
  - Company overview & recent news
  - Lead background & social activity
  - Hiring signals & tech stack
  - Meeting agenda
  - Talking points
- 📅 **Calendar Event** updated with doc link
- 📊 **Prep History** tracked to avoid duplicates

## Troubleshooting

**"AUTOBOUND_API_KEY not set"**
- Make sure you exported the key
- Test: `echo $AUTOBOUND_API_KEY`
- Should show your key, not empty

**"No upcoming discovery calls found"**
- Make sure event title contains "discovery call"
- Check event is within next 14 days
- Run with `--dry-run` to debug

**"Already prepped - skipping"**
- Skill tracks what it's prepped to avoid duplicates
- To re-prep: `uv run scripts/auto_trigger.py --reset-history`

**Cron not running**
- Check: `crontab -l`
- Should see entry with `auto_trigger.py`
- Check logs: `tail -f logs/auto_trigger.log`

## Optional: Additional Research APIs

For even more data, add these (optional):
```bash
export SERP_API_KEY="your-serpapi-key"
export TAVILY_API_KEY="your-tavily-key"
export PERPLEXITY_API_KEY="your-perplexity-key"
```

But Autobound alone gives you excellent coverage!

## Support

Questions? Check the full SKILL.md or ask Lena! ✨
