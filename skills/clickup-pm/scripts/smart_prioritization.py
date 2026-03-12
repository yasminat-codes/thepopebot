#!/usr/bin/env python3
"""
Smart Prioritization - AI-powered task priority suggestions.

Factors considered:
- Due date urgency
- Client importance/tier
- Dependencies
- Task complexity
- Business impact
- Current workload

Usage:
    python smart_prioritization.py                    # Show priority suggestions
    python smart_prioritization.py --today            # Today's priorities
    python smart_prioritization.py --apply            # Apply suggested priorities
    python smart_prioritization.py --client "Acme"    # Prioritize for specific client
    python smart_prioritization.py --strategy         # Show prioritization strategy

Cron: Run daily to suggest priorities
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
CLIENT_TIERS_FILE = DATA_DIR / "client_tiers.json"

# Default client tiers (higher = more important)
DEFAULT_TIERS = {
    "enterprise": 5,
    "premium": 4,
    "standard": 3,
    "starter": 2,
    "trial": 1
}

# Task type impact scores
TASK_IMPACT = {
    "milestone": 10,
    "client_facing": 8,
    "revenue": 9,
    "deadline": 7,
    "blocker": 9,
    "quick_win": 5,
    "admin": 2,
    "internal": 3
}

def run_command(cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run shell command."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout"

def mcporter_call(tool_call: str) -> dict:
    """Execute mcporter call."""
    cmd = f"mcporter call '{tool_call}'"
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        return {"error": stderr}
    try:
        return json.loads(stdout)
    except:
        return {"raw": stdout}

def load_client_tiers() -> dict:
    """Load client tier configuration."""
    DATA_DIR.mkdir(exist_ok=True)
    if CLIENT_TIERS_FILE.exists():
        return json.load(open(CLIENT_TIERS_FILE))
    return {"tiers": DEFAULT_TIERS, "clients": {}}

def save_client_tiers(config: dict):
    """Save client tiers."""
    with open(CLIENT_TIERS_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_all_tasks() -> list:
    """Get all active tasks."""
    result = mcporter_call('clickup.clickup_search(keywords: "*", count: 200)')
    if result and "results" in result:
        return [t for t in result["results"] if t.get("type") == "task"]
    return []

def parse_timestamp(ts) -> datetime:
    """Parse ClickUp timestamp."""
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts) / 1000)
    except:
        return None

def get_client_tier(client_name: str, config: dict) -> int:
    """Get client tier score."""
    # Check explicit assignment
    if client_name in config.get("clients", {}):
        tier_name = config["clients"][client_name]
        return config.get("tiers", DEFAULT_TIERS).get(tier_name, 3)
    
    # Default to standard
    return 3

def detect_task_type(task_name: str, task: dict) -> list:
    """Detect task types for scoring."""
    types = []
    name_lower = task_name.lower()
    
    # Check for various types
    if any(kw in name_lower for kw in ["launch", "go live", "delivery", "handoff"]):
        types.append("milestone")
    
    if any(kw in name_lower for kw in ["call", "meeting", "demo", "presentation", "training"]):
        types.append("client_facing")
    
    if any(kw in name_lower for kw in ["invoice", "payment", "proposal", "contract", "deal"]):
        types.append("revenue")
    
    if any(kw in name_lower for kw in ["blocked", "blocker", "waiting", "urgent"]):
        types.append("blocker")
    
    # Check tags
    for tag in task.get("tags", []):
        tag_name = tag.get("name", "").lower()
        if tag_name in ["urgent", "blocker", "vip"]:
            types.append("blocker")
    
    # Quick wins (low time estimate)
    time_estimate = task.get("time_estimate", 0)
    if time_estimate and int(time_estimate) < 1800000:  # Less than 30 min
        types.append("quick_win")
    
    if not types:
        types.append("internal")
    
    return types

def calculate_priority_score(task: dict, config: dict) -> dict:
    """Calculate priority score for a task."""
    now = datetime.now()
    
    score_breakdown = {
        "task_id": task.get("id"),
        "task_name": task.get("name"),
        "client": task.get("folder", {}).get("name", "Unknown"),
        "current_priority": task.get("priority", {}).get("priority", 4),
        "scores": {},
        "total_score": 0,
        "suggested_priority": 3
    }
    
    # 1. Due Date Urgency (0-30 points)
    due_date = parse_timestamp(task.get("due_date"))
    if due_date:
        hours_until_due = (due_date - now).total_seconds() / 3600
        
        if hours_until_due < 0:
            urgency_score = 30  # Overdue
        elif hours_until_due < 24:
            urgency_score = 25  # Due today
        elif hours_until_due < 48:
            urgency_score = 20  # Due tomorrow
        elif hours_until_due < 168:  # This week
            urgency_score = 15
        else:
            urgency_score = 5
    else:
        urgency_score = 10  # No due date, medium urgency
    
    score_breakdown["scores"]["urgency"] = urgency_score
    
    # 2. Client Tier (0-25 points)
    client_name = score_breakdown["client"]
    client_tier = get_client_tier(client_name, config)
    tier_score = client_tier * 5  # 5-25 points
    score_breakdown["scores"]["client_tier"] = tier_score
    
    # 3. Task Type Impact (0-20 points)
    task_types = detect_task_type(task.get("name", ""), task)
    impact_scores = [TASK_IMPACT.get(t, 3) for t in task_types]
    impact_score = min(max(impact_scores) * 2, 20)
    score_breakdown["scores"]["impact"] = impact_score
    score_breakdown["task_types"] = task_types
    
    # 4. Current Status (0-15 points)
    status = task.get("status", {}).get("status", "").lower()
    if "blocked" in status:
        status_score = 15  # High priority to unblock
    elif status in ["in progress", "doing"]:
        status_score = 10  # Keep momentum
    else:
        status_score = 5
    
    score_breakdown["scores"]["status"] = status_score
    
    # 5. Dependencies (0-10 points) - simplified
    # Would need dependency data from ClickUp
    dependency_score = 5  # Default
    score_breakdown["scores"]["dependencies"] = dependency_score
    
    # Calculate total
    total = sum(score_breakdown["scores"].values())
    score_breakdown["total_score"] = total
    
    # Map to priority (1=urgent, 2=high, 3=normal, 4=low)
    if total >= 70:
        score_breakdown["suggested_priority"] = 1  # Urgent
    elif total >= 55:
        score_breakdown["suggested_priority"] = 2  # High
    elif total >= 35:
        score_breakdown["suggested_priority"] = 3  # Normal
    else:
        score_breakdown["suggested_priority"] = 4  # Low
    
    return score_breakdown

def prioritize_tasks(tasks: list, limit: int = None) -> list:
    """Prioritize all tasks."""
    config = load_client_tiers()
    
    prioritized = []
    
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        
        # Skip completed tasks
        if status in ["complete", "closed", "done"]:
            continue
        
        score = calculate_priority_score(task, config)
        prioritized.append(score)
    
    # Sort by total score (highest first)
    prioritized.sort(key=lambda x: x["total_score"], reverse=True)
    
    if limit:
        prioritized = prioritized[:limit]
    
    return prioritized

def get_todays_priorities(tasks: list, max_tasks: int = 10) -> list:
    """Get prioritized tasks for today."""
    now = datetime.now()
    today_end = now.replace(hour=23, minute=59, second=59)
    
    # Filter to tasks due today or overdue
    today_tasks = []
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        if status in ["complete", "closed", "done"]:
            continue
        
        due_date = parse_timestamp(task.get("due_date"))
        if due_date and due_date <= today_end:
            today_tasks.append(task)
    
    # Prioritize
    prioritized = prioritize_tasks(today_tasks, limit=max_tasks)
    
    return prioritized

def format_priority_report(prioritized: list) -> str:
    """Format priority report."""
    report = f"""# 🎯 Smart Priority Suggestions
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Top Priorities

