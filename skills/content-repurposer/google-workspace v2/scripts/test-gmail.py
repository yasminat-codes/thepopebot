#!/usr/bin/env python3
"""
Test Gmail API access with domain-wide delegation
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

# Config
SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_credentials():
    """Get delegated credentials for the user."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    return credentials

def test_gmail():
    """Test Gmail API access."""
    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Get profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Gmail API working!")
        print(f"Email: {profile.get('emailAddress')}")
        print(f"Messages Total: {profile.get('messagesTotal')}")
        print(f"Threads Total: {profile.get('threadsTotal')}")
        
        # Get unread count
        unread = service.users().labels().get(userId='me', id='UNREAD').execute()
        print(f"Unread Messages: {unread.get('messagesUnread', 0)}")
        
        # List recent messages
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])
        
        if messages:
            print(f"\n📧 Recent messages:")
            for msg in messages:
                msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
                headers = msg_data.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                print(f"  - {subject[:50]}... (from: {from_addr})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_gmail()
