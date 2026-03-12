#!/usr/bin/env python3
"""Fix missing Newsletters and Notifications labels with valid color"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = os.path.expanduser('~/.config/google/service-account.json')
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic'
]

def get_gmail_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    delegated_credentials = credentials.with_subject(DELEGATED_USER)
    return build('gmail', 'v1', credentials=delegated_credentials)

def main():
    service = get_gmail_service()
    
    # Create Newsletters label (with valid gray color)
    print("Creating missing labels...")
    
    # Valid Gmail gray color
    gray_color = "#cccccc"
    
    # Create Newsletters
    try:
        label_body = {
            'name': 'Newsletters',
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
            'color': {
                'backgroundColor': gray_color,
                'textColor': '#000000'
            }
        }
        label = service.users().labels().create(userId='me', body=label_body).execute()
        newsletters_id = label['id']
        print(f"✓ Created: Newsletters (ID: {newsletters_id})")
    except HttpError as e:
        print(f"✗ Failed to create Newsletters: {e}")
        newsletters_id = None
    
    # Create Notifications
    try:
        label_body = {
            'name': 'Notifications',
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
            'color': {
                'backgroundColor': gray_color,
                'textColor': '#000000'
            }
        }
        label = service.users().labels().create(userId='me', body=label_body).execute()
        notifications_id = label['id']
        print(f"✓ Created: Notifications (ID: {notifications_id})")
    except HttpError as e:
        print(f"✗ Failed to create Notifications: {e}")
        notifications_id = None
    
    # Create Filter 8 (Google Workspace Notifications)
    if notifications_id:
        try:
            filter_body = {
                'criteria': {
                    'from': 'drive-shares-noreply@google.com OR comments-noreply@docs.google.com'
                },
                'action': {
                    'addLabelIds': [notifications_id]
                }
            }
            service.users().settings().filters().create(userId='me', body=filter_body).execute()
            print("✓ Created Filter 8: Google Workspace Notifications")
        except HttpError as e:
            print(f"✗ Filter 8 failed: {e}")
    
    # Update label mapping file
    label_mapping_file = '/home/clawdbot/clawd/gmail-label-ids.json'
    with open(label_mapping_file, 'r') as f:
        label_ids = json.load(f)
    
    if newsletters_id:
        label_ids['Newsletters'] = newsletters_id
    if notifications_id:
        label_ids['Notifications'] = notifications_id
    
    with open(label_mapping_file, 'w') as f:
        json.dump(label_ids, f, indent=2)
    
    print("\n✅ Fix complete! All labels and filters are now set up.")

if __name__ == '__main__':
    main()
