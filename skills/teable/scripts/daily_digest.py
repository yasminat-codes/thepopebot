#!/usr/bin/env python3
"""
Generate a morning digest report for OpenClaw task management.

Usage:
  python3 daily_digest.py [--send-slack] [--format markdown|text]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from task_manager import TaskManager

YASMINE_CHANNEL = "C0AF4HR9SJX"


def _task_line(task, extra=""):
    """Format a single task for the digest."""
    fields = task.get("fields", {})
    priority = fields.get("Priority", "Normal")
    title = fields.get("Title", "(untitled)")
    assignee = fields.get("Assignee", "?")
    extra_str = f" -> {extra}" if extra else ""
    return f"  - [{priority}] {title} ({assignee}){extra_str}"


def format_digest(digest, use_markdown=False):
    """Format the digest dict into a readable report."""
    today = datetime.now().strftime("%Y-%m-%d")
    sep = "---" if use_markdown else "=" * 50

    lines = []

    if use_markdown:
        lines.append(f"# OpenClaw Daily Digest - {today}")
    else:
        lines.append(f"=== OpenClaw Daily Digest - {today} ===")

    lines.append("")

    # Needs Review
    needs_review = digest.get("needs_review", [])
    header = f"**NEEDS REVIEW ({len(needs_review)})**" if use_markdown else f"NEEDS REVIEW ({len(needs_review)})"
    lines.append(header)
    if needs_review:
        for task in needs_review:
            lines.append(_task_line(task))
    else:
        lines.append("  (none)")
    lines.append("")

    # Blocked
    blocked = digest.get("blocked", [])
    header = f"**BLOCKED ({len(blocked)})**" if use_markdown else f"BLOCKED ({len(blocked)})"
    lines.append(header)
    if blocked:
        for task in blocked:
            reason = task.get("fields", {}).get("Blocked Reason", "")
            lines.append(_task_line(task, extra=f'"{reason}"' if reason else ""))
    else:
        lines.append("  (none)")
    lines.append("")

    # In Progress
    in_progress = digest.get("in_progress", [])
    header = f"**IN PROGRESS ({len(in_progress)})**" if use_markdown else f"IN PROGRESS ({len(in_progress)})"
    lines.append(header)
    if in_progress:
        for task in in_progress:
            lines.append(_task_line(task))
    else:
        lines.append("  (none)")
    lines.append("")

    # Overdue
    overdue = digest.get("overdue", [])
    header = f"**OVERDUE ({len(overdue)})**" if use_markdown else f"OVERDUE ({len(overdue)})"
    lines.append(header)
    if overdue:
        for task in overdue:
            due = task.get("fields", {}).get("Due Date", "")
            lines.append(_task_line(task, extra=f"due {due}" if due else ""))
    else:
        lines.append("  (none)")
    lines.append("")

    # Completed Yesterday
    completed = digest.get("completed_yesterday", [])
    header = f"**COMPLETED YESTERDAY ({len(completed)})**" if use_markdown else f"COMPLETED YESTERDAY ({len(completed)})"
    lines.append(header)
    if completed:
        for task in completed:
            lines.append(_task_line(task))
    else:
        lines.append("  (none)")
    lines.append("")

    # Summary line
    lines.append(sep)
    lines.append(
        f"Summary: {len(needs_review)} awaiting review, {len(blocked)} blocked, "
        f"{len(in_progress)} active, {len(overdue)} overdue"
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Daily Digest")
    parser.add_argument("--send-slack", action="store_true", help="Send digest to Yasmine via Slack")
    parser.add_argument("--format", dest="fmt", choices=["markdown", "text"], default="text", help="Output format")
    args = parser.parse_args()

    try:
        tm = TaskManager()
        digest = tm.get_daily_digest()
    except Exception as e:
        print(f"Error fetching digest: {e}", file=sys.stderr)
        sys.exit(1)

    use_markdown = args.fmt == "markdown"
    report = format_digest(digest, use_markdown=use_markdown)
    print(report)

    if args.send_slack:
        print(f"\n[Slack] Would send digest to Yasmine's channel ({YASMINE_CHANNEL}):")
        print(f"[Slack] Message length: {len(report)} chars")
        print("[Slack] (Slack sending not yet implemented - printed above instead)")


if __name__ == "__main__":
    main()
