#!/usr/bin/env python3
"""
Weekly Project Digest - Generates and sends weekly status report.

Includes:
- Active projects and their status
- Tasks completed this week
- Upcoming deadlines (next 7 days)
- Overdue tasks
- Hours tracked per client
- Blockers/at-risk items

Usage:
    python weekly_digest.py                    # Generate digest
    python weekly_digest.py --send             # Generate and send via Telegram
    python weekly_digest.py --json             # Output as JSON

Cron: Run every Monday at 6 AM
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

def get_clickup_tasks() -> dict:
    """Get tasks from ClickUp."""
    # Search for all tasks
    result = mcporter_call('clickup.clickup_search(keywords: "*", count: 200)')
    return result

def get_workspace_hierarchy() -> dict:
    """Get workspace structure."""
    return mcporter_call('clickup.clickup_get_workspace_hierarchy(limit: 100)')

def categorize_tasks(tasks: list) -> dict:
    """Categorize tasks by status and due date."""
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    week_ahead = now + timedelta(days=7)
    
    categorized = {
        "completed_this_week": [],
        "overdue": [],
        "due_this_week": [],
        "in_progress": [],
        "blocked": [],
        "total_active": 0
    }
    
    for task in tasks:
        if task.get("type") != "task":
            continue
            
        status = task.get("status", {}).get("status", "").lower()
        due_date_str = task.get("due_date")
        
        # Parse due date
        due_date = None
        if due_date_str:
            try:
                # ClickUp returns milliseconds
                due_date = datetime.fromtimestamp(int(due_date_str) / 1000)
            except:
                pass
        
        # Completed this week
        if status in ["complete", "closed", "done"]:
            date_closed = task.get("date_closed")
            if date_closed:
                try:
                    closed = datetime.fromtimestamp(int(date_closed) / 1000)
                    if closed >= week_ago:
                        categorized["completed_this_week"].append(task)
                except:
                    pass
            continue
        
        # Active tasks
        categorized["total_active"] += 1
        
        # Overdue
        if due_date and due_date < now:
            categorized["overdue"].append(task)
        # Due this week
        elif due_date and due_date <= week_ahead:
            categorized["due_this_week"].append(task)
        
        # In progress
        if status in ["in progress", "doing", "working"]:
            categorized["in_progress"].append(task)
        
        # Blocked (check for blocked tag or status)
        if "blocked" in status or any(t.get("name", "").lower() == "blocked" for t in task.get("tags", [])):
            categorized["blocked"].append(task)
    
    return categorized

def get_client_projects(hierarchy: dict) -> list:
    """Extract client projects from hierarchy."""
    projects = []
    
    if not hierarchy:
        return projects
    
    for space in hierarchy.get("spaces", []):
        if space.get("name", "").lower() == "clients":
            for folder in space.get("folders", []):
                client_name = folder.get("name", "Unknown")
                lists = folder.get("lists", [])
                projects.append({
                    "client": client_name,
                    "folder_id": folder.get("id"),
                    "active_lists": len(lists),
                    "lists": [l.get("name") for l in lists]
                })
    
    return projects

def generate_digest() -> dict:
    """Generate the weekly digest."""
    print("Generating weekly digest...")
    
    digest = {
        "generated_at": datetime.now().isoformat(),
        "week_ending": datetime.now().strftime("%B %d, %Y"),
        "summary": {},
        "projects": [],
        "completed": [],
        "overdue": [],
        "upcoming": [],
        "blocked": [],
        "recommendations": []
    }
    
    # Get workspace data
    print("  Fetching workspace hierarchy...")
    hierarchy = get_workspace_hierarchy()
    
    print("  Fetching tasks...")
    tasks_result = get_clickup_tasks()
    tasks = tasks_result.get("results", []) if tasks_result else []
    
    # Categorize tasks
    categorized = categorize_tasks(tasks)
    
    # Get client projects
    projects = get_client_projects(hierarchy)
    
    # Build summary
    digest["summary"] = {
        "total_active_tasks": categorized["total_active"],
        "completed_this_week": len(categorized["completed_this_week"]),
        "overdue_tasks": len(categorized["overdue"]),
        "due_this_week": len(categorized["due_this_week"]),
        "blocked_tasks": len(categorized["blocked"]),
        "active_clients": len(projects)
    }
    
    # Add details
    digest["projects"] = projects
    digest["completed"] = [{"name": t.get("name"), "list": t.get("list", {}).get("name")} 
                          for t in categorized["completed_this_week"][:10]]
    digest["overdue"] = [{"name": t.get("name"), "due": t.get("due_date"), "list": t.get("list", {}).get("name")} 
                        for t in categorized["overdue"][:10]]
    digest["upcoming"] = [{"name": t.get("name"), "due": t.get("due_date"), "list": t.get("list", {}).get("name")} 
                         for t in categorized["due_this_week"][:10]]
    digest["blocked"] = [{"name": t.get("name"), "list": t.get("list", {}).get("name")} 
                        for t in categorized["blocked"]]
    
    # Generate recommendations
    if categorized["overdue"]:
        digest["recommendations"].append(f"⚠️ {len(categorized['overdue'])} overdue tasks need attention")
    if categorized["blocked"]:
        digest["recommendations"].append(f"🚫 {len(categorized['blocked'])} blocked tasks - unblock to keep momentum")
    if len(categorized["due_this_week"]) > 10:
        digest["recommendations"].append(f"📅 Heavy week ahead with {len(categorized['due_this_week'])} tasks due")
    if categorized["total_active"] > 50:
        digest["recommendations"].append("📋 Consider prioritizing - many active tasks")
    
    return digest

def format_digest_markdown(digest: dict) -> str:
    """Format digest as markdown."""
    md = f"""# 📊 Weekly Project Digest
