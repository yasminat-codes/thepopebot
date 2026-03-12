#!/usr/bin/env python3
"""
Meeting Prep Orchestrator v2
Creates dedicated folder per lead with intelligence doc, talking points doc, and Gamma slides
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
#   "requests",
# ]
# ///

import json
import sys
from pathlib import Path
from datetime import datetime

# Import standalone skills
sys.path.insert(0, "/home/clawdbot/clawd/skills/autobound/scripts")
from autobound import AutoboundClient

sys.path.insert(0, "/home/clawdbot/clawd/skills/gamma/scripts")
from gamma import GammaClient

sys.path.insert(0, "/home/clawdbot/clawd/skills/gdocs-pro/scripts")
from beautiful_doc import BeautifulDocBuilder
from folder_manager import create_folder, move_to_folder

sys.path.insert(0, str(Path(__file__).parent))
from lead_researcher import LeadResearcher
from calendar_integration import CalendarIntegration

class MeetingPrepOrchestratorV2:
    """Complete meeting prep with dedicated folder structure"""
    
    def __init__(self):
        self.researcher = LeadResearcher()
        self.calendar = CalendarIntegration()
        
        # Try to initialize Autobound (optional but recommended)
        try:
            self.autobound = AutoboundClient()
            self.autobound_enabled = True
        except Exception as e:
            print(f"⚠️  Autobound not available: {e}")
            self.autobound = None
            self.autobound_enabled = False
        
        # Try to initialize Gamma (optional)
        try:
            self.gamma = GammaClient()
            self.gamma_enabled = True
        except Exception as e:
            print(f"⚠️  Gamma not available: {e}")
            self.gamma = None
            self.gamma_enabled = False
    
    def prep_meeting(
        self,
        lead_name: str,
        company_name: str,
        meeting_date=None,
        event_id=None,
        lead_email=None,
        company_domain=None
    ):
        """
        Complete meeting prep workflow with folder structure
        
        Args:
            lead_name: Lead's full name
            company_name: Company name
            meeting_date: Optional meeting date
            event_id: Optional calendar event ID to update
            lead_email: Lead's email (for Autobound)
            company_domain: Company domain (for Autobound)
        """
        print("="*80)
        print(f"🎯 DISCOVERY MEETING PREP: {lead_name} @ {company_name}")
        print("="*80)
        
        prep = {
            'lead_name': lead_name,
            'company_name': company_name,
            'meeting_date': meeting_date or datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'event_id': event_id,
            'lead_email': lead_email,
            'company_domain': company_domain
        }
        
        # PHASE 1: CREATE FOLDER
        print("\n📁 PHASE 1: CREATE DEDICATED FOLDER")
        folder_name = f"Discovery - {lead_name} @ {company_name}"
        folder_id = create_folder(folder_name)
        print(f"   ✅ Folder created: {folder_name}")
        print(f"   📂 ID: {folder_id}")
        prep['folder_id'] = folder_id
        prep['folder_name'] = folder_name
        
        # PHASE 2: RESEARCH
        print("\n📚 PHASE 2: RESEARCH & INTELLIGENCE")
        
        # 2a. Autobound Intelligence
        autobound_data = None
        if self.autobound_enabled and (lead_email or company_domain):
            print("   🚀 Getting Autobound intelligence...")
            try:
                autobound_data = self.autobound.get_insights(
                    contact_email=lead_email,
                    company_domain=company_domain,
                    company_name=company_name
                )
                formatted_insights = self.autobound.format_insights_for_prep(autobound_data)
                print(f"   ✅ Autobound: {formatted_insights['total_insights']} insights found")
                prep['autobound_insights'] = formatted_insights
            except Exception as e:
                print(f"   ⚠️  Autobound error: {e}")
        
        # 2b. Additional research
        print("   🔍 Running additional research...")
        research = self.researcher.research_lead(lead_name, company_name)
        prep['research'] = research
        
        # PHASE 3: CREATE INTELLIGENCE DOC
        print("\n📄 PHASE 3: CREATE MEETING INTELLIGENCE DOC")
        intelligence_doc_url = self._create_intelligence_doc(prep, folder_id)
        prep['intelligence_doc_url'] = intelligence_doc_url
        print(f"   ✅ Intelligence doc created")
        
        # PHASE 4: CREATE TALKING POINTS DOC
        print("\n💬 PHASE 4: CREATE TALKING POINTS DOC")
        talking_points_doc_url = self._create_talking_points_doc(prep, folder_id)
        prep['talking_points_doc_url'] = talking_points_doc_url
        print(f"   ✅ Talking points doc created")
        
        # PHASE 5: CREATE GAMMA SLIDES
        print("\n🎨 PHASE 5: CREATE GAMMA PRESENTATION")
        gamma_url = self._create_gamma_presentation(prep, folder_id)
        prep['gamma_url'] = gamma_url
        if gamma_url != "Gamma not available":
            print(f"   ✅ Gamma slides created")
        
        # PHASE 6: UPDATE CALENDAR EVENT
        if event_id:
            print("\n📅 PHASE 6: UPDATE CALENDAR EVENT")
            self._update_calendar_event(event_id, prep)
            print(f"   ✅ Calendar event updated with all links")
        
        print("\n" + "="*80)
        print("✅ MEETING PREP COMPLETE!")
        print("="*80)
        print(f"\n📂 Folder: {folder_name}")
        print(f"📄 Intelligence Doc: {intelligence_doc_url}")
        print(f"💬 Talking Points Doc: {talking_points_doc_url}")
        if gamma_url != "Gamma not available":
            print(f"🎨 Gamma Slides: {gamma_url}")
        print()
        
        return prep
    
    def _create_intelligence_doc(self, prep_data, folder_id):
        """Create meeting intelligence document"""
        lead_name = prep_data['lead_name']
        company_name = prep_data['company_name']
        autobound = prep_data.get('autobound_insights')
        research = prep_data.get('research', {})
        
        builder = BeautifulDocBuilder()
        doc_id = builder.create_document(f"Intelligence - {lead_name} @ {company_name}")
        
        # Move to folder
        move_to_folder(doc_id, folder_id)
        
        # Title
        builder.add_title(f"MEETING INTELLIGENCE\n{lead_name} @ {company_name}")
        builder.add_paragraph(f"Prepared: {datetime.now().strftime('%B %d, %Y')}")
        builder.add_line_break()
        
        # Autobound Intelligence Section
        if autobound:
            builder.add_section_header("🚀 REAL-TIME INTELLIGENCE (Autobound)")
            builder.add_line_break()
            
            # Contact Info
            contact = autobound.get('contact', {})
            if contact.get('title'):
                builder.add_paragraph(f"**{contact.get('name', 'Contact')}**")
                builder.add_paragraph(f"Title: {contact['title']}")
            if contact.get('linkedin'):
                builder.add_paragraph(f"LinkedIn: {contact['linkedin']}")
            if contact.get('email'):
                builder.add_paragraph(f"Email: {contact['email']}")
            builder.add_line_break()
            
            # Company Info
            company = autobound.get('company', {})
            if company.get('description'):
                builder.add_paragraph(f"**About {company_name}**")
                builder.add_paragraph(company['description'][:600])
                builder.add_line_break()
            
            # Recent News
            news = autobound.get('insights', {}).get('recent_news', [])
            if news:
                builder.add_section_header("📰 RECENT NEWS & ANNOUNCEMENTS")
                for item in news[:5]:
                    builder.add_paragraph(f"• **{item['title']}**")
                    if item.get('description'):
                        builder.add_paragraph(f"  {item['description'][:200]}")
                    if item.get('date'):
                        builder.add_paragraph(f"  Date: {item['date']}")
                    builder.add_line_break()
            
            # Hiring Signals
            hiring = autobound.get('insights', {}).get('hiring_signals', [])
            if hiring:
                builder.add_section_header("👥 HIRING SIGNALS")
                for item in hiring[:3]:
                    builder.add_paragraph(f"• {item['description']}")
                builder.add_line_break()
            
            # Tech Stack
            tech = autobound.get('insights', {}).get('tech_stack', [])
            if tech:
                builder.add_section_header("💻 TECH STACK")
                tech_items = [f"{item['technology']}" for item in tech[:8]]
                builder.add_bullet_list(tech_items)
                builder.add_line_break()
            
            # LinkedIn Activity
            linkedin = autobound.get('insights', {}).get('linkedin_activity', [])
            if linkedin:
                builder.add_section_header("💼 LINKEDIN ACTIVITY")
                for item in linkedin[:3]:
                    builder.add_paragraph(f"• {item['content'][:200]}")
                    if item.get('date'):
                        builder.add_paragraph(f"  {item['date']}")
                builder.add_line_break()
            
            # Funding
            funding = autobound.get('insights', {}).get('funding', [])
            if funding:
                builder.add_section_header("💰 FUNDING & INVESTMENTS")
                for item in funding:
                    builder.add_paragraph(f"• {item['description']}")
                builder.add_line_break()
        
        # Traditional Research Section
        builder.add_section_header("📊 ADDITIONAL RESEARCH")
        builder.add_line_break()
        
        # Company Overview
        if research.get('company_overview'):
            builder.add_paragraph("**Company Overview:**")
            builder.add_paragraph(research['company_overview'][:800])
            builder.add_line_break()
        
        # Recent News (if not from Autobound)
        if not autobound or not autobound.get('insights', {}).get('recent_news'):
            if research.get('recent_news'):
                builder.add_paragraph("**Recent News:**")
                news_items = [
                    f"{item['title']} ({item.get('source', 'Unknown')}, {item.get('date', 'Recent')})"
                    for item in research['recent_news'][:5]
                ]
                builder.add_bullet_list(news_items)
                builder.add_line_break()
        
        # Lead Background
        if research.get('lead_background'):
            builder.add_paragraph("**About the Lead:**")
            builder.add_paragraph(research['lead_background'][:600])
            builder.add_line_break()
        
        # Industry Context
        if research.get('industry_context'):
            builder.add_paragraph("**Industry Context:**")
            context_items = [
                f"{item.get('title', 'Insight')}: {item.get('content', '')[:120]}"
                for item in research['industry_context'][:3]
            ]
            builder.add_bullet_list(context_items)
        
        builder.flush()
        builder.make_shareable()
        
        return builder.get_url()
    
    def _create_talking_points_doc(self, prep_data, folder_id):
        """Create talking points, agenda, icebreakers document"""
        lead_name = prep_data['lead_name']
        company_name = prep_data['company_name']
        autobound = prep_data.get('autobound_insights')
        research = prep_data.get('research', {})
        
        builder = BeautifulDocBuilder()
        doc_id = builder.create_document(f"Talking Points - {lead_name} @ {company_name}")
        
        # Move to folder
        move_to_folder(doc_id, folder_id)
        
        # Title
        builder.add_title(f"DISCOVERY CALL GUIDE\n{lead_name} @ {company_name}")
        builder.add_paragraph(f"Meeting Date: {prep_data.get('meeting_date', 'TBD')}")
        builder.add_line_break()
        
        # Ice Breakers
        builder.add_section_header("❄️ ICE BREAKERS")
        icebreakers = self._generate_icebreakers(autobound, research, lead_name, company_name)
        for icebreaker in icebreakers:
            builder.add_paragraph(f"• {icebreaker}")
        builder.add_line_break()
        
        # Meeting Agenda
        builder.add_section_header("📋 MEETING AGENDA (50 MIN)")
        agenda_items = [
            "**Introduction (5 min)** - Quick intros, set expectations",
            "**Understand Their Business (15 min)** - Current situation, goals, challenges",
            "**Explore Pain Points (10 min)** - Dig into specific challenges",
            "**Discuss Solutions (15 min)** - How we can help, relevant examples",
            "**Next Steps (5 min)** - Follow-up actions, timeline"
        ]
        for item in agenda_items:
            builder.add_paragraph(item)
        builder.add_line_break()
        
        # Key Questions
        builder.add_section_header("❓ KEY QUESTIONS TO ASK")
        questions = self._generate_questions(autobound, research, company_name)
        builder.add_bullet_list(questions)
        builder.add_line_break()
        
        # Talking Points
        builder.add_section_header("💬 TALKING POINTS")
        
        # Company Context Points
        builder.add_paragraph("**Company Context:**")
        company_points = self._generate_company_points(autobound, research, company_name)
        builder.add_bullet_list(company_points)
        builder.add_line_break()
        
        # Recent News Hooks
        news = autobound.get('insights', {}).get('recent_news', []) if autobound else research.get('recent_news', [])
        if news:
            builder.add_paragraph("**Recent News Hooks:**")
            news_points = [
                f"Congratulate on: {item.get('title', item.get('title', 'recent announcement'))}"
                for item in news[:3]
            ]
            builder.add_bullet_list(news_points)
            builder.add_line_break()
        
        # Personal Connection Points
        builder.add_paragraph("**Personal Connection:**")
        personal_points = self._generate_personal_points(autobound, research, lead_name)
        builder.add_bullet_list(personal_points)
        builder.add_line_break()
        
        # Solution Positioning
        builder.add_section_header("🎯 SOLUTION POSITIONING")
        positioning_points = [
            "Focus on automating repetitive tasks",
            "Highlight time saved for strategic work",
            "Reference similar clients in their industry",
            "Emphasize ROI and measurable results",
            "Position as growth enabler, not just cost savings"
        ]
        builder.add_bullet_list(positioning_points)
        builder.add_line_break()
        
        # Objection Handling
        builder.add_section_header("🛡️ POTENTIAL OBJECTIONS & RESPONSES")
        objections = [
            "**'We're too small'** → Many 1-50 employee companies see biggest impact from automation",
            "**'Too expensive'** → ROI typically realized in 2-3 months through time savings",
            "**'Too complex'** → We handle implementation, you focus on your business",
            "**'Not sure we need it'** → Let's identify 1-2 pain points and see if automation fits"
        ]
        for objection in objections:
            builder.add_paragraph(objection)
        builder.add_line_break()
        
        # Next Steps Template
        builder.add_section_header("✅ NEXT STEPS TEMPLATE")
        next_steps = [
            "Schedule follow-up for proposal review",
            "Send personalized proposal within 48 hours",
            "Provide relevant case studies",
            "Offer pilot/POC if appropriate",
            "Connect on LinkedIn"
        ]
        builder.add_bullet_list(next_steps)
        
        builder.flush()
        builder.make_shareable()
        
        return builder.get_url()
    
    def _generate_icebreakers(self, autobound, research, lead_name, company_name):
        """Generate personalized icebreakers"""
        icebreakers = []
        
        # From LinkedIn activity
        if autobound:
            linkedin = autobound.get('insights', {}).get('linkedin_activity', [])
            if linkedin:
                recent_post = linkedin[0]['content'][:80]
                icebreakers.append(f"Saw your recent LinkedIn post about {recent_post}... - great insights!")
        
        # From recent news
        news = None
        if autobound:
            news = autobound.get('insights', {}).get('recent_news', [])
        elif research:
            news = research.get('recent_news', [])
        
        if news:
            icebreakers.append(f"Congrats on {news[0].get('title', 'recent announcement')}!")
        
        # From hiring
        if autobound:
            hiring = autobound.get('insights', {}).get('hiring_signals', [])
            if hiring:
                icebreakers.append(f"Noticed you're hiring - exciting growth phase!")
        
        # Generic but warm
        icebreakers.append(f"Thanks for taking the time today - looking forward to learning about {company_name}!")
        
        return icebreakers[:4]  # Top 4
    
    def _generate_questions(self, autobound, research, company_name):
        """Generate key questions to ask"""
        questions = [
            "What's your current workflow for [relevant process]?",
            "What are your biggest challenges right now?",
            "How much time does your team spend on [specific task]?",
            "What does success look like for you this quarter/year?",
            "Have you tried automation solutions before? What was the experience?"
        ]
        
        # Add tech stack question if we have that info
        if autobound:
            tech = autobound.get('insights', {}).get('tech_stack', [])
            if tech:
                tech_names = [t['technology'] for t in tech[:3]]
                questions.insert(2, f"I see you're using {', '.join(tech_names)} - how's that working for you?")
        
        # Add hiring question if they're hiring
        if autobound:
            hiring = autobound.get('insights', {}).get('hiring_signals', [])
            if hiring:
                questions.append("You're growing the team - what are the biggest scaling challenges?")
        
        return questions
    
    def _generate_company_points(self, autobound, research, company_name):
        """Generate company context points"""
        points = []
        
        # From Autobound company info
        if autobound:
            company = autobound.get('company', {})
            if company.get('industry'):
                points.append(f"Operating in {company['industry']} space")
            if company.get('size'):
                points.append(f"Team size: {company['size']}")
        
        # From research
        if research.get('company_overview'):
            overview_snippet = research['company_overview'][:100]
            points.append(f"Focus: {overview_snippet}...")
        
        # Generic starter
        points.append(f"Ask about current workflow and process bottlenecks")
        points.append(f"Understand their tech stack and integration needs")
        
        return points[:5]
    
    def _generate_personal_points(self, autobound, research, lead_name):
        """Generate personal connection points"""
        points = []
        
        # From Autobound contact
        if autobound:
            contact = autobound.get('contact', {})
            if contact.get('title'):
                points.append(f"Acknowledge expertise as {contact['title']}")
        
        # From research
        if research.get('lead_background'):
            bg_snippet = research['lead_background'][:80]
            points.append(f"Reference: {bg_snippet}...")
        
        # Generic
        points.append(f"Ask about biggest challenges in their role")
        points.append(f"Understand decision-making process and timeline")
        
        return points[:4]
    
    def _create_gamma_presentation(self, prep_data, folder_id):
        """Create Gamma presentation slides - CLIENT-FACING for use during the call"""
        if not self.gamma_enabled:
            print("   ⚠️  Gamma API not available - skipping slides")
            return "Gamma not available"
        
        lead_name = prep_data['lead_name']
        company_name = prep_data['company_name']
        autobound = prep_data.get('autobound_insights')
        research = prep_data.get('research', {})
        
        # Build CLIENT-FACING presentation content
        # This is what you'll screen share during the discovery call
        
        slides_content = f"""# Welcome!
