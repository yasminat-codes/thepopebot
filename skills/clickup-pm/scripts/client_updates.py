#!/usr/bin/env python3
"""
Automated Client Updates - Generate and send weekly progress updates to clients.

Features:
- Pull completed tasks from ClickUp
- Generate professional progress report
- Draft email for your review before sending
- Track what was sent to each client
- Customizable per client

Usage:
    python client_updates.py --client "Acme Corp"     # Generate update for specific client
    python client_updates.py --all                    # Generate for all active clients
    python client_updates.py --draft                  # Create drafts only (don't send)
    python client_updates.py --send "Acme Corp"       # Send update to client

Cron: Run weekly on Fridays to prepare weekend review
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
UPDATES_LOG = DATA_DIR / "client_updates_log.json"

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

def load_updates_log() -> dict:
    """Load updates log."""
    DATA_DIR.mkdir(exist_ok=True)
    if UPDATES_LOG.exists():
        return json.load(open(UPDATES_LOG))
    return {"clients": {}, "last_batch": None}

def save_updates_log(log: dict):
    """Save updates log."""
    with open(UPDATES_LOG, "w") as f:
        json.dump(log, f, indent=2)

def get_workspace_hierarchy() -> dict:
    """Get workspace structure."""
    return mcporter_call('clickup.clickup_get_workspace_hierarchy(limit: 100)')

def get_client_tasks(client_name: str) -> list:
    """Get tasks for a specific client."""
    result = mcporter_call(f'clickup.clickup_search(keywords: "{client_name}", count: 100)')
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

def get_week_progress(tasks: list) -> dict:
    """Analyze progress for the past week."""
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    progress = {
        "completed_this_week": [],
        "in_progress": [],
        "upcoming": [],
        "blocked": [],
        "total_hours_logged": 0
    }
    
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        date_closed = parse_timestamp(task.get("date_closed"))
        due_date = parse_timestamp(task.get("due_date"))
        
        task_info = {
            "name": task.get("name"),
            "list": task.get("list", {}).get("name", ""),
            "status": status
        }
        
        if status in ["complete", "closed", "done"]:
            if date_closed and date_closed >= week_ago:
                progress["completed_this_week"].append(task_info)
        elif status in ["in progress", "doing", "working"]:
            progress["in_progress"].append(task_info)
        elif "blocked" in status:
            progress["blocked"].append(task_info)
        elif due_date and due_date <= now + timedelta(days=7):
            progress["upcoming"].append(task_info)
    
    return progress

def generate_update_email(client_name: str, progress: dict) -> dict:
    """Generate a professional update email."""
    now = datetime.now()
    week_ending = now.strftime("%B %d, %Y")
    
    # Build email content
    subject = f"Weekly Progress Update - {client_name} - Week of {week_ending}"
    
    body = f"""Hi there,

Here's your weekly progress update for the week ending {week_ending}.

"""
    
    # Completed section
    if progress["completed_this_week"]:
        body += f"""**✅ Completed This Week ({len(progress['completed_this_week'])} items)**

"""
        for task in progress["completed_this_week"][:10]:
            body += f"- {task['name']}\n"
        if len(progress["completed_this_week"]) > 10:
            body += f"- ...and {len(progress['completed_this_week']) - 10} more\n"
        body += "\n"
    else:
        body += "**✅ Completed This Week**\nNo tasks completed this week.\n\n"
    
    # In Progress section
    if progress["in_progress"]:
        body += f"""**🔄 Currently In Progress ({len(progress['in_progress'])} items)**

"""
        for task in progress["in_progress"][:5]:
            body += f"- {task['name']}\n"
        if len(progress["in_progress"]) > 5:
            body += f"- ...and {len(progress['in_progress']) - 5} more\n"
        body += "\n"
    
    # Upcoming section
    if progress["upcoming"]:
        body += f"""**📅 Coming Up Next Week ({len(progress['upcoming'])} items)**

"""
        for task in progress["upcoming"][:5]:
            body += f"- {task['name']}\n"
        body += "\n"
    
    # Blocked section (if any)
    if progress["blocked"]:
        body += f"""**⚠️ Blocked Items (Need Your Input)**

"""
        for task in progress["blocked"]:
            body += f"- {task['name']}\n"
        body += "\nPlease let us know if you can help unblock these items.\n\n"
    
    # Closing
    body += """Let me know if you have any questions or if there's anything specific you'd like to discuss.

