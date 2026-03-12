#!/usr/bin/env python3
"""
AI-powered task breakdown - takes a task and generates intelligent subtasks.

Usage:
    python break_down_task.py "Build lead scraping automation"
    python break_down_task.py "Set up cold email campaign for Acme Corp" --create --list-id 12345
    python break_down_task.py --task-id abc123  # Break down existing ClickUp task
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd: str) -> tuple[int, str, str]:
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def mcporter_call(tool_call: str) -> dict:
    """Execute mcporter call."""
    cmd = f"mcporter call '{tool_call}'"
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        return None
    try:
        return json.loads(stdout)
    except:
        return {"raw": stdout}

# Task breakdown templates based on common patterns
BREAKDOWN_PATTERNS = {
    "automation": {
        "keywords": ["automation", "automate", "script", "bot", "scraper", "scraping"],
        "subtasks": [
            {"name": "Define requirements and success criteria", "time": "30m", "priority": 2},
            {"name": "Research tools, APIs, and libraries", "time": "1h", "priority": 2},
            {"name": "Set up development environment", "time": "30m", "priority": 2},
            {"name": "Build core functionality", "time": "3h", "priority": 1},
            {"name": "Add data validation and cleaning", "time": "1h", "priority": 2},
            {"name": "Implement error handling and retries", "time": "1h", "priority": 2},
            {"name": "Write tests", "time": "1h", "priority": 3},
            {"name": "Test with sample data", "time": "30m", "priority": 2},
            {"name": "Deploy and schedule", "time": "1h", "priority": 2},
            {"name": "Document usage and maintenance", "time": "30m", "priority": 3}
        ]
    },
    "campaign": {
        "keywords": ["campaign", "email", "outreach", "cold email", "marketing"],
        "subtasks": [
            {"name": "Define target audience (ICP)", "time": "30m", "priority": 2},
            {"name": "Build lead list", "time": "2h", "priority": 2},
            {"name": "Verify email addresses", "time": "30m", "priority": 2},
            {"name": "Write email sequence (4 emails)", "time": "2h", "priority": 1},
            {"name": "Create subject line variants for A/B testing", "time": "30m", "priority": 2},
            {"name": "Set up campaign in email tool", "time": "30m", "priority": 2},
            {"name": "Get client approval", "time": "30m", "priority": 1},
            {"name": "Launch campaign", "time": "15m", "priority": 1},
            {"name": "Set up reply handling workflow", "time": "30m", "priority": 2},
            {"name": "Schedule Week 1 review", "time": "15m", "priority": 3}
        ]
    },
    "website": {
        "keywords": ["website", "landing page", "web page", "site", "frontend"],
        "subtasks": [
            {"name": "Review brand guidelines", "time": "30m", "priority": 2},
            {"name": "Analyze competitor sites", "time": "1h", "priority": 3},
            {"name": "Create sitemap and wireframes", "time": "1h", "priority": 2},
            {"name": "Design homepage mockup", "time": "3h", "priority": 1},
            {"name": "Design key pages", "time": "3h", "priority": 2},
            {"name": "Get client feedback", "time": "30m", "priority": 1},
            {"name": "Build pages", "time": "6h", "priority": 1},
            {"name": "Add forms and integrations", "time": "2h", "priority": 2},
            {"name": "Set up SEO (meta, sitemap, schema)", "time": "1h", "priority": 2},
            {"name": "Speed optimization", "time": "1h", "priority": 2},
            {"name": "Final QA and testing", "time": "1h", "priority": 1},
            {"name": "Deploy and go live", "time": "30m", "priority": 1}
        ]
    },
    "integration": {
        "keywords": ["integration", "integrate", "connect", "api", "sync"],
        "subtasks": [
            {"name": "Document requirements and data flow", "time": "30m", "priority": 2},
            {"name": "Research API documentation", "time": "1h", "priority": 2},
            {"name": "Set up API credentials and access", "time": "30m", "priority": 2},
            {"name": "Build connection and authentication", "time": "1h", "priority": 1},
            {"name": "Implement data mapping", "time": "2h", "priority": 1},
            {"name": "Add error handling", "time": "1h", "priority": 2},
            {"name": "Test with real data", "time": "1h", "priority": 2},
            {"name": "Deploy integration", "time": "30m", "priority": 1},
            {"name": "Monitor and verify", "time": "30m", "priority": 2},
            {"name": "Document the integration", "time": "30m", "priority": 3}
        ]
    },
    "onboarding": {
        "keywords": ["onboard", "onboarding", "new client", "kickoff"],
        "subtasks": [
            {"name": "Schedule kickoff call", "time": "15m", "priority": 2},
            {"name": "Send welcome email with questionnaire", "time": "15m", "priority": 2},
            {"name": "Conduct kickoff call", "time": "1h", "priority": 1},
            {"name": "Collect all necessary access and logins", "time": "30m", "priority": 2},
            {"name": "Audit current state and workflows", "time": "2h", "priority": 2},
            {"name": "Create requirements document", "time": "1h", "priority": 2},
            {"name": "Design solution and timeline", "time": "2h", "priority": 1},
            {"name": "Get client sign-off on plan", "time": "30m", "priority": 1},
            {"name": "Set up project folder and tracking", "time": "30m", "priority": 2},
            {"name": "Begin implementation", "time": "varies", "priority": 1}
        ]
    },
    "research": {
        "keywords": ["research", "analyze", "evaluate", "compare", "investigate"],
        "subtasks": [
            {"name": "Define research questions", "time": "15m", "priority": 2},
            {"name": "Identify sources and methods", "time": "15m", "priority": 2},
            {"name": "Gather data and information", "time": "2h", "priority": 1},
            {"name": "Analyze findings", "time": "1h", "priority": 1},
            {"name": "Document key insights", "time": "30m", "priority": 2},
            {"name": "Create summary/recommendation", "time": "30m", "priority": 2},
            {"name": "Present findings", "time": "30m", "priority": 1}
        ]
    },
    "default": {
        "keywords": [],
        "subtasks": [
            {"name": "Clarify requirements and scope", "time": "30m", "priority": 2},
            {"name": "Plan approach", "time": "30m", "priority": 2},
            {"name": "Execute main work", "time": "varies", "priority": 1},
            {"name": "Review and quality check", "time": "30m", "priority": 2},
            {"name": "Deliver/complete", "time": "15m", "priority": 1}
        ]
    }
}

def detect_task_type(task_name: str) -> str:
    """Detect task type based on keywords."""
    task_lower = task_name.lower()
    
    for task_type, config in BREAKDOWN_PATTERNS.items():
        if task_type == "default":
            continue
        for keyword in config["keywords"]:
            if keyword in task_lower:
                return task_type
    
    return "default"

def generate_breakdown(task_name: str, task_type: str = None) -> list:
    """Generate subtask breakdown for a task."""
    if not task_type:
        task_type = detect_task_type(task_name)
    
    pattern = BREAKDOWN_PATTERNS.get(task_type, BREAKDOWN_PATTERNS["default"])
    
    subtasks = []
    for i, subtask in enumerate(pattern["subtasks"], 1):
        subtasks.append({
            "number": i,
            "name": subtask["name"],
            "time_estimate": subtask["time"],
            "priority": subtask["priority"],
            "description": f"Step {i} of {len(pattern['subtasks'])} for: {task_name}"
        })
    
    return subtasks, task_type

def calculate_total_time(subtasks: list) -> str:
    """Calculate total time estimate."""
    total_minutes = 0
    has_varies = False
    
    for subtask in subtasks:
        time = subtask["time_estimate"]
        if time == "varies":
            has_varies = True
            continue
        
        if "h" in time:
            hours = float(time.replace("h", ""))
            total_minutes += int(hours * 60)
        elif "m" in time:
            total_minutes += int(time.replace("m", ""))
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    result = ""
    if hours > 0:
        result += f"{hours}h "
    if minutes > 0:
        result += f"{minutes}m"
    
    if has_varies:
        result += " + variable"
    
    return result.strip()

def create_subtasks_in_clickup(parent_task_id: str, subtasks: list):
    """Create subtasks in ClickUp under a parent task."""
    # Get parent task to find list_id
    parent = mcporter_call(f'clickup.clickup_get_task(task_id: "{parent_task_id}")')
    if not parent:
        print(f"Error: Could not find task {parent_task_id}")
        return
    
    list_id = parent.get("list", {}).get("id")
    if not list_id:
        print("Error: Could not determine list for task")
        return
    
    print(f"\nCreating subtasks for: {parent.get('name')}")
    
    for subtask in subtasks:
        priority_map = {1: "urgent", 2: "high", 3: "normal", 4: "low"}
        priority = priority_map.get(subtask["priority"], "normal")
        
        desc = f"Time estimate: {subtask['time_estimate']}"
        
        result = mcporter_call(
            f'clickup.clickup_create_task('
            f'list_id: "{list_id}", '
            f'name: "{subtask["name"]}", '
            f'description: "{desc}", '
            f'priority: "{priority}", '
            f'parent: "{parent_task_id}"'
            f')'
        )
        
        if result and result.get("id"):
            print(f"  ✓ {subtask['name']}")
        else:
            print(f"  ✗ {subtask['name']}")

def create_task_with_subtasks(task_name: str, list_id: str, subtasks: list):
    """Create a new task with subtasks in ClickUp."""
    # Create parent task
    total_time = calculate_total_time(subtasks)
    desc = f"Total estimate: {total_time}\\n\\nAuto-generated breakdown with {len(subtasks)} subtasks"
    
    parent = mcporter_call(
        f'clickup.clickup_create_task('
        f'list_id: "{list_id}", '
        f'name: "{task_name}", '
        f'description: "{desc}", '
        f'priority: "high"'
        f')'
    )
    
    if not parent or not parent.get("id"):
        print(f"Error creating parent task: {parent}")
        return
    
    print(f"✓ Created parent task: {task_name}")
    
    # Create subtasks
    create_subtasks_in_clickup(parent["id"], subtasks)

def print_breakdown(task_name: str, subtasks: list, task_type: str):
    """Print breakdown in readable format."""
    total_time = calculate_total_time(subtasks)
    
    print(f"\n{'='*60}")
    print(f"Task: {task_name}")
    print(f"Type detected: {task_type}")
    print(f"Total estimate: {total_time}")
    print(f"{'='*60}\n")
    
    priority_labels = {1: "🔴 Urgent", 2: "🟠 High", 3: "🟡 Normal", 4: "🟢 Low"}
    
    for subtask in subtasks:
        pri = priority_labels.get(subtask["priority"], "Normal")
        print(f"  {subtask['number']:2}. {subtask['name']}")
        print(f"      Time: {subtask['time_estimate']} | Priority: {pri}")
        print()

def main():
    parser = argparse.ArgumentParser(description="AI-powered task breakdown")
    parser.add_argument("task", nargs="?", help="Task name to break down")
    parser.add_argument("--task-id", help="Existing ClickUp task ID to break down")
    parser.add_argument("--create", action="store_true", help="Create tasks in ClickUp")
    parser.add_argument("--list-id", help="ClickUp list ID (required with --create)")
    parser.add_argument("--type", choices=list(BREAKDOWN_PATTERNS.keys()),
                        help="Force task type (auto-detected if not specified)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Get task name
    task_name = args.task
    
    if args.task_id:
        task = mcporter_call(f'clickup.clickup_get_task(task_id: "{args.task_id}")')
        if task:
            task_name = task.get("name")
        else:
            print(f"Error: Could not find task {args.task_id}")
            return
    
    if not task_name:
        parser.print_help()
        print("\nExamples:")
        print('  python break_down_task.py "Build lead scraping automation"')
        print('  python break_down_task.py "Set up cold email campaign" --create --list-id 12345')
        print('  python break_down_task.py --task-id abc123')
        return
    
    # Generate breakdown
    subtasks, task_type = generate_breakdown(task_name, args.type)
    
    if args.json:
        print(json.dumps({
            "task": task_name,
            "type": task_type,
            "total_estimate": calculate_total_time(subtasks),
            "subtasks": subtasks
        }, indent=2))
        return
    
    # Print breakdown
    print_breakdown(task_name, subtasks, task_type)
    
    # Create in ClickUp if requested
    if args.create:
        if args.task_id:
            create_subtasks_in_clickup(args.task_id, subtasks)
        elif args.list_id:
            create_task_with_subtasks(task_name, args.list_id, subtasks)
        else:
            print("Error: --list-id required when creating new task (or use --task-id for existing)")

if __name__ == "__main__":
    main()
