#!/usr/bin/env python3
"""
Sync ClickUp projects with Airtable client/project records.

Rules:
- New active client in Airtable → Create ClickUp Folder
- Project status updates in ClickUp → Update Airtable record
- Time tracked in ClickUp → Sum to Airtable hours field

Usage:
    python sync_airtable.py --push     # Push ClickUp updates to Airtable
    python sync_airtable.py --pull     # Pull Airtable clients to ClickUp
    python sync_airtable.py --full     # Full bidirectional sync
    python sync_airtable.py --status   # Show sync status
    python sync_airtable.py --setup    # Interactive setup for Airtable base
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

AIRTABLE_SCRIPT = Path("/home/clawdbot/clawd/skills/airtable/scripts/airtable_client.py")

# Configuration - update these with your actual IDs
CONFIG = {
    "airtable_base_id": None,  # Set during setup or via --base-id
    "clients_table": "Clients",
    "projects_table": "Projects",
    "clickup_space_name": "Clients"
}

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

def load_config():
    """Load config from file."""
    global CONFIG
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            CONFIG.update(json.load(f))
    return CONFIG

def save_config():
    """Save config to file."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(CONFIG, f, indent=2)

def run_command(cmd: str) -> tuple[int, str, str]:
    """Run shell command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def mcporter_call(tool_call: str) -> dict:
    """Execute mcporter call and return result."""
    cmd = f"mcporter call '{tool_call}'"
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        print(f"mcporter error: {stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}

def airtable_call(action: str, *args) -> dict:
    """Call Airtable client script."""
    cmd = f"python3 {AIRTABLE_SCRIPT} {action} {' '.join(args)}"
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        print(f"Airtable error: {stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}

def get_airtable_clients() -> list:
    """Get all clients from Airtable."""
    if not CONFIG.get("airtable_base_id"):
        print("Error: Airtable base ID not configured. Run --setup first.")
        return []
    
    result = airtable_call("list-records", CONFIG["airtable_base_id"], CONFIG["clients_table"])
    if result and "records" in result:
        return result["records"]
    return []

def get_airtable_projects() -> list:
    """Get all projects from Airtable."""
    if not CONFIG.get("airtable_base_id"):
        return []
    
    result = airtable_call("list-records", CONFIG["airtable_base_id"], CONFIG["projects_table"])
    if result and "records" in result:
        return result["records"]
    return []

def update_airtable_record(table: str, record_id: str, fields: dict):
    """Update an Airtable record."""
    fields_json = json.dumps(fields)
    return airtable_call("update-record", CONFIG["airtable_base_id"], table, record_id, f"'{fields_json}'")

def get_clickup_workspace():
    """Get ClickUp workspace hierarchy."""
    return mcporter_call("clickup.clickup_get_workspace_hierarchy(limit: 100)")

def get_clickup_clients_space(hierarchy: dict) -> dict:
    """Find Clients space in ClickUp."""
    for space in hierarchy.get("spaces", []):
        if space.get("name", "").lower() == CONFIG["clickup_space_name"].lower():
            return space
    return None

def create_clickup_folder(space_id: str, name: str) -> dict:
    """Create a folder in ClickUp."""
    return mcporter_call(f'clickup.clickup_create_folder(space_id: "{space_id}", name: "{name}")')

def get_time_entries_for_folder(folder_id: str) -> int:
    """Get total time tracked for a folder (all tasks)."""
    # This would need to iterate through all tasks in the folder
    # For now, return 0 - implement based on your needs
    return 0

def pull_clients_to_clickup():
    """Pull new clients from Airtable and create ClickUp folders."""
    print("Fetching Airtable clients...")
    clients = get_airtable_clients()
    active_clients = [c for c in clients if c.get("fields", {}).get("Status", "").lower() in ["active", "onboarding"]]
    print(f"Found {len(active_clients)} active clients")
    
    print("\nFetching ClickUp workspace...")
    hierarchy = get_clickup_workspace()
    if not hierarchy:
        print("Error: Could not fetch ClickUp workspace")
        return
    
    clients_space = get_clickup_clients_space(hierarchy)
    if not clients_space:
        print(f"Error: No '{CONFIG['clickup_space_name']}' space found in ClickUp")
        return
    
    space_id = clients_space.get("id")
    existing_folders = {f.get("name", "").lower(): f for f in clients_space.get("folders", [])}
    
    created = 0
    skipped = 0
    
    for client in active_clients:
        client_name = client.get("fields", {}).get("Name", "Unknown")
        
        # Check if folder already exists
        if client_name.lower() in existing_folders:
            skipped += 1
            continue
        
        # Create folder
        result = create_clickup_folder(space_id, client_name)
        if result and result.get("id"):
            print(f"  ✓ Created folder: {client_name}")
            
            # Update Airtable with ClickUp folder ID
            update_airtable_record(
                CONFIG["clients_table"],
                client.get("id"),
                {"ClickUp Folder ID": result.get("id")}
            )
            created += 1
        else:
            print(f"  ✗ Failed to create: {client_name}")
    
    print(f"\nPull complete: {created} folders created, {skipped} already existed")

def push_status_to_airtable():
    """Push ClickUp project status updates to Airtable."""
    print("Fetching ClickUp workspace...")
    hierarchy = get_clickup_workspace()
    if not hierarchy:
        print("Error: Could not fetch ClickUp workspace")
        return
    
    clients_space = get_clickup_clients_space(hierarchy)
    if not clients_space:
        return
    
    print("Fetching Airtable projects...")
    projects = get_airtable_projects()
    
    # Build lookup by ClickUp ID
    projects_by_clickup_id = {}
    for project in projects:
        cid = project.get("fields", {}).get("ClickUp List ID")
        if cid:
            projects_by_clickup_id[cid] = project
    
    updated = 0
    
    # Check each folder/list in ClickUp
    for folder in clients_space.get("folders", []):
        for list_item in folder.get("lists", []):
            list_id = list_item.get("id")
            list_name = list_item.get("name")
            
            if list_id in projects_by_clickup_id:
                project = projects_by_clickup_id[list_id]
                
                # Get task stats for this list
                # Count completed vs total tasks
                # This is simplified - you'd want more detailed logic
                
                # For now, just sync the name
                current_name = project.get("fields", {}).get("Name")
                if current_name != list_name:
                    update_airtable_record(
                        CONFIG["projects_table"],
                        project.get("id"),
                        {"Name": list_name}
                    )
                    print(f"  ✓ Updated: {list_name}")
                    updated += 1
    
    print(f"\nPush complete: {updated} projects updated")

def show_status():
    """Show sync status between ClickUp and Airtable."""
    print("=== ClickUp ↔ Airtable Sync Status ===\n")
    
    config = load_config()
    if not config.get("airtable_base_id"):
        print("❌ Airtable base not configured. Run: python sync_airtable.py --setup")
        return
    
    print(f"Airtable Base ID: {config['airtable_base_id']}")
    print(f"Clients Table: {config['clients_table']}")
    print(f"Projects Table: {config['projects_table']}")
    print(f"ClickUp Space: {config['clickup_space_name']}")
    
    # Get counts
    clients = get_airtable_clients()
    projects = get_airtable_projects()
    
    print(f"\nAirtable:")
    print(f"  - {len(clients)} clients")
    print(f"  - {len(projects)} projects")
    
    hierarchy = get_clickup_workspace()
    if hierarchy:
        clients_space = get_clickup_clients_space(hierarchy)
        if clients_space:
            folders = len(clients_space.get("folders", []))
            lists = sum(len(f.get("lists", [])) for f in clients_space.get("folders", []))
            print(f"\nClickUp '{CONFIG['clickup_space_name']}' Space:")
            print(f"  - {folders} client folders")
            print(f"  - {lists} project lists")
    
    # Check for unsynced
    clients_with_folders = [c for c in clients if c.get("fields", {}).get("ClickUp Folder ID")]
    clients_without_folders = [c for c in clients if not c.get("fields", {}).get("ClickUp Folder ID")]
    
    active_without = [c for c in clients_without_folders 
                      if c.get("fields", {}).get("Status", "").lower() in ["active", "onboarding"]]
    
    if active_without:
        print(f"\n⚠️  {len(active_without)} active clients without ClickUp folders:")
        for client in active_without[:5]:
            print(f"   - {client.get('fields', {}).get('Name', 'Unknown')}")
        if len(active_without) > 5:
            print(f"   ... and {len(active_without) - 5} more")
    else:
        print("\n✅ All active clients have ClickUp folders")

def interactive_setup():
    """Interactive setup for Airtable base configuration."""
    print("=== ClickUp-Airtable Sync Setup ===\n")
    
    # List available bases
    print("Fetching your Airtable bases...")
    result = airtable_call("list-bases")
    
    if not result or "bases" not in result:
        print("Error: Could not fetch Airtable bases. Check your AIRTABLE_API_KEY.")
        return
    
    bases = result["bases"]
    print("\nAvailable bases:")
    for i, base in enumerate(bases, 1):
        print(f"  {i}. {base.get('name')} ({base.get('id')})")
    
    # Select base
    choice = input("\nEnter base number (or paste base ID): ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(bases):
        selected_base = bases[int(choice) - 1]
    elif choice.startswith("app"):
        selected_base = {"id": choice, "name": "Custom"}
    else:
        print("Invalid selection")
        return
    
    CONFIG["airtable_base_id"] = selected_base["id"]
    print(f"\n✓ Selected: {selected_base.get('name')} ({selected_base['id']})")
    
    # Get schema to list tables
    print("\nFetching base schema...")
    schema = airtable_call("get-schema", selected_base["id"])
    
    if schema and "tables" in schema:
        tables = [t.get("name") for t in schema["tables"]]
        print(f"Tables: {', '.join(tables)}")
        
        # Clients table
        clients_table = input(f"\nClients table name [{CONFIG['clients_table']}]: ").strip()
        if clients_table:
            CONFIG["clients_table"] = clients_table
        
        # Projects table
        projects_table = input(f"Projects table name [{CONFIG['projects_table']}]: ").strip()
        if projects_table:
            CONFIG["projects_table"] = projects_table
    
    # ClickUp space name
    space_name = input(f"\nClickUp space name [{CONFIG['clickup_space_name']}]: ").strip()
    if space_name:
        CONFIG["clickup_space_name"] = space_name
    
    # Save config
    save_config()
    print(f"\n✅ Configuration saved to {CONFIG_PATH}")
    print("\nYou can now run:")
    print("  python sync_airtable.py --status   # Check sync status")
    print("  python sync_airtable.py --pull     # Create ClickUp folders from Airtable clients")
    print("  python sync_airtable.py --push     # Update Airtable from ClickUp")

def main():
    parser = argparse.ArgumentParser(description="Sync ClickUp with Airtable")
    parser.add_argument("--push", action="store_true", help="Push ClickUp updates to Airtable")
    parser.add_argument("--pull", action="store_true", help="Pull Airtable clients to ClickUp")
    parser.add_argument("--full", action="store_true", help="Full bidirectional sync")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--setup", action="store_true", help="Interactive setup")
    parser.add_argument("--base-id", help="Airtable base ID (overrides config)")
    
    args = parser.parse_args()
    
    load_config()
    
    if args.base_id:
        CONFIG["airtable_base_id"] = args.base_id
    
    if args.setup:
        interactive_setup()
        return
    
    if not any([args.push, args.pull, args.full, args.status]):
        parser.print_help()
        return
    
    if args.status:
        show_status()
        return
    
    if args.pull or args.full:
        print("=== Pulling Airtable → ClickUp ===")
        pull_clients_to_clickup()
    
    if args.push or args.full:
        print("\n=== Pushing ClickUp → Airtable ===")
        push_status_to_airtable()

if __name__ == "__main__":
    main()