Discovery Call with {company_name}

Thank you for your time today. We're excited to learn about your business and explore how we can help.

---

# About Smarterflo

**AI Automation Agency**

We help businesses with 1-50 employees:
• Automate repetitive tasks
• Optimize workflows
• Generate & nurture leads
• Scale without adding headcount

Focus: Practical AI automation that delivers ROI in 60-90 days

---

# Today's Agenda

**50 minutes together:**

1. **Understand your business** (15 min)
   Learn about your goals and challenges

2. **Explore opportunities** (15 min)
   Identify automation potential

3. **Share solutions** (15 min)
   Relevant examples and approaches

4. **Next steps** (5 min)
   Agree on follow-up

---

# What We've Learned About {company_name}

"""
        
        # Add what we know about them (show we did homework)
        insights_added = False
        
        if autobound:
            company = autobound.get('company', {})
            if company.get('industry'):
                slides_content += f"• Industry: {company['industry']}\n"
                insights_added = True
            if company.get('size'):
                slides_content += f"• Team size: {company['size']}\n"
                insights_added = True
        
        # Add recent news (shows we're current)
        news = autobound.get('insights', {}).get('recent_news', []) if autobound else research.get('recent_news', [])
        if news and len(news) > 0:
            slides_content += f"• Recent: {news[0].get('title', 'Growth activity')}\n"
            insights_added = True
        
        # Add hiring if relevant
        if autobound:
            hiring = autobound.get('insights', {}).get('hiring_signals', [])
            if hiring:
                slides_content += f"• Growing team - exciting phase!\n"
                insights_added = True
        
        if not insights_added:
            slides_content += f"Looking forward to learning more about {company_name} today!\n"
        
        slides_content += """
