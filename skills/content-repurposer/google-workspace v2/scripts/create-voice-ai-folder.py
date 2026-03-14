#!/usr/bin/env python3
"""Create Voice AI folder in Google Drive."""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    return credentials

def find_folder(service, name):
    """Find a folder by name."""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields='files(id, webViewLink)').execute()
    files = results.get('files', [])
    return files[0] if files else None

def create_folder(service, name):
    """Create a folder in Google Drive."""
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    return folder

def main():
    credentials = get_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Check if Voice AI folder exists
    folder = find_folder(drive_service, 'Voice AI')
    
    if folder:
        print(f"📁 Voice AI folder already exists!")
    else:
        folder = create_folder(drive_service, 'Voice AI')
        print(f"✅ Created Voice AI folder!")
    
    print(f"   Folder ID: {folder['id']}")
    
    # Get web view link
    file_info = drive_service.files().get(fileId=folder['id'], fields='webViewLink').execute()
    print(f"   Link: {file_info.get('webViewLink', 'N/A')}")
    
    return folder['id']

if __name__ == '__main__':
    main()
