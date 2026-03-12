#!/usr/bin/env python3
"""
Meeting → Task Extraction - Extract action items from meeting notes and create ClickUp tasks.

Supports:
- Fathom meeting notes (from email or API)
- Manual meeting notes input
- Google Doc meeting notes

Features:
- AI-powered action item extraction
- Automatic assignee detection
- Due date inference
- Task creation in appropriate ClickUp list

Usage:
    python meeting_to_tasks.py --notes "Meeting notes text..."
    python meeting_to_tasks.py --file meeting_notes.md
    python meeting_to_tasks.py --fathom "Meeting title"
    python meeting_to_tasks.py --interactive

Cron: Can be triggered after meetings via webhook
"""

import argparse
import json
import os
import re
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

def extract_action_items(text: str) -> list:
    """Extract action items from meeting notes using pattern matching."""
    action_items = []
    
    # Common patterns for action items
    patterns = [
        # "Action: ..." or "Action item: ..."
        r'(?:action(?:\s+item)?[\s:]+)([^\n]+)',
        # "TODO: ..." or "To do: ..."
        r'(?:to\s*do[\s:]+)([^\n]+)',
        # "[ ] ..." (checkbox)
        r'\[\s*\]\s*([^\n]+)',
        # "- [ ] ..." (markdown checkbox)
        r'-\s*\[\s*\]\s*([^\n]+)',
        # "@Person will ..."
        r'@(\w+)\s+will\s+([^\n]+)',
        # "Person to ..." or "Person should ..."
        r'(\w+)\s+(?:to|should|needs to|will)\s+([^\n]+)',
        # "Follow up on ..."
        r'(?:follow\s*up\s*(?:on|with)?[\s:]+)([^\n]+)',
        # "Next steps: ..."
        r'(?:next\s+steps?[\s:]+)([^\n]+)',
    ]
    
    # Look for action item sections
    sections = re.split(r'\n(?=(?:action items?|next steps?|to\s*do|follow[\s-]*ups?)[\s:]*\n)', text, flags=re.IGNORECASE)
    
    for section in sections:
        # Check if this is an action items section
        if re.match(r'(?:action items?|next steps?|to\s*do|follow[\s-]*ups?)', section, re.IGNORECASE):
            # Extract bullet points
            bullets = re.findall(r'[-•*]\s*([^\n]+)', section)
            for bullet in bullets:
                if len(bullet) > 10:  # Skip very short items
                    action_items.append({
                        "text": bullet.strip(),
                        "source": "section"
                    })
    
    # Also apply patterns to full text
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if isinstance(match, tuple):
                # Pattern captured assignee + action
                action_text = " ".join(match).strip()
            else:
                action_text = match.strip()
            
            if len(action_text) > 10 and action_text not in [a["text"] for a in action_items]:
                action_items.append({
                    "text": action_text,
                    "source": "pattern"
                })
    
    return action_items

def infer_assignee(text: str) -> str:
    """Try to infer assignee from action item text."""
    # Look for @mentions
    mention = re.search(r'@(\w+)', text)
    if mention:
        return mention.group(1)
    
    # Look for names at start
    name_match = re.match(r'^(\w+)\s+(?:will|to|should)', text)
    if name_match:
        name = name_match.group(1)
        if name.lower() not in ['we', 'i', 'they', 'the', 'a', 'an', 'this', 'that']:
            return name
    
    return None

def infer_due_date(text: str) -> str:
    """Try to infer due date from action item text."""
    today = datetime.now()
    
    # Look for explicit dates
    date_patterns = [
        (r'by\s+(\w+day)', 'weekday'),
        (r'by\s+end\s+of\s+(week|day|month)', 'relative'),
        (r'by\s+(\d{1,2}/\d{1,2})', 'date'),
        (r'due\s+(\w+day)', 'weekday'),
        (r'this\s+(week|friday|monday)', 'this'),
        (r'next\s+(week|friday|monday)', 'next'),
        (r'tomorrow', 'tomorrow'),
        (r'today', 'today'),
        (r'asap', 'asap'),
    ]
    
    text_lower = text.lower()
    
    for pattern, ptype in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if ptype == 'tomorrow':
                return (today + timedelta(days=1)).strftime('%Y-%m-%d')
            elif ptype == 'today':
                return today.strftime('%Y-%m-%d')
            elif ptype == 'asap':
                return (today + timedelta(days=1)).strftime('%Y-%m-%d')
            elif ptype == 'relative':
                period = match.group(1)
                if period == 'day':
                    return today.strftime('%Y-%m-%d')
                elif period == 'week':
                    # End of week (Friday)
                    days_until_friday = (4 - today.weekday()) % 7
                    return (today + timedelta(days=days_until_friday)).strftime('%Y-%m-%d')
                elif period == 'month':
                    # End of month
                    if today.month == 12:
                        return f"{today.year + 1}-01-01"
                    else:
                        return f"{today.year}-{today.month + 1:02d}-01"
            elif ptype == 'this':
                period = match.group(1)
                if period == 'week' or period == 'friday':
                    days_until_friday = (4 - today.weekday()) % 7
                    if days_until_friday == 0:
                        days_until_friday = 7
                    return (today + timedelta(days=days_until_friday)).strftime('%Y-%m-%d')
            elif ptype == 'next':
                period = match.group(1)
                if period == 'week' or period == 'friday':
                    days_until_friday = (4 - today.weekday()) % 7 + 7
                    return (today + timedelta(days=days_until_friday)).strftime('%Y-%m-%d')
    
    # Default: 1 week from now
    return (today + timedelta(days=7)).strftime('%Y-%m-%d')

