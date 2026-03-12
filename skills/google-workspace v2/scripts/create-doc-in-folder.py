#!/usr/bin/env python3
"""Create a Google Doc in a specific folder with content."""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]
SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    return credentials

def create_doc_in_folder(drive_service, docs_service, title, folder_id, content):
    """Create a Google Doc in a specific folder with content."""
    
    # Create the document
    doc_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    
    doc = drive_service.files().create(body=doc_metadata, fields='id, webViewLink').execute()
    doc_id = doc['id']
    
    # Add content to the document
    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]
    
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()
    
    # Make it shareable (anyone with link can view)
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    drive_service.permissions().create(fileId=doc_id, body=permission).execute()
    
    # Get the shareable link
    file_info = drive_service.files().get(fileId=doc_id, fields='webViewLink').execute()
    
    return doc_id, file_info.get('webViewLink')

def main():
    if len(sys.argv) < 4:
        print("Usage: create-doc-in-folder.py <title> <folder_id> <content_file>")
        sys.exit(1)
    
    title = sys.argv[1]
    folder_id = sys.argv[2]
    content_file = sys.argv[3]
    
    with open(content_file, 'r') as f:
        content = f.read()
    
    credentials = get_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)
    docs_service = build('docs', 'v1', credentials=credentials)
    
    doc_id, link = create_doc_in_folder(drive_service, docs_service, title, folder_id, content)
    
    print(f"✅ Created document: {title}")
    print(f"   Doc ID: {doc_id}")
    print(f"   Shareable Link: {link}")

if __name__ == '__main__':
    main()
