#!/usr/bin/env python3
"""
Resource Planning - Track capacity and workload across projects.

Features:
- Track capacity across all projects
- Warn when overbooked
- Suggest project scheduling
- Visualize workload distribution
- Balance work across time

Usage:
    python resource_planning.py                      # Show capacity overview
    python resource_planning.py --week               # This week's workload
    python resource_planning.py --forecast 4         # 4-week forecast
    python resource_planning.py --balance            # Suggest rebalancing
    python resource_planning.py --capacity 40        # Set weekly capacity (hours)

Cron: Run weekly for planning
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
CAPACITY_CONFIG = DATA_DIR / "capacity_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "weekly_capacity_hours": 40,
    "buffer_percent": 20,  # Keep 20% buffer
    "max_projects_concurrent": 5,
    "ideal_utilization": 80  # Aim for 80% utilization
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

def load_config() -> dict:
    """Load capacity config."""
    DATA_DIR.mkdir(exist_ok=True)
    if CAPACITY_CONFIG.exists():
        config = json.load(open(CAPACITY_CONFIG))
        return {**DEFAULT_CONFIG, **config}
    return DEFAULT_CONFIG

def save_config(config: dict):
    """Save capacity config."""
    with open(CAPACITY_CONFIG, "w") as f:
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

def parse_duration(duration_str) -> float:
    """Parse duration to hours."""
    if not duration_str:
        return 0
    
    if isinstance(duration_str, (int, float)):
        return duration_str / 3600000  # ms to hours
    
    import re
    hours = 0
    
    h_match = re.search(r'(\d+(?:\.\d+)?)\s*h', str(duration_str).lower())
    if h_match:
        hours += float(h_match.group(1))
    
    m_match = re.search(r'(\d+)\s*m', str(duration_str).lower())
    if m_match:
        hours += float(m_match.group(1)) / 60
    
    return hours

def get_task_week(due_date: datetime) -> int:
    """Get week number relative to today (0 = this week)."""
    if not due_date:
        return -1  # No due date
    
    today = datetime.now()
    today_week_start = today - timedelta(days=today.weekday())
    task_week_start = due_date - timedelta(days=due_date.weekday())
    
    delta = (task_week_start - today_week_start).days
    return delta // 7

def analyze_workload(tasks: list, weeks_ahead: int = 4) -> dict:
    """Analyze workload distribution."""
    config = load_config()
    
    analysis = {
        "config": config,
        "weeks": {},
        "by_client": defaultdict(lambda: {"hours": 0, "tasks": 0}),
        "unscheduled": {"hours": 0, "tasks": 0},
        "summary": {}
    }
    
    # Initialize weeks
    for i in range(weeks_ahead):
        week_start = datetime.now() + timedelta(weeks=i)
        week_start = week_start - timedelta(days=week_start.weekday())
        analysis["weeks"][i] = {
            "week_of": week_start.strftime("%Y-%m-%d"),
            "hours_scheduled": 0,
            "tasks_count": 0,
            "capacity": config["weekly_capacity_hours"],
            "utilization": 0,
            "status": "ok",
            "tasks": []
        }
    
    # Analyze tasks
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        
        # Skip completed tasks
        if status in ["complete", "closed", "done"]:
            continue
        
        due_date = parse_timestamp(task.get("due_date"))
        time_estimate = parse_duration(task.get("time_estimate", 0))
        client = task.get("folder", {}).get("name", "Unknown")
        
        task_info = {
            "name": task.get("name"),
            "client": client,
            "hours": time_estimate or 2,  # Default 2 hours if no estimate
            "priority": task.get("priority", {}).get("priority", 4)
        }
        
        # Categorize by week
        week_num = get_task_week(due_date)
        
        if week_num < 0 or week_num >= weeks_ahead:
            analysis["unscheduled"]["hours"] += task_info["hours"]
            analysis["unscheduled"]["tasks"] += 1
        else:
            analysis["weeks"][week_num]["hours_scheduled"] += task_info["hours"]
            analysis["weeks"][week_num]["tasks_count"] += 1
            analysis["weeks"][week_num]["tasks"].append(task_info)
        
        # Track by client
        analysis["by_client"][client]["hours"] += task_info["hours"]
        analysis["by_client"][client]["tasks"] += 1
    
    # Calculate utilization and status
    total_scheduled = 0
    total_capacity = 0
    overbooked_weeks = 0
    
    for week_num, week_data in analysis["weeks"].items():
        capacity = week_data["capacity"]
        scheduled = week_data["hours_scheduled"]
        
        utilization = (scheduled / capacity * 100) if capacity > 0 else 0
        week_data["utilization"] = round(utilization, 1)
        
        if utilization > 100:
            week_data["status"] = "overbooked"
            overbooked_weeks += 1
        elif utilization > config["ideal_utilization"]:
            week_data["status"] = "busy"
        elif utilization < 50:
            week_data["status"] = "light"
        else:
            week_data["status"] = "ok"
        
        total_scheduled += scheduled
        total_capacity += capacity
    
    # Summary
    avg_utilization = (total_scheduled / total_capacity * 100) if total_capacity > 0 else 0
    
    analysis["summary"] = {
        "total_hours_scheduled": round(total_scheduled, 1),
        "total_capacity": total_capacity,
        "average_utilization": round(avg_utilization, 1),
        "overbooked_weeks": overbooked_weeks,
        "active_clients": len(analysis["by_client"]),
        "unscheduled_hours": round(analysis["unscheduled"]["hours"], 1)
    }
    
    # Convert defaultdict
    analysis["by_client"] = dict(analysis["by_client"])
    
    return analysis

def suggest_rebalancing(analysis: dict) -> list:
    """Suggest how to rebalance workload."""
    suggestions = []
    config = analysis["config"]
    
    # Find overbooked and light weeks
    overbooked = []
    light = []
    
    for week_num, week_data in analysis["weeks"].items():
        if week_data["status"] == "overbooked":
            overbooked.append((week_num, week_data))
        elif week_data["status"] == "light":
            light.append((week_num, week_data))
    
    # Suggest moving tasks from overbooked to light weeks
    for ob_week, ob_data in overbooked:
        excess_hours = ob_data["hours_scheduled"] - ob_data["capacity"]
        
        for light_week, light_data in light:
            if light_week > ob_week:  # Only suggest moving to future weeks
                available = light_data["capacity"] * 0.8 - light_data["hours_scheduled"]
                
                if available > 0:
                    move_hours = min(excess_hours, available)
                    suggestions.append({
                        "type": "move_tasks",
                        "from_week": ob_week,
                        "to_week": light_week,
                        "hours": round(move_hours, 1),
                        "reason": f"Week {ob_week} is overbooked by {round(excess_hours, 1)}h"
                    })
                    excess_hours -= move_hours
                    
                    if excess_hours <= 0:
                        break
    
    # Suggest if unscheduled work is high
    if analysis["unscheduled"]["hours"] > config["weekly_capacity_hours"]:
        suggestions.append({
            "type": "schedule_backlog",
            "hours": round(analysis["unscheduled"]["hours"], 1),
            "reason": f"{round(analysis['unscheduled']['hours'], 1)}h of work has no due dates"
        })
    
    # Suggest if too many concurrent clients
    active_clients = len(analysis["by_client"])
    if active_clients > config["max_projects_concurrent"]:
        suggestions.append({
            "type": "reduce_concurrent",
            "current": active_clients,
            "max": config["max_projects_concurrent"],
            "reason": f"Working on {active_clients} clients, max recommended is {config['max_projects_concurrent']}"
        })
    
    return suggestions

def format_capacity_report(analysis: dict) -> str:
    """Format capacity report."""
    report = f"""# 📊 Resource Planning Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Configuration

