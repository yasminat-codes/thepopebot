#!/usr/bin/env python3
"""
Test Google Tasks API access
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
SCOPES = ['https://www.googleapis.com/auth/tasks']

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    return credentials

def test_tasks():
    try:
        creds = get_credentials()
        service = build('tasks', 'v1', credentials=creds)
        
        # List task lists
        tasklists = service.tasklists().list().execute()
        print(f"✅ Google Tasks API working!")
        print(f"Task lists found: {len(tasklists.get('items', []))}")
        
        for tasklist in tasklists.get('items', []):
            print(f"\n📋 List: {tasklist['title']}")
            
            # Get tasks from this list
            tasks = service.tasks().list(tasklist=tasklist['id']).execute()
            task_items = tasks.get('items', [])
            
            if task_items:
                for task in task_items[:5]:  # Show first 5
                    print(f"  - {task.get('title', 'No title')}")
            else:
                print("  (No tasks)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_tasks()
