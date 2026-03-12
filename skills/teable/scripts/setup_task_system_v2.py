#!/usr/bin/env python3
"""
Bootstrap the OpenClaw Task Management System v2 in Teable.

Creates 6 tables (Projects, Epics, Tasks, Activity Log, Task Templates, Agents),
their fields, views, and seeds the 16 agents.

Usage:
    python3 setup_task_system_v2.py --base-id basXXXXXXXXXXXXXX
    python3 setup_task_system_v2.py --base-id basXXXXXXXXXXXXXX --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# --- Constants ---

AGENT_NAMES = [
    "Amira", "Rashid", "Fatima", "Layla", "Salma", "Qamar", "Najat", "Tariq",
    "Yusuf", "Idris", "Zahra", "Mariam", "Rafi", "Hana", "Aisha", "Hamza",
]

AGENT_NAMES_PLUS_YASMINE = AGENT_NAMES + ["Yasmine"]
ACTIVITY_ACTORS = AGENT_NAMES_PLUS_YASMINE + ["System"]

AGENTS_DATA = [
    {"Name": "Amira", "Role": "Personal Assistant", "Team": "Operations", "Status": "Active", "Slack Channel": "#amira-personal-assistant", "Slack Channel ID": "C0AF4HR9SJX", "Max Concurrent": 1},
    {"Name": "Rashid", "Role": "Business Strategist", "Team": "Operations", "Status": "Active", "Slack Channel": "#rashid-business-strategist", "Slack Channel ID": "C0AFF5HL876", "Max Concurrent": 1},
    {"Name": "Fatima", "Role": "Finance Manager", "Team": "Operations", "Status": "Active", "Slack Channel": "#fatima-finance-manager", "Slack Channel ID": "C0AFF5X6HM2", "Max Concurrent": 1},
    {"Name": "Layla", "Role": "Sales Lead", "Team": "Revenue Pipeline", "Status": "Active", "Slack Channel": "#layla-sales-lead", "Slack Channel ID": "C0AFF5N6KSQ", "Max Concurrent": 1},
    {"Name": "Salma", "Role": "Outreach Specialist", "Team": "Revenue Pipeline", "Status": "Active", "Slack Channel": "#salma-outreach-specialist", "Slack Channel ID": "C0AF9FDEH6J", "Max Concurrent": 1},
    {"Name": "Qamar", "Role": "Cold Email Specialist", "Team": "Revenue Pipeline", "Status": "Active", "Slack Channel": "#qamar-cold-email-specialist", "Slack Channel ID": "C0AGFUBL0RX", "Max Concurrent": 1},
    {"Name": "Najat", "Role": "LinkedIn Specialist", "Team": "Revenue Pipeline", "Status": "Active", "Slack Channel": "#najat-linkedin-specialist", "Slack Channel ID": "C0AJA1NCW94", "Max Concurrent": 1},
    {"Name": "Tariq", "Role": "Research Analyst", "Team": "Revenue Pipeline", "Status": "Active", "Slack Channel": "#tariq-research-analyst", "Slack Channel ID": "C0AG5RNTYGY", "Max Concurrent": 1},
    {"Name": "Yusuf", "Role": "Project Manager", "Team": "Client Delivery", "Status": "Active", "Slack Channel": "#yusuf-project-manager", "Slack Channel ID": "C0AFBHE00JE", "Max Concurrent": 1},
    {"Name": "Idris", "Role": "Lead Developer", "Team": "Client Delivery", "Status": "Active", "Slack Channel": "#idris-lead-developer", "Slack Channel ID": "C0AF9FLFBL6", "Max Concurrent": 1},
    {"Name": "Zahra", "Role": "Systems Architect", "Team": "Client Delivery", "Status": "Active", "Slack Channel": "#zahra-systems-architect", "Slack Channel ID": "C0AEW3Z7G31", "Max Concurrent": 1},
    {"Name": "Mariam", "Role": "Client Success", "Team": "Client Delivery", "Status": "Active", "Slack Channel": "#mariam-client-success", "Slack Channel ID": "C0AF84R2NE9", "Max Concurrent": 1},
    {"Name": "Rafi", "Role": "Tech Support", "Team": "Client Delivery", "Status": "Active", "Slack Channel": "#rafi-tech-support", "Slack Channel ID": "C0AK6BK6CBA", "Max Concurrent": 1},
    {"Name": "Hana", "Role": "Content Specialist", "Team": "Content & Brand", "Status": "Active", "Slack Channel": "#hana-content-specialist", "Slack Channel ID": "C0AF55YUG1H", "Max Concurrent": 1},
    {"Name": "Aisha", "Role": "Wellness Coach", "Team": "Wellness", "Status": "Active", "Slack Channel": "#aisha-wellness-coach", "Slack Channel ID": "C0AFQF5HKHP", "Max Concurrent": 1},
    {"Name": "Hamza", "Role": "DevOps Engineer", "Team": "Client Delivery", "Status": "Active", "Slack Channel": "#hamza-devops", "Slack Channel ID": "", "Max Concurrent": 1},
]

# --- Table Definitions ---

def _choices(names, color_map=None):
    """Build singleSelect/multipleSelect choices list."""
    if color_map:
        return [{"name": n, "color": color_map.get(n, "blue")} for n in names]
    return [{"name": n} for n in names]


PRIORITY_CHOICES = _choices(["Urgent", "High", "Normal", "Low"])
TASK_STATUS_COLORS = {
    "Draft": "gray", "Backlog": "blue", "Ready": "cyan",
    "In Progress": "yellow", "Blocked": "red", "Needs Review": "orange",
    "Approved": "purple", "Done": "green",
}
TASK_TAGS = [
    "cold-email", "linkedin", "sales", "content", "technical",
    "research", "client", "operations", "automation", "finance",
]

TABLES_SPEC = {
    "projects": {
        "name": "Projects",
        "description": "All projects with ownership and tracking",
        "fields": [
            {"name": "Description", "type": "longText"},
            {"name": "Status", "type": "singleSelect", "options": {"choices": _choices(
                ["Planning", "Active", "On Hold", "Complete", "Cancelled"],
                {"Planning": "blue", "Active": "green", "On Hold": "yellow", "Complete": "gray", "Cancelled": "red"},
            )}},
            {"name": "Priority", "type": "singleSelect", "options": {"choices": PRIORITY_CHOICES}},
            {"name": "Owner", "type": "singleSelect", "options": {"choices": _choices(AGENT_NAMES_PLUS_YASMINE)}},
            {"name": "Start Date", "type": "date"},
            {"name": "Target End Date", "type": "date"},
            {"name": "Tags", "type": "multipleSelect", "options": {"choices": _choices(
                ["revenue", "internal", "client", "product", "infrastructure"],
            )}},
            {"name": "Notes", "type": "longText"},
        ],
        "views": [
            {"name": "Active Projects", "type": "kanban"},
            {"name": "All Projects", "type": "grid"},
        ],
    },
    "epics": {
        "name": "Epics",
        "description": "High-level epics grouping related tasks",
        "fields": [
            {"name": "Description", "type": "longText"},
            {"name": "Status", "type": "singleSelect", "options": {"choices": _choices(
                ["Draft", "Backlog", "Ready", "In Progress", "Done"],
                {"Draft": "gray", "Backlog": "blue", "Ready": "cyan", "In Progress": "yellow", "Done": "green"},
            )}},
            {"name": "Owner", "type": "singleSelect", "options": {"choices": _choices(AGENT_NAMES_PLUS_YASMINE)}},
            {"name": "Priority", "type": "singleSelect", "options": {"choices": PRIORITY_CHOICES}},
            {"name": "Target Date", "type": "date"},
        ],
        "views": [
            {"name": "Active Epics", "type": "grid"},
        ],
    },
    "tasks": {
        "name": "Tasks",
        "description": "Core task table for all agent work",
        "fields": [
            {"name": "Description", "type": "longText"},
            {"name": "Status", "type": "singleSelect", "options": {"choices": _choices(
                list(TASK_STATUS_COLORS.keys()), TASK_STATUS_COLORS,
            )}},
            {"name": "Priority", "type": "singleSelect", "options": {"choices": PRIORITY_CHOICES}},
            {"name": "Assignee", "type": "singleSelect", "options": {"choices": _choices(AGENT_NAMES)}},
            {"name": "Requester", "type": "singleSelect", "options": {"choices": _choices(AGENT_NAMES_PLUS_YASMINE)}},
            {"name": "Creator", "type": "singleSelect", "options": {"choices": _choices(AGENT_NAMES_PLUS_YASMINE)}},
            {"name": "Due Date", "type": "date"},
            {"name": "Tags", "type": "multipleSelect", "options": {"choices": _choices(TASK_TAGS)}},
            {"name": "Template Source", "type": "singleLineText"},
            {"name": "Workflow Ref", "type": "singleLineText"},
            {"name": "Started At", "type": "date"},
            {"name": "Completed At", "type": "date"},
            {"name": "Report Summary", "type": "longText"},
            {"name": "Report Files Changed", "type": "longText"},
            {"name": "Report Outputs", "type": "longText"},
            {"name": "Report Follow Ups", "type": "longText"},
            {"name": "Blocked Reason", "type": "singleLineText"},
            {"name": "Review Notes", "type": "longText"},
        ],
        "views": [
            {"name": "Kanban Board", "type": "kanban"},
            {"name": "Needs Review", "type": "grid"},
            {"name": "Blocked Tasks", "type": "grid"},
            {"name": "Ready Queue", "type": "grid"},
            {"name": "Recently Completed", "type": "grid"},
            {"name": "Calendar", "type": "calendar"},
        ],
        "agent_views": True,
    },
    "activity_log": {
        "name": "Activity Log",
        "description": "Audit trail of all task activity",
        "fields": [
            {"name": "Actor", "type": "singleSelect", "options": {"choices": _choices(ACTIVITY_ACTORS)}},
            {"name": "Action", "type": "singleSelect", "options": {"choices": _choices([
                "created", "assigned", "status_changed", "commented", "blocked",
                "unblocked", "reviewed", "approved", "completed", "reopened",
            ])}},
            {"name": "From Value", "type": "singleLineText"},
            {"name": "To Value", "type": "singleLineText"},
            {"name": "Details", "type": "longText"},
            {"name": "Timestamp", "type": "date"},
        ],
        "views": [],
    },
    "task_templates": {
        "name": "Task Templates",
        "description": "Reusable task templates with default values",
        "fields": [
            {"name": "Description", "type": "longText"},
            {"name": "Category", "type": "singleSelect", "options": {"choices": _choices([
                "campaign", "build", "research", "content", "onboarding", "maintenance", "outreach",
            ])}},
            {"name": "Default Priority", "type": "singleSelect", "options": {"choices": PRIORITY_CHOICES}},
            {"name": "Default Tags", "type": "multipleSelect", "options": {"choices": _choices(TASK_TAGS)}},
            {"name": "Default Assignee", "type": "singleSelect", "options": {"choices": _choices(AGENT_NAMES)}},
            {"name": "Subtask Definitions", "type": "longText"},
            {"name": "Workflow Ref", "type": "singleLineText"},
        ],
        "views": [],
    },
    "agents": {
        "name": "Agents",
        "description": "All 16 OpenClaw AI agents",
        "fields": [
            {"name": "Role", "type": "singleSelect", "options": {"choices": _choices([
                "Personal Assistant", "Business Strategist", "Finance Manager",
                "Sales Lead", "Outreach Specialist", "Cold Email Specialist",
                "LinkedIn Specialist", "Research Analyst", "Project Manager",
                "Lead Developer", "Systems Architect", "Client Success",
                "Tech Support", "Content Specialist", "Wellness Coach", "DevOps Engineer",
            ])}},
            {"name": "Team", "type": "singleSelect", "options": {"choices": _choices([
                "Operations", "Revenue Pipeline", "Client Delivery", "Content & Brand", "Wellness",
            ])}},
            {"name": "Status", "type": "singleSelect", "options": {"choices": _choices(
                ["Active", "Away", "Offline"],
                {"Active": "green", "Away": "yellow", "Offline": "red"},
            )}},
            {"name": "Slack Channel", "type": "singleLineText"},
            {"name": "Slack Channel ID", "type": "singleLineText"},
            {"name": "Max Concurrent", "type": "number"},
        ],
        "views": [],
    },
}

# --- Helpers ---

def create_client():
    """Create a fresh TeableExtendedClient (avoids module-level init failures)."""
    from extended import TeableExtendedClient
    return TeableExtendedClient()


def create_table_with_fields(client, base_id, key, spec, dry_run=False):
    """Create a single table and all its fields. Returns (table_id, view_ids_dict)."""
    name = spec["name"]

    if dry_run:
        print(f"\n[DRY RUN] Would create table: {name}")
        for f in spec["fields"]:
            print(f"  [DRY RUN] Field: {f['name']} ({f['type']})")
        return f"tbl_dry_{key}", {}

    print(f"\nCreating table: {name}...")
    table = client.create_table(base_id=base_id, name=name, description=spec.get("description"))
    table_id = table["id"]
    print(f"  Table created: {table_id}")

    for field_def in spec["fields"]:
        try:
            client.create_field(
                table_id=table_id,
                name=field_def["name"],
                field_type=field_def["type"],
                options=field_def.get("options"),
            )
            print(f"  Field: {field_def['name']}")
        except Exception as e:
            print(f"  WARN {field_def['name']}: {e}")

    return table_id, {}


def create_views_for_table(client, table_id, spec, dry_run=False):
    """Create views for a table. Returns dict of view name -> view id."""
    views = {}
    for view_def in spec.get("views", []):
        vname = view_def["name"]
        vtype = view_def["type"]
        if dry_run:
            print(f"  [DRY RUN] View: {vname} ({vtype})")
            views[vname] = f"viw_dry_{vname}"
            continue
        try:
            v = client.create_view(table_id=table_id, name=vname, view_type=vtype)
            views[vname] = v["id"]
            print(f"  View: {vname} ({vtype}) -> {v['id']}")
        except Exception as e:
            print(f"  WARN view {vname}: {e}")

    # Per-agent views for Tasks table
    if spec.get("agent_views"):
        for agent in AGENT_NAMES:
            vname = f"My Tasks - {agent}"
            if dry_run:
                print(f"  [DRY RUN] Agent view: {vname}")
                views[vname] = f"viw_dry_{agent}"
                continue
            try:
                v = client.create_view(table_id=table_id, name=vname, view_type="grid")
                views[vname] = v["id"]
                print(f"  Agent view: {vname} -> {v['id']}")
            except Exception as e:
                print(f"  WARN agent view {vname}: {e}")

    return views


def seed_agents(client, table_id, dry_run=False):
    """Seed the Agents table with 16 agents."""
    if dry_run:
        print(f"\n[DRY RUN] Would seed {len(AGENTS_DATA)} agents")
        return

    print(f"\nSeeding {len(AGENTS_DATA)} agents...")
    records = [{"fields": agent} for agent in AGENTS_DATA]
    try:
        result = client.create_records(table_id=table_id, records=records, typecast=True)
        print(f"  Created {len(result.get('records', []))} agent records")
    except Exception as e:
        print(f"  ERROR seeding agents: {e}")


def build_config(base_id, table_ids, view_ids):
    """Build the table_ids.json config structure."""
    config = {"base_id": base_id, "tables": {}}

    # Projects
    pv = view_ids.get("projects", {})
    config["tables"]["projects"] = {
        "id": table_ids["projects"],
        "views": {
            "kanban": pv.get("Active Projects", ""),
            "grid": pv.get("All Projects", ""),
        },
    }

    # Epics
    ev = view_ids.get("epics", {})
    config["tables"]["epics"] = {
        "id": table_ids["epics"],
        "views": {
            "grid": ev.get("Active Epics", ""),
        },
    }

    # Tasks
    tv = view_ids.get("tasks", {})
    agent_views = {}
    for agent in AGENT_NAMES:
        agent_views[agent.lower()] = tv.get(f"My Tasks - {agent}", "")
    config["tables"]["tasks"] = {
        "id": table_ids["tasks"],
        "views": {
            "kanban": tv.get("Kanban Board", ""),
            "needs_review": tv.get("Needs Review", ""),
            "blocked": tv.get("Blocked Tasks", ""),
            "ready_queue": tv.get("Ready Queue", ""),
            "completed": tv.get("Recently Completed", ""),
            "calendar": tv.get("Calendar", ""),
            "agent_views": agent_views,
        },
    }

    # Simple tables (no views defined)
    config["tables"]["activity_log"] = {"id": table_ids["activity_log"]}
    config["tables"]["task_templates"] = {"id": table_ids["task_templates"]}
    config["tables"]["agents"] = {"id": table_ids["agents"]}

    return config


def write_config(config, dry_run=False):
    """Write table_ids.json to skills/teable/config/."""
    config_dir = Path(__file__).parent.parent / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "table_ids.json"

    if dry_run:
        print(f"\n[DRY RUN] Would write config to: {config_path}")
        print(json.dumps(config, indent=2))
        return

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\nConfig written to: {config_path}")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Bootstrap OpenClaw Task Management System v2 in Teable")
    parser.add_argument("--base-id", required=True, help="Teable base ID (starts with bas)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created without making API calls")
    args = parser.parse_args()

    base_id = args.base_id
    dry_run = args.dry_run

    if not base_id:
        print("ERROR: Base ID required")
        sys.exit(1)

    client = None
    if not dry_run:
        client = create_client()

    mode = "[DRY RUN] " if dry_run else ""
    print(f"\n{mode}Creating OpenClaw Task Management System v2")
    print(f"Base: {base_id}")
    print("=" * 60)

    # Phase 1: Create all tables and fields
    print("\n--- Phase 1: Tables & Fields ---")
    table_ids = {}
    table_order = ["projects", "epics", "tasks", "activity_log", "task_templates", "agents"]
    for key in table_order:
        spec = TABLES_SPEC[key]
        tid, _ = create_table_with_fields(client, base_id, key, spec, dry_run=dry_run)
        table_ids[key] = tid

    # NOTE: Link fields (e.g. Tasks -> Projects, Tasks -> Epics) should be
    # configured manually in the Teable UI after bootstrap, as the API for
    # creating bidirectional link fields between existing tables is complex.

    # Phase 2: Create views
    print("\n--- Phase 2: Views ---")
    view_ids = {}
    for key in table_order:
        spec = TABLES_SPEC[key]
        if spec.get("views") or spec.get("agent_views"):
            print(f"\nViews for {spec['name']}:")
            view_ids[key] = create_views_for_table(client, table_ids[key], spec, dry_run=dry_run)

    # Phase 3: Seed agents
    print("\n--- Phase 3: Seed Agents ---")
    seed_agents(client, table_ids["agents"], dry_run=dry_run)

    # Phase 4: Write config
    print("\n--- Phase 4: Config ---")
    config = build_config(base_id, table_ids, view_ids)
    write_config(config, dry_run=dry_run)

    # Summary
    print("\n" + "=" * 60)
    print(f"\n{mode}COMPLETE! OpenClaw Task Management System v2")
    print(f"\nTables created: {len(table_ids)}")
    for key, tid in table_ids.items():
        vcount = len(view_ids.get(key, {}))
        suffix = f" ({vcount} views)" if vcount else ""
        print(f"  {TABLES_SPEC[key]['name']}: {tid}{suffix}")
    print(f"\nView in Teable: https://app.teable.ai/base/{base_id}")
    print("\nNext steps:")
    print("1. Open Teable UI and configure link fields between tables")
    print("2. Set up view filters (Needs Review, Blocked, etc.)")
    print("3. Start creating tasks!")


if __name__ == "__main__":
    main()
