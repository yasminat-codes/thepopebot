#!/usr/bin/env python3
"""
Load all 140 Hana (Content Specialist Agent) skills into the Teable Skills Pipeline.

Usage:
    TEABLE_API_TOKEN="..." python3 load_hana_skills.py
    TEABLE_API_TOKEN="..." python3 load_hana_skills.py --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

TABLE_ID = "tblyl5mzFebauxrGf1L"
HANA_RECORD_ID = "rech31QU9ENLjHaAXgb"
WORKSPACE = "hana-workspace"
BUILDER = "Zahra"
CREATION_SKILL = "Skillforge"

# All 140 Hana skills: (name, description, category, priority)
HANA_SKILLS = [
    # ─── 1. CONTENT STRATEGY & PLANNING ──────────────────────────────────
    ("multi-channel-content-strategist",
     "Develop the overarching content strategy across all non-LinkedIn channels: define the role each channel plays (blog for SEO and depth, X for real-time thought leadership, Facebook for community and ads, email for nurture, YouTube for demonstration), how they interconnect, and how content flows between them.",
     "content", "High"),
    ("channel-audience-mapper",
     "Research and map the audience on each channel: who follows on X vs. who reads the blog vs. who engages on Facebook vs. who opens emails. Understand how audience segments differ across channels and tailor content accordingly.",
     "research", "Normal"),
    ("content-pillar-architect",
     "Define content pillars that span all channels: AI Implementation, Automation Strategy, Business Transformation, Tool Reviews, Industry Insights, Behind the Scenes, and Client Results. Ensure every piece of content maps to a pillar and pillars are balanced across channels.",
     "content", "High"),
    ("quarterly-content-roadmap",
     "Build quarterly content roadmaps: themes by month, key campaigns, content series, seasonal hooks, and alignment with business goals (launches, events, promotions). The strategic backbone that prevents random content production.",
     "content", "High"),
    ("monthly-content-calendar-builder",
     "Build detailed monthly content calendars across all channels: what publishes where, on which day, in which format, targeting which audience segment, and supporting which business objective. Every slot filled, every piece purposeful.",
     "content", "High"),
    ("weekly-content-plan-finalizer",
     "Finalize the weekly content plan every Sunday: confirm all pieces are drafted, reviewed, and scheduled. Swap in timely content if trending opportunities have emerged. Ensure nothing publishes without being ready.",
     "content", "High"),
    ("content-campaign-designer",
     "Design multi-channel content campaigns: coordinated pushes around a theme, launch, or event. Blog post as the anchor, social posts driving traffic, email nurturing the engaged, and retargeting capturing the interested.",
     "content", "Normal"),
    ("content-flywheel-architect",
     "Design the content flywheel: how blog content feeds social, social engagement feeds email list growth, email nurtures feed sales pipeline, and client results feed new content. Every piece of content should generate momentum for the next.",
     "content", "Normal"),
    ("content-budget-allocator",
     "Allocate content budget across channels: tool costs (scheduling, SEO, design), paid promotion budget, freelancer costs if needed, and content creation tool subscriptions. Maximize output per dollar.",
     "operations", "Normal"),
    ("channel-priority-ranker",
     "Rank content channels by ROI and strategic value: which channels drive the most traffic, which generate the most leads, which build the most authority, and which have the most growth potential. Reallocate effort toward highest-impact channels.",
     "content", "Normal"),

    # ─── 2. SEO RESEARCH & STRATEGY ──────────────────────────────────────
    ("keyword-research-engine",
     "Conduct comprehensive keyword research: identify high-volume keywords in the AI consulting space, long-tail keywords with lower competition, question-format keywords (how to, what is, why does), and semantic keyword clusters. Build a master keyword database.",
     "research", "High"),
    ("keyword-difficulty-assessor",
     "Assess keyword difficulty for every target keyword: domain authority needed to rank, current top-10 competition analysis, content quality of ranking pages, and realistic ranking timeline. Prioritize keywords the agency can actually win.",
     "research", "Normal"),
    ("search-intent-classifier",
     "Classify search intent for every keyword: informational (wants to learn), navigational (looking for something specific), commercial investigation (comparing options), or transactional (ready to buy). Match content type to intent.",
     "research", "High"),
    ("content-gap-analyzer",
     "Analyze content gaps: what keywords do competitors rank for that the agency does not, what questions are being asked that nobody answers well, and what topics have search volume but no quality content. Every gap is an opportunity.",
     "research", "High"),
    ("serp-feature-researcher",
     "Research SERP features for target keywords: featured snippets, People Also Ask, knowledge panels, video results, and image packs. Design content to capture SERP features, not just blue link rankings.",
     "research", "Normal"),
    ("competitor-seo-analyzer",
     "Analyze competitor SEO strategies: what keywords they target, what content ranks, their backlink profile, their content publishing cadence, and their domain authority trajectory. Identify where to compete and where to outflank.",
     "research", "High"),
    ("topic-cluster-architect",
     "Design topic clusters: pillar pages (comprehensive guides on broad topics) surrounded by cluster content (specific subtopics linking back to the pillar). Build topical authority that Google rewards with higher rankings.",
     "content", "High"),
    ("keyword-mapping-to-content",
     "Map keywords to specific content pieces: every blog post targets a primary keyword and 3-5 secondary keywords. Ensure no keyword cannibalization (two pages competing for the same keyword) and full coverage of the keyword universe.",
     "content", "Normal"),
    ("seo-trend-monitor",
     "Monitor SEO trends: algorithm updates (Google core updates, helpful content updates), ranking factor changes, new SERP features, and shifts in search behavior (AI search, voice search, zero-click searches). Adapt strategy to search landscape evolution.",
     "research", "Normal"),
    ("local-seo-optimizer",
     "If applicable, optimize for local search: Google Business Profile, local keywords, location-specific content, and local link building. Capture prospects searching for AI consultant near me or city-specific queries.",
     "content", "Normal"),
    ("backlink-strategy-designer",
     "Design a backlink acquisition strategy: guest posting targets, digital PR opportunities, resource page outreach, broken link building, and partnership link exchanges. Backlinks remain the strongest off-page ranking factor.",
     "outreach", "Normal"),
    ("seo-technical-auditor",
     "Audit technical SEO: site speed, mobile-friendliness, crawlability, indexation status, structured data markup, canonical tags, internal linking structure, and Core Web Vitals. Fix technical issues that suppress ranking potential.",
     "research", "High"),

    # ─── 3. BLOG CONTENT CREATION ────────────────────────────────────────
    ("blog-post-writer",
     "Write long-form blog posts that rank on Google and convert readers into prospects: in-depth, well-structured, original-insight-driven content that answers the search query better than anything currently ranking. 1,500-3,000 words, scannable, with clear takeaways.",
     "content", "High"),
    ("blog-post-outliner",
     "Before writing, create detailed blog outlines: H2 and H3 structure mapped to search intent and keyword targets, key points for each section, data or examples to include, and the narrative arc from hook to CTA.",
     "content", "High"),
    ("blog-headline-writer",
     "Write blog headlines that balance SEO and click appeal: include the primary keyword naturally, create curiosity or promise value, keep under 60 characters for SERP display, and test multiple variants.",
     "content", "High"),
    ("blog-introduction-writer",
     "Write blog introductions that prevent bounce: hook the reader in the first sentence, establish relevance (this is for you if...), preview the value they will get, and transition smoothly into the body. The intro determines if the remaining 2,500 words get read.",
     "content", "High"),
    ("blog-cta-strategist",
     "Design blog CTAs: what to ask for at the end of each post (newsletter signup, free resource download, consultation booking, related content), where to place CTAs (mid-post and end-post), and how to frame them naturally within the content flow.",
     "content", "Normal"),
    ("pillar-page-builder",
     "Build comprehensive pillar pages: 3,000-5,000 word definitive guides on core topics, structured with a table of contents, interlinked with cluster content, and designed to rank for high-volume head terms.",
     "content", "High"),
    ("how-to-guide-writer",
     "Write step-by-step how-to guides: actionable, specific, with screenshots or examples where helpful, and organized so readers can follow along and implement. The format that builds the most trust with a technical audience.",
     "content", "High"),
    ("case-study-blog-writer",
     "Write blog-format case studies: the client's challenge (anonymized if needed), the approach, the implementation details, the results with specific metrics, and the lessons learned. Proof that the agency delivers results.",
     "content", "High"),
    ("comparison-post-writer",
     "Write comparison and vs. posts: tool comparisons (ChatGPT vs. Claude for business), approach comparisons (build vs. buy AI), and strategy comparisons. High commercial intent keywords that attract prospects in decision mode.",
     "content", "High"),
    ("listicle-writer",
     "Write list-format blog posts: 10 Ways AI Is Transforming Industry, 7 Mistakes Businesses Make When Implementing AI. Scannable, shareable, and effective for capturing featured snippets.",
     "content", "Normal"),
    ("thought-leadership-essay-writer",
     "Write long-form thought leadership essays: original perspectives on the future of AI consulting, contrarian takes on industry trends, and philosophical pieces on technology and business. The content that gets shared by other thought leaders.",
     "content", "High"),
    ("blog-update-and-refresher",
     "Identify and refresh outdated blog content: update statistics, add new information, improve structure, refresh screenshots, and resubmit to Google for recrawling. Refreshed content often ranks higher than new content.",
     "content", "Normal"),
    ("internal-linking-optimizer",
     "Optimize internal linking within blog content: link new posts to relevant existing content, ensure pillar pages link to all cluster content, fix orphan pages, and design link architecture that distributes page authority efficiently.",
     "content", "Normal"),
    ("blog-seo-on-page-optimizer",
     "Optimize every blog post for on-page SEO: title tag, meta description, URL slug, header tags, keyword placement, image alt text, schema markup, and readability score. The invisible work that makes content discoverable.",
     "content", "High"),
    ("featured-snippet-optimizer",
     "Optimize content specifically to capture featured snippets: identify snippet opportunities, structure content to match snippet formats (paragraph, list, table), and position answer content directly below the target H2.",
     "content", "Normal"),

    # ─── 4. X (TWITTER) CONTENT ──────────────────────────────────────────
    ("x-content-strategist",
     "Define the X content strategy: posting cadence (3-5x daily), content mix (threads, single tweets, quote tweets, replies, reposts with commentary), voice and tone (sharper and more opinionated than blog), and growth targets.",
     "content", "High"),
    ("x-thread-writer",
     "Write X threads: 5-15 tweet threads that break down complex AI topics, share frameworks, tell stories, and deliver concentrated value. Strong hook tweet, clear numbering, and a closing CTA. Threads are the blog posts of X.",
     "content", "High"),
    ("x-single-post-writer",
     "Write single-post tweets: hot takes, quick insights, observations, questions, and reactions to industry news. Short, punchy, and designed to spark engagement. Every tweet should make someone think, laugh, or save it.",
     "content", "High"),
    ("x-reply-strategist",
     "Develop a strategic reply approach: identify high-visibility accounts and trending conversations to reply to, craft replies that add genuine value (not great point!), and use replies to build visibility with new audiences.",
     "content", "Normal"),
    ("x-quote-tweet-writer",
     "Write quote tweets that add perspective: take someone else's tweet and add Yasmine's unique angle, counter-perspective, additional data, or practical application. Piggyback on existing reach with original thinking.",
     "content", "Normal"),
    ("x-engagement-manager",
     "Manage daily engagement on X: respond to replies on Yasmine's tweets, engage in conversations, follow relevant accounts, and maintain the human presence that algorithms reward.",
     "content", "Normal"),
    ("x-trend-hijacker",
     "Monitor X trending topics and breaking news for opportunities to insert Yasmine's perspective on AI-related trends. Rapid-response content that rides the attention wave while adding substantive value.",
     "content", "Normal"),
    ("x-audience-growth-strategist",
     "Design and execute X audience growth strategies: content that drives follows (threads, valuable insights), engagement that builds community (replies, conversations), and consistency that signals algorithmic favor.",
     "content", "Normal"),
    ("x-analytics-tracker",
     "Track X performance metrics: impressions, engagement rate, follower growth, profile visits, link clicks, and top-performing content. Identify what is working and double down.",
     "operations", "Normal"),
    ("x-to-blog-bridge",
     "Use X content as a testing ground for blog topics: tweets that get high engagement signal topics worth deep-diving into as blog posts. Track the tweet-to-blog pipeline.",
     "content", "Normal"),

    # ─── 5. FACEBOOK CONTENT ─────────────────────────────────────────────
    ("facebook-content-strategist",
     "Define the Facebook content strategy: organic posting cadence, content types (text posts, images, videos, links, events), community engagement approach, and whether to leverage Facebook Groups for community building.",
     "content", "Normal"),
    ("facebook-post-writer",
     "Write Facebook posts optimized for the platform: longer-form than X but more conversational than blog, designed for the Facebook algorithm (engagement-driving, comment-provoking, share-worthy), and formatted for mobile consumption.",
     "content", "Normal"),
    ("facebook-group-strategist",
     "If leveraging a Facebook Group: define the group positioning, membership criteria, content cadence, engagement rules, and growth strategy. Groups build community and trust that profiles cannot.",
     "content", "Normal"),
    ("facebook-ad-copy-writer",
     "Write Facebook ad copy for content promotion and lead generation: scroll-stopping headlines, benefit-driven body copy, clear CTAs, and multiple variants for A/B testing. Align ad copy with the landing page experience.",
     "outreach", "Normal"),
    ("facebook-audience-builder",
     "Build and manage Facebook audiences: custom audiences from email lists, lookalike audiences from clients and engaged prospects, interest-based targeting for cold audiences, and retargeting audiences from website visitors.",
     "outreach", "Normal"),
    ("facebook-content-repurposer",
     "Adapt content from other channels for Facebook: turn blog posts into Facebook-native summaries, convert X threads into Facebook posts, and create Facebook-specific visual content from existing assets.",
     "content", "Normal"),
    ("facebook-analytics-tracker",
     "Track Facebook performance: reach, engagement, click-through rates, audience growth, and ad performance metrics. Compare organic vs. paid performance and optimize the mix.",
     "operations", "Normal"),
    ("facebook-community-manager",
     "Manage Facebook community engagement: respond to comments, moderate discussions, handle inquiries, share user-generated content, and maintain a positive community environment.",
     "content", "Normal"),

    # ─── 6. EMAIL NEWSLETTER & NURTURE CONTENT ───────────────────────────
    ("email-newsletter-strategist",
     "Define the email newsletter strategy: platform selection (ConvertKit, Beehiiv, Substack), publishing cadence, content differentiation from the blog and LinkedIn, subscriber growth strategy, and monetization path.",
     "outreach", "High"),
    ("email-newsletter-writer",
     "Write email newsletter editions: compelling subject lines, engaging openings, valuable body content, and clear CTAs. Shorter and more personal than blog posts, more direct than LinkedIn newsletters. Write like you are emailing a smart friend.",
     "outreach", "High"),
    ("email-subject-line-writer",
     "Write email subject lines optimized for open rates: curiosity-driven, benefit-driven, urgency-driven, and personalized variants. A/B test systematically and build a library of winning subject line patterns.",
     "outreach", "High"),
    ("email-nurture-sequence-writer",
     "Write email nurture sequences for different audience segments: new subscribers (welcome sequence introducing Yasmine and the agency), warm leads (value sequence building trust toward a sales conversation), and cold re-engagement (win-back sequence for dormant subscribers).",
     "outreach", "High"),
    ("email-segmentation-strategist",
     "Design email segmentation strategy: segment by source (blog subscriber, social follower, event attendee), by interest (AI strategy, automation, specific industry), by engagement level (active, declining, dormant), and by funnel stage.",
     "outreach", "Normal"),
    ("email-automation-designer",
     "Design email automation flows: trigger-based sequences (downloaded a resource → nurture → offer), behavior-based branching (opened/did not open, clicked/did not click), and time-based drips. Map the entire automated email ecosystem.",
     "workflow", "Normal"),
    ("email-deliverability-optimizer",
     "Optimize email deliverability for the newsletter: list hygiene, authentication (SPF, DKIM, DMARC), engagement-based sending, sunset policy for inactive subscribers, and spam score monitoring.",
     "operations", "Normal"),
    ("email-growth-strategist",
     "Grow the email list: lead magnets (guides, templates, checklists), content upgrades within blog posts, newsletter CTAs across all channels, co-registration partnerships, and referral programs.",
     "outreach", "High"),
    ("lead-magnet-creator",
     "Create lead magnets that drive email signups: downloadable PDF guides, templates, checklists, toolkits, and mini-courses. Each lead magnet aligned with a specific audience segment and funnel stage.",
     "content", "High"),
    ("email-analytics-tracker",
     "Track email metrics: open rate, click rate, unsubscribe rate, list growth rate, and revenue attributed to email. Analyze by segment, by sequence, and by individual send.",
     "operations", "Normal"),

    # ─── 7. VIDEO & MULTIMEDIA CONTENT ───────────────────────────────────
    ("youtube-content-strategist",
     "Define the YouTube strategy (if applicable): channel positioning, video types (tutorials, thought leadership, vlogs, interviews), publishing cadence, and growth approach. YouTube is the second-largest search engine — SEO applies here too.",
     "content", "Normal"),
    ("video-script-writer",
     "Write video scripts: hook within the first 5 seconds, clear structure, conversational delivery, visual callouts (b-roll suggestions, on-screen text), and strong closing CTA. Scripts for talking-head, screen-share, and presentation formats.",
     "content", "Normal"),
    ("video-seo-optimizer",
     "Optimize videos for YouTube search: keyword-rich titles, detailed descriptions with timestamps, relevant tags, custom thumbnails, and playlist organization. Apply SEO discipline to video content.",
     "content", "Normal"),
    ("podcast-content-planner",
     "If launching a podcast: define the format (solo, interview, panel), episode cadence, topic planning, guest research and outreach, and distribution strategy. Plan the content that makes a podcast worth subscribing to.",
     "content", "Normal"),
    ("podcast-episode-outliner",
     "Outline podcast episodes: key talking points, questions for guests, story beats, transitions, and closing thoughts. Enough structure to be coherent, enough flexibility to be natural.",
     "content", "Normal"),
    ("audio-content-repurposer",
     "Repurpose audio content: transcribe podcasts into blog posts, extract quotes for social content, create audiograms for social promotion, and compile highlights into recap episodes.",
     "content", "Normal"),
    ("infographic-designer",
     "Design infographics that visualize data, processes, and frameworks: shareable on social, embeddable in blog posts, and linked by other sites (backlink magnet). Combine data credibility with visual appeal.",
     "content", "Normal"),
    ("visual-content-strategist",
     "Plan visual content across all channels: what needs custom graphics, what can use templates, what warrants video, and what works as simple text. Balance visual quality with production speed.",
     "content", "Normal"),

    # ─── 8. GUEST CONTENT & EXTERNAL PUBLISHING ──────────────────────────
    ("guest-post-opportunity-researcher",
     "Research guest posting opportunities: identify high-authority publications in the AI, business, and technology space that accept guest contributions. Evaluate by domain authority, audience fit, and editorial quality.",
     "research", "Normal"),
    ("guest-post-pitch-writer",
     "Write pitches for guest post placements: personalized to each publication, proposing specific topics aligned with their editorial focus, demonstrating Yasmine's expertise, and including writing samples.",
     "outreach", "Normal"),
    ("guest-post-writer",
     "Write guest posts for external publications: match the publication's style and tone, deliver genuine value to their audience, include a natural author bio with CTA, and meet editorial guidelines. Guest posts build authority and backlinks simultaneously.",
     "content", "High"),
    ("media-opportunity-researcher",
     "Research media opportunities: podcast guest appearances, expert commentary opportunities, industry publication features, and award nominations. Build Yasmine's presence beyond owned channels.",
     "research", "Normal"),
    ("podcast-guest-pitch-writer",
     "Write pitches for podcast guest appearances: identify relevant podcasts, craft compelling topic proposals, highlight Yasmine's unique angle, and manage the booking process.",
     "outreach", "Normal"),
    ("expert-commentary-provider",
     "Prepare expert commentary for journalists and publications: when reporters need AI expert quotes (HARO, Qwoted, direct outreach), craft responses that are quotable, credible, and brand-building.",
     "outreach", "Normal"),
    ("content-syndication-strategist",
     "Design a content syndication strategy: which blog posts to syndicate, to which platforms (Medium, Substack, industry publications), with what modifications (canonical tags, unique introductions), and how to drive traffic back to owned properties.",
     "content", "Normal"),

    # ─── 9. TREND MONITORING & CONTENT INTELLIGENCE ──────────────────────
    ("multi-platform-trend-monitor",
     "Monitor content trends across all platforms simultaneously: what is trending on X, what is performing on Facebook, what is ranking on Google, what is viral on YouTube, and what topics are crossing platforms. Identify cross-platform trend waves.",
     "research", "High"),
    ("google-trends-analyzer",
     "Analyze Google Trends for content opportunities: rising search queries, seasonal patterns, geographic interest variations, and related queries that expand the content horizon.",
     "research", "Normal"),
    ("industry-news-content-trigger",
     "Monitor industry news for content triggers: AI company announcements, tool launches, regulatory changes, market reports, and major partnerships. Each news item is a potential content piece if the agency can add unique perspective.",
     "research", "High"),
    ("social-listening-monitor",
     "Monitor social conversations across platforms: what are business owners saying about AI, what complaints are recurring, what questions keep appearing, and what misconceptions are spreading. Social listening feeds content ideation.",
     "research", "Normal"),
    ("content-format-trend-tracker",
     "Track which content formats are gaining traction: are carousels outperforming text on Facebook, are long-form threads declining on X, are short-form videos surging on all platforms. Adapt format mix to platform evolution.",
     "research", "Normal"),
    ("algorithm-change-monitor",
     "Monitor algorithm changes across all platforms: Google search updates, X algorithm shifts, Facebook reach changes, YouTube recommendation updates, and email deliverability changes. Adapt strategy to algorithmic reality.",
     "research", "High"),
    ("emerging-topic-detector",
     "Detect emerging topics before they peak: conversations starting in niche communities that have not hit mainstream channels yet, academic research nearing commercial relevance, and policy discussions that will affect the AI space.",
     "research", "Normal"),
    ("seasonal-content-planner",
     "Plan content around seasonal and calendar events: New Year business planning, Q1 budget season, conference season, summer slowdown, Q4 planning, and industry-specific seasonal patterns. Ride the attention waves.",
     "content", "Normal"),

    # ─── 10. CONTENT ANALYTICS & PERFORMANCE ─────────────────────────────
    ("blog-analytics-dashboard",
     "Track and analyze blog performance: pageviews, unique visitors, time on page, bounce rate, scroll depth, conversion rate, and organic search traffic. Per-post and aggregate analysis.",
     "operations", "High"),
    ("social-media-analytics-dashboard",
     "Track performance across X, Facebook, and any other social platforms: impressions, engagement rate, follower growth, click-throughs, and top-performing content per platform.",
     "operations", "Normal"),
    ("email-analytics-dashboard",
     "Track email performance: open rates, click rates, conversion rates, list growth, churn rate, and revenue attributed to email. Per-send and trend analysis.",
     "operations", "Normal"),
    ("cross-channel-attribution-analyzer",
     "Analyze content attribution across channels: which channels drive awareness, which drive consideration, which drive conversion, and what the typical multi-touch journey looks like from first content touch to client.",
     "operations", "Normal"),
    ("content-roi-calculator",
     "Calculate ROI of content efforts: total investment (time, tools, promotion spend) vs. value generated (traffic, leads, pipeline influence, deals attributed). Calculate cost-per-lead and cost-per-client from content.",
     "operations", "Normal"),
    ("content-performance-ranker",
     "Rank all content by performance: top posts by traffic, top posts by engagement, top posts by conversion, and top posts by backlinks. Identify the content DNA that drives results.",
     "operations", "Normal"),
    ("underperforming-content-diagnoser",
     "Diagnose why content underperforms: poor keyword targeting, weak headline, wrong format for the platform, published at the wrong time, insufficient promotion, or simply a topic the audience does not care about. Diagnose and prescribe fixes.",
     "operations", "Normal"),
    ("content-decay-detector",
     "Detect content decay: blog posts that were ranking but are declining, social content formats that are losing engagement over time, and email sequences with declining open rates. Flag decaying content for refresh or retirement.",
     "operations", "Normal"),
    ("a-b-test-manager",
     "Manage A/B tests across content: headline variants, CTA variants, email subject lines, social post formats, and publishing times. Run tests with statistical rigor and document learnings.",
     "operations", "Normal"),

    # ─── 11. CONTENT OPTIMIZATION & IMPROVEMENT ──────────────────────────
    ("blog-seo-refresh-engine",
     "Systematically refresh blog content for SEO: update target keywords based on current search data, improve content depth, add new sections, update internal links, and resubmit sitemaps. Schedule quarterly refreshes for top-performing posts.",
     "content", "High"),
    ("headline-optimization-engine",
     "Test and optimize headlines across platforms: blog post titles for CTR in search, social post hooks for engagement, and email subject lines for open rates. Build a headline performance database.",
     "content", "Normal"),
    ("content-readability-optimizer",
     "Optimize content readability: Fleisch-Kincaid scoring, sentence length variation, paragraph length for mobile, jargon simplification, and active voice enforcement. Technical content should be accessible, not academic.",
     "content", "Normal"),
    ("conversion-rate-optimizer",
     "Optimize content for conversion: CTA placement and wording, lead magnet alignment with content topic, form design and friction reduction, and post-conversion experience. Turn traffic into leads.",
     "content", "High"),
    ("content-personalization-engine",
     "Personalize content experiences where possible: dynamic CTAs based on visitor behavior, content recommendations based on reading history, and segmented email content based on subscriber interests.",
     "content", "Normal"),
    ("content-accessibility-checker",
     "Ensure all content meets accessibility standards: alt text on images, readable font sizes, sufficient color contrast, captions on videos, transcript availability for audio, and screen-reader-friendly formatting.",
     "content", "Normal"),
    ("mobile-optimization-checker",
     "Verify all content is optimized for mobile consumption: responsive layouts, appropriate font sizes, tap-friendly CTAs, fast load times, and no horizontal scrolling. Most content is consumed on phones.",
     "content", "Normal"),

    # ─── 12. CONTENT REPURPOSING & DISTRIBUTION ──────────────────────────
    ("content-atomization-engine",
     "Atomize every major content piece into micro-content: one blog post becomes 5 X posts, 3 Facebook posts, 2 email sections, 1 infographic, and 5 quote graphics. Maximum distribution from minimum ideation.",
     "content", "High"),
    ("blog-to-social-converter",
     "Convert blog posts into platform-native social content: extract key insights for X threads, create visual summaries for Facebook, pull data points for quote graphics, and write email teasers that drive blog traffic.",
     "content", "High"),
    ("social-to-blog-expander",
     "When social content gets high engagement, expand into full blog posts: add depth, research, examples, and SEO optimization. Validated ideas get the long-form treatment.",
     "content", "Normal"),
    ("content-to-lead-magnet-converter",
     "Convert high-performing blog content into downloadable lead magnets: compile related posts into comprehensive guides, add templates and checklists, and package behind an email gate.",
     "content", "Normal"),
    ("cross-channel-distribution-scheduler",
     "Schedule content distribution across all channels: stagger publishing to avoid competing with yourself, tailor the promotion message per platform, and maximize the lifespan of each content piece.",
     "operations", "Normal"),
    ("content-promotion-strategist",
     "Design content promotion beyond organic: paid social promotion for top content, email newsletter features, community sharing, influencer tagging, and strategic comment placement. Great content with no promotion is invisible content.",
     "outreach", "Normal"),
    ("evergreen-content-recycler",
     "Identify and recycle evergreen content: republish with updated hooks, share on social with fresh commentary, feature in email newsletters, and reintroduce to new audience segments that were not following when it first published.",
     "content", "Normal"),
    ("user-generated-content-amplifier",
     "Identify and amplify user-generated content: client testimonials shared on social, community members creating content about the agency, and positive mentions. Reshare with permission and gratitude.",
     "content", "Normal"),

    # ─── 13. BRAND VOICE & QUALITY ASSURANCE ─────────────────────────────
    ("brand-voice-guardian",
     "Guard Yasmine's brand voice across all content channels: confident but not arrogant, technical but accessible, opinionated but evidence-based, and warm but professional. The voice should be recognizable on any platform without seeing the author name.",
     "content", "High"),
    ("cross-channel-voice-adapter",
     "Adapt the brand voice per channel while maintaining core identity: sharper on X, more conversational on Facebook, more thorough on the blog, more direct in email, and more personable in video. Same person, different rooms.",
     "content", "High"),
    ("anti-ai-content-detector",
     "Screen all content for AI-generated tells before publishing: remove robotic phrasing, generic transitions, over-balanced perspectives, hedge words, and list-heavy structures. Add human imperfections, specific anecdotes, and conversational asides.",
     "content", "High"),
    ("fact-checker",
     "Fact-check all content before publishing: verify statistics, confirm claims, check that referenced tools and features are current, validate links, and ensure nothing outdated or incorrect reaches the audience. Credibility is fragile.",
     "content", "High"),
    ("plagiarism-checker",
     "Run plagiarism checks on all original content: ensure nothing inadvertently mirrors existing published content too closely. Originality is both an ethical requirement and an SEO factor.",
     "content", "Normal"),
    ("editorial-standards-enforcer",
     "Enforce editorial standards: grammar, style consistency (AP style or house style), formatting standards, image quality requirements, and CTA placement rules. Consistent quality builds professional credibility.",
     "content", "Normal"),
    ("content-legal-reviewer",
     "Review content for legal considerations: proper attribution for referenced data, no unsubstantiated claims about competitors, compliant use of client information, and appropriate disclaimers where needed.",
     "content", "Normal"),

    # ─── 14. CONTENT OPERATIONS ──────────────────────────────────────────
    ("content-production-pipeline-manager",
     "Manage the content production pipeline: ideation → outline → draft → edit → optimize → design → schedule → publish → promote → analyze. Track every piece through every stage.",
     "operations", "High"),
    ("editorial-calendar-maintainer",
     "Maintain the master editorial calendar: all channels, all content types, all stages, all deadlines, and all assignees. The single source of truth for what is publishing when and where.",
     "operations", "High"),
    ("content-asset-library-manager",
     "Maintain the content asset library: all published content indexed by topic, format, channel, and performance. All visual assets organized by type and brand element. All templates accessible and current.",
     "operations", "Normal"),
    ("content-workflow-optimizer",
     "Optimize the content production workflow: reduce time from idea to publish, eliminate bottlenecks, streamline review processes, and improve batch production efficiency.",
     "operations", "Normal"),
    ("content-tool-stack-manager",
     "Manage the content tool stack: writing tools, SEO tools (Ahrefs, SEMrush, Surfer SEO), scheduling tools (Buffer, Hootsuite, Later), design tools (Canva, Figma), analytics tools (Google Analytics, Search Console), and email platforms.",
     "operations", "Normal"),
    ("content-collaboration-coordinator",
     "Coordinate content collaboration with other agents: receive research from Research Analyst, receive client stories from Client Success, receive technical accuracy reviews from Lead Developer, and receive competitive intelligence from the LinkedIn Content Agent.",
     "operations", "Normal"),

    # ─── 15. CONTENT REPORTING & INTELLIGENCE ────────────────────────────
    ("weekly-content-performance-report",
     "Weekly report across all channels: publishing output vs. plan, engagement metrics, traffic trends, top-performing content, and conversion data. Include actionable insights, not just numbers.",
     "operations", "High"),
    ("monthly-content-analytics-report",
     "Monthly comprehensive analytics: channel-by-channel performance, content-to-lead pipeline, SEO ranking progress, audience growth, engagement trends, and content ROI assessment.",
     "operations", "Normal"),
    ("quarterly-content-strategy-review",
     "Quarterly strategic review: what themes resonated, which channels grew, where content drove business results, what the competitive content landscape looks like, and strategic adjustments for next quarter.",
     "operations", "Normal"),
    ("seo-ranking-tracker",
     "Track search rankings for all target keywords: current position, position change over time, estimated traffic from each ranking, and keywords approaching page 1 that need a final push.",
     "operations", "High"),
    ("content-attribution-report",
     "Monthly content attribution report: which content pieces influenced which leads, which blog posts were in the conversion path of closed deals, and what the full-funnel content contribution looks like.",
     "operations", "Normal"),
    ("audience-growth-report",
     "Track audience growth across all channels: blog subscriber growth, X follower growth, Facebook audience growth, email list growth, and YouTube subscriber growth (if applicable). Combined audience reach trend.",
     "operations", "Normal"),
    ("content-experiment-log",
     "Maintain a log of all content experiments: what was tested (format, topic, timing, channel), what the hypothesis was, what the result was, and what was learned. Build institutional knowledge of what works.",
     "operations", "Normal"),
    ("annual-content-review",
     "Annual comprehensive review: total content output, best-performing pieces, channel growth, SEO gains, content ROI, and content strategy evolution over the year. Set the direction for next year.",
     "operations", "Normal"),

    # ─── 16. AI-SPECIFIC CONTENT EXPERTISE ───────────────────────────────
    ("ai-topic-simplifier",
     "Translate complex AI concepts into content business owners can understand: no jargon without explanation, real-world analogies, practical examples, and what this means for your business framing. The gap between AI capability and business understanding is where the agency's content lives.",
     "content", "High"),
    ("ai-tool-review-writer",
     "Write in-depth AI tool reviews: hands-on evaluation, feature analysis, pricing breakdown, best use cases, limitations, and comparison with alternatives. Tool reviews attract high-intent traffic from people actively evaluating solutions.",
     "content", "High"),
    ("ai-trend-interpreter",
     "Interpret AI industry developments for a business audience: when OpenAI releases a new model, what does it mean for a business owner? When new regulations are proposed, how does it affect companies using AI? Translate tech news into business impact.",
     "content", "High"),
    ("ai-use-case-content-creator",
     "Create content around real-world AI use cases: how specific industries are using AI, what results they are getting, and what the implementation looked like. Use case content builds credibility and helps prospects envision AI in their own business.",
     "content", "High"),
    ("ai-myth-debunking-content",
     "Create content that debunks AI myths: AI will replace all jobs, AI is only for big companies, AI is too expensive, AI cannot be trusted. Evidence-based myth busting positions the agency as the credible, honest voice in a space full of hype.",
     "content", "High"),
    ("ai-implementation-educational-content",
     "Create educational content about the AI implementation process: what to expect, common pitfalls, realistic timelines, how to prepare, and what questions to ask a consultant. Content that educates prospects into confident buyers.",
     "content", "High"),
    ("prompt-engineering-content-creator",
     "Create tactical prompt engineering content: tips, templates, frameworks, and examples that readers can use immediately. High-value giveaway content that demonstrates deep expertise and drives email signups.",
     "content", "High"),
]


def build_record(skill_name, description, category, priority):
    return {
        "fields": {
            "Name": skill_name,
            "Description": description,
            "Target Agent": [{"id": HANA_RECORD_ID}],
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
    parser = argparse.ArgumentParser(description="Load Hana Content Specialist skills into Teable Skills Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print skills without inserting")
    args = parser.parse_args()

    print(f"\nHana Content Specialist Skills Loader")
    print(f"Total skills: {len(HANA_SKILLS)}")
    print(f"Table: {TABLE_ID}")
    print(f"Agent record: {HANA_RECORD_ID}")
    print("=" * 60)

    if args.dry_run:
        for i, (name, desc, cat, pri) in enumerate(HANA_SKILLS, 1):
            print(f"  [{i:3}] {name} | {cat} | {pri}")
        print(f"\n[DRY RUN] Would insert {len(HANA_SKILLS)} skills")
        return

    from extended import TeableExtendedClient
    client = TeableExtendedClient()

    records = [build_record(name, desc, cat, pri) for name, desc, cat, pri in HANA_SKILLS]

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
        print("All 140 Hana Content Specialist skills loaded successfully.")


if __name__ == "__main__":
    main()
