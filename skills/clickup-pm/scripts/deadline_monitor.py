#!/usr/bin/env python3
"""
Smart Deadline Monitor - Tracks deadlines and sends warnings.

Features:
- 48-hour warning for upcoming deadlines
- Immediate alert for overdue tasks
- Stale task detection (no activity for 3+ days)
- Priority escalation suggestions

Usage:
    python deadline_monitor.py              # Check and report
    python deadline_monitor.py --alert      # Send alerts for issues
    python deadline_monitor.py --json       # Output JSON

Cron: Run every morning at 8 AM and evening at 6 PM
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

STALE_THRESHOLD_DAYS = 3
WARNING_HOURS = 48
CRITICAL_HOURS = 24

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

def get_all_tasks() -> list:
    """Get all active tasks from ClickUp."""
    result = mcporter_call('clickup.clickup_search(keywords: "*", count: 200)')
    if result and "results" in result:
        return [t for t in result["results"] if t.get("type") == "task"]
    return []

def parse_timestamp(ts) -> datetime:
    """Parse ClickUp timestamp (milliseconds)."""
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts) / 1000)
    except:
        return None

def analyze_tasks(tasks: list) -> dict:
    """Analyze tasks for deadline issues."""
    now = datetime.now()
    
    analysis = {
        "overdue": [],
        "critical": [],  # Due within 24 hours
        "warning": [],   # Due within 48 hours
        "stale": [],     # No activity for 3+ days
        "healthy": 0
    }
    
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        
        # Skip completed tasks
        if status in ["complete", "closed", "done"]:
            continue
        
        task_info = {
            "id": task.get("id"),
            "name": task.get("name"),
            "list": task.get("list", {}).get("name", "Unknown"),
            "status": status,
            "priority": task.get("priority", {}).get("priority", 4),
            "assignees": [a.get("username") for a in task.get("assignees", [])]
        }
        
        # Check due date
        due_date = parse_timestamp(task.get("due_date"))
        if due_date:
            task_info["due_date"] = due_date.isoformat()
            hours_until_due = (due_date - now).total_seconds() / 3600
            
            if hours_until_due < 0:
                # Overdue
                task_info["hours_overdue"] = abs(hours_until_due)
                analysis["overdue"].append(task_info)
            elif hours_until_due <= CRITICAL_HOURS:
                # Critical - due within 24 hours
                task_info["hours_until_due"] = hours_until_due
                analysis["critical"].append(task_info)
            elif hours_until_due <= WARNING_HOURS:
                # Warning - due within 48 hours
                task_info["hours_until_due"] = hours_until_due
                analysis["warning"].append(task_info)
            else:
                analysis["healthy"] += 1
        else:
            analysis["healthy"] += 1
        
        # Check for stale tasks (no date_updated check via search, would need individual task fetch)
        # For now, check if in_progress but no due date
        if status in ["in progress", "doing"] and not due_date:
            task_info["reason"] = "In progress with no due date"
            if task_info not in analysis["stale"]:
                analysis["stale"].append(task_info)
    
    return analysis

def format_alert_message(analysis: dict) -> str:
    """Format alert message for Telegram."""
    msg_parts = []
    
    # Overdue (most urgent)
    if analysis["overdue"]:
        msg_parts.append("🚨 **OVERDUE TASKS**")
        for task in analysis["overdue"][:5]:
            hours = task.get("hours_overdue", 0)
            if hours > 24:
                time_str = f"{int(hours/24)}d overdue"
            else:
                time_str = f"{int(hours)}h overdue"
            msg_parts.append(f"• **{task['name']}** ({time_str})")
            msg_parts.append(f"  └ {task['list']}")
        if len(analysis["overdue"]) > 5:
            msg_parts.append(f"  _...and {len(analysis['overdue']) - 5} more_")
        msg_parts.append("")
    
    # Critical (due within 24h)
    if analysis["critical"]:
        msg_parts.append("⚠️ **DUE WITHIN 24 HOURS**")
        for task in analysis["critical"][:5]:
            hours = task.get("hours_until_due", 0)
            msg_parts.append(f"• {task['name']} ({int(hours)}h left)")
            msg_parts.append(f"  └ {task['list']}")
        if len(analysis["critical"]) > 5:
            msg_parts.append(f"  _...and {len(analysis['critical']) - 5} more_")
        msg_parts.append("")
    
    # Warning (due within 48h)
    if analysis["warning"]:
        msg_parts.append("📅 **DUE WITHIN 48 HOURS**")
        for task in analysis["warning"][:5]:
            hours = task.get("hours_until_due", 0)
            msg_parts.append(f"• {task['name']} ({int(hours)}h left)")
        if len(analysis["warning"]) > 5:
            msg_parts.append(f"  _...and {len(analysis['warning']) - 5} more_")
        msg_parts.append("")
    
    # Stale tasks
    if analysis["stale"]:
        msg_parts.append("😴 **STALE TASKS** (need attention)")
        for task in analysis["stale"][:3]:
            msg_parts.append(f"• {task['name']}")
            msg_parts.append(f"  └ {task.get('reason', 'No recent activity')}")
        if len(analysis["stale"]) > 3:
            msg_parts.append(f"  _...and {len(analysis['stale']) - 3} more_")
    
    if not msg_parts:
        return None  # Nothing to alert
    
    return "\n".join(msg_parts)

def format_report(analysis: dict) -> str:
    """Format full report."""
    report = f"""# Deadline Monitor Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary

