#!/usr/bin/env python3
"""
Get daily info from Google Workspace for Daily Digest
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

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'

def get_credentials(scopes):
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes,
        subject=DELEGATED_USER
    )

# Get Gmail summary
def get_gmail_summary():
    try:
        creds = get_credentials(['https://www.googleapis.com/auth/gmail.readonly'])
        service = build('gmail', 'v1', credentials=creds)
        
        profile = service.users().getProfile(userId='me').execute()
        unread_label = service.users().labels().get(userId='me', id='UNREAD').execute()
        unread_count = unread_label.get('messagesUnread', 0)
        
        return f"**{unread_count} unread messages** ({profile.get('messagesTotal')} total)"
    except:
        return "Unable to fetch email summary"

# Get today's calendar events
def get_calendar_events():
    try:
        creds = get_credentials(['https://www.googleapis.com/auth/calendar'])
        service = build('calendar', 'v3', credentials=creds)
        
        # Get today's events
        now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end = now + timedelta(days=1)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "*No events scheduled for today*"
        
        output = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            
            # Format time
            if 'T' in start:
                time_str = datetime.fromisoformat(start.replace('Z', '+00:00')).strftime('%I:%M %p')
                output.append(f"  - {time_str} - {summary}")
            else:
                output.append(f"  - All day - {summary}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Unable to fetch calendar events: {str(e)[:50]}"

# Main
if __name__ == '__main__':
    print("## 📧 Email Summary")
    print(get_gmail_summary())
    print()
    print("## 📆 Today's Calendar")
    print(get_calendar_events())
