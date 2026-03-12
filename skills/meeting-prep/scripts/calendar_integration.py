#!/usr/bin/env python3
"""
Calendar Integration for Meeting Prep
Adds Google Doc link to calendar events
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SERVICE_ACCOUNT_FILE = '/home/clawdbot/.config/google/service-account.json'
DELEGATED_USER = 'yasmine@smarterflo.com'

class CalendarIntegration:
    """Add meeting prep docs to calendar events"""
    
    def __init__(self):
        self.creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/calendar'],
            subject=DELEGATED_USER
        )
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def find_discovery_calls(self, days_ahead=14):
        """Find upcoming discovery calls"""
        now = datetime.utcnow()
        end = now + timedelta(days=days_ahead)
        
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime',
            q='discovery call'  # Search for "discovery call" in title
        ).execute()
        
        events = events_result.get('items', [])
        
        discovery_calls = []
        for event in events:
            # Extract attendees
            attendees = event.get('attendees', [])
            external_attendees = [
                a['email'] for a in attendees 
                if a.get('email') and a.get('email') != DELEGATED_USER
            ]
            
            discovery_calls.append({
                'id': event['id'],
                'summary': event.get('summary', 'Untitled'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'attendees': external_attendees,
                'description': event.get('description', '')
            })
        
        return discovery_calls
    
    def add_doc_to_event(self, event_id, doc_url, lead_name, company_name, custom_description=None):
        """Add meeting prep doc to calendar event"""
        
        # Get current event
        event = self.service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Update description with doc link
        current_desc = event.get('description', '')
        
        # Use custom description if provided, otherwise default
        if custom_description:
            new_section = custom_description
        else:
            new_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MEETING PREP - {lead_name} @ {company_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Research Report: {doc_url}

✅ Prep includes:
• Company overview & recent news
• Lead background & social activity
• Meeting agenda & talking points
• Industry context & insights

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{current_desc}
"""
        
        event['description'] = new_section.strip()
        
        # Update event
        updated_event = self.service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        print(f"   ✅ Added prep materials to calendar event: {event.get('summary')}")
        
        return updated_event
    
    def watch_and_prep(self):
        """Watch for new discovery calls and trigger prep"""
        print("🔍 Checking for upcoming discovery calls...")
        
        calls = self.find_discovery_calls()
        
        if not calls:
            print("   No upcoming discovery calls found")
            return []
        
        print(f"   Found {len(calls)} discovery call(s):")
        
        for call in calls:
            print(f"\n   📅 {call['summary']}")
            print(f"      Time: {call['start']}")
            print(f"      Attendees: {', '.join(call['attendees']) if call['attendees'] else 'None'}")
            
            # Check if already prepped
            if '🎯 MEETING PREP' in call['description']:
                print(f"      ✅ Already prepped - skipping")
            else:
                print(f"      ⏭️  Ready for prep")
        
        return calls

# Test
if __name__ == '__main__':
    integration = CalendarIntegration()
    
    # Find discovery calls
    calls = integration.watch_and_prep()
    
    if calls:
        print(f"\n💡 Run meeting prep for these calls:")
        for call in calls:
            if '🎯 MEETING PREP' not in call['description']:
                print(f"   • {call['summary']}")
