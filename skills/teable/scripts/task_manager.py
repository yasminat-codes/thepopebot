#!/usr/bin/env python3
"""
TaskManager - Core module for OpenClaw Teable Task Management System.

Handles task lifecycle, status transitions, activity logging,
dependency checking, and agent notifications.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Import TeableClient from common.py (same directory)
sys.path.insert(0, str(Path(__file__).parent))
from common import TeableClient, build_filter


# --- Status lifecycle constants ---

STATUSES = [
    "Draft",
    "Backlog",
    "Ready",
    "In Progress",
    "Blocked",
    "Needs Review",
    "Approved",
    "Done",
]

# Allowed transitions: (from_status, to_status) -> requirements
# Requirements: "anyone", "assignee", "system", "yasmine", or a combo
TRANSITIONS = {
    ("Draft", "Backlog"): {"who": "anyone"},
    ("Backlog", "Ready"): {"who": "anyone"},
    ("Ready", "In Progress"): {"who": "assignee", "check_deps": True},
    ("Ready", "Blocked"): {"who": "system"},
    ("In Progress", "Blocked"): {"who": "assignee", "reason_required": True},
    ("In Progress", "Needs Review"): {"who": "assignee", "report_required": True},
    ("Blocked", "Ready"): {"who": "system"},
    ("Blocked", "In Progress"): {"who": "assignee"},
    ("Needs Review", "Approved"): {"who": "yasmine"},
    ("Needs Review", "In Progress"): {"who": "yasmine"},
    ("Approved", "Done"): {"who": "system_or_yasmine"},
    ("Done", "Backlog"): {"who": "yasmine"},
}

PRIORITY_SORT_ORDER = {
    "Urgent": 1,
    "High": 2,
    "Normal": 3,
    "Low": 4,
}


class TaskManager:
    """Manages task lifecycle in the OpenClaw Teable task system."""

    def __init__(self):
        self.client = TeableClient()
        self._config_dir = Path(__file__).parent.parent / "config"
        self._table_ids = self._load_json("table_ids.json")
        self._slack_channels = self._load_json("slack_channels.json")

    def _load_json(self, filename: str) -> Dict:
        filepath = self._config_dir / filename
        if not filepath.exists():
            print(f"[WARN] Config file not found: {filepath}")
            return {}
        with open(filepath, "r") as f:
            return json.load(f)

    def _get_table_id(self, key: str) -> str:
        """Get table ID supporting both flat and nested config formats."""
        # Nested format: {"tables": {"tasks": {"id": "tblXXX"}}}
        tables = self._table_ids.get("tables", {})
        if tables and key in tables:
            entry = tables[key]
            if isinstance(entry, dict):
                return entry.get("id", "")
            return entry
        # Flat format: {"tasks": "tblXXX"}
        return self._table_ids.get(key, "")

    @property
    def tasks_table(self) -> str:
        return self._get_table_id("tasks")

    @property
    def activity_log_table(self) -> str:
        return self._get_table_id("activity_log")

    @property
    def agents_table(self) -> str:
        return self._get_table_id("agents")

    @property
    def projects_table(self) -> str:
        return self._get_table_id("projects")

    @property
    def epics_table(self) -> str:
        return self._get_table_id("epics")

    @property
    def templates_table(self) -> str:
        return self._get_table_id("task_templates")

    # --- Query methods ---

    def get_my_tasks(self, agent_name: str, status: Optional[str] = None) -> List[Dict]:
        """Get tasks assigned to an agent, optionally filtered by status."""
        conditions = [
            {"fieldId": "Assignee", "operator": "is", "value": agent_name}
        ]
        if status:
            conditions.append(
                {"fieldId": "Status", "operator": "is", "value": status}
            )
        filter_obj = build_filter(conditions)
        try:
            return self.client.get_records(
                self.tasks_table,
                filter_obj=filter_obj,
                field_key_type="name",
            )
        except Exception as e:
            print(f"[ERROR] get_my_tasks failed: {e}")
            return []

    def get_ready_tasks(self, agent_name: str) -> List[Dict]:
        """Get Ready tasks for an agent, sorted by priority then creation date."""
        filter_obj = build_filter([
            {"fieldId": "Assignee", "operator": "is", "value": agent_name},
            {"fieldId": "Status", "operator": "is", "value": "Ready"},
        ])
        try:
            records = self.client.get_records(
                self.tasks_table,
                filter_obj=filter_obj,
                field_key_type="name",
            )
            # Sort by priority (Urgent first) then by createdTime (oldest first)
            def sort_key(rec):
                fields = rec.get("fields", {})
                priority = fields.get("Priority", "Normal")
                priority_val = PRIORITY_SORT_ORDER.get(priority, 3)
                created = fields.get("Created At", "")
                return (priority_val, created)

            records.sort(key=sort_key)
            return records
        except Exception as e:
            print(f"[ERROR] get_ready_tasks failed: {e}")
            return []

    # --- Task creation ---

    def create_task(
        self,
        title: str,
        description: str,
        assignee: str,
        requester: str,
        priority: str = "Normal",
        epic_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
        workflow_ref: Optional[str] = None,
        template_source: Optional[str] = None,
    ) -> Optional[Dict]:
        """Create a new task and log the creation activity."""
        fields: Dict[str, Any] = {
            "Title": title,
            "Description": description,
            "Assignee": assignee,
            "Requester": requester,
            "Priority": priority,
            "Status": "Draft",
            "Creator": requester,
        }
        if epic_id:
            fields["Epic"] = [epic_id]
        if tags:
            fields["Tags"] = tags
        if due_date:
            fields["Due Date"] = due_date
        if workflow_ref:
            fields["Workflow Ref"] = workflow_ref
        if template_source:
            fields["Template Source"] = template_source

        try:
            result = self.client.create_records(
                self.tasks_table,
                records=[{"fields": fields}],
                typecast=True,
                field_key_type="name",
            )
            created = result.get("records", [{}])[0]
            record_id = created.get("id")
            if record_id:
                self.log_activity(
                    record_id, requester, "created",
                    details=f"Task created: {title}",
                )
            return created
        except Exception as e:
            print(f"[ERROR] create_task failed: {e}")
            return None

    # --- Status transitions ---

    def transition(
        self,
        record_id: str,
        new_status: str,
        actor: str,
        reason: Optional[str] = None,
        report: Optional[str] = None,
    ) -> bool:
        """
        Validate and execute a status transition.

        Returns True on success, False on validation failure or error.
        """
        try:
            record = self.client.get_record(
                self.tasks_table, record_id, field_key_type="name"
            )
        except Exception as e:
            print(f"[ERROR] Could not fetch task {record_id}: {e}")
            return False

        fields = record.get("fields", {})
        current_status = fields.get("Status", "Draft")
        assignee = fields.get("Assignee", "")

        # Validate transition is allowed
        transition_key = (current_status, new_status)
        rule = TRANSITIONS.get(transition_key)
        if not rule:
            print(f"[DENIED] Transition {current_status} -> {new_status} is not allowed.")
            return False

        # Check actor permission
        who = rule.get("who", "anyone")
        if who == "assignee" and actor.lower() != assignee.lower():
            print(f"[DENIED] Only assignee ({assignee}) can do {current_status} -> {new_status}.")
            return False
        if who == "yasmine" and actor.lower() != "yasmine":
            print(f"[DENIED] Only Yasmine can do {current_status} -> {new_status}.")
            return False

        # Check required fields
        if rule.get("reason_required") and not reason:
            print(f"[DENIED] Reason is required for {current_status} -> {new_status}.")
            return False
        if rule.get("report_required") and not report:
            print(f"[DENIED] Report is required for {current_status} -> {new_status}.")
            return False

        # Check dependencies for Ready -> In Progress
        if rule.get("check_deps"):
            if not self.check_dependencies(record_id):
                print(f"[BLOCKED] Task {record_id} has unresolved dependencies.")
                return False

        # Execute the transition
        update_fields: Dict[str, Any] = {
            "Status": new_status,
        }
        if new_status == "In Progress":
            update_fields["Started At"] = _now_iso()
        if new_status == "Done":
            update_fields["Completed At"] = _now_iso()
        if reason:
            update_fields["Blocked Reason"] = reason

        try:
            self.client.update_record(
                self.tasks_table, record_id, update_fields,
                typecast=True, field_key_type="name",
            )
            self.log_activity(
                record_id, actor, "status_change",
                from_val=current_status, to_val=new_status,
                details=reason or report,
            )
            return True
        except Exception as e:
            print(f"[ERROR] transition update failed: {e}")
            return False

    def start_task(self, record_id: str, agent_name: str) -> bool:
        """Ready -> In Progress. Sets Started At and updates agent's Current Task."""
        success = self.transition(record_id, "In Progress", agent_name)
        if success:
            self._update_agent_current_task(agent_name, record_id)
        return success

    def block_task(
        self,
        record_id: str,
        agent_name: str,
        reason: str,
        blocked_by_ids: Optional[List[str]] = None,
    ) -> bool:
        """In Progress -> Blocked. Records reason and optional blocker task IDs."""
        success = self.transition(record_id, "Blocked", agent_name, reason=reason)
        if success and blocked_by_ids:
            try:
                self.client.update_record(
                    self.tasks_table, record_id,
                    {"Blocked By": blocked_by_ids},
                    typecast=True, field_key_type="name",
                )
            except Exception as e:
                print(f"[WARN] Could not set Blocked By links: {e}")
        return success

    def submit_for_review(
        self,
        record_id: str,
        agent_name: str,
        summary: str,
        files_changed: Optional[List[str]] = None,
        outputs: Optional[str] = None,
        follow_ups: Optional[List[str]] = None,
    ) -> bool:
        """In Progress -> Needs Review. Populates completion report fields."""
        success = self.transition(
            record_id, "Needs Review", agent_name, report=summary
        )
        if success:
            report_fields: Dict[str, Any] = {"Report Summary": summary}
            if files_changed:
                report_fields["Report Files Changed"] = "\n".join(files_changed)
            if outputs:
                report_fields["Report Outputs"] = outputs
            if follow_ups:
                report_fields["Report Follow Ups"] = "\n".join(follow_ups)
            try:
                self.client.update_record(
                    self.tasks_table, record_id, report_fields,
                    typecast=True, field_key_type="name",
                )
            except Exception as e:
                print(f"[WARN] Could not update report fields: {e}")
            # Notify Yasmine
            self.notify("yasmine", f"Task ready for review: {record_id} - {summary[:80]}")
            self._update_agent_current_task(agent_name, "")
        return success

    def approve_task(self, record_id: str, notes: Optional[str] = None) -> bool:
        """Needs Review -> Approved -> Done. Yasmine only."""
        success = self.transition(record_id, "Approved", "Yasmine")
        if success:
            # Auto-advance to Done
            self.transition(record_id, "Done", "Yasmine", reason=notes)
            if notes:
                try:
                    self.client.update_record(
                        self.tasks_table, record_id,
                        {"Review Notes": notes},
                        typecast=True, field_key_type="name",
                    )
                except Exception as e:
                    print(f"[WARN] Could not save review notes: {e}")
        return success

    def reject_task(self, record_id: str, notes: str) -> bool:
        """Needs Review -> In Progress. Yasmine only, with rejection notes."""
        success = self.transition(record_id, "In Progress", "Yasmine", reason=notes)
        if success:
            try:
                self.client.update_record(
                    self.tasks_table, record_id,
                    {"Review Notes": notes},
                    typecast=True, field_key_type="name",
                )
            except Exception as e:
                print(f"[WARN] Could not save rejection notes: {e}")
            # Notify assignee
            record = self.client.get_record(
                self.tasks_table, record_id, field_key_type="name"
            )
            assignee = record.get("fields", {}).get("Assignee", "")
            if assignee:
                self.notify(
                    assignee,
                    f"Task rejected and sent back: {record_id} - {notes[:80]}",
                )
        return success

    # --- Dependency checking ---

    def check_dependencies(self, record_id: str) -> bool:
        """Check if all Blocked By tasks are Done. Returns True if clear."""
        try:
            record = self.client.get_record(
                self.tasks_table, record_id, field_key_type="name"
            )
            blocked_by = record.get("fields", {}).get("Blocked By", [])
            if not blocked_by:
                return True

            for dep_id in blocked_by:
                dep_record = self.client.get_record(
                    self.tasks_table, dep_id, field_key_type="name"
                )
                dep_status = dep_record.get("fields", {}).get("Status", "")
                if dep_status != "Done":
                    return False
            return True
        except Exception as e:
            print(f"[ERROR] check_dependencies failed: {e}")
            return False

    # --- Activity logging ---

    def log_activity(
        self,
        task_id: str,
        actor: str,
        action: str,
        from_val: Optional[str] = None,
        to_val: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Write a row to the Activity Log table."""
        if not self.activity_log_table:
            return
        fields: Dict[str, Any] = {
            "Name": f"{action}: {task_id[:12]}",
            "Actor": actor,
            "Action": action,
            "Timestamp": _now_iso(),
        }
        if from_val:
            fields["From Value"] = from_val
        if to_val:
            fields["To Value"] = to_val
        if details:
            fields["Details"] = details

        try:
            self.client.create_records(
                self.activity_log_table,
                records=[{"fields": fields}],
                typecast=True,
                field_key_type="name",
            )
        except Exception as e:
            print(f"[WARN] log_activity failed: {e}")

    # --- Notifications ---

    def notify(self, agent_name: str, message: str) -> bool:
        """Send a notification to an agent's Slack channel."""
        channel_info = self._get_channel(agent_name)
        if not channel_info or not channel_info.get("channel_id"):
            print(f"[NOTIFY -> {agent_name}] (no channel) {message}")
            return False
        print(f"[NOTIFY -> {agent_name}] {message}")
        return True

    def _get_channel(self, agent_name: str) -> Optional[Dict]:
        """Look up Slack channel info for an agent or Yasmine."""
        name_lower = agent_name.lower()
        if name_lower == "yasmine":
            return self._slack_channels.get("yasmine")
        return self._slack_channels.get("agents", {}).get(name_lower)

    # --- Agent helpers ---

    def _update_agent_current_task(self, agent_name: str, task_id: str) -> None:
        """Update the agent's Current Task field in the Agents table."""
        if not self.agents_table:
            return
        try:
            agents = self.client.get_records(
                self.agents_table,
                filter_obj=build_filter([
                    {"fieldId": "Name", "operator": "is", "value": agent_name}
                ]),
                field_key_type="name",
            )
            if agents:
                agent_record_id = agents[0]["id"]
                update = {"Current Task": task_id} if task_id else {"Current Task": ""}
                self.client.update_record(
                    self.agents_table, agent_record_id, update,
                    typecast=True, field_key_type="name",
                )
        except Exception as e:
            print(f"[WARN] _update_agent_current_task failed: {e}")

    # --- Daily digest ---

    def get_daily_digest(self) -> Dict[str, Any]:
        """
        Returns a digest dict with:
        - needs_review: tasks awaiting Yasmine's review
        - blocked: currently blocked tasks
        - in_progress: currently in-progress tasks
        - overdue: tasks past their due date
        - completed_yesterday: tasks completed in the last day
        """
        digest: Dict[str, Any] = {
            "needs_review": [],
            "blocked": [],
            "in_progress": [],
            "overdue": [],
            "completed_yesterday": [],
        }

        try:
            # Needs Review
            digest["needs_review"] = self.client.get_records(
                self.tasks_table,
                filter_obj=build_filter([
                    {"fieldId": "Status", "operator": "is", "value": "Needs Review"}
                ]),
                field_key_type="name",
            )

            # Blocked
            digest["blocked"] = self.client.get_records(
                self.tasks_table,
                filter_obj=build_filter([
                    {"fieldId": "Status", "operator": "is", "value": "Blocked"}
                ]),
                field_key_type="name",
            )

            # In Progress
            digest["in_progress"] = self.client.get_records(
                self.tasks_table,
                filter_obj=build_filter([
                    {"fieldId": "Status", "operator": "is", "value": "In Progress"}
                ]),
                field_key_type="name",
            )

            # Completed recently (Done status)
            all_done = self.client.get_records(
                self.tasks_table,
                filter_obj=build_filter([
                    {"fieldId": "Status", "operator": "is", "value": "Done"}
                ]),
                field_key_type="name",
            )

            # Overdue: not Done, check Due Date client-side
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            yesterday = today
            not_done = self.client.get_records(
                self.tasks_table,
                filter_obj=build_filter([
                    {"fieldId": "Status", "operator": "isNot", "value": "Done"},
                ]),
                field_key_type="name",
            )
            digest["overdue"] = [
                r for r in not_done
                if r.get("fields", {}).get("Due Date", "")
                and r.get("fields", {}).get("Due Date", "") < today
            ]

            digest["completed_yesterday"] = [
                r for r in all_done
                if r.get("fields", {}).get("Completed At", "").startswith(yesterday)
            ]

        except Exception as e:
            print(f"[ERROR] get_daily_digest failed: {e}")

        return digest


def _now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


if __name__ == "__main__":
    print("OpenClaw Task Manager - Core Module")
    print("=" * 40)
    print()
    print("Available methods on TaskManager():")
    print("  get_my_tasks(agent_name, status=None)")
    print("  get_ready_tasks(agent_name)")
    print("  create_task(title, description, assignee, requester, ...)")
    print("  transition(record_id, new_status, actor, reason=None, report=None)")
    print("  start_task(record_id, agent_name)")
    print("  block_task(record_id, agent_name, reason, blocked_by_ids=None)")
    print("  submit_for_review(record_id, agent_name, summary, ...)")
    print("  approve_task(record_id, notes=None)")
    print("  reject_task(record_id, notes)")
    print("  check_dependencies(record_id)")
    print("  log_activity(task_id, actor, action, ...)")
    print("  notify(agent_name, message)")
    print("  get_daily_digest()")
    print()
    print("Statuses:", " -> ".join(STATUSES))
    print()
    print("Config dir:", Path(__file__).parent.parent / "config")
