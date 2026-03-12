#!/usr/bin/env python3
"""
Time Tracking Intelligence - Analyze time tracking data for insights.

Features:
- Compare actual time vs estimates
- Learn from history to improve estimates
- Alert if project going over budget
- Track utilization by client
- Identify estimation patterns

Usage:
    python time_intelligence.py                      # Full report
    python time_intelligence.py --client "Acme"      # Specific client
    python time_intelligence.py --budget-check       # Check budget alerts
    python time_intelligence.py --learn              # Update estimation model
    python time_intelligence.py --json               # Output JSON

Cron: Run weekly for reports, daily for budget checks
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Store learned estimates
ESTIMATES_FILE = Path(__file__).parent.parent / "data" / "time_estimates.json"

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

def load_estimates() -> dict:
    """Load learned estimates from file."""
    if ESTIMATES_FILE.exists():
        return json.load(open(ESTIMATES_FILE))
    return {"task_types": {}, "last_updated": None}

def save_estimates(estimates: dict):
    """Save learned estimates to file."""
    ESTIMATES_FILE.parent.mkdir(exist_ok=True)
    estimates["last_updated"] = datetime.now().isoformat()
    with open(ESTIMATES_FILE, "w") as f:
        json.dump(estimates, f, indent=2)

def parse_duration(duration_str: str) -> float:
    """Parse duration string to hours (e.g., '2h 30m' -> 2.5)."""
    if not duration_str:
        return 0
    
    hours = 0
    
    # Handle milliseconds (ClickUp format)
    if isinstance(duration_str, (int, float)):
        return duration_str / 3600000  # ms to hours
    
    # Handle string formats
    import re
    
    # Hours
    h_match = re.search(r'(\d+(?:\.\d+)?)\s*h', str(duration_str).lower())
    if h_match:
        hours += float(h_match.group(1))
    
    # Minutes
    m_match = re.search(r'(\d+)\s*m', str(duration_str).lower())
    if m_match:
        hours += float(m_match.group(1)) / 60
    
    return hours

def get_time_entries(task_id: str = None) -> list:
    """Get time entries from ClickUp."""
    if task_id:
        result = mcporter_call(f'clickup.clickup_get_task_time_entries(task_id: "{task_id}")')
    else:
        # Get current time entry to check active tracking
        result = mcporter_call('clickup.clickup_get_current_time_entry()')
    
    if result and "data" in result:
        return result["data"]
    elif result and isinstance(result, list):
        return result
    return []

def get_workspace_tasks() -> list:
    """Get all tasks with time tracking data."""
    result = mcporter_call('clickup.clickup_search(keywords: "*", count: 200)')
    if result and "results" in result:
        return [t for t in result["results"] if t.get("type") == "task"]
    return []

def categorize_task(task_name: str) -> str:
    """Categorize task by name for estimation learning."""
    name_lower = task_name.lower()
    
    categories = {
        "meeting": ["meeting", "call", "sync", "standup", "review"],
        "development": ["build", "develop", "code", "implement", "create", "script"],
        "research": ["research", "analyze", "investigate", "explore"],
        "writing": ["write", "document", "sop", "content", "copy"],
        "design": ["design", "mockup", "wireframe", "ui", "ux"],
        "testing": ["test", "qa", "debug", "fix"],
        "admin": ["setup", "configure", "organize", "update"],
        "communication": ["email", "respond", "follow up", "outreach"],
    }
    
    for category, keywords in categories.items():
        if any(kw in name_lower for kw in keywords):
            return category
    
    return "other"

def analyze_task_time(task: dict) -> dict:
    """Analyze time data for a single task."""
    analysis = {
        "id": task.get("id"),
        "name": task.get("name"),
        "list": task.get("list", {}).get("name", "Unknown"),
        "category": categorize_task(task.get("name", "")),
        "estimate_hours": 0,
        "actual_hours": 0,
        "variance": 0,
        "variance_pct": 0,
        "status": task.get("status", {}).get("status", "unknown")
    }
    
    # Get estimate
    time_estimate = task.get("time_estimate")
    if time_estimate:
        analysis["estimate_hours"] = parse_duration(time_estimate)
    
    # Get actual (time_spent field or sum of time entries)
    time_spent = task.get("time_spent")
    if time_spent:
        analysis["actual_hours"] = parse_duration(time_spent)
    
    # Calculate variance
    if analysis["estimate_hours"] > 0:
        analysis["variance"] = analysis["actual_hours"] - analysis["estimate_hours"]
        analysis["variance_pct"] = (analysis["variance"] / analysis["estimate_hours"]) * 100
    
    return analysis

def analyze_client_time(tasks: list, client_name: str) -> dict:
    """Analyze time for a specific client."""
    analysis = {
        "client": client_name,
        "total_estimated": 0,
        "total_actual": 0,
        "total_variance": 0,
        "task_count": 0,
        "tasks_over_estimate": 0,
        "tasks_under_estimate": 0,
        "avg_variance_pct": 0,
        "by_category": defaultdict(lambda: {"estimated": 0, "actual": 0, "count": 0})
    }
    
    variances = []
    
    for task in tasks:
        task_analysis = analyze_task_time(task)
        
        analysis["task_count"] += 1
        analysis["total_estimated"] += task_analysis["estimate_hours"]
        analysis["total_actual"] += task_analysis["actual_hours"]
        
        if task_analysis["estimate_hours"] > 0:
            if task_analysis["variance"] > 0:
                analysis["tasks_over_estimate"] += 1
            elif task_analysis["variance"] < 0:
                analysis["tasks_under_estimate"] += 1
            variances.append(task_analysis["variance_pct"])
        
        # By category
        cat = task_analysis["category"]
        analysis["by_category"][cat]["estimated"] += task_analysis["estimate_hours"]
        analysis["by_category"][cat]["actual"] += task_analysis["actual_hours"]
        analysis["by_category"][cat]["count"] += 1
    
    analysis["total_variance"] = analysis["total_actual"] - analysis["total_estimated"]
    
    if variances:
        analysis["avg_variance_pct"] = sum(variances) / len(variances)
    
    # Convert defaultdict to regular dict
    analysis["by_category"] = dict(analysis["by_category"])
    
    return analysis

def check_budget_alerts(tasks: list, budget_hours: float = None) -> list:
    """Check for budget alerts."""
    alerts = []
    
    # Group tasks by client/folder
    by_client = defaultdict(list)
    for task in tasks:
        folder = task.get("folder", {}).get("name", "Unknown")
        by_client[folder].append(task)
    
    for client, client_tasks in by_client.items():
        client_analysis = analyze_client_time(client_tasks, client)
        
        # Alert if over estimate by more than 20%
        if client_analysis["total_estimated"] > 0:
            if client_analysis["total_variance"] > client_analysis["total_estimated"] * 0.2:
                alerts.append({
                    "type": "over_budget",
                    "severity": "high",
                    "client": client,
                    "estimated": client_analysis["total_estimated"],
                    "actual": client_analysis["total_actual"],
                    "over_by": client_analysis["total_variance"],
                    "message": f"⚠️ {client} is {client_analysis['total_variance']:.1f}h over estimate"
                })
        
        # Alert if approaching budget
        if budget_hours and client_analysis["total_actual"] > budget_hours * 0.8:
            alerts.append({
                "type": "approaching_budget",
                "severity": "medium",
                "client": client,
                "budget": budget_hours,
                "used": client_analysis["total_actual"],
                "remaining": budget_hours - client_analysis["total_actual"],
                "message": f"📊 {client} at {(client_analysis['total_actual']/budget_hours)*100:.0f}% of budget"
            })
    
    return alerts

def learn_from_history(tasks: list) -> dict:
    """Learn estimation patterns from completed tasks."""
    estimates = load_estimates()
    
    # Analyze completed tasks with both estimate and actual
    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        if status not in ["complete", "closed", "done"]:
            continue
        
        analysis = analyze_task_time(task)
        
        if analysis["estimate_hours"] > 0 and analysis["actual_hours"] > 0:
            category = analysis["category"]
            
            if category not in estimates["task_types"]:
                estimates["task_types"][category] = {
                    "samples": [],
                    "avg_ratio": 1.0,
                    "recommended_buffer": 0
                }
            
            # Store ratio of actual/estimated
            ratio = analysis["actual_hours"] / analysis["estimate_hours"]
            estimates["task_types"][category]["samples"].append({
                "task": analysis["name"][:50],
                "estimated": analysis["estimate_hours"],
                "actual": analysis["actual_hours"],
                "ratio": ratio,
                "date": datetime.now().isoformat()
            })
            
            # Keep only last 50 samples
            estimates["task_types"][category]["samples"] = estimates["task_types"][category]["samples"][-50:]
            
            # Recalculate averages
            samples = estimates["task_types"][category]["samples"]
            if samples:
                ratios = [s["ratio"] for s in samples]
                estimates["task_types"][category]["avg_ratio"] = sum(ratios) / len(ratios)
                estimates["task_types"][category]["recommended_buffer"] = max(0, (estimates["task_types"][category]["avg_ratio"] - 1) * 100)
    
    save_estimates(estimates)
    return estimates

def suggest_estimate(task_name: str, initial_estimate: float) -> dict:
    """Suggest adjusted estimate based on learned patterns."""
    estimates = load_estimates()
    category = categorize_task(task_name)
    
    suggestion = {
        "task": task_name,
        "category": category,
        "initial_estimate": initial_estimate,
        "suggested_estimate": initial_estimate,
        "buffer_pct": 0,
        "confidence": "low",
        "reasoning": ""
    }
    
    if category in estimates.get("task_types", {}):
        cat_data = estimates["task_types"][category]
        samples = len(cat_data.get("samples", []))
        
        if samples >= 5:
            suggestion["confidence"] = "high" if samples >= 20 else "medium"
            suggestion["buffer_pct"] = cat_data.get("recommended_buffer", 0)
            suggestion["suggested_estimate"] = initial_estimate * cat_data.get("avg_ratio", 1.0)
            suggestion["reasoning"] = f"Based on {samples} similar {category} tasks"
    
    if suggestion["confidence"] == "low":
        # Default 20% buffer for unknown
        suggestion["buffer_pct"] = 20
        suggestion["suggested_estimate"] = initial_estimate * 1.2
        suggestion["reasoning"] = "Default 20% buffer (limited history)"
    
    return suggestion

def format_time_report(analysis: dict) -> str:
    """Format time intelligence report."""
    report = f"""# ⏱️ Time Intelligence Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Overall Summary