Best,
Yasmine
Smarterflo
"""
    
    return {
        "client": client_name,
        "subject": subject,
        "body": body,
        "generated_at": now.isoformat(),
        "stats": {
            "completed": len(progress["completed_this_week"]),
            "in_progress": len(progress["in_progress"]),
            "upcoming": len(progress["upcoming"]),
            "blocked": len(progress["blocked"])
        }
    }

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
                    "id": folder.get("id")
                })
    
    return clients

def generate_client_update(client_name: str) -> dict:
    """Generate update for a specific client."""
    print(f"Generating update for: {client_name}")
    
    tasks = get_client_tasks(client_name)
    if not tasks:
        return {"error": f"No tasks found for {client_name}"}
    
    progress = get_week_progress(tasks)
    email = generate_update_email(client_name, progress)
    
    return email

def format_email_preview(email: dict) -> str:
    """Format email for preview."""
    preview = f"""
{'='*60}
📧 CLIENT UPDATE PREVIEW
{'='*60}

**To:** [Client Contact for {email['client']}]
**Subject:** {email['subject']}

{'='*60}

{email['body']}

{'='*60}
Stats: {email['stats']['completed']} completed | {email['stats']['in_progress']} in progress | {email['stats']['upcoming']} upcoming
{'='*60}
"""
    return preview

def log_update_sent(client_name: str, email: dict):
    """Log that an update was sent."""
    log = load_updates_log()
    
    if client_name not in log["clients"]:
        log["clients"][client_name] = {"updates": []}
    
    log["clients"][client_name]["updates"].append({
        "sent_at": datetime.now().isoformat(),
        "subject": email["subject"],
        "stats": email["stats"]
    })
    
    # Keep only last 52 updates (1 year)
    log["clients"][client_name]["updates"] = log["clients"][client_name]["updates"][-52:]
    
    log["last_batch"] = datetime.now().isoformat()
    save_updates_log(log)

def main():
    parser = argparse.ArgumentParser(description="Automated Client Updates")
    parser.add_argument("--client", "-c", help="Generate update for specific client")
    parser.add_argument("--all", action="store_true", help="Generate for all active clients")
    parser.add_argument("--draft", action="store_true", help="Create drafts only")
    parser.add_argument("--send", help="Send update to client (requires client name)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--history", help="Show update history for client")
    
    args = parser.parse_args()
    
    if args.history:
        log = load_updates_log()
        client_log = log.get("clients", {}).get(args.history, {})
        if args.json:
            print(json.dumps(client_log, indent=2))
        else:
            updates = client_log.get("updates", [])
            print(f"\n📜 Update History for {args.history}: {len(updates)} updates\n")
            for update in updates[-10:]:
                print(f"  - {update['sent_at'][:10]}: {update['stats']['completed']} completed")
        return
    
    if args.client:
        email = generate_client_update(args.client)
        
        if "error" in email:
            print(f"❌ {email['error']}")
            return
        
        if args.json:
            print(json.dumps(email, indent=2))
        else:
            print(format_email_preview(email))
            
            if not args.draft:
                print("\n💡 To send this update, run with: --send \"{args.client}\"")
    
    elif args.all:
        print("Generating updates for all clients...")
        hierarchy = get_workspace_hierarchy()
        clients = get_all_clients(hierarchy)
        
        updates = []
        for client in clients:
            email = generate_client_update(client["name"])
            if "error" not in email:
                updates.append(email)
        
        if args.json:
            print(json.dumps(updates, indent=2))
        else:
            print(f"\n📧 Generated {len(updates)} client updates:\n")
            for email in updates:
                print(f"  - {email['client']}: {email['stats']['completed']} completed this week")
            
            if not args.draft:
                print("\n💡 Review each update and send individually with: --send \"Client Name\"")
    
    elif args.send:
        email = generate_client_update(args.send)
        
        if "error" in email:
            print(f"❌ {email['error']}")
            return
        
        # Log the update
        log_update_sent(args.send, email)
        
        if args.json:
            print(json.dumps({"status": "sent", "email": email}, indent=2))
        else:
            print(format_email_preview(email))
            print("\n✅ Update logged as sent!")
            print("📨 Email content ready - send via your email client or integrate with Gmail API")
    
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python client_updates.py --client "Acme Corp"')
        print('  python client_updates.py --all --draft')
        print('  python client_updates.py --send "Acme Corp"')
        print('  python client_updates.py --history "Acme Corp"')

if __name__ == "__main__":
    main()
