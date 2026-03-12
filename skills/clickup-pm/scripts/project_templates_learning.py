#!/usr/bin/env python3
"""
Project Templates from History - Learn from completed projects to improve templates.

Features:
- Analyze completed projects for patterns
- "Create project like [past project]"
- Smart defaults based on client type, project size
- Template effectiveness scoring
- Suggest template improvements

Usage:
    python project_templates_learning.py --learn              # Learn from history
    python project_templates_learning.py --like "Acme Corp"   # Create like past project
    python project_templates_learning.py --suggest            # Suggest template improvements
    python project_templates_learning.py --stats              # Show template stats

Cron: Run monthly to update learnings
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
LEARNINGS_FILE = DATA_DIR / "project_learnings.json"
TEMPLATES_FILE = Path(__file__).parent.parent / "templates" / "projects.json"

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

def load_learnings() -> dict:
    """Load project learnings."""
    DATA_DIR.mkdir(exist_ok=True)
    if LEARNINGS_FILE.exists():
        return json.load(open(LEARNINGS_FILE))
    return {
        "projects": {},
        "patterns": {},
        "template_usage": {},
        "last_updated": None
    }

def save_learnings(learnings: dict):
    """Save project learnings."""
    learnings["last_updated"] = datetime.now().isoformat()
    with open(LEARNINGS_FILE, "w") as f:
        json.dump(learnings, f, indent=2)

def load_templates() -> dict:
    """Load project templates."""
    if TEMPLATES_FILE.exists():
        return json.load(open(TEMPLATES_FILE))
    return {}

def get_workspace_hierarchy() -> dict:
    """Get workspace structure."""
    return mcporter_call('clickup.clickup_get_workspace_hierarchy(limit: 100)')

def parse_timestamp(ts) -> datetime:
    """Parse ClickUp timestamp."""
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts) / 1000)
    except:
        return None

def analyze_project(folder: dict, lists: list) -> dict:
    """Analyze a completed project."""
    analysis = {
        "name": folder.get("name", "Unknown"),
        "folder_id": folder.get("id"),
        "phases": [],
        "total_tasks": 0,
        "completed_tasks": 0,
        "total_hours_estimated": 0,
        "total_hours_actual": 0,
        "duration_days": 0,
        "task_types": defaultdict(int),
        "avg_task_duration": 0
    }
    
    start_date = None
    end_date = None
    
    for list_item in lists:
        phase = {
            "name": list_item.get("name"),
            "tasks": [],
            "task_count": 0,
            "completed": 0
        }
        
        # Would need to fetch tasks for each list
        # For now, use list metadata
        analysis["phases"].append(phase)
    
    return analysis

def detect_project_type(project_name: str, phases: list) -> str:
    """Detect what type of project this was."""
    name_lower = project_name.lower()
    phase_names = " ".join([p.get("name", "").lower() for p in phases])
    combined = name_lower + " " + phase_names
    
    type_keywords = {
        "onboarding": ["onboarding", "kickoff", "discovery", "setup"],
        "automation": ["automation", "build", "development", "script"],
        "campaign": ["campaign", "outreach", "email", "linkedin"],
        "website": ["website", "landing", "design", "launch"],
        "research": ["research", "analysis", "report"],
        "integration": ["integration", "api", "sync", "connect"]
    }
    
    for ptype, keywords in type_keywords.items():
        if any(kw in combined for kw in keywords):
            return ptype
    
    return "general"

def learn_from_projects() -> dict:
    """Learn patterns from completed projects."""
    print("Learning from completed projects...")
    
    learnings = load_learnings()
    hierarchy = get_workspace_hierarchy()
    
    if not hierarchy:
        print("Could not fetch workspace")
        return learnings
    
    # Find Clients space
    clients_space = None
    for space in hierarchy.get("spaces", []):
        if space.get("name", "").lower() == "clients":
            clients_space = space
            break
    
    if not clients_space:
        print("No Clients space found")
        return learnings
    
    # Analyze each client folder
    for folder in clients_space.get("folders", []):
        folder_name = folder.get("name", "Unknown")
        folder_id = folder.get("id")
        lists = folder.get("lists", [])
        
        print(f"  Analyzing: {folder_name}")
        
        project_type = detect_project_type(folder_name, lists)
        
        # Store project data
        learnings["projects"][folder_id] = {
            "name": folder_name,
            "type": project_type,
            "phases": [l.get("name") for l in lists],
            "phase_count": len(lists),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Update patterns
        if project_type not in learnings["patterns"]:
            learnings["patterns"][project_type] = {
                "avg_phases": 0,
                "common_phase_names": defaultdict(int),
                "project_count": 0
            }
        
        pattern = learnings["patterns"][project_type]
        pattern["project_count"] += 1
        
        for list_item in lists:
            phase_name = list_item.get("name", "").lower()
            pattern["common_phase_names"][phase_name] = pattern["common_phase_names"].get(phase_name, 0) + 1
        
        # Recalculate averages
        total_phases = sum(p["phase_count"] for p in learnings["projects"].values() 
                         if learnings["projects"][p.get("folder_id", "")].get("type") == project_type)
        pattern["avg_phases"] = total_phases / pattern["project_count"] if pattern["project_count"] > 0 else 0
    
    # Convert defaultdicts
    for ptype in learnings["patterns"]:
        if isinstance(learnings["patterns"][ptype].get("common_phase_names"), defaultdict):
            learnings["patterns"][ptype]["common_phase_names"] = dict(learnings["patterns"][ptype]["common_phase_names"])
    
    save_learnings(learnings)
    print(f"Learned from {len(learnings['projects'])} projects")
    
    return learnings

def find_similar_project(reference_name: str) -> dict:
    """Find a project similar to the reference."""
    learnings = load_learnings()
    
    reference_lower = reference_name.lower()
    
    # Search in learned projects
    best_match = None
    best_score = 0
    
    for project_id, project in learnings.get("projects", {}).items():
        project_name = project.get("name", "").lower()
        
        # Simple similarity: word overlap
        ref_words = set(reference_lower.split())
        proj_words = set(project_name.split())
        
        overlap = len(ref_words & proj_words)
        score = overlap / max(len(ref_words), 1)
        
        if score > best_score:
            best_score = score
            best_match = project
    
    return best_match

def generate_project_like(reference_name: str) -> dict:
    """Generate a project configuration based on a similar past project."""
    similar = find_similar_project(reference_name)
    
    if not similar:
        return {"error": f"No similar project found for '{reference_name}'"}
    
    templates = load_templates()
    project_type = similar.get("type", "general")
    
    # Try to find matching template
    template_key = None
    for key, template in templates.items():
        if project_type in key or key in project_type:
            template_key = key
            break
    
    result = {
        "based_on": similar.get("name"),
        "detected_type": project_type,
        "suggested_template": template_key,
        "phases": similar.get("phases", []),
        "recommendations": []
    }
    
    # Add recommendations based on patterns
    learnings = load_learnings()
    if project_type in learnings.get("patterns", {}):
        pattern = learnings["patterns"][project_type]
        
        # Recommend common phases
        common_phases = sorted(
            pattern.get("common_phase_names", {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        if common_phases:
            result["recommendations"].append(
                f"Common phases for {project_type} projects: {', '.join([p[0] for p in common_phases])}"
            )
    
    return result

def suggest_template_improvements() -> list:
    """Suggest improvements to templates based on learnings."""
    learnings = load_learnings()
    templates = load_templates()
    
    suggestions = []
    
    for project_type, pattern in learnings.get("patterns", {}).items():
        if pattern.get("project_count", 0) < 3:
            continue  # Not enough data
        
        # Find corresponding template
        template_key = None
        for key in templates.keys():
            if project_type in key:
                template_key = key
                break
        
        if not template_key:
            suggestions.append({
                "type": "missing_template",
                "project_type": project_type,
                "suggestion": f"Consider creating a template for '{project_type}' projects ({pattern['project_count']} completed)"
            })
            continue
        
        template = templates[template_key]
        template_phases = [p.get("name", "").lower() for p in template.get("phases", [])]
        
        # Check for commonly used phases not in template
        common_phases = pattern.get("common_phase_names", {})
        for phase_name, count in common_phases.items():
            if count >= pattern["project_count"] * 0.5:  # Used in 50%+ of projects
                if phase_name not in " ".join(template_phases):
                    suggestions.append({
                        "type": "missing_phase",
                        "template": template_key,
                        "suggestion": f"Consider adding '{phase_name}' phase - used in {count}/{pattern['project_count']} projects"
                    })
    
    return suggestions

def show_stats() -> dict:
    """Show template and project statistics."""
    learnings = load_learnings()
    templates = load_templates()
    
    stats = {
        "total_projects_analyzed": len(learnings.get("projects", {})),
        "project_types": {},
        "template_count": len(templates),
        "last_updated": learnings.get("last_updated")
    }
    
    # Count by type
    for project in learnings.get("projects", {}).values():
        ptype = project.get("type", "unknown")
        stats["project_types"][ptype] = stats["project_types"].get(ptype, 0) + 1
    
    return stats

def format_stats_report(stats: dict) -> str:
    """Format stats as readable report."""
    report = f"""# 📊 Project Template Statistics
