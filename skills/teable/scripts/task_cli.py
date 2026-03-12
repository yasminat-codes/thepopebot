#!/usr/bin/env python3
"""
CLI tool for OpenClaw task management via Teable.

Usage:
  python3 task_cli.py my-tasks --agent amira [--status "Ready"]
  python3 task_cli.py create --title "..." --description "..." --assignee qamar --requester yasmine [--priority High] [--tags cold-email,sales] [--due 2026-03-15]
  python3 task_cli.py start --record-id recXXX --agent idris
  python3 task_cli.py block --record-id recXXX --agent idris --reason "Waiting for API credentials"
  python3 task_cli.py submit --record-id recXXX --agent idris --summary "Built the dashboard" [--files "src/dashboard.py,src/api.py"] [--outputs "https://docs.google.com/xxx"] [--follow-ups "Deploy to staging"]
  python3 task_cli.py approve --record-id recXXX [--notes "Looks good"]
  python3 task_cli.py reject --record-id recXXX --notes "Needs error handling"
  python3 task_cli.py digest
  python3 task_cli.py ready --agent idris
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from task_manager import TaskManager


PRIORITY_ICONS = {
    "Urgent": "!!!",
    "High": "!! ",
    "Normal": "!  ",
    "Low": ".  ",
}


def format_task_line(task):
    """Format a single task record as a one-line summary."""
    fields = task.get("fields", {})
    status = fields.get("Status", "?")
    priority = fields.get("Priority", "Normal")
    title = fields.get("Title", "(untitled)")
    due = fields.get("Due Date", "")
    icon = PRIORITY_ICONS.get(priority, "   ")
    due_str = f"  due {due}" if due else ""
    return f"  {icon} [{status:<12}] {title}{due_str}"


def cmd_my_tasks(args):
    tm = TaskManager()
    status = args.status if args.status else None
    tasks = tm.get_my_tasks(args.agent, status=status)
    if not tasks:
        print(f"No tasks found for {args.agent}.")
        return
    print(f"\nTasks for {args.agent} ({len(tasks)}):\n")
    print(f"  {'Pri':<4} {'Status':<14} {'Title':<50} {'Due'}")
    print(f"  {'---':<4} {'------':<14} {'-----':<50} {'---'}")
    for task in tasks:
        print(format_task_line(task))
    print()


def cmd_create(args):
    tm = TaskManager()
    tags = args.tags.split(",") if args.tags else None
    result = tm.create_task(
        title=args.title,
        description=args.description,
        assignee=args.assignee,
        requester=args.requester,
        priority=args.priority,
        tags=tags,
        due_date=args.due,
    )
    rec_id = result.get("id", "?") if result else "?"
    print(f"Task created: {rec_id}")
    print(f"  Title:    {args.title}")
    print(f"  Assignee: {args.assignee}")
    print(f"  Priority: {args.priority}")


def cmd_start(args):
    tm = TaskManager()
    tm.start_task(args.record_id, args.agent)
    print(f"Task {args.record_id} started by {args.agent}.")


def cmd_block(args):
    tm = TaskManager()
    tm.block_task(args.record_id, args.agent, args.reason)
    print(f"Task {args.record_id} blocked.")
    print(f"  Reason: {args.reason}")


def cmd_submit(args):
    tm = TaskManager()
    files = args.files.split(",") if args.files else None
    follow_ups = args.follow_ups.split(",") if args.follow_ups else None
    tm.submit_for_review(
        record_id=args.record_id,
        agent_name=args.agent,
        summary=args.summary,
        files_changed=files,
        outputs=args.outputs,
        follow_ups=follow_ups,
    )
    print(f"Task {args.record_id} submitted for review by {args.agent}.")


def cmd_approve(args):
    tm = TaskManager()
    tm.approve_task(args.record_id, notes=args.notes)
    print(f"Task {args.record_id} approved.")


def cmd_reject(args):
    tm = TaskManager()
    tm.reject_task(args.record_id, notes=args.notes)
    print(f"Task {args.record_id} rejected. Moved back to In Progress.")
    print(f"  Notes: {args.notes}")


def cmd_digest(_args):
    tm = TaskManager()
    digest = tm.get_daily_digest()
    from daily_digest import format_digest  # noqa: E402
    print(format_digest(digest))


def cmd_ready(args):
    tm = TaskManager()
    tasks = tm.get_ready_tasks(args.agent)
    if not tasks:
        print(f"No ready tasks for {args.agent}.")
        return
    print(f"\nReady tasks for {args.agent} ({len(tasks)}):\n")
    for task in tasks:
        print(format_task_line(task))
    print()


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Task Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # my-tasks
    p_my = subparsers.add_parser("my-tasks", help="List tasks for an agent")
    p_my.add_argument("--agent", required=True, help="Agent name (e.g. amira)")
    p_my.add_argument("--status", help='Filter by status (e.g. "Ready")')
    p_my.set_defaults(func=cmd_my_tasks)

    # create
    p_create = subparsers.add_parser("create", help="Create a new task")
    p_create.add_argument("--title", required=True, help="Task title")
    p_create.add_argument("--description", required=True, help="Task description")
    p_create.add_argument("--assignee", required=True, help="Agent to assign to")
    p_create.add_argument("--requester", required=True, help="Who requested the task")
    p_create.add_argument("--priority", default="Normal", choices=["Urgent", "High", "Normal", "Low"])
    p_create.add_argument("--tags", help="Comma-separated tags (e.g. cold-email,sales)")
    p_create.add_argument("--due", help="Due date (YYYY-MM-DD)")
    p_create.set_defaults(func=cmd_create)

    # start
    p_start = subparsers.add_parser("start", help="Start working on a task")
    p_start.add_argument("--record-id", required=True, help="Record ID (recXXX)")
    p_start.add_argument("--agent", required=True, help="Agent name")
    p_start.set_defaults(func=cmd_start)

    # block
    p_block = subparsers.add_parser("block", help="Mark a task as blocked")
    p_block.add_argument("--record-id", required=True, help="Record ID")
    p_block.add_argument("--agent", required=True, help="Agent name")
    p_block.add_argument("--reason", required=True, help="Why the task is blocked")
    p_block.set_defaults(func=cmd_block)

    # submit
    p_submit = subparsers.add_parser("submit", help="Submit task for review")
    p_submit.add_argument("--record-id", required=True, help="Record ID")
    p_submit.add_argument("--agent", required=True, help="Agent name")
    p_submit.add_argument("--summary", required=True, help="Summary of work done")
    p_submit.add_argument("--files", help="Comma-separated list of changed files")
    p_submit.add_argument("--outputs", help="Comma-separated output URLs/paths")
    p_submit.add_argument("--follow-ups", help="Comma-separated follow-up items")
    p_submit.set_defaults(func=cmd_submit)

    # approve
    p_approve = subparsers.add_parser("approve", help="Approve a task")
    p_approve.add_argument("--record-id", required=True, help="Record ID")
    p_approve.add_argument("--notes", default="", help="Approval notes")
    p_approve.set_defaults(func=cmd_approve)

    # reject
    p_reject = subparsers.add_parser("reject", help="Reject a task back to In Progress")
    p_reject.add_argument("--record-id", required=True, help="Record ID")
    p_reject.add_argument("--notes", required=True, help="Rejection reason")
    p_reject.set_defaults(func=cmd_reject)

    # digest
    p_digest = subparsers.add_parser("digest", help="Show daily digest")
    p_digest.set_defaults(func=cmd_digest)

    # ready
    p_ready = subparsers.add_parser("ready", help="Show ready tasks for an agent")
    p_ready.add_argument("--agent", required=True, help="Agent name")
    p_ready.set_defaults(func=cmd_ready)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
