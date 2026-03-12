#!/usr/bin/env python3
"""
Create complete task management system in Teable

Creates:
- Agents table (15 AI agents)
- Tasks table (with priorities, statuses, assignments)
- Projects table (with milestones, owners)
- Proper interlinking
- Multiple views

Usage:
    python3 create_task_system.py --base-id basXXXXXXXXXXXXXX
"""

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extended import extended_client as client

# 15 AI Agents data
AGENTS_DATA = [
    {"Agent Name": "Aaliyah", "Role": "Chief of Staff", "Domain": "Operations", "Discord Channel": "@AaliyaPABot", "Status": "Active"},
    {"Agent Name": "Zayd", "Role": "Strategy", "Domain": "Business Strategy", "Discord Channel": "@YasmineMarcus_Bot", "Status": "Active"},
    {"Agent Name": "Laila", "Role": "Outreach", "Domain": "LinkedIn", "Discord Channel": "@Leeiinaa_Bot", "Status": "Active"},
    {"Agent Name": "Jalila", "Role": "Sales", "Domain": "Deal Closing", "Discord Channel": "@QuinnSalesBot", "Status": "Active"},
    {"Agent Name": "Qamar", "Role": "Outreach", "Domain": "Cold Email", "Discord Channel": "@QamarColdEmailBot", "Status": "Active"},
    {"Agent Name": "Huda", "Role": "Client Success", "Domain": "Retention", "Discord Channel": "@HudaClientSuccessBot", "Status": "Active"},
    {"Agent Name": "Nadia", "Role": "Operations", "Domain": "Project Delivery", "Discord Channel": "@YasmineNadia_Bot", "Status": "Active"},
    {"Agent Name": "Zahra", "Role": "Content", "Domain": "Content Creation", "Discord Channel": "@ZahraContentBot", "Status": "Active"},
    {"Agent Name": "Suwaida", "Role": "Content", "Domain": "Social Media", "Discord Channel": "@SuwaidaSocialBot", "Status": "Active"},
    {"Agent Name": "Bilal", "Role": "Technical", "Domain": "Development", "Discord Channel": "@DevSmartCoderBot", "Status": "Active"},
    {"Agent Name": "Omar", "Role": "Systems", "Domain": "Architecture", "Discord Channel": "@YasmineEli_Bot", "Status": "Active"},
    {"Agent Name": "Noor", "Role": "Research", "Domain": "Market Intel", "Discord Channel": "@SashaResearchBot", "Status": "Active"},
    {"Agent Name": "Maida", "Role": "Finance", "Domain": "Accounting", "Discord Channel": "@JulesFinanceBot", "Status": "Active"},
    {"Agent Name": "Rahmah", "Role": "Wellbeing", "Domain": "Team Health", "Discord Channel": "@SageWellnessBot", "Status": "Active"},
    {"Agent Name": "Zayn", "Role": "Fitness", "Domain": "Health & Fitness", "Discord Channel": "@ZaynFitnessBot", "Status": "Active"},
]


def create_agents_table(base_id):
    """Create Agents table with all fields"""
    
    print("\n📊 Creating Agents table...")
    
    # Create table
    table = client.create_table(
        base_id=base_id,
        name="Agents",
        description="All 15 AI agents with roles, status, and workload"
    )
    
    table_id = table['id']
    print(f"✅ Table created: {table_id}")
    
    # Create fields
    fields_to_create = [
        {"name": "Role", "type": "singleSelect", "options": {"choices": [
            {"name": "Chief of Staff"}, {"name": "Strategy"}, {"name": "Outreach"}, 
            {"name": "Sales"}, {"name": "Client Success"}, {"name": "Operations"},
            {"name": "Content"}, {"name": "Technical"}, {"name": "Systems"},
            {"name": "Research"}, {"name": "Finance"}, {"name": "Wellbeing"}, {"name": "Fitness"}
        ]}},
        {"name": "Domain", "type": "singleLineText"},
        {"name": "Status", "type": "singleSelect", "options": {"choices": [
            {"name": "Active", "color": "green"}, 
            {"name": "Away", "color": "yellow"}, 
            {"name": "Offline", "color": "red"}
        ]}},
        {"name": "Discord Channel", "type": "singleLineText"},
        {"name": "Workload", "type": "percent"},
        {"name": "Notes", "type": "longText"},
    ]
    
    for field_def in fields_to_create:
        try:
            field = client.create_field(
                table_id=table_id,
                name=field_def['name'],
                field_type=field_def['type'],
                options=field_def.get('options')
            )
            print(f"  ✅ Field: {field_def['name']}")
        except Exception as e:
            print(f"  ⚠️  {field_def['name']}: {e}")
    
    return table_id