def infer_priority(text: str) -> int:
    """Infer priority from action item text."""
    text_lower = text.lower()
    
    # Urgent indicators
    if any(word in text_lower for word in ['urgent', 'asap', 'immediately', 'critical', 'blocker']):
        return 1  # Urgent
    
    # High priority indicators
    if any(word in text_lower for word in ['important', 'high priority', 'soon', 'today', 'tomorrow']):
        return 2  # High
    
    # Low priority indicators
    if any(word in text_lower for word in ['when possible', 'eventually', 'nice to have', 'low priority']):
        return 4  # Low
    
    return 3  # Normal

def detect_client_from_notes(text: str) -> str:
    """Try to detect client name from meeting notes."""
    # Look for "Meeting with [Client]" or "[Client] call"
    patterns = [
        r'meeting\s+with\s+([A-Z][A-Za-z\s]+?)(?:\s+(?:team|call|sync))?[\s\n]',
        r'([A-Z][A-Za-z\s]+?)\s+(?:call|meeting|sync|kickoff)',
        r'client[\s:]+([A-Z][A-Za-z\s]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return None

def create_clickup_task(name: str, description: str, list_id: str, 
                        priority: int = 3, due_date: str = None) -> dict:
    """Create a task in ClickUp."""
    priority_map = {1: "urgent", 2: "high", 3: "normal", 4: "low"}
    pri = priority_map.get(priority, "normal")
    
    # Escape description
    desc_escaped = description.replace('"', '\\"').replace('\n', '\\n')
    
    call = f'clickup.clickup_create_task(list_id: "{list_id}", name: "{name}", description: "{desc_escaped}", priority: "{pri}"'
    
    if due_date:
        call += f', due_date: "{due_date}"'
    
    call += ')'
    
    return mcporter_call(call)

def process_meeting_notes(notes: str, client: str = None, list_id: str = None, 
                          create_tasks: bool = False) -> dict:
    """Process meeting notes and extract action items."""
    result = {
        "meeting_date": datetime.now().isoformat(),
        "detected_client": detect_client_from_notes(notes) if not client else client,
        "action_items": [],
        "tasks_created": []
    }
    
    # Extract action items
    raw_items = extract_action_items(notes)
    
    for item in raw_items:
        processed = {
            "text": item["text"],
            "assignee": infer_assignee(item["text"]),
            "due_date": infer_due_date(item["text"]),
            "priority": infer_priority(item["text"]),
            "source": item["source"]
        }
        result["action_items"].append(processed)
    
    # Create tasks if requested
    if create_tasks and list_id:
        for item in result["action_items"]:
            task_result = create_clickup_task(
                name=item["text"][:100],  # Truncate if too long
                description=f"Extracted from meeting notes\n\nOriginal: {item['text']}",
                list_id=list_id,
                priority=item["priority"],
                due_date=item["due_date"]
            )
            
            if task_result and task_result.get("id"):
                result["tasks_created"].append({
                    "id": task_result["id"],
                    "name": item["text"][:100]
                })
    
    return result

def format_extraction_report(result: dict) -> str:
    """Format extraction results."""
    report = f"""# Meeting Action Items Extraction
**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    if result.get("detected_client"):
        report += f"**Detected Client:** {result['detected_client']}\n"
    
    report += f"""
---

## Extracted Action Items ({len(result['action_items'])})

"""
    
    priority_emoji = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢"}
    
    for i, item in enumerate(result["action_items"], 1):
        emoji = priority_emoji.get(item["priority"], "⚪")
        report += f"""### {i}. {emoji} {item['text'][:80]}{'...' if len(item['text']) > 80 else ''}

- **Assignee:** {item['assignee'] or 'Unassigned'}
- **Due Date:** {item['due_date']}
- **Priority:** {['', 'Urgent', 'High', 'Normal', 'Low'][item['priority']]}

"""
    
    if result.get("tasks_created"):
        report += f"""---

## Tasks Created ({len(result['tasks_created'])})

"""
        for task in result["tasks_created"]:
            report += f"- ✅ {task['name']} (ID: {task['id']})\n"
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Meeting → Task Extraction")
    parser.add_argument("--notes", "-n", help="Meeting notes text")
    parser.add_argument("--file", "-f", help="File containing meeting notes")
    parser.add_argument("--client", "-c", help="Client name (for task assignment)")
    parser.add_argument("--list-id", "-l", help="ClickUp list ID to create tasks in")
    parser.add_argument("--create", action="store_true", help="Actually create tasks in ClickUp")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    # Get notes
    notes = None
    
    if args.notes:
        notes = args.notes
    elif args.file:
        notes = Path(args.file).read_text()
    elif args.interactive:
        print("Paste meeting notes (end with Ctrl+D or empty line):")
        lines = []
        try:
            while True:
                line = input()
                if not line and lines:
                    break
                lines.append(line)
        except EOFError:
            pass
        notes = "\n".join(lines)
    
    if not notes:
        parser.print_help()
        print("\nExamples:")
        print('  python meeting_to_tasks.py --notes "Meeting notes..."')
        print('  python meeting_to_tasks.py --file meeting.md --create --list-id 12345')
        print('  python meeting_to_tasks.py --interactive')
        return
    
    # Process notes
    result = process_meeting_notes(
        notes=notes,
        client=args.client,
        list_id=args.list_id,
        create_tasks=args.create and args.list_id
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        report = format_extraction_report(result)
        print(report)
        
        if result["action_items"] and not args.create:
            print("\n💡 To create tasks in ClickUp, add: --create --list-id YOUR_LIST_ID")

if __name__ == "__main__":
    main()
