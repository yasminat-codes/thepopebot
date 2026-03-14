#!/usr/bin/env python3
"""Add Neon and HeyGen to Notifications filter"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.labels'
]

def get_gmail_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    delegated_credentials = credentials.with_subject(DELEGATED_USER)
    return build('gmail', 'v1', credentials=delegated_credentials)

def main():
    service = get_gmail_service()
    
    # Load label IDs
    with open('/home/clawdbot/clawd/gmail-label-ids.json', 'r') as f:
        label_ids = json.load(f)
    
    notifications_label_id = label_ids.get('Notifications')
    
    if not notifications_label_id:
        print("Error: Notifications label not found")
        return
    
    # Create filter for Neon and HeyGen
    print("Adding Neon and HeyGen to Notifications filter...")
    
    try:
        filter_body = {
            'criteria': {
                'from': 'neon.tech OR heygen.com'
            },
            'action': {
                'addLabelIds': [notifications_label_id],
                'removeLabelIds': ['INBOX', 'UNREAD']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("✓ Created filter: Neon and HeyGen → Auto-archive to Notifications")
    except HttpError as e:
        print(f"✗ Filter creation failed: {e}")

if __name__ == '__main__':
    main()