def create_tasks_table(base_id):
    """Create Tasks table with all fields"""
    
    print("\n📋 Creating Tasks table...")
    
    table = client.create_table(
        base_id=base_id,
        name="Tasks",
        description="All tasks across agents with priorities and statuses"
    )
    
    table_id = table['id']
    print(f"✅ Table created: {table_id}")
    
    # Create fields
    fields_to_create = [
        {"name": "Description", "type": "longText"},
        {"name": "Status", "type": "singleSelect", "options": {"choices": [
            {"name": "Open", "color": "blue"},
            {"name": "In Progress", "color": "yellow"},
            {"name": "Blocked", "color": "red"},
            {"name": "Done", "color": "green"},
            {"name": "Archived", "color": "gray"}
        ]}},
        {"name": "Priority", "type": "number"},
        {"name": "Due Date", "type": "date"},
        {"name": "Tags", "type": "multipleSelect", "options": {"choices": [
            {"name": "cold-email"}, {"name": "linkedin"}, {"name": "sales"},
            {"name": "content"}, {"name": "technical"}, {"name": "research"},
            {"name": "client"}, {"name": "operations"}
        ]}},
        {"name": "Effort", "type": "singleSelect", "options": {"choices": [
            {"name": "Small"}, {"name": "Medium"}, {"name": "Large"}, {"name": "XL"}
        ]}},
        {"name": "Notes", "type": "longText"},
    ]
    
    for field_def in fields_to_create:
        try:
            field = client.create_field(
                table_id=table_id,
                name=field_def['name'],
                field_type=field_def['type'],
                options=field_def.get('options')
            )
            print(f"  ✅ Field: {field_def['name']}")
        except Exception as e:
            print(f"  ⚠️  {field_def['name']}: {e}")
    
    return table_id


def create_projects_table(base_id):
    """Create Projects table with all fields"""
    
    print("\n🎯 Creating Projects table...")
    
    table = client.create_table(
        base_id=base_id,
        name="Projects",
        description="All projects with milestones and ownership"
    )
    
    table_id = table['id']
    print(f"✅ Table created: {table_id}")
    
    # Create fields
    fields_to_create = [
        {"name": "Description", "type": "longText"},
        {"name": "Status", "type": "singleSelect", "options": {"choices": [
            {"name": "Planning", "color": "blue"},
            {"name": "Active", "color": "green"},
            {"name": "On Hold", "color": "yellow"},
            {"name": "Complete", "color": "gray"},
            {"name": "Cancelled", "color": "red"}
        ]}},
        {"name": "Priority", "type": "singleSelect", "options": {"choices": [
            {"name": "Low"}, {"name": "Medium"}, {"name": "High"}, {"name": "Critical"}
        ]}},
        {"name": "Start Date", "type": "date"},
        {"name": "Target End Date", "type": "date"},
        {"name": "Client", "type": "singleLineText"},
        {"name": "Tags", "type": "multipleSelect", "options": {"choices": [
            {"name": "revenue"}, {"name": "internal"}, {"name": "client"}, {"name": "product"}
        ]}},
        {"name": "Notes", "type": "longText"},
    ]
    
    for field_def in fields_to_create:
        try:
            field = client.create_field(
                table_id=table_id,
                name=field_def['name'],
                field_type=field_def['type'],
                options=field_def.get('options')
            )
            print(f"  ✅ Field: {field_def['name']}")
        except Exception as e:
            print(f"  ⚠️  {field_def['name']}: {e}")
    
    return table_id


