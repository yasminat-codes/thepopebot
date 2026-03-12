#!/usr/bin/env python3
"""Quick inbox check for urgent/client emails"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from datetime import datetime, timezone

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# Known categories
NEWSLETTERS = ['todoist', 'canva', 'substack', 'linkedin', 'mailchimp', 'constantcontact', 
               'hubspot', 'newsletter', 'digest', 'weekly', 'noreply', 'no-reply', 'skool',
               'circle.so', 'beehiiv', 'convertkit', 'drip', 'klaviyo']
CLIENTS = ['@', 'client', 'project']  # Will check manually

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=DELEGATED_USER
    )
    return credentials

def check_inbox():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # Get unread messages
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=50).execute()
    messages = results.get('messages', [])
    
    urgent = []
    leads = []
    newsletters = []
    other = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        email_lower = from_addr.lower()
        subject_lower = subject.lower()
        
        # Categorize
        is_newsletter = any(nl in email_lower for nl in NEWSLETTERS)
        is_urgent = any(w in subject_lower for w in ['urgent', 'asap', 'important', 'action required', 'time sensitive'])
        is_lead = any(w in subject_lower for w in ['inquiry', 'interested', 'demo', 'call', 'meeting', 'proposal', 'quote'])
        
        email_info = {
            'id': msg['id'],
            'from': from_addr[:60],
            'subject': subject[:80],
            'date': date
        }
        
        if is_urgent:
            urgent.append(email_info)
        elif is_lead:
            leads.append(email_info)
        elif is_newsletter:
            newsletters.append(email_info)
        else:
            other.append(email_info)
    
    # Print results
    print(f"📊 INBOX STATUS ({len(messages)} unread)")
    print("=" * 60)
    
    if urgent:
        print(f"\n🚨 URGENT ({len(urgent)}):")
        for e in urgent:
            print(f"  • {e['subject']}")
            print(f"    From: {e['from']}")
    
    if leads:
        print(f"\n🔥 LEADS/OPPORTUNITIES ({len(leads)}):")
        for e in leads:
            print(f"  • {e['subject']}")
            print(f"    From: {e['from']}")
    
    if newsletters:
        print(f"\n📰 NEWSLETTERS/NOTIFICATIONS ({len(newsletters)}):")
        for e in newsletters[:5]:
            print(f"  • {e['subject'][:50]}...")
        if len(newsletters) > 5:
            print(f"    ... and {len(newsletters) - 5} more")
    
    if other:
        print(f"\n📧 OTHER ({len(other)}):")
        for e in other[:10]:
            print(f"  • {e['subject']}")
            print(f"    From: {e['from']}")
        if len(other) > 10:
            print(f"    ... and {len(other) - 10} more")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  🚨 Urgent: {len(urgent)}")
    print(f"  🔥 Leads: {len(leads)}")
    print(f"  📰 Newsletters: {len(newsletters)}")
    print(f"  📧 Other: {len(other)}")
    
    return urgent, leads, newsletters, other

if __name__ == '__main__':
    check_inbox()
