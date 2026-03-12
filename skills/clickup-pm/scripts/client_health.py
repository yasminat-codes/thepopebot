#!/usr/bin/env python3
"""
Client Health Scoring - Track client satisfaction and flag at-risk clients.

Scoring Factors:
- Task completion rate (on-time vs late)
- Communication frequency
- Overdue tasks count
- Time since last interaction
- Project progress vs timeline

Health Levels:
- 🟢 Healthy (80-100): Everything on track
- 🟡 At Risk (50-79): Needs attention
- 🔴 Critical (0-49): Immediate action required

Usage:
    python client_health.py                    # Show all client health
    python client_health.py --client "Acme"    # Specific client
    python client_health.py --alert            # Alert on at-risk clients
    python client_health.py --json             # Output JSON

Cron: Run weekly on Sundays
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

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

def get_workspace_hierarchy() -> dict:
    """Get workspace structure."""
    return mcporter_call('clickup.clickup_get_workspace_hierarchy(limit: 100)')

def get_folder_tasks(folder_name: str) -> list:
    """Search for tasks in a specific folder/client."""
    result = mcporter_call(f'clickup.clickup_search(keywords: "{folder_name}", count: 100)')
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

def calculate_client_health(client_name: str, tasks: list) -> dict:
    """Calculate health score for a client."""
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    health = {
        "client": client_name,
        "score": 100,
        "level": "healthy",
        "factors": {},
        "issues": [],
        "recommendations": []
    }
    
    if not tasks:
        health["score"] = 50
        health["level"] = "at_risk"
        health["issues"].append("No tasks found - may need project setup")
        return health
    
    # Analyze tasks
    total_tasks = 0
    completed_tasks = 0
    overdue_tasks = 0
    completed_on_time = 0
    completed_late = 0
    active_tasks = 0
    blocked_tasks = 0
    recent_activity = False
    
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        total_tasks += 1
        
        due_date = parse_timestamp(task.get("due_date"))
        date_closed = parse_timestamp(task.get("date_closed"))
        date_updated = parse_timestamp(task.get("date_updated"))
        
        # Check for recent activity
        if date_updated and date_updated >= thirty_days_ago:
            recent_activity = True
        
        if status in ["complete", "closed", "done"]:
            completed_tasks += 1
            if due_date and date_closed:
                if date_closed <= due_date:
                    completed_on_time += 1
                else:
                    completed_late += 1
        else:
            active_tasks += 1
            if due_date and due_date < now:
                overdue_tasks += 1
            if "blocked" in status:
                blocked_tasks += 1
    
    # Calculate scores
    score = 100
    
    # Factor 1: On-time completion rate (30 points)
    if completed_tasks > 0:
        on_time_rate = completed_on_time / completed_tasks
        on_time_score = on_time_rate * 30
        health["factors"]["on_time_rate"] = f"{on_time_rate:.0%}"
        if on_time_rate < 0.7:
            health["issues"].append(f"Low on-time completion rate: {on_time_rate:.0%}")
            health["recommendations"].append("Review project timelines and capacity")
    else:
        on_time_score = 15  # Neutral if no completed tasks
        health["factors"]["on_time_rate"] = "N/A"
    
    score = on_time_score
    
    # Factor 2: Overdue tasks (25 points)
    if active_tasks > 0:
        overdue_rate = overdue_tasks / active_tasks
        overdue_score = (1 - overdue_rate) * 25
        health["factors"]["overdue_tasks"] = overdue_tasks
        if overdue_tasks > 0:
            health["issues"].append(f"{overdue_tasks} overdue tasks")
            health["recommendations"].append("Address overdue tasks immediately")
    else:
        overdue_score = 25
        health["factors"]["overdue_tasks"] = 0
    
    score += overdue_score
    
    # Factor 3: Blocked tasks (15 points)
    if active_tasks > 0:
        blocked_rate = blocked_tasks / active_tasks
        blocked_score = (1 - blocked_rate) * 15
        health["factors"]["blocked_tasks"] = blocked_tasks
        if blocked_tasks > 0:
            health["issues"].append(f"{blocked_tasks} blocked tasks")
            health["recommendations"].append("Unblock tasks to maintain momentum")
    else:
        blocked_score = 15
        health["factors"]["blocked_tasks"] = 0
    
    score += blocked_score
    
    # Factor 4: Recent activity (15 points)
    if recent_activity:
        activity_score = 15
        health["factors"]["recent_activity"] = "Yes"
    else:
        activity_score = 0
        health["factors"]["recent_activity"] = "No"
        health["issues"].append("No activity in the last 30 days")
        health["recommendations"].append("Schedule check-in with client")
    
    score += activity_score
    
    # Factor 5: Project progress (15 points)
    if total_tasks > 0:
        completion_rate = completed_tasks / total_tasks
        progress_score = completion_rate * 15
        health["factors"]["completion_rate"] = f"{completion_rate:.0%}"
    else:
        progress_score = 7.5
        health["factors"]["completion_rate"] = "N/A"
    
    score += progress_score
    
    # Final score and level
    health["score"] = round(score)
    
    if score >= 80:
        health["level"] = "healthy"
        health["emoji"] = "🟢"
    elif score >= 50:
        health["level"] = "at_risk"
        health["emoji"] = "🟡"
    else:
        health["level"] = "critical"
        health["emoji"] = "🔴"
    
    # Stats
    health["stats"] = {
        "total_tasks": total_tasks,
        "completed": completed_tasks,
        "active": active_tasks,
        "overdue": overdue_tasks,
        "blocked": blocked_tasks
    }
    
    return health

def get_all_clients(hierarchy: dict) -> list:
    """Get all client folders."""
    clients = []
    
    if not hierarchy:
        return clients
    
    for space in hierarchy.get("spaces", []):
        if space.get("name", "").lower() == "clients":
            for folder in space.get("folders", []):
                clients.append({
                    "name": folder.get("name"),
                    "id": folder.get("id"),
                    "lists": len(folder.get("lists", []))
                })
    
    return clients

def format_health_report(health_scores: list) -> str:
    """Format health report."""
    report = f"""# 🏥 Client Health Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary

