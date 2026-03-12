#!/usr/bin/env python3
"""
Smart Task Creation - Auto-detects task type and applies relevant fields
"""

import json
import os
import re
import sys
import requests
from pathlib import Path

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
SCHEMA_PATH = Path.home() / ".config/clickup/schema.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

with open(SCHEMA_PATH) as f:
    schema = json.load(f)

API_KEY = os.environ.get("CLICKUP_API_KEY", config["clickup"]["api_key"])
HEADERS = {"Authorization": API_KEY, "Content-Type": "application/json"}

# Task type detection patterns
TASK_PATTERNS = {
    "dev": {
        "keywords": ["build", "code", "develop", "implement", "api", "database", "backend", "frontend", "deploy", "debug", "fix bug", "refactor", "script", "automation"],
        "list": "internal_builds",
        "project": "dev_work",
        "context": "computer",
        "energy": "high",
        "time": "1hr",
        "fields": ["tool_system", "feature_module", "github_url"]
    },
    "business360": {
        "keywords": ["business360", "b360", "niche research", "market research", "orchestrator", "agent"],
        "list": "business360ai",
        "project": "business360ai",
        "context": "computer",
        "energy": "high",
        "time": "2hrs",
        "fields": ["feature_module", "sprint"]
    },
    "sales": {
        "keywords": ["lead", "prospect", "outreach", "cold email", "campaign", "pipeline", "deal", "proposal", "client", "meeting"],
        "list": "cold_outreach",
        "project": "cold_outreach",
        "context": "computer",
        "energy": "medium",
        "time": "30mins",
        "fields": ["pipeline_stage", "lead_source", "deal_value"]
    },
    "sop": {
        "keywords": ["sop", "document", "process", "procedure", "workflow", "template"],
        "list": "agency_sops",
        "project": "agency_sops",
        "context": "computer",
        "energy": "medium",
        "time": "1hr",
        "fields": ["sop_status"]
    },
    "learning": {
        "keywords": ["learn", "course", "watch", "study", "tutorial", "skool", "video", "read"],
        "list": "someday_maybe",
        "project": "learning",
        "context": "anywhere",
        "energy": "low",
        "time": "30mins",
        "fields": ["learning_format", "skill_category", "youtube_url"]
    },
    "personal": {
        "keywords": ["call", "family", "mom", "salman", "doctor", "appointment", "errand", "buy", "pick up"],
        "list": "inbox",
        "project": "personal_tasks",
        "context": "phone",
        "energy": "low",
        "time": "15mins",
        "fields": ["life_area"]
    },
    "nursing": {
        "keywords": ["shift", "nursing", "hospital", "patient", "clinic"],
        "list": "inbox",
        "project": "nursing",
        "context": "office",
        "energy": "high",
        "time": "3hrs_plus",
        "fields": ["shift_type", "location"]
    }
}

# Custom field ID mappings
FIELD_IDS = schema["custom_fields"]


def detect_task_type(task_name: str, description: str = "") -> dict:
    """Analyze task name/description and return detected type info"""
    text = f"{task_name} {description}".lower()
    
    scores = {}
    for task_type, patterns in TASK_PATTERNS.items():
        score = sum(1 for kw in patterns["keywords"] if kw in text)
        if score > 0:
            scores[task_type] = score
    
    if not scores:
        return TASK_PATTERNS["personal"]  # Default
    
    best_type = max(scores, key=scores.get)
    return TASK_PATTERNS[best_type]


def get_field_value(field_name: str, option_key: str) -> dict:
    """Get the custom field payload for a dropdown option"""
    field = FIELD_IDS.get(field_name, {})
    field_id = field.get("id")
    options = field.get("options", {})
    option_id = options.get(option_key)
    
    if field_id and option_id:
        return {"id": field_id, "value": option_id}
    elif field_id:
        return {"id": field_id, "value": option_key}
    return None


def build_custom_fields(task_type: dict) -> list:
    """Build the custom_fields array for task creation"""
    fields = []
    
    # Always add core fields
    if project := get_field_value("project", task_type["project"]):
        fields.append(project)
    
    if context := get_field_value("context", task_type["context"]):
        fields.append(context)
    
    if energy := get_field_value("energy_levels", task_type["energy"]):
        fields.append(energy)
    
    if time_needed := get_field_value("time_needed", task_type["time"]):
        fields.append(time_needed)
    
    return fields


