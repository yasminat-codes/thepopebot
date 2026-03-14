#!/usr/bin/env python3
"""
Test Google Calendar with full scope
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'

# Try the main calendar scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

print(f"Testing Calendar API for: {DELEGATED_USER}")
print(f"Service Account: {SERVICE_ACCOUNT_FILE}")
print(f"Scopes: {SCOPES}")
print()

try:
    # Load service account
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        sa_data = json.load(f)
    
    print(f"Service Account Email: {sa_data['client_email']}")
    print(f"Client ID: {sa_data['client_id']}")
    print()
    
    # Create credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    
    print("Credentials created successfully")
    print(f"Delegating as: {DELEGATED_USER}")
    print()
    
    # Build service
    service = build('calendar', 'v3', credentials=credentials)
    
    print("Attempting to call Calendar API...")
    
    # Try to get calendar list
    result = service.calendarList().list().execute()
    
    print("✅ SUCCESS!")
    print(f"Calendars: {len(result.get('items', []))}")
    
except Exception as e:
    print(f"❌ FAILED")
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {str(e)}")
    
    # Try to get more details
    if hasattr(e, '__dict__'):
        print(f"Error attributes: {e.__dict__}")
