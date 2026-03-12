#!/usr/bin/env python3
"""
Task Management Examples using Teable

Real-world integration examples for OpenClaw agents
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from common import client
from datetime import datetime, timedelta


# Configuration - replace with your table ID
TASKS_TABLE_ID = "tblYOUR_TASKS_TABLE_ID"  # Get from Teable URL


def get_my_tasks(agent_name: str):
    """
    Get all open tasks assigned to an agent
    
    Use in: Morning briefing
    """
    
    tasks = client.get_records(
        table_id=TASKS_TABLE_ID,
        filter_obj={
            "conjunction": "and",
            "conditions": [
                {"fieldId": "fldAssignedTo", "operator": "is", "value": agent_name},
                {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"}
            ]
        },
        order_by=[{"fieldId": "fldDueDate", "order": "asc"}]
    )
    
    print(f"\n📋 Tasks for {agent_name}: {len(tasks)} open\n")
    
    for task in tasks:
        fields = task['fields']
        title = fields.get('Title', 'Untitled')
        status = fields.get('Status', 'Unknown')
        priority = fields.get('Priority', 1)
        due_date = fields.get('Due Date', 'No deadline')
        
        priority_emoji = "🔴" if priority >= 3 else "🟡" if priority == 2 else "🟢"
        
        print(f"{priority_emoji} [{status}] {title}")
        print(f"   Due: {due_date}")
        print()


def get_overdue_tasks():
    """
    Get all overdue tasks across all agents
    
    Use in: Heartbeat checks
    """
    
    today = datetime.now().isoformat()
    
    tasks = client.get_records(
        table_id=TASKS_TABLE_ID,
        filter_obj={
            "conjunction": "and",
            "conditions": [
                {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"},
                {"fieldId": "fldDueDate", "operator": "isBefore", "value": today}
            ]
        }
    )
    
    if not tasks:
        print("✅ No overdue tasks")
        return
    
    print(f"\n⚠️  {len(tasks)} overdue task(s):\n")
    
    for task in tasks:
        fields = task['fields']
        title = fields.get('Title', 'Untitled')
        agent = fields.get('Assigned To', 'Unassigned')
        due_date = fields.get('Due Date', 'No deadline')
        
        print(f"• {title}")
        print(f"  Assigned to: {agent}")
        print(f"  Was due: {due_date}")
        print()


def create_task(
    title: str,
    assigned_to: str,
    priority: int = 1,
    due_date: str = None,
    description: str = "",
    project: str = None,
    tags: list = None
):
    """
    Create a new task
    
    Use in: Delegation workflows
    """
    
    fields = {
        "Title": title,
        "Assigned To": assigned_to,
        "Priority": priority,
        "Status": "Open",
        "Description": description
    }
    
    if due_date:
        fields["Due Date"] = due_date
    
    if project:
        fields["Project"] = project
    
    if tags:
        fields["Tags"] = tags
    
    result = client.create_records(
        table_id=TASKS_TABLE_ID,
        records=[{"fields": fields}],
        typecast=True
    )
    
    record_id = result['records'][0]['id']
    
    print(f"✅ Task created: {title}")
    print(f"   ID: {record_id}")
    print(f"   Assigned to: {assigned_to}")
    print(f"   Priority: {priority}")
    print(f"   Due: {due_date or 'No deadline'}")


def update_task_status(record_id: str, status: str, notes: str = ""):
    """
    Update task status
    
    Use in: Task completion workflows
    """
    
    fields = {"Status": status}
    
    if status == "Done":
        fields["Completed At"] = datetime.now().isoformat()
    
    if notes:
        fields["Notes"] = notes
    
    client.update_record(
        table_id=TASKS_TABLE_ID,
        record_id=record_id,
        fields=fields,
        typecast=True
    )
    
    print(f"✅ Task updated to: {status}")
    if notes:
        print(f"   Notes: {notes}")


def get_team_workload():
    """
    Get task distribution across all agents
    
    Use in: Weekly reports, team pulse checks
    """
    
    tasks = client.get_records(
        table_id=TASKS_TABLE_ID,
        filter_obj={
            "conjunction": "and",
            "conditions": [
                {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"}
            ]
        }
    )
    
    # Count tasks per agent
    workload = {}
    for task in tasks:
        agent = task['fields'].get('Assigned To', 'Unassigned')
        workload[agent] = workload.get(agent, 0) + 1
    
    print("\n📊 Team Workload:\n")
    
    for agent, count in sorted(workload.items(), key=lambda x: x[1], reverse=True):
        print(f"{agent}: {count} open tasks")


def get_high_priority_tasks():
    """
    Get all high-priority (3+) tasks
    
    Use in: Daily standups, urgent items check
    """
    
    tasks = client.get_records(
        table_id=TASKS_TABLE_ID,
        filter_obj={
            "conjunction": "and",
            "conditions": [
                {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"},
                {"fieldId": "fldPriority", "operator": "isGreaterEqual", "value": 3}
            ]
        },
        order_by=[{"fieldId": "fldPriority", "order": "desc"}]
    )
    
    print(f"\n🔴 High Priority Tasks: {len(tasks)}\n")
    
    for task in tasks:
        fields = task['fields']
        print(f"[P{fields.get('Priority', 1)}] {fields.get('Title', 'Untitled')}")
        print(f"    Assigned: {fields.get('Assigned To', 'Unassigned')}")
        print(f"    Due: {fields.get('Due Date', 'No deadline')}")
        print()


def bulk_create_campaign_tasks(campaign_name: str, agent: str):
    """
    Example: Create multiple related tasks for a campaign
    
    Use in: Campaign launches, project kickoffs
    """
    
    tasks = [
        {
            "fields": {
                "Title": f"{campaign_name} - Build lead list",
                "Assigned To": agent,
                "Priority": 4,
                "Due Date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "Project": campaign_name,
                "Tags": ["campaign", "research"]
            }
        },
        {
            "fields": {
                "Title": f"{campaign_name} - Write email sequences",
                "Assigned To": agent,
                "Priority": 4,
                "Due Date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "Project": campaign_name,
                "Tags": ["campaign", "copywriting"]
            }
        },
        {
            "fields": {
                "Title": f"{campaign_name} - Set up automation",
                "Assigned To": agent,
                "Priority": 3,
                "Due Date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                "Project": campaign_name,
                "Tags": ["campaign", "technical"]
            }
        },
        {
            "fields": {
                "Title": f"{campaign_name} - Monitor deliverability",
                "Assigned To": agent,
                "Priority": 2,
                "Due Date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "Project": campaign_name,
                "Tags": ["campaign", "monitoring"]
            }
        }
    ]
    
    result = client.create_records(
        table_id=TASKS_TABLE_ID,
        records=tasks,
        typecast=True
    )
    
    print(f"✅ Created {len(result['records'])} tasks for: {campaign_name}")
    print(f"   Assigned to: {agent}")


# Example usage
if __name__ == "__main__":
    print("Teable Task Management Examples")
    print("=" * 50)
    
    # Uncomment and run examples:
    
    # get_my_tasks("Aaliyah")
    # get_overdue_tasks()
    # create_task("Test task", "Aaliyah", priority=3, due_date="2026-02-25")
    # get_team_workload()
    # get_high_priority_tasks()
    # bulk_create_campaign_tasks("Financial Services Outreach", "Qamar")
    
    print("\nUpdate TASKS_TABLE_ID in this file to run examples")