**Our goal today:** Understand if we're a good fit to help you scale.

---

# Common Challenges We Solve

**For businesses like yours:**

• **Lead generation** - Consistent pipeline without manual work
• **Follow-up automation** - Never miss an opportunity
• **Data entry & admin** - Free up time for strategy
• **Customer onboarding** - Smooth, automated experience
• **Reporting & insights** - Real-time visibility

Sound familiar? Let's discuss your specific challenges.

---

# Our Approach

**1. Discovery** (Today!)
   Understand your workflows and pain points

**2. Custom Proposal** (48 hours)
   Tailored automation plan with clear ROI

**3. Pilot Implementation** (2-4 weeks)
   Start small, prove value quickly

**4. Scale** (Ongoing)
   Expand automation as we prove results

**Focus:** Quick wins first, then scale.

---

# Similar Success Stories

**Recent client examples:**

• **15-person agency:** Automated lead qualification → 40% more qualified calls
• **30-person SaaS:** Email sequences → 3x conversion rate
• **Small consultancy:** Onboarding automation → 10 hours/week saved

**Key insight:** You don't need to be "big enough" for automation. 
Small teams see the biggest impact.

---

# Questions for You

**To make this valuable, we'd love to understand:**

• What's your biggest time sink right now?
• Where are leads falling through the cracks?
• What manual tasks frustrate your team?
• What would free up 10 hours/week enable?
• What does success look like for you?

