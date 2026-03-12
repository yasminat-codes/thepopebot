#!/usr/bin/env python3
"""
Smart Project Creator - Intelligently creates projects with relevant tasks only.

Features:
- Analyzes project context to select ONLY relevant subtasks
- Adapts to ClickUp fields (priority, status, custom fields)
- Proactively creates Google Docs when needed
- Links docs in task descriptions
- Creates proper folder structure

Usage:
    python smart_project_creator.py --analyze "Build AI chatbot for dental practice"
    python smart_project_creator.py --create "Client onboarding" --client "Acme"
    python smart_project_creator.py --interactive

"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

TEMPLATES_FILE = Path(__file__).parent.parent / "templates" / "projects.json"
DATA_DIR = Path(__file__).parent.parent / "data"

# Task relevance keywords - used to filter out irrelevant tasks
RELEVANCE_KEYWORDS = {
    "automation": ["automation", "bot", "script", "api", "integration", "workflow", "scraper", "ai", "agent"],
    "website": ["website", "landing", "page", "design", "ui", "ux", "frontend", "responsive"],
    "webapp": ["webapp", "application", "app", "backend", "database", "api", "fullstack"],
    "campaign": ["campaign", "email", "outreach", "marketing", "cold", "linkedin", "ads"],
    "research": ["research", "analysis", "market", "niche", "persona", "competitor"],
    "onboarding": ["onboarding", "client", "kickoff", "discovery", "setup"],
    "content": ["content", "blog", "social", "video", "copy", "writing"],
    "seo": ["seo", "search", "ranking", "keywords", "optimization"],
    "integration": ["integration", "connect", "sync", "api", "webhook"]
}

# Tasks that ALWAYS need Google Docs
DOC_REQUIRED_KEYWORDS = [
    "requirements", "specification", "spec", "brief", "document",
    "sop", "procedure", "guide", "plan", "strategy", "report",
    "analysis", "research", "proposal"
]

def run_command(cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run shell command."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout"

def mcporter_call(tool_call: str) -> dict:
    """Execute mcporter call."""
    cmd = f"mcporter call '{tool_call}'"
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        return {"error": stderr}
    try:
        return json.loads(stdout)
    except:
        return {"raw": stdout}

def load_templates() -> dict:
    """Load project templates."""
    if TEMPLATES_FILE.exists():
        return json.load(open(TEMPLATES_FILE))
    return {}

def detect_project_type(description: str) -> list:
    """Detect project type(s) from description."""
    desc_lower = description.lower()
    detected = []
    
    for ptype, keywords in RELEVANCE_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            detected.append(ptype)
    
    return detected if detected else ["general"]

def calculate_task_relevance(task_name: str, project_types: list, project_context: str) -> float:
    """Calculate how relevant a task is to the project (0-1)."""
    name_lower = task_name.lower()
    context_lower = project_context.lower()
    
    score = 0.5  # Base score
    
    # Boost if task keywords match project types
    for ptype in project_types:
        if ptype in RELEVANCE_KEYWORDS:
            for kw in RELEVANCE_KEYWORDS[ptype]:
                if kw in name_lower:
                    score += 0.15
    
    # Boost if task words appear in project context
    task_words = set(name_lower.split())
    context_words = set(context_lower.split())
    overlap = len(task_words & context_words)
    score += overlap * 0.1
    
    # Penalize very generic tasks unless context matches
    generic_terms = ["setup", "configure", "review", "update", "check"]
    if any(term in name_lower for term in generic_terms):
        if not any(term in context_lower for term in generic_terms):
            score -= 0.2
    
    return min(max(score, 0), 1)

def should_create_doc(task_name: str, task_data: dict) -> bool:
    """Determine if a task needs a Google Doc."""
    name_lower = task_name.lower()
    
    # Explicit flag in template
    if task_data.get("create_doc"):
        return True
    
    # Check for doc-requiring keywords
    if any(kw in name_lower for kw in DOC_REQUIRED_KEYWORDS):
        return True
    
    return False

def get_doc_type(task_name: str) -> str:
    """Determine what type of doc to create."""
    name_lower = task_name.lower()
    
    if any(kw in name_lower for kw in ["requirements", "requirement"]):
        return "requirements"
    elif any(kw in name_lower for kw in ["spec", "technical", "architecture"]):
        return "technical_spec"
    elif any(kw in name_lower for kw in ["brief", "overview", "plan"]):
        return "project_brief"
    elif any(kw in name_lower for kw in ["sop", "procedure", "guide", "how to"]):
        return "sop"
    elif any(kw in name_lower for kw in ["meeting", "notes", "call"]):
        return "meeting_notes"
    elif any(kw in name_lower for kw in ["research", "analysis"]):
        return "research"
    else:
        return "project_brief"  # Default

def analyze_project(description: str, template_key: str = None) -> dict:
    """Analyze a project and determine optimal structure."""
    templates = load_templates()
    
    analysis = {
        "description": description,
        "detected_types": detect_project_type(description),
        "recommended_template": None,
        "relevant_tasks": [],
        "docs_needed": [],
        "estimated_hours": 0,
        "phases": []
    }
    
    # Find best matching template
    if template_key and template_key in templates:
        analysis["recommended_template"] = template_key
    else:
        # Auto-detect best template
        best_match = None
        best_score = 0
        
        for key, template in templates.items():
            score = 0
            template_name = template.get("name", "").lower()
            template_desc = template.get("description", "").lower()
            
            for ptype in analysis["detected_types"]:
                if ptype in key or ptype in template_name:
                    score += 2
                if ptype in template_desc:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = key
        
        analysis["recommended_template"] = best_match or "client_onboarding"
    
    # Analyze tasks from template
    if analysis["recommended_template"] in templates:
        template = templates[analysis["recommended_template"]]
        
        for phase in template.get("phases", []):
            phase_data = {
                "name": phase["name"],
                "duration": phase.get("duration", ""),
                "tasks": []
            }
            
            for task in phase.get("tasks", []):
                task_name = task["name"]
                relevance = calculate_task_relevance(
                    task_name, 
                    analysis["detected_types"],
                    description
                )
                
                if relevance >= 0.4:  # Threshold for inclusion
                    task_data = {
                        "name": task_name,
                        "relevance": round(relevance, 2),
                        "priority": task.get("priority", 3),
                        "time_estimate": task.get("time_estimate", "1h"),
                        "description": task.get("description", ""),
                        "needs_doc": should_create_doc(task_name, task)
                    }
                    
                    if task_data["needs_doc"]:
                        doc_type = get_doc_type(task_name)
                        task_data["doc_type"] = doc_type
                        analysis["docs_needed"].append({
                            "task": task_name,
                            "doc_type": doc_type
                        })
                    
                    phase_data["tasks"].append(task_data)
                    analysis["relevant_tasks"].append(task_data)
                    
                    # Sum time estimates
                    time_str = task.get("time_estimate", "1h")
                    if "h" in time_str:
                        hours = float(time_str.replace("h", "").strip())
                        analysis["estimated_hours"] += hours
                    elif "m" in time_str:
                        mins = float(time_str.replace("m", "").strip())
                        analysis["estimated_hours"] += mins / 60
            
            if phase_data["tasks"]:  # Only include phases with tasks
                analysis["phases"].append(phase_data)
    
    return analysis

def create_project(
    description: str,
    client_name: str,
    project_name: str = None,
    template_key: str = None,
    list_id: str = None,
    create_docs: bool = True,
    dry_run: bool = False
) -> dict:
    """Create a project with intelligent task selection."""
    
    # Analyze the project
    analysis = analyze_project(description, template_key)
    
    if not project_name:
        project_name = description[:50]
    
    result = {
        "project_name": project_name,
        "client": client_name,
        "analysis": analysis,
        "created_tasks": [],
        "created_docs": [],
        "errors": []
    }
    
    if dry_run:
        result["dry_run"] = True
        return result
    
    # Create Google Drive folder structure
    if create_docs and analysis["docs_needed"]:
        print(f"Creating Google Drive folder for {client_name}/{project_name}...")
        
        # Call Google Drive integration
        drive_cmd = (
            f'python3 {Path(__file__).parent}/google_drive_integration.py '
            f'--create-project "{client_name}" "{project_name}" --json'
        )
        code, stdout, stderr = run_command(drive_cmd)
        
        if code == 0:
            try:
                folder_info = json.loads(stdout)
                result["project_folder"] = folder_info
                print(f"  ✓ Created folder: {folder_info.get('link', 'N/A')}")
            except:
                result["errors"].append("Could not parse folder creation result")
        else:
            result["errors"].append(f"Folder creation failed: {stderr}")
    
    # Create tasks in ClickUp
    if list_id:
        print(f"\nCreating tasks in ClickUp...")
        
        for phase in analysis["phases"]:
            print(f"\n  Phase: {phase['name']}")
            
            for task in phase["tasks"]:
                task_name = task["name"]
                description_parts = [task.get("description", "")]
                
                # Create doc if needed
                if create_docs and task.get("needs_doc"):
                    doc_type = task.get("doc_type", "project_brief")
                    
                    doc_cmd = (
                        f'python3 {Path(__file__).parent}/google_drive_integration.py '
                        f'--create-doc {doc_type} --client "{client_name}" '
                        f'--project "{project_name}" --json'
                    )
                    code, stdout, stderr = run_command(doc_cmd)
                    
                    if code == 0:
                        try:
                            doc_info = json.loads(stdout)
                            result["created_docs"].append(doc_info)
                            description_parts.append(f"\n\n📄 Document: {doc_info.get('link', 'N/A')}")
                            print(f"    ✓ Doc: {doc_info.get('title', doc_type)}")
                        except:
                            pass
                
                # Build description
                full_description = "\n".join(description_parts)
                if task.get("time_estimate"):
                    full_description += f"\n\nTime estimate: {task['time_estimate']}"
                
                # Create task in ClickUp
                priority_map = {1: "urgent", 2: "high", 3: "normal", 4: "low"}
                priority = priority_map.get(task.get("priority", 3), "normal")
                
                desc_escaped = full_description.replace('"', '\\"').replace('\n', '\\n')
                
                clickup_result = mcporter_call(
                    f'clickup.clickup_create_task('
                    f'list_id: "{list_id}", '
                    f'name: "{task_name}", '
                    f'description: "{desc_escaped}", '
                    f'priority: "{priority}"'
                    f')'
                )
                
                if clickup_result and clickup_result.get("id"):
                    result["created_tasks"].append({
                        "id": clickup_result["id"],
                        "name": task_name,
                        "priority": priority
                    })
                    print(f"    ✓ Task: {task_name}")
                else:
                    result["errors"].append(f"Failed to create: {task_name}")
                    print(f"    ✗ Task: {task_name}")
    
    return result

def format_analysis_report(analysis: dict) -> str:
    """Format analysis as readable report."""
    report = f"""
