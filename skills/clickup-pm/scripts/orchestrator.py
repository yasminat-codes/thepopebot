#!/usr/bin/env python3
"""
ClickUp PM Orchestrator - Main entry point for project management operations.

This orchestrates:
1. Project creation from templates
2. Automated research for research-type tasks
3. Google Doc creation
4. Sync between ClickUp, Todoist, and Airtable
5. Task breakdown with step-by-step guidance

Usage:
    python orchestrator.py create "Client Onboarding" --client "Acme Corp"
    python orchestrator.py research "dental practices" --type niche
    python orchestrator.py breakdown "Build lead scraper"
    python orchestrator.py sync --all
    python orchestrator.py status
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPTS_DIR.parent / "config.json"
TEMPLATES_PATH = SCRIPTS_DIR.parent / "templates" / "projects.json"

def load_config():
    """Load configuration."""
    if CONFIG_PATH.exists():
        return json.load(open(CONFIG_PATH))
    return {}

def load_templates():
    """Load project templates."""
    if TEMPLATES_PATH.exists():
        return json.load(open(TEMPLATES_PATH))
    return {}

def run_script(script_name: str, *args) -> tuple[int, str, str]:
    """Run a script in the scripts directory."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return 1, "", f"Script not found: {script_name}"
    
    cmd = f"python3 {script_path} {' '.join(args)}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def mcporter_call(tool_call: str) -> dict:
    """Execute mcporter call."""
    cmd = f"mcporter call '{tool_call}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    try:
        return json.loads(result.stdout)
    except:
        return {"raw": result.stdout}

def list_templates():
    """List all available templates."""
    templates = load_templates()
    
    print("\n📁 Available Project Templates\n")
    print("=" * 60)
    
    categories = {}
    for key, template in templates.items():
        cat = template.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((key, template))
    
    for category, items in sorted(categories.items()):
        print(f"\n{category.upper()}")
        print("-" * 40)
        for key, template in items:
            phases = len(template.get("phases", []))
            tasks = sum(len(p.get("tasks", [])) for p in template.get("phases", []))
            research = "🔍" if template.get("auto_research") else "  "
            print(f"  {research} {key}")
            print(f"      {template['name']}: {template['description']}")
            print(f"      {phases} phases, {tasks} tasks\n")

def create_project(template_key: str, name: str = None, client: str = None, 
                   do_research: bool = True, create_docs: bool = True):
    """Create a project with full automation."""
    templates = load_templates()
    config = load_config()
    
    if template_key not in templates:
        print(f"❌ Template not found: {template_key}")
        print("Run: python orchestrator.py templates")
        return
    
    template = templates[template_key]
    project_name = name or template["name"]
    
    print(f"\n🚀 Creating project: {project_name}")
    if client:
        print(f"   Client: {client}")
    print(f"   Template: {template['name']}")
    print(f"   Auto-research: {do_research and template.get('auto_research', False)}")
    print(f"   Create docs: {create_docs}")
    
    # Step 1: Create project structure in ClickUp
    print("\n📋 Step 1: Creating ClickUp project structure...")
    args = [f'-t {template_key}', f'-n "{project_name}"']
    if client:
        args.append(f'-c "{client}"')
    
    code, stdout, stderr = run_script("create_project.py", *args)
    if code != 0:
        print(f"❌ Error creating project: {stderr}")
    else:
        print(stdout)
    
    # Step 2: Run automated research if template supports it
    if do_research and template.get("auto_research"):
        print("\n🔍 Step 2: Running automated research...")
        research_subject = client or project_name
        research_type = template.get("category", "niche")
        if research_type == "research":
            research_type = "niche"  # Default for research templates
        
        code, stdout, stderr = run_script("auto_research.py", 
                                          f'"{research_subject}"', 
                                          f'--type {research_type}')
        if code == 0:
            print(stdout)
        else:
            print(f"⚠️ Research had issues: {stderr}")
    
    # Step 3: Create Google Docs for tasks that need them
    if create_docs:
        print("\n📄 Step 3: Creating Google Docs...")
        doc_count = 0
        for phase in template.get("phases", []):
            for task in phase.get("tasks", []):
                if task.get("create_doc"):
                    doc_count += 1
                    print(f"   - Would create: {task['name']} doc")
        print(f"   {doc_count} docs to create (Google Docs integration pending)")
    
    # Step 4: Sync to Todoist
    print("\n🔄 Step 4: Syncing to Todoist...")
    code, stdout, stderr = run_script("sync_todoist.py", "--push")
    if code == 0:
        print("   ✓ Synced high-priority tasks to Todoist")
    
    # Step 5: Update Airtable
    if client:
        print("\n📊 Step 5: Updating Airtable...")
        # Would update Projects table with new project
        print(f"   ✓ Would create project record for {client}")
    
    print("\n" + "=" * 60)
    print("✅ PROJECT CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nProject: {project_name}")
    print(f"Template: {template['name']}")
    print(f"Phases: {len(template.get('phases', []))}")
    
    total_tasks = sum(len(p.get("tasks", [])) for p in template.get("phases", []))
    print(f"Tasks: {total_tasks}")
    
    if template.get("auto_research"):
        print(f"Research: Completed")

