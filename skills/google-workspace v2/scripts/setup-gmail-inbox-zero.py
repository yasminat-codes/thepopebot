#!/usr/bin/env python3
"""
Gmail Inbox Zero Setup Script
Wipes existing labels and creates complete label + filter structure
"""
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

# Configuration
SERVICE_ACCOUNT_FILE = os.path.expanduser('~/.config/google/service-account.json')
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Label definitions
LABELS_TO_CREATE = [
    # Action labels
    {"name": "@Action", "color": "#fb4c2f", "textColor": "#ffffff"},
    {"name": "@Waiting", "color": "#ffad47", "textColor": "#ffffff"},
    {"name": "@Review", "color": "#4986e7", "textColor": "#ffffff"},
    
    # Client labels
    {"name": "Clients", "color": "#16a766", "textColor": "#ffffff"},
    {"name": "Clients/Active", "color": "#16a766", "textColor": "#ffffff"},
    {"name": "Clients/Past", "color": "#43d692", "textColor": "#ffffff"},
    
    # Lead labels
    {"name": "Leads", "color": "#a479e2", "textColor": "#ffffff"},
    {"name": "Leads/Hot", "color": "#a479e2", "textColor": "#ffffff"},
    {"name": "Leads/Cold", "color": "#b99aff", "textColor": "#ffffff"},
    
    # Category labels
    {"name": "Smarterflo", "color": "#f691b3", "textColor": "#ffffff"},
    {"name": "Nursing", "color": "#c9daf8", "textColor": "#000000"},
    
    # Auto-sort labels
    {"name": "Receipts", "color": "#b6cff5", "textColor": "#000000"},
    {"name": "Newsletters", "color": "#e3e3e3", "textColor": "#000000"},
    {"name": "Notifications", "color": "#e3e3e3", "textColor": "#000000"},
    {"name": "Scheduling", "color": "#a4c2f4", "textColor": "#000000"},
    
    # Reference labels
    {"name": "Reference", "color": "#f2b2a8", "textColor": "#000000"},
    {"name": "Reference/Contracts", "color": "#f2b2a8", "textColor": "#000000"},
    {"name": "Reference/Credentials", "color": "#f2b2a8", "textColor": "#000000"},
    {"name": "Reference/Templates", "color": "#f2b2a8", "textColor": "#000000"},
]

# System labels that should NOT be deleted
SYSTEM_LABELS = {
    'INBOX', 'SPAM', 'TRASH', 'UNREAD', 'STARRED', 'IMPORTANT',
    'SENT', 'DRAFT', 'CATEGORY_PERSONAL', 'CATEGORY_SOCIAL',
    'CATEGORY_PROMOTIONS', 'CATEGORY_UPDATES', 'CATEGORY_FORUMS'
}


