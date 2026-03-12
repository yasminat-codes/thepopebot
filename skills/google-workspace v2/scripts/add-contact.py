#!/usr/bin/env python3
"""
Add contact to Google Contacts
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = ['https://www.googleapis.com/auth/contacts']

def add_contact(name, email, phone=None, location=None):
    """Add contact to Google Contacts"""
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    
    service = build('people', 'v1', credentials=creds)
    
    # Build contact
    contact = {
        'names': [{
            'givenName': name.split()[0],
            'familyName': ' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            'displayName': name
        }],
        'emailAddresses': [{
            'value': email,
            'type': 'work'
        }]
    }
    
    if phone:
        # Format phone
        clean_phone = ''.join(c for c in phone if c.isdigit())
        if len(clean_phone) == 10:
            formatted_phone = f'({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}'
        else:
            formatted_phone = phone
        
        contact['phoneNumbers'] = [{
            'value': formatted_phone,
            'type': 'mobile'
        }]
    
    if location:
        contact['addresses'] = [{
            'formattedValue': location,
            'type': 'home'
        }]
    
    try:
        result = service.people().createContact(body=contact).execute()
        print(f"✅ Contact added: {name}")
        print(f"   Email: {email}")
        if phone:
            print(f"   Phone: {formatted_phone}")
        if location:
            print(f"   Location: {location}")
        return result
    except Exception as e:
        print(f"❌ Failed to add contact: {str(e)}")
        return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='Full name')
    parser.add_argument('email', help='Email address')
    parser.add_argument('--phone', help='Phone number')
    parser.add_argument('--location', help='Location')
    
    args = parser.parse_args()
    
    add_contact(args.name, args.email, args.phone, args.location)
