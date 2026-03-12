#!/usr/bin/env python3
"""
Load all 138 Rafi (TechOps Agent) skills into the Teable Skills Pipeline.

Usage:
    TEABLE_API_TOKEN="..." python3 load_rafi_skills.py
    TEABLE_API_TOKEN="..." python3 load_rafi_skills.py --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

TABLE_ID = "tblyl5mzFebauxrGf1L"
RAFI_RECORD_ID = "rec7VbQBQpcglcI4Kyj"
WORKSPACE = "rafi-workspace"
BUILDER = "Zahra"
CREATION_SKILL = "Skillforge"

# All 138 Rafi skills: (name, description, category, priority)
RAFI_SKILLS = [
    # ─── 1. CONTINUOUS MONITORING ───────────────────────────────────────
    ("cron-job-monitor",
     "Monitor every scheduled cron job: did it fire on time, complete successfully, produce expected output, and finish within expected duration. Alert immediately on any failure, hang, or skipped execution.",
     "operations", "High"),
    ("cron-job-failure-diagnoser",
     "When a cron job fails, automatically diagnose the cause: check error log, identify permission issues, missing dependencies, resource exhaustion, timeouts, changed endpoints, expired credentials, or code errors.",
     "operations", "High"),
    ("automation-execution-monitor",
     "Monitor all automations (n8n, Make, Zapier, custom scripts): execution status, success/failure rates, duration, and output validation. Catch automations that run but produce wrong results.",
     "operations", "High"),
    ("api-endpoint-health-checker",
     "Continuously health-check all API endpoints the agency depends on: internal APIs, third-party APIs, webhook receivers, and integration endpoints. Monitor response times, status codes, and payload integrity.",
     "operations", "High"),
    ("webhook-delivery-monitor",
     "Monitor all inbound and outbound webhooks: delivery confirmations, payload integrity, retry status, and dead letter queues. Detect webhooks that silently fail.",
     "operations", "High"),
    ("database-health-monitor",
     "Monitor all databases: connection pool status, query performance, storage utilization, replication lag, backup status, and index health. Alert on slow queries, approaching storage limits, and failed backups.",
     "operations", "High"),
    ("server-resource-monitor",
     "Monitor server resources across all infrastructure: CPU utilization, memory usage, disk space, network throughput, and process counts. Alert when resources approach thresholds before performance degrades.",
     "operations", "High"),
    ("ssl-certificate-monitor",
     "Monitor SSL/TLS certificates across all domains and services: expiration dates, configuration validity, and certificate chain integrity. Alert 30, 14, and 7 days before expiration. Auto-renew where configured.",
     "operations", "High"),
    ("dns-resolution-monitor",
     "Monitor DNS resolution for all domains: verify records resolve correctly, check propagation status after changes, and detect unauthorized DNS modifications.",
     "operations", "Normal"),
    ("uptime-monitor",
     "Monitor uptime for all deployed applications, client projects, internal tools, and critical services. Track uptime percentage, detect downtime within 60 seconds, and trigger incident response.",
     "operations", "High"),
    ("email-deliverability-system-monitor",
     "Monitor health of all email sending infrastructure: SPF/DKIM/DMARC pass rates, sending IP reputation, warmup tool health, and mailbox connectivity. Coordinate with Cold Email Specialist on deliverability issues.",
     "operations", "High"),
    ("queue-depth-monitor",
     "Monitor all job queues, message queues, and task queues: depth trends, processing rates, stuck jobs, and consumer health. A growing queue is an early warning of downstream failure.",
     "operations", "High"),
    ("log-aggregation-monitor",
     "Monitor log aggregation systems: are logs being collected, are they searchable, is storage within limits, and are there gaps in log coverage. The monitoring of the monitoring.",
     "operations", "Normal"),
    ("third-party-status-watcher",
     "Monitor status pages of all critical third-party services (Stripe, OpenAI, Anthropic, Vercel, Google Workspace, GitHub, etc.). Detect outages and correlate with internal issues.",
     "operations", "High"),
    ("heartbeat-monitor",
     "Implement heartbeat checks for all background processes, long-running services, and agent systems: each system regularly reports it is alive. If a heartbeat is missed, investigate immediately.",
     "operations", "High"),

    # ─── 2. PROACTIVE ISSUE DETECTION ───────────────────────────────────
    ("anomaly-detector",
     "Detect anomalies across all monitored metrics: unusual traffic patterns, unexpected error rate spikes, abnormal resource consumption, irregular execution times, and data volume deviations.",
     "operations", "High"),
    ("trend-based-failure-predictor",
     "Analyze metric trends to predict failures before they occur: disk space filling at current rate, memory leak growing, API rate limit approaching. Fix the trajectory, not the crash.",
     "operations", "High"),
    ("configuration-drift-detector",
     "Detect configuration drift: when a system's actual configuration diverges from its documented or intended configuration. Drift accumulates silently and causes mysterious failures weeks later.",
     "operations", "Normal"),
    ("credential-expiration-tracker",
     "Track expiration dates for all credentials: API keys, OAuth tokens, service account passwords, SSL certificates, domain registrations, and license keys. Alert well in advance and manage rotation.",
     "operations", "High"),
    ("dependency-vulnerability-scanner",
     "Continuously scan all project dependencies for known vulnerabilities: npm audit, pip safety check, Docker image scanning, and third-party library CVE monitoring. Prioritize by severity and exploitability.",
     "operations", "High"),
    ("stale-process-detector",
     "Detect stale processes: automations that have not run in 30+ days, scripts referencing deprecated endpoints, integrations using old API versions, and scheduled tasks for discontinued features.",
     "operations", "Normal"),
    ("silent-failure-hunter",
     "Actively hunt for silent failures: processes that run without errors but produce no output, integrations returning 200 with empty payloads, automations that execute but don't achieve their intended effect.",
     "operations", "High"),
    ("resource-leak-detector",
     "Detect resource leaks: memory not being freed, database connections not being closed, file handles accumulating, temp files growing, and orphaned processes consuming resources.",
     "operations", "High"),
    ("integration-degradation-detector",
     "Detect when integrations are degrading but not failing: response times slowly increasing, partial data returns more frequent, retry rates climbing, success rates declining.",
     "operations", "High"),
    ("data-integrity-checker",
     "Periodically verify data integrity across systems: records that should exist in System A also in System B, counts matching, timestamps consistent, and data flowing correctly through the pipeline.",
     "operations", "Normal"),

    # ─── 3. AUTOMATED REMEDIATION ────────────────────────────────────────
    ("auto-fix-engine",
     "For known failure patterns, automatically apply fixes without waiting for human intervention: restart failed services, retry failed jobs, refresh expired tokens, clear temp directories, reconnect dropped integrations.",
     "workflow", "High"),
    ("cron-job-auto-restarter",
     "When a cron job fails, automatically attempt restart based on failure type: immediate retry for transient errors, delayed retry for resource issues, dependency-check-then-retry for upstream failures.",
     "workflow", "High"),
    ("service-auto-healer",
     "Automatically heal failed services: restart crashed processes, reconnect dropped database connections, refresh stale caches, and re-register dropped webhook subscriptions.",
     "workflow", "High"),
    ("disk-space-auto-cleaner",
     "When disk space crosses warning thresholds, automatically clean: remove old log files, clear build caches, compress archived data, clean temp directories, and alert if automated cleaning cannot free sufficient space.",
     "workflow", "High"),
    ("token-auto-refresher",
     "Automatically refresh OAuth tokens, API keys with rotation capabilities, and session tokens before they expire. Maintain a schedule of all credential lifetimes and proactively rotate.",
     "workflow", "High"),
    ("failed-webhook-replayer",
     "When webhooks fail delivery, automatically replay them: pull from dead letter queues, verify the receiving endpoint is healthy, replay in order, and confirm successful delivery.",
     "workflow", "High"),
    ("stuck-job-unsticker",
     "Detect and unstick stuck jobs: identify jobs exceeding expected duration by 3x+, determine if they are actually processing or hung, kill hung processes, and restart with appropriate state recovery.",
     "workflow", "High"),
    ("auto-scaling-trigger",
     "When resource utilization crosses thresholds, automatically trigger scaling actions: increase container resources, spin up additional instances, or activate overflow capacity. Scale down when demand normalizes.",
     "workflow", "Normal"),
    ("backup-failure-auto-retrier",
     "When scheduled backups fail, automatically diagnose and retry: check storage availability, verify credentials, confirm network connectivity, and attempt backup with adjusted parameters.",
     "workflow", "High"),
    ("self-healing-integration-reconnector",
     "When an integration disconnects (API timeout, auth failure, rate limit), automatically reconnect: wait for rate limit windows, refresh authentication, re-establish WebSocket connections, and resume from last checkpoint.",
     "workflow", "High"),

    # ─── 4. TECH SUPPORT FOR ALL AGENTS ──────────────────────────────────
    ("agent-tech-request-receiver",
     "Receive and triage technical support requests from any agent in the fleet: parse the request, classify by type (bug, configuration, access, performance, capability), assess urgency, and route to resolution workflow.",
     "agent-tools", "High"),
    ("agent-bug-fixer",
     "Diagnose and fix bugs reported by other agents: reproduce the issue, identify root cause, implement the fix, test, deploy, and confirm resolution with the requesting agent.",
     "agent-tools", "High"),
    ("agent-configuration-supporter",
     "Handle configuration requests from agents: update environment variables, adjust tool settings, modify integration parameters, and change workflow configurations. Verify changes don't break dependent systems.",
     "agent-tools", "Normal"),
    ("agent-access-provisioner",
     "Provision access for agents that need new tool access, API keys, or system permissions: verify the request is appropriate, create the credentials, configure the access, test connectivity, and confirm with requesting agent.",
     "agent-tools", "Normal"),
    ("agent-performance-troubleshooter",
     "When an agent reports slow performance: diagnose the bottleneck (API latency, database query, memory limits, rate limiting, or resource contention), implement the fix, and optimize for sustained performance.",
     "agent-tools", "High"),
    ("agent-capability-expander",
     "When an agent needs a new capability (new API integration, new tool access, new automation): evaluate the request, design the implementation, build or configure it, test it, and hand off with documentation.",
     "agent-tools", "Normal"),
    ("agent-error-interpreter",
     "When an agent encounters an error it cannot resolve: interpret the error in context, explain what went wrong, implement the fix, and educate the agent's error handling to catch similar issues in the future.",
     "agent-tools", "Normal"),
    ("agent-request-priority-manager",
     "Manage the priority queue of all agent tech requests: critical issues first (blocking agent work), then high (degrading performance), then medium (improvement requests), then low (nice-to-haves). Communicate ETAs.",
     "agent-tools", "Normal"),
    ("inter-agent-integration-fixer",
     "When data flow between agents breaks (handoff failures, format mismatches, routing errors): diagnose the integration point, fix the data flow, validate end-to-end, and add monitoring to prevent recurrence.",
     "agent-tools", "High"),
    ("agent-tech-support-knowledge-base",
     "Maintain a knowledge base of resolved agent tech issues: searchable by error type, agent, and system. Before investigating a new issue, check if it has been solved before to reduce resolution time.",
     "agent-tools", "Normal"),

    # ─── 5. CLAUDE SYSTEM MANAGEMENT ─────────────────────────────────────
    ("claude-config-backup-to-github",
     "Regularly back up the entire Claude system configuration to GitHub: agent configs, skill files, memory edits, prompt templates, tool configurations, and custom settings. Maintain version history with meaningful commit messages.",
     "operations", "High"),
    ("claude-backup-scheduler",
     "Schedule automated Claude backups: daily incremental backups, weekly full backups, and on-demand backups before major changes. Verify backup integrity after each run.",
     "operations", "Normal"),
    ("claude-backup-restore-tester",
     "Periodically test backup restoration: pull a backup from GitHub, verify completeness, confirm all configs are intact, and document the restoration procedure. A backup that cannot be restored is not a backup.",
     "operations", "Normal"),
    ("claude-update-checker",
     "Monitor for Claude platform updates, new features, API changes, and capability additions: check Anthropic changelog, documentation updates, and community channels. Flag new capabilities that could benefit the agency.",
     "operations", "Normal"),
    ("claude-update-impact-assessor",
     "When a Claude update is available, assess its impact: what changes, what might break, what new capabilities are available, and what configuration adjustments are needed. Categorize as implement-now, schedule, or monitor.",
     "operations", "Normal"),
    ("claude-feature-implementer",
     "Implement new Claude features: update configurations, adjust prompts to leverage new capabilities, add new tool integrations, and modify agent behaviors to take advantage of platform improvements.",
     "operations", "Normal"),
    ("claude-memory-health-checker",
     "Monitor Claude memory system health: are memories being stored correctly, are retrievals working accurately, are there stale or conflicting memories, and is the memory system being utilized effectively by all agents.",
     "operations", "High"),
    ("claude-memory-optimizer",
     "Optimize Claude memory: identify redundant memories, consolidate related memories, remove outdated information, and ensure high-value context is prioritized. Clean memory means better agent performance.",
     "operations", "Normal"),
    ("claude-prompt-performance-monitor",
     "Monitor the performance of agent prompts and skill files: are agents producing expected quality outputs, are there prompt drift issues, and are there prompt patterns that consistently underperform.",
     "operations", "Normal"),
    ("claude-skill-file-auditor",
     "Audit all skill files across the agent fleet: verify they are current, check for conflicts between skills, ensure triggers are firing correctly, and identify skills that need updating based on system changes.",
     "operations", "Normal"),
    ("claude-context-window-optimizer",
     "Monitor and optimize context window usage across agents: are agents hitting context limits, is irrelevant context consuming window space, and can context be structured more efficiently for better performance.",
     "operations", "Normal"),
    ("claude-rollback-manager",
     "When a Claude configuration change causes problems, execute rollback: restore from the most recent known-good GitHub backup, verify restoration, and document what went wrong with the change.",
     "operations", "High"),

    # ─── 6. SCRIPT & CODE HEALTH ──────────────────────────────────────────
    ("script-health-scanner",
     "Scan all operational scripts (bash, Python, Node) for health issues: deprecated function calls, hardcoded values that should be environment variables, missing error handling, and outdated dependencies.",
     "operations", "Normal"),
    ("script-failure-fixer",
     "When a script fails in production, diagnose and fix: read error output, identify the failure point, check for environmental changes that caused the break, implement the fix, and add error handling to prevent recurrence.",
     "operations", "High"),
    ("script-dependency-updater",
     "Monitor and update script dependencies: check for outdated packages, apply security patches, test compatibility after updates, and maintain a dependency manifest for each script.",
     "operations", "Normal"),
    ("script-performance-optimizer",
     "Identify and optimize slow scripts: profile execution time, find bottlenecks (slow loops, inefficient queries, unnecessary API calls), implement optimizations, and measure improvement.",
     "operations", "Normal"),
    ("dead-code-cleaner",
     "Identify and remove dead code: scripts that are no longer called, functions that are never executed, commented-out blocks that will never be uncommented, and configuration for features that no longer exist.",
     "operations", "Normal"),
    ("environment-variable-auditor",
     "Audit all environment variables across all systems: verify they are set correctly, check for missing variables that scripts expect, identify unused variables, and ensure sensitive values are not hardcoded or logged.",
     "operations", "High"),
    ("script-documentation-enforcer",
     "Ensure all scripts are documented: purpose, expected inputs, expected outputs, dependencies, schedule (if cron), and error handling behavior. Undocumented scripts are unmaintainable scripts.",
     "operations", "Normal"),
    ("code-syntax-validator",
     "Run syntax validation on all configuration files, scripts, and automation definitions: YAML, JSON, TOML, crontab syntax, n8n flow definitions, and Dockerfile syntax. Catch syntax errors before runtime failures.",
     "operations", "Normal"),

    # ─── 7. INFRASTRUCTURE MANAGEMENT ────────────────────────────────────
    ("server-configuration-manager",
     "Manage server configurations across all infrastructure: OS patches, security updates, firewall rules, service configurations, and system settings. Maintain configuration-as-code where possible.",
     "operations", "Normal"),
    ("docker-container-health-monitor",
     "Monitor all Docker containers: running status, resource usage, restart counts, log output, and image freshness. Detect containers that are crash-looping, consuming excessive resources, or running outdated images.",
     "operations", "High"),
    ("docker-image-updater",
     "Track and update Docker images: check for base image updates, rebuild images with security patches, test updated images, and deploy with rollback capability.",
     "operations", "Normal"),
    ("network-connectivity-tester",
     "Test network connectivity between all systems: internal service-to-service communication, external API reachability, DNS resolution, and firewall rule verification. Detect networking issues before they affect operations.",
     "operations", "Normal"),
    ("load-balancer-monitor",
     "Monitor load balancer health: traffic distribution, backend health, SSL termination, and routing rules. Detect misconfiguration and uneven distribution.",
     "operations", "Normal"),
    ("cdn-and-cache-monitor",
     "Monitor CDN and caching layers: cache hit rates, invalidation status, origin server load, and content freshness. Ensure cached content is serving correctly and efficiently.",
     "operations", "Normal"),
    ("infrastructure-cost-monitor",
     "Monitor infrastructure costs in real-time: track spending against budget, identify cost anomalies (unexpected spikes), and flag resources that are over-provisioned or idle.",
     "operations", "Normal"),
    ("deployment-pipeline-monitor",
     "Monitor CI/CD pipeline health: build success rates, deployment frequency, rollback frequency, and pipeline execution times. A degrading pipeline slows the entire development cycle.",
     "operations", "Normal"),
    ("staging-production-parity-checker",
     "Verify parity between staging and production environments: same configurations, same dependency versions, same environment variable structure, and same infrastructure specs.",
     "operations", "Normal"),

    # ─── 8. BACKUP & DISASTER RECOVERY ───────────────────────────────────
    ("backup-system-manager",
     "Manage all backup systems: schedule, verify, and monitor backups for databases, file systems, configurations, code repositories, and critical data stores. Maintain backup inventory with retention policies.",
     "operations", "High"),
    ("backup-integrity-verifier",
     "Regularly verify backup integrity: can backups be decompressed, are checksums valid, is the data complete, and can a restore actually be performed. Run verification weekly for critical systems.",
     "operations", "High"),
    ("disaster-recovery-plan-maintainer",
     "Maintain the disaster recovery plan: documented procedures for every critical system failure scenario, updated contact information, current infrastructure details, and tested recovery timelines.",
     "operations", "Normal"),
    ("disaster-recovery-drill-conductor",
     "Conduct periodic DR drills: simulate a system failure, execute recovery procedures, measure recovery time, identify gaps in the plan, and update procedures based on drill results.",
     "operations", "Normal"),
    ("point-in-time-recovery-manager",
     "For databases and critical stores, maintain point-in-time recovery capability: transaction logs, WAL archiving, and tested recovery to specific timestamps.",
     "operations", "Normal"),
    ("cross-region-backup-manager",
     "Manage backups stored in separate regions or providers: ensure geographic redundancy for critical data, verify cross-region restore capability, and maintain sync between primary and backup locations.",
     "operations", "Normal"),
    ("github-repo-backup-manager",
     "Back up all GitHub repositories including the Claude system backup repo: mirror to a secondary location, verify backup completeness, and maintain an inventory of all repos with backup status.",
     "operations", "Normal"),

    # ─── 9. PERFORMANCE TUNING & OPTIMIZATION ────────────────────────────
    ("system-performance-profiler",
     "Profile overall system performance: identify the slowest components, most resource-hungry processes, and operations with worst user-perceived latency. Produce a performance heatmap.",
     "operations", "Normal"),
    ("database-query-optimizer",
     "Identify and optimize slow database queries: analyze query execution plans, recommend index additions, suggest query rewrites, and measure improvement after optimization.",
     "operations", "Normal"),
    ("api-response-time-optimizer",
     "Optimize API response times: identify slow endpoints, diagnose causes (database, computation, external calls), implement caching, optimize code paths, and measure improvement.",
     "operations", "Normal"),
    ("memory-usage-optimizer",
     "Optimize memory usage across all services: identify memory-hungry processes, find memory leaks, optimize data structures, implement garbage collection tuning, and right-size container memory limits.",
     "operations", "Normal"),
    ("caching-strategy-tuner",
     "Tune caching strategies across the stack: adjust TTLs based on data change frequency, implement cache warming for predictable access patterns, optimize cache key design, and monitor cache effectiveness.",
     "operations", "Normal"),
    ("batch-process-optimizer",
     "Optimize batch processes (data imports, report generation, bulk operations): parallelize where possible, optimize chunk sizes, schedule during low-load periods, and reduce total execution time.",
     "operations", "Normal"),
    ("cold-start-eliminator",
     "Identify and eliminate cold start problems: serverless function cold starts, container spin-up delays, connection establishment overhead, and cache miss storms after restarts. Pre-warm systems.",
     "operations", "Normal"),
    ("rate-limit-optimizer",
     "Optimize API rate limit usage: distribute requests evenly over time, implement request queuing, batch where possible, and prioritize high-value requests when approaching limits.",
     "operations", "Normal"),
    ("cost-performance-optimizer",
     "Find the optimal balance between cost and performance: identify over-provisioned resources wasting money, under-provisioned resources degrading performance, and the sweet spot for each component.",
     "operations", "Normal"),

    # ─── 10. SECURITY MONITORING & HARDENING ─────────────────────────────
    ("security-event-monitor",
     "Monitor security events: failed login attempts, unusual access patterns, permission changes, new admin accounts, and API key usage anomalies. Detect potential security incidents early.",
     "operations", "High"),
    ("intrusion-detection-monitor",
     "Monitor for intrusion indicators: unexpected processes, unauthorized network connections, file system changes in protected directories, and privilege escalation attempts.",
     "operations", "High"),
    ("secrets-exposure-scanner",
     "Scan for exposed secrets: API keys in code, credentials in logs, passwords in configuration files, and tokens in error messages. Alert immediately on any exposure and rotate the compromised credential.",
     "operations", "High"),
    ("patch-management-system",
     "Manage security patching: track available patches for all systems, assess criticality, schedule and apply patches, verify post-patch system health, and maintain patch compliance records.",
     "operations", "High"),
    ("firewall-rule-auditor",
     "Audit firewall rules: verify rules match documented policy, identify overly permissive rules, remove rules for decommissioned services, and test that blocked traffic is actually blocked.",
     "operations", "Normal"),
    ("access-log-analyzer",
     "Analyze access logs for suspicious patterns: brute force attempts, credential stuffing, API abuse, data scraping, and authorized users accessing unusual resources.",
     "operations", "High"),
    ("security-hardening-implementer",
     "Implement security hardening: disable unnecessary services, enforce strong authentication, configure security headers, implement CSP policies, and follow CIS benchmarks for server hardening.",
     "operations", "Normal"),

    # ─── 11. INCIDENT MANAGEMENT ─────────────────────────────────────────
    ("incident-detector",
     "Detect incidents through multiple signals: monitoring alerts, error rate spikes, user reports, and cascading failures. Classify incident severity (P1-P4) and initiate the appropriate response.",
     "workflow", "High"),
    ("incident-response-coordinator",
     "Coordinate incident response: assemble the response team (relevant agents), establish communication channels, track mitigation progress, and manage the timeline from detection to resolution.",
     "workflow", "High"),
    ("incident-triage-engine",
     "Triage incidents: determine scope (which systems affected), impact (which users/clients affected), urgency (is it getting worse), and root cause hypothesis. Direct investigation toward the most likely cause.",
     "workflow", "High"),
    ("incident-communicator",
     "Communicate during incidents: internal status to Amira and Yasmine, client-facing communications if client systems are affected, and status page updates if applicable. Keep stakeholders informed.",
     "workflow", "High"),
    ("incident-resolution-tracker",
     "Track incident resolution: what was tried, what worked, what did not, current status, and ETA to resolution. Maintain a real-time incident log for post-mortem reference.",
     "workflow", "High"),
    ("post-incident-reviewer",
     "Conduct post-incident reviews: timeline reconstruction, root cause analysis, contributing factors, detection effectiveness, response effectiveness, and remediation actions. Produce a post-incident report.",
     "workflow", "Normal"),
    ("incident-pattern-analyzer",
     "Analyze incident patterns over time: recurring failure modes, common root causes, systems with highest incident frequency, and time-of-day or day-of-week patterns. Use patterns to drive preventive improvements.",
     "workflow", "Normal"),
    ("incident-runbook-updater",
     "After each incident, update the relevant runbook: add the new failure mode, document the resolution steps that worked, and update the diagnostic checklist. Each incident makes future incidents faster to resolve.",
     "workflow", "Normal"),

    # ─── 12. SELF-LEARNING & CONTINUOUS IMPROVEMENT ───────────────────────
    ("failure-pattern-learner",
     "Learn from every failure: catalog the root cause, symptoms, detection method, and resolution. Build a failure pattern library that enables faster diagnosis and predictive detection.",
     "operations", "High"),
    ("resolution-playbook-builder",
     "Build resolution playbooks from experience: for each known failure type, document the fastest path to resolution. Over time, the playbook grows comprehensive enough to handle most issues automatically.",
     "operations", "Normal"),
    ("monitoring-gap-identifier",
     "After every incident, evaluate: should monitoring have caught this sooner? If yes, implement the missing monitoring. Continuously close gaps in observability.",
     "operations", "Normal"),
    ("automation-gap-identifier",
     "After every manual fix, evaluate: could this have been automated? If yes, build the automation. The goal is to automate away every known remediation so human intervention is only needed for novel problems.",
     "workflow", "Normal"),
    ("performance-baseline-learner",
     "Continuously learn and update performance baselines: what is normal for each metric, how does normal shift over time (growing data, more users, new features), and what deviation constitutes an alert.",
     "operations", "Normal"),
    ("false-positive-reducer",
     "Track and reduce false positive alerts: which alerts fire but do not indicate real problems, which thresholds are too sensitive, and which monitoring rules need refinement. Alert fatigue kills monitoring effectiveness.",
     "operations", "Normal"),
    ("fix-durability-tracker",
     "Track whether fixes are durable: did the same issue recur after the fix? If yes, the fix addressed a symptom, not the cause. Escalate to root cause resolution.",
     "operations", "Normal"),
    ("system-improvement-ideator",
     "Continuously generate improvement ideas from operational experience: manual steps that could be automated, alerts that would be more useful if redesigned, systems that would be more resilient. Feed into a prioritized backlog.",
     "operations", "Normal"),
    ("knowledge-decay-preventer",
     "Prevent knowledge decay: keep documentation current as systems change, refresh runbooks after architecture modifications, update monitoring rules after deployments, and archive knowledge about decommissioned systems.",
     "operations", "Normal"),
    ("operational-maturity-self-assessor",
     "Periodically self-assess operational maturity: monitoring coverage, automation rate, mean time to detect (MTTD), mean time to resolve (MTTR), incident frequency trend, and documentation completeness.",
     "operations", "Normal"),

    # ─── 13. AGENT FLEET TECHNICAL HEALTH ────────────────────────────────
    ("agent-system-health-dashboard",
     "Maintain a dashboard of technical health for every agent in the fleet: are their integrations working, are their tools accessible, are their scheduled tasks running, and are their outputs meeting quality standards.",
     "agent-tools", "High"),
    ("agent-tool-connectivity-tester",
     "Periodically test every agent's connection to every tool it uses: API connectivity, authentication validity, permission adequacy, and response quality. Detect broken connections before the agent encounters them.",
     "agent-tools", "High"),
    ("agent-skill-execution-monitor",
     "Monitor skill execution across the fleet: which skills are firing, which are failing, which are slow, and which are never triggered (possibly misconfigured). Keep the fleet operationally sharp.",
     "agent-tools", "High"),
    ("agent-error-rate-tracker",
     "Track error rates per agent: which agents are encountering the most errors, what types of errors, and is the error rate trending up or down. Identify agents that need configuration attention.",
     "agent-tools", "Normal"),
    ("agent-memory-sync-verifier",
     "Verify that agent memories are syncing correctly: are memories being stored, are they retrievable, are there conflicts between agents' understanding of shared context, and is memory pruning working correctly.",
     "agent-tools", "Normal"),
    ("agent-upgrade-coordinator",
     "When Claude platform updates affect agent behavior, coordinate the upgrade across the fleet: test each agent against the update, adjust configurations as needed, deploy in staged rollout, and verify fleet health post-upgrade.",
     "agent-tools", "Normal"),

    # ─── 14. DOCUMENTATION & REPORTING ───────────────────────────────────
    ("daily-system-health-report",
     "Every morning: overnight job status, current system health (all green/yellow/red), any auto-remediated issues, open incidents, and items needing human attention. Delivered before the morning briefing.",
     "operations", "High"),
    ("weekly-techops-report",
     "Weekly: incidents this week, issues resolved, auto-remediations performed, performance improvements implemented, security scan results, backup verification status, and agent fleet health.",
     "operations", "Normal"),
    ("monthly-infrastructure-report",
     "Monthly: system reliability metrics (uptime, MTTR, incident count), performance trends, cost analysis, security posture, backup health, and strategic recommendations.",
     "operations", "Normal"),
    ("incident-log-maintainer",
     "Maintain the complete incident log: every incident with timeline, root cause, resolution, impact, and prevention measures. Searchable and linked to relevant runbooks.",
     "operations", "Normal"),
    ("system-change-log",
     "Log every change: what changed, when, why, who authorized it, and how to roll it back. Every change is a potential cause of the next incident — the change log is the first place to look.",
     "operations", "Normal"),
    ("tech-debt-register",
     "Maintain the technical debt register: known shortcuts, deferred maintenance, aging dependencies, deprecated patterns still in use, and workarounds that should be replaced with proper solutions.",
     "operations", "Normal"),
    ("sla-compliance-reporter",
     "Track and report SLA compliance: uptime commitments, response time commitments, and support resolution time commitments for both internal operations and client-facing services.",
     "operations", "Normal"),

    # ─── 15. PROACTIVE SYSTEM EVOLUTION ──────────────────────────────────
    ("technology-deprecation-tracker",
     "Track technology deprecations: libraries approaching end-of-life, API versions being sunsetted, platforms changing pricing or terms, and tools being acquired or shut down. Plan migrations well before forced deadlines.",
     "operations", "Normal"),
    ("infrastructure-modernization-advisor",
     "Continuously evaluate infrastructure for modernization opportunities: legacy components to replace, manual processes new tools can automate, and architectural patterns with better alternatives.",
     "operations", "Normal"),
    ("observability-improver",
     "Continuously improve system observability: add monitoring where gaps exist, improve log quality and structure, implement distributed tracing where helpful, and build better dashboards for faster diagnosis.",
     "operations", "Normal"),
    ("chaos-engineering-lite",
     "Conduct controlled resilience testing: deliberately introduce small failures in staging to verify monitoring detects the issue and auto-remediation handles it. Build confidence in system resilience.",
     "operations", "Normal"),
    ("capacity-forecaster",
     "Forecast future capacity needs: extrapolate current growth trends, model the impact of upcoming client onboarding, and predict when current infrastructure will need scaling. Plan capacity before emergencies.",
     "operations", "Normal"),
    ("tool-sunset-planner",
     "When a tool needs to be decommissioned, plan the sunset: data migration path, dependent system updates, replacement tool configuration, transition timeline, and rollback plan if migration encounters issues.",
     "operations", "Normal"),
    ("zero-downtime-deployment-enabler",
     "Design and maintain zero-downtime deployment capabilities: blue-green deployments, rolling updates, database migration strategies that do not lock tables, and feature flags for gradual rollouts.",
     "operations", "Normal"),
    ("reliability-engineering-advisor",
     "Advise on reliability improvements: error budgets, SLO definitions, redundancy additions, graceful degradation patterns, and circuit breaker implementations. Move from reactive firefighting to proactive reliability engineering.",
     "operations", "Normal"),
    ("system-simplification-advisor",
     "Identify opportunities to simplify the system: remove unnecessary layers, consolidate duplicate services, replace complex custom solutions with simpler alternatives, and reduce the total number of moving parts.",
     "operations", "Normal"),
    ("future-proofing-assessor",
     "Assess systems for future readiness: will current architecture handle 5x growth, are we locked into vendors that may not survive, are we building on technologies gaining or losing adoption, what changes are cheap now but expensive later.",
     "operations", "Normal"),
]


def build_record(skill_name, description, category, priority):
    return {
        "fields": {
            "Name": skill_name,
            "Description": description,
            "Target Agent": [{"id": RAFI_RECORD_ID}],
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
    parser = argparse.ArgumentParser(description="Load Rafi TechOps skills into Teable Skills Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print skills without inserting")
    args = parser.parse_args()

    print(f"\nRafi TechOps Skills Loader")
    print(f"Total skills: {len(RAFI_SKILLS)}")
    print(f"Table: {TABLE_ID}")
    print(f"Agent record: {RAFI_RECORD_ID}")
    print("=" * 60)

    if args.dry_run:
        for i, (name, desc, cat, pri) in enumerate(RAFI_SKILLS, 1):
            print(f"  [{i:3}] {name} | {cat} | {pri}")
        print(f"\n[DRY RUN] Would insert {len(RAFI_SKILLS)} skills")
        return

    from extended import TeableExtendedClient
    client = TeableExtendedClient()

    records = [build_record(name, desc, cat, pri) for name, desc, cat, pri in RAFI_SKILLS]

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
        print("All 138 Rafi TechOps skills loaded successfully.")


if __name__ == "__main__":
    main()