**This is your call** - let's focus on what matters to you.

---

# Next Steps

**If today goes well:**

1. **Custom proposal** within 48 hours
   Specific to your challenges and goals

2. **Case studies** in your industry
   See what's worked for similar businesses

3. **Pilot scope** (optional)
   Start with one high-impact workflow

**No pressure** - only move forward if it makes sense for {company_name}.

---

# Let's Talk!

**Thank you for your time, {lead_name}**

Ready when you are - what would you like to focus on first?
"""
        
        try:
            print("   🎨 Generating client-facing Gamma presentation...")
            result = self.gamma.create_presentation(
                input_text=slides_content,
                text_mode="preserve",
                format="presentation",
                num_cards=10,
                tone="professional, warm, consultative",
                audience=f"{lead_name} at {company_name} - potential client",
                additional_instructions=f"Client-facing discovery call presentation. Clean, professional, conversational. For {company_name}. Use high-quality images that convey trust and professionalism.",
                image_source="unsplash",
                image_style="professional business, modern, clean"
            )
            
            generation_id = result['generationId']
            print(f"   ⏳ Waiting for Gamma to complete...")
            
            status = self.gamma.wait_for_completion(generation_id, max_wait=180)
            
            return status['gammaUrl']
            
        except Exception as e:
            print(f"   ⚠️  Gamma generation failed: {e}")
            return "Gamma generation failed"
    
    def _update_calendar_event(self, event_id, prep_data):
        """Update calendar event with all prep links"""
        lead_name = prep_data['lead_name']
        company_name = prep_data['company_name']
        folder_name = prep_data['folder_name']
        intelligence_url = prep_data['intelligence_doc_url']
        talking_points_url = prep_data['talking_points_doc_url']
        gamma_url = prep_data.get('gamma_url', '')
        
        description = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DISCOVERY CALL PREP - {lead_name} @ {company_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 **All materials in folder:** {folder_name}

📄 **Meeting Intelligence Doc**
   {intelligence_url}
   → Real-time Autobound insights, company research, lead background

💬 **Talking Points Doc**
   {talking_points_url}
   → Icebreakers, agenda, questions, talking points, objection handling

🎨 **Presentation Slides**
   {gamma_url if gamma_url and gamma_url != "Gamma not available" else "Create manually or run Gamma generation"}
   → Visual presentation for the call

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **You're ready for this discovery call!**

**Quick Prep (10 min before call):**
1. Review talking points doc
2. Check icebreakers section
3. Have intelligence doc open for reference

**After Call:**
• Add call transcript to folder
• Update talking points with notes
• Schedule follow-up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        self.calendar.add_doc_to_event(
            event_id,
            intelligence_url,  # Primary doc URL
            lead_name,
            company_name,
            custom_description=description
        )

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeting Prep Automation V2")
    parser.add_argument('lead_name', help="Lead's name")
    parser.add_argument('company_name', help="Company name")
    parser.add_argument('--date', help="Meeting date")
    parser.add_argument('--event-id', help="Calendar event ID")
    parser.add_argument('--email', help="Lead's email (for Autobound)")
    parser.add_argument('--domain', help="Company domain (for Autobound)")
    
    args = parser.parse_args()
    
    orchestrator = MeetingPrepOrchestratorV2()
    
    result = orchestrator.prep_meeting(
        lead_name=args.lead_name,
        company_name=args.company_name,
        meeting_date=args.date,
        event_id=args.event_id,
        lead_email=args.email,
        company_domain=args.domain
    )
    
    print("\n" + "="*80)
    print("📊 PREP SUMMARY")
    print("="*80)
    print(f"Folder: {result['folder_name']}")
    print(f"Intelligence Doc: {result['intelligence_doc_url']}")
    print(f"Talking Points Doc: {result['talking_points_doc_url']}")
    if result.get('gamma_url') and result['gamma_url'] not in ['Gamma not available', 'Gamma generation failed']:
        print(f"Gamma Slides: {result['gamma_url']}")
    print()

if __name__ == '__main__':
    main()
