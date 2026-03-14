#!/usr/bin/env python3
"""
Test Google Drive API access
"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    return credentials

def test_drive():
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        
        # List recent files
        results = service.files().list(
            pageSize=10,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        
        print(f"✅ Google Drive API working!")
        print(f"Recent files found: {len(files)}")
        
        if files:
            print("\n📁 Recent files:")
            for file in files:
                print(f"  - {file['name']} ({file['mimeType'].split('.')[-1]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_drive()
