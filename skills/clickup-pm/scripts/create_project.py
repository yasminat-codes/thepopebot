#!/usr/bin/env python3
"""
Create ClickUp project from template with optional Google Doc creation.

Usage:
    python create_project.py --template client_onboarding --name "Acme Corp"
    python create_project.py --template ai_automation --name "Lead Scraper" --client "Acme Corp"
    python create_project.py --template cold_email_campaign --name "Q1 Outreach" --space-id 12345
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

TEMPLATES_PATH = Path(__file__).parent.parent / "templates" / "projects.json"

def load_templates():
    """Load project templates from JSON."""
    with open(TEMPLATES_PATH) as f:
        return json.load(f)

def mcporter_call(tool_call: str) -> dict:
    """Execute mcporter call and return result."""
    cmd = f"mcporter call '{tool_call}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}

def get_workspace_hierarchy():
    """Get ClickUp workspace structure."""
    return mcporter_call("clickup.clickup_get_workspace_hierarchy(limit: 50)")

def find_or_create_space(hierarchy: dict, space_name: str = "Clients"):
    """Find existing space or return None."""
    if not hierarchy or "spaces" not in hierarchy:
        return None
    for space in hierarchy.get("spaces", []):
        if space.get("name", "").lower() == space_name.lower():
            return space
    return None

def create_folder(space_id: str, folder_name: str):
    """Create a folder in a space."""
    return mcporter_call(f'clickup.clickup_create_folder(space_id: "{space_id}", name: "{folder_name}")')

def create_list(folder_id: str = None, space_id: str = None, list_name: str = None):
    """Create a list in folder or space."""
    if folder_id:
        return mcporter_call(f'clickup.clickup_create_list_in_folder(folder_id: "{folder_id}", name: "{list_name}")')
    elif space_id:
        return mcporter_call(f'clickup.clickup_create_list(space_id: "{space_id}", name: "{list_name}")')
    return None

def create_task(list_id: str, name: str, description: str = "", priority: int = 3, time_estimate: str = None):
    """Create a task in a list."""
    # Priority: 1=urgent, 2=high, 3=normal, 4=low
    priority_map = {1: "urgent", 2: "high", 3: "normal", 4: "low"}
    pri = priority_map.get(priority, "normal")
    
    desc_escaped = description.replace('"', '\\"').replace('\n', '\\n')
    call = f'clickup.clickup_create_task(list_id: "{list_id}", name: "{name}", description: "{desc_escaped}", priority: "{pri}")'
    return mcporter_call(call)

def calculate_due_dates(phases: list, start_date: datetime = None):
    """Calculate due dates based on phase durations."""
    if not start_date:
        start_date = datetime.now()
    
    current_date = start_date
    for phase in phases:
        duration = phase.get("duration", "Week 1")
        # Parse duration
        if "week" in duration.lower():
            # Extract week number or range
            if "-" in duration:
                # "Weeks 3-4" -> 2 weeks
                parts = duration.lower().replace("weeks", "").replace("week", "").strip().split("-")
                weeks = int(parts[1]) - int(parts[0]) + 1
            else:
                weeks = 1
            phase["start_date"] = current_date
            phase["end_date"] = current_date + timedelta(weeks=weeks)
            current_date = phase["end_date"]
        elif "day" in duration.lower():
            if "-" in duration:
                parts = duration.lower().replace("days", "").replace("day", "").strip().split("-")
                days = int(parts[1]) - int(parts[0]) + 1
            else:
                days = 1
            phase["start_date"] = current_date
            phase["end_date"] = current_date + timedelta(days=days)
            current_date = phase["end_date"]
    
    return phases

def create_project(template_key: str, project_name: str, client_name: str = None, space_id: str = None):
    """Create a full project from template."""
    templates = load_templates()
    
    if template_key not in templates:
        print(f"Error: Template '{template_key}' not found.")
        print(f"Available templates: {', '.join(templates.keys())}")
        return False
    
    template = templates[template_key]
    
    # Get workspace structure
    print("Fetching workspace structure...")
    hierarchy = get_workspace_hierarchy()
    
    # Find Clients space if no space_id provided
    if not space_id:
        clients_space = find_or_create_space(hierarchy, "Clients")
        if clients_space:
            space_id = clients_space.get("id")
            print(f"Using 'Clients' space (ID: {space_id})")
        else:
            print("Error: No 'Clients' space found. Please provide --space-id")
            return False
    
    # Create project folder
    folder_name = f"{client_name} - {project_name}" if client_name else project_name
    print(f"Creating folder: {folder_name}")
    folder = create_folder(space_id, folder_name)
    
    if not folder or "id" not in folder:
        print(f"Error creating folder: {folder}")
        return False
    
    folder_id = folder["id"]
    print(f"Created folder (ID: {folder_id})")
    
    # Calculate due dates
    phases = calculate_due_dates(template["phases"])
    
    # Create lists and tasks for each phase
    created_tasks = []
    for phase in phases:
        print(f"\nCreating phase: {phase['name']} ({phase['duration']})")
        
        # Create list for phase
        list_result = create_list(folder_id=folder_id, list_name=phase["name"])
        if not list_result or "id" not in list_result:
            print(f"Error creating list: {list_result}")
            continue
        
        list_id = list_result["id"]
        print(f"  Created list (ID: {list_id})")
        
        # Create tasks
        for task in phase["tasks"]:
            description = task.get("description", "")
            if task.get("time_estimate"):
                description += f"\n\nTime estimate: {task['time_estimate']}"
            
            task_result = create_task(
                list_id=list_id,
                name=task["name"],
                description=description,
                priority=task.get("priority", 3),
                time_estimate=task.get("time_estimate")
            )
            
            if task_result and "id" in task_result:
                print(f"    ✓ {task['name']}")
                created_tasks.append(task_result)
            else:
                print(f"    ✗ {task['name']} - {task_result}")
    
    print(f"\n✅ Project created: {folder_name}")
    print(f"   Phases: {len(phases)}")
    print(f"   Tasks: {len(created_tasks)}")
    
    return True

def list_templates():
    """List available templates."""
    templates = load_templates()
    print("Available project templates:\n")
    for key, template in templates.items():
        phase_count = len(template["phases"])
        task_count = sum(len(p["tasks"]) for p in template["phases"])
        print(f"  {key}")
        print(f"    {template['name']}: {template['description']}")
        print(f"    {phase_count} phases, {task_count} tasks\n")

def main():
    parser = argparse.ArgumentParser(description="Create ClickUp project from template")
    parser.add_argument("--template", "-t", help="Template key (e.g., client_onboarding)")
    parser.add_argument("--name", "-n", help="Project name")
    parser.add_argument("--client", "-c", help="Client name (optional)")
    parser.add_argument("--space-id", "-s", help="ClickUp Space ID")
    parser.add_argument("--list", "-l", action="store_true", help="List available templates")
    
    args = parser.parse_args()
    
    if args.list:
        list_templates()
        return
    
    if not args.template or not args.name:
        parser.print_help()
        print("\nExamples:")
        print("  python create_project.py --list")
        print('  python create_project.py -t client_onboarding -n "Website Redesign" -c "Acme Corp"')
        print('  python create_project.py -t ai_automation -n "Lead Scraper"')
        return
    
    create_project(
        template_key=args.template,
        project_name=args.name,
        client_name=args.client,
        space_id=args.space_id
    )

if __name__ == "__main__":
    main()