| Setting | Value |
|---------|-------|
| Weekly Capacity | {analysis['config']['weekly_capacity_hours']}h |
| Target Utilization | {analysis['config']['ideal_utilization']}% |
| Max Concurrent Projects | {analysis['config']['max_projects_concurrent']} |

## Summary

| Metric | Value |
|--------|-------|
| Total Scheduled | {analysis['summary']['total_hours_scheduled']}h |
| Average Utilization | {analysis['summary']['average_utilization']}% |
| Active Clients | {analysis['summary']['active_clients']} |
| Unscheduled Work | {analysis['summary']['unscheduled_hours']}h |
| Overbooked Weeks | {analysis['summary']['overbooked_weeks']} |

## Weekly Breakdown

"""
    
    status_emoji = {
        "overbooked": "🔴",
        "busy": "🟡",
        "ok": "🟢",
        "light": "⚪"
    }
    
    for week_num in sorted(analysis["weeks"].keys()):
        week = analysis["weeks"][week_num]
        emoji = status_emoji.get(week["status"], "⚪")
        
        report += f"""### {emoji} Week {week_num} ({week['week_of']})

| Scheduled | Capacity | Utilization | Status |
|-----------|----------|-------------|--------|
| {week['hours_scheduled']:.1f}h | {week['capacity']}h | {week['utilization']}% | {week['status']} |