"""
    
    priority_names = {1: "🔴 URGENT", 2: "🟠 HIGH", 3: "🟡 NORMAL", 4: "🟢 LOW"}
    
    for i, task in enumerate(prioritized[:20], 1):
        current = priority_names.get(task["current_priority"], "Unknown")
        suggested = priority_names.get(task["suggested_priority"], "Unknown")
        change = "" if task["current_priority"] == task["suggested_priority"] else " → " + suggested
        
        report += f"""### {i}. {task['task_name'][:50]}

| Factor | Score |
|--------|-------|
| Urgency | {task['scores']['urgency']} |
| Client Tier | {task['scores']['client_tier']} |
| Impact | {task['scores']['impact']} |
| Status | {task['scores']['status']} |
| **Total** | **{task['total_score']}** |

- **Client:** {task['client']}
- **Current:** {current}{change}
- **Types:** {', '.join(task.get('task_types', []))}

---

"""
    
    return report

def format_today_priorities(priorities: list) -> str:
    """Format today's priorities."""
    if not priorities:
        return "\n✅ No urgent tasks for today!"
    
    report = f"""# 🎯 Today's Priorities
**{datetime.now().strftime('%A, %B %d, %Y')}**

"""
    
    priority_emoji = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢"}
    
    for i, task in enumerate(priorities, 1):
        emoji = priority_emoji.get(task["suggested_priority"], "⚪")
        report += f"{i}. {emoji} **{task['task_name'][:60]}**\n"
        report += f"   {task['client']} | Score: {task['total_score']}\n\n"
    
    return report

