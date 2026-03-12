import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from extended import TeableExtendedClient

TABLE_ID = "tblyl5mzFebauxrGf1L"
LAYLA_RECORD_ID = "rechUYRPxe2HmEg5EFc"
WORKSPACE = "layla-workspace"
BUILDER = "Zahra"
CREATION_SKILL = "Skillforge"


def build_record(skill_name, description, category, priority):
    return {"fields": {
        "Name": skill_name,
        "Description": description,
        "Target Agent": [{"id": LAYLA_RECORD_ID}],
        "Status": "Backlog",
        "Workspace": WORKSPACE,
        "Builder": BUILDER,
        "Creation Skill": CREATION_SKILL,
        "Priority": priority,
        "Category": category,
    }}


def batch(lst, size=25):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


SKILLS = [
    # 1. LEAD INTAKE & QUALIFICATION (workflow, High)
    build_record("lead-intake-processor", "When a new lead arrives from any source (cold email reply, LinkedIn DM, inbound form, referral, content engagement), capture all available information: name, company, title, source channel, initial message, timestamp, and any contextual data. Create a clean lead record immediately.", "workflow", "High"),
    build_record("lead-source-tagger", "Tag every lead by source: cold email campaign (which campaign, which sequence, which step), LinkedIn inbound, website form, referral (from whom), content-driven (which content piece), or event-driven (which event). Source tracking feeds attribution and strategy.", "workflow", "High"),
    build_record("lead-qualification-scorer", "Score every lead against the ICP: company size fit, industry fit, title/role fit, budget indicators, timing signals, and expressed pain points. Produce a qualification score (A/B/C/D) that determines follow-up priority and approach.", "workflow", "High"),
    build_record("lead-enrichment-coordinator", "Coordinate lead enrichment: pull company data, technology stack, recent news, funding status, hiring signals, and social profiles. Assemble a complete lead profile before the first sales touch. Coordinate with the Research Analyst agent for deep enrichment on high-value leads.", "workflow", "High"),
    build_record("speed-to-lead-enforcer", "Enforce speed-to-lead: respond to inbound leads within 5 minutes during business hours, within 1 hour outside business hours. Every minute of delay reduces conversion probability. Queue and prioritize by lead score.", "workflow", "Urgent"),
    build_record("lead-routing-engine", "Route leads to the appropriate workflow based on qualification: A-leads get immediate personal outreach and fast-tracked to discovery call, B-leads get nurture sequence with periodic personal touches, C-leads enter automated nurture, D-leads are politely declined or redirected.", "workflow", "High"),
    build_record("duplicate-lead-detector", "Detect duplicate leads: same person from different channels, same company from different contacts, and leads that are already in the pipeline or are existing clients. Prevent embarrassing double-outreach and data pollution.", "workflow", "Normal"),
    build_record("disqualification-handler", "Handle disqualified leads gracefully: explain why the fit isn't right (if appropriate), suggest alternative resources, leave the door open for the future, and log the disqualification reason for ICP refinement.", "workflow", "Normal"),

    # 2. COLD EMAIL RESPONSE MANAGEMENT (outreach, Urgent)
    build_record("cold-email-response-monitor", "Monitor all cold email campaign responses in real-time: detect positive replies, questions, objections, out-of-office, referrals, and opt-outs across all sending mailboxes and platforms (Instantly, Smartlead, etc.). Route each response to the appropriate handler.", "outreach", "Urgent"),
    build_record("positive-response-fast-responder", "Respond to positive cold email replies within 15 minutes: acknowledge their interest warmly, answer any question they asked, and advance toward booking a discovery call. Speed and warmth win deals.", "outreach", "Urgent"),
    build_record("question-response-handler", "Handle prospect questions from cold email replies: provide clear, helpful answers that demonstrate expertise without overwhelming, and naturally guide toward a call where deeper discussion is possible.", "outreach", "High"),
    build_record("soft-interest-nurturer", "Nurture soft interest responses ('interesting, tell me more', 'not right now but maybe later', 'send me some info'): provide the requested information, add genuine value, and keep the conversation alive without pushing. Patience converts these leads.", "outreach", "High"),
    build_record("referral-response-handler", "Handle referral responses ('I'm not the right person, but talk to...'): thank the referrer, capture the referred contact, research them, and craft outreach that leverages the referral warmly.", "outreach", "High"),
    build_record("objection-response-handler", "Handle objections in email responses with empathy and substance: 'too expensive' (reframe around value and ROI), 'bad timing' (acknowledge and schedule future follow-up), 'already have a solution' (explore satisfaction and gaps), 'not interested' (respect the no gracefully).", "outreach", "High"),
    build_record("response-tone-calibrator", "Calibrate response tone to match the prospect: match their formality level, their energy, their communication style. If they're casual, be casual. If they're direct, be direct. Mirror builds rapport.", "outreach", "Normal"),
    build_record("non-salesy-voice-enforcer", "Enforce a non-salesy tone across all sales communications: no pressure language, no artificial urgency, no manipulative tactics, no 'just following up' without value. Every message should feel like it's from a helpful human, not a sales sequence.", "outreach", "High"),

    # 3. INBOX MANAGEMENT & COMMUNICATION (outreach, High)
    build_record("sales-inbox-monitor", "Monitor all sales-related inboxes continuously: cold email replies, inbound inquiries, follow-up threads, referral introductions, and lead responses across all platforms. Nothing sits unread for more than 30 minutes during business hours.", "outreach", "High"),
    build_record("inbox-priority-ranker", "Rank inbox items by priority: hot leads first (ready to book), active conversations second (momentum to maintain), new inquiries third (need qualification), and informational responses fourth (lower urgency).", "outreach", "High"),
    build_record("email-thread-tracker", "Track all active email threads with prospects: conversation history, last touchpoint, next action needed, and days since last contact. No thread goes cold without a conscious decision.", "outreach", "High"),
    build_record("follow-up-cadence-manager", "Manage follow-up cadences for every active prospect: day 1 response, day 3 follow-up if no reply, day 7 value-add touchpoint, day 14 re-engagement, day 30 long-term nurture trigger. Cadences adjust based on lead score and engagement signals.", "outreach", "High"),
    build_record("multi-channel-message-coordinator", "Coordinate messages across channels: if a prospect was emailed, don't send a LinkedIn DM the same day. If they responded on LinkedIn, continue there. Maintain channel consistency and prevent the 'this person is everywhere' feeling.", "outreach", "Normal"),
    build_record("communication-log-maintainer", "Log every communication with every prospect in the sales database: emails sent and received, calls made, LinkedIn messages, meeting notes, and any other touchpoint. Complete communication history accessible in one place.", "outreach", "Normal"),
    build_record("email-drafting-engine", "Draft prospect emails that are warm, specific, and value-driven: reference their specific situation, address their stated needs, provide useful information, and include a clear but soft next step. Every email should earn a response by deserving one.", "outreach", "High"),
    build_record("reply-timing-optimizer", "Optimize reply timing: respond fast to hot leads, time follow-ups for optimal open rates (Tuesday-Thursday mornings), and avoid sending on Fridays or late nights unless the prospect operates on that schedule.", "outreach", "Normal"),

    # 4. DISCOVERY CALL PREPARATION (research, High)
    build_record("prospect-deep-researcher", "Before every discovery call, conduct deep research on the prospect: company overview, recent news, leadership team, technology stack, competitive landscape, funding history, growth trajectory, and any public pain points. Know more about them than they expect.", "research", "High"),
    build_record("stakeholder-profiler", "Profile every stakeholder who'll be on the call: their role, background, LinkedIn activity, communication style indicators, likely priorities, and potential objections. Prepare for the person, not just the company.", "research", "High"),
    build_record("pain-hypothesis-builder", "Based on research, build pain hypotheses before the call: 'Based on their job postings for AI roles, they're likely struggling to build internal AI capability.' Enter the call with informed hypotheses to validate, not generic questions to ask.", "research", "High"),
    build_record("call-prep-packet-assembler", "Assemble a complete call prep packet: prospect profile, stakeholder profiles, pain hypotheses, relevant case studies, talking points, questions to ask, potential objections and responses, and the ideal call outcome. Everything needed in one document.", "research", "High"),
    build_record("discovery-question-designer", "Design discovery questions tailored to each prospect: open-ended questions that uncover real pain (not leading questions), questions that demonstrate understanding of their industry, and questions that naturally lead toward the agency's solution without feeling scripted.", "research", "High"),
    build_record("relevant-case-study-matcher", "Match relevant case studies to the prospect: same industry, similar company size, comparable pain points, or analogous use cases. Have the right proof ready before it's needed.", "research", "Normal"),
    build_record("competitive-intel-pre-call", "Research competitive intelligence before calls: what solutions the prospect might already be evaluating, what competitors might have approached them, and how to position against likely alternatives.", "research", "Normal"),
    build_record("pre-call-reminder-sender", "Send pre-call reminders to prospects: 24 hours before (confirm the meeting, share a brief agenda), and 1 hour before (quick reminder with call link). Reduce no-show rates through professional preparation.", "workflow", "Normal"),
    build_record("pre-call-internal-briefing", "Brief Yasmine before every call: 5-minute summary of who she's meeting, what matters to them, what to listen for, what to ask, and what the ideal outcome is. She walks in prepared and confident.", "research", "High"),

    # 5. SALES CALL SUPPORT & EXECUTION (workflow, Normal/High)
    build_record("sales-script-builder", "Build flexible sales call scripts: not word-for-word scripts but structured conversation guides with key phases (rapport building, discovery, pain deepening, solution presentation, next steps), transition phrases, and key questions at each phase. Structure without rigidity.", "workflow", "High"),
    build_record("discovery-call-framework", "Design the discovery call framework: opening (rapport and agenda setting — 5 min), discovery (pain exploration — 20 min), solution alignment (how the agency helps — 10 min), and next steps (clear commitment — 5 min). Flexible timing but clear structure.", "workflow", "High"),
    build_record("rapport-building-guide", "Build rapport-building guides per prospect: reference something specific from their LinkedIn, company news, or shared connection. Authentic rapport, not forced small talk.", "workflow", "Normal"),
    build_record("live-call-support-notes", "Prepare live support notes for calls: objection responses ready to reference, pricing frameworks at hand, case study data points accessible, and key questions to ask if the conversation stalls. Yasmine's cheat sheet during the call.", "workflow", "Normal"),
    build_record("demo-preparation-coordinator", "When a demo is needed: prepare the demo environment, create a demo script tailored to the prospect's use case, anticipate questions, and have backup plans for technical issues.", "workflow", "Normal"),
    build_record("presentation-slide-creator", "Create presentation slides for sales calls using Gamma or other tools: prospect-specific slides showing how the agency solves their specific problems, relevant case studies, proposed approach overview, and pricing options. Clean, professional, not generic.", "workflow", "Normal"),
    build_record("proposal-document-builder", "Build proposal documents tailored to each prospect: their problem restated (proving understanding), the proposed solution, the approach and methodology, timeline, team, pricing, and terms. Professional, branded, and specific.", "workflow", "High"),
    build_record("pricing-presentation-strategist", "Strategize pricing presentation: when to present pricing (after value is established, never in the first call), how to frame it (investment, not cost), what anchoring to use, and how to present options (three tiers is optimal).", "workflow", "High"),

    # 6. OBJECTION HANDLING (workflow, High)
    build_record("objection-library-maintainer", "Maintain a comprehensive objection library: every objection ever heard, categorized by type, with multiple response strategies rated by effectiveness. The library grows with every sales conversation.", "workflow", "High"),
    build_record("price-objection-handler", "Handle price objections with finesse: reframe around ROI ('this costs $X but saves $Y'), compare against the cost of inaction, break into smaller numbers (per month, per employee), offer payment terms, and know when price truly isn't the issue.", "workflow", "Urgent"),
    build_record("timing-objection-handler", "Handle 'not the right time' objections: explore what would make it the right time, offer a smaller starting engagement, propose a paid discovery phase, or set a specific follow-up date tied to a trigger event.", "workflow", "High"),
    build_record("already-have-a-solution-handler", "Handle 'we already have something' objections: explore satisfaction level, identify gaps in their current solution, offer a free audit or comparison, and position as complementary rather than replacement if appropriate.", "workflow", "High"),
    build_record("need-to-think-about-it-handler", "Handle 'need to think about it': acknowledge the need for consideration, ask what specific concerns need thinking through, offer to address those concerns now, set a specific follow-up date, and provide materials that help the thinking process.", "workflow", "High"),
    build_record("need-buy-in-handler", "Handle 'need to get buy-in from others': offer to present to the broader team, provide materials specifically designed for the other decision-makers, ask who else is involved and what their concerns would be, and offer a joint call.", "workflow", "High"),
    build_record("trust-and-credibility-objection-handler", "Handle trust and credibility objections ('you're small', 'never heard of you', 'how do I know this works'): lead with specific results, offer references, propose a small pilot project, and demonstrate expertise through the sales conversation itself.", "workflow", "High"),
    build_record("bad-past-experience-handler", "Handle 'we tried AI consulting before and it didn't work': explore what went wrong, acknowledge the frustration, explain specifically how this would be different, offer risk-reducing terms (milestone-based billing, satisfaction guarantee), and empathize before pitching.", "workflow", "High"),
    build_record("competitor-comparison-handler", "Handle competitor comparisons ('X offers this for less'): avoid badmouthing competitors, differentiate on value and approach rather than price, highlight unique advantages, and ask what matters most to them beyond price.", "workflow", "High"),
    build_record("objection-pattern-tracker", "Track objection patterns across all sales conversations: which objections appear most frequently, which are hardest to overcome, and which correlate with lost deals. Feed patterns into training and strategy refinement.", "operations", "Normal"),

    # 7. PIPELINE MANAGEMENT (operations, High)
    build_record("pipeline-stage-manager", "Manage the sales pipeline with defined stages: New Lead → Qualified → Discovery Scheduled → Discovery Complete → Proposal Sent → Negotiation → Verbal Commit → Contract Signed → Onboarding. Move deals through stages based on clear criteria, not gut feeling.", "operations", "High"),
    build_record("pipeline-database-maintainer", "Maintain the sales pipeline database (GoHighLevel, Airtable, or CRM): every deal with current stage, next action, expected close date, deal value, probability, key contacts, and notes. The database is the single source of pipeline truth.", "operations", "High"),
    build_record("pipeline-velocity-tracker", "Track pipeline velocity: average time in each stage, conversion rate between stages, overall cycle length, and stage-specific bottlenecks. Identify where deals slow down and design interventions.", "operations", "Normal"),
    build_record("deal-probability-assessor", "Assess deal probability at each stage: based on engagement signals, stakeholder involvement, timeline alignment, budget confirmation, and competitive dynamics. Update probability as new information emerges.", "operations", "Normal"),
    build_record("pipeline-value-forecaster", "Forecast pipeline value: total pipeline × stage-weighted probability = expected revenue. Project monthly and quarterly expected closes. Alert when pipeline coverage ratio drops below 3x target.", "operations", "High"),
    build_record("stale-deal-detector", "Detect deals that have stalled: no activity in X days, stuck in a stage beyond normal duration, prospect gone quiet, or next steps unclear. Trigger re-engagement or pipeline cleanup.", "operations", "High"),
    build_record("deal-review-facilitator", "Facilitate regular deal reviews: assess each active deal's health, probability, next steps, and risks. Recommend where to invest effort and where to cut losses.", "operations", "Normal"),
    build_record("pipeline-hygiene-maintainer", "Maintain pipeline hygiene: remove dead deals, update stale information, verify contact details, and ensure every deal has a clear next action and owner. A clean pipeline enables accurate forecasting.", "operations", "Normal"),
    build_record("win-loss-tracker", "Track every deal outcome: won (why), lost (why), and stalled (why). Maintain a win/loss database that feeds continuous improvement of the sales process.", "operations", "High"),

    # 8. CALL BOOKING & SCHEDULING (workflow, Normal)
    build_record("discovery-call-booker", "Book discovery calls with qualified leads: propose times, handle timezone coordination, send calendar invitations with call links, and confirm 24 hours before. Make booking frictionless.", "workflow", "High"),
    build_record("calendar-availability-manager", "Manage Yasmine's sales call availability: define bookable windows, protect non-sales time, prevent back-to-back calls without buffer, and coordinate with Amira's calendar management.", "workflow", "Normal"),
    build_record("no-show-handler", "Handle no-shows: wait 5 minutes, send a 'looks like we missed each other' message within 15 minutes, propose reschedule within 24 hours, and track no-show patterns by source and lead quality.", "workflow", "Normal"),
    build_record("reschedule-manager", "Handle rescheduling requests gracefully: accommodate changes quickly, confirm new times promptly, and don't let rescheduling momentum kill the deal. Track how many times a prospect reschedules (3+ reschedules is a red flag).", "workflow", "Normal"),
    build_record("follow-up-call-scheduler", "Schedule follow-up calls, proposal review calls, and closing calls: propose times aligned with the agreed timeline, include a clear agenda, and send prep materials in advance.", "workflow", "Normal"),
    build_record("booking-link-manager", "Manage booking link tools (Calendly, Cal.com, etc.): configure booking pages for different call types (15-min intro, 30-min discovery, 45-min deep dive), set buffer times, and customize confirmation messages.", "workflow", "Normal"),
    build_record("meeting-confirmation-sender", "Send meeting confirmations with substance: what the call will cover, what to prepare (if anything), who from the agency will be on the call, and a link to relevant materials. Professional confirmations reduce no-shows and set expectations.", "workflow", "Normal"),

    # 9. POST-CALL PROCESSING (operations, Normal)
    build_record("call-transcript-extractor", "Extract and process call transcripts from recording tools (Fireflies, Otter, Gong, or native Zoom): clean up auto-transcription, identify speakers, and format for analysis.", "operations", "Normal"),
    build_record("call-insight-analyzer", "Analyze call transcripts for insights: what pain points were expressed, what objections surfaced, what buying signals appeared, what concerns remain, and what the prospect's emotional state seemed to be throughout the call.", "operations", "High"),
    build_record("call-action-item-extractor", "Extract action items from every call: what Yasmine committed to, what the prospect committed to, deadlines for both sides, and any conditional next steps ('if X happens, then we'll Y').", "operations", "High"),
    build_record("post-call-follow-up-drafter", "Draft post-call follow-up emails within 1 hour: thank them for the conversation, summarize key discussion points, confirm action items, attach any promised resources, and state the clear next step with a date.", "outreach", "Urgent"),
    build_record("call-notes-logger", "Log comprehensive call notes in the sales database: attendees, topics discussed, pain points confirmed, objections raised, buying signals, competitive mentions, budget discussion, timeline discussion, and next steps.", "operations", "High"),
    build_record("call-learning-extractor", "Extract learning from every call for continuous improvement: what questions worked well, what objections were handled effectively, what could have been handled better, and what new information about the market was gained.", "operations", "Normal"),
    build_record("call-coaching-note-generator", "Generate self-coaching notes from calls: moments where the conversation went well (do more of this), moments that were awkward or lost (improve this), and patterns emerging across multiple calls.", "operations", "Normal"),
    build_record("call-sentiment-analyzer", "Analyze prospect sentiment throughout the call: enthusiasm level, concern level, engagement level, and trust level. Track how sentiment shifted at different points in the conversation.", "operations", "Normal"),
    build_record("call-transcript-to-knowledge", "Extract knowledge from call transcripts that benefits other agents: market insights for the Research Analyst, content ideas for Content agents, product feedback for the Lead Developer, and competitive intelligence for the Business Strategist.", "operations", "Normal"),

    # 10. PROPOSAL & NEGOTIATION (workflow, High)
    build_record("proposal-strategy-designer", "Design the proposal strategy per deal: what to include, how to frame pricing, which case studies to feature, what terms to offer, and how to differentiate from likely alternatives. Every proposal should feel custom, not templated.", "workflow", "High"),
    build_record("proposal-content-writer", "Write proposal content: executive summary that restates their problem (proving understanding), solution overview, methodology description, timeline, team bios, relevant case studies, and pricing section. Clear, compelling, and professional.", "workflow", "High"),
    build_record("proposal-pricing-packager", "Package pricing within proposals: present 2-3 options (good, better, best), anchor with the premium option, highlight the recommended option, and make the value clear at every price point.", "workflow", "High"),
    build_record("proposal-presentation-scheduler", "Schedule proposal presentations rather than just emailing proposals: walking through a proposal live converts significantly better than a PDF sitting in an inbox. Book the review call before sending the document.", "workflow", "High"),
    build_record("proposal-follow-up-manager", "Follow up on sent proposals: day 1 (confirm receipt and offer to answer questions), day 3 (check in on review progress), day 7 (address any concerns that may have emerged), and beyond (maintain contact without pressure).", "workflow", "High"),
    build_record("negotiation-strategist", "Prepare negotiation strategies: know the walk-away point, prepare concession options (payment terms, scope adjustments, timeline flexibility), anticipate their negotiation tactics, and have a BATNA (Best Alternative to Negotiated Agreement).", "workflow", "High"),
    build_record("discount-management-protocol", "Manage discount requests: never discount without getting something in return (longer commitment, upfront payment, case study permission, referral commitment), have pre-approved discount levels, and frame discounts as exceptions earned by the prospect.", "workflow", "High"),
    build_record("contract-preparation-coordinator", "Coordinate contract preparation: work with the Finance Agent on terms, ensure scope matches what was discussed, include proper legal protections, and prepare the document for signature.", "workflow", "High"),
    build_record("e-signature-manager", "Manage the contract signing process: send for e-signature, track signing status, follow up on unsigned contracts, and confirm execution. The deal isn't closed until the contract is signed.", "workflow", "Urgent"),

    # 11. LEAD NURTURE & REACTIVATION (outreach, Normal)
    build_record("warm-nurture-sequence-designer", "Design nurture sequences for leads that aren't ready to buy: value-driven email sequences, resource sharing, industry insights, and periodic check-ins. Keep the agency top-of-mind without being annoying.", "outreach", "Normal"),
    build_record("content-based-nurture-engine", "Nurture through content: share relevant blog posts, case studies, industry reports, and thought leadership that addresses the prospect's specific pain points. Every nurture touch should provide genuine value.", "outreach", "Normal"),
    build_record("trigger-event-reactivator", "Reactivate dormant leads based on trigger events: the company raised funding (budget is available), hired for an AI role (they're thinking about AI), leadership changed (new decision-maker), or a competitor launched an AI initiative (competitive pressure).", "outreach", "High"),
    build_record("stale-lead-reactivation-campaigner", "Design and execute reactivation campaigns for leads that went cold: new angle, new offer, new case study, or simply 'checking in because we've helped companies like yours since we last spoke.' Reactivation brings dead pipeline back to life.", "outreach", "Normal"),
    build_record("seasonal-reactivation-planner", "Plan seasonal reactivation around buying cycles: Q1 budget season (money is fresh), Q3 planning season (next year is being planned), and after industry events (AI is top of mind). Time reactivation to buying psychology.", "outreach", "Normal"),
    build_record("lost-deal-recovery-strategist", "Recover lost deals: wait an appropriate period (30-90 days), approach with new information or a new offer, address the original reason for loss if possible, and avoid rehashing the old conversation.", "outreach", "Normal"),
    build_record("referral-from-non-buyers", "Extract referrals from leads who didn't buy: 'Even though the timing wasn't right for you, do you know anyone who might benefit?' Non-buyers can still be referral sources.", "outreach", "Normal"),
    build_record("long-term-relationship-nurturer", "Nurture long-term relationships with high-value leads who aren't ready: quarterly check-ins, annual strategy insights, and relationship maintenance that pays off when the timing finally aligns.", "outreach", "Normal"),

    # 12. LIST BUILDING & DATABASE MANAGEMENT (operations, Normal)
    build_record("prospect-list-builder", "Build targeted prospect lists: coordinate with the Research Analyst for ICP data, pull from data providers, enrich with contact information, verify email addresses, and deliver clean, segmented lists ready for outreach.", "operations", "High"),
    build_record("sales-database-architect", "Design and maintain the sales database structure: lead records, deal records, activity logs, communication history, and custom fields for the agency's specific sales process. The database architecture determines reporting quality.", "operations", "Normal"),
    build_record("data-entry-automator", "Automate data entry wherever possible: auto-log emails sent and received, auto-create lead records from inbound forms, auto-update deal stages from calendar events, and minimize manual database work.", "operations", "Normal"),
    build_record("database-hygiene-maintainer", "Maintain database hygiene: merge duplicates, update stale contact information, verify email deliverability, remove invalid records, and enforce data quality standards.", "operations", "Normal"),
    build_record("lead-status-lifecycle-manager", "Manage lead status through the complete lifecycle: new → contacted → engaged → qualified → opportunity → customer → advocate. Or: new → contacted → unresponsive → reactivation-eligible → recycled. Every lead has a clear status.", "operations", "Normal"),
    build_record("suppression-list-coordinator", "Coordinate with the Cold Email Specialist on suppression lists: ensure active sales conversations aren't interrupted by cold outreach, existing clients aren't prospected, and opted-out contacts are universally suppressed.", "operations", "High"),
    build_record("sales-data-enrichment-scheduler", "Schedule periodic data enrichment: re-enrich stale records, update company information that may have changed, verify job titles for contacts who may have moved roles, and refresh email validity.", "operations", "Low"),

    # 13. SALES-TO-ONBOARDING HANDOFF (workflow, High)
    build_record("deal-won-processor", "When a deal is closed-won, process the handoff: compile all prospect information, sales conversation history, promises made, expectations set, key contacts, and any special terms. Package everything the Client Success Agent needs.", "workflow", "Urgent"),
    build_record("onboarding-trigger", "Trigger the onboarding workflow: notify the Client Success Agent, PM Agent, and Lead Developer Agent. Create the client record, initiate onboarding checklist, and schedule the kickoff call.", "workflow", "Urgent"),
    build_record("client-expectations-documenter", "Document all expectations set during the sales process: what was promised, what timeline was discussed, what success looks like to the client, and any specific commitments made. Prevent the 'but your sales person said...' problem.", "workflow", "High"),
    build_record("warm-introduction-facilitator", "Facilitate warm introductions between the prospect and the delivery team: introduce the Client Success Agent, explain who they'll be working with, and make the transition from sales relationship to delivery relationship feel seamless.", "workflow", "High"),
    build_record("post-close-thank-you", "Send a personal post-close thank you: express genuine gratitude for their trust, reaffirm the commitment to deliver results, and set the tone for a great working relationship. The first impression after close sets the trajectory.", "outreach", "High"),
    build_record("early-buyer-remorse-preventer", "In the first week after close, prevent buyer's remorse: send a reassurance touchpoint with a quick win or insight, confirm the onboarding timeline, and make the new client feel confident in their decision.", "outreach", "High"),

    # 14. SALES ANALYTICS & REPORTING (operations, Normal)
    build_record("daily-sales-activity-report", "Daily report: leads engaged, emails sent, calls made, calls booked, proposals sent, and deals closed. Activity metrics that ensure consistent pipeline feeding.", "operations", "Normal"),
    build_record("weekly-pipeline-report", "Weekly pipeline report: total pipeline value by stage, deals moving forward, deals stalling, new deals added, deals closed (won and lost), and pipeline coverage ratio against target.", "operations", "High"),
    build_record("monthly-sales-performance-report", "Monthly performance report: revenue closed vs. target, conversion rates by stage, average deal size, sales cycle length, win rate, and activity-to-outcome ratios.", "operations", "High"),
    build_record("quarterly-sales-review", "Quarterly deep review: performance vs. OKRs, win/loss analysis, ICP validation from actual deals, pricing effectiveness, channel performance, and strategic sales recommendations for next quarter.", "operations", "Normal"),
    build_record("conversion-rate-tracker", "Track conversion rates at every funnel stage: lead → qualified, qualified → discovery, discovery → proposal, proposal → negotiation, negotiation → closed. Identify the leakiest stage and prioritize fixing it.", "operations", "High"),
    build_record("lead-source-roi-tracker", "Track ROI by lead source: which channels produce the most leads, the highest-quality leads, the fastest-closing leads, and the highest-value deals. Feed source ROI data to the Business Strategist for channel allocation decisions.", "operations", "Normal"),
    build_record("sales-cycle-length-analyzer", "Analyze sales cycle length: by deal size, by source, by industry, and by service type. Identify what accelerates or slows the cycle and optimize accordingly.", "operations", "Normal"),
    build_record("call-metrics-tracker", "Track call metrics: calls booked vs. completed, no-show rate, average call duration, calls to close ratio, and call quality trends. Calls are the highest-leverage sales activity — measure them carefully.", "operations", "Normal"),
    build_record("objection-frequency-reporter", "Report on objection frequency and outcomes: which objections appear most, which are successfully handled, and which correlate with lost deals. Drive objection handling improvement with data.", "operations", "Normal"),
    build_record("forecast-accuracy-tracker", "Track forecast accuracy: compare predicted close dates and probabilities against actual outcomes. Improve forecasting calibration over time.", "operations", "Normal"),

    # 15. SALES STRATEGY & OPTIMIZATION (operations, Normal)
    build_record("sales-process-optimizer", "Continuously optimize the sales process: identify friction points, test new approaches, measure impact, and refine. The sales process should improve every month.", "operations", "High"),
    build_record("ideal-sales-conversation-designer", "Design the ideal sales conversation arc: how to open, how to discover, how to present, how to handle objections, and how to close. Based on what actually works from analyzed call transcripts, not theory.", "operations", "Normal"),
    build_record("sales-messaging-tester", "Test different sales messages: value propositions, pain point framing, offer positioning, and CTA language. A/B test messaging across outreach and track which messages produce the best conversion rates.", "operations", "Normal"),
    build_record("pricing-strategy-refiner", "Refine pricing based on sales data: what price points close fastest, where price resistance is strongest, what discounts are being given most often, and whether pricing is leaving money on the table.", "operations", "Normal"),
    build_record("sales-playbook-builder", "Build and maintain the sales playbook: documented processes for every sales scenario, scripts and frameworks, objection handling guides, and competitive battle cards. The playbook makes every sales conversation more effective.", "operations", "High"),
    build_record("competitive-battle-card-creator", "Create competitive battle cards: for each known competitor, document their strengths, weaknesses, pricing, typical approach, and specific talking points for when they come up in sales conversations.", "operations", "Normal"),
    build_record("ideal-customer-story-builder", "Build the portfolio of customer stories for sales use: different stories for different niches, different pain points, and different deal sizes. The right story at the right moment in the right conversation closes deals.", "operations", "Normal"),
    build_record("sales-email-template-library", "Maintain a library of high-performing sales email templates: initial response templates, follow-up templates, proposal cover emails, objection response templates, and re-engagement templates. Tested, refined, and ready to customize.", "operations", "Normal"),
    build_record("win-rate-improvement-strategist", "Analyze win rates and design improvement strategies: what do won deals have in common, what do lost deals have in common, and what specific change would move the win rate by 5 percentage points?", "operations", "High"),

    # 16. SALES ENABLEMENT & LEARNING (operations, Low/Normal)
    build_record("call-recording-library-maintainer", "Maintain a library of call recordings organized by outcome: won calls, lost calls, great discovery calls, great objection handling, and calls where things went wrong. Reference library for continuous improvement.", "operations", "Normal"),
    build_record("sales-learning-extractor", "Extract learning from the aggregate of all sales conversations: what's changing in the market, what prospects care about most right now, what competitors are doing differently, and what objections are new.", "operations", "Normal"),
    build_record("best-practice-identifier", "Identify best practices from successful deals: what actions, timing, messaging, and approaches correlate with wins. Document and systematize what works.", "operations", "Normal"),
    build_record("sales-collateral-library-maintainer", "Maintain the sales collateral library: case studies, one-pagers, proposal templates, presentation decks, ROI calculators, and comparison sheets. Organized, current, and accessible.", "operations", "Normal"),
    build_record("prospect-insight-to-content-feeder", "Feed prospect insights to content agents: what questions do prospects ask most, what concerns do they have, what misconceptions exist? These insights become blog posts, LinkedIn content, and lead magnets.", "operations", "Normal"),
    build_record("market-intelligence-from-sales", "Extract market intelligence from sales conversations: competitive movements prospects mention, technology trends they're responding to, budget dynamics, and buying behavior shifts. Sales conversations are primary market research.", "operations", "Normal"),
    build_record("sales-knowledge-base-builder", "Build and maintain the sales knowledge base: FAQ answers, technical explanations for non-technical prospects, industry-specific talking points, and ROI justification data. Everything a salesperson needs to sound knowledgeable, in one place.", "operations", "Normal"),
]


def main():
    token = os.environ.get("TEABLE_API_TOKEN")
    if not token:
        print("ERROR: TEABLE_API_TOKEN not set")
        sys.exit(1)

    client = TeableExtendedClient(api_token=token)

    total = len(SKILLS)
    print(f"Loading {total} skills for Layla (Sales Lead Agent)...")

    inserted = 0
    for i, chunk in enumerate(batch(SKILLS)):
        result = client.create_records(TABLE_ID, chunk)
        count = len(result) if isinstance(result, list) else len(chunk)
        inserted += count
        print(f"  Batch {i + 1}: {count} records → {inserted}/{total}")
        time.sleep(0.3)

    print(f"\nDone. {inserted}/{total} skills loaded.")


if __name__ == "__main__":
    main()
