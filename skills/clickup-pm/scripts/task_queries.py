#!/usr/bin/env python3
"""
Natural Language Task Queries - Query ClickUp tasks using natural language
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Load config
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
SCHEMA_PATH = Path.home() / ".config/clickup/schema.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

with open(SCHEMA_PATH) as f:
    schema = json.load(f)

API_KEY = os.environ.get("CLICKUP_API_KEY", config["clickup"]["api_key"])
HEADERS = {"Authorization": API_KEY, "Content-Type": "application/json"}
WORKSPACE_ID = config["clickup"]["workspace_id"]


def get_tasks_by_filter(list_ids: list = None, statuses: list = None, 
                        due_date_gt: int = None, due_date_lt: int = None,
                        include_closed: bool = False) -> list:
    """Fetch tasks with filters"""
    url = f"https://api.clickup.com/api/v2/team/{WORKSPACE_ID}/task"
    
    params = {
        "include_closed": str(include_closed).lower(),
        "subtasks": "true"
    }
    
    if list_ids:
        params["list_ids[]"] = list_ids
    if statuses:
        params["statuses[]"] = statuses
    if due_date_gt:
        params["due_date_gt"] = due_date_gt
    if due_date_lt:
        params["due_date_lt"] = due_date_lt
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        return response.json().get("tasks", [])
    return []


def get_custom_field_value(task: dict, field_name: str) -> str:
    """Extract custom field value from task"""
    field_id = schema["custom_fields"].get(field_name, {}).get("id")
    if not field_id:
        return None
    
    for cf in task.get("custom_fields", []):
        if cf["id"] == field_id:
            if cf["type"] == "drop_down" and cf.get("value"):
                # Return the option name
                return cf.get("type_config", {}).get("options", [{}])[0].get("name", cf["value"])
            return cf.get("value")
    return None


def format_task(task: dict, include_details: bool = False) -> str:
    """Format a task for display"""
    name = task["name"]
    status = task["status"]["status"]
    priority = task.get("priority", {})
    priority_str = f"P{priority.get('priority', '?')}" if priority else ""
    
    # Due date
    due = ""
    if task.get("due_date"):
        due_dt = datetime.fromtimestamp(int(task["due_date"]) / 1000)
        due = due_dt.strftime("%m/%d")
    
    line = f"• {name}"
    if priority_str:
        line = f"• [{priority_str}] {name}"
    if due:
        line += f" (due {due})"
    
    if include_details:
        project = get_custom_field_value(task, "project")
        context = get_custom_field_value(task, "context")
        if project:
            line += f"\n  Project: {project}"
        if context:
            line += f" | Context: {context}"
    
    return line


# Query handlers
def query_today(include_overdue: bool = True) -> dict:
    """What's on my plate today?"""
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Get tasks due today
    tasks = get_tasks_by_filter(
        due_date_gt=int(start_of_day.timestamp() * 1000) - 1,
        due_date_lt=int(end_of_day.timestamp() * 1000)
    )
    
    # Also get overdue if requested
    overdue = []
    if include_overdue:
        overdue = get_tasks_by_filter(
            due_date_lt=int(start_of_day.timestamp() * 1000)
        )
    
    # Sort by priority
    def priority_sort(t):
        p = t.get("priority")
        if p and isinstance(p, dict):
            val = p.get("priority")
            if val is None:
                return 5
            if isinstance(val, int):
                return val
            # Map string priorities
            priority_map = {"urgent": 1, "high": 2, "normal": 3, "low": 4}
            return priority_map.get(str(val).lower(), 5)
        return 5
    
    tasks = sorted(tasks, key=priority_sort)
    overdue = sorted(overdue, key=priority_sort)
    
    return {
        "query": "today",
        "today_count": len(tasks),
        "overdue_count": len(overdue),
        "today": tasks,
        "overdue": overdue
    }


def query_blocking() -> dict:
    """What's blocking? (Waiting For items)"""
    waiting_list = config["clickup"]["default_lists"]["waiting_for"]
    
    url = f"https://api.clickup.com/api/v2/list/{waiting_list}/task"
    response = requests.get(url, headers=HEADERS, params={"include_closed": "false"})
    
    tasks = response.json().get("tasks", []) if response.status_code == 200 else []
    
    # Check for tasks with Waiting For field set
    all_tasks = get_tasks_by_filter()
    waiting_for_field = schema["custom_fields"]["waiting_for"]["id"]
    
    tasks_with_waiting = []
    for task in all_tasks:
        for cf in task.get("custom_fields", []):
            if cf["id"] == waiting_for_field and cf.get("value"):
                tasks_with_waiting.append({
                    **task,
                    "waiting_for": cf["value"]
                })
    
    return {
        "query": "blocking",
        "waiting_list_count": len(tasks),
        "waiting_field_count": len(tasks_with_waiting),
        "waiting_list": tasks,
        "waiting_field": tasks_with_waiting
    }