# 🎯 Project Analysis

**Description:** {analysis['description']}
**Detected Types:** {', '.join(analysis['detected_types'])}
**Recommended Template:** {analysis['recommended_template']}
**Estimated Hours:** {analysis['estimated_hours']:.1f}h

## Relevant Tasks ({len(analysis['relevant_tasks'])})

"""
    
    for phase in analysis["phases"]:
        report += f"### {phase['name']} ({phase['duration']})\n\n"
        
        for task in phase["tasks"]:
            relevance_bar = "█" * int(task['relevance'] * 5) + "░" * (5 - int(task['relevance'] * 5))
            doc_icon = "📄" if task.get("needs_doc") else "  "
            
            report += f"- {doc_icon} **{task['name']}** [{relevance_bar}] {task['time_estimate']}\n"
        
        report += "\n"
    
    if analysis["docs_needed"]:
        report += f"## Documents to Create ({len(analysis['docs_needed'])})\n\n"
        for doc in analysis["docs_needed"]:
            report += f"- {doc['doc_type']}: {doc['task']}\n"
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Smart Project Creator")
    parser.add_argument("--analyze", "-a", help="Analyze project description")
    parser.add_argument("--create", "-c", help="Create project (description)")
    parser.add_argument("--client", help="Client name")
    parser.add_argument("--name", "-n", help="Project name")
    parser.add_argument("--template", "-t", help="Force specific template")
    parser.add_argument("--list-id", "-l", help="ClickUp list ID")
    parser.add_argument("--no-docs", action="store_true", help="Skip doc creation")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.analyze:
        analysis = analyze_project(args.analyze, args.template)
        
        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            print(format_analysis_report(analysis))
    
    elif args.create:
        if not args.client:
            print("❌ --client required for project creation")
            return
        
        result = create_project(
            description=args.create,
            client_name=args.client,
            project_name=args.name,
            template_key=args.template,
            list_id=args.list_id,
            create_docs=not args.no_docs,
            dry_run=args.dry_run
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n✅ Project Created: {result['project_name']}")
            print(f"   Client: {result['client']}")
            print(f"   Tasks: {len(result['created_tasks'])}")
            print(f"   Docs: {len(result['created_docs'])}")
            
            if result.get("project_folder"):
                print(f"   Folder: {result['project_folder'].get('link', 'N/A')}")
            
            if result.get("errors"):
                print(f"\n⚠️ Errors ({len(result['errors'])}):")
                for err in result["errors"]:
                    print(f"   - {err}")
    
    elif args.interactive:
        print("Smart Project Creator - Interactive Mode\n")
        
        description = input("Project description: ").strip()
        client = input("Client name: ").strip()
        name = input("Project name (optional): ").strip() or None
        
        # Analyze first
        analysis = analyze_project(description)
        print(format_analysis_report(analysis))
        
        confirm = input("\nCreate this project? (y/n): ").strip().lower()
        if confirm == 'y':
            list_id = input("ClickUp list ID (or press Enter to skip): ").strip() or None
            
            result = create_project(
                description=description,
                client_name=client,
                project_name=name,
                list_id=list_id,
                create_docs=True
            )
            
            print(f"\n✅ Created {len(result['created_tasks'])} tasks, {len(result['created_docs'])} docs")
    
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python smart_project_creator.py --analyze "Build AI chatbot for dental practice"')
        print('  python smart_project_creator.py --create "Client onboarding" --client "Acme Corp"')
        print('  python smart_project_creator.py --create "Build automation" --client "Acme" --list-id 12345')

if __name__ == "__main__":
    main()
