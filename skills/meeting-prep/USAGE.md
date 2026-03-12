# Meeting Prep - How to Use

## 📁 What You Get

When you prep a discovery call, you get a **dedicated folder** with 3 things:

```
Discovery - Sarah Johnson @ Acme Corp/
├── 📄 Intelligence Doc (YOUR REFERENCE)
├── 💬 Talking Points Doc (YOUR SCRIPT)
└── 🎨 Gamma Presentation (CLIENT SEES THIS)
```

## 🎯 Purpose of Each

| Document | Who Sees It | Purpose | When to Use |
|----------|-------------|---------|-------------|
| **Intelligence Doc** | You only | All research & Autobound insights | Quick reference during call |
| **Talking Points Doc** | You only | Your complete call script | Before call + open during call |
| **Gamma Presentation** | **CLIENT** | Professional presentation | **Screen-share during call** |

## 🖥️ Setup During Call

### Recommended Screen Layout

**Monitor 1 (Main - what client sees):**
- Gamma Presentation (screen-shared)
- Zoom/Meet window with their camera

**Monitor 2 (Your reference):**
- Talking Points Doc (not shared)
- Intelligence Doc in background tab

**OR if single monitor:**
- Screen-share: Gamma Presentation
- Side window (not shared): Talking Points Doc

## 📋 Step-by-Step Usage

### Day Before Call

1. **Auto-trigger runs** (or run manually)
   ```bash
   uv run scripts/meeting_prep_orchestrator_v2.py "Sarah Johnson" "Acme Corp" \
     --email [email protected] --domain acme.com
   ```

2. **Folder created** with all materials
3. **Calendar updated** with links

### Morning of Call (10 min prep)

1. **Open folder** from calendar link
2. **Read Talking Points Doc** (5 min)
   - Icebreakers
   - Questions to ask
   - Agenda flow
3. **Skim Intelligence Doc** (3 min)
   - Recent news
   - Key company facts
   - Lead background
4. **Load Gamma Presentation** (2 min)
   - Open in browser
   - Test screen-share works

### During Call (50 min)

**What client sees:**
- Your face (camera)
- Gamma presentation (screen-share)

**What you see (not shared):**
- Talking Points Doc (your script)
- Intelligence Doc (quick facts)

**Flow:**
1. **Start with Gamma slide 1** - Welcome
2. **Follow slides 2-10** - Guide conversation
3. **Refer to Talking Points** - For questions/icebreakers
4. **Check Intelligence Doc** - If they ask specific questions
5. **Take notes** in Talking Points Doc

### After Call

1. **Stop screen-share**
2. **Add call transcript** to folder (Fathom auto-saves)
3. **Update Talking Points** with notes & action items
4. **Send follow-up:**
   - Share Gamma presentation link
   - Reference specific points from call
   - Propose next steps

## 🎨 About the Gamma Presentation

### Purpose
Professional, client-facing deck that:
- Shows you did your homework
- Guides the conversation
- Keeps you on track
- Looks polished and prepared

### Structure (10 slides)
1. Welcome - Set tone
2. About Smarterflo - Who we are
3. Agenda - What to expect
4. About Them - Show research
5. Common Challenges - Relatable
6. Our Approach - How we work
7. Success Stories - Proof
8. Questions - Collaborative
9. Next Steps - Clear path
10. Open Discussion - Their turn

### How to Present It
- **Screen-share in presentation mode**
- **Advance slides as conversation flows**
- **Don't read verbatim** - slides are prompts
- **Pause for discussion** - it's a conversation, not a pitch
- **Let them drive** if they want to jump around

## 📊 Example Call Flow

**0:00-5:00** - Welcome & Intro
- Screen-share Gamma (slide 1)
- Use icebreaker from Talking Points
- Show agenda (slide 3)

**5:00-20:00** - Understand Their Business
- Show "What We Learned" (slide 4)
- Ask questions from Talking Points
- Listen more than talk
- Take notes in Talking Points Doc

**20:00-35:00** - Explore Challenges
- Show "Common Challenges" (slide 5)
- Dig into their pain points
- Reference Intelligence Doc for specific facts

**35:00-45:00** - Discuss Solutions
- Show "Our Approach" (slide 6)
- Share "Success Stories" (slide 7)
- Position how you can help

**45:00-50:00** - Next Steps
- Show "Next Steps" (slide 9)
- Agree on follow-up
- Open discussion (slide 10)

## 💡 Pro Tips

### Do's ✅
- **Personalize icebreakers** from recent LinkedIn/news
- **Let them talk 70%** of the time
- **Take live notes** in Talking Points Doc
- **Reference specific insights** from Intelligence Doc
- **Send Gamma link after** as follow-up

### Don'ts ❌
- **Don't read slides word-for-word** - use as guide
- **Don't rush through** - pause for discussion
- **Don't screen-share your notes** - only Gamma
- **Don't pitch too early** - understand first
- **Don't skip objection prep** - review before call

## 🔧 Technical Setup

### Before First Call
```bash
# 1. Get API keys
export AUTOBOUND_API_KEY="your-key"
export GAMMA_API_KEY="sk-gamma-xxx"

# 2. Test it works
cd /home/clawdbot/clawd/skills/meeting-prep
./test_v2.sh "Test Lead" "Test Company" [email protected] test.com

# 3. Install auto-trigger
bash install_cron.sh
```

### Test Your Setup
- Screen-share works in Zoom/Meet
- Gamma presentation loads
- Can open docs without screen-sharing them
- Audio/video working

## 📞 Quick Reference Card

**Print this and keep next to you:**

```
DISCOVERY CALL CHECKLIST

Before:
□ Open Talking Points Doc (not shared)
□ Load Gamma Presentation (will share)
□ Have Intelligence Doc ready (background)
□ Test screen-share

During:
□ Screen-share Gamma only
□ Follow slides 1-10
□ Use icebreakers from Talking Points
□ Take notes in Talking Points Doc
□ Let them talk 70%

After:
□ Add transcript to folder
□ Update notes
□ Send Gamma link
□ Propose next steps
```

## 🎯 Success Metrics

Good discovery call = 
- Client talked more than you
- Uncovered 2-3 real pain points
- Clear next steps agreed
- Gamma helped guide conversation
- You looked prepared and professional

---

**Remember:** The Gamma presentation is FOR THE CLIENT. 
Your docs are FOR YOU. Keep them separate during the call.