"""
    
    # Count by level
    healthy = sum(1 for h in health_scores if h["level"] == "healthy")
    at_risk = sum(1 for h in health_scores if h["level"] == "at_risk")
    critical = sum(1 for h in health_scores if h["level"] == "critical")
    
    report += f"""| Level | Count |
|-------|-------|
| 🟢 Healthy | {healthy} |
| 🟡 At Risk | {at_risk} |
| 🔴 Critical | {critical} |

---

## Client Details

"""
    
    # Sort by score (lowest first)
    for health in sorted(health_scores, key=lambda x: x["score"]):
        report += f"""### {health['emoji']} {health['client']} - Score: {health['score']}/100

**Stats:** {health['stats']['completed']}/{health['stats']['total_tasks']} completed, {health['stats']['overdue']} overdue, {health['stats']['blocked']} blocked

"""
        
        if health["issues"]:
            report += "**Issues:**\n"
            for issue in health["issues"]:
                report += f"- {issue}\n"
            report += "\n"
        
        if health["recommendations"]:
            report += "**Recommendations:**\n"
            for rec in health["recommendations"]:
                report += f"- {rec}\n"
            report += "\n"
        
        report += "---\n\n"
    
    return report

def format_alert_message(at_risk_clients: list) -> str:
    """Format alert message for at-risk clients."""
    msg = "🏥 **Client Health Alert**\n\n"
    
    critical = [c for c in at_risk_clients if c["level"] == "critical"]
    at_risk = [c for c in at_risk_clients if c["level"] == "at_risk"]
    
    if critical:
        msg += "🔴 **CRITICAL:**\n"
        for client in critical:
            msg += f"• **{client['client']}** ({client['score']}/100)\n"
            if client["issues"]:
                msg += f"  └ {client['issues'][0]}\n"
        msg += "\n"
    
    if at_risk:
        msg += "🟡 **AT RISK:**\n"
        for client in at_risk:
            msg += f"• {client['client']} ({client['score']}/100)\n"
            if client["issues"]:
                msg += f"  └ {client['issues'][0]}\n"
    
    return msg

def main():
    parser = argparse.ArgumentParser(description="Client Health Scoring")
    parser.add_argument("--client", "-c", help="Check specific client")
    parser.add_argument("--alert", action="store_true", help="Alert on at-risk clients")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    print("Analyzing client health...", file=sys.stderr)
    
    # Get workspace
    hierarchy = get_workspace_hierarchy()
    
    if args.client:
        # Specific client
        tasks = get_folder_tasks(args.client)
        health = calculate_client_health(args.client, tasks)
        
        if args.json:
            print(json.dumps(health, indent=2))
        else:
            print(f"\n{health['emoji']} {health['client']}: {health['score']}/100 ({health['level']})")
            print(f"\nStats: {health['stats']}")
            if health["issues"]:
                print(f"\nIssues:")
                for issue in health["issues"]:
                    print(f"  - {issue}")
            if health["recommendations"]:
                print(f"\nRecommendations:")
                for rec in health["recommendations"]:
                    print(f"  - {rec}")
    else:
        # All clients
        clients = get_all_clients(hierarchy)
        health_scores = []
        
        for client in clients:
            print(f"  Checking {client['name']}...", file=sys.stderr)
            tasks = get_folder_tasks(client["name"])
            health = calculate_client_health(client["name"], tasks)
            health_scores.append(health)
        
        if args.json:
            print(json.dumps(health_scores, indent=2))
            return
        
        # Check for at-risk clients
        at_risk = [h for h in health_scores if h["level"] in ["at_risk", "critical"]]
        
        if args.alert and at_risk:
            alert_msg = format_alert_message(at_risk)
            print(alert_msg)
            print("\n[Would send via Telegram]")
        else:
            report = format_health_report(health_scores)
            print(report)
        
        # Exit code
        if any(h["level"] == "critical" for h in health_scores):
            sys.exit(2)
        elif at_risk:
            sys.exit(1)

if __name__ == "__main__":
    main()