def show_strategy():
    """Show prioritization strategy."""
    strategy = """
# 📋 Prioritization Strategy

## Scoring Factors

| Factor | Max Points | Description |
|--------|------------|-------------|
| Urgency | 30 | Based on due date |
| Client Tier | 25 | VIP/Enterprise clients score higher |
| Impact | 20 | Milestones, revenue tasks score higher |
| Status | 15 | Blocked/in-progress items prioritized |
| Dependencies | 10 | Tasks blocking others |

## Priority Mapping

| Score Range | Priority | Action |
|-------------|----------|--------|
| 70+ | 🔴 Urgent | Do immediately |
| 55-69 | 🟠 High | Do today |
| 35-54 | 🟡 Normal | Do this week |
| <35 | 🟢 Low | Schedule for later |

## Client Tiers

| Tier | Score | Description |
|------|-------|-------------|
| Enterprise | 5 | Highest value clients |
| Premium | 4 | High-paying retainers |
| Standard | 3 | Regular clients |
| Starter | 2 | New/small clients |
| Trial | 1 | Prospects |

## Task Impact Types

| Type | Impact | Examples |
|------|--------|----------|
| milestone | 10 | Launch, delivery, go-live |
| revenue | 9 | Invoice, proposal, contract |
| blocker | 9 | Blocked items, urgent |
| client_facing | 8 | Meetings, demos, training |
| deadline | 7 | Has due date |
| quick_win | 5 | <30 min tasks |
| internal | 3 | Internal tasks |
| admin | 2 | Administrative work |
"""
    return strategy

def main():
    parser = argparse.ArgumentParser(description="Smart Prioritization")
    parser.add_argument("--today", action="store_true", help="Today's priorities")
    parser.add_argument("--apply", action="store_true", help="Apply suggested priorities")
    parser.add_argument("--client", "-c", help="Prioritize for specific client")
    parser.add_argument("--strategy", action="store_true", help="Show prioritization strategy")
    parser.add_argument("--set-tier", nargs=2, metavar=("CLIENT", "TIER"), help="Set client tier")
    parser.add_argument("--limit", type=int, default=20, help="Max tasks to show")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    if args.strategy:
        print(show_strategy())
        return
    
    if args.set_tier:
        client, tier = args.set_tier
        config = load_client_tiers()
        config["clients"][client] = tier
        save_client_tiers(config)
        print(f"✅ Set {client} to {tier} tier")
        return
    
    print("Analyzing priorities...", file=sys.stderr)
    tasks = get_all_tasks()
    
    if args.client:
        tasks = [t for t in tasks if args.client.lower() in t.get("folder", {}).get("name", "").lower()]
    
    if args.today:
        priorities = get_todays_priorities(tasks)
        
        if args.json:
            print(json.dumps(priorities, indent=2))
        else:
            print(format_today_priorities(priorities))
    else:
        priorities = prioritize_tasks(tasks, limit=args.limit)
        
        if args.json:
            print(json.dumps(priorities, indent=2))
        else:
            print(format_priority_report(priorities))
    
    if args.apply:
        print("\n[Would apply priorities via ClickUp API]")
        changes = 0
        for task in priorities:
            if task["current_priority"] != task["suggested_priority"]:
                changes += 1
        print(f"Would update {changes} task priorities")

if __name__ == "__main__":
    main()
