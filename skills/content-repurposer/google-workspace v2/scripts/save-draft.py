#!/usr/bin/env python3
"""
Save email as draft in Gmail
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

import sys
import base64
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def save_draft(to_email, subject, body):
    """Save email as draft in Gmail"""
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(body)
    message['to'] = to_email
    message['from'] = DELEGATED_USER
    message['subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    draft = {
        'message': {
            'raw': raw
        }
    }
    
    try:
        result = service.users().drafts().create(userId='me', body=draft).execute()
        print(f"✅ Draft saved to Gmail!")
        print(f"   To: {to_email}")
        print(f"   Subject: {subject}")
        return result
    except Exception as e:
        print(f"❌ Failed to save draft: {str(e)}")
        return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('to', help='Recipient email')
    parser.add_argument('--subject', required=True)
    parser.add_argument('--body', required=True)
    
    args = parser.parse_args()
    
    save_draft(args.to, args.subject, args.body)