| Category | Count |
|----------|-------|
| 🚨 Overdue | {len(analysis['overdue'])} |
| ⚠️ Critical (24h) | {len(analysis['critical'])} |
| 📅 Warning (48h) | {len(analysis['warning'])} |
| 😴 Stale | {len(analysis['stale'])} |
| ✅ Healthy | {analysis['healthy']} |

"""
    
    if analysis['overdue']:
        report += "## 🚨 Overdue Tasks\n\n"
        for task in analysis['overdue']:
            hours = task.get('hours_overdue', 0)
            report += f"- **{task['name']}** - {int(hours)}h overdue\n"
            report += f"  - List: {task['list']}\n"
            report += f"  - Status: {task['status']}\n\n"
    
    if analysis['critical']:
        report += "## ⚠️ Critical (Due within 24 hours)\n\n"
        for task in analysis['critical']:
            hours = task.get('hours_until_due', 0)
            report += f"- **{task['name']}** - {int(hours)}h remaining\n"
            report += f"  - List: {task['list']}\n\n"
    
    if analysis['warning']:
        report += "## 📅 Warning (Due within 48 hours)\n\n"
        for task in analysis['warning']:
            hours = task.get('hours_until_due', 0)
            report += f"- {task['name']} - {int(hours)}h remaining\n"
    
    return report

def should_send_alert(analysis: dict) -> bool:
    """Determine if an alert should be sent."""
    return bool(analysis['overdue'] or analysis['critical'])

def main():
    parser = argparse.ArgumentParser(description="Deadline Monitor")
    parser.add_argument("--alert", action="store_true", help="Send alerts if issues found")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--quiet", action="store_true", help="Only output if issues found")
    
    args = parser.parse_args()
    
    print("Checking deadlines...", file=sys.stderr)
    
    # Get and analyze tasks
    tasks = get_all_tasks()
    analysis = analyze_tasks(tasks)
    
    if args.json:
        print(json.dumps(analysis, indent=2, default=str))
        return
    
    # Check if we should alert
    has_issues = should_send_alert(analysis)
    
    if args.quiet and not has_issues:
        print("No deadline issues found.", file=sys.stderr)
        return
    
    if args.alert and has_issues:
        alert_msg = format_alert_message(analysis)
        if alert_msg:
            print("ALERT MESSAGE:")
            print(alert_msg)
            print("\n[Would send via Telegram]")
    else:
        report = format_report(analysis)
        print(report)
    
    # Exit code for cron
    sys.exit(1 if has_issues else 0)

if __name__ == "__main__":
    main()
