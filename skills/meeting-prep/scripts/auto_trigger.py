#!/usr/bin/env python3
"""
Auto-Trigger for Meeting Prep
Watches calendar for discovery calls and auto-preps them
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from calendar_integration import CalendarIntegration
from meeting_prep_orchestrator_v2 import MeetingPrepOrchestratorV2

# Track what we've already prepped
PREP_HISTORY_FILE = Path(__file__).parent.parent / 'config' / 'prep_history.json'

class AutoTrigger:
    """Auto-trigger meeting prep for discovery calls"""
    
    def __init__(self):
        self.calendar = CalendarIntegration()
        self.orchestrator = MeetingPrepOrchestratorV2()
        self.history = self._load_history()
    
    def _load_history(self):
        """Load prep history to avoid duplicates"""
        if PREP_HISTORY_FILE.exists():
            with open(PREP_HISTORY_FILE) as f:
                return json.load(f)
        return {'prepped_events': []}
    
    def _save_history(self):
        """Save prep history"""
        PREP_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PREP_HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _is_already_prepped(self, event_id):
        """Check if event already prepped"""
        return event_id in self.history['prepped_events']
    
    def _mark_as_prepped(self, event_id):
        """Mark event as prepped"""
        if event_id not in self.history['prepped_events']:
            self.history['prepped_events'].append(event_id)
            self._save_history()
    
    def _extract_lead_info(self, event):
        """
        Extract lead name and company from event
        
        For now, we'll use:
        - First external attendee as lead
        - Extract company from their email domain
        
        TODO: Could enhance with:
        - Parse from event description
        - Lookup from GoHighLevel
        - Check Airtable for lead info
        """
        attendees = event.get('attendees', [])
        
        if not attendees:
            print(f"   ⚠️  No attendees found - skipping")
            return None, None
        
        # Get first external attendee email
        lead_email = attendees[0]
        
        # Extract name from description or use "Lead"
        summary = event.get('summary', '')
        description = event.get('description', '')
        
        # Try to find name in title (e.g., "Discovery Call - John Smith")
        lead_name = None
        if ' - ' in summary:
            parts = summary.split(' - ')
            if len(parts) > 1:
                lead_name = parts[1].strip()
        
        # Try to extract company from email domain
        company_name = None
        if '@' in lead_email:
            domain = lead_email.split('@')[1]
            # Remove common TLDs and make it title case
            company_name = domain.split('.')[0].title()
        
        # Fallback
        if not lead_name:
            lead_name = lead_email.split('@')[0].replace('.', ' ').title()
        
        if not company_name:
            company_name = "Prospect Company"
        
        return lead_name, company_name, lead_email
    
    def run(self, dry_run=False):
        """
        Check calendar and auto-prep discovery calls
        
        Args:
            dry_run: If True, just show what would be prepped
        """
        print("🔍 AUTO-TRIGGER: Checking for discovery calls...")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Find discovery calls in next 14 days
        calls = self.calendar.find_discovery_calls(days_ahead=14)
        
        if not calls:
            print("   ✅ No upcoming discovery calls found")
            return
        
        print(f"   📅 Found {len(calls)} discovery call(s)\n")
        
        prepped_count = 0
        skipped_count = 0
        
        for call in calls:
            event_id = call['id']
            summary = call['summary']
            start_time = call['start']
            attendees = call['attendees']
            
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📅 {summary}")
            print(f"   Time: {start_time}")
            print(f"   Attendees: {', '.join(attendees) if attendees else 'None'}")
            
            # Check if already prepped
            if self._is_already_prepped(event_id):
                print(f"   ✅ Already prepped - skipping\n")
                skipped_count += 1
                continue
            
            # Check if description already has prep
            if '🎯 MEETING PREP' in call.get('description', ''):
                print(f"   ✅ Already has prep doc - marking as done\n")
                self._mark_as_prepped(event_id)
                skipped_count += 1
                continue
            
            # Check if meeting is too soon (less than 2 hours away)
            try:
                meeting_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                hours_until = (meeting_time - datetime.now(meeting_time.tzinfo)).total_seconds() / 3600
                
                if hours_until < 2:
                    print(f"   ⚠️  Meeting in {hours_until:.1f}h - too soon to prep\n")
                    skipped_count += 1
                    continue
            except Exception as e:
                print(f"   ⚠️  Could not parse meeting time: {e}")
            
            # Extract lead info
            result = self._extract_lead_info(call)
            if result is None:
                skipped_count += 1
                continue
            
            lead_name, company_name, lead_email = result
            
            print(f"   👤 Lead: {lead_name}")
            print(f"   🏢 Company: {company_name}")
            print(f"   📧 Email: {lead_email}")
            
            if dry_run:
                print(f"   🔍 DRY RUN - would prep this meeting\n")
                continue
            
            # RUN MEETING PREP
            print(f"\n   🚀 Running meeting prep...\n")
            
            try:
                prep_result = self.orchestrator.prep_meeting(
                    lead_name=lead_name,
                    company_name=company_name,
                    meeting_date=start_time,
                    event_id=event_id,
                    lead_email=lead_email  # Pass email for Autobound
                )
                
                # Mark as prepped
                self._mark_as_prepped(event_id)
                prepped_count += 1
                
                print(f"\n   ✅ Prep complete!")
                print(f"   📄 Report: {prep_result.get('report_url', 'N/A')}")
                print()
                
            except Exception as e:
                print(f"\n   ❌ Error during prep: {e}")
                print(f"   Skipping this meeting\n")
                skipped_count += 1
                continue
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n📊 SUMMARY:")
        print(f"   Total calls found: {len(calls)}")
        print(f"   Prepped: {prepped_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print()

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-trigger meeting prep for discovery calls")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be prepped without actually doing it")
    parser.add_argument('--reset-history', action='store_true', help="Clear prep history (re-prep all meetings)")
    
    args = parser.parse_args()
    
    trigger = AutoTrigger()
    
    if args.reset_history:
        print("🗑️  Resetting prep history...")
        trigger.history = {'prepped_events': []}
        trigger._save_history()
        print("   ✅ History cleared\n")
    
    trigger.run(dry_run=args.dry_run)

if __name__ == '__main__':
    main()
