#!/usr/bin/env python3
"""
Test Google Calendar API access
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
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    return credentials

def test_calendar():
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        # List calendars
        calendars = service.calendarList().list().execute()
        print(f"✅ Google Calendar API working!")
        print(f"Calendars found: {len(calendars.get('items', []))}")
        
        # Get today's events
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"Today's events: {len(events)}")
        
        if events:
            print("\n📆 Today's schedule:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"  - {event.get('summary', 'No title')} at {start}")
        else:
            print("No events today")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_calendar()