**Week Ending:** {digest['week_ending']}

---

## Summary

| Metric | Count |
|--------|-------|
| Active Tasks | {digest['summary']['total_active_tasks']} |
| Completed This Week | {digest['summary']['completed_this_week']} |
| Overdue | {digest['summary']['overdue_tasks']} |
| Due This Week | {digest['summary']['due_this_week']} |
| Blocked | {digest['summary']['blocked_tasks']} |
| Active Clients | {digest['summary']['active_clients']} |

---

## ✅ Completed This Week ({len(digest['completed'])})

"""
    
    if digest['completed']:
        for task in digest['completed']:
            md += f"- {task['name']} ({task.get('list', 'No list')})\n"
    else:
        md += "_No tasks completed this week_\n"
    
    md += f"""
---

## ⚠️ Overdue ({len(digest['overdue'])})

"""
    
    if digest['overdue']:
        for task in digest['overdue']:
            md += f"- **{task['name']}** ({task.get('list', 'No list')})\n"
    else:
        md += "_No overdue tasks_ ✨\n"
    
    md += f"""
---

## 📅 Due This Week ({len(digest['upcoming'])})

"""
    
    if digest['upcoming']:
        for task in digest['upcoming']:
            md += f"- {task['name']} ({task.get('list', 'No list')})\n"
    else:
        md += "_Nothing due this week_\n"
    
    md += f"""
---

## 🚫 Blocked ({len(digest['blocked'])})

"""
    
    if digest['blocked']:
        for task in digest['blocked']:
            md += f"- {task['name']} ({task.get('list', 'No list')})\n"
    else:
        md += "_No blocked tasks_ ✨\n"
    
    md += """
---

## 💡 Recommendations

"""
    
    if digest['recommendations']:
        for rec in digest['recommendations']:
            md += f"- {rec}\n"
    else:
        md += "_Everything looks good!_ 🎉\n"
    
    md += f"""
---

_Generated by ClickUp PM • {datetime.now().strftime('%Y-%m-%d %H:%M')}_
"""
    
    return md

def format_digest_telegram(digest: dict) -> str:
    """Format digest for Telegram (shorter)."""
    msg = f"""📊 **Weekly Project Digest**
Week ending {digest['week_ending']}

**Summary:**
• {digest['summary']['completed_this_week']} tasks completed
• {digest['summary']['overdue_tasks']} overdue
• {digest['summary']['due_this_week']} due this week
• {digest['summary']['blocked_tasks']} blocked

"""
    
    if digest['overdue']:
        msg += "**⚠️ Overdue:**\n"
        for task in digest['overdue'][:5]:
            msg += f"• {task['name']}\n"
        if len(digest['overdue']) > 5:
            msg += f"_...and {len(digest['overdue']) - 5} more_\n"
        msg += "\n"
    
    if digest['recommendations']:
        msg += "**💡 Action Items:**\n"
        for rec in digest['recommendations']:
            msg += f"• {rec}\n"
    
    return msg

def main():
    parser = argparse.ArgumentParser(description="Weekly Project Digest")
    parser.add_argument("--send", action="store_true", help="Send via Telegram")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--save", action="store_true", help="Save to file")
    
    args = parser.parse_args()
    
    digest = generate_digest()
    
    if args.json:
        print(json.dumps(digest, indent=2))
        return
    
    # Generate markdown
    markdown = format_digest_markdown(digest)
    
    if args.save:
        output_dir = Path("/home/clawdbot/clawd/digests")
        output_dir.mkdir(exist_ok=True)
        filename = f"weekly_digest_{datetime.now().strftime('%Y%m%d')}.md"
        (output_dir / filename).write_text(markdown)
        print(f"Saved to: {output_dir / filename}")
    
    if args.send:
        # Send via Telegram
        telegram_msg = format_digest_telegram(digest)
        print("Sending via Telegram...")
        # This would use the message tool
        print(telegram_msg)
        print("\n[Would send via Telegram]")
    else:
        print(markdown)

if __name__ == "__main__":
    main()
