#!/usr/bin/env python3
"""
Meeting Prep Orchestrator
Triggers on calendar events, researches, creates slides, agenda, talking points
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
from google.oauth2 import service_account
from googleapiclient.discovery import build

sys.path.insert(0, str(Path(__file__).parent))
from lead_researcher import LeadResearcher
from calendar_integration import CalendarIntegration
from autobound_client import AutoboundClient
sys.path.insert(0, "/home/clawdbot/clawd/skills/gdocs-pro/scripts")
from beautiful_doc import BeautifulDocBuilder

SERVICE_ACCOUNT_FILE = '/home/clawdbot/.config/google/service-account.json'
DELEGATED_USER = 'yasmine@smarterflo.com'

class MeetingPrepOrchestrator:
    """Complete meeting prep automation"""
    
    def __init__(self):
        self.researcher = LeadResearcher()
        self.calendar = CalendarIntegration()
        
        # Try to initialize Autobound (optional)
        try:
            self.autobound = AutoboundClient()
            self.autobound_enabled = True
        except Exception as e:
            print(f"⚠️  Autobound not available: {e}")
            self.autobound = None
            self.autobound_enabled = False
    
    def prep_meeting(self, lead_name, company_name, meeting_date=None, event_id=None, lead_email=None, company_domain=None):
        """
        Complete meeting prep workflow
        
        Args:
            lead_name: Lead's full name
            company_name: Company name
            meeting_date: Optional meeting date
            event_id: Optional calendar event ID to update
            lead_email: Lead's email (for Autobound)
            company_domain: Company domain (for Autobound)
        """
        print("="*70)
        print(f"🎯 MEETING PREP: {lead_name} @ {company_name}")
        print("="*70)
        
        prep = {
            'lead_name': lead_name,
            'company_name': company_name,
            'meeting_date': meeting_date or datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'event_id': event_id,
            'lead_email': lead_email,
            'company_domain': company_domain
        }
        
        # 1. RESEARCH
        print("\n📚 PHASE 1: RESEARCH")
        
        # 1a. Autobound Intelligence (if available)
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
        
        # 1b. Additional research
        research = self.researcher.research_lead(lead_name, company_name)
        prep['research'] = research
        
        # 2. CREATE REPORT
        print("\n📄 PHASE 2: CREATE REPORT")
        report_url = self._create_report(prep)
        prep['report_url'] = report_url
        
        # 2.5. ADD TO CALENDAR EVENT (if event_id provided)
        if event_id:
            print("\n📅 ADDING TO CALENDAR EVENT")
            self.calendar.add_doc_to_event(event_id, report_url, lead_name, company_name)
            prep['calendar_updated'] = True
        
        # 3. CREATE GAMMA SLIDES
        print("\n🎨 PHASE 3: CREATE PRESENTATION")
        gamma_url = self._create_gamma_slides(research)
        prep['gamma_url'] = gamma_url
        
        # 4. CREATE AGENDA
        print("\n📋 PHASE 4: CREATE AGENDA")
        agenda = self._create_agenda(research)
        prep['agenda'] = agenda
        
        # 5. CREATE TALKING POINTS
        print("\n💬 PHASE 5: CREATE TALKING POINTS")
        talking_points = self._create_talking_points(research)
        prep['talking_points'] = talking_points
        
        # 6. SEND SUMMARY
        print("\n📧 PHASE 6: SEND SUMMARY")
        summary = self._create_summary(prep)
        prep['summary'] = summary
        
        print("\n" + "="*70)
        print("✅ MEETING PREP COMPLETE!")
        print("="*70)
        
        return prep
    
    def _create_report(self, prep_data):
        """Create beautiful Google Doc report"""
        research = prep_data.get('research', {})
        autobound = prep_data.get('autobound_insights')
        
        builder = BeautifulDocBuilder()
        doc_id = builder.create_document(f"Meeting Prep: {prep_data['lead_name']} - {prep_data['company_name']}")
        
        # Title
        builder.add_title(f"MEETING PREP\n{prep_data['lead_name']} @ {prep_data['company_name']}")
        
        # Autobound Intelligence (if available)
        if autobound:
            builder.add_section_header("🚀 AUTOBOUND INTELLIGENCE")
            
            # Contact info
            contact = autobound.get('contact', {})
            if contact.get('title'):
                builder.add_paragraph(f"Title: {contact['title']}")
            if contact.get('linkedin'):
                builder.add_paragraph(f"LinkedIn: {contact['linkedin']}")
            builder.add_line_break()
            
            # Company info
            company = autobound.get('company', {})
            if company.get('description'):
                builder.add_paragraph(company['description'][:500])
            builder.add_line_break()
            
            # Recent News from Autobound
            news = autobound.get('insights', {}).get('recent_news', [])
            if news:
                builder.add_section_header("📰 RECENT NEWS (Autobound)")
                news_items = [
                    f"{item['title']} - {item.get('date', 'Recent')}"
                    for item in news[:5]
                ]
                builder.add_bullet_list(news_items)
                builder.add_line_break()
            
            # Hiring Signals
            hiring = autobound.get('insights', {}).get('hiring_signals', [])
            if hiring:
                builder.add_section_header("👥 HIRING SIGNALS")
                hiring_items = [item['description'][:150] for item in hiring[:3]]
                builder.add_bullet_list(hiring_items)
                builder.add_line_break()
            
            # Tech Stack
            tech = autobound.get('insights', {}).get('tech_stack', [])
            if tech:
                builder.add_section_header("💻 TECH STACK")
                tech_items = [f"{item['technology']}: {item.get('description', '')[:100]}" for item in tech[:5]]
                builder.add_bullet_list(tech_items)
                builder.add_line_break()
            
            # LinkedIn Activity
            linkedin = autobound.get('insights', {}).get('linkedin_activity', [])
            if linkedin:
                builder.add_section_header("💼 LINKEDIN ACTIVITY")
                linkedin_items = [item['content'][:150] for item in linkedin[:3]]
                builder.add_bullet_list(linkedin_items)
                builder.add_line_break()
        
        # Traditional Research
        # Company Overview
        builder.add_section_header("COMPANY OVERVIEW")
        if research.get('company_overview'):
            builder.add_paragraph(research['company_overview'][:1000])
        builder.add_line_break()
        
        # Recent News (from traditional research)
        if not autobound or not autobound.get('insights', {}).get('recent_news'):
            builder.add_section_header("RECENT NEWS")
            if research.get('recent_news'):
                news_items = [
                    f"{item['title']} ({item['source']}, {item.get('date', 'Recent')})"
                    for item in research['recent_news'][:5]
                ]
                builder.add_bullet_list(news_items)
            builder.add_line_break()
        
        # Lead Background
        builder.add_section_header("ABOUT THE LEAD")
        if research.get('lead_background'):
            builder.add_paragraph(research['lead_background'][:800])
        builder.add_line_break()
        
        # LinkedIn Activity (from traditional research)
        if not autobound or not autobound.get('insights', {}).get('linkedin_activity'):
            builder.add_section_header("LINKEDIN PRESENCE")
            if research.get('linkedin_info'):
                linkedin_items = [
                    f"{item['title']}: {item.get('snippet', '')[:100]}"
                    for item in research['linkedin_info']
                ]
                builder.add_bullet_list(linkedin_items)
            builder.add_line_break()
        
        # Industry Context
        builder.add_section_header("INDUSTRY CONTEXT")
        if research.get('industry_context'):
            context_items = [
                f"{item.get('title', 'Insight')}: {item.get('content', '')[:150]}"
                for item in research['industry_context'][:3]
            ]
            builder.add_bullet_list(context_items)
        
        builder.flush()
        builder.make_shareable()
        
        return builder.get_url()
    
    def _create_gamma_slides(self, research):
        """Create presentation with Gamma API"""
        # Gamma API integration (placeholder - would use actual Gamma API)
        print("   🎨 Gamma slides feature coming soon")
        print("   📝 For now: Use research report to create slides manually")
        
        # Would call Gamma API here:
        # gamma_api_key = os.getenv('GAMMA_API_KEY')
        # Create presentation with:
        # - Slide 1: Company Overview
        # - Slide 2: Recent News & Achievements  
        # - Slide 3: About the Lead
        # - Slide 4: Industry Context
        # - Slide 5: Discussion Topics
        
        return "Gamma slides (manual creation recommended for now)"
    
    def _create_agenda(self, research):
        """Create meeting agenda"""
        agenda = f"""