| Metric | Value |
|--------|-------|
| Total Estimated | {analysis.get('total_estimated', 0):.1f}h |
| Total Actual | {analysis.get('total_actual', 0):.1f}h |
| Variance | {analysis.get('total_variance', 0):+.1f}h |
| Tasks Analyzed | {analysis.get('task_count', 0)} |
| Over Estimate | {analysis.get('tasks_over_estimate', 0)} |
| Under Estimate | {analysis.get('tasks_under_estimate', 0)} |

---

## By Category

| Category | Estimated | Actual | Variance |
|----------|-----------|--------|----------|
"""
    
    for cat, data in analysis.get("by_category", {}).items():
        variance = data["actual"] - data["estimated"]
        report += f"| {cat.title()} | {data['estimated']:.1f}h | {data['actual']:.1f}h | {variance:+.1f}h |\n"
    
    report += """
---

## Estimation Insights

"""
    
    estimates = load_estimates()
    if estimates.get("task_types"):
        report += "Based on historical data:\n\n"
        for cat, data in estimates["task_types"].items():
            samples = len(data.get("samples", []))
            buffer = data.get("recommended_buffer", 0)
            if samples >= 5:
                report += f"- **{cat.title()}**: Add {buffer:.0f}% buffer ({samples} samples)\n"
    else:
        report += "_Not enough historical data yet. Run with --learn to build estimation model._\n"
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Time Tracking Intelligence")
    parser.add_argument("--client", "-c", help="Analyze specific client")
    parser.add_argument("--budget-check", action="store_true", help="Check for budget alerts")
    parser.add_argument("--learn", action="store_true", help="Learn from history")
    parser.add_argument("--suggest", help="Suggest estimate for task name")
    parser.add_argument("--estimate", type=float, help="Initial estimate (hours) for --suggest")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    print("Analyzing time tracking data...", file=sys.stderr)
    
    # Get tasks
    tasks = get_workspace_tasks()
    
    if args.suggest:
        # Suggest estimate
        estimate = args.estimate or 1.0
        suggestion = suggest_estimate(args.suggest, estimate)
        
        if args.json:
            print(json.dumps(suggestion, indent=2))
        else:
            print(f"\n📊 Estimate Suggestion for: {args.suggest}")
            print(f"   Category: {suggestion['category']}")
            print(f"   Initial estimate: {suggestion['initial_estimate']:.1f}h")
            print(f"   Suggested estimate: {suggestion['suggested_estimate']:.1f}h")
            print(f"   Buffer: +{suggestion['buffer_pct']:.0f}%")
            print(f"   Confidence: {suggestion['confidence']}")
            print(f"   Reasoning: {suggestion['reasoning']}")
        return
    
    if args.learn:
        # Learn from history
        estimates = learn_from_history(tasks)
        
        if args.json:
            print(json.dumps(estimates, indent=2))
        else:
            print(f"\n✅ Learned from {len(tasks)} tasks")
            print(f"\nEstimation buffers by category:")
            for cat, data in estimates.get("task_types", {}).items():
                samples = len(data.get("samples", []))
                buffer = data.get("recommended_buffer", 0)
                print(f"  - {cat.title()}: +{buffer:.0f}% ({samples} samples)")
        return
    
    if args.budget_check:
        # Check budget alerts
        alerts = check_budget_alerts(tasks)
        
        if args.json:
            print(json.dumps(alerts, indent=2))
        elif alerts:
            print("\n🚨 Budget Alerts:\n")
            for alert in alerts:
                print(f"  {alert['message']}")
        else:
            print("\n✅ No budget alerts")
        return
    
    # Full analysis
    if args.client:
        # Filter tasks for specific client
        client_tasks = [t for t in tasks if args.client.lower() in t.get("folder", {}).get("name", "").lower()]
        analysis = analyze_client_time(client_tasks, args.client)
    else:
        # Overall analysis
        analysis = analyze_client_time(tasks, "All Clients")
    
    if args.json:
        print(json.dumps(analysis, indent=2, default=str))
    else:
        report = format_time_report(analysis)
        print(report)

if __name__ == "__main__":
    main()
