#!/usr/bin/env python3
"""
Add task to Google Tasks
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
from datetime import datetime, timedelta

SERVICE_ACCOUNT_FILE = '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = ['https://www.googleapis.com/auth/tasks']

def add_task(title, notes=None, due_date=None):
    """Add task to Google Tasks"""
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    
    service = build('tasks', 'v1', credentials=creds)
    
    # Get default task list
    tasklists = service.tasklists().list().execute()
    tasklist_id = tasklists['items'][0]['id']
    
    # Build task
    task = {
        'title': title
    }
    
    if notes:
        task['notes'] = notes
    
    if due_date:
        task['due'] = due_date
    
    try:
        result = service.tasks().insert(
            tasklist=tasklist_id,
            body=task
        ).execute()
        print(f"✅ Task added: {title}")
        if notes:
            print(f"   Notes: {notes}")
        return result
    except Exception as e:
        print(f"❌ Failed to add task: {str(e)}")
        return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('title', help='Task title')
    parser.add_argument('--notes', help='Task notes')
    parser.add_argument('--due', help='Due date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    due_date = None
    if args.due:
        due_date = f"{args.due}T00:00:00.000Z"
    
    add_task(args.title, args.notes, due_date)
