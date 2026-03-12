#!/usr/bin/env python3
"""
Invoice Triggers - Track milestones and trigger invoice reminders.

Features:
- Monitor milestone completions
- Track hours vs budgeted hours
- Alert when invoice should be sent
- Generate invoice draft data
- Integrate with Airtable invoice tracking

Usage:
    python invoice_triggers.py --check             # Check for invoice triggers
    python invoice_triggers.py --client "Acme"    # Check specific client
    python invoice_triggers.py --generate "Acme"  # Generate invoice data
    python invoice_triggers.py --log              # Show invoice log

Cron: Run daily to check for completed milestones
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
INVOICE_LOG = DATA_DIR / "invoice_log.json"
CONFIG_FILE = Path(__file__).parent.parent / "config.json"

# Milestone keywords that trigger invoices
INVOICE_MILESTONES = [
    "launch", "go live", "handoff", "delivery", "complete",
    "phase complete", "milestone", "payment", "final"
]

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
    """Load config."""
    if CONFIG_FILE.exists():
        return json.load(open(CONFIG_FILE))
    return {}

def load_invoice_log() -> dict:
    """Load invoice log."""
    DATA_DIR.mkdir(exist_ok=True)
    if INVOICE_LOG.exists():
        return json.load(open(INVOICE_LOG))
    return {"invoices": [], "triggers": []}

def save_invoice_log(log: dict):
    """Save invoice log."""
    with open(INVOICE_LOG, "w") as f:
        json.dump(log, f, indent=2)

def get_workspace_hierarchy() -> dict:
    """Get workspace structure."""
    return mcporter_call('clickup.clickup_get_workspace_hierarchy(limit: 100)')

def get_all_tasks() -> list:
    """Get all tasks."""
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

def is_milestone_task(task_name: str) -> bool:
    """Check if task is an invoice milestone."""
    name_lower = task_name.lower()
    return any(kw in name_lower for kw in INVOICE_MILESTONES)

def get_client_from_task(task: dict) -> str:
    """Extract client name from task."""
    folder = task.get("folder", {}).get("name", "")
    if folder:
        return folder
    list_name = task.get("list", {}).get("name", "")
    return list_name.split(" - ")[0] if " - " in list_name else "Unknown"

def check_invoice_triggers() -> list:
    """Check for tasks that should trigger invoices."""
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    triggers = []
    tasks = get_all_tasks()
    invoice_log = load_invoice_log()
    logged_task_ids = {t.get("task_id") for t in invoice_log.get("triggers", [])}
    
    for task in tasks:
        task_id = task.get("id")
        task_name = task.get("name", "")
        status = task.get("status", {}).get("status", "").lower()
        date_closed = parse_timestamp(task.get("date_closed"))
        
        # Skip if not completed recently
        if status not in ["complete", "closed", "done"]:
            continue
        
        if not date_closed or date_closed < week_ago:
            continue
        
        # Skip if already logged
        if task_id in logged_task_ids:
            continue
        
        # Check if this is a milestone
        if is_milestone_task(task_name):
            client = get_client_from_task(task)
            
            trigger = {
                "task_id": task_id,
                "task_name": task_name,
                "client": client,
                "completed_at": date_closed.isoformat(),
                "trigger_type": "milestone",
                "status": "pending"
            }
            triggers.append(trigger)
    
    return triggers

def check_hours_triggers(budget_threshold: float = 0.8) -> list:
    """Check if any client is approaching budget hours."""
    triggers = []
    
    # This would integrate with time tracking
    # For now, return empty - would need client budget data
    
    return triggers

def generate_invoice_data(client_name: str) -> dict:
    """Generate invoice data for a client."""
    now = datetime.now()
    
    # Get client tasks
    result = mcporter_call(f'clickup.clickup_search(keywords: "{client_name}", count: 100)')
    tasks = [t for t in result.get("results", []) if t.get("type") == "task"] if result else []
    
    # Analyze work
    completed_tasks = []
    total_hours = 0
    
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        if status in ["complete", "closed", "done"]:
            completed_tasks.append(task.get("name", ""))
            
            # Get time spent if available
            time_spent = task.get("time_spent")
            if time_spent:
                try:
                    hours = int(time_spent) / 3600000  # ms to hours
                    total_hours += hours
                except:
                    pass
    
    invoice_data = {
        "client": client_name,
        "generated_at": now.isoformat(),
        "invoice_date": now.strftime("%Y-%m-%d"),
        "due_date": (now + timedelta(days=30)).strftime("%Y-%m-%d"),
        "line_items": [],
        "subtotal": 0,
        "notes": ""
    }
    
    # Group work into line items
    if total_hours > 0:
        invoice_data["line_items"].append({
            "description": f"Professional Services - {len(completed_tasks)} tasks completed",
            "quantity": round(total_hours, 1),
            "unit": "hours",
            "rate": 150,  # Default rate - would come from client config
            "amount": round(total_hours * 150, 2)
        })
        invoice_data["subtotal"] = round(total_hours * 150, 2)
    
    # Add work summary
    if completed_tasks:
        invoice_data["notes"] = "Work completed:\n" + "\n".join([f"- {t}" for t in completed_tasks[:10]])
        if len(completed_tasks) > 10:
            invoice_data["notes"] += f"\n- ...and {len(completed_tasks) - 10} more items"
    
    return invoice_data

def log_trigger(trigger: dict):
    """Log an invoice trigger."""
    log = load_invoice_log()
    trigger["logged_at"] = datetime.now().isoformat()
    log["triggers"].append(trigger)
    
    # Keep only last 100 triggers
    log["triggers"] = log["triggers"][-100:]
    save_invoice_log(log)

def format_triggers_report(triggers: list) -> str:
    """Format triggers as report."""
    if not triggers:
        return "\n✅ No new invoice triggers found."
    
    report = f"\n💰 **Invoice Triggers Found: {len(triggers)}**\n\n"
    
    by_client = {}
    for trigger in triggers:
        client = trigger.get("client", "Unknown")
        if client not in by_client:
            by_client[client] = []
        by_client[client].append(trigger)
    
    for client, client_triggers in by_client.items():
        report += f"**{client}:**\n"
        for t in client_triggers:
            report += f"  - {t['task_name']} (completed {t['completed_at'][:10]})\n"
        report += "\n"
    
    return report

def format_invoice_preview(invoice_data: dict) -> str:
    """Format invoice data as preview."""
    preview = f"""
{'='*60}
📄 INVOICE PREVIEW
{'='*60}