def populate_agents(table_id):
    """Populate Agents table with 15 agents"""
    
    print("\n👥 Populating Agents table...")
    
    records = [{"fields": agent} for agent in AGENTS_DATA]
    
    try:
        result = client.create_records(
            table_id=table_id,
            records=records,
            typecast=True
        )
        print(f"✅ Created {len(result['records'])} agent records")
        return result['records']
    except Exception as e:
        print(f"❌ Error populating agents: {e}")
        return []


def create_sample_tasks(table_id):
    """Create sample tasks"""
    
    print("\n📝 Creating sample tasks...")
    
    sample_tasks = [
        {
            "fields": {
                "Title": "Launch cold email campaign - Financial services",
                "Description": "Target CFOs at $5M-50M companies. Build list of 500 leads.",
                "Status": "Open",
                "Priority": 4,
                "Due Date": "2026-02-27",
                "Tags": ["cold-email", "sales"],
                "Effort": "Large"
            }
        },
        {
            "fields": {
                "Title": "LinkedIn outreach - Tech executives",
                "Description": "Connect with 100 CTOs and VP Engineering at Series A companies.",
                "Status": "In Progress",
                "Priority": 3,
                "Due Date": "2026-02-28",
                "Tags": ["linkedin", "sales"],
                "Effort": "Medium"
            }
        },
        {
            "fields": {
                "Title": "Create content calendar for March",
                "Description": "Plan 20 posts across LinkedIn, Twitter, and blog.",
                "Status": "Open",
                "Priority": 2,
                "Due Date": "2026-02-25",
                "Tags": ["content"],
                "Effort": "Medium"
            }
        },
    ]
    
    try:
        result = client.create_records(
            table_id=table_id,
            records=sample_tasks,
            typecast=True
        )
        print(f"✅ Created {len(result['records'])} sample tasks")
        return result['records']
    except Exception as e:
        print(f"❌ Error creating tasks: {e}")
        return []


def create_sample_projects(table_id):
    """Create sample projects"""
    
    print("\n🎯 Creating sample projects...")
    
    sample_projects = [
        {
            "fields": {
                "Name": "Q1 Outreach Campaign",
                "Description": "Cold email + LinkedIn outreach targeting financial services sector.",
                "Status": "Active",
                "Priority": "High",
                "Start Date": "2026-02-01",
                "Target End Date": "2026-03-31",
                "Tags": ["revenue", "client"]
            }
        },
        {
            "fields": {
                "Name": "Yumba.ai Launch",
                "Description": "AI-first sales automation platform launch and marketing.",
                "Status": "Planning",
                "Priority": "Critical",
                "Start Date": "2026-03-01",
                "Target End Date": "2026-04-30",
                "Tags": ["product", "revenue"]
            }
        },
    ]
    
    try:
        result = client.create_records(
            table_id=table_id,
            records=sample_projects,
            typecast=True
        )
        print(f"✅ Created {len(result['records'])} sample projects")
        return result['records']
    except Exception as e:
        print(f"❌ Error creating projects: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Create Teable task management system')
    parser.add_argument('--base-id', required=True, help='Teable base ID (starts with bas)')
    
    args = parser.parse_args()
    base_id = args.base_id
    
    # Accept any base ID format
    if not base_id:
        print("❌ Error: Base ID required")
        sys.exit(1)
    
    print(f"\n🚀 Creating Task Management System in base: {base_id}\n")
    print("=" * 60)
    
    # Create tables
    agents_table_id = create_agents_table(base_id)
    tasks_table_id = create_tasks_table(base_id)
    projects_table_id = create_projects_table(base_id)
    
    # Populate data
    agents = populate_agents(agents_table_id)
    tasks = create_sample_tasks(tasks_table_id)
    projects = create_sample_projects(projects_table_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("\n✅ COMPLETE! Task Management System Created\n")
    print(f"📊 Agents table: {agents_table_id} ({len(agents)} records)")
    print(f"📋 Tasks table: {tasks_table_id} ({len(tasks)} records)")
    print(f"🎯 Projects table: {projects_table_id} ({len(projects)} records)")
    print(f"\n🔗 View in Teable: https://app.teable.ai/base/{base_id}")
    print("\nNext steps:")
    print("1. Open Teable web UI")
    print("2. Create link fields to connect tables")
    print("3. Create Kanban/Calendar views")
    print("4. Start using for task management!")
    

if __name__ == '__main__':
    main()
