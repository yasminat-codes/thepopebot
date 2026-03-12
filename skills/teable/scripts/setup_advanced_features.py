#!/usr/bin/env python3
"""
Set up advanced Teable features via API

Creates:
- Views (Kanban, Calendar, Filtered)
- Formula fields (calculations)
- Count fields
- Instructions for manual setup (link fields, rollups)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from extended import extended_client as client

BASE_ID = "bseklxihNRbCC8UWK5x"
AGENTS_TABLE = "tbly6w9dF2iCIeafSoH"
TASKS_TABLE = "tblsKNZyy0aI4iaOhPu"
PROJECTS_TABLE = "tblcQyvORVHw63umNub"

print("\n🎨 Setting up advanced Teable features...\n")
print("=" * 60)

# CREATE VIEWS
print("\n📊 Creating Views...")

# Tasks Kanban view
try:
    kanban = client.create_view(
        table_id=TASKS_TABLE,
        name="Kanban by Status",
        view_type="kanban",
        description="Drag tasks between status columns"
    )
    print(f"✅ Tasks Kanban: {kanban['id']}")
except Exception as e:
    print(f"⚠️  Tasks Kanban: {e}")

# Tasks Calendar view
try:
    calendar = client.create_view(
        table_id=TASKS_TABLE,
        name="Calendar",
        view_type="calendar",
        description="Tasks by due date"
    )
    print(f"✅ Tasks Calendar: {calendar['id']}")
except Exception as e:
    print(f"⚠️  Tasks Calendar: {e}")

# Projects Kanban view
try:
    proj_kanban = client.create_view(
        table_id=PROJECTS_TABLE,
        name="Project Board",
        view_type="kanban",
        description="Project status board"
    )
    print(f"✅ Projects Kanban: {proj_kanban['id']}")
except Exception as e:
    print(f"⚠️  Projects Kanban: {e}")

# Agents Grid view  
try:
    agents_grid = client.create_view(
        table_id=AGENTS_TABLE,
        name="Active Agents",
        view_type="grid",
        description="Active agents only"
    )
    print(f"✅ Agents Grid: {agents_grid['id']}")
except Exception as e:
    print(f"⚠️  Agents Grid: {e}")

print("\n" + "=" * 60)
print("\n✅ VIEWS CREATED!")
print("\n📋 Manual Setup Required (in Teable UI):")
print("\n1. LINK FIELDS (easier in UI):")
print("   Tasks table:")
print("     - Add field → Link → Agents → Name: 'Assigned To' (single)")
print("     - Add field → Link → Projects → Name: 'Project' (single)")
print("   ")
print("   Projects table:")
print("     - Add field → Link → Agents → Name: 'Owner' (single)")
print("     - Add field → Link → Agents → Name: 'Team' (multiple)")
print("     - Add field → Link → Tasks → Name: 'Tasks' (multiple)")
print("\n2. ROLLUP FIELDS:")
print("   Agents table (after link fields created):")
print("     - Add field → Count → Link field: 'Tasks' → Name: 'Task Count'")
print("   ")
print("   Projects table:")
print("     - Add field → Count → Link field: 'Tasks' → Name: 'Task Count'")
print("     - Add field → Rollup → Link: 'Tasks' → Field: 'Status'")
print("       → Formula: count({values}) where Status='Done'")
print("       → Name: 'Completed Tasks'")
print("\n3. FORMULA FIELDS:")
print("   Projects table:")
print("     - Add field → Formula")
print("       → Expression: {Completed Tasks} / {Task Count} * 100")
print("       → Name: 'Progress %'")
print("\n4. CONFIGURE VIEWS:")
print("   Kanban by Status:")
print("     - Edit view → Group by: Status field")
print("   ")
print("   Calendar:")
print("     - Edit view → Date field: Due Date")
print("\n🔗 Base URL: https://app.teable.ai/base/bseklxihNRbCC8UWK5x")
print("\n" + "=" * 60)