**Last Updated:** {stats.get('last_updated', 'Never')}

## Overview

| Metric | Value |
|--------|-------|
| Projects Analyzed | {stats['total_projects_analyzed']} |
| Templates Available | {stats['template_count']} |

## Projects by Type

"""
    
    for ptype, count in sorted(stats.get("project_types", {}).items(), key=lambda x: x[1], reverse=True):
        report += f"| {ptype.title()} | {count} |\n"
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Project Templates Learning")
    parser.add_argument("--learn", action="store_true", help="Learn from completed projects")
    parser.add_argument("--like", help="Create project like a past project")
    parser.add_argument("--suggest", action="store_true", help="Suggest template improvements")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    if args.learn:
        learnings = learn_from_projects()
        if args.json:
            print(json.dumps(learnings, indent=2))
        else:
            print(f"\n✅ Learned from {len(learnings.get('projects', {}))} projects")
            print(f"   Patterns identified: {len(learnings.get('patterns', {}))}")
    
    elif args.like:
        result = generate_project_like(args.like)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"\n📋 Project Configuration (based on: {result['based_on']})")
                print(f"   Type: {result['detected_type']}")
                print(f"   Suggested template: {result['suggested_template']}")
                print(f"   Phases: {', '.join(result['phases'])}")
                if result['recommendations']:
                    print(f"\n   Recommendations:")
                    for rec in result['recommendations']:
                        print(f"   - {rec}")
    
    elif args.suggest:
        suggestions = suggest_template_improvements()
        if args.json:
            print(json.dumps(suggestions, indent=2))
        else:
            if suggestions:
                print("\n💡 Template Improvement Suggestions:\n")
                for s in suggestions:
                    print(f"  [{s['type']}] {s['suggestion']}")
            else:
                print("\n✅ No suggestions - templates look good!")
    
    elif args.stats:
        stats = show_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(format_stats_report(stats))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
