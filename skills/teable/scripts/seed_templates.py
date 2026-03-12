#!/usr/bin/env python3
"""
Seed the Task Templates table with 6 starter templates.

Usage:
  python3 seed_templates.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import TeableClient

CONFIG_PATH = Path(__file__).parent.parent / "config" / "table_ids.json"

TEMPLATES = [
    {
        "Name": "Cold Email Campaign",
        "Description": "Launch a targeted cold email campaign with list building, sequence writing, and monitoring",
        "Category": "campaign",
        "Default Priority": "High",
        "Default Tags": ["cold-email", "sales"],
        "Default Assignee": "Qamar",
        "Subtask Definitions": json.dumps([
            {"title": "Build lead list", "description": "Research and compile target list"},
            {"title": "Write email sequences", "description": "Draft 3-step email sequence"},
            {"title": "Set up campaign in Instantly", "description": "Configure sending"},
            {"title": "Monitor deliverability", "description": "Track opens, replies, bounces"},
        ]),
        "Workflow Ref": "",
    },
    {
        "Name": "LinkedIn Outreach Sequence",
        "Description": "Connect with target prospects on LinkedIn with personalized messaging",
        "Category": "outreach",
        "Default Priority": "Normal",
        "Default Tags": ["linkedin", "sales"],
        "Default Assignee": "Najat",
        "Subtask Definitions": json.dumps([
            {"title": "Define ICP and build target list", "description": "Identify ideal customer profiles"},
            {"title": "Write connection request templates", "description": "Personalized connection messages"},
            {"title": "Execute outreach", "description": "Send connection requests and follow-ups"},
            {"title": "Track responses and handoff", "description": "Log responses and warm leads to sales"},
        ]),
        "Workflow Ref": "",
    },
    {
        "Name": "Content Creation Sprint",
        "Description": "Plan and produce a batch of content pieces across platforms",
        "Category": "content",
        "Default Priority": "Normal",
        "Default Tags": ["content"],
        "Default Assignee": "Hana",
        "Subtask Definitions": json.dumps([
            {"title": "Research topics and keywords", "description": "SEO and audience research"},
            {"title": "Create content calendar", "description": "Schedule posts across platforms"},
            {"title": "Write and design content", "description": "Draft all pieces"},
            {"title": "Review and publish", "description": "Quality check and schedule publishing"},
        ]),
        "Workflow Ref": "",
    },
    {
        "Name": "Client Onboarding",
        "Description": "Complete onboarding process for a new client",
        "Category": "onboarding",
        "Default Priority": "Urgent",
        "Default Tags": ["client", "operations"],
        "Default Assignee": "Mariam",
        "Subtask Definitions": json.dumps([
            {"title": "Send welcome package", "description": "Welcome email, access credentials, expectations doc"},
            {"title": "Schedule kickoff call", "description": "30-min intro call with key stakeholders"},
            {"title": "Set up project workspace", "description": "Create folders, channels, tracking"},
            {"title": "Deliver first milestone", "description": "Complete and deliver initial deliverable"},
        ]),
        "Workflow Ref": "",
    },
    {
        "Name": "Technical Build Project",
        "Description": "Plan and execute a software development task",
        "Category": "build",
        "Default Priority": "High",
        "Default Tags": ["technical"],
        "Default Assignee": "Idris",
        "Subtask Definitions": json.dumps([
            {"title": "Requirements and design", "description": "Gather requirements, design architecture"},
            {"title": "Implementation", "description": "Write code, create tests"},
            {"title": "Code review", "description": "Review, fix feedback"},
            {"title": "Deploy and verify", "description": "Deploy to staging/production, verify"},
        ]),
        "Workflow Ref": "",
    },
    {
        "Name": "Market Research Report",
        "Description": "Research a market, niche, or competitor and produce an analysis report",
        "Category": "research",
        "Default Priority": "Normal",
        "Default Tags": ["research"],
        "Default Assignee": "Tariq",
        "Subtask Definitions": json.dumps([
            {"title": "Define research scope", "description": "What to research, key questions"},
            {"title": "Data collection", "description": "Gather data from sources"},
            {"title": "Analysis and synthesis", "description": "Analyze findings, identify patterns"},
            {"title": "Write and deliver report", "description": "Format findings into report doc"},
        ]),
        "Workflow Ref": "",
    },
]


def main():
    if not CONFIG_PATH.exists():
        print(f"Error: table_ids.json not found at {CONFIG_PATH}", file=sys.stderr)
        print("Run the bootstrap script first to create tables and config.", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        table_ids = json.load(f)

    # Support both nested and flat config formats
    tables = table_ids.get("tables", table_ids)
    entry = tables.get("task_templates", "")
    templates_table_id = entry.get("id", "") if isinstance(entry, dict) else entry
    if not templates_table_id:
        print("Error: 'task_templates' table ID not found in config.", file=sys.stderr)
        sys.exit(1)

    client = TeableClient()

    print(f"Seeding {len(TEMPLATES)} templates into table {templates_table_id}...\n")

    for i, template in enumerate(TEMPLATES, 1):
        record = {"fields": template}
        try:
            result = client.create_records(
                table_id=templates_table_id,
                records=[record],
                typecast=True,
            )
            created = result.get("records", [{}])[0]
            rec_id = created.get("id", "?")
            print(f"  [{i}/{len(TEMPLATES)}] {template['Name']} -> {rec_id}")
        except Exception as e:
            print(f"  [{i}/{len(TEMPLATES)}] {template['Name']} -> FAILED: {e}")

    print(f"\nDone. {len(TEMPLATES)} templates seeded.")


if __name__ == "__main__":
    main()