def query_revenue() -> dict:
    """Revenue-generating tasks"""
    all_tasks = get_tasks_by_filter()
    revenue_field = schema["custom_fields"]["revenue_generating"]["id"]
    
    revenue_tasks = []
    for task in all_tasks:
        for cf in task.get("custom_fields", []):
            if cf["id"] == revenue_field and cf.get("value") == True:
                revenue_tasks.append(task)
    
    # Also include tasks in Cold Outreach and Sales lists
    sales_lists = [
        config["clickup"]["default_lists"]["cold_outreach"],
        config["clickup"]["default_lists"]["sales_conversations"],
        config["clickup"]["default_lists"]["client_delivery"]
    ]
    
    sales_tasks = get_tasks_by_filter(list_ids=sales_lists)
    
    # Dedupe
    seen_ids = {t["id"] for t in revenue_tasks}
    for task in sales_tasks:
        if task["id"] not in seen_ids:
            revenue_tasks.append(task)
    
    return {
        "query": "revenue",
        "count": len(revenue_tasks),
        "tasks": revenue_tasks
    }


def query_quick_wins() -> dict:
    """Quick wins - low energy, short duration tasks"""
    all_tasks = get_tasks_by_filter()
    
    energy_field = schema["custom_fields"]["energy_levels"]["id"]
    time_field = schema["custom_fields"]["time_needed"]["id"]
    
    quick_wins = []
    for task in all_tasks:
        energy = None
        time_needed = None
        
        for cf in task.get("custom_fields", []):
            if cf["id"] == energy_field:
                # Check if low energy
                if cf.get("value"):
                    option_index = cf.get("value")
                    options = cf.get("type_config", {}).get("options", [])
                    for opt in options:
                        if opt.get("id") == option_index or opt.get("orderindex") == option_index:
                            if opt.get("name", "").lower() == "low":
                                energy = "low"
            
            if cf["id"] == time_field:
                if cf.get("value"):
                    option_index = cf.get("value")
                    options = cf.get("type_config", {}).get("options", [])
                    for opt in options:
                        if opt.get("id") == option_index:
                            name = opt.get("name", "")
                            if name in ["5mins", "15mins", "30mins"]:
                                time_needed = name
        
        # Include if either low energy OR quick time
        if energy == "low" or time_needed:
            quick_wins.append(task)
    
    return {
        "query": "quick_wins",
        "count": len(quick_wins),
        "tasks": quick_wins
    }


def query_deep_work() -> dict:
    """Deep work - high energy, long duration tasks"""
    all_tasks = get_tasks_by_filter()
    
    energy_field = schema["custom_fields"]["energy_levels"]["id"]
    
    deep_work = []
    for task in all_tasks:
        for cf in task.get("custom_fields", []):
            if cf["id"] == energy_field and cf.get("value"):
                options = cf.get("type_config", {}).get("options", [])
                for opt in options:
                    if opt.get("id") == cf["value"]:
                        if opt.get("name", "").lower() == "high":
                            deep_work.append(task)
    
    # Also include tasks tagged with deep-work
    for task in all_tasks:
        if any(t.get("name") == "deep-work" for t in task.get("tags", [])):
            if task["id"] not in [t["id"] for t in deep_work]:
                deep_work.append(task)
    
    return {
        "query": "deep_work",
        "count": len(deep_work),
        "tasks": deep_work
    }


def query_overdue() -> dict:
    """All overdue tasks"""
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    overdue = get_tasks_by_filter(
        due_date_lt=int(start_of_day.timestamp() * 1000)
    )
    
    return {
        "query": "overdue",
        "count": len(overdue),
        "tasks": overdue
    }


def query_this_week() -> dict:
    """Tasks due this week"""
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)
    
    tasks = get_tasks_by_filter(
        due_date_gt=int(start_of_week.timestamp() * 1000) - 1,
        due_date_lt=int(end_of_week.timestamp() * 1000)
    )
    
    return {
        "query": "this_week",
        "count": len(tasks),
        "tasks": tasks,
        "week_start": start_of_week.strftime("%m/%d"),
        "week_end": end_of_week.strftime("%m/%d")
    }


