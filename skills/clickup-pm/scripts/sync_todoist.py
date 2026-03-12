#!/usr/bin/env python3
"""
Sync ClickUp tasks with Todoist.

Rules:
- ClickUp high-priority tasks → Todoist with @clickup label
- Tasks completed in Todoist @clickup → Mark complete in ClickUp
- Personal tasks (no @clickup) stay only in Todoist

Usage:
    python sync_todoist.py --push    # Push ClickUp tasks to Todoist
    python sync_todoist.py --pull    # Pull Todoist completions to ClickUp
    python sync_todoist.py --full    # Full bidirectional sync
    python sync_todoist.py --status  # Show sync status
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Todoist API
TODOIST_TOKEN = os.environ.get("TODOIST_API_TOKEN") or Path("~/.config/todoist/token").expanduser().read_text().strip()

def run_command(cmd: str) -> tuple[int, str, str]:
    """Run shell command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def mcporter_call(tool_call: str) -> dict:
    """Execute mcporter call and return result."""
    cmd = f"mcporter call '{tool_call}'"
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        print(f"mcporter error: {stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}

def todoist_api(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Call Todoist REST API."""
    import urllib.request
    import urllib.error
    
    url = f"https://api.todoist.com/rest/v2/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TODOIST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return {"success": True}
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Todoist API error: {e.code} - {e.read().decode()}", file=sys.stderr)
        return None

def get_clickup_tasks(priority_filter: list = None) -> list:
    """Get tasks from ClickUp that should sync to Todoist."""
    # Search for high priority tasks
    result = mcporter_call('clickup.clickup_search(keywords: "*", count: 100)')
    
    if not result or "results" not in result:
        return []
    
    tasks = []
    for item in result.get("results", []):
        if item.get("type") == "task":
            # Get full task details
            task_id = item.get("id")
            if task_id:
                task = mcporter_call(f'clickup.clickup_get_task(task_id: "{task_id}")')
                if task:
                    # Filter by priority if specified
                    priority = task.get("priority", {}).get("priority", 4)
                    if priority_filter and priority not in priority_filter:
                        continue
                    tasks.append(task)
    
    return tasks

def get_todoist_clickup_tasks() -> list:
    """Get Todoist tasks with @clickup label."""
    # Get labels
    labels = todoist_api("labels")
    clickup_label_id = None
    for label in labels or []:
        if label.get("name", "").lower() == "clickup":
            clickup_label_id = label.get("id")
            break
    
    if not clickup_label_id:
        print("Warning: @clickup label not found in Todoist")
        return []
    
    # Get tasks with this label
    tasks = todoist_api(f"tasks?label_id={clickup_label_id}")
    return tasks or []

def get_or_create_clickup_label() -> str:
    """Get or create @clickup label in Todoist."""
    labels = todoist_api("labels")
    for label in labels or []:
        if label.get("name", "").lower() == "clickup":
            return label.get("id")
    
    # Create label
    result = todoist_api("labels", method="POST", data={
        "name": "clickup",
        "color": "blue"
    })
    return result.get("id") if result else None

def get_business_project_id() -> str:
    """Get BUSINESS project ID in Todoist."""
    projects = todoist_api("projects")
    for project in projects or []:
        if project.get("name", "").upper() == "BUSINESS":
            return project.get("id")
    return None

def push_to_todoist(tasks: list):
    """Push ClickUp tasks to Todoist."""
    label_id = get_or_create_clickup_label()
    project_id = get_business_project_id()
    
    if not label_id:
        print("Error: Could not get @clickup label")
        return
    
    existing_tasks = get_todoist_clickup_tasks()
    existing_clickup_ids = set()
    
    # Extract ClickUp IDs from existing Todoist task descriptions
    for task in existing_tasks:
        desc = task.get("description", "")
        if "clickup_id:" in desc:
            cid = desc.split("clickup_id:")[1].split()[0]
            existing_clickup_ids.add(cid)
    
    created = 0
    skipped = 0
    
    for task in tasks:
        clickup_id = task.get("id")
        
        if clickup_id in existing_clickup_ids:
            skipped += 1
            continue
        
        # Create in Todoist
        task_data = {
            "content": task.get("name"),
            "description": f"From ClickUp\nclickup_id:{clickup_id}",
            "labels": ["clickup"],
            "priority": 4 - min(task.get("priority", {}).get("priority", 3), 3)  # Invert priority
        }
        
        if project_id:
            task_data["project_id"] = project_id
        
        if task.get("due_date"):
            task_data["due_date"] = task["due_date"][:10]
        
        result = todoist_api("tasks", method="POST", data=task_data)
        if result:
            print(f"  ✓ Created: {task.get('name')}")
            created += 1
        else:
            print(f"  ✗ Failed: {task.get('name')}")
    
    print(f"\nPush complete: {created} created, {skipped} already existed")

def pull_from_todoist():
    """Pull completions from Todoist back to ClickUp."""
    # Get completed tasks from Todoist with @clickup label
    # Note: Todoist REST API doesn't easily expose completed tasks
    # We'd need to use the Sync API for this
    
    print("Checking for completed @clickup tasks...")
    
    # For now, we check active tasks and their status
    tasks = get_todoist_clickup_tasks()
    
    completed = 0
    for task in tasks:
        # If task is completed in Todoist
        if task.get("is_completed"):
            desc = task.get("description", "")
            if "clickup_id:" in desc:
                clickup_id = desc.split("clickup_id:")[1].split()[0]
                
                # Update ClickUp task status
                result = mcporter_call(f'clickup.clickup_update_task(task_id: "{clickup_id}", status: "complete")')
                if result:
                    print(f"  ✓ Completed in ClickUp: {task.get('content')}")
                    completed += 1
    
    print(f"\nPull complete: {completed} tasks synced to ClickUp")

def show_status():
    """Show sync status between ClickUp and Todoist."""
    print("=== ClickUp ↔ Todoist Sync Status ===\n")
    
    # Get ClickUp tasks
    print("Fetching ClickUp tasks...")
    clickup_tasks = get_clickup_tasks(priority_filter=[1, 2])
    print(f"ClickUp high-priority tasks: {len(clickup_tasks)}")
    
    # Get Todoist @clickup tasks
    print("Fetching Todoist @clickup tasks...")
    todoist_tasks = get_todoist_clickup_tasks()
    print(f"Todoist @clickup tasks: {len(todoist_tasks)}")
    
    # Find unsynced
    todoist_clickup_ids = set()
    for task in todoist_tasks:
        desc = task.get("description", "")
        if "clickup_id:" in desc:
            cid = desc.split("clickup_id:")[1].split()[0]
            todoist_clickup_ids.add(cid)
    
    unsynced = []
    for task in clickup_tasks:
        if task.get("id") not in todoist_clickup_ids:
            unsynced.append(task)
    
    if unsynced:
        print(f"\n⚠️  {len(unsynced)} tasks not yet in Todoist:")
        for task in unsynced[:10]:
            print(f"   - {task.get('name')}")
        if len(unsynced) > 10:
            print(f"   ... and {len(unsynced) - 10} more")
    else:
        print("\n✅ All high-priority ClickUp tasks are synced to Todoist")

def main():
    parser = argparse.ArgumentParser(description="Sync ClickUp with Todoist")
    parser.add_argument("--push", action="store_true", help="Push ClickUp tasks to Todoist")
    parser.add_argument("--pull", action="store_true", help="Pull Todoist completions to ClickUp")
    parser.add_argument("--full", action="store_true", help="Full bidirectional sync")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--priority", type=int, nargs="+", default=[1, 2],
                        help="Priority levels to sync (1=urgent, 2=high, 3=normal, 4=low)")
    
    args = parser.parse_args()
    
    if not any([args.push, args.pull, args.full, args.status]):
        parser.print_help()
        return
    
    if args.status:
        show_status()
        return
    
    if args.push or args.full:
        print("=== Pushing ClickUp → Todoist ===")
        tasks = get_clickup_tasks(priority_filter=args.priority)
        print(f"Found {len(tasks)} tasks to consider")
        push_to_todoist(tasks)
    
    if args.pull or args.full:
        print("\n=== Pulling Todoist → ClickUp ===")
        pull_from_todoist()

if __name__ == "__main__":
    main()
