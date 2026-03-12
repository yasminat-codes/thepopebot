#!/usr/bin/env python3
"""
Create the Skills Pipeline table in the OpenClaw Teable base.

Adds an 8th table to base bseMapd4GGreO0szW6i so Zahra can pick up
skill-build tasks on her heartbeat, the same way agents pick up regular tasks.

Usage:
    export TEABLE_API_TOKEN="<your-token>"
    python3 create_skills_table.py
    python3 create_skills_table.py --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BASE_ID = "bseMapd4GGreO0szW6i"

AGENT_NAMES = [
    "Amira", "Rashid", "Fatima", "Layla", "Salma", "Qamar", "Najat", "Tariq",
    "Yusuf", "Idris", "Zahra", "Mariam", "Rafi", "Hana", "Aisha", "Hamza",
]

TARGET_AGENT_CHOICES = [{"name": n} for n in (["All"] + AGENT_NAMES)]

BUILDER_CHOICES = [{"name": n} for n in AGENT_NAMES]

STATUS_CHOICES = [
    {"name": "Backlog",     "color": "blue"},
    {"name": "In Progress", "color": "yellow"},
    {"name": "Needs Review","color": "orange"},
    {"name": "Done",        "color": "green"},
]

PRIORITY_CHOICES = [
    {"name": "Urgent", "color": "red"},
    {"name": "High",   "color": "orange"},
    {"name": "Normal", "color": "blue"},
    {"name": "Low",    "color": "gray"},
]

CATEGORY_CHOICES = [
    {"name": "agent-tools"},
    {"name": "workflow"},
    {"name": "integration"},
    {"name": "content"},
    {"name": "operations"},
    {"name": "research"},
    {"name": "outreach"},
]

# Fields to create (Name is auto-created as primary by Teable)
FIELDS = [
    {"name": "Description",     "type": "longText"},
    {"name": "Workspace",       "type": "singleLineText"},
    {"name": "Target Agent",    "type": "singleSelect",
     "options": {"choices": TARGET_AGENT_CHOICES}},
    {"name": "Builder",         "type": "singleSelect",
     "options": {"choices": BUILDER_CHOICES}},
    {"name": "Creation Skill",  "type": "singleLineText"},
    {"name": "Reference Path",  "type": "singleLineText"},
    {"name": "Best Practices",  "type": "longText"},
    {"name": "Status",          "type": "singleSelect",
     "options": {"choices": STATUS_CHOICES}},
    {"name": "Priority",        "type": "singleSelect",
     "options": {"choices": PRIORITY_CHOICES}},
    {"name": "Category",        "type": "singleSelect",
     "options": {"choices": CATEGORY_CHOICES}},
    {"name": "Started At",      "type": "date"},
    {"name": "Completed At",    "type": "date"},
]


def create_client():
    from extended import TeableExtendedClient
    return TeableExtendedClient()


def delete_auto_fields(client, table_id):
    """Delete Teable's auto-created Count and Status fields."""
    try:
        fields = client.list_fields(table_id)
        for field in fields:
            if field.get("name") in ("Count", "Status") and field.get("isPrimary") is not True:
                try:
                    client.delete_field(table_id, field["id"])
                    print(f"  Deleted auto-field: {field['name']} ({field['id']})")
                except Exception as e:
                    print(f"  WARN delete {field['name']}: {e}")
    except Exception as e:
        print(f"  WARN listing fields for cleanup: {e}")


def main():
    parser = argparse.ArgumentParser(description="Create Skills Pipeline table in Teable")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be created without making API calls")
    args = parser.parse_args()
    dry_run = args.dry_run

    mode = "[DRY RUN] " if dry_run else ""
    print(f"\n{mode}Creating Skills Pipeline table")
    print(f"Base: {BASE_ID}")
    print("=" * 60)

    client = None
    if not dry_run:
        client = create_client()

    # Step 1: Create table
    if dry_run:
        print("\n[DRY RUN] Would create table: Skills Pipeline")
        table_id = "tbl_dry_skills_pipeline"
    else:
        print("\nCreating table: Skills Pipeline...")
        table = client.create_table(
            base_id=BASE_ID,
            name="Skills Pipeline",
            description="Tracks skill creation requests so Zahra can pick them up on heartbeat",
        )
        table_id = table["id"]
        print(f"  Table created: {table_id}")

    # Step 2: Delete auto-created Count/Status fields
    if not dry_run:
        print("\nCleaning up auto-created fields...")
        delete_auto_fields(client, table_id)

    # Step 3: Create all custom fields
    print(f"\nCreating {len(FIELDS)} fields...")
    for field_def in FIELDS:
        if dry_run:
            print(f"  [DRY RUN] Field: {field_def['name']} ({field_def['type']})")
            continue
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

    # Summary
    print("\n" + "=" * 60)
    print(f"\n{mode}COMPLETE!")
    print(f"\nTable: Skills Pipeline")
    print(f"Table ID: {table_id}")
    if not dry_run:
        print(f"\nView in Teable: https://app.teable.ai/base/{BASE_ID}")
        print(f"\nNext steps:")
        print(f"1. Add table ID to shared/TASK-SYSTEM.md")
        print(f"2. Optionally seed starter skill entries")


if __name__ == "__main__":
    main()