"""
        
        if week["tasks"] and week_num < 2:  # Show tasks for next 2 weeks
            report += "**Tasks:**\n"
            for task in week["tasks"][:5]:
                report += f"- {task['name']} ({task['hours']:.1f}h) - {task['client']}\n"
            if len(week["tasks"]) > 5:
                report += f"- ...and {len(week['tasks']) - 5} more\n"
            report += "\n"
    
    # By client
    report += "## Workload by Client\n\n"
    report += "| Client | Hours | Tasks |\n|--------|-------|-------|\n"
    
    for client, data in sorted(analysis["by_client"].items(), key=lambda x: x[1]["hours"], reverse=True):
        report += f"| {client} | {data['hours']:.1f}h | {data['tasks']} |\n"
    
    return report

def format_suggestions(suggestions: list) -> str:
    """Format rebalancing suggestions."""
    if not suggestions:
        return "\n✅ Workload looks balanced!"
    
    report = "\n## 💡 Rebalancing Suggestions\n\n"
    
    for s in suggestions:
        if s["type"] == "move_tasks":
            report += f"- **Move {s['hours']}h** from Week {s['from_week']} to Week {s['to_week']}\n"
            report += f"  _{s['reason']}_\n\n"
        elif s["type"] == "schedule_backlog":
            report += f"- **Schedule backlog**: {s['hours']}h of unscheduled work\n"
            report += f"  _{s['reason']}_\n\n"
        elif s["type"] == "reduce_concurrent":
            report += f"- **Reduce concurrent projects**: {s['current']} → {s['max']}\n"
            report += f"  _{s['reason']}_\n\n"
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Resource Planning")
    parser.add_argument("--week", action="store_true", help="This week's workload")
    parser.add_argument("--forecast", type=int, default=4, help="Weeks to forecast")
    parser.add_argument("--balance", action="store_true", help="Suggest rebalancing")
    parser.add_argument("--capacity", type=int, help="Set weekly capacity (hours)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--alert", action="store_true", help="Alert if overbooked")
    
    args = parser.parse_args()
    
    # Update config if capacity specified
    if args.capacity:
        config = load_config()
        config["weekly_capacity_hours"] = args.capacity
        save_config(config)
        print(f"✅ Weekly capacity set to {args.capacity} hours")
        return
    
    print("Analyzing workload...", file=sys.stderr)
    
    tasks = get_all_tasks()
    analysis = analyze_workload(tasks, weeks_ahead=args.forecast)
    
    if args.json:
        print(json.dumps(analysis, indent=2, default=str))
        return
    
    if args.week:
        # Show just this week
        week = analysis["weeks"].get(0, {})
        print(f"\n📅 This Week's Workload\n")
        print(f"Scheduled: {week.get('hours_scheduled', 0):.1f}h / {week.get('capacity', 40)}h")
        print(f"Utilization: {week.get('utilization', 0)}%")
        print(f"Status: {week.get('status', 'unknown')}")
        
        if week.get("tasks"):
            print(f"\nTasks ({len(week['tasks'])}):")
            for task in week["tasks"][:10]:
                print(f"  - {task['name']} ({task['hours']:.1f}h)")
        return
    
    # Full report
    report = format_capacity_report(analysis)
    print(report)
    
    if args.balance:
        suggestions = suggest_rebalancing(analysis)
        print(format_suggestions(suggestions))
    
    # Alert if overbooked
    if args.alert and analysis["summary"]["overbooked_weeks"] > 0:
        print(f"\n⚠️ ALERT: {analysis['summary']['overbooked_weeks']} weeks are overbooked!")
        print("[Would send alert via Telegram]")

if __name__ == "__main__":
    main()
