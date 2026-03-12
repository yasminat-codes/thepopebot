import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from extended import TeableExtendedClient

TABLE_ID = "tblyl5mzFebauxrGf1L"
SALMA_RECORD_ID = "recXbSpSwCMIzqCmRLL"
WORKSPACE = "salma-workspace"
BUILDER = "Zahra"
CREATION_SKILL = "Skillforge"


def build_record(skill_name, description, category, priority):
    return {"fields": {
        "Name": skill_name,
        "Description": description,
        "Target Agent": [{"id": SALMA_RECORD_ID}],
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
    # 1. MULTI-CHANNEL OUTREACH STRATEGY (outreach, High)
    build_record("multi-channel-strategy-architect", "Design the overarching multi-channel outreach strategy: which channels serve which purpose (LinkedIn for warm professional outreach, X for thought-leader engagement, Facebook for community-based outreach, Instagram for brand visibility), how channels coordinate, and how the strategy adapts by niche, persona, and funnel stage.", "outreach", "High"),
    build_record("channel-role-definer", "Define the role of each outreach channel: LinkedIn is the primary professional outreach channel (connection requests, DMs, comment engagement), X is for visibility and conversation insertion, Facebook is for group-based community engagement, and others serve supporting roles. Every channel has a job.", "outreach", "High"),
    build_record("channel-mix-optimizer", "Optimize the channel mix per ICP segment: some personas live on LinkedIn, some are active on X, some engage in Facebook groups, some respond to Instagram DMs. Match channel investment to where the target audience actually spends time.", "outreach", "High"),
    build_record("multi-channel-sequence-designer", "Design multi-channel outreach sequences: Day 1 LinkedIn profile view → Day 2 LinkedIn connection request → Day 4 connection accepted → Day 5 first DM → Day 8 engage with their post → Day 12 second DM with value → Day 15 email follow-up. Orchestrate touches across channels in a natural progression.", "outreach", "High"),
    build_record("touch-frequency-calibrator", "Calibrate touch frequency: enough touches to stay visible without becoming annoying. Factor in channel-specific norms (daily X engagement is normal, daily LinkedIn DMs are aggressive), prospect engagement signals, and the overall volume of touches per week across all channels.", "outreach", "High"),
    build_record("channel-saturation-monitor", "Monitor channel saturation: are too many prospects being contacted on LinkedIn this month (risk of account restriction), is X engagement volume sustainable, and is any single channel being overworked relative to its capacity?", "operations", "Normal"),
    build_record("outreach-calendar-builder", "Build outreach calendars: daily and weekly outreach activity plans per channel, balanced across the week to maintain consistency without burnout. Monday heavy on LinkedIn, Tuesday focus on X engagement, Wednesday community engagement, etc.", "outreach", "Normal"),
    build_record("seasonal-outreach-adjuster", "Adjust outreach strategy by season: lighter outreach during holiday periods, increased volume during Q1 budget season and Q3 planning season, event-driven outreach around industry conferences, and sensitivity to cultural calendars.", "outreach", "Normal"),
    build_record("outreach-budget-allocator", "Allocate outreach budget across channels: LinkedIn premium/Sales Nav, HeyReach or similar automation costs, social media scheduling tools, community memberships, and any paid outreach tools. Maximize ROI per dollar.", "operations", "Normal"),
    build_record("a-b-test-framework-designer", "Design A/B testing frameworks for outreach: test connection request messages, DM sequences, engagement approaches, timing, and channel combinations. Measure with statistical rigor and implement winners.", "outreach", "Normal"),

    # 2. LINKEDIN OUTREACH (outreach, High)
    build_record("linkedin-outreach-strategist", "Design the LinkedIn outreach strategy: daily connection request volume, DM cadence, engagement-first approach, content-then-outreach coordination, and Sales Navigator usage optimization.", "outreach", "High"),
    build_record("linkedin-connection-request-writer", "Write personalized connection request messages: under 300 characters, reference something specific (their content, company news, mutual connection, shared interest), no pitch, just a genuine reason to connect. The connection request is a handshake, not a sales letter.", "outreach", "High"),
    build_record("linkedin-dm-sequence-writer", "Write LinkedIn DM sequences: first message (value-driven, no pitch), follow-up messages (share relevant insights, ask thoughtful questions), and conversion message (soft transition to a call when interest is demonstrated). 3-5 message sequences that feel like natural conversation.", "outreach", "High"),
    build_record("linkedin-voice-note-strategist", "Strategize LinkedIn voice note outreach: when voice notes outperform text DMs (higher open rate, more personal), what to say in a voice note (conversational, brief, specific), and how to integrate voice notes into the DM sequence.", "outreach", "Normal"),
    build_record("linkedin-video-message-strategist", "Strategize LinkedIn video messages for high-value prospects: personalized 30-60 second videos that reference something specific about the prospect, demonstrate real expertise, and stand out from text-based outreach.", "outreach", "Normal"),
    build_record("linkedin-engagement-first-strategy", "Execute engagement-first outreach: before sending a DM, engage with the prospect's content (meaningful comments, not 'great post!'), view their profile, and build familiarity. When the DM arrives, they already recognize the name.", "outreach", "High"),
    build_record("linkedin-comment-outreach", "Use strategic commenting as outreach: leave insightful comments on target prospects' posts that demonstrate expertise and attract profile visits. Comments are public outreach that benefits from social proof.", "outreach", "High"),
    build_record("linkedin-sales-navigator-operator", "Operate LinkedIn Sales Navigator: build saved searches by ICP criteria, use lead lists for organized outreach, leverage intent signals (job changes, company news, content engagement), and track prospect activity for timing optimization.", "outreach", "High"),
    build_record("linkedin-inmail-writer", "Write LinkedIn InMails for prospects not yet connected: subject lines that get opened, messages that demonstrate value without pitching, and CTAs that are low-friction. InMails are premium touches — make every one count.", "outreach", "Normal"),
    build_record("linkedin-group-outreach-strategist", "Strategize outreach through LinkedIn groups: identify groups where target prospects are active, contribute value consistently, build visibility, and transition group interactions to DM conversations naturally.", "outreach", "Normal"),
    build_record("linkedin-event-outreach-leverager", "Leverage LinkedIn events for outreach: identify events prospects are attending or hosting, engage around the event context, and use shared event participation as a natural connection point.", "outreach", "Normal"),
    build_record("linkedin-automation-manager", "Manage LinkedIn automation tools (HeyReach, Expandi, Dripify, or similar): configure sequences, manage daily limits, rotate accounts if using multiple profiles, and ensure automation feels human. Monitor for platform compliance to avoid account restrictions.", "operations", "High"),
    build_record("linkedin-account-health-protector", "Protect LinkedIn account health: stay within daily connection and messaging limits, avoid spam-like patterns, maintain a high connection acceptance rate, and monitor for warnings or restrictions.", "operations", "High"),
    build_record("linkedin-profile-view-strategist", "Use strategic profile views as micro-touchpoints: view target prospects' profiles to trigger the 'someone viewed your profile' notification, creating familiarity before the connection request arrives.", "outreach", "Normal"),

    # 3. X (TWITTER) OUTREACH (outreach, Normal)
    build_record("x-outreach-strategist", "Design the X outreach strategy: identify target prospects active on X, build engagement relationships through replies and quote tweets, transition to DMs when rapport is established, and coordinate with the Content Specialist's X presence.", "outreach", "Normal"),
    build_record("x-reply-outreach", "Execute outreach through strategic replies: reply to prospects' tweets with genuine insights, additional data, or helpful resources. Consistent valuable replies build recognition that makes DMs welcome.", "outreach", "Normal"),
    build_record("x-dm-writer", "Write X DMs for warm outreach: short, casual, specific to something they posted, and with a clear but soft reason for reaching out. X DMs are informal — match the platform's conversational tone.", "outreach", "Normal"),
    build_record("x-list-builder-for-outreach", "Build private X lists of target prospects: organize by niche, engagement level, and outreach stage. Lists enable focused engagement without algorithm dependency.", "outreach", "Normal"),
    build_record("x-engagement-warming", "Warm prospects through X engagement before DM outreach: like their tweets, retweet valuable posts with commentary, reply to threads, and build a visible engagement history. By the time the DM arrives, they know who's messaging.", "outreach", "Normal"),
    build_record("x-spaces-outreach-leverager", "Leverage X Spaces for outreach: join Spaces where target prospects host or participate, ask thoughtful questions, contribute insights, and use Spaces participation as a conversation starter for follow-up DMs.", "outreach", "Low"),
    build_record("x-thread-engagement-outreach", "Use X threads as an outreach vehicle: create threads that address pain points of target prospects, tag relevant people when appropriate (not spammy), and use thread engagement as a relationship opener.", "outreach", "Normal"),

    # 4. FACEBOOK OUTREACH (outreach, Normal)
    build_record("facebook-outreach-strategist", "Design the Facebook outreach strategy: identify Facebook groups where target prospects are active, build credibility through value contribution, and transition group interactions to messenger conversations.", "outreach", "Normal"),
    build_record("facebook-group-engagement-outreach", "Execute outreach through Facebook group participation: answer questions, share insights, provide value consistently, and become a recognized expert in groups where prospects gather.", "outreach", "Normal"),
    build_record("facebook-group-identifier", "Identify and join high-value Facebook groups: groups where target ICPs congregate, groups with active discussion (not dead groups), and groups where the admin culture allows genuine expertise sharing.", "outreach", "Normal"),
    build_record("facebook-messenger-outreach-writer", "Write Facebook Messenger outreach messages: casual, personal, reference shared group membership or content interaction, and offer genuine help rather than pitching.", "outreach", "Normal"),
    build_record("facebook-comment-outreach", "Use strategic comments on prospect posts and in group discussions: demonstrate expertise, add value to conversations, and build visibility that leads to inbound interest.", "outreach", "Normal"),
    build_record("facebook-event-outreach", "Leverage Facebook events for outreach: attend or host events relevant to the target audience, engage with attendees, and use event participation as a relationship-building touchpoint.", "outreach", "Low"),

    # 5. INSTAGRAM & OTHER PLATFORMS (outreach, Normal/Low)
    build_record("instagram-outreach-strategist", "Design Instagram outreach strategy (if applicable): engage with prospect content through story reactions, meaningful comments, and DMs that reference specific content. Instagram is personal — outreach must feel personal.", "outreach", "Normal"),
    build_record("instagram-dm-writer", "Write Instagram DMs for outreach: brief, specific, reference their content, and feel like a genuine human interaction. Instagram DMs that feel like sales pitches get blocked immediately.", "outreach", "Normal"),
    build_record("instagram-story-engagement-outreach", "Use Instagram story engagement as micro-outreach: react to prospect stories, respond to polls and questions, and use story interactions to build familiarity before direct messaging.", "outreach", "Low"),
    build_record("whatsapp-outreach-strategist", "Design WhatsApp outreach strategy (where culturally appropriate): typically for warm leads or referrals where WhatsApp is the preferred communication channel. Always respectful of the personal nature of the platform.", "outreach", "Low"),
    build_record("community-platform-outreach", "Execute outreach on community platforms: Slack communities, Discord servers, Circle communities, and niche forums where target prospects participate. Build reputation through value contribution, then connect directly.", "outreach", "Normal"),
    build_record("quora-outreach-strategist", "Use Quora for outreach: answer questions related to AI consulting, automation, and business transformation. Detailed, expert answers drive profile visits and inbound interest from prospects actively seeking solutions.", "outreach", "Low"),
    build_record("emerging-platform-scout", "Scout emerging platforms for outreach opportunity: new social networks, new community platforms, and new communication channels where early adoption provides outreach advantage.", "research", "Low"),

    # 6. EVENT-BASED & TRIGGER OUTREACH (outreach, High)
    build_record("conference-outreach-planner", "Plan outreach around industry conferences and events: pre-event outreach to confirmed attendees, during-event engagement (social media, networking), and post-event follow-up. Events create time-sensitive outreach windows.", "outreach", "High"),
    build_record("webinar-outreach-leverager", "Leverage webinars for outreach: attendees of relevant webinars are demonstrating interest in the topic. Reach out post-webinar with a relevant perspective and offer to discuss further.", "outreach", "Normal"),
    build_record("job-posting-trigger-outreach", "Trigger outreach based on job postings: when a target company posts for AI, automation, or data roles, it signals need and budget. Reach out with 'I noticed you're building your AI team — we help companies like yours accelerate that with external expertise.'", "outreach", "High"),
    build_record("funding-trigger-outreach", "Trigger outreach based on funding announcements: newly funded companies have budget and growth pressure. Reach out within days of the announcement with a relevant perspective on scaling with AI.", "outreach", "High"),
    build_record("leadership-change-trigger-outreach", "Trigger outreach based on leadership changes: new CTO, new COO, or new VP of Operations often bring new priorities and new budgets. Reach out with a welcome and relevant insight.", "outreach", "High"),
    build_record("company-news-trigger-outreach", "Trigger outreach based on company news: product launches, expansions, partnerships, or challenges. Reference the specific news and connect it to how AI consulting could help.", "outreach", "High"),
    build_record("content-engagement-trigger-outreach", "Trigger outreach based on content engagement: when a prospect engages with Yasmine's content (likes, comments, shares), reach out and continue the conversation. They've already shown interest.", "outreach", "Urgent"),
    build_record("technology-adoption-trigger-outreach", "Trigger outreach based on technology signals: when a company adopts a new platform (visible through job postings or tech stack changes), reach out with expertise on maximizing that platform with AI.", "outreach", "Normal"),
    build_record("competitor-loss-trigger-outreach", "When intelligence suggests a competitor lost a client or delivered poorly, tactfully reach out to the affected company with a value-driven approach. Never badmouth the competitor — lead with how you'd help.", "outreach", "Normal"),

    # 7. OUTREACH MESSAGING & COPYWRITING (outreach, High)
    build_record("first-touch-message-writer", "Write first-touch messages for every channel: personalized, specific, value-driven, and never pitchy. The first message determines whether the conversation continues or dies. Each channel has its own first-touch style.", "outreach", "High"),
    build_record("follow-up-message-writer", "Write follow-up messages that add new value with each touch: don't just 'bump' — share a relevant insight, a useful resource, a specific observation about their business, or a thought-provoking question. Every follow-up earns the right to exist.", "outreach", "High"),
    build_record("breakup-message-writer", "Write breakup messages for sequences that received no response: create curiosity or give a graceful exit. 'I'll assume the timing isn't right — I'll check back in a few months unless you tell me otherwise.'", "outreach", "Normal"),
    build_record("value-first-message-designer", "Design value-first outreach messages: lead with an insight, a resource, a framework, or a specific observation about their business. The value comes before any ask. Give before you take.", "outreach", "High"),
    build_record("personalization-framework-builder", "Build personalization frameworks for scalable outreach: first-line personalization (specific to the individual), company-level personalization (specific to their business), and industry-level personalization (specific to their niche). Layers of specificity.", "outreach", "High"),
    build_record("social-proof-message-integrator", "Integrate social proof into outreach messages naturally: mention relevant case studies, drop specific metrics, reference recognizable client names (with permission), and let results do the selling.", "outreach", "Normal"),
    build_record("conversation-transition-writer", "Write messages that transition from engagement to business conversation: 'I've enjoyed our exchanges on [topic] — curious if you're facing [specific challenge] at [company]? I've helped similar companies with exactly that.' Natural, not forced.", "outreach", "High"),
    build_record("warm-introduction-request-writer", "Write warm introduction requests: when a mutual connection exists, craft the request so the introducer has everything they need (who, why, and a forwardable blurb). Make it easy for people to introduce you.", "outreach", "Normal"),
    build_record("referral-outreach-writer", "Write outreach messages that leverage referrals: mention the referrer, establish the credibility transfer, reference the specific context the referrer provided, and make the ask clear but soft.", "outreach", "Normal"),
    build_record("tone-and-voice-adapter", "Adapt outreach tone by channel and prospect: formal on LinkedIn for enterprise prospects, casual on X for startup founders, community-appropriate for group engagement, and culturally sensitive across all touchpoints.", "outreach", "High"),

    # 8. LEAD TRACKING & CRM SYNC (operations, High)
    build_record("multi-channel-lead-tracker", "Track every lead across every channel: which channels have been used, what messages were sent, what responses were received, and what the current status is per channel. Single view of all touchpoints per prospect.", "operations", "High"),
    build_record("crm-sync-engine", "Sync all outreach activity to the CRM (GoHighLevel, HubSpot, or Airtable): every connection request, DM, comment, reply, and status change reflected in the CRM. No outreach activity exists only in the platform where it happened.", "operations", "High"),
    build_record("lead-status-updater", "Update lead status in real-time based on outreach activity: new → contacted → engaged → warm → meeting booked → in pipeline. Status transitions trigger the appropriate next workflow.", "operations", "High"),
    build_record("cross-channel-activity-logger", "Log all cross-channel activity per prospect: LinkedIn profile view on Day 1, connection request Day 2, X engagement Day 5, LinkedIn DM Day 7, email follow-up Day 10. The complete touchpoint timeline in one record.", "operations", "Normal"),
    build_record("engagement-score-calculator", "Calculate engagement scores per prospect: weight different engagement types (profile view < like < comment < DM reply < call booked), track score trend, and prioritize high-engagement leads for accelerated outreach.", "operations", "Normal"),
    build_record("contact-info-harvester", "Harvest contact information from outreach interactions: when a prospect provides their email in a DM, when a LinkedIn connection reveals their email, or when a community interaction leads to contact sharing. Add to the master contact record.", "operations", "Normal"),
    build_record("outreach-suppression-coordinator", "Coordinate suppression across all outreach channels: if a prospect is in active sales conversation with the Sales Lead agent, pause all automated outreach. If they've opted out on one channel, respect it across all channels. If they're an existing client, don't prospect them.", "operations", "High"),
    build_record("tag-and-segment-manager", "Tag and segment prospects based on outreach interactions: which channel they engage on most, what topics resonate, what stage they're at, and what their communication preferences seem to be.", "operations", "Normal"),

    # 9. RESPONSE MANAGEMENT & FOLLOW-UP (outreach, Urgent/High)
    build_record("multi-channel-response-monitor", "Monitor responses across all outreach channels in real-time: LinkedIn DM replies, X DM replies, Facebook Messenger responses, Instagram DMs, community platform messages, and email replies triggered by outreach. No response goes unseen.", "outreach", "Urgent"),
    build_record("response-categorizer", "Categorize every response: positive/interested, question/info request, objection, not interested, wrong person, referral, out of office, or spam/irrelevant. Route each category to the appropriate handling workflow.", "outreach", "High"),
    build_record("positive-response-accelerator", "When a positive response comes in on any channel, accelerate: respond within 15 minutes, advance the conversation toward a call, and coordinate with the Sales Lead agent for immediate pipeline entry.", "outreach", "Urgent"),
    build_record("question-response-handler", "Handle questions from any channel: provide clear, helpful answers that demonstrate expertise, address the specific question asked, and naturally guide toward deeper conversation.", "outreach", "High"),
    build_record("cross-channel-follow-up-sequencer", "When a prospect doesn't respond on one channel, follow up on another: no response to LinkedIn DM → engage with their X content → second LinkedIn DM referencing their recent post. Multi-channel follow-up feels like serendipity, not stalking — when done with the right spacing and value.", "outreach", "High"),
    build_record("ghosted-prospect-recovery", "Recover ghosted conversations: when a prospect was engaged but went silent, diagnose the likely reason (busy, lost interest, bad timing) and design the recovery approach (value-add re-engagement, different angle, longer pause then fresh approach).", "outreach", "Normal"),
    build_record("response-time-tracker", "Track response times across all channels: how fast are prospects responding, is response time improving or declining, and are there prospects whose response time is slowing (disengagement signal)?", "operations", "Normal"),
    build_record("conversation-continuation-writer", "Write messages that continue stalled conversations naturally: reference the last exchange, add something new (insight, case study, question), and reopen the dialogue without the awkward 'just following up.'", "outreach", "Normal"),
    build_record("meeting-transition-handler", "Handle the transition from outreach conversation to booked meeting: propose the call naturally, handle scheduling logistics, confirm the meeting, and hand off to the Sales Lead agent with full conversation context.", "outreach", "High"),

    # 10. LEAD REACTIVATION & NURTURE (outreach, Normal)
    build_record("dormant-lead-reactivator", "Reactivate dormant leads across all channels: identify leads who engaged but went cold, design channel-specific reactivation approaches, and execute with fresh value and new angles.", "outreach", "Normal"),
    build_record("multi-channel-nurture-designer", "Design multi-channel nurture for leads not yet ready: LinkedIn content engagement, X interactions, email newsletter inclusion, and periodic DM touchpoints. Stay top-of-mind across channels without overwhelming.", "outreach", "Normal"),
    build_record("trigger-based-reactivation", "Reactivate based on trigger events: prospect changed jobs (LinkedIn notification), company raised funding (news alert), prospect engaged with content (engagement trigger), or seasonal buying cycle. Right message at the right trigger moment.", "outreach", "High"),
    build_record("cold-to-warm-rewarmer", "Rewarm leads that were contacted but never engaged: new channel approach (tried LinkedIn, now try X), new messaging angle (different pain point, different value prop), and longer-form value delivery (share a relevant guide or resource).", "outreach", "Normal"),
    build_record("lost-opportunity-recycler", "Recycle lost opportunities into the outreach pipeline: leads that went through sales but didn't close can be re-entered into multi-channel nurture with new angles, updated offers, and respect for the previous conversation.", "outreach", "Normal"),
    build_record("seasonal-reactivation-campaigner", "Execute seasonal reactivation campaigns: 'As you plan for Q1, here's what we're seeing work for companies like yours' or 'Before end-of-year budget freeze, worth discussing how AI could transform [specific process] next year.'", "outreach", "Normal"),
    build_record("anniversary-reactivation", "Reactivate based on relationship anniversaries: 6 months since initial conversation, 1 year since they first engaged, or anniversary of a trigger event. 'It's been X months since we discussed Y — wanted to share what's changed.'", "outreach", "Low"),
    build_record("win-back-outreach-designer", "Design win-back outreach for prospects who explicitly declined: respectful timing (minimum 90 days), new value proposition, acknowledgment of previous conversation, and zero pressure.", "outreach", "Normal"),

    # 11. COMMUNITY & PARTNERSHIP OUTREACH (outreach, Normal)
    build_record("community-outreach-strategist", "Design outreach through online communities: Slack groups, Discord servers, Reddit communities, Facebook groups, and niche forums. Build reputation through consistent value contribution before any direct outreach.", "outreach", "Normal"),
    build_record("community-value-contributor", "Contribute genuine value in target communities: answer questions, share insights, provide resources, and help others without expectation of return. Community reputation is the most authentic form of outreach.", "outreach", "Normal"),
    build_record("community-to-dm-transitioner", "Transition community interactions to direct conversations: when a community member expresses a pain point the agency can solve, offer to discuss further in DM. The transition should feel helpful, not predatory.", "outreach", "Normal"),
    build_record("partnership-outreach-executor", "Execute outreach to potential partners: complementary service providers, technology vendors, industry associations, and event organizers. Partnership outreach is relationship-first with mutual benefit as the foundation.", "outreach", "Normal"),
    build_record("influencer-outreach-executor", "Execute outreach to industry influencers: thought leaders, content creators, and community leaders whose audience overlaps with the agency's ICP. Offer value (guest content, collaboration, interview), not extraction.", "outreach", "Normal"),
    build_record("podcast-guest-outreach", "Execute outreach to podcast hosts: identify relevant podcasts, craft tailored pitch emails, propose specific topics aligned with their audience, and manage the booking process.", "outreach", "Normal"),
    build_record("event-organizer-outreach", "Execute outreach to event organizers: propose speaking sessions, panel participation, or sponsorship. Position Yasmine as a valuable contributor to their event, not just someone seeking a platform.", "outreach", "Normal"),
    build_record("co-marketing-outreach", "Execute co-marketing outreach: propose joint webinars, co-authored content, or shared resources with companies that serve the same audience but don't compete directly.", "outreach", "Normal"),

    # 12. OUTREACH COMPLIANCE & ACCOUNT HEALTH (operations, High)
    build_record("platform-compliance-monitor", "Monitor compliance with each platform's outreach policies: LinkedIn daily limits, X DM restrictions, Facebook group rules, and any platform-specific terms of service. Violation = account restriction = pipeline death.", "operations", "High"),
    build_record("linkedin-account-safety-manager", "Manage LinkedIn account safety: stay under connection request limits (100/week as of current limits), maintain high acceptance rates, avoid flagged behavior patterns, and monitor Social Selling Index.", "operations", "High"),
    build_record("automation-humanization-enforcer", "Ensure all automated outreach feels human: randomized send times, personalized elements in every message, natural language variation, and manual intervention points in automated sequences. If it feels automated, it fails.", "operations", "High"),
    build_record("opt-out-processor", "Process opt-outs across all channels: when someone says 'not interested' or 'stop messaging me,' immediately cease all outreach across all channels, log the opt-out, and update suppression lists. One bad opt-out experience can become a public complaint.", "operations", "Urgent"),
    build_record("data-privacy-compliance", "Ensure all outreach data handling complies with privacy regulations: GDPR consent requirements for EU prospects, CAN-SPAM compliance for email touchpoints, and platform-specific data usage rules.", "operations", "High"),
    build_record("account-rotation-manager", "If using multiple accounts or profiles for outreach: manage rotation, prevent overlap, maintain account health across all profiles, and ensure consistent messaging regardless of which account sends.", "operations", "Normal"),

    # 13. OUTREACH ANALYTICS & REPORTING (operations, Normal)
    build_record("daily-outreach-activity-report", "Daily report: connection requests sent, DMs sent, comments made, responses received, meetings booked, and leads advanced. Activity metrics by channel.", "operations", "Normal"),
    build_record("weekly-outreach-performance-report", "Weekly performance: response rates by channel, engagement rates, conversion rates (touch → response → meeting), best-performing messages, and channel comparison.", "operations", "High"),
    build_record("monthly-outreach-analytics", "Monthly deep analytics: channel ROI comparison, message performance analysis, sequence effectiveness, lead source attribution, and outreach-to-pipeline contribution.", "operations", "Normal"),
    build_record("channel-effectiveness-ranker", "Rank channels by effectiveness: which channel produces the highest response rate, the highest quality conversations, the fastest time-to-meeting, and the best eventual close rate. Reallocate effort toward winners.", "operations", "High"),
    build_record("message-performance-analyzer", "Analyze message performance across all channels: which first-touch messages get the best response rate, which follow-ups reopen conversations, and which CTAs book the most meetings. Data-driven message optimization.", "operations", "Normal"),
    build_record("sequence-conversion-tracker", "Track full sequence conversion: from first touch through every step to meeting booked or lead lost. Identify which steps in the sequence lose the most prospects and optimize those specific steps.", "operations", "Normal"),
    build_record("engagement-trend-monitor", "Monitor engagement trends over time: are response rates improving or declining, are certain channels becoming more or less effective, and are seasonal patterns emerging?", "operations", "Normal"),
    build_record("outreach-to-revenue-attributor", "Attribute revenue back to outreach activities: which channel, which message, which sequence, and which touchpoint was the first meaningful interaction for deals that eventually closed. Prove outreach ROI.", "operations", "Normal"),

    # 14. OUTREACH OPTIMIZATION (operations, Normal)
    build_record("outreach-process-optimizer", "Continuously optimize the outreach process: reduce time per outreach action, increase personalization quality, improve response rates, and streamline the flow from first touch to meeting booked.", "operations", "Normal"),
    build_record("personalization-at-scale-optimizer", "Optimize personalization at scale: build systems that enable genuine personalization without spending 20 minutes per message. Templated structures with personalized components, research shortcuts, and batch preparation.", "operations", "High"),
    build_record("multi-touch-attribution-optimizer", "Optimize the multi-touch journey: which combination of touches across which channels produces the highest conversion? Design the optimal touch sequence based on attribution data.", "operations", "Normal"),
    build_record("response-rate-improvement-engine", "Systematically improve response rates: test new approaches, analyze winning patterns, incorporate prospect feedback, and benchmark against industry standards. Target improvement every quarter.", "operations", "Normal"),
    build_record("outreach-timing-optimizer", "Optimize outreach timing: best days and hours for each channel, optimal spacing between touches, and timing alignment with prospect timezone and schedule patterns.", "operations", "Normal"),
    build_record("outreach-template-refresher", "Regularly refresh outreach templates: messages that worked 3 months ago may be stale. Update language, refresh references, incorporate new case studies, and adapt to market changes.", "operations", "Normal"),
    build_record("competitor-outreach-analyzer", "Analyze competitor outreach: what messages are prospects receiving from competitors, how can the agency differentiate its outreach, and what approaches are prospects tired of seeing?", "research", "Normal"),

    # 15. CROSS-AGENT COORDINATION (workflow, Normal)
    build_record("cold-email-to-multi-channel-coordinator", "Coordinate with the Cold Email Specialist: when cold email generates interest but doesn't book a call, the Outreach Strategist picks up the prospect on LinkedIn or other channels. Seamless hand-off between email and social outreach.", "workflow", "High"),
    build_record("content-to-outreach-bridge", "Coordinate with LinkedIn Content and Content Specialist agents: when content generates engagement from target prospects, transition that engagement into direct outreach. Content warms, outreach converts.", "workflow", "High"),
    build_record("sales-lead-handoff-manager", "Manage handoff to the Sales Lead agent: when multi-channel outreach produces a qualified, interested prospect ready for a sales conversation, hand off with complete context — every touchpoint, every message, every signal.", "workflow", "High"),
    build_record("research-request-coordinator", "Coordinate with the Research Analyst: request prospect research before high-value outreach, request niche intelligence for new outreach campaigns, and request trigger event monitoring for reactivation.", "workflow", "Normal"),
    build_record("client-success-coordination", "Coordinate with Client Success agent: ensure existing clients aren't being prospected, that referral conversations from clients flow into outreach, and that case studies from successful projects feed into outreach messaging.", "workflow", "Normal"),
    build_record("crm-single-source-enforcer", "Ensure the CRM remains the single source of truth: all outreach activity logged, all lead statuses current, all communication history complete, and no outreach happening outside the tracked system.", "workflow", "High"),

    # 16. STRATEGIC OUTREACH INTELLIGENCE (research, Normal)
    build_record("outreach-landscape-researcher", "Research the outreach landscape: what channels prospects are most receptive on, what outreach fatigue looks like in target niches, and how outreach norms are evolving. Stay ahead of the curve.", "research", "Normal"),
    build_record("platform-feature-monitor", "Monitor platform feature changes that affect outreach: new LinkedIn features, X DM changes, Facebook group policy updates, and new platforms emerging. Adapt outreach tactics to platform evolution.", "research", "Normal"),
    build_record("outreach-playbook-builder", "Build and maintain the multi-channel outreach playbook: documented processes for every outreach scenario, templates for every channel, sequence designs for every persona, and decision trees for response handling.", "operations", "High"),
    build_record("quarterly-outreach-strategy-review", "Quarterly strategic review: channel performance, message effectiveness, sequence optimization, competitive outreach landscape, and strategic adjustments for next quarter.", "operations", "Normal"),
    build_record("annual-outreach-review", "Annual comprehensive review: total outreach volume, response rates by channel, meetings generated, pipeline contribution, revenue attributed, and strategic direction for the coming year.", "operations", "Normal"),
]


def main():
    token = os.environ.get("TEABLE_API_TOKEN")
    if not token:
        print("ERROR: TEABLE_API_TOKEN not set")
        sys.exit(1)

    client = TeableExtendedClient(api_token=token)

    total = len(SKILLS)
    print(f"Loading {total} skills for Salma (Outreach Strategist Agent)...")

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
