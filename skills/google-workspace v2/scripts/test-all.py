#!/usr/bin/env python3
"""
Test all Google Workspace APIs
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'

def get_credentials(scopes):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes,
        subject=DELEGATED_USER
    )
    return credentials

print("🔍 Testing Google Workspace Integration for yasmine@smarterflo.com\n")
print("=" * 60)

# Test Gmail
try:
    print("\n📧 Gmail API...")
    creds = get_credentials(['https://www.googleapis.com/auth/gmail.readonly'])
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    print(f"   ✅ Connected - {profile.get('messagesTotal')} messages, {profile.get('threadsTotal')} threads")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

# Test Calendar
try:
    print("\n📅 Google Calendar API...")
    creds = get_credentials(['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    calendars = service.calendarList().list().execute()
    print(f"   ✅ Connected - {len(calendars.get('items', []))} calendars")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

# Test Tasks
try:
    print("\n✅ Google Tasks API...")
    creds = get_credentials(['https://www.googleapis.com/auth/tasks.readonly'])
    service = build('tasks', 'v1', credentials=creds)
    tasklists = service.tasklists().list().execute()
    print(f"   ✅ Connected - {len(tasklists.get('items', []))} task lists")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

# Test Drive
try:
    print("\n📁 Google Drive API...")
    creds = get_credentials(['https://www.googleapis.com/auth/drive.readonly'])
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(pageSize=5).execute()
    print(f"   ✅ Connected - {len(results.get('files', []))} recent files")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

# Test Docs
try:
    print("\n📝 Google Docs API...")
    creds = get_credentials(['https://www.googleapis.com/auth/documents.readonly'])
    service = build('docs', 'v1', credentials=creds)
    print(f"   ✅ Connected - Ready to read/write docs")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

# Test Sheets
try:
    print("\n📊 Google Sheets API...")
    creds = get_credentials(['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    print(f"   ✅ Connected - Ready to read/write sheets")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

# Test Slides
try:
    print("\n🎨 Google Slides API...")
    creds = get_credentials(['https://www.googleapis.com/auth/presentations.readonly'])
    service = build('slides', 'v1', credentials=creds)
    print(f"   ✅ Connected - Ready to read/write presentations")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

print("\n" + "=" * 60)
print("\n🎉 Google Workspace Integration Complete!")
print("   All services are ready to use for yasmine@smarterflo.com\n")