MEETING AGENDA
{research['company_name']} Discovery Call

1. INTRODUCTION (5 min)
   - Brief introductions
   - Set expectations for the call

2. UNDERSTAND THEIR BUSINESS (15 min)
   - Current situation & challenges
   - Goals and objectives
   - Ask about: {research.get('company_overview', 'their business model')[:100]}...

3. EXPLORE PAIN POINTS (10 min)
   - Dig into specific challenges
   - Reference: {research.get('recent_news', [{}])[0].get('title', 'recent developments') if research.get('recent_news') else 'industry trends'}

4. DISCUSS SOLUTIONS (15 min)
   - How we can help
   - Relevant case studies
   - Initial ideas

5. NEXT STEPS (5 min)
   - Follow-up actions
   - Timeline
   - Schedule next meeting
"""
        return agenda
    
    def _create_talking_points(self, research):
        """Generate talking points"""
        talking_points = []
        
        # From company overview
        talking_points.append({
            'category': 'Company Context',
            'points': [
                f"Reference their focus on: {research.get('company_overview', '')[:100]}",
                "Ask about their current workflow/process",
                "Understand their team structure"
            ]
        })
        
        # From news
        if research.get('recent_news'):
            news_points = [
                f"Congratulate on: {item['title']}"
                for item in research['recent_news'][:2]
            ]
            talking_points.append({
                'category': 'Recent News',
                'points': news_points
            })
        
        # From lead background
        if research.get('lead_background'):
            talking_points.append({
                'category': 'Personal Connection',
                'points': [
                    f"Acknowledge their expertise in: {research.get('lead_background', '')[:80]}",
                    "Ask about their biggest challenges in current role",
                    "Understand their decision-making process"
                ]
            })
        
        # Industry insights
        talking_points.append({
            'category': 'Industry Trends',
            'points': [
                "Discuss current industry challenges",
                "Share relevant insights from similar clients",
                "Position our solution in context"
            ]
        })
        
        return talking_points
    
    def _create_summary(self, prep):
        """Create email summary"""
        summary = f"""
Meeting Prep Complete: {prep['lead_name']} @ {prep['company_name']}

📄 Research Report: {prep.get('report_url', 'Generated')}
🎨 Presentation: {prep.get('gamma_url', 'See report')}

📋 QUICK AGENDA:
{prep['agenda'][:300]}...

💬 KEY TALKING POINTS:
"""
        
        for category in prep.get('talking_points', []):
            summary += f"\n{category['category']}:\n"
            for point in category['points'][:2]:
                summary += f"  • {point}\n"
        
        summary += "\nYou're ready for the meeting! 🎯"
        
        return summary

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeting Prep Automation")
    parser.add_argument('lead_name', help="Lead's name")
    parser.add_argument('company_name', help="Company name")
    parser.add_argument('--date', help="Meeting date (YYYY-MM-DD)")
    parser.add_argument('--event-id', help="Calendar event ID to update")
    
    args = parser.parse_args()
    
    orchestrator = MeetingPrepOrchestrator()
    
    result = orchestrator.prep_meeting(
        args.lead_name,
        args.company_name,
        args.date,
        args.event_id
    )
    
    print("\n📊 SUMMARY:")
    print(result['summary'])
    print(f"\n📄 Full Report: {result['report_url']}")

if __name__ == '__main__':
    main()