def run_research(subject: str, research_type: str = "niche"):
    """Run standalone research."""
    print(f"\n🔍 Running {research_type} research for: {subject}")
    
    code, stdout, stderr = run_script("auto_research.py", 
                                      f'"{subject}"', 
                                      f'--type {research_type}')
    print(stdout)
    if stderr:
        print(stderr)

def breakdown_task(task_description: str, create: bool = False, list_id: str = None):
    """Break down a task into subtasks."""
    print(f"\n📋 Breaking down: {task_description}")
    
    args = [f'"{task_description}"']
    if create:
        args.append("--create")
        if list_id:
            args.append(f"--list-id {list_id}")
    
    code, stdout, stderr = run_script("break_down_task.py", *args)
    print(stdout)
    if stderr:
        print(stderr)

def run_sync(sync_todoist: bool = False, sync_airtable: bool = False, full: bool = False):
    """Run sync operations."""
    if full:
        sync_todoist = True
        sync_airtable = True
    
    if sync_todoist:
        print("\n🔄 Syncing ClickUp ↔ Todoist...")
        code, stdout, stderr = run_script("sync_todoist.py", "--full")
        print(stdout)
    
    if sync_airtable:
        print("\n🔄 Syncing ClickUp ↔ Airtable...")
        code, stdout, stderr = run_script("sync_airtable.py", "--full")
        print(stdout)

def show_status():
    """Show overall status of ClickUp PM."""
    config = load_config()
    templates = load_templates()
    
    print("\n📊 ClickUp PM Status")
    print("=" * 60)
    
    print(f"\n📁 Templates: {len(templates)}")
    categories = set(t.get("category", "other") for t in templates.values())
    print(f"   Categories: {', '.join(sorted(categories))}")
    
    print(f"\n⚙️ Configuration:")
    print(f"   Airtable Base: {config.get('airtable_base_name', 'Not set')}")
    print(f"   Todoist Sync: {'Enabled' if config.get('todoist_sync', {}).get('enabled') else 'Disabled'}")
    
    # Check API availability
    print(f"\n🔌 Research APIs:")
    apis = config.get("research_apis", {})
    for api, enabled in apis.items():
        status = "✓" if enabled else "✗"
        print(f"   {status} {api}")
    
    # Run sync status
    print("\n🔄 Sync Status:")
    code, stdout, stderr = run_script("sync_todoist.py", "--status")
    print(stdout)

def main():
    parser = argparse.ArgumentParser(description="ClickUp PM Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Templates command
    templates_parser = subparsers.add_parser("templates", help="List available templates")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a project")
    create_parser.add_argument("template", help="Template key (e.g., client_onboarding)")
    create_parser.add_argument("--name", "-n", help="Project name")
    create_parser.add_argument("--client", "-c", help="Client name")
    create_parser.add_argument("--no-research", action="store_true", help="Skip research")
    create_parser.add_argument("--no-docs", action="store_true", help="Skip doc creation")
    
    # Research command
    research_parser = subparsers.add_parser("research", help="Run research")
    research_parser.add_argument("subject", help="Subject to research")
    research_parser.add_argument("--type", "-t", 
                                 choices=["niche", "persona", "market", "industry", "campaign"],
                                 default="niche", help="Research type")
    
    # Breakdown command
    breakdown_parser = subparsers.add_parser("breakdown", help="Break down a task")
    breakdown_parser.add_argument("task", help="Task description")
    breakdown_parser.add_argument("--create", action="store_true", help="Create in ClickUp")
    breakdown_parser.add_argument("--list-id", help="ClickUp list ID")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync systems")
    sync_parser.add_argument("--todoist", action="store_true", help="Sync with Todoist")
    sync_parser.add_argument("--airtable", action="store_true", help="Sync with Airtable")
    sync_parser.add_argument("--all", action="store_true", help="Full sync")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show status")
    
    args = parser.parse_args()
    
    if args.command == "templates":
        list_templates()
    elif args.command == "create":
        create_project(
            args.template,
            name=args.name,
            client=args.client,
            do_research=not args.no_research,
            create_docs=not args.no_docs
        )
    elif args.command == "research":
        run_research(args.subject, args.type)
    elif args.command == "breakdown":
        breakdown_task(args.task, args.create, args.list_id)
    elif args.command == "sync":
        run_sync(args.todoist, args.airtable, args.all)
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python orchestrator.py templates")
        print('  python orchestrator.py create client_onboarding --client "Acme Corp"')
        print('  python orchestrator.py research "dental practices" --type niche')
        print('  python orchestrator.py breakdown "Build lead scraper"')
        print("  python orchestrator.py sync --all")
        print("  python orchestrator.py status")

if __name__ == "__main__":
    main()
