#!/usr/bin/env python3
"""Get full details of specific emails"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
import sys

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=DELEGATED_USER
    )
    return credentials

def search_and_get_email(query):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # Search for emails matching query
    results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print(f"No emails found matching: {query}")
        return
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        print(f"📧 From: {from_addr}")
        print(f"📝 Subject: {subject}")
        print(f"📅 Date: {date}")
        print("-" * 60)
        
        # Get body
        payload = msg_data.get('payload', {})
        body = ""
        
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
                elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data') and not body:
                    # Fallback to HTML if no plain text
                    html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    # Simple HTML stripping
                    import re
                    body = re.sub('<[^<]+?>', '', html)
        
        # Print first 1500 chars of body
        if body:
            print("CONTENT:")
            print(body[:1500])
            if len(body) > 1500:
                print("... [truncated]")
        
        print("\n" + "=" * 60 + "\n")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = "is:unread from:zapmail"
    search_and_get_email(query)
