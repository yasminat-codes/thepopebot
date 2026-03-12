#!/usr/bin/env python3
"""
Load all 120 Rashid (Business Strategist Agent) skills into the Teable Skills Pipeline.

Usage:
    TEABLE_API_TOKEN="..." python3 load_rashid_skills.py
    TEABLE_API_TOKEN="..." python3 load_rashid_skills.py --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

TABLE_ID = "tblyl5mzFebauxrGf1L"
RASHID_RECORD_ID = "recV1GI8pG4PKqBkZlw"
WORKSPACE = "rashid-workspace"
BUILDER = "Zahra"
CREATION_SKILL = "Skillforge"

# All 120 Rashid skills: (name, description, category, priority)
RASHID_SKILLS = [
    # ─── 1. BUSINESS VISION & STRATEGIC FOUNDATION ───────────────────────
    ("vision-clarifier",
     "Work with Yasmine to articulate and refine the long-term business vision: where is this agency in 3 years, 5 years, 10 years? What does it look like at scale? What is the endgame — lifestyle business, acquisition target, platform company, or holding company? The vision governs every strategic decision.",
     "operations", "High"),
    ("mission-statement-crafter",
     "Craft and refine the agency's mission statement: what problem does it solve, for whom, in what unique way, and why does it matter. The mission is the filter for what to pursue and what to decline.",
     "operations", "Normal"),
    ("core-values-definer",
     "Define the agency's core values: the non-negotiable principles that guide how the business operates, hires, serves clients, and makes decisions under pressure. Values are decision-making shortcuts.",
     "operations", "Normal"),
    ("strategic-positioning-architect",
     "Define the agency's strategic positioning: how it is different from every other AI consultant, what the unique value proposition is, what the agency does that nobody else can or will, and why a prospect should choose this agency over all alternatives including doing nothing.",
     "operations", "High"),
    ("competitive-moat-builder",
     "Identify and build competitive moats: proprietary systems (the agent fleet itself), unique methodology, niche expertise, brand authority, client relationships, data advantages, and network effects. What makes this agency increasingly difficult to compete with over time?",
     "operations", "High"),
    ("business-model-architect",
     "Design and evolve the business model: revenue streams (consulting, implementation, retainers, products, training), pricing architecture, delivery model, cost structure, and margin targets. Continuously evaluate whether the model supports the vision.",
     "operations", "High"),
    ("strategic-narrative-builder",
     "Build the strategic narrative: the story the agency tells the market, investors, partners, and itself about where it is going and why it will win. A compelling narrative attracts clients, talent, and opportunities.",
     "operations", "Normal"),
    ("north-star-metric-definer",
     "Define the North Star Metric: the single metric that best captures the value the agency delivers and correlates most strongly with long-term success. All other metrics ladder up to this one.",
     "operations", "High"),

    # ─── 2. REVENUE STRATEGY & GROWTH PLANNING ───────────────────────────
    ("revenue-goal-setter",
     "Set revenue goals: annual target broken into quarterly targets, broken into monthly targets. Goals should be ambitious but achievable, with clear assumptions documented. Define the revenue composition (new clients, retainers, expansion, products).",
     "operations", "High"),
    ("revenue-model-builder",
     "Build detailed revenue models: average deal size by service type, expected close rate by channel, sales cycle length, client lifetime value, and monthly recurring revenue trajectory. Model revenue under conservative, base, and aggressive scenarios.",
     "operations", "High"),
    ("revenue-gap-analyzer",
     "Analyze gaps between revenue targets and current trajectory: how much pipeline is needed to hit the target, what close rate is required, how many leads are needed, and where the biggest gaps are. Turn revenue goals into activity goals.",
     "operations", "High"),
    ("pricing-strategist",
     "Develop and evolve pricing strategy: value-based pricing frameworks, pricing tiers, package structures, retainer pricing, and introductory pricing for new services. Price for value delivered, not hours spent.",
     "operations", "High"),
    ("revenue-diversification-planner",
     "Plan revenue diversification: reduce dependency on any single client, service, or channel. Design a portfolio of revenue streams that balances high-value consulting with recurring retainer revenue and scalable product revenue.",
     "operations", "High"),
    ("average-deal-size-increaser",
     "Strategize ways to increase average deal size: upsell strategies, bundled offerings, premium positioning, scope expansion techniques, and multi-phase engagement design. Growing deal size is the highest-leverage revenue lever.",
     "operations", "High"),
    ("client-lifetime-value-maximizer",
     "Design strategies to maximize client lifetime value: retainer conversion, expansion selling, annual renewals, referral programs, and becoming so embedded that switching costs are prohibitive.",
     "operations", "High"),
    ("revenue-per-client-optimizer",
     "Optimize revenue per client: identify undermonetized relationships, propose additional services that address unmet needs, and design pricing that captures the full value delivered.",
     "operations", "Normal"),
    ("new-revenue-stream-designer",
     "Design entirely new revenue streams: productized services (fixed scope, fixed price, scalable delivery), digital products (courses, templates, tools), licensing the agent framework, white-labeling services, and partnership revenue.",
     "operations", "High"),
    ("revenue-acceleration-strategist",
     "Identify ways to accelerate revenue: shorten the sales cycle, increase close rates, reduce time-to-first-invoice, and front-load payment terms. Speed up the cash conversion cycle.",
     "operations", "High"),

    # ─── 3. QUARTERLY PLANNING & OKR MANAGEMENT ──────────────────────────
    ("quarterly-planning-facilitator",
     "Facilitate comprehensive quarterly planning: review previous quarter performance, assess market conditions, evaluate capacity, set priorities, and build the next quarter's strategic plan. The most important planning ritual in the business.",
     "operations", "High"),
    ("okr-architect",
     "Design OKRs (Objectives and Key Results) for each quarter: 3-5 objectives that are ambitious and qualitative, each with 3-5 key results that are measurable and time-bound. OKRs translate vision into quarterly focus.",
     "operations", "High"),
    ("quarterly-theme-setter",
     "Set a quarterly theme that focuses the entire operation: Q1 Foundation Quarter (systems and process), Q2 Growth Quarter (aggressive outreach and client acquisition), Q3 Authority Quarter (content and thought leadership), Q4 Optimization Quarter (margins and efficiency).",
     "operations", "Normal"),
    ("quarterly-goal-cascader",
     "Cascade quarterly goals to every agent: translate high-level OKRs into specific agent-level goals. The Cold Email agent's targets ladder up to the revenue OKR. The Content agent's targets ladder up to the authority OKR. Every agent knows how their work connects to the quarterly plan.",
     "operations", "High"),
    ("quarterly-initiative-prioritizer",
     "Prioritize quarterly initiatives: rank by impact (revenue, strategic positioning, operational efficiency), effort (time, cost, complexity), and urgency (time-sensitive opportunity or competitive pressure). Say no to more things than you say yes to.",
     "operations", "High"),
    ("quarterly-resource-allocator",
     "Allocate resources across quarterly initiatives: agent capacity, tool budget, Yasmine's time, and any external resources. Ensure high-priority initiatives get adequate resources and low-priority work does not starve them.",
     "operations", "High"),
    ("quarterly-risk-assessor",
     "Assess risks to the quarterly plan: what could prevent achieving the OKRs, what external factors could disrupt the plan, and what contingency plans exist. Identify the top 3 risks and their mitigation strategies.",
     "operations", "Normal"),
    ("mid-quarter-review-conductor",
     "Conduct a mid-quarter review at week 6: are OKRs on track, what is ahead of plan, what is behind, what needs to change, and what decisions need to be made now to save the quarter?",
     "operations", "High"),
    ("quarterly-retrospective-facilitator",
     "Facilitate end-of-quarter retrospectives: what worked, what did not, what was learned, what should continue into next quarter, and what should be abandoned. Honest assessment without blame.",
     "operations", "Normal"),
    ("annual-plan-builder",
     "Build the annual strategic plan: 4 quarterly plans that build on each other, annual revenue targets, major milestones, strategic bets, and the narrative of how the year should unfold.",
     "operations", "High"),

    # ─── 4. GROWTH STRATEGY ───────────────────────────────────────────────
    ("growth-lever-identifier",
     "Identify all available growth levers: more leads (volume), better leads (quality), higher close rate (conversion), bigger deals (deal size), more retainers (retention), and referrals (multiplication). Rank levers by current impact potential.",
     "operations", "High"),
    ("growth-experiment-designer",
     "Design structured growth experiments: hypothesis, test design, success criteria, sample size, timeline, and decision framework. Test growth ideas with discipline rather than gut feeling.",
     "operations", "Normal"),
    ("growth-flywheel-designer",
     "Design the agency's growth flywheel: what reinforcing loops create compounding growth? Content builds authority → authority generates inbound leads → successful projects create case studies → case studies fuel content → repeat. Map every loop.",
     "operations", "High"),
    ("client-acquisition-cost-optimizer",
     "Optimize client acquisition cost (CAC): track CAC by channel, identify the most efficient acquisition paths, reduce waste in underperforming channels, and improve conversion at every funnel stage.",
     "operations", "High"),
    ("channel-strategy-architect",
     "Design the channel strategy: which acquisition channels to invest in (cold email, content/inbound, referrals, partnerships, paid ads, speaking), how much to invest in each, and what the expected return per channel is.",
     "operations", "High"),
    ("inbound-vs-outbound-balancer",
     "Balance inbound and outbound strategy: outbound (cold email) provides predictable pipeline, inbound (content, SEO) provides compounding long-term growth. Design the optimal mix and transition plan as inbound matures.",
     "operations", "High"),
    ("referral-engine-designer",
     "Design a systematic referral engine: when to ask for referrals, how to ask, what incentives to offer, how to track referral sources, and how to make it easy for happy clients to refer. Referrals are the highest-quality, lowest-cost acquisition channel.",
     "operations", "High"),
    ("partnership-strategy-designer",
     "Design strategic partnerships: complementary service providers (design agencies, dev shops, marketing agencies), technology vendors (affiliate and referral relationships), and industry partnerships (associations, accelerators). Partnerships extend reach without proportional cost.",
     "operations", "Normal"),
    ("market-expansion-planner",
     "Plan market expansion: new niches to enter, new geographies to serve, new service offerings to launch, and new buyer personas to target. Sequence expansion to maximize learning while minimizing risk.",
     "operations", "Normal"),
    ("viral-coefficient-strategist",
     "Design for virality: content that gets shared, tools that get recommended, frameworks that get cited, and client results that get talked about. Build the agency's organic reach multiplier.",
     "operations", "Normal"),

    # ─── 5. SERVICE OFFERING STRATEGY ────────────────────────────────────
    ("service-portfolio-architect",
     "Design the service portfolio: what services to offer, at what price points, targeting which audiences, and how services relate to each other (entry-level to premium, one-time to ongoing). Design a portfolio that serves the full client lifecycle.",
     "operations", "High"),
    ("service-productizer",
     "Productize consulting services: define fixed scope, fixed price, fixed timeline offerings that can be sold and delivered repeatedly. AI Readiness Assessment — $5,000 — 2 weeks is more sellable than we will figure out the scope. Productized services scale.",
     "operations", "High"),
    ("service-ladder-designer",
     "Design the service ladder: the progression from low-commitment entry (free audit, paid assessment) to mid-commitment (implementation project) to high-commitment (ongoing retainer). Each rung builds trust for the next.",
     "operations", "High"),
    ("new-service-validator",
     "Before launching a new service, validate demand: test messaging in outreach, gauge interest in content, run small pilots, and confirm willingness to pay. Do not build services nobody wants.",
     "operations", "Normal"),
    ("service-retirement-advisor",
     "Identify services to retire: low-margin, low-demand, or misaligned with strategic direction. Sunsetting underperforming services frees capacity for high-value offerings.",
     "operations", "Normal"),
    ("service-differentiation-strategist",
     "Ensure every service is differentiated: what makes the agency's AI implementation different from a competitor's? Proprietary process, unique technology (the agent fleet), deeper niche expertise, or superior delivery model.",
     "operations", "High"),
    ("service-packaging-optimizer",
     "Optimize how services are packaged and presented: naming that communicates value, descriptions that resonate with buyer psychology, and packaging that makes the purchase decision easy.",
     "operations", "Normal"),
    ("service-delivery-margin-analyzer",
     "Analyze the margin of each service: revenue minus direct delivery costs. Identify high-margin services to promote and low-margin services to reprice, restructure, or retire.",
     "operations", "High"),

    # ─── 6. COMPETITIVE STRATEGY ──────────────────────────────────────────
    ("competitive-strategy-definer",
     "Define the competitive strategy: are we competing on price (never), on quality (always), on speed (sometimes), on specialization (usually), or on methodology (ideally)? Make the competitive stance explicit and consistent.",
     "research", "High"),
    ("competitive-positioning-matrix",
     "Build and maintain a competitive positioning matrix: how the agency stacks up against every identified competitor on key dimensions (price, quality, speed, specialization, methodology, reputation). Identify where the agency wins and where it does not compete.",
     "research", "High"),
    ("competitive-response-planner",
     "When a competitor makes a move (new service, price change, enters a niche, wins a key client), plan the response: ignore, match, counter, or leapfrog. Not every competitive move deserves a response.",
     "research", "Normal"),
    ("blue-ocean-strategist",
     "Identify blue ocean opportunities: market spaces where competition is irrelevant because the offering is fundamentally different. Where can the agency create new demand rather than fight for existing demand?",
     "research", "High"),
    ("competitive-intelligence-consumer",
     "Consume and act on competitive intelligence from the Research Analyst agent: translate raw intelligence into strategic decisions about positioning, pricing, targeting, and service design.",
     "research", "High"),
    ("first-mover-vs-fast-follower-advisor",
     "For emerging opportunities, advise on timing: when to move first (before competitors establish position) and when to follow fast (let others validate the market, then enter with a better offering).",
     "research", "Normal"),

    # ─── 7. CLIENT STRATEGY ───────────────────────────────────────────────
    ("ideal-client-portfolio-designer",
     "Design the ideal client portfolio: mix of client sizes, industries, engagement types, and revenue per client. Avoid over-concentration in any dimension. Design a portfolio that is resilient and profitable.",
     "operations", "High"),
    ("client-tier-strategist",
     "Define client tiers: platinum (high revenue, high strategic value), gold (solid revenue, good fit), silver (smaller revenue, growth potential), and bronze (entry-level, proving ground). Differentiate service levels and attention by tier.",
     "operations", "Normal"),
    ("client-selection-criteria-definer",
     "Define criteria for accepting or declining clients: minimum budget, strategic fit, niche alignment, team chemistry, realistic expectations, and growth potential. Not every client is a good client. Saying no to wrong-fit clients protects the business.",
     "operations", "High"),
    ("client-concentration-risk-manager",
     "Monitor and manage client concentration risk: no single client should represent more than 25% of revenue. When concentration gets dangerous, actively diversify through targeted acquisition.",
     "operations", "High"),
    ("client-expansion-strategist",
     "Design strategies for expanding within existing clients: land-and-expand playbooks, identifying additional departments or use cases, timing expansion conversations, and packaging expansion offerings.",
     "operations", "High"),
    ("client-retention-strategist",
     "Design retention strategies: what makes clients stay (results, relationship, dependency, switching costs), what makes them leave (poor results, poor communication, better alternatives), and how to maximize the stay factors while minimizing the leave factors.",
     "operations", "High"),
    ("win-back-strategist",
     "Design strategies for winning back lost clients: when to re-approach, what to offer, how to address the reason they left, and how to demonstrate that things have changed.",
     "operations", "Normal"),

    # ─── 8. FINANCIAL STRATEGY ────────────────────────────────────────────
    ("financial-goal-architect",
     "Set comprehensive financial goals: revenue targets, profit margin targets, cash reserve targets, owner compensation targets, and reinvestment targets. Financial goals must be specific, time-bound, and balanced.",
     "operations", "High"),
    ("profit-margin-strategist",
     "Design strategies to improve profit margins: pricing optimization, delivery efficiency, tool cost reduction, scope discipline, and shifting the service mix toward higher-margin offerings.",
     "operations", "High"),
    ("cash-flow-strategist",
     "Design cash flow strategy: payment terms that favor the agency (deposits, milestone billing, prepayment discounts), expense timing optimization, and cash reserve management. Cash flow kills more businesses than profitability.",
     "operations", "High"),
    ("investment-prioritizer",
     "Prioritize business investments: when to invest in tools, when to invest in content, when to invest in capabilities, and when to conserve cash. Every dollar spent should generate more than a dollar in return.",
     "operations", "High"),
    ("unit-economics-optimizer",
     "Optimize unit economics: cost to acquire a client, cost to deliver a project, revenue per client per year, and lifetime value to CAC ratio. When unit economics are strong, growth is profitable. When they are weak, growth accelerates losses.",
     "operations", "High"),
    ("financial-scenario-planner",
     "Model financial scenarios: what happens if revenue grows 50%, what if the biggest client churns, what if a recession cuts demand by 30%, and what if a major opportunity requires upfront investment. Prepare for multiple futures.",
     "operations", "Normal"),
    ("funding-strategy-advisor",
     "If external funding is ever considered: advise on options (bootstrapping, revenue-based financing, angel investment, venture capital), trade-offs (control, dilution, pressure, timeline), and preparation required.",
     "operations", "Normal"),
    ("owner-compensation-optimizer",
     "Optimize Yasmine's compensation: salary vs. distribution structure, tax-efficient compensation strategies, reinvestment vs. extraction balance, and compensation benchmarking against comparable founders.",
     "operations", "Normal"),

    # ─── 9. OPERATIONAL STRATEGY ─────────────────────────────────────────
    ("operational-efficiency-strategist",
     "Design operational efficiency strategies: automate everything automatable, systematize everything repeatable, and reserve human judgment for what truly requires it. The agency should deliver 10x the value with 1/10th the overhead of traditional competitors.",
     "operations", "High"),
    ("scalability-architect",
     "Design the agency for scale: what processes work at current size but will break at 3x, what tools need upgrading, what bottlenecks exist, and what the scaling sequence should be (people, then tools, then process — or the reverse).",
     "operations", "High"),
    ("leverage-maximizer",
     "Identify and maximize leverage: systems leverage (build once, use forever), technology leverage (AI agents multiply output), knowledge leverage (expertise compounds), and brand leverage (reputation precedes sales). Build a business that produces disproportionate output per unit of input.",
     "operations", "High"),
    ("build-vs-buy-vs-partner-advisor",
     "For every capability need, advise on build vs. buy vs. partner: build when it is a core competency, buy when it is a commodity, and partner when someone else does it better. Allocate effort to maximum competitive advantage.",
     "operations", "Normal"),
    ("team-scaling-strategist",
     "When the time comes to scale beyond AI agents: what roles to hire first, what to keep automated, what the organizational structure should look like, and how to maintain culture and quality through growth.",
     "operations", "Normal"),
    ("delivery-model-optimizer",
     "Optimize the delivery model: how to deliver more value in less time, how to standardize without losing customization, and how to make delivery so efficient that margins expand as revenue grows.",
     "operations", "High"),
    ("capacity-planning-strategist",
     "Strategic capacity planning: how much client work can the operation handle, when does capacity need to expand, and what is the cost and timeline to add capacity. Never turn away good business because of avoidable capacity constraints.",
     "operations", "High"),

    # ─── 10. MARKET POSITIONING & BRAND STRATEGY ─────────────────────────
    ("brand-positioning-strategist",
     "Define and evolve brand positioning: what the agency is known for, what it wants to be known for, and how to bridge the gap. Positioning should be narrow enough to be memorable and broad enough to grow into.",
     "operations", "High"),
    ("thought-leadership-strategist",
     "Design the thought leadership strategy: what ideas Yasmine should own in the market, what contrarian positions to take, what frameworks to publish, and how to build recognition as the definitive voice in AI consulting.",
     "operations", "High"),
    ("authority-building-roadmap",
     "Build a roadmap for authority: speaking engagements, publications, media appearances, awards, certifications, and strategic associations. Map the milestones from unknown to the first person people think of for AI consulting.",
     "operations", "High"),
    ("personal-brand-vs-company-brand-strategist",
     "Navigate the personal brand vs. company brand dynamic: when to lead with Yasmine's name, when to lead with the agency name, and how to build both simultaneously so neither is a single point of failure.",
     "operations", "Normal"),
    ("reputation-capital-builder",
     "Build reputation capital: the accumulated trust, credibility, and goodwill that makes everything else easier. Client results build reputation, content amplifies it, and consistency compounds it.",
     "operations", "High"),
    ("category-creation-advisor",
     "Evaluate whether the agency should create a new category rather than compete in an existing one: AI Implementation Partner vs. AI Consultant vs. something entirely new that the agency defines and owns.",
     "operations", "Normal"),
    ("premium-positioning-strategist",
     "Position the agency at the premium end of the market: justify higher prices through demonstrated expertise, proprietary methodology, superior delivery, and selective client acceptance. Premium positioning repels price shoppers and attracts value buyers.",
     "operations", "High"),

    # ─── 11. STRATEGIC PARTNERSHIPS & ECOSYSTEM ──────────────────────────
    ("partnership-opportunity-evaluator",
     "Evaluate partnership opportunities: strategic fit, revenue potential, effort required, brand alignment, and exit terms. Not every partnership is worth pursuing.",
     "operations", "Normal"),
    ("technology-partner-strategist",
     "Design technology partnerships: become a certified partner or preferred implementer for AI platforms, automation tools, or SaaS companies. Technology partnerships generate referrals and credibility.",
     "operations", "Normal"),
    ("referral-partnership-architect",
     "Architect referral partnerships with complementary service providers: design agencies, marketing agencies, development shops, and business consultants who serve the same clients but do not compete.",
     "operations", "Normal"),
    ("ecosystem-position-designer",
     "Design the agency's position within the broader AI ecosystem: vendor relationships, platform partnerships, community involvement, and industry association membership. An agency embedded in the ecosystem attracts opportunities the isolated agency never sees.",
     "operations", "Normal"),
    ("strategic-alliance-designer",
     "Design strategic alliances for specific opportunities: joint ventures for large projects, co-marketing agreements, knowledge-sharing partnerships, and capability-pooling arrangements.",
     "operations", "Normal"),
    ("event-and-speaking-strategist",
     "Strategize event and speaking presence: which events to attend, which to speak at, which to sponsor, and which to skip. Events are expensive — invest only where the strategic return justifies the cost.",
     "operations", "Normal"),

    # ─── 12. INNOVATION & FUTURE PLANNING ────────────────────────────────
    ("innovation-portfolio-manager",
     "Manage an innovation portfolio: allocate effort across core (improving current services — 70%), adjacent (expanding into related markets — 20%), and transformational (entirely new offerings — 10%). Balance exploitation with exploration.",
     "operations", "Normal"),
    ("future-service-designer",
     "Design services the market will need in 12-24 months: based on technology trajectory, market trends, and emerging client needs. Build capabilities ahead of demand so the agency is ready when the market arrives.",
     "operations", "High"),
    ("disruption-preparedness-planner",
     "Plan for potential disruptions: what if AI tools become so easy that consulting demand drops, what if a platform bundles consulting into their offering, what if the economy contracts severely. Prepare pivot options for each scenario.",
     "operations", "Normal"),
    ("technology-as-moat-strategist",
     "Strategize how to use the agency's own technology (the agent fleet, proprietary systems) as a competitive moat: can the fleet be productized, can the methodology be licensed, can the systems be white-labeled.",
     "operations", "High"),
    ("exit-strategy-designer",
     "Even if an exit is not planned, design exit options: what would make the agency acquirable, what is the current estimated valuation, what increases value, and what timeline would exit planning require. Understanding exit value drives better building decisions.",
     "operations", "Normal"),
    ("legacy-and-impact-planner",
     "Beyond financial goals, plan for legacy and impact: what mark does Yasmine want to leave on the AI consulting industry, what transformation does she want to enable, and how does the business serve purposes larger than revenue.",
     "operations", "Normal"),

    # ─── 13. DECISION FRAMEWORKS & STRATEGIC THINKING ────────────────────
    ("decision-framework-library",
     "Build and maintain a library of decision frameworks for recurring strategic decisions: Eisenhower matrix for prioritization, RICE scoring for feature/initiative prioritization, Porter's Five Forces for market analysis, and custom frameworks for agency-specific decisions.",
     "operations", "Normal"),
    ("strategic-decision-packager",
     "When a major decision is needed, package it for Yasmine: clear framing of the decision, options with pros/cons, data supporting each option, recommended path with reasoning, and reversibility assessment. Make decisions easy to make well.",
     "operations", "High"),
    ("opportunity-cost-calculator",
     "For every opportunity, calculate the opportunity cost: what would the agency NOT be doing if it pursues this? Every yes is a no to something else. Make the tradeoff explicit.",
     "operations", "High"),
    ("second-order-thinking-engine",
     "Apply second-order thinking to strategic decisions: if we do X, the first-order effect is Y, but the second-order effect is Z, and the third-order effect is... Think beyond the obvious to the consequences of consequences.",
     "operations", "High"),
    ("assumption-challenger",
     "Actively challenge assumptions in strategic plans: We assume clients will pay $10K for this — based on what? We assume the market is growing — what if it is not? Every strategy is built on assumptions. Test them before betting on them.",
     "operations", "High"),
    ("pre-mortem-conductor",
     "Before executing a major strategy, conduct a pre-mortem: Imagine this failed completely. Why did it fail? Identify failure modes in advance and design prevention measures.",
     "operations", "Normal"),
    ("sunk-cost-advisor",
     "Advise on sunk cost situations: when a strategy is not working, advise on whether to persist (it needs more time) or pivot (it is fundamentally flawed). The hardest strategic discipline is knowing when to quit.",
     "operations", "Normal"),
    ("optionality-creator",
     "Design strategic optionality: decisions that keep future options open rather than committing irreversibly. When uncertain, prefer moves that create options over moves that close them.",
     "operations", "Normal"),

    # ─── 14. PERFORMANCE MEASUREMENT & ACCOUNTABILITY ────────────────────
    ("okr-progress-tracker",
     "Track OKR progress weekly: percentage complete on each key result, confidence level (on track, at risk, off track), and what needs to change to hit the quarterly targets.",
     "operations", "High"),
    ("leading-indicator-monitor",
     "Monitor leading indicators: metrics that predict future results before they materialize. Pipeline value predicts future revenue. Content output predicts future authority. Outreach volume predicts future pipeline. Leading indicators enable proactive adjustment.",
     "operations", "High"),
    ("lagging-indicator-analyst",
     "Analyze lagging indicators: metrics that confirm past performance. Revenue, profit, client count, and satisfaction scores. Lagging indicators verify whether strategy worked.",
     "operations", "Normal"),
    ("kpi-dashboard-designer",
     "Design the strategic KPI dashboard: the 8-12 metrics that tell the complete story of business health. Organize by category (revenue, growth, efficiency, quality, brand) and set thresholds for green/yellow/red.",
     "operations", "High"),
    ("strategic-accountability-enforcer",
     "Enforce accountability on strategic commitments: when quarterly initiatives fall behind, diagnose why, propose recovery, and escalate if needed. Strategy without accountability is just aspiration.",
     "operations", "High"),
    ("goal-recalibrator",
     "When circumstances change materially (market shift, capacity change, unexpected opportunity), recalibrate goals: adjust targets to reflect new reality while maintaining ambition. Rigid goals in fluid circumstances lead to either demoralization or delusion.",
     "operations", "Normal"),

    # ─── 15. STRATEGIC COMMUNICATION ─────────────────────────────────────
    ("strategy-communicator",
     "Communicate strategy clearly to all agents: why this direction was chosen, what each agent's role is in executing it, what success looks like, and how progress will be measured. Strategy that is not understood cannot be executed.",
     "operations", "High"),
    ("quarterly-kickoff-briefing",
     "Produce the quarterly kickoff briefing: the strategic context, the OKRs, the key initiatives, the resource allocation, and the success criteria. Set the tone and direction for the quarter.",
     "operations", "High"),
    ("strategic-narrative-updater",
     "Update the strategic narrative as the business evolves: incorporate new wins, adjust positioning based on market feedback, and refine the story as it becomes more proven.",
     "operations", "Normal"),
    ("investor-and-partner-pitch-builder",
     "If needed, build investment or partnership pitches: market opportunity, business model, traction, competitive positioning, team, and financial projections. Even bootstrapped businesses benefit from pitch-grade clarity.",
     "operations", "Normal"),
    ("board-of-advisors-briefing",
     "If/when an advisory board exists, prepare advisory briefings: business update, strategic questions, specific areas where advice is sought, and relevant data. Maximize the value of advisor time.",
     "operations", "Normal"),

    # ─── 16. REPORTING & STRATEGIC INTELLIGENCE ──────────────────────────
    ("weekly-strategic-pulse",
     "Weekly strategic pulse: are we on track for the quarterly OKRs, what is the biggest risk this week, what is the biggest opportunity this week, and what decision does Yasmine need to make? One page, every Monday.",
     "operations", "High"),
    ("monthly-business-review",
     "Monthly business review: revenue vs. target, pipeline health, client portfolio status, operational efficiency, content authority growth, and strategic initiative progress. The monthly health check.",
     "operations", "High"),
    ("quarterly-business-review",
     "Comprehensive quarterly business review: full OKR assessment, financial performance, client analysis, competitive position, operational improvements, and strategic plan for next quarter.",
     "operations", "High"),
    ("annual-state-of-the-business",
     "Annual state-of-the-business report: year in review, goal attainment, key learnings, market evolution, competitive landscape, and strategic direction for the coming year.",
     "operations", "Normal"),
    ("strategic-opportunity-brief",
     "When a significant strategic opportunity emerges (new market, potential partner, acquisition target, pivot option), produce a brief: what it is, why it matters, what it requires, what the risks are, and the recommended action.",
     "operations", "High"),
    ("strategic-threat-alert",
     "When a strategic threat emerges (competitive move, market shift, regulatory change, technology disruption), alert immediately with assessment and recommended response options.",
     "operations", "High"),
    ("business-health-scorecard",
     "Maintain a comprehensive business health scorecard: financial health, operational health, client health, brand health, team health, and strategic health. Updated monthly, trending over time.",
     "operations", "High"),
    ("strategic-backlog-maintainer",
     "Maintain a strategic backlog: ideas, opportunities, and initiatives that are not active now but should be considered in future quarters. The backlog ensures good ideas are not lost just because the timing is not right.",
     "operations", "Normal"),
]


def build_record(skill_name, description, category, priority):
    return {
        "fields": {
            "Name": skill_name,
            "Description": description,
            "Target Agent": [{"id": RASHID_RECORD_ID}],
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
    parser = argparse.ArgumentParser(description="Load Rashid Business Strategist skills into Teable Skills Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print skills without inserting")
    args = parser.parse_args()

    print(f"\nRashid Business Strategist Skills Loader")
    print(f"Total skills: {len(RASHID_SKILLS)}")
    print(f"Table: {TABLE_ID}")
    print(f"Agent record: {RASHID_RECORD_ID}")
    print("=" * 60)

    if args.dry_run:
        for i, (name, desc, cat, pri) in enumerate(RASHID_SKILLS, 1):
            print(f"  [{i:3}] {name} | {cat} | {pri}")
        print(f"\n[DRY RUN] Would insert {len(RASHID_SKILLS)} skills")
        return

    from extended import TeableExtendedClient
    client = TeableExtendedClient()

    records = [build_record(name, desc, cat, pri) for name, desc, cat, pri in RASHID_SKILLS]

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
        print("All 120 Rashid Business Strategist skills loaded successfully.")


if __name__ == "__main__":
    main()
