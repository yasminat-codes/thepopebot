#!/usr/bin/env python3
"""
Load all 135 Yusuf (PM Agent) skills into the Teable Skills Pipeline.

Usage:
    TEABLE_API_TOKEN="..." python3 load_yusuf_skills.py
    TEABLE_API_TOKEN="..." python3 load_yusuf_skills.py --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

TABLE_ID = "tblyl5mzFebauxrGf1L"
YUSUF_RECORD_ID = "rec21WoNhlQRl9DNzh6"
WORKSPACE = "yusuf-workspace"
BUILDER = "Zahra"
CREATION_SKILL = "Skillforge"

# All 135 Yusuf skills: (name, description, category, priority)
YUSUF_SKILLS = [
    # ─── 1. TASK CREATION & ENRICHMENT ───────────────────────────────────
    ("task-creator",
     "Create tasks from any input source: meeting notes, Slack messages, email threads, verbal instructions, client requests, agent outputs, and strategic decisions. Every task is created with a clear title, description, acceptance criteria, priority, deadline, and assignee. No task enters the system incomplete.",
     "workflow", "High"),
    ("task-enricher",
     "Before assigning any task, enrich it with everything the assignee needs to execute without asking questions: background context, relevant links, reference documents, prior art, related tasks, stakeholder expectations, and any constraints. The goal is zero back-and-forth between assignment and execution.",
     "workflow", "High"),
    ("task-description-writer",
     "Write detailed task descriptions that eliminate ambiguity: what needs to be done (action), why it matters (context), what done looks like (acceptance criteria), what resources are available (links, docs, access), and what constraints exist (time, budget, dependencies).",
     "workflow", "High"),
    ("subtask-decomposer",
     "Break complex tasks into atomic subtasks: each subtask independently executable, clearly scoped, with its own acceptance criteria, and ordered by dependency. A task that cannot be started in the next 30 minutes has not been decomposed enough.",
     "workflow", "High"),
    ("checklist-builder",
     "Build detailed checklists for recurring or multi-step tasks: every step enumerated, verification points included, common mistakes flagged, and nothing left to memory. Checklists are the simplest tool that prevents the most failures.",
     "workflow", "Normal"),
    ("task-context-researcher",
     "Before creating a task, research the context the assignee will need: pull relevant Slack threads, find the latest version of referenced documents, check the current status of dependencies, and gather any background information. Attach everything to the task so the executor has a complete package.",
     "workflow", "High"),
    ("task-dependency-mapper",
     "Map dependencies between tasks: what must finish before this can start, what can run in parallel, what is blocked by external input, and what is on the critical path. Visualize dependencies so scheduling decisions are informed.",
     "workflow", "High"),
    ("task-priority-calculator",
     "Calculate task priority using multiple factors: deadline urgency, business impact, dependency chains (blocking other work), client visibility, effort required, and strategic alignment. Produce a priority score, not just a gut-feel label.",
     "workflow", "High"),
    ("task-effort-estimator",
     "Estimate effort for every task: time required, complexity level, and appropriate assignee skill level. Use historical data from similar completed tasks to improve estimate accuracy over time.",
     "workflow", "Normal"),
    ("task-template-library",
     "Maintain a library of task templates for recurring work: client onboarding tasks, content creation tasks, deployment tasks, research tasks, and reporting tasks. Templates include pre-filled descriptions, standard subtasks, checklists, and default assignments. Create a new project from templates in minutes, not hours.",
     "operations", "Normal"),
    ("task-duplication-detector",
     "Before creating a new task, check for duplicates or related existing tasks: same objective described differently, overlapping scope with another task, or a task previously completed that can be referenced. Prevent duplicate work.",
     "workflow", "Normal"),
    ("task-acceptance-criteria-writer",
     "Write specific, testable acceptance criteria for every task: the email sequence has 5 steps, each under 150 words, with personalized first lines referencing company news — not write a good email sequence. Eliminate subjective quality debates.",
     "workflow", "High"),

    # ─── 2. TASK ASSIGNMENT & DELEGATION ─────────────────────────────────
    ("intelligent-task-assigner",
     "Assign tasks to the agent best suited for the work: match task type to agent expertise, check agent current workload, verify the agent has access to required tools, and confirm the task falls within the agent's skill set. Wrong assignments waste everyone's time.",
     "workflow", "High"),
    ("agent-workload-balancer",
     "Monitor and balance workload across all agents: no agent overloaded while another is idle, no agent receiving tasks outside their capability, and capacity distributed to maintain consistent throughput without burnout.",
     "agent-tools", "High"),
    ("yasmine-task-preparer",
     "For tasks assigned to Yasmine personally, go beyond normal enrichment: pre-research the topic, draft starting frameworks, pull all reference materials, outline the suggested approach, pre-fill templates where possible, and organize everything so Yasmine can sit down and execute with minimum startup friction.",
     "workflow", "High"),
    ("energy-based-scheduler",
     "Schedule Yasmine's tasks based on energy levels and cognitive demand: deep creative or strategic work during peak energy hours, administrative tasks during low-energy windows, meetings clustered to protect focus blocks, and no high-cognitive tasks after back-to-back meetings.",
     "workflow", "High"),
    ("task-briefing-generator",
     "Generate a task briefing for every assigned task: a quick summary of what, why, how, and what is already been prepared. The briefing is the first thing the assignee reads, orienting them in 30 seconds before diving into details.",
     "workflow", "Normal"),
    ("delegation-recommendation-engine",
     "When Yasmine is about to take on a task, evaluate if it should be delegated instead: can an agent handle this, would it be faster to delegate, is this the highest use of Yasmine's time? Recommend delegation with a suggested assignee and prepared handoff.",
     "workflow", "High"),
    ("skill-gap-task-router",
     "When a task does not clearly fit any existing agent's expertise, identify the gap: flag for Yasmine's decision (do it herself, create a new skill for an agent, or outsource), and recommend the best path forward.",
     "agent-tools", "Normal"),
    ("task-handoff-protocol",
     "When a task transitions between agents or phases, manage the handoff: ensure the outgoing work is complete, package the context for the incoming assignee, confirm receipt, and verify the new assignee understands the task.",
     "workflow", "High"),
    ("multi-agent-task-coordinator",
     "For tasks requiring multiple agents to collaborate: define each agent's contribution, sequence the work, manage information flow between agents, and integrate the final output. Orchestrate without bottlenecking.",
     "agent-tools", "High"),
    ("batch-task-assigner",
     "For large batches of similar tasks (research 50 companies, write 30 email variants), intelligently batch and distribute: parallel assignments where possible, sequential where dependencies exist, and progress tracking across the batch.",
     "workflow", "Normal"),

    # ─── 3. PLATFORM MANAGEMENT & SYNCHRONIZATION ────────────────────────
    ("clickup-manager",
     "Full ownership of ClickUp workspace: create spaces, folders, and lists for each project. Create tasks, set custom fields, manage views, configure automations, maintain templates, and ensure the workspace structure reflects the agency's actual workflow.",
     "operations", "High"),
    ("airtable-manager",
     "Manage Airtable bases: maintain project databases, client trackers, content calendars, research databases, and any other structured data. Create views, configure formulas, build interfaces, and sync data with other platforms.",
     "operations", "Normal"),
    ("gohighlevel-manager",
     "Manage GoHighLevel for CRM and client management: pipeline stages, contact management, opportunity tracking, workflow automations, and reporting dashboards. Ensure GHL reflects current pipeline reality.",
     "operations", "Normal"),
    ("platform-sync-engine",
     "Keep all platforms in sync: when a task is completed in ClickUp, update Airtable and GHL. When a deal moves in GHL, create the project in ClickUp. When research is added to Airtable, attach it to the relevant ClickUp task. No platform should contradict another.",
     "integration", "High"),
    ("cross-platform-status-reconciler",
     "Periodically reconcile status across platforms: find discrepancies between ClickUp task status, Airtable records, and GHL pipeline stages. Fix inconsistencies before they cause confusion or missed work.",
     "integration", "Normal"),
    ("custom-field-manager",
     "Manage custom fields across platforms: ensure consistent field names and values, maintain dropdown options, create new fields when workflows evolve, and archive unused fields. Clean metadata enables clean reporting.",
     "operations", "Normal"),
    ("view-and-filter-optimizer",
     "Create and optimize views and filters in each platform: agent-specific views (show only their tasks), project-specific views, deadline views, priority views, and blocked-task views. The right view makes the right work visible to the right person.",
     "operations", "Normal"),
    ("platform-automation-builder",
     "Build automations within project management platforms: auto-assign tasks based on type, auto-move tasks through stages, auto-notify on status changes, auto-create follow-up tasks on completion, and auto-escalate overdue items.",
     "workflow", "High"),
    ("notification-management",
     "Configure and manage notifications across platforms: ensure critical updates reach the right people, suppress noise from low-priority changes, batch non-urgent notifications, and prevent notification fatigue while maintaining awareness.",
     "operations", "Normal"),
    ("platform-cleanup-scheduler",
     "Schedule periodic platform cleanup: archive completed projects, close stale tasks, remove inactive users, clean up test data, and maintain workspace hygiene. Cluttered platforms slow everyone down.",
     "operations", "Normal"),

    # ─── 4. PROJECT PLANNING & SETUP ─────────────────────────────────────
    ("project-initializer",
     "When a new project is approved (internal or client), initialize it end-to-end: create the project space in ClickUp, set up the Airtable records, configure GHL if client-facing, create the task structure from templates, assign initial tasks, and notify all involved agents.",
     "workflow", "High"),
    ("project-scope-to-task-converter",
     "Convert project scope documents (PRDs, SOWs, briefs) into complete task structures: every deliverable becomes a task group, every requirement becomes a task, every task has subtasks and checklists, and nothing in the scope document is left without a corresponding trackable item.",
     "workflow", "High"),
    ("project-timeline-builder",
     "Build project timelines: sequence tasks by dependency, assign durations, calculate the critical path, identify parallel tracks, set milestones, and produce a Gantt-style view. Make the timeline realistic — padding included.",
     "workflow", "High"),
    ("sprint-planner",
     "Plan sprints for development and delivery work: select tasks from the backlog, fit them into sprint capacity, balance quick wins with complex work, define sprint goals, and set up sprint review checkpoints.",
     "workflow", "High"),
    ("milestone-definer",
     "Define clear project milestones: what constitutes each milestone, what deliverables must be complete, what sign-offs are required, and what the milestone triggers (invoice, next phase, client review). Milestones are the heartbeat of project progress.",
     "workflow", "High"),
    ("kickoff-task-generator",
     "Generate the standard kickoff task set for any new project: initial research tasks, setup tasks, communication tasks, first deliverable tasks, and administrative tasks. Pre-populated from templates but customized per project.",
     "workflow", "Normal"),
    ("resource-allocation-planner",
     "Plan resource allocation across projects: which agents are assigned to which projects, what percentage of their capacity each project consumes, and where resource conflicts exist. Prevent over-commitment.",
     "operations", "High"),
    ("project-risk-register-creator",
     "Create a risk register for each project: identified risks, probability, impact, mitigation plans, and risk owners. Review weekly and update as the project progresses.",
     "operations", "Normal"),
    ("project-buffer-calculator",
     "Calculate and build schedule buffers: task-level buffers for uncertain work, milestone buffers for integration risk, and project-level buffers for unknown unknowns. Buffers are not padding — they are risk management.",
     "workflow", "Normal"),
    ("parallel-workstream-designer",
     "Design parallel workstreams within projects: identify which tracks can progress simultaneously, define integration points where streams must merge, and schedule checkpoints to verify streams are converging correctly.",
     "workflow", "Normal"),

    # ─── 5. PROGRESS TRACKING & MONITORING ───────────────────────────────
    ("real-time-progress-tracker",
     "Track real-time progress across all projects: tasks completed vs. planned, percentage complete by project, velocity trends, and actual vs. estimated effort. The single source of truth for where are we.",
     "operations", "High"),
    ("daily-progress-scanner",
     "Every morning, scan all active tasks across all platforms: what moved yesterday, what is due today, what is overdue, what is blocked, and what needs attention. Produce the daily task landscape.",
     "operations", "High"),
    ("overdue-task-hunter",
     "Identify every overdue task across every project and platform: how many days overdue, who is responsible, what is the impact of the delay, and what is needed to unblock. No overdue task should exist without a documented reason and recovery plan.",
     "operations", "High"),
    ("blocked-task-resolver",
     "Identify blocked tasks and actively work to unblock them: determine the blocker source (waiting on input, missing access, dependency not complete, unclear requirements), take action to resolve (follow up, provide the input, escalate), and track time-in-blocked-state.",
     "workflow", "High"),
    ("velocity-tracker",
     "Track task completion velocity: tasks completed per day/week by agent and by project, trend direction, and velocity anomalies. Slowing velocity is an early warning of problems.",
     "operations", "Normal"),
    ("burndown-chart-maintainer",
     "Maintain burndown charts for sprints and projects: remaining work vs. time remaining, actual burndown vs. ideal burndown, and projected completion date based on current velocity.",
     "operations", "Normal"),
    ("scope-change-tracker",
     "Track every scope change: what was added, what was removed, who approved it, and how it impacts timeline and budget. Cumulative scope change tells the story of project health.",
     "operations", "Normal"),
    ("milestone-progress-reporter",
     "Track and report milestone progress: percentage complete, projected completion date, risks to milestone, and required actions to stay on track. Milestones are what clients and leadership actually care about.",
     "operations", "High"),
    ("stale-task-detector",
     "Detect stale tasks: tasks that have not been updated in X days, tasks with no activity since assignment, and tasks sitting in in progress without any progress. Stale tasks are either blocked, forgotten, or no longer needed.",
     "operations", "Normal"),
    ("time-tracking-manager",
     "Track time spent on tasks and projects: actual hours vs. estimated hours, time by project, time by agent, and time by task type. Time data feeds capacity planning, pricing, and profitability analysis.",
     "operations", "Normal"),

    # ─── 6. SPRINT & AGILE MANAGEMENT ────────────────────────────────────
    ("sprint-conductor",
     "Conduct sprints end-to-end: sprint planning session, daily standups, mid-sprint check, sprint review, and sprint retrospective. Maintain sprint rhythm and ceremony.",
     "workflow", "Normal"),
    ("daily-standup-runner",
     "Run daily standups across the agent fleet: collect done yesterday, doing today, any blockers from each agent, compile into a single standup summary, escalate blockers, and distribute the standup report.",
     "workflow", "High"),
    ("sprint-backlog-groomer",
     "Groom the sprint backlog: ensure upcoming tasks are fully enriched, re-prioritize as new information arrives, remove tasks that are no longer relevant, and ensure the backlog is always ready for the next sprint.",
     "workflow", "Normal"),
    ("sprint-retrospective-facilitator",
     "Facilitate sprint retrospectives: what went well, what did not, what should change for next sprint. Document action items from the retro and track their implementation.",
     "workflow", "Normal"),
    ("sprint-velocity-analyzer",
     "Analyze sprint velocity trends: are we getting faster, slower, or staying flat? What factors correlate with higher velocity (fewer meetings, better-enriched tasks, smaller task sizes)? Use data to improve sprint performance.",
     "operations", "Normal"),
    ("kanban-board-manager",
     "Maintain kanban boards for work that does not fit sprint cycles: continuous work, support requests, ad-hoc tasks, and maintenance work. Manage WIP limits, flow efficiency, and queue times.",
     "operations", "Normal"),
    ("backlog-prioritization-engine",
     "Prioritize the master backlog using weighted scoring: business value, effort, urgency, strategic alignment, client impact, and dependency position. Re-prioritize weekly as conditions change.",
     "workflow", "High"),
    ("sprint-capacity-calculator",
     "Calculate sprint capacity per agent: available hours minus meetings, minus overhead, minus planned absence. Match sprint commitment to actual capacity — overcommitted sprints fail by design.",
     "operations", "Normal"),

    # ─── 7. AGENT TASK MANAGEMENT ────────────────────────────────────────
    ("agent-task-queue-manager",
     "Manage each agent's task queue: what they should work on next, what is queued behind it, what is expected this week, and what is on their horizon. Every agent always knows their priorities.",
     "agent-tools", "High"),
    ("agent-task-completion-verifier",
     "When an agent marks a task complete, verify completion: does the output meet acceptance criteria, were all subtasks completed, were all checklists checked, and is the deliverable actually done — not just I worked on it.",
     "agent-tools", "High"),
    ("agent-task-quality-reviewer",
     "Review the quality of agent task outputs: does the work meet the standard, is it client-ready (if client-facing), and does it match what was requested? Flag quality issues before they reach Yasmine or clients.",
     "agent-tools", "High"),
    ("agent-deadline-enforcer",
     "Enforce deadlines across the agent fleet: send reminders at 48 hours, 24 hours, and 4 hours before deadline. If a deadline will be missed, require a reason and a revised ETA before the deadline passes, not after.",
     "agent-tools", "High"),
    ("agent-accountability-tracker",
     "Track each agent's accountability metrics: on-time completion rate, quality pass rate, revision frequency, and average time-to-complete by task type. Identify patterns that indicate an agent needs reconfiguration or additional skills.",
     "agent-tools", "Normal"),
    ("agent-capacity-dashboard",
     "Maintain a real-time dashboard showing each agent's capacity: current task count, estimated hours committed, percentage of capacity used, and availability for new assignments.",
     "agent-tools", "High"),
    ("agent-performance-benchmarker",
     "Benchmark agent performance against historical data: is this agent getting faster, producing higher quality, handling more volume? Track improvement trajectories and identify agents that are plateauing.",
     "agent-tools", "Normal"),
    ("agent-task-redistribution",
     "When an agent is overloaded, behind schedule, or encountering issues, redistribute tasks: identify which tasks can be moved, which agents have capacity, and execute the redistribution with full context handoff.",
     "agent-tools", "High"),

    # ─── 8. YASMINE-SPECIFIC TASK OPTIMIZATION ───────────────────────────
    ("yasmine-daily-task-briefing",
     "Every morning, prepare Yasmine's personal daily task briefing: her top 3-5 tasks for the day, each with a one-paragraph summary of what it is and everything she needs to start immediately, time estimates, and suggested order based on energy and calendar.",
     "operations", "High"),
    ("yasmine-task-pre-work",
     "For every task Yasmine needs to do personally, complete as much pre-work as possible: research the topic, draft an outline, gather reference materials, prepare templates, pre-fill known information, and create a start-here document that eliminates the cold-start problem.",
     "operations", "High"),
    ("yasmine-decision-packager",
     "When a task requires Yasmine's decision (not execution), package the decision: present the options, pros/cons for each, the recommended option with reasoning, and what happens next based on each choice. Reduce decision-making from research to selection.",
     "operations", "High"),
    ("yasmine-energy-profiler",
     "Learn and maintain Yasmine's energy profile: when she does her best deep work, when she is best for meetings, when administrative work is most tolerable, and when she needs breaks. Schedule her task day around her energy, not just her calendar.",
     "operations", "Normal"),
    ("yasmine-focus-block-protector",
     "Protect Yasmine's deep focus blocks: no meetings scheduled, no Slack interruptions, only emergency escalations. Batch all questions and non-urgent items for after the focus block. Fight for her attention on her behalf.",
     "operations", "High"),
    ("yasmine-context-loading-minimizer",
     "Minimize context-switching cost for Yasmine: group related tasks together, provide all context in one place (not scattered across platforms), and sequence tasks so each one builds on the mental model from the previous.",
     "operations", "High"),
    ("yasmine-weekly-task-previewer",
     "Every Sunday, provide Yasmine with a preview of her week: what is due, what requires her specifically, what decisions are needed, and suggested daily task allocation. Let her walk into Monday with a complete picture.",
     "operations", "High"),
    ("yasmine-task-completion-celebrator",
     "Track and celebrate Yasmine's task completions: daily progress bar, weekly completion count, and milestone acknowledgments. Visible progress fuels motivation.",
     "operations", "Normal"),
    ("yasmine-low-energy-task-bank",
     "Maintain a bank of low-energy tasks Yasmine can knock out when she is not at peak performance: approvals, reviews, email responses, and administrative items. No energy level is wasted.",
     "operations", "Normal"),
    ("yasmine-meeting-action-extractor",
     "After every meeting Yasmine attends, extract and create tasks from the action items: what she committed to, what others committed to that she needs to track, and any follow-ups. No meeting action item gets lost.",
     "workflow", "High"),

    # ─── 9. INTERNAL PROJECT MANAGEMENT ──────────────────────────────────
    ("internal-project-portfolio-manager",
     "Manage the portfolio of all internal projects: tool implementations, process improvements, agent skill development, infrastructure upgrades, and content initiatives. Track status, priority, and resource allocation across the internal portfolio.",
     "operations", "High"),
    ("internal-improvement-project-tracker",
     "Track all internal improvement projects from the S-Agent, TechOps Agent, and other agents: what improvements are in progress, what is completed, what is queued, and what is the cumulative impact of improvements over time.",
     "operations", "Normal"),
    ("agent-skill-development-tracker",
     "Track the development of new skills for agents: which skills are being built, testing status, deployment readiness, and integration with existing agent capabilities.",
     "agent-tools", "Normal"),
    ("infrastructure-project-manager",
     "Manage infrastructure projects: migrations, upgrades, new tool deployments, and architecture changes. Coordinate with Lead Developer, TechOps, and S-Agent to ensure infrastructure work is planned, tracked, and completed.",
     "operations", "Normal"),
    ("content-production-tracker",
     "Track the content production pipeline: content in ideation, in writing, in design, in review, scheduled, and published. Ensure the LinkedIn Content Agent's output pipeline flows without bottlenecks.",
     "operations", "Normal"),
    ("internal-process-change-tracker",
     "When a process changes, track the implementation: new SOP deployed, affected agents notified, training completed, and old process officially deprecated. Process changes are not done until adoption is confirmed.",
     "operations", "Normal"),

    # ─── 10. CLIENT PROJECT MANAGEMENT ───────────────────────────────────
    ("client-project-portfolio-manager",
     "Manage the portfolio of all active client projects: status overview, timeline health, resource allocation, risk status, and milestone tracking across every client engagement simultaneously.",
     "operations", "High"),
    ("client-project-task-manager",
     "Manage task-level execution within client projects: task creation from deliverables, assignment to Lead Developer agent, progress tracking, quality verification, and deliverable packaging.",
     "operations", "High"),
    ("client-timeline-guardian",
     "Guard client timelines: monitor progress against committed dates, identify timeline risk early, calculate recovery paths when delays occur, and communicate timeline changes proactively.",
     "operations", "High"),
    ("client-milestone-invoice-trigger",
     "When a client milestone is completed and accepted, trigger the invoicing workflow: notify the Finance Agent with milestone details, confirmation of acceptance, and the billing amount per contract terms.",
     "workflow", "High"),
    ("client-scope-change-task-manager",
     "When a scope change is approved, create and integrate the new tasks: add to the project plan, adjust timelines, reassign resources if needed, and update all tracking platforms.",
     "workflow", "Normal"),
    ("client-project-handoff-manager",
     "Manage the handoff from project completion to ongoing operations or retainer: archive project tasks, create maintenance task templates, transition from project tracking to retainer tracking, and ensure nothing from the project phase leaks into an untracked state.",
     "workflow", "Normal"),
    ("multi-client-resource-balancer",
     "Balance resources across multiple active client projects: prevent one client's project from starving another, manage priority conflicts, and ensure all clients receive consistent service quality.",
     "operations", "High"),
    ("client-project-template-deployer",
     "Deploy project templates for new client engagements: create the full task structure, assign standard tasks, configure milestone tracking, and set up reporting — all from a template that is refined with every project.",
     "operations", "Normal"),

    # ─── 11. REPORTING & DASHBOARDS ──────────────────────────────────────
    ("daily-operations-report",
     "Produce a daily operations report: tasks completed across all agents, tasks started, tasks blocked, overdue items, and today's priorities. The pulse of the operation in one page.",
     "operations", "High"),
    ("weekly-project-status-report",
     "Produce weekly status across all projects: per-project status summary, milestone progress, velocity trends, risks, and next-week priorities. The report Yasmine and Amira use for weekly planning.",
     "operations", "High"),
    ("weekly-agent-performance-report",
     "Weekly agent performance: tasks assigned, tasks completed, on-time rate, quality rate, and capacity utilization per agent. Identify which agents are crushing it and which need support.",
     "operations", "Normal"),
    ("monthly-portfolio-report",
     "Monthly comprehensive portfolio report: all active projects status, resource utilization, timeline adherence, budget burn, quality metrics, and strategic recommendations.",
     "operations", "Normal"),
    ("sprint-report-generator",
     "Generate sprint reports: what was committed, what was delivered, velocity achieved, carryover items, and retrospective findings.",
     "operations", "Normal"),
    ("client-status-report-feeder",
     "Feed accurate project data to the Client Success Agent for client-facing reports: task completion percentages, milestone status, next deliverable timelines, and any items needing client input. Ensure client reports reflect reality.",
     "operations", "High"),
    ("executive-dashboard-maintainer",
     "Maintain an executive dashboard for Yasmine: all projects at a glance, overall capacity utilization, pipeline health, financial health, and the three most important things needing attention.",
     "operations", "High"),
    ("trend-and-velocity-reporter",
     "Track and report trends: are we getting faster at delivery, are projects becoming more predictable, are estimates becoming more accurate, and is task quality improving over time.",
     "operations", "Normal"),
    ("bottleneck-report",
     "Produce a bottleneck report: where are tasks piling up, which agents are over capacity, which dependencies are causing delays, and what systemic issues are slowing the operation down.",
     "operations", "Normal"),

    # ─── 12. REMINDERS, FOLLOW-UPS & NUDGES ──────────────────────────────
    ("smart-reminder-system",
     "Send intelligent reminders: not just this is due tomorrow but this is due tomorrow and here is the context you need, the files you will want, and 30 minutes is blocked on your calendar. Reminders that enable action, not just anxiety.",
     "workflow", "High"),
    ("escalating-follow-up-system",
     "For overdue items, escalate follow-ups: first a friendly nudge, then a direct reminder with impact context (this is blocking X), then an escalation to Amira. Graduated pressure that resolves without confrontation.",
     "workflow", "High"),
    ("waiting-on-others-tracker",
     "Track everything that is waiting on someone else: client approvals, external vendor deliverables, agent responses, and stakeholder decisions. Follow up systematically and report on aging waiting items.",
     "workflow", "High"),
    ("recurring-task-scheduler",
     "Manage recurring tasks across the operation: weekly reports, monthly reviews, quarterly audits, and daily standups. Ensure recurring tasks auto-create on schedule with updated context for the current period.",
     "workflow", "Normal"),
    ("deadline-early-warning-system",
     "Issue early warnings for approaching deadlines: 1 week out (is the task on track?), 3 days out (is everything needed available?), 1 day out (final reminder with all context), and day-of (last chance alert).",
     "workflow", "High"),
    ("commitment-tracker",
     "Track commitments made in meetings, emails, and conversations: who committed to what, by when, and is it in the task system? If someone said I will have that by Friday, there should be a task and a reminder.",
     "workflow", "High"),
    ("promise-to-client-tracker",
     "Track every promise made to clients: deliverable dates, response commitments, follow-up promises, and feature commitments. Broken promises are the fastest path to lost clients.",
     "workflow", "High"),

    # ─── 13. WORKFLOW OPTIMIZATION ───────────────────────────────────────
    ("task-flow-optimizer",
     "Optimize the flow of tasks through the system: reduce wait times between stages, minimize handoff friction, eliminate unnecessary approval gates, and streamline the path from created to done.",
     "workflow", "Normal"),
    ("estimation-accuracy-improver",
     "Track estimated vs. actual time for all tasks. Analyze patterns: which task types are consistently underestimated, which agents estimate well, and what factors cause estimates to miss. Use data to improve future estimates.",
     "operations", "Normal"),
    ("task-size-optimizer",
     "Analyze task sizes for optimal execution: are tasks too large (causing procrastination and unclear progress) or too small (causing overhead and context-switching)? Find and enforce the optimal task granularity.",
     "workflow", "Normal"),
    ("process-cycle-time-reducer",
     "Identify and reduce cycle times for common processes: how long does client onboarding take end-to-end, how long from content idea to published post, and how long from project kickoff to first deliverable. Reduce every cycle.",
     "workflow", "Normal"),
    ("meeting-to-task-efficiency",
     "Maximize meeting-to-task efficiency: ensure every meeting produces clear action items, action items are captured as tasks within 30 minutes, and meetings that produce no actions are flagged for elimination.",
     "workflow", "Normal"),
    ("template-improvement-engine",
     "Continuously improve task and project templates: add steps that were consistently forgotten, remove steps that are consistently skipped, update descriptions with lessons learned, and incorporate new tools or processes.",
     "operations", "Normal"),
    ("work-in-progress-limiter",
     "Enforce WIP limits: prevent too many tasks from being in progress simultaneously (for Yasmine and for each agent). Too much WIP means nothing finishes. Force completion before starting new work.",
     "workflow", "Normal"),
    ("task-batching-optimizer",
     "Identify tasks that should be batched for efficiency: similar research tasks, similar writing tasks, similar configuration tasks. Group them so the assignee can get into a flow state rather than context-switching.",
     "workflow", "Normal"),

    # ─── 14. CROSS-FUNCTIONAL COORDINATION ───────────────────────────────
    ("cross-agent-project-coordinator",
     "Coordinate work that spans multiple agents: when a client project needs Research Analyst output feeding into Lead Developer work feeding into Client Success delivery, ensure the chain is sequenced, tracked, and flowing.",
     "agent-tools", "High"),
    ("dependency-chain-expediter",
     "When a task on the critical path is delayed, actively expedite: escalate with the responsible agent, propose shortcuts, find alternative paths, and communicate downstream impact to all affected agents.",
     "workflow", "High"),
    ("inter-project-dependency-manager",
     "Manage dependencies between projects: when an internal tool upgrade affects a client project timeline, or when a research output is needed by both the content team and the outreach team simultaneously.",
     "operations", "Normal"),
    ("resource-conflict-resolver",
     "When two projects need the same agent at the same time, resolve the conflict: assess priority, negotiate timelines, propose task sequencing, and communicate the resolution to all affected parties.",
     "agent-tools", "High"),
    ("meeting-coordination-engine",
     "Coordinate all project-related meetings: schedule syncs only when needed, prepare agendas from task data, ensure all relevant agents have pre-read materials, and cancel meetings where async updates suffice.",
     "workflow", "Normal"),
    ("stakeholder-communication-coordinator",
     "Ensure the right stakeholders get the right information at the right time: Yasmine gets executive summaries, agents get detailed task updates, clients get polished progress reports, and nobody gets information they do not need.",
     "workflow", "Normal"),

    # ─── 15. KNOWLEDGE & DOCUMENTATION ───────────────────────────────────
    ("project-lessons-learned-capturer",
     "At the end of every project, capture lessons learned: what worked, what did not, what was learned, and what should change for next time. Store in a searchable format linked to the project type.",
     "operations", "Normal"),
    ("estimation-database-maintainer",
     "Maintain a database of task estimates vs. actuals: by task type, by agent, by project type, and by complexity level. This database makes every future estimate more accurate.",
     "operations", "Normal"),
    ("pm-playbook-maintainer",
     "Maintain the PM playbook: standard procedures for every PM activity (project setup, sprint planning, status reporting, escalation, closeout), updated with improvements from every project cycle.",
     "operations", "Normal"),
    ("project-archive-manager",
     "Archive completed projects: store all project data, tasks, deliverables, timelines, and retrospective notes in an organized, retrievable format. Make past project knowledge accessible for future reference.",
     "operations", "Normal"),
    ("decision-log-keeper",
     "Log every significant project decision: what was decided, by whom, based on what information, and what the expected outcome was. Decision logs prevent revisiting settled questions and provide context for future questions.",
     "operations", "Normal"),
    ("task-pattern-library",
     "Build a library of task patterns from experience: common task sequences, typical subtask structures, recurring checklist items, and known pitfalls by task type. Each project makes the library richer.",
     "operations", "Normal"),

    # ─── 16. STRATEGIC PROJECT INTELLIGENCE ──────────────────────────────
    ("portfolio-health-analyzer",
     "Analyze the health of the entire project portfolio: are we overcommitted, is work balanced, are high-priority projects getting adequate resources, and what is the risk exposure across the portfolio.",
     "operations", "High"),
    ("capacity-vs-demand-forecaster",
     "Forecast capacity vs. demand: based on current projects, pipeline deals, internal initiatives, and seasonal patterns, when will the agency be at capacity? When is capacity opening up? Inform both sales pacing and hiring/scaling decisions.",
     "operations", "High"),
    ("project-profitability-analyzer",
     "Analyze project profitability: actual hours vs. estimated hours, actual cost vs. revenue, and margin by project type. Feed findings to the Finance Agent and to future pricing decisions.",
     "operations", "Normal"),
    ("delivery-predictability-scorer",
     "Score the agency's delivery predictability: what percentage of projects deliver on time, within budget, and to spec? Track the score over time and identify what drives predictability improvement.",
     "operations", "Normal"),
    ("process-maturity-assessor",
     "Assess PM process maturity: are we ad-hoc, defined, managed, or optimized? Where are the maturity gaps and what is the next improvement to make.",
     "operations", "Normal"),
    ("quarterly-pm-strategy-reviewer",
     "Quarterly review of PM operations: what is working, what is struggling, what tools or processes need to change, and what the PM improvement priorities are for next quarter.",
     "operations", "Normal"),
    ("annual-delivery-review",
     "Annual comprehensive review: total projects delivered, on-time rate, client satisfaction, agent utilization, and year-over-year improvement in delivery capability.",
     "operations", "Normal"),
]


def build_record(skill_name, description, category, priority):
    return {
        "fields": {
            "Name": skill_name,
            "Description": description,
            "Target Agent": [{"id": YUSUF_RECORD_ID}],
            "Status": "Backlog",
            "Workspace": WORKSPACE,
            "Builder": BUILDER,
            "Creation Skill": CREATION_SKILL,
            "Priority": priority,
            "Category": category,
        }
    }


def batch(lst, size=25):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def main():
    parser = argparse.ArgumentParser(description="Load Yusuf PM Agent skills into Teable Skills Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print skills without inserting")
    args = parser.parse_args()

    print(f"\nYusuf PM Agent Skills Loader")
    print(f"Total skills: {len(YUSUF_SKILLS)}")
    print(f"Table: {TABLE_ID}")
    print(f"Agent record: {YUSUF_RECORD_ID}")
    print("=" * 60)

    if args.dry_run:
        for i, (name, desc, cat, pri) in enumerate(YUSUF_SKILLS, 1):
            print(f"  [{i:3}] {name} | {cat} | {pri}")
        print(f"\n[DRY RUN] Would insert {len(YUSUF_SKILLS)} skills")
        return

    from extended import TeableExtendedClient
    client = TeableExtendedClient()

    records = [build_record(name, desc, cat, pri) for name, desc, cat, pri in YUSUF_SKILLS]

    inserted = 0
    failed = 0
    for i, chunk in enumerate(batch(records, 25)):
        print(f"  Inserting batch {i + 1} ({len(chunk)} records)...", end=" ", flush=True)
        try:
            client.create_records(TABLE_ID, chunk)
            inserted += len(chunk)
            print(f"OK ({inserted}/{len(records)})")
        except Exception as e:
            failed += len(chunk)
            print(f"FAILED: {e}")
        time.sleep(0.3)

    print("\n" + "=" * 60)
    print(f"Done. Inserted: {inserted} | Failed: {failed}")
    if failed == 0:
        print("All 135 Yusuf PM Agent skills loaded successfully.")


if __name__ == "__main__":
    main()
