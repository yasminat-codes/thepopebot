#!/usr/bin/env python3
"""
Load all 128 Tariq (Research Analyst Agent) skills into the Teable Skills Pipeline.

Usage:
    TEABLE_API_TOKEN="..." python3 load_tariq_skills.py
    TEABLE_API_TOKEN="..." python3 load_tariq_skills.py --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

TABLE_ID = "tblyl5mzFebauxrGf1L"
TARIQ_RECORD_ID = "recfXQutvw12toTwUWe"
WORKSPACE = "tariq-workspace"
BUILDER = "Zahra"
CREATION_SKILL = "Skillforge"

# All 128 Tariq skills: (name, description, category, priority)
TARIQ_SKILLS = [
    # ─── 1. NICHE RESEARCH & SCOUTING ────────────────────────────────────
    ("niche-discovery-researcher",
     "Research and identify potential niches for AI consulting outreach. Scan industries for AI adoption signals, pain point density, budget capacity, decision-maker accessibility, and competitive white space. Produce ranked niche opportunity scorecards.",
     "research", "High"),
    ("niche-deep-diver",
     "Conduct comprehensive deep dives into selected niches: industry structure, value chain, market size, growth trajectory, key players, regulatory landscape, technology adoption curve, business models, buying cycles, and decision-making structures. Produce 10-20 page niche intelligence briefs.",
     "research", "High"),
    ("niche-pain-point-researcher",
     "For each niche, research specific pain points that AI consulting can address: operational inefficiencies, manual processes, data silos, customer experience gaps, compliance burdens, and scaling bottlenecks. Map each pain point to a potential service offering with estimated value.",
     "research", "High"),
    ("niche-technology-landscape-mapper",
     "Map the technology landscape within each niche: dominant tools and platforms, common tech stacks, legacy systems creating friction, emerging technologies gaining traction, and where AI/automation fits into the existing tech ecosystem.",
     "research", "Normal"),
    ("niche-competitive-density-analyzer",
     "Analyze competitive density per niche: how many AI consultants are targeting it, saturation of outreach, what competitors offer, and where differentiation opportunities exist. Produce competitive density heat maps.",
     "research", "High"),
    ("niche-buying-cycle-researcher",
     "Research the buying cycle for each niche: how long from first contact to closed deal, who's involved in the decision, what triggers purchasing decisions, what budget cycles look like, and when optimal outreach windows are.",
     "research", "High"),
    ("niche-entry-strategist",
     "For each new niche being considered, research the optimal entry strategy: which sub-segment to target first, what language resonates, which proof points matter most, and what the fastest path to first client is. Produce niche entry playbooks.",
     "research", "Normal"),
    ("adjacent-niche-spotter",
     "Identify niches adjacent to current successful ones: if AI consulting works well in healthcare, what adjacent niches (healthtech, biotech, pharma, medical devices) share similar characteristics? Map adjacency networks for efficient expansion.",
     "research", "Normal"),
    ("niche-risk-assessor",
     "Assess risks for each niche: regulatory risk, technology risk (niche could adopt AI internally), economic risk (industry downturn), and competitive risk (big players entering). Produce risk-adjusted niche rankings.",
     "research", "Normal"),
    ("global-niche-opportunity-scanner",
     "Scan for niche opportunities beyond domestic markets: which industries in which geographies are underserved by AI consulting, where English-language outreach is viable, and where timezone overlap enables service delivery.",
     "research", "Normal"),

    # ─── 2. IDEAL CUSTOMER PROFILE (ICP) RESEARCH ────────────────────────
    ("icp-firmographic-researcher",
     "Research firmographic attributes for ideal customers: optimal company size ranges (revenue, headcount), geographic concentrations, founding age, funding stages, growth rates, and organizational structures that indicate readiness for AI consulting.",
     "research", "High"),
    ("icp-technographic-researcher",
     "Research technographic profiles of ideal customers: what CRM they use, what marketing stack, what internal tools, what cloud infrastructure, and what level of technical sophistication indicates AI readiness vs. AI overwhelm.",
     "research", "Normal"),
    ("icp-behavioral-signal-researcher",
     "Research behavioral signals that indicate a company is ready to buy AI consulting: recent job postings for AI/automation roles, attendance at AI events, content engagement on AI topics, recent technology purchases, and vendor review site activity.",
     "research", "High"),
    ("icp-trigger-event-researcher",
     "Research trigger events that create buying windows: new funding rounds, leadership changes (new CTO, new COO), digital transformation announcements, competitor pressure, regulatory changes, and rapid growth phases.",
     "research", "High"),
    ("icp-negative-filter-researcher",
     "Research characteristics that disqualify prospects: companies too small to afford consulting, companies with internal AI teams, industries with regulatory barriers to AI adoption, and companies in financial distress.",
     "research", "Normal"),
    ("icp-validation-researcher",
     "After campaigns run, research whether the ICP is accurate: compare won deals against ICP criteria, identify characteristics of deals that closed vs. did not, and refine the ICP based on actual conversion data.",
     "research", "Normal"),
    ("lookalike-company-researcher",
     "Given a successful client, research lookalike companies: same industry, similar size, similar tech stack, similar growth stage, and similar pain points. Build target lists of companies that match winning client profiles.",
     "research", "High"),

    # ─── 3. BUYER PERSONA RESEARCH ───────────────────────────────────────
    ("persona-role-researcher",
     "Research buyer personas by role: what a VP of Operations at a mid-market company does day-to-day, what KPIs they are measured on, what frustrates them, what would make them a hero internally, and how they prefer to be contacted.",
     "research", "High"),
    ("persona-psychology-researcher",
     "Research the psychology of target personas: what motivates their decisions (fear of falling behind, desire for promotion, pressure from board), what objections are instinctive vs. considered, and what communication styles resonate.",
     "research", "High"),
    ("persona-content-consumption-researcher",
     "Research where target personas consume content: which LinkedIn influencers they follow, which podcasts they listen to, which newsletters they read, which events they attend, and which communities they participate in.",
     "research", "Normal"),
    ("persona-language-researcher",
     "Research the language target personas use: industry jargon, how they describe their problems, what words they use for AI/automation vs. what marketers use, and the vocabulary gap between how consultants pitch and how buyers think.",
     "research", "High"),
    ("persona-objection-researcher",
     "Deep-research common objections by persona: what their actual budget reality is, what AI they likely tried and why it failed, what data they actually have. Arm the outreach team with objection-specific intelligence.",
     "research", "High"),
    ("persona-day-in-the-life-builder",
     "Research and build day-in-the-life profiles for each persona: morning routine, first thing they check, meetings they attend, tools they use, decisions they make, pressures they face, and when they have time to read emails or LinkedIn.",
     "research", "Normal"),
    ("decision-committee-mapper",
     "Research the typical decision-making committee for AI consulting purchases: who initiates, who evaluates, who influences, who approves budget, and who can kill the deal. Map the buying committee structure per company size and industry.",
     "research", "High"),

    # ─── 4. LEAD & COMPANY RESEARCH ──────────────────────────────────────
    ("company-deep-researcher",
     "Conduct deep research on specific target companies: business model, revenue streams, recent news, leadership team, org structure, technology investments, strategic priorities, competitive position, and public financials. Produce company intelligence dossiers.",
     "research", "High"),
    ("company-news-monitor",
     "Monitor news about target companies and active prospects: press releases, funding announcements, leadership changes, product launches, partnerships, earnings reports, and industry mentions. Flag time-sensitive outreach opportunities.",
     "research", "High"),
    ("company-technology-detective",
     "Research a company's technology stack through public signals: job postings (what tools they hire for), website analysis, vendor case studies, technology review sites, and conference presentations.",
     "research", "Normal"),
    ("company-growth-signal-researcher",
     "Research growth signals at target companies: hiring velocity, new office openings, revenue growth indicators, product expansion, market expansion, and investor activity. Growing companies are buying companies.",
     "research", "High"),
    ("company-pain-signal-researcher",
     "Research pain signals at target companies: job postings that indicate unfilled capability gaps, negative employee reviews about operational inefficiency, public complaints about their technology, and industry headwinds affecting their business.",
     "research", "High"),
    ("executive-profile-researcher",
     "Research individual executives: career history, educational background, public speaking topics, LinkedIn activity, published content, professional interests, mutual connections, and communication style indicators. Build relationship-ready executive profiles.",
     "research", "High"),
    ("company-financial-health-researcher",
     "Research the financial health of target companies: revenue trends, profitability, funding runway, recent investment rounds, debt levels, and spending patterns. Ensure outreach targets companies that can actually afford to buy.",
     "research", "Normal"),
    ("company-culture-researcher",
     "Research company culture indicators: Glassdoor reviews, leadership communications, public values statements, hiring practices, and work environment signals. Culture affects buying decisions and project success.",
     "research", "Normal"),
    ("competitive-threat-researcher",
     "Research the competitive landscape of target companies: who their competitors are, how they are using technology, what their strengths and weaknesses are, and how AI consulting could give the client a competitive edge.",
     "research", "Normal"),
    ("account-mapping-researcher",
     "For high-priority target accounts, build complete account maps: organizational structure, key stakeholders, reporting relationships, decision-making process, existing vendor relationships, and potential champions and blockers.",
     "research", "High"),

    # ─── 5. MARKET & INDUSTRY RESEARCH ───────────────────────────────────
    ("market-size-estimator",
     "Estimate Total Addressable Market, Serviceable Available Market, and Serviceable Obtainable Market for each niche and service offering. Use multiple estimation methods (top-down, bottom-up, comparable) and present ranges with assumptions.",
     "research", "Normal"),
    ("market-trend-researcher",
     "Research macro market trends affecting AI consulting: overall AI adoption rates, enterprise AI spending forecasts, SMB technology investment trends, consulting industry growth, and automation market trajectory. Produce quarterly trend reports.",
     "research", "High"),
    ("industry-report-synthesizer",
     "Find, analyze, and synthesize industry reports from Gartner, McKinsey, Deloitte, CB Insights, Statista, and other research firms. Extract data points and insights relevant to the agency's positioning and outreach. Convert dense reports into actionable summaries.",
     "research", "High"),
    ("regulatory-landscape-researcher",
     "Research regulatory developments affecting AI consulting and client industries: AI regulation (EU AI Act, US state laws), data privacy updates (GDPR enforcement, new state privacy laws), and industry-specific compliance changes.",
     "research", "Normal"),
    ("technology-adoption-curve-researcher",
     "Research where specific technologies sit on the adoption curve within each target industry: early innovator phase, early majority, late majority, or laggard. Position outreach messaging based on where the target audience sits on the curve.",
     "research", "Normal"),
    ("market-disruption-scanner",
     "Scan for market disruptions that create consulting opportunities: new AI model releases that change what is possible, platform shifts, industry consolidation, economic shifts that force efficiency, and regulatory changes that mandate new capabilities.",
     "research", "High"),
    ("venture-capital-trend-researcher",
     "Research VC investment trends in AI and adjacent spaces: what is getting funded, what sectors are hot, which emerging companies are potential future clients, and what investment patterns signal about market direction.",
     "research", "Normal"),
    ("industry-event-researcher",
     "Research industry events, conferences, and webinars relevant to target niches: speaker lineups, attendee profiles, topics covered, sponsorship opportunities, and networking potential. Produce an event calendar with strategic value assessments.",
     "research", "Normal"),
    ("economic-indicator-monitor",
     "Monitor economic indicators that affect AI consulting demand: business confidence indexes, technology spending forecasts, employment trends, GDP growth, and inflation impact on consulting budgets. Translate macro economics into micro strategy.",
     "research", "Normal"),
    ("geographical-market-researcher",
     "Research geographic market variations: which regions have highest AI consulting demand, where buyers are concentrated, what regional factors affect pricing, and where remote delivery is accepted vs. where local presence matters.",
     "research", "Normal"),

    # ─── 6. COMPETITIVE INTELLIGENCE ─────────────────────────────────────
    ("competitor-landscape-mapper",
     "Map the complete competitive landscape: direct competitors (other AI consultants), indirect competitors (in-house AI teams, DIY platforms, general consulting firms), and substitute competitors (status quo). Maintain a living competitive map.",
     "research", "High"),
    ("competitor-deep-profiler",
     "Build deep profiles on key competitors: services offered, pricing where discoverable, positioning and messaging, target market, team size, technology stack, client base, strengths, and weaknesses. Produce competitor intelligence files.",
     "research", "High"),
    ("competitor-content-analyzer",
     "Analyze competitor content across all channels: topics they publish on, messaging they use, thought leadership positions, case studies they share, and engagement they receive. Identify messaging gaps and differentiation opportunities.",
     "research", "Normal"),
    ("competitor-client-researcher",
     "Research competitor client lists: who they have worked with (from case studies, testimonials, LinkedIn connections), what industries they serve, what size companies, and what results they claim. Identify prospects competitors are ignoring.",
     "research", "Normal"),
    ("competitor-pricing-researcher",
     "Research competitor pricing where possible: published rates, job posting salary data, proposals found in public forums, and pricing signals from case studies. Build pricing intelligence.",
     "research", "Normal"),
    ("competitor-hiring-analyzer",
     "Analyze competitor hiring patterns: what roles they are hiring indicates their strategic direction, team structure, and growth trajectory. Rapid hiring in a new niche signals market validation.",
     "research", "Normal"),
    ("win-loss-researcher",
     "When deals are won or lost, research the competitive dynamics: who else was the prospect talking to, what influenced their decision, what the competitor offered that the agency did not (or vice versa), and what the deciding factor was.",
     "research", "High"),
    ("competitive-positioning-advisor",
     "Based on all competitive intelligence, advise on positioning: where to compete head-on, where to differentiate, where to avoid, and how to frame the agency's unique value against each competitor type.",
     "research", "High"),

    # ─── 7. EMPLOYMENT & TALENT TREND RESEARCH ───────────────────────────
    ("ai-job-market-researcher",
     "Research the AI job market: what roles are in demand, what skills command premium salaries, what companies are hiring for AI, and what the talent shortage looks like. This data informs both client pain points and agency positioning.",
     "research", "Normal"),
    ("hiring-trend-analyzer",
     "Analyze hiring trends in target industries: are companies trying to build internal AI teams (potential competitor) or looking for external help (potential client)? Track the build-vs-buy trend by industry and company size.",
     "research", "High"),
    ("salary-and-rate-benchmarker",
     "Research salary and consulting rate benchmarks: what AI consultants charge per hour, per project, and per retainer. What in-house AI engineers cost vs. consulting costs. Use to validate and defend agency pricing.",
     "research", "Normal"),
    ("skill-demand-forecaster",
     "Forecast which AI and automation skills will be in highest demand: which programming languages, frameworks, platforms, and specializations are growing fastest. Inform the agency's own skill development and service offering evolution.",
     "research", "Normal"),
    ("remote-work-trend-researcher",
     "Research remote work trends as they affect AI consulting: client acceptance of remote delivery, geographic arbitrage opportunities, talent access implications, and how remote-first positioning affects competitiveness.",
     "research", "Normal"),
    ("outsourcing-trend-researcher",
     "Research outsourcing trends in AI development and consulting: what companies are outsourcing, what they keep in-house, what drives the outsourcing decision, and how the agency can position at the premium end of the outsourcing spectrum.",
     "research", "Normal"),
    ("emerging-role-researcher",
     "Research emerging roles in the AI space: AI Operations Manager, Prompt Engineer, AI Ethics Officer, Agent Orchestrator, and similar new titles. New roles signal new needs that consulting can fill before the roles are hired for.",
     "research", "Normal"),

    # ─── 8. TOOL & TECHNOLOGY RESEARCH ───────────────────────────────────
    ("ai-tool-researcher",
     "Research AI tools and platforms: new releases, feature updates, pricing changes, integration capabilities, and real-world performance. Maintain a current AI tool database covering LLMs, automation platforms, vector databases, deployment tools, and agent frameworks.",
     "research", "High"),
    ("tool-comparison-researcher",
     "Conduct head-to-head tool comparisons on demand: feature matrices, pricing comparisons, performance benchmarks, user reviews, integration compatibility, and vendor reliability. Produce comparison reports that drive buy decisions.",
     "research", "High"),
    ("emerging-technology-researcher",
     "Research emerging technologies before they hit mainstream: new AI architectures, novel automation approaches, cutting-edge platforms in beta, and academic research nearing commercialization. Identify technologies the agency should explore early.",
     "research", "Normal"),
    ("open-source-project-researcher",
     "Research open-source AI and automation projects: trending GitHub repos, new frameworks, community-driven tools, and open-source alternatives to commercial products. Feed findings to the Lead Developer agent for evaluation and potential adoption.",
     "research", "Normal"),
    ("api-capability-researcher",
     "Research API capabilities of relevant platforms: what is possible via API that is not obvious from the UI, undocumented capabilities, rate limits, pricing tiers, and new API features that create automation opportunities.",
     "research", "Normal"),
    ("platform-roadmap-researcher",
     "Research the public roadmaps of platforms the agency depends on or recommends: upcoming features, deprecation timelines, pricing direction, and strategic shifts. Anticipate changes rather than react to them.",
     "research", "Normal"),
    ("integration-possibility-researcher",
     "Research integration possibilities between specific tools: native integrations, middleware options, API-based custom integrations, and community-built connectors. Enable the S-Agent and Lead Developer to make informed integration decisions.",
     "research", "Normal"),
    ("tool-failure-and-outage-researcher",
     "Research the reliability history of tools under consideration: documented outages, customer complaints, support quality, and vendor financial stability. Avoid recommending tools with poor reliability track records.",
     "research", "Normal"),

    # ─── 9. CONTENT & THOUGHT LEADERSHIP RESEARCH ────────────────────────
    ("trending-topic-researcher",
     "Research trending topics in AI, automation, consulting, and adjacent spaces: what is being discussed on LinkedIn, Twitter, Reddit, Hacker News, and industry publications. Identify topics with momentum before they peak.",
     "research", "High"),
    ("thought-leadership-gap-researcher",
     "Research what thought leadership exists and does not exist in the AI consulting space: what topics are saturated, what topics are underexplored, and where an authoritative voice is missing. Feed gap analysis to the LinkedIn Content Agent.",
     "research", "High"),
    ("viral-content-pattern-researcher",
     "Research patterns of viral content in the B2B AI space: what formats go viral (data, controversy, storytelling, frameworks), what emotional triggers drive sharing, and what structural elements correlate with outsized reach.",
     "research", "Normal"),
    ("audience-question-researcher",
     "Research the actual questions the target audience is asking: Quora, Reddit, LinkedIn comments, industry forums, support communities, and Stack Overflow. Real questions from real people are the highest-value content seeds.",
     "research", "High"),
    ("case-study-data-researcher",
     "Research data and statistics to strengthen case studies and content: industry benchmarks, ROI data, productivity improvements from AI adoption, and comparable results from similar implementations. Back every claim with research.",
     "research", "Normal"),
    ("original-data-opportunity-researcher",
     "Identify opportunities to create original research and data: surveys the agency could run, data it uniquely has access to, analyses it could perform, and benchmarks it could establish. Original data is the ultimate authority builder.",
     "research", "Normal"),
    ("seo-keyword-researcher",
     "Research keywords for content optimization: search volume, keyword difficulty, long-tail opportunities, question-format keywords, and keyword clusters. Ensure content is discoverable beyond just LinkedIn.",
     "research", "Normal"),
    ("content-format-effectiveness-researcher",
     "Research which content formats are most effective for B2B AI consulting audiences: long-form vs. short-form, carousel vs. text post, newsletter vs. blog, video vs. written. Track format preferences by persona and platform.",
     "research", "Normal"),

    # ─── 10. PRICING & BUSINESS MODEL RESEARCH ───────────────────────────
    ("consulting-pricing-model-researcher",
     "Research consulting pricing models: hourly rates, project-based pricing, value-based pricing, retainer structures, performance-based pricing, and equity-for-services models. Analyze which models are most profitable and most accepted by target markets.",
     "research", "High"),
    ("value-based-pricing-data-researcher",
     "Research the value that AI consulting delivers: documented ROI percentages, cost savings, revenue increases, efficiency gains, and productivity improvements. This data supports value-based pricing conversations.",
     "research", "High"),
    ("productized-service-researcher",
     "Research productized service models in consulting: what is being packaged as fixed-scope fixed-price offerings, how it is positioned, how it is delivered, and what margins it achieves. Inform the agency's own productization strategy.",
     "research", "Normal"),
    ("subscription-model-researcher",
     "Research subscription and retainer models for consulting: common structures, pricing ranges, what is included, client retention rates, and revenue predictability benefits. Inform retainer offer design.",
     "research", "Normal"),
    ("pricing-elasticity-researcher",
     "Research pricing elasticity in AI consulting: at what price points do win rates drop significantly, what the market ceiling is for different service types, and where the floor of credibility sits (too cheap signals low quality).",
     "research", "Normal"),
    ("ancillary-revenue-researcher",
     "Research ancillary revenue opportunities: affiliate partnerships with tool vendors, referral fees, training and certification programs, digital products, SaaS add-ons to consulting, and white-label opportunities.",
     "research", "Normal"),

    # ─── 11. CLIENT INDUSTRY DEEP DIVES ──────────────────────────────────
    ("client-industry-expert",
     "When a new client is onboarded, conduct a rapid deep dive into their specific industry: market dynamics, competitive landscape, regulatory environment, technology landscape, industry jargon, and key metrics. Produce a brief that makes the delivery team sound like industry insiders.",
     "research", "High"),
    ("client-competitor-researcher",
     "Research the client's competitors: who they are, how they are using technology, what their strengths and weaknesses are, and how AI consulting could give the client a competitive edge. Arm client conversations with competitive context.",
     "research", "High"),
    ("client-customer-researcher",
     "Research the client's customers: who they are, what they value, how they behave, and what their expectations are. Understanding the client's customer enables better AI solution design.",
     "research", "Normal"),
    ("client-vendor-landscape-researcher",
     "Research the vendor landscape for a client's needs: what tools exist for their specific use case, how they compare, what others in their industry use, and what the total cost of ownership looks like. Support tool recommendation decisions.",
     "research", "Normal"),
    ("client-benchmark-researcher",
     "Research industry benchmarks relevant to client projects: what good performance looks like for their KPIs, what comparable companies achieve, and what realistic targets are for AI-driven improvement. Ground client expectations in data.",
     "research", "Normal"),
    ("client-regulatory-researcher",
     "Research regulations affecting client projects: data privacy requirements for their industry, AI-specific regulations, compliance frameworks they are subject to, and how proposed solutions need to account for regulatory constraints.",
     "research", "Normal"),

    # ─── 12. RESEARCH SYNTHESIS & ANALYSIS ───────────────────────────────
    ("cross-source-synthesizer",
     "Synthesize information across multiple sources into coherent insights: reconcile conflicting data, weight sources by credibility, identify consensus and outliers, and produce synthesis reports that present the clear picture, not just a data dump.",
     "research", "High"),
    ("pattern-recognition-engine",
     "Identify patterns across research findings: correlations between seemingly unrelated data points, recurring themes across industries, emerging patterns that have not been named yet, and historical parallels that inform predictions.",
     "research", "High"),
    ("signal-vs-noise-separator",
     "Separate signal from noise in research: distinguish meaningful trends from random fluctuation, credible sources from hype, and actionable insights from interesting-but-useless information. Only signal reaches the other agents.",
     "research", "High"),
    ("contrarian-insight-finder",
     "Actively look for contrarian evidence: data that challenges the agency's assumptions, research that suggests a popular strategy is wrong, and signals that the market is moving in an unexpected direction. Prevent confirmation bias.",
     "research", "Normal"),
    ("implication-chain-builder",
     "Build implication chains from research findings: if X is true, then Y follows, which means Z for strategy. Connect dots forward from data to strategic action. Do not just report facts — report what facts mean.",
     "research", "High"),
    ("confidence-level-assessor",
     "Assess and communicate confidence levels for research findings: high confidence (multiple credible sources, strong data), medium confidence (some supporting evidence, some gaps), and low confidence (early signals, limited data).",
     "research", "Normal"),
    ("research-bias-checker",
     "Check for biases in research: survivorship bias (only studying winners), recency bias (overweighting recent data), confirmation bias (finding what you expected), and selection bias (non-representative samples).",
     "research", "Normal"),
    ("trend-lifecycle-classifier",
     "Classify where trends sit in their lifecycle: nascent (early signal, high uncertainty), growing (accelerating adoption), mature (established, well-documented), and declining (past peak). Different lifecycle stages require different strategic responses.",
     "research", "Normal"),

    # ─── 13. RESEARCH DELIVERABLES & FORMATS ─────────────────────────────
    ("niche-intelligence-brief",
     "Produce comprehensive niche intelligence briefs: 10-20 page documents covering market overview, pain points, ICP characteristics, competitive landscape, entry strategy, and opportunity assessment. The go-to document for niche decisions.",
     "operations", "High"),
    ("company-dossier",
     "Produce company dossiers for high-priority targets: company overview, key stakeholders, technology landscape, pain signals, growth signals, recent news, competitive position, and recommended outreach approach.",
     "operations", "High"),
    ("market-trend-report",
     "Produce periodic market trend reports: quarterly analysis of AI consulting market dynamics, technology shifts, competitive movements, and pricing trends. The strategic intelligence that informs quarterly planning.",
     "operations", "Normal"),
    ("competitive-intelligence-brief",
     "Produce competitive intelligence briefs: competitor profiles, competitive positioning analysis, win/loss analysis, and recommended competitive strategies. Updated quarterly or when significant competitive changes occur.",
     "operations", "Normal"),
    ("executive-summary-generator",
     "Generate executive summaries for any research document: distill the key findings, implications, and recommended actions into a 1-page summary that busy decision-makers can absorb in 3 minutes.",
     "operations", "Normal"),
    ("data-visualization-creator",
     "Create data visualizations for research findings: charts, graphs, maps, comparison matrices, timeline visualizations, and infographics that make data immediately comprehensible. A good chart replaces a page of text.",
     "operations", "Normal"),
    ("research-presentation-builder",
     "Build presentation decks from research findings: for internal strategy sessions, client presentations, and team briefings. Structure research for storytelling, not just data dumping.",
     "operations", "Normal"),
    ("one-pager-creator",
     "Create one-page research summaries: dense, scannable, visual, and actionable. The format for research that needs to be consumed quickly and referenced often.",
     "operations", "Normal"),
    ("comparison-matrix-builder",
     "Build structured comparison matrices: tools vs. tools, niches vs. niches, competitors vs. competitors, and strategies vs. strategies. Side-by-side comparisons enable faster decisions.",
     "operations", "Normal"),
    ("research-database-maintainer",
     "Maintain a searchable research database: all research documents, source materials, data sets, and analysis outputs. Tagged by topic, date, confidence level, and consuming agent. Prevent re-researching what has already been researched.",
     "operations", "Normal"),

    # ─── 14. RESEARCH OPERATIONS ─────────────────────────────────────────
    ("research-request-intake",
     "Receive and triage research requests from all agents: understand what is needed, clarify scope, assess urgency, estimate effort, and commit to a delivery timeline. Manage the research queue.",
     "operations", "High"),
    ("source-credibility-evaluator",
     "Evaluate the credibility of information sources: primary vs. secondary sources, methodology quality, author expertise, publication reputation, recency, and potential conflicts of interest. Build and maintain a source credibility database.",
     "operations", "Normal"),
    ("research-methodology-selector",
     "For each research task, select the appropriate methodology: desk research, data analysis, survey design, expert interviews, competitive mystery shopping, or multi-source triangulation. Match method to question.",
     "operations", "Normal"),
    ("automated-monitoring-configurator",
     "Configure automated monitoring for recurring research needs: Google Alerts, social listening tools, news monitoring, job posting trackers, and regulatory update feeds. Automate the information gathering layer so more time is spent on analysis.",
     "operations", "High"),
    ("research-freshness-manager",
     "Track the freshness of all research outputs: flag research aging beyond its useful life, schedule refresh cycles for ongoing intelligence needs, and proactively update high-value research before it becomes stale.",
     "operations", "Normal"),
    ("research-pipeline-manager",
     "Manage the research pipeline: incoming requests, in-progress research, completed outputs, and scheduled recurring research. Ensure capacity is allocated to the highest-value research and nothing falls through.",
     "operations", "Normal"),
    ("source-network-builder",
     "Build and maintain a network of information sources: industry publications, data providers, government data portals, academic databases, community forums, and expert connections. A strong source network produces faster, deeper research.",
     "operations", "Normal"),
    ("research-quality-auditor",
     "Audit the quality of research outputs: accuracy verification, source attribution, analytical rigor, actionability of recommendations, and format quality. Ensure every deliverable meets the agency's intelligence standards.",
     "operations", "Normal"),

    # ─── 15. STRATEGIC INTELLIGENCE ──────────────────────────────────────
    ("strategic-opportunity-researcher",
     "Research strategic opportunities: new service lines the agency could offer, new markets to enter, partnership opportunities, acquisition targets (tools or businesses), and revenue diversification paths. Feed long-term strategy with researched options.",
     "research", "High"),
    ("threat-landscape-researcher",
     "Research strategic threats: market shifts that could reduce demand, technology changes that could commoditize services, regulatory changes that could restrict operations, and competitor moves that could erode market position.",
     "research", "High"),
    ("scenario-research-provider",
     "When the agency faces a major decision, research the key variables for scenario planning: what data supports each option, what precedents exist, what comparable companies did in similar situations, and what the risk factors are for each path.",
     "research", "Normal"),
    ("innovation-radar-operator",
     "Operate an innovation radar: continuously scan for innovations across AI, automation, business operations, and consulting delivery that could give the agency a meaningful advantage. Classify by proximity (adopt now, explore soon, watch for later).",
     "research", "Normal"),
    ("client-success-factor-researcher",
     "Research what makes AI consulting engagements succeed or fail: common success factors, common failure modes, client characteristics that predict success, and project characteristics that predict difficulty. Inform client selection and delivery approach.",
     "research", "High"),
    ("agency-growth-benchmark-researcher",
     "Research growth benchmarks for comparable agencies: revenue growth rates, client acquisition rates, team scaling patterns, and milestone timelines. Provide realistic reference points for the agency's own growth trajectory.",
     "research", "Normal"),
    ("future-of-work-researcher",
     "Research the future of work as it relates to AI consulting: how AI is changing business operations, what jobs will be created vs. eliminated, how consulting itself will evolve, and what the agency needs to do to stay relevant in 2, 5, and 10 years.",
     "research", "Normal"),

    # ─── 16. REPORTING CADENCE & INTELLIGENCE DISTRIBUTION ───────────────
    ("daily-intelligence-digest",
     "Produce a daily intelligence digest: key news items, market movements, competitor activity, and anything time-sensitive that Amira should include in the morning briefing. Brief, scannable, and prioritized.",
     "operations", "High"),
    ("weekly-research-roundup",
     "Weekly compilation of all research completed: summaries of each deliverable, key findings across all research streams, and flagged items that need strategic attention.",
     "operations", "Normal"),
    ("monthly-market-intelligence-report",
     "Monthly comprehensive market intelligence: trend analysis, competitive landscape update, niche performance data, and strategic research recommendations for the coming month.",
     "operations", "Normal"),
    ("quarterly-strategic-intelligence-brief",
     "Quarterly strategic intelligence: deep-dive analysis on the most important market shifts, competitive movements, and opportunity/threat developments. The research that informs quarterly planning.",
     "operations", "Normal"),
    ("ad-hoc-research-rapid-response",
     "For urgent research needs (prospect call in 2 hours, competitive situation developing, client asking about a specific topic), execute rapid research and deliver actionable findings within the required timeframe. Speed over depth when urgency demands it.",
     "operations", "High"),
    ("intelligence-distribution-router",
     "Route research outputs to the right agents: niche research to the Cold Email Specialist, content research to the LinkedIn Content Agent, tool research to the Lead Developer, pricing research to the Finance Agent, and client research to the Client Success Agent.",
     "operations", "High"),
    ("research-impact-tracker",
     "Track the impact of research on business outcomes: did niche research lead to successful campaigns, did competitive intelligence lead to won deals, did tool research lead to better client solutions. Measure the ROI of research efforts.",
     "operations", "Normal"),
    ("annual-intelligence-review",
     "Annual review of the agency's intelligence capabilities: research quality trends, most impactful research outputs, source network health, methodology effectiveness, and intelligence capability improvements for the coming year.",
     "operations", "Normal"),
]


def build_record(skill_name, description, category, priority):
    return {
        "fields": {
            "Name": skill_name,
            "Description": description,
            "Target Agent": [{"id": TARIQ_RECORD_ID}],
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
    parser = argparse.ArgumentParser(description="Load Tariq Research Analyst skills into Teable Skills Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print skills without inserting")
    args = parser.parse_args()

    print(f"\nTariq Research Analyst Skills Loader")
    print(f"Total skills: {len(TARIQ_SKILLS)}")
    print(f"Table: {TABLE_ID}")
    print(f"Agent record: {TARIQ_RECORD_ID}")
    print("=" * 60)

    if args.dry_run:
        for i, (name, desc, cat, pri) in enumerate(TARIQ_SKILLS, 1):
            print(f"  [{i:3}] {name} | {cat} | {pri}")
        print(f"\n[DRY RUN] Would insert {len(TARIQ_SKILLS)} skills")
        return

    from extended import TeableExtendedClient
    client = TeableExtendedClient()

    records = [build_record(name, desc, cat, pri) for name, desc, cat, pri in TARIQ_SKILLS]

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
        print("All 128 Tariq Research Analyst skills loaded successfully.")


if __name__ == "__main__":
    main()
