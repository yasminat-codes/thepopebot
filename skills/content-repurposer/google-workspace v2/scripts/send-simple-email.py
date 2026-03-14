#!/usr/bin/env python3
"""
Send simple email via Gmail
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
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_email(to, subject, body):
    """Send email via Gmail"""
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    
    service = build('gmail', 'v1', credentials=creds)
    
    # Create message
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    message['from'] = DELEGATED_USER
    
    # Encode
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        
        print(f"✅ Email sent to {to}")
        print(f"   Subject: {subject}")
        return result
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('to', help='Recipient email')
    parser.add_argument('subject', help='Email subject')
    parser.add_argument('body', help='Email body')
    
    args = parser.parse_args()
    
    send_email(args.to, args.subject, args.body)