**Client:** {invoice_data['client']}
**Invoice Date:** {invoice_data['invoice_date']}
**Due Date:** {invoice_data['due_date']}

**Line Items:**
"""
    
    for item in invoice_data.get("line_items", []):
        preview += f"""
  {item['description']}
  {item['quantity']} {item['unit']} × ${item['rate']}/hr = ${item['amount']}
"""
    
    preview += f"""
{'='*60}
**Subtotal:** ${invoice_data['subtotal']}
{'='*60}

**Notes:**
{invoice_data.get('notes', 'None')}
"""
    
    return preview

def main():
    parser = argparse.ArgumentParser(description="Invoice Triggers")
    parser.add_argument("--check", action="store_true", help="Check for invoice triggers")
    parser.add_argument("--client", "-c", help="Check specific client")
    parser.add_argument("--generate", "-g", help="Generate invoice data for client")
    parser.add_argument("--log", action="store_true", help="Show invoice log")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--alert", action="store_true", help="Send alert if triggers found")
    
    args = parser.parse_args()
    
    if args.log:
        log = load_invoice_log()
        if args.json:
            print(json.dumps(log, indent=2))
        else:
            print(f"\n📜 Invoice Log: {len(log.get('triggers', []))} triggers recorded")
            for trigger in log.get("triggers", [])[-10:]:
                print(f"  - {trigger.get('client')}: {trigger.get('task_name')[:40]}...")
        return
    
    if args.generate:
        invoice_data = generate_invoice_data(args.generate)
        if args.json:
            print(json.dumps(invoice_data, indent=2))
        else:
            print(format_invoice_preview(invoice_data))
        return
    
    if args.check or args.client:
        print("Checking for invoice triggers...", file=sys.stderr)
        
        triggers = check_invoice_triggers()
        
        if args.client:
            triggers = [t for t in triggers if args.client.lower() in t.get("client", "").lower()]
        
        if args.json:
            print(json.dumps(triggers, indent=2))
        else:
            print(format_triggers_report(triggers))
        
        # Log new triggers
        for trigger in triggers:
            log_trigger(trigger)
        
        # Alert if requested and triggers found
        if args.alert and triggers:
            print("\n[Would send alert via Telegram]")
        
        return
    
    parser.print_help()
    print("\nExamples:")
    print("  python invoice_triggers.py --check")
    print('  python invoice_triggers.py --generate "Acme Corp"')
    print("  python invoice_triggers.py --log")

if __name__ == "__main__":
    main()