def query_stale() -> dict:
    """Stale tasks - in planning for 7+ days, or no updates in 14+ days"""
    all_tasks = get_tasks_by_filter()
    
    now = datetime.now()
    stale_threshold = now - timedelta(days=7)
    very_stale_threshold = now - timedelta(days=14)
    
    stale = []
    for task in all_tasks:
        status = task["status"]["status"].lower()
        
        # Check if in planning for too long
        if status == "planning":
            updated = datetime.fromtimestamp(int(task["date_updated"]) / 1000)
            if updated < stale_threshold:
                stale.append({**task, "stale_reason": "In planning 7+ days"})
                continue
        
        # Check if no updates in 14+ days
        updated = datetime.fromtimestamp(int(task["date_updated"]) / 1000)
        if updated < very_stale_threshold:
            stale.append({**task, "stale_reason": "No updates 14+ days"})
    
    return {
        "query": "stale",
        "count": len(stale),
        "tasks": stale
    }


# Natural language parser
QUERY_PATTERNS = {
    r"(what.*(today|plate|do today|on tap))": query_today,
    r"(block|waiting|stuck|held up)": query_blocking,
    r"(revenue|money|sales|client|billable)": query_revenue,
    r"(quick|fast|easy|low.energy|5.min|15.min)": query_quick_wins,
    r"(deep.work|focus|high.energy|concentrate)": query_deep_work,
    r"(overdue|late|missed|past.due)": query_overdue,
    r"(this.week|weekly|week)": query_this_week,
    r"(stale|old|forgotten|neglected)": query_stale,
}


def parse_query(query: str) -> dict:
    """Parse natural language query and execute"""
    query_lower = query.lower()
    
    for pattern, handler in QUERY_PATTERNS.items():
        if re.search(pattern, query_lower):
            return handler()
    
    # Default to today
    return query_today()


def format_query_result(result: dict) -> str:
    """Format query result for display"""
    query_type = result.get("query", "unknown")
    lines = []
    
    if query_type == "today":
        lines.append(f"📋 **Today's Tasks** ({result['today_count']})")
        if result["overdue_count"] > 0:
            lines.append(f"⚠️ Plus {result['overdue_count']} overdue")
        lines.append("")
        
        if result["overdue"]:
            lines.append("**Overdue:**")
            for task in result["overdue"][:5]:
                lines.append(format_task(task))
            lines.append("")
        
        if result["today"]:
            lines.append("**Due Today:**")
            for task in result["today"][:10]:
                lines.append(format_task(task))
        else:
            lines.append("No tasks due today.")
    
    elif query_type == "blocking":
        total = result["waiting_list_count"] + result["waiting_field_count"]
        lines.append(f"🚧 **Blocking Items** ({total})")
        lines.append("")
        
        if result["waiting_list"]:
            lines.append("**Waiting For List:**")
            for task in result["waiting_list"][:5]:
                lines.append(format_task(task))
        
        if result["waiting_field"]:
            lines.append("\n**Tasks with Waiting For field:**")
            for task in result["waiting_field"][:5]:
                lines.append(f"• {task['name'][:40]}")
                lines.append(f"  ↳ Waiting on: {task['waiting_for']}")
    
    elif query_type == "revenue":
        lines.append(f"💰 **Revenue Tasks** ({result['count']})")
        lines.append("")
        for task in result["tasks"][:10]:
            lines.append(format_task(task))
    
    elif query_type == "quick_wins":
        lines.append(f"⚡ **Quick Wins** ({result['count']})")
        lines.append("_Low energy or under 30 mins_")
        lines.append("")
        for task in result["tasks"][:10]:
            lines.append(format_task(task))
    
    elif query_type == "deep_work":
        lines.append(f"🎯 **Deep Work** ({result['count']})")
        lines.append("_High energy, focus tasks_")
        lines.append("")
        for task in result["tasks"][:10]:
            lines.append(format_task(task))
    
    elif query_type == "overdue":
        lines.append(f"⏰ **Overdue Tasks** ({result['count']})")
        lines.append("")
        for task in result["tasks"][:10]:
            lines.append(format_task(task))
    
    elif query_type == "this_week":
        lines.append(f"📅 **This Week** ({result['count']})")
        lines.append(f"_{result['week_start']} - {result['week_end']}_")
        lines.append("")
        for task in result["tasks"][:10]:
            lines.append(format_task(task))
    
    elif query_type == "stale":
        lines.append(f"🕸️ **Stale Tasks** ({result['count']})")
        lines.append("_In planning 7+ days or no updates 14+ days_")
        lines.append("")
        for task in result["tasks"][:10]:
            reason = task.get("stale_reason", "")
            lines.append(f"• {task['name'][:35]}...")
            lines.append(f"  ↳ {reason}")
    
    if not lines:
        lines.append("No results found.")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Queries")
    parser.add_argument("query", nargs="?", default="today", help="Natural language query")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = parse_query(args.query)
    
    if args.json:
        # Remove task objects for cleaner JSON
        output = {k: v if k != "tasks" else len(v) for k, v in result.items()}
        print(json.dumps(output, indent=2))
    else:
        print(format_query_result(result))