def get_gmail_service():
    """Create Gmail API service instance"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    delegated_credentials = credentials.with_subject(DELEGATED_USER)
    return build('gmail', 'v1', credentials=delegated_credentials)


def delete_all_custom_labels(service):
    """Delete all user-created labels (not system labels)"""
    print("\n🗑️  Deleting existing custom labels...")
    
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        deleted_count = 0
        for label in labels:
            label_id = label['id']
            label_name = label['name']
            
            # Skip system labels
            if label_id in SYSTEM_LABELS or label['type'] == 'system':
                continue
            
            try:
                service.users().labels().delete(userId='me', id=label_id).execute()
                print(f"   ✓ Deleted: {label_name}")
                deleted_count += 1
            except HttpError as e:
                print(f"   ✗ Failed to delete {label_name}: {e}")
        
        print(f"\n   Total deleted: {deleted_count} labels")
        return deleted_count
        
    except HttpError as e:
        print(f"Error listing labels: {e}")
        return 0


def create_labels(service):
    """Create all labels defined in LABELS_TO_CREATE"""
    print("\n📝 Creating new labels...")
    
    created_labels = {}
    
    for label_def in LABELS_TO_CREATE:
        label_name = label_def['name']
        
        label_body = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
            'color': {
                'backgroundColor': label_def['color'],
                'textColor': label_def['textColor']
            }
        }
        
        try:
            label = service.users().labels().create(userId='me', body=label_body).execute()
            created_labels[label_name] = label['id']
            print(f"   ✓ Created: {label_name} (ID: {label['id']})")
        except HttpError as e:
            print(f"   ✗ Failed to create {label_name}: {e}")
    
    print(f"\n   Total created: {len(created_labels)} labels")
    return created_labels


def create_filters(service, label_ids):
    """Create all Gmail filters"""
    print("\n🔧 Creating filters...")
    
    # Note: Gmail API doesn't have a native filter creation endpoint
    # Filters must be created via settings.filters.create (Gmail v1)
    # Or we provide manual instructions
    
    filters_created = 0
    
    # Filter 1: Payment/Financial Receipts
    try:
        filter_body = {
            'criteria': {
                'from': 'stripe.com OR quickbooks.com OR pandadoc.com OR paypal.com OR wise.com OR mercury.com'
            },
            'action': {
                'addLabelIds': [label_ids.get('Receipts')],
                'removeLabelIds': ['INBOX', 'UNREAD']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 1: Payment/Financial Receipts")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 1 failed: {e}")
    
    # Filter 2: App Notifications
    try:
        filter_body = {
            'criteria': {
                'from': 'notion.so OR airtable.com OR todoist.com OR slack.com OR zapier.com OR n8n.io'
            },
            'action': {
                'addLabelIds': [label_ids.get('Notifications')],
                'removeLabelIds': ['INBOX', 'UNREAD']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 2: App Notifications")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 2 failed: {e}")
    
    # Filter 3: Newsletters
    try:
        filter_body = {
            'criteria': {
                'from': 'substack.com OR beehiiv.com OR convertkit.com OR mailchimp.com'
            },
            'action': {
                'addLabelIds': [label_ids.get('Newsletters')],
                'removeLabelIds': ['INBOX']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 3: Newsletters")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 3 failed: {e}")
    
    # Filter 4: Scheduling
    try:
        filter_body = {
            'criteria': {
                'from': 'calendly.com OR fathom.video OR calendar.google.com OR zoom.us'
            },
            'action': {
                'addLabelIds': [label_ids.get('Scheduling'), 'STARRED']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 4: Scheduling & Calendar")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 4 failed: {e}")
    
    # Filter 5: Receipts by Keywords
    try:
        filter_body = {
            'criteria': {
                'subject': 'invoice OR receipt OR "payment confirmation" OR "order confirmation"'
            },
            'action': {
                'addLabelIds': [label_ids.get('Receipts')]
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 5: Receipts by Keywords")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 5 failed: {e}")
    
    # Filter 6: Email Verification Tools
    try:
        filter_body = {
            'criteria': {
                'from': 'tomba.io OR muraena.io OR findymail.com OR icypeas.com OR voilanorbert.com OR reoon.com'
            },
            'action': {
                'addLabelIds': [label_ids.get('Notifications')],
                'removeLabelIds': ['INBOX', 'UNREAD']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 6: Email Verification Tools")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 6 failed: {e}")
    
    # Filter 7: LinkedIn Notifications
    try:
        filter_body = {
            'criteria': {
                'from': 'linkedin.com'
            },
            'action': {
                'addLabelIds': [label_ids.get('Notifications')],
                'removeLabelIds': ['INBOX', 'UNREAD']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 7: LinkedIn Notifications")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 7 failed: {e}")
    
    # Filter 8: Google Workspace Notifications
    try:
        filter_body = {
            'criteria': {
                'from': 'drive-shares-noreply@google.com OR comments-noreply@docs.google.com'
            },
            'action': {
                'addLabelIds': [label_ids.get('Notifications')]
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 8: Google Workspace Notifications")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 8 failed: {e}")
    
    # Filter 9: Contracts & Legal
    try:
        filter_body = {
            'criteria': {
                'subject': 'contract OR agreement OR NDA OR "scope of work" OR proposal',
                'hasAttachment': True
            },
            'action': {
                'addLabelIds': [label_ids.get('Reference/Contracts'), 'STARRED']
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 9: Contracts & Legal Documents")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 9 failed: {e}")
    
    # Filter 10: Credentials
    try:
        filter_body = {
            'criteria': {
                'subject': 'password OR login OR credentials OR "API key" OR "access token"'
            },
            'action': {
                'addLabelIds': [label_ids.get('Reference/Credentials')]
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 10: Credential/Login Information")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 10 failed: {e}")
    
    # Filter 11: Smarterflo Domain
    try:
        filter_body = {
            'criteria': {
                'from': 'smarterflo.com'
            },
            'action': {
                'addLabelIds': [label_ids.get('Smarterflo')]
            }
        }
        service.users().settings().filters().create(userId='me', body=filter_body).execute()
        print("   ✓ Filter 11: Smarterflo Domain")
        filters_created += 1
    except HttpError as e:
        print(f"   ✗ Filter 11 failed: {e}")
    
    print(f"\n   Total filters created: {filters_created}")
    return filters_created


def save_label_mapping(label_ids):
    """Save label ID mapping to file for future reference"""
    output_file = '/home/clawdbot/clawd/gmail-label-ids.json'
    
    with open(output_file, 'w') as f:
        json.dump(label_ids, f, indent=2)
    
    print(f"\n💾 Label ID mapping saved to: {output_file}")


def main():
    """Main execution"""
    print("=" * 60)
    print("Gmail Inbox Zero Setup")
    print("User: yasmine@smarterflo.com")
    print("=" * 60)
    
    # Get Gmail service
    service = get_gmail_service()
    
    # Step 1: Delete existing labels
    delete_all_custom_labels(service)
    
    # Step 2: Create new labels
    label_ids = create_labels(service)
    
    # Step 3: Create filters
    create_filters(service, label_ids)
    
    # Step 4: Save label mapping
    save_label_mapping(label_ids)
    
    print("\n" + "=" * 60)
    print("✅ Gmail setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review labels in Gmail")
    print("2. Test filters by sending test emails")
    print("3. Add client/lead email addresses to Filters 13-14 manually")
    print("4. Update Gmail settings (undo send, stars, templates)")
    print("5. Create canned response templates")
    print("\n")


if __name__ == '__main__':
    main()
