#!/usr/bin/env python3
"""
Inbox Processor - Daily job to analyze GTD Inbox and suggest categorization
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests

# Import smart task detection
sys.path.insert(0, str(Path(__file__).parent))
from smart_task_create import detect_task_type, TASK_PATTERNS, suggest_tags

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
SCHEMA_PATH = Path.home() / ".config/clickup/schema.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

with open(SCHEMA_PATH) as f:
    schema = json.load(f)

API_KEY = os.environ.get("CLICKUP_API_KEY", config["clickup"]["api_key"])
HEADERS = {"Authorization": API_KEY, "Content-Type": "application/json"}
INBOX_LIST_ID = config["clickup"]["default_lists"]["inbox"]


def get_inbox_tasks() -> list:
    """Fetch all tasks from GTD Inbox"""
    url = f"https://api.clickup.com/api/v2/list/{INBOX_LIST_ID}/task"
    params = {"include_closed": "false"}
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        return response.json().get("tasks", [])
    return []


def analyze_task_fields(task: dict) -> dict:
    """Check which required fields are missing"""
    custom_fields = {cf["id"]: cf.get("value") for cf in task.get("custom_fields", [])}
    
    required_fields = {
        "project": schema["custom_fields"]["project"]["id"],
        "context": schema["custom_fields"]["context"]["id"],
        "energy_levels": schema["custom_fields"]["energy_levels"]["id"],
        "time_needed": schema["custom_fields"]["time_needed"]["id"]
    }
    
    missing = []
    for name, field_id in required_fields.items():
        value = custom_fields.get(field_id)
        # Check for None explicitly (0 is a valid value)
        if value is None:
            missing.append(name)
    
    return missing


def categorize_tasks(tasks: list) -> dict:
    """Analyze and categorize all inbox tasks"""
    categories = {
        "dev": [],
        "business360": [],
        "sales": [],
        "sop": [],
        "learning": [],
        "personal": [],
        "nursing": [],
        "uncategorized": []
    }
    
    missing_fields_count = 0
    analysis = []
    
    for task in tasks:
        task_name = task["name"]
        description = task.get("description", "") or ""
        
        # Detect type
        task_type = detect_task_type(task_name, description)
        detected = [k for k, v in TASK_PATTERNS.items() if v == task_type]
        detected_type = detected[0] if detected else "uncategorized"
        
        # Check missing fields
        missing = analyze_task_fields(task)
        if missing:
            missing_fields_count += 1
        
        # Suggest tags
        tags = suggest_tags(task_name)
        
        task_analysis = {
            "id": task["id"],
            "name": task_name,
            "detected_type": detected_type,
            "suggested_list": task_type["list"],
            "suggested_project": task_type["project"],
            "missing_fields": missing,
            "suggested_tags": tags,
            "current_status": task["status"]["status"],
            "priority": task.get("priority", {}).get("priority") if task.get("priority") else None
        }
        
        analysis.append(task_analysis)
        categories[detected_type].append(task_analysis)
    
    return {
        "total_tasks": len(tasks),
        "missing_fields_count": missing_fields_count,
        "categories": categories,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat()
    }


def generate_triage_report(result: dict) -> str:
    """Generate a human-readable triage report"""
    lines = []
    lines.append(f"📥 **GTD Inbox Triage Report**")
    lines.append(f"_{datetime.now().strftime('%B %d, %Y at %I:%M %p')}_")
    lines.append("")
    lines.append(f"**Total tasks:** {result['total_tasks']}")
    lines.append(f"**Missing required fields:** {result['missing_fields_count']}")
    lines.append("")
    
    # Category breakdown
    lines.append("**By Category:**")
    for cat, tasks in result["categories"].items():
        if tasks:
            lines.append(f"• {cat.replace('_', ' ').title()}: {len(tasks)}")
    lines.append("")
    
    # Top suggestions
    lines.append("**Suggested Moves:**")
    
    # Group by suggested list
    by_list = {}
    for task in result["analysis"]:
        suggested = task["suggested_list"]
        if suggested != "inbox":  # Only show moves away from inbox
            if suggested not in by_list:
                by_list[suggested] = []
            by_list[suggested].append(task["name"][:40])
    
    for list_name, task_names in by_list.items():
        lines.append(f"\n→ **{list_name.replace('_', ' ').title()}** ({len(task_names)}):")
        for name in task_names[:5]:  # Show first 5
            lines.append(f"  • {name}")
        if len(task_names) > 5:
            lines.append(f"  • ...and {len(task_names) - 5} more")
    
    # Tasks missing fields
    if result["missing_fields_count"] > 0:
        lines.append("")
        lines.append(f"**⚠️ {result['missing_fields_count']} tasks missing required fields**")
        missing_tasks = [t for t in result["analysis"] if t["missing_fields"]][:5]
        for task in missing_tasks:
            lines.append(f"• {task['name'][:35]}... (needs: {', '.join(task['missing_fields'])})")
    
    lines.append("")
    lines.append("Reply 'organize inbox' to auto-sort these tasks.")
    
    return "\n".join(lines)


def auto_organize_task(task_id: str, task_analysis: dict) -> dict:
    """Apply custom fields to task (ClickUp API can't move tasks between lists)"""
    suggested_list = task_analysis["suggested_list"]
    
    # NOTE: ClickUp API doesn't support moving tasks between lists
    # So we apply custom fields instead - users can filter by these fields
    
    task_type = TASK_PATTERNS.get(task_analysis["detected_type"], TASK_PATTERNS["personal"])
    
    custom_fields = []
    
    # Project field
    project_field = schema["custom_fields"]["project"]
    project_option = project_field.get("options", {}).get(task_analysis["suggested_project"])
    if project_option:
        custom_fields.append({"id": project_field["id"], "value": project_option})
    
    # Context field
    context_field = schema["custom_fields"]["context"]
    context_option = context_field.get("options", {}).get(task_type["context"])
    if context_option:
        custom_fields.append({"id": context_field["id"], "value": context_option})
    
    # Energy field
    energy_field = schema["custom_fields"]["energy_levels"]
    energy_option = energy_field.get("options", {}).get(task_type["energy"])
    if energy_option:
        custom_fields.append({"id": energy_field["id"], "value": energy_option})
    
    # Time field
    time_field = schema["custom_fields"]["time_needed"]
    time_option = time_field.get("options", {}).get(task_type["time"])
    if time_option:
        custom_fields.append({"id": time_field["id"], "value": time_option})
    
    # Update task with fields using custom_field endpoint
    fields_applied = []
    for cf in custom_fields:
        cf_url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{cf['id']}"
        response = requests.post(cf_url, headers=HEADERS, json={"value": cf["value"]})
        if response.status_code == 200:
            fields_applied.append(cf["id"])
    
    # Add tags
    tags_applied = []
    if task_analysis["suggested_tags"]:
        for tag in task_analysis["suggested_tags"]:
            tag_url = f"https://api.clickup.com/api/v2/task/{task_id}/tag/{tag}"
            response = requests.post(tag_url, headers=HEADERS)
            if response.status_code == 200:
                tags_applied.append(tag)
    
    return {
        "success": len(fields_applied) > 0,
        "task_id": task_id,
        "category": suggested_list,
        "fields_applied": len(fields_applied),
        "tags_applied": tags_applied
    }


def organize_all(dry_run: bool = True) -> dict:
    """Organize all inbox tasks"""
    tasks = get_inbox_tasks()
    result = categorize_tasks(tasks)
    
    organized = []
    skipped = []
    
    for task in result["analysis"]:
        if task["suggested_list"] != "inbox":
            if dry_run:
                organized.append({
                    "name": task["name"],
                    "move_to": task["suggested_list"],
                    "dry_run": True
                })
            else:
                org_result = auto_organize_task(task["id"], task)
                if org_result["success"]:
                    organized.append({
                        "name": task["name"],
                        "move_to": task["suggested_list"],
                        "success": True
                    })
                else:
                    skipped.append({
                        "name": task["name"],
                        "reason": org_result.get("reason", org_result.get("error"))
                    })
        else:
            skipped.append({
                "name": task["name"],
                "reason": "Stays in inbox"
            })
    
    return {
        "organized": len(organized),
        "skipped": len(skipped),
        "dry_run": dry_run,
        "details": organized
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inbox Processor")
    parser.add_argument("--report", action="store_true", help="Generate triage report")
    parser.add_argument("--organize", action="store_true", help="Auto-organize tasks")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.organize:
        result = organize_all(dry_run=args.dry_run)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            action = "Would organize" if args.dry_run else "Organized"
            print(f"{action} {result['organized']} tasks")
            print(f"Skipped: {result['skipped']}")
            if result['details']:
                print("\nDetails:")
                for item in result['details'][:10]:
                    print(f"  • {item['name'][:40]} → {item['move_to']}")
    else:
        # Default: generate report
        tasks = get_inbox_tasks()
        result = categorize_tasks(tasks)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            report = generate_triage_report(result)
            print(report)