def get_list_id(list_key: str) -> str:
    """Get list ID from key"""
    return config["clickup"]["default_lists"].get(list_key, config["clickup"]["default_lists"]["inbox"])


def suggest_tags(task_name: str) -> list:
    """Suggest tags based on task content"""
    tags = []
    text = task_name.lower()
    
    if any(kw in text for kw in ["email", "write", "draft", "document"]):
        tags.append("writing")
    if any(kw in text for kw in ["build", "code", "develop", "automation"]):
        tags.append("deep-work")
    if any(kw in text for kw in ["revenue", "client", "sales", "deal"]):
        tags.append("revenue-direct")
    if any(kw in text for kw in ["system", "setup", "configure", "integrate"]):
        tags.append("systems")
    
    return tags


def create_smart_task(task_name: str, description: str = "", override_list: str = None, priority: int = 3) -> dict:
    """Create a task with smart field detection"""
    
    # Detect task type
    task_type = detect_task_type(task_name, description)
    
    # Get list ID
    list_key = override_list or task_type["list"]
    list_id = get_list_id(list_key)
    
    # Build custom fields
    custom_fields = build_custom_fields(task_type)
    
    # Suggest tags
    tags = suggest_tags(task_name)
    
    # Build task payload
    payload = {
        "name": task_name,
        "description": description,
        "assignees": [int(config["clickup"]["member_id"])],
        "priority": priority,
        "status": "backlog",
        "custom_fields": custom_fields
    }
    
    if tags:
        payload["tags"] = tags
    
    # Create task
    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        task = response.json()
        return {
            "success": True,
            "task_id": task["id"],
            "task_name": task["name"],
            "list": list_key,
            "detected_type": [k for k, v in TASK_PATTERNS.items() if v == task_type][0],
            "fields_applied": ["project", "context", "energy_levels", "time_needed"],
            "tags": tags,
            "url": task["url"]
        }
    else:
        return {
            "success": False,
            "error": response.text
        }


def analyze_task(task_name: str, description: str = "") -> dict:
    """Analyze a task without creating it - returns what would be applied"""
    task_type = detect_task_type(task_name, description)
    detected = [k for k, v in TASK_PATTERNS.items() if v == task_type][0]
    
    return {
        "task_name": task_name,
        "detected_type": detected,
        "suggested_list": task_type["list"],
        "suggested_project": task_type["project"],
        "suggested_context": task_type["context"],
        "suggested_energy": task_type["energy"],
        "suggested_time": task_type["time"],
        "suggested_tags": suggest_tags(task_name),
        "additional_fields": task_type["fields"]
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Task Creation")
    parser.add_argument("task_name", help="Task name")
    parser.add_argument("-d", "--description", default="", help="Task description")
    parser.add_argument("-l", "--list", help="Override list (inbox, projects, cold_outreach, etc.)")
    parser.add_argument("-p", "--priority", type=int, default=3, help="Priority 1-4")
    parser.add_argument("--analyze", action="store_true", help="Analyze only, don't create")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.analyze:
        result = analyze_task(args.task_name, args.description)
    else:
        result = create_smart_task(args.task_name, args.description, args.list, args.priority)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if args.analyze:
            print(f"Task: {result['task_name']}")
            print(f"Detected Type: {result['detected_type']}")
            print(f"List: {result['suggested_list']}")
            print(f"Project: {result['suggested_project']}")
            print(f"Context: {result['suggested_context']}")
            print(f"Energy: {result['suggested_energy']}")
            print(f"Time: {result['suggested_time']}")
            print(f"Tags: {', '.join(result['suggested_tags']) or 'none'}")
        else:
            if result["success"]:
                print(f"✅ Created: {result['task_name']}")
                print(f"   List: {result['list']}")
                print(f"   Type: {result['detected_type']}")
                print(f"   Fields: {', '.join(result['fields_applied'])}")
                print(f"   URL: {result['url']}")
            else:
                print(f"❌ Error: {result['error']}")
