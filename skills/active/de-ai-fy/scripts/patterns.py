"""
patterns.py — AI Pattern Definitions for de-ai-fy

All regex patterns, word lists, and replacement maps used by the de-ai-fy engine.
"""

import re

# ─────────────────────────────────────────────
# TIER 1: HARD BANS — always replace
# ─────────────────────────────────────────────

TIER1_REPLACEMENTS = {
    # ── POETIC AI WORDS ──────────────────────────────
    r"\btapestry\b": "[REWRITE: say mix/blend/combination]",
    r"\bvibrant\b": "lively",
    r"\brealm\b": "area",
    r"\bin the realm of\b": "in",
    r"\bbeacon\b": "[REWRITE: say model/example/standard]",
    r"\bbustling\b": "busy",
    r"\bnestled\b": "[REWRITE: say sitting/located/tucked]",
    r"\blabyrinth(?:ine)?\b": "maze",
    r"\benigma\b": "mystery",
    r"\btapestry of\b": "mix of",
    r"\ba testament to\b": "proof of",
    r"\bshed light on\b": "explain",
    r"\bunpack\b(?!ing boxes|\s+the box)": "break down",
    r"\bharnessing\b": "using",
    r"\bharness the power of\b": "use",
    r"\bunleash\b": "release",
    r"\bunlock\b": "access",
    r"\belevate\b(?! to the position)": "improve",
    r"\bdaunting\b": "tough",
    r"\bever[- ]evolving\b": "changing",
    r"\bpivotal\b": "key",
    r"\bunderscores\b": "shows",
    r"\bunderscore\b": "show",
    r"\bshowcasing\b": "showing",
    r"\bshowcase\b": "show",
    r"\baligns with\b": "matches",
    r"\bnavigate\b(?!\s+to\s+[\w/])": "handle",
    r"\bnavigating\b": "handling",
    r"\bcomplexities\b": "details",
    r"\bintricacies\b": "details",
    r"\bintricate\b": "complex",
    r"\bunprecedented\b": "new",
    r"\baugment\b": "add to",
    r"\brendeavour\b": "effort",
    r"\bendeavor\b": "effort",
    r"\breimag(?:ine|ined|ining)\b": "[REWRITE: say rethink/redesign]",
    r"\bimpactful\b": "effective",
    r"\bspearhead\b": "lead",
    r"\bpave the way\b": "make it possible",
    r"\blocale\b": "area",
    r"\bnuanced\b": "subtle",
    r"\btreasure trove\b": "goldmine",
    r"\blandscape\b(?=\s+of|\s+in|s?\b)(?<!\bthe\s)": "field",

    # ── CORPORATE AI WORDS ───────────────────────────
    r"\bdelve into\b": "dig into",
    r"\bdelve\b": "dig",
    r"\butilize\b": "use",
    r"\butilizes\b": "uses",
    r"\butilized\b": "used",
    r"\butilizing\b": "using",
    r"\butilization\b": "use",
    r"\bsynergy\b": "[REWRITE: remove synergy]",
    r"\bsynergies\b": "[REWRITE: remove synergies]",
    r"\bholistic approach\b": "[REWRITE: name actual components]",
    r"\bparadigm shift\b": "major change",
    r"\bgame[- ]changer\b": "[REWRITE: say specifically why it matters]",
    r"\bgame[- ]changing\b": "[REWRITE: say what it changes]",
    r"\bmoving the needle\b": "making progress",
    r"\bdeep dive\b": "close look",
    r"\bcircle back\b": "follow up",
    r"\btouch base\b": "check in",
    r"\bbandwidth\b(?=.*(?:time|capacity|availability|team))": "capacity",
    r"\bvalue[- ]add\b": "benefit",
    r"\bactionable insights\b": "useful findings",
    r"\bactionable\b": "practical",
    r"\bseamless(?:ly)?\b": "[REWRITE: say what's actually smooth]",
    r"\brobust\b": "solid",
    r"\bcutting[- ]edge\b": "latest",
    r"\bstate[- ]of[- ]the[- ]art\b": "latest",
    r"\bpain points\b": "problems",
    r"\bpain point\b": "problem",
    r"\blow[- ]hanging fruit\b": "easy wins",
    r"\bthink outside the box\b": "think creatively",
    r"\bbest practices\b": "what works",
    r"\bstreamline\b": "simplify",
    r"\boptimize\b": "improve",
    r"\benhance\b(?!\s+your\s+(?:image|reputation))": "improve",
    r"\bstakeholders\b": "[REWRITE: name who — team/investors/customers]",
    r"\bdeliverables\b": "output",
    r"\bsynergize\b": "[REWRITE: say work together]",
    r"\bpropel\b": "drive",
    r"\bamplify\b(?!\s+(?:the signal|the audio|the sound))": "boost",
    r"\bdemonstrate\b": "show",
    r"\brussell\b": "work",
    r"\bequip\b(?=\s+(?:you|us|them|teams?)\s+with)": "give",

    # ── STARTUP / STRATEGY JARGON ────────────────────
    r"\bdemocratize[sd]?\b": "[REWRITE: say who gets access and how]",
    r"\bdemocratizing\b": "[REWRITE: same]",
    r"\bflywheel\b": "[REWRITE: say what drives what]",
    r"\binflection point\b": "turning point",
    r"\bnorth star\b(?=\s+(?:metric|goal|vision|value))": "main goal",
    r"\blean into\b": "commit to",
    r"\bdouble down\b": "double down",   # keep — it's actually human sometimes; score.py handles freq
    r"\btable stakes\b": "the minimum",
    r"\bvalue proposition\b": "[REWRITE: say what the actual value is]",
    r"\bbespoke\b": "custom",
    r"\bcurated\b(?!\s+(?:list of|selection of|collection of)\s+\w+\b(?!\s+(?:just|only|by)))": "selected",
    r"\bcuration\b": "selection",
    r"\bevangelize\b": "[REWRITE: say promote/champion/spread the word about]",
    r"\bevangeli(?:st|zing|zed)\b": "[REWRITE: same]",
    r"\bsocialize\b(?=\s+(?:the|this|that|an|a)\s+(?:idea|concept|plan|proposal))": "share",
    r"\bwhitespace\b(?=\s+(?:in|for|within|opportunity))": "gap",
    r"\bmission[- ]critical\b": "essential",
    r"\bbusiness[- ]critical\b": "essential",
    r"\bgo[- ]to[- ]market\b": "launch",
    r"\bgrowth mindset\b": "[REWRITE: say what learning behavior you mean]",
    r"\bfail fast\b": "[REWRITE: say test early and fix quickly]",
    r"\bstep[- ]change\b": "major shift",
    r"\bmission[- ]driven\b": "[REWRITE: say what the mission is]",
    r"\bpurpose[- ]driven\b": "[REWRITE: say what the purpose is]",
    r"\bdata[- ]driven\b": "[REWRITE: say what data is guiding the decision]",
    r"\bimpact[- ]driven\b": "[REWRITE: same for impact]",
    r"\bcommunity[- ]driven\b": "[REWRITE: say how the community shapes it]",
    r"\bon[- ]brand\b": "consistent with our voice",
    r"\btailor[- ]made\b": "custom",
    r"\bcore competenc(?:y|ies)\b": "strengths",
    r"\bat a high level[,]?\s*": "",
    r"\bdrill down\b": "dig into",
    r"\bpeel back\b(?=\s+(?:the|that|this|a))": "look closer at",
    r"\bboil the ocean\b": "do everything at once",
    r"\bno[- ]brainer\b": "obvious choice",
    r"\bnet net\b[,]?\s*": "",
    r"\b10x\b(?=\s+(?:your|our|the|growth|revenue|results|impact))": "[REWRITE: give the actual target]",
    r"\bmore (?:important|relevant|critical|urgent) than ever\b": "[REWRITE: say why it matters now]",
    r"\bnow more than ever[,]?\s*": "",
    r"\bnever been more (?:important|critical|relevant|necessary|urgent)\b": "[REWRITE: say why now]",

    # ── GPTZero STATISTICAL HARD-BANS ────────────────
    r"\bplay a significant role in shaping\b": "[REWRITE: say exactly what role]",
    r"\bplay(?:s|ed)? a (?:significant|key|crucial|important|pivotal) role in\b": "[REWRITE: say what it does]",
    r"\baims to explore\b": "explores",
    r"\bnotable works include\b": "key works include",

    # ── GRAMMAR AI CONSTRUCTIONS ──────────────────────
    r"\bnot only\b(.{1,60})\bbut also\b": r"[REWRITE: collapse to one claim — \1]",
    r"\bit is (?:essential|crucial|vital|important|necessary) that\s*": "",
    r"\bit is (?:worth noting|worth mentioning) that\s*": "",
    r"\bit is clear that\s*": "",
    r"\bit is evident that\s*": "",

    # ── FILLER SETUPS ────────────────────────────────
    r"\bat the end of the day[,]?\s*": "",
    r"\bgoing forward[,]?\s*": "",
    r"\bmoving forward[,]?\s*": "",
    r"\bit'?s worth noting that\s*": "",
    r"\bit is worth noting that\s*": "",
    r"\bit'?s important to note that\s*": "",
    r"\bit is important to note that\s*": "",
    r"\bit'?s important to remember that\s*": "",
    r"\bit'?s crucial to (?:recognize|understand|note) that\s*": "",
    r"\bit is crucial to (?:recognize|understand) that\s*": "",
    r"\bit should be noted that\s*": "",
    r"\bit'?s essential to consider that\s*": "",
    r"\bit goes without saying that\s*": "",
    r"\bneedless to say[,]?\s*": "",
    r"\bas previously mentioned[,]?\s*": "",
    r"\bas we can see[,]?\s*": "",
    r"\bin conclusion[,]?\s*": "",
    r"\bto summarize[,]?\s*": "",
    r"\bin summary[,]?\s*": "",
    r"\ball things considered[,]?\s*": "",
    r"\blast but not least[,]?\s*": "",
    r"\bfirst and foremost[,]?\s*": "first, ",
    r"\bin order to\b": "to",
    r"\bdue to the fact that\b": "because",
    r"\bin the event that\b": "if",
    r"\bat this point in time\b": "now",
    r"\bon a regular basis\b": "regularly",
    r"\bthat being said[,]?\s*": "",
    r"\bhaving said that[,]?\s*": "",
    r"\bwith that in mind[,]?\s*": "",
    r"\bwithout further ado[,]?\s*": "",
    r"\bat this juncture[,]?\s*": "",
    r"\bin terms of\b": "for",
    r"\bwith regard to\b": "about",
    r"\bin essence[,]?\s*": "",
    r"\bto put it simply[,]?\s*": "",
    r"\bin today's .{0,50} landscape\b": "[REWRITE: cut opener, start with the point]",
    r"\bin today's (?:digital|fast-paced|modern|competitive|rapidly evolving) (?:age|world|era)[,]?\s*": "[REWRITE: cut opener] ",
    r"\bin today's .{0,20} world[,]?\s*": "[REWRITE: cut opener] ",
    r"\bas we navigate\b": "[REWRITE: cut] ",
    r"\bnow more than ever[,]?\s*": "",
    r"\bwhen it comes to\b": "for",
    r"\bgiven the fact that\b": "because",
    r"\bbearing in mind that\b": "",

    # ── LEVERAGE / EMPOWER / FOSTER FAMILY ──────────
    r"\bleverage\b(?=\s+(?:the|this|these|our|your|a|an))": "use",
    r"\bleverages\b": "uses",
    r"\bleveraged\b": "used",
    r"\bleveraging\b": "using",
    r"\bempower\b": "give",
    r"\bempowers\b": "gives",
    r"\bempowered\b": "",
    r"\bempowering\b": "giving",
    r"\bfoster\b": "build",
    r"\bfosters\b": "builds",
    r"\bfostered\b": "built",
    r"\bfostering\b": "building",
    r"\bcultivate\b(?!.*(?:crop|plant|garden|soil|farm))": "develop",
    r"\bcultivates\b": "develops",
    r"\bcultivated\b": "developed",
    r"\bcultivating\b": "developing",
    r"\bfacilitate\b": "help",
    r"\bfacilitates\b": "helps",
    r"\bfacilitated\b": "helped",
    r"\bfacilitating\b": "helping",
    r"\bparadigm\b": "model",
    r"\bgame[- ]changing\b": "[REWRITE: say what changed]",
    r"\btransformative\b": "[REWRITE: say what it transforms]",
    r"\bdisruptive\b(?!.*(?:technology context))": "[REWRITE: say what it disrupts]",
    r"\binnovative\b": "[REWRITE: say what the innovation is]",
    r"\bscalable\b": "can grow",
    r"\bcomprehensive\b": "thorough",
    r"\bholistic\b": "full",
    r"\bproactive\b": "ahead of time",
    r"\bfirstly\b": "first",
    r"\bsecondly\b": "second",
    r"\bthirdly\b": "third",
    r"\brevolutionize\b": "[REWRITE: say what changes and how]",
    r"\bimpacting\b(?=\s+(?:the|our|their|a|an))": "affecting",
    r"\bimpact\b(?=s?\s+(?:the|our|their|a|an))": "affect",
    r"\bsignificantly\b": "significantly",   # frequency-flagged — let score.py handle

    # ── MISSING CORPORATE/BUZZWORD AI WORDS ──────────
    r"\bresonate[sd]?\b(?=\s+with\b)": "connect",
    r"\bresonate[sd]?\b": "connect",
    r"\bplethora\b": "a lot",
    r"\bmyriad\b": "many",
    r"\blearnings\b": "lessons",
    r"\bthought leadership\b": "[REWRITE: say what the actual idea is]",
    r"\bgroundbreaking\b": "[REWRITE: say what it breaks]",
    r"\boverarching\b": "main",
    r"\bsalient\b": "key",
    r"\bmultifaceted\b": "complex",
    r"\bnoteworthy\b": "worth noting",
    r"\balignment\b(?=\s+(?:on|with|between|around|across))": "agreement",
    r"\bcadence\b(?=\s+(?:of|for|with|in))": "rhythm",
    r"\bcross[- ]functional\b": "cross-team",
    r"\bideation\b": "brainstorming",
    r"\bgranular\b": "detailed",
    r"\bpivot\b(?=(?:ed|ing|s)?\s+(?:to|away|from|toward))": "shift",
    r"\btraction\b(?=\s+(?:in|with|among|on))": "momentum",
    r"\bscale\b(?=\s+(?:this|it|up|our|the))": "grow",
    r"\bbuy[- ]in\b": "support",
    r"\btouchpoints?\b": "contact points",
    r"\biterat(?:e|ed|ing|ion)\b(?=\s+(?:on|over|through|quickly|fast))": "[REWRITE: say refine/improve/repeat]",
    r"\bforward[- ]thinking\b": "practical",
    r"\bfuture[- ]proof\b": "[REWRITE: say built for change or durable]",
    r"\bworld[- ]class\b": "[REWRITE: say what makes it exceptional]",
    r"\bbest[- ]in[- ]class\b": "[REWRITE: say what makes it the best]",
    r"\bindustry[- ]leading\b": "[REWRITE: say what leads it]",
    r"\btruly\b": "",
    r"\bsimply put[,]?\s*": "",
    r"\bat its core[,]?\s*": "",
    r"\bmeticulous(?:ly)?\b": "careful",
    r"\bembark(?:ed|ing)? on\b": "start",
    r"\bpara(?:mount|graph)\b(?=.*(?:important|crucial|essential))": "essential",
}

# ─────────────────────────────────────────────
# LINKEDIN-SPECIFIC AI PATTERNS
# ─────────────────────────────────────────────

LINKEDIN_PATTERNS = [
    # ── ANNOUNCEMENT OPENERS ──────────────────────────
    (r"^I'?m (?:thrilled|excited|delighted|honored|humbled) to (?:announce|share|present)\b", "[REWRITE: just announce it]"),
    (r"\bI'?m (?:thrilled|excited|delighted|honored|humbled) to (?:announce|share)\b", "[REWRITE: just announce it]"),
    (r"\bhumbled and honored\b", "[REWRITE: just say what happened]"),
    (r"\bhonored and humbled\b", "[REWRITE: same]"),
    (r"\bI had the privilege of\b", "I"),
    (r"\bwhat (?:an|a) incredible journey (?:it'?s been|this has been)\b", "[REWRITE: say what actually happened]"),
    (r"\bit'?s been an incredible journey\b", "[REWRITE: say what happened]"),
    (r"\bwhat a journey it'?s been\b", "[REWRITE: same]"),
    (r"\bgrateful for this (?:incredible |amazing )?opportunity\b", "[REWRITE: say what you're grateful for specifically or cut]"),
    # ── "HERE'S" SETUPS ───────────────────────────────
    (r"\bhere'?s what I (?:learned|discovered|realized|know)(?:\s+for sure)?:\s*$", "[REWRITE: write in prose]"),
    (r"\bhere'?s what I (?:learned|discovered|realized|know)(?:\s+for sure)?:\s*", ""),
    (r"\bhere'?s the (?:thing|kicker|truth|reality|deal):\s*", ""),
    (r"\bhere'?s what most people miss:\s*", ""),
    (r"\bhere'?s what (?:they|nobody) (?:won'?t tell you|don'?t tell you|never told me):\s*", ""),
    (r"\band here'?s the part most people miss:\s*", ""),
    (r"\bhere'?s the truth nobody talks about:\s*", ""),
    (r"\blet me be real with you:\s*", ""),
    (r"\bi'?ll be honest:\s*", ""),
    (r"\btrue story:\s*", ""),
    (r"\breal talk:\s*", ""),
    # ── OPINION LABELS ────────────────────────────────
    (r"\bunpopular opinion:\s*", ""),
    (r"\bhot take:\s*", ""),
    (r"\bcontroversial (?:take|opinion):\s*", ""),
    (r"\bpsa:\s*", ""),
    (r"\breminder that:\s*", ""),
    (r"\bgenuine question:\s*", ""),
    (r"\bnot sure if this is a hot take (?:but)?:\s*", ""),
    # ── AI STORY LABELS ───────────────────────────────
    (r"\bwhat most people don'?t realize\b", ""),
    (r"\bwhat nobody tells you about\b", "what you need to know about"),
    (r"\bwhat they don'?t teach you\b", ""),
    (r"\bmost people get (?:this )?wrong\b", ""),
    (r"\bthis (?:is the )?#?1 (?:thing|reason|mistake)\b", "[REWRITE: say the thing directly]"),
    (r"\bif I could tell my younger self\b", "[REWRITE: say the lesson directly]"),
    (r"\bthe secret to .{1,40} is\b", "[REWRITE: say what it is directly]"),
    (r"\bI used to think .{1,60}\. I was wrong\b", "[REWRITE: say what you think now]"),
    (r"\bstop doing .{1,40}\. start doing\b", "[REWRITE: make the case with specifics]"),
    # ── ENGAGEMENT BAIT ───────────────────────────────
    (r"\bdrop a .{1,10} (?:in|below) (?:the )?comments?\b.*$", "[CUT: engagement beg]"),
    (r"\bdrop a .{1,10} if (?:you agree|this resonated|this helped|this spoke to you)\b.*$", "[CUT]"),
    (r"\bif this resonated[,.]?\s*$", ""),
    (r"\bwhat do you think\??\s*(?:drop|leave|let me know in)(?: a)? (?:comment|thoughts?)?\b.*$", "[CUT or ask specific question]"),
    (r"\brepost (?:this )?if (?:this )?resonated\b.*$", ""),
    (r"\bshare this with someone who needs (?:to hear )?this\b.*$", ""),
    (r"\bfollow me for more (?:content|posts|tips|insights)\b.*$", ""),
    (r"\blike and follow for more\b.*$", ""),
    (r"\bagree(?: or disagree)?\?+\s*$", ""),
    (r"\bdisagree\? (?:let me know|drop a comment)\b.*$", ""),
    (r"\bsave this (?:post |for later)?\b.*$", ""),
    (r"\bbookmark this\b.*$", ""),
    (r"\bam I the only one who thinks this\?\s*$", ""),
    (r"\bwhat'?s your (?:take|experience|thought) on this\?\s*$", ""),
    (r"\bthoughts\?\s*$", ""),
    (r"\bthis is your sign to\b", ""),
    (r"\btag someone who needs (?:to see |to hear )?this\b.*$", ""),
    # ── CLOSING PATTERNS ──────────────────────────────
    (r"\bmoving forward[,]? (?:I|we|our team) (?:remain|are) committed to\b", "[REWRITE: say what you're actually doing next]"),
    (r"\bI'?m (?:excited|thrilled) for what'?s to come\b", "[REWRITE: say what's actually coming or cut]"),
    (r"\bthe best is yet to come\b", "[CUT]"),
    (r"\bwatch this space\b", "[CUT or say what to watch for]"),
    (r"\bstay tuned\b", "[CUT]"),
    # ── HASHTAG BLOCKS (3+ consecutive hashtags) ──────
    (r"(\s#\w+){4,}\s*$", " [CUT: hashtag block]"),
]

# ─────────────────────────────────────────────
# EMAIL-SPECIFIC AI PATTERNS
# ─────────────────────────────────────────────

EMAIL_OPENERS = [
    (r"^I hope this (?:email|message) finds you well[.,]?\s*", ""),
    (r"^I hope you(?:'re| are) doing well[.,]?\s*", ""),
    (r"^I hope you(?:'re| are) having a (?:great|wonderful|good) (?:week|day|morning)[.,]?\s*", ""),
    (r"^I hope (?:all is|everything is) well (?:on your end|with you)[.,]?\s*", ""),
    (r"^I trust this (?:email|message) finds you (?:well|in good health)[.,]?\s*", ""),
    (r"^I wanted to reach out(?:\s+to\s+\w+)?\b", "[REWRITE: start with the reason]"),
    (r"^I'?m reaching out today to\b", "[REWRITE: start with the reason]"),
    (r"^I'?m reaching out because\b", ""),
    (r"^I am writing to (?:inform|let you know|confirm|clarify)\b", "[REWRITE: start with the information]"),
    (r"^I wanted to (?:follow up on|touch base (?:regarding|about))\b", "Following up:"),
    (r"^Further to (?:my previous email|our (?:conversation|discussion|call))\b", "Following up:"),
    (r"^Please allow me to introduce myself\b", "[REWRITE: just introduce yourself]"),
    (r"^By way of introduction\b", "[REWRITE: just introduce yourself]"),
    (r"^Thank you for taking the time to\b", "[REWRITE: cut opener, express thanks at end if needed]"),
    (r"^First and foremost[,]? thank you for\b", "[CUT opener]"),
]

EMAIL_BODY = [
    (r"\bplease be (?:advised|informed|aware) that\s*", ""),
    (r"\bplease note that\s*", "Note: "),
    (r"\bI would (?:like to |just )?bring (?:this |it )?to your attention\b", ""),
    (r"\bit has come to my attention that\b", "I noticed that"),
    (r"\bI am (?:pleased|delighted) to inform you that\b", ""),
    (r"\bas per (?:our|my) (?:discussion|conversation|call|previous email|last email)\b", "As we discussed,"),
    (r"\bas previously (?:discussed|agreed|mentioned)\b", "As discussed,"),
    (r"\bpursuant to (?:our agreement|your request)\b", "Per our agreement,"),
    (r"\bwith (?:regard|reference|respect) to\b", "About"),
    (r"\bregarding the matter of\b", "About"),
    (r"\bkindly (?:note|be advised|find|review|confirm)\b", "Please"),
    (r"\bdo not hesitate to (?:contact|reach out|ask)\b", ""),
    (r"\bshould you (?:have|require) any (?:further |additional )?(?:questions|information)\b", ""),
    (r"\bI would be (?:grateful|appreciative) if you could\b", "Could you"),
    (r"\bit would be (?:greatly |much )?appreciated if\b", "Could you please"),
    (r"\bI would like to take this opportunity to\b", ""),
    (r"\bat your earliest convenience\b", "when you get a chance"),
    (r"\bplease find (?:attached|enclosed)\b", "Attached:"),
]

EMAIL_CLOSERS = [
    (r"\s*I hope this (?:helps?|clarifies?|provides? (?:the information|clarity))[.!]?\s*$", ""),
    (r"\s*I trust this (?:is satisfactory|has been helpful|response has been helpful)[.!]?\s*$", ""),
    (r"\s*I hope this (?:is helpful|helps clarify things)[.!]?\s*$", ""),
    (r"\s*Please don'?t hesitate to (?:contact|reach out|ask)[.!]?\s*$", ""),
    (r"\s*Feel free to (?:reach out|contact me|ask) if you have any (?:questions|concerns)[.!]?\s*$", ""),
    (r"\s*Should you (?:have|require) any (?:further )?(?:questions|information)[^.]*[.!]?\s*$", ""),
    (r"\s*I (?:look forward to|am looking forward to) hearing from you[.!]?\s*$", ""),
    (r"\s*I (?:look forward to|am looking forward to) your (?:response|reply|feedback)[.!]?\s*$", ""),
    (r"\s*I remain at your (?:disposal|service)(?: for any (?:further )?(?:inquiries|questions))?[.!]?\s*$", ""),
    (r"\s*Thank you for your (?:time and consideration|continued support|business)[.!]?\s*$", ""),
    (r"\s*It has been a pleasure (?:assisting|helping) you(?: today)?[.!]?\s*$", ""),
    (r"\s*(?:Have a )?(?:wonderful|great|fantastic|nice) (?:day|rest of your week|weekend)[.!]?\s*$", ""),
    (r"\s*Wishing you all the best[.!]?\s*$", ""),
]

# ─────────────────────────────────────────────
# TWITTER/X-SPECIFIC AI PATTERNS
# ─────────────────────────────────────────────

TWITTER_PATTERNS = [
    (r"^🧵\s*(?:A thread on|Thread:)\s*", ""),
    (r"^(?:thread|a thread)[:\s]*\n", ""),
    (r"\bThat'?s it[.!] (?:Follow|RT|Retweet|Like)\b.*$", ""),
    (r"\bIf you found this (?:useful|helpful|valuable)[,]? (?:please )?(?:RT|retweet)\b.*$", ""),
    (r"^(?:Hot|Unpopular|Controversial|Spicy) (?:take|opinion)[:\s]*", ""),
    (r"^PSA[:\s]*", ""),
    (r"^Reminder that[:\s]*", ""),
    (r"^Genuine question[:\s]*", ""),
    (r"\bWhat would you add\?\s*$", ""),
    (r"\bAnything I missed\?\s*$", ""),
    (r"\b\(thread\)\s*$", ""),
    (r"\bI don'?t usually (?:post|tweet) about .{1,40}[,]? but\b", ""),
    (r"\bSharing this because everyone needs to see it\b", ""),
    (r"\bThis is everything\.\s*$", ""),
    (r"^This\.\s*$", ""),
    (r"\bRT if you agree\b.*$", ""),
    (r"\bLike if you agree\b.*$", ""),
]

# ─────────────────────────────────────────────
# TIER 2: TRANSITION OPENERS TO KILL/REDUCE
# ─────────────────────────────────────────────

TRANSITION_OPENERS = [
    (r"^Furthermore[,]?\s+", ""),
    (r"^Additionally[,]?\s+", ""),
    (r"^Moreover[,]?\s+", ""),
    (r"^In addition[,]?\s+", ""),
    (r"^Nevertheless[,]?\s+", "But "),
    (r"^Nonetheless[,]?\s+", "Still, "),
    (r"^Consequently[,]?\s+", "So "),
    (r"^Subsequently[,]?\s+", "Then "),
    (r"^Therefore[,]?\s+", "So "),
    (r"^Thus[,]?\s+", "So "),
    (r"^Hence[,]?\s+", ""),
    (r"^Indeed[,]?\s+", ""),
    (r"^Certainly[,]?\s+", ""),
    (r"^Undoubtedly[,]?\s+", ""),
    (r"^Importantly[,]?\s+", ""),
    (r"^Interestingly[,]?\s+", ""),
    (r"^Notably[,]?\s+", ""),
    (r"^Essentially[,]?\s+", "Basically, "),
    (r"^Fundamentally[,]?\s+", ""),
    (r"^Remarkably[,]?\s+", ""),
    (r"^Evidently[,]?\s+", ""),
    (r"^Accordingly[,]?\s+", "So, "),
    (r"^Alternatively[,]?\s+", "Or, "),
    (r"^Specifically[,]?\s+", ""),
]

# ─────────────────────────────────────────────
# COMPLIMENT/HOLLOW OPENERS (for chat contexts)
# ─────────────────────────────────────────────

HOLLOW_OPENERS = [
    r"^(Great|Excellent|Wonderful|Fantastic|Perfect|Amazing) (question|point|observation|idea)[!.]?\s*",
    r"^That'?s? (a )?(great|excellent|wonderful|fantastic|interesting|insightful) (question|point|observation)[!.]?\s*",
    r"^Absolutely[!.]?\s*",
    r"^Certainly[!.]?\s*",
    r"^Of course[!.]?\s*",
    r"^I'?d? be happy to (help|assist)(?: with that)?[!.]?\s*",
]

# ─────────────────────────────────────────────
# HOLLOW CLOSERS
# ─────────────────────────────────────────────

HOLLOW_CLOSERS = [
    r"\s*I hope this (helps|clarifies|provides clarity|has been helpful)[!.]?\s*$",
    r"\s*Feel free to (reach out|ask|contact me) if (you have|there are) (any )?(questions|concerns)[!.]?\s*$",
    r"\s*Please don'?t hesitate to (reach out|contact me|ask)[!.]?\s*$",
    r"\s*I look forward to (hearing from you|your (response|feedback|thoughts))[!.]?\s*$",
    r"\s*Let me know if (you have|there are) (any )?questions[!.]?\s*$",
    r"\s*I (trust|hope) this (response|answer|explanation) has been (helpful|useful|informative)[!.]?\s*$",
    r"\s*It has been (a pleasure|my pleasure) (assisting|helping) you (today)?[!.]?\s*$",
    r"\s*Have (a )?(great|wonderful|fantastic|nice) day[!.]?\s*$",
]

# ─────────────────────────────────────────────
# SETUP PHRASES (mid-text)
# ─────────────────────────────────────────────

SETUP_PHRASES = [
    (r"[Ii]t'?s important to (note|understand|recognize) that ", ""),
    (r"[Ii]t'?s worth (noting|mentioning|considering|highlighting) that ", ""),
    (r"[Ii]t should be noted that ", ""),
    (r"[Ii]t'?s crucial to (note|understand|recognize) that ", ""),
    (r"[Ww]ith (that|this) in mind[,]? ", ""),
    (r"[Tt]hat being said[,]? ", ""),
    (r"[Hh]aving said that[,]? ", ""),
    (r"[Ww]ithout further ado[,]? ", ""),
    (r"[Aa]t this juncture[,]? ", ""),
    (r"[Nn]ow[,]? let'?s (explore|dive into|examine|look at|discuss) ", ""),
    (r"[Ll]et'?s take a closer look at ", ""),
    (r"[Aa]s we can see from the above[,]? ", ""),
    (r"[Ii]n (the )?(following|next) section[s]?[,]? (we will|I will|we'll|I'll) ", ""),
]

# ─────────────────────────────────────────────
# PASSIVE VOICE PATTERNS (detection only)
# ─────────────────────────────────────────────

PASSIVE_PATTERNS = [
    r"\bis (being )?(?:done|made|used|implemented|created|built|designed|considered|found|seen|noted|reviewed|analyzed|evaluated|determined|recommended|suggested|required|needed|provided|given|shown|demonstrated|established|developed|improved|enhanced|increased|reduced|managed|handled|addressed|resolved|identified|described|defined|explained|outlined|discussed|presented|included|excluded|applied|generated|processed|stored|retrieved|updated|deleted|removed|added|placed|set|kept|left|taken|brought|sent|received|received|written|read|heard|understood|known|thought|believed|expected|wanted|needed|used|seen|found|made|done|given|taken|shown|told|known|called|named|considered|regarded|viewed)\b",
    r"\bwas (?:being )?(?:done|made|created|built|designed|found|noted|considered|determined|recommended|required|provided|shown|established|developed|implemented|managed|addressed|identified|described|explained|discussed|presented)\b",
    r"\bwere (?:being )?(?:done|made|created|built|designed|found|noted|considered|determined|recommended|required|provided|shown|established|developed|implemented|managed|addressed|identified|described|explained|discussed|presented)\b",
    r"\bhas been (?:done|made|created|built|designed|found|established|implemented|developed|improved|enhanced|completed|finalized|approved|reviewed|analyzed)\b",
    r"\bhave been (?:done|made|created|built|designed|found|established|implemented|developed|improved|enhanced|completed|finalized|approved|reviewed|analyzed)\b",
    r"\bcan be (?:accomplished|achieved|done|completed|implemented|used|applied|seen|found|considered|noted)\b",
    r"\bshould be (?:noted|considered|used|implemented|done|applied|reviewed|analyzed|evaluated)\b",
    r"\bit is (?:recommended|suggested|noted|important|worth) (that )?\b",
]

# ─────────────────────────────────────────────
# CONTRACTION EXPANSIONS → CONTRACTIONS
# ─────────────────────────────────────────────

CONTRACTIONS = [
    (r"\bit is\b(?! not\b)", "it's"),
    (r"\bIt is\b(?! not\b)", "It's"),
    (r"\bthey are\b", "they're"),
    (r"\bThey are\b", "They're"),
    (r"\bdo not\b", "don't"),
    (r"\bDo not\b", "Don't"),
    (r"\bcannot\b", "can't"),
    (r"\bCannot\b", "Can't"),
    (r"\bwill not\b", "won't"),
    (r"\bWill not\b", "Won't"),
    (r"\bshould not\b", "shouldn't"),
    (r"\bShould not\b", "Shouldn't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bDoes not\b", "Doesn't"),
    (r"\bare not\b", "aren't"),
    (r"\bAre not\b", "Aren't"),
    (r"\bis not\b", "isn't"),
    (r"\bIs not\b", "Isn't"),
    (r"\bhave not\b", "haven't"),
    (r"\bHave not\b", "Haven't"),
    (r"\bhas not\b", "hasn't"),
    (r"\bHas not\b", "Hasn't"),
    (r"\bwould not\b", "wouldn't"),
    (r"\bWould not\b", "Wouldn't"),
    (r"\bcould not\b", "couldn't"),
    (r"\bCould not\b", "Couldn't"),
    (r"\bI am\b", "I'm"),
    (r"\bwe are\b", "we're"),
    (r"\bWe are\b", "We're"),
    (r"\byou are\b", "you're"),
    (r"\bYou are\b", "You're"),
    (r"\bthat is\b", "that's"),
    (r"\bThat is\b", "That's"),
    (r"\bthere is\b", "there's"),
    (r"\bThere is\b", "There's"),
    (r"\bhere is\b", "here's"),
    (r"\bHere is\b", "Here's"),
    (r"\bwhat is\b", "what's"),
    (r"\bWhat is\b", "What's"),
]

# ─────────────────────────────────────────────
# EM-DASH OVERUSE DETECTION
# ─────────────────────────────────────────────

EM_DASH_PATTERN = r"—"
EM_DASH_THRESHOLD = 3  # per 500 words

# ─────────────────────────────────────────────
# SENTENCE LENGTH ANALYSIS
# ─────────────────────────────────────────────

def get_sentence_lengths(text):
    """Return list of word counts per sentence."""
    sentences = re.split(r'[.!?]+', text)
    return [len(s.split()) for s in sentences if len(s.split()) > 2]


def sentence_length_variance(lengths):
    """Calculate variance in sentence lengths."""
    if not lengths:
        return 0
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    return variance


def has_low_variance(text, threshold=20):
    """Return True if sentence lengths have suspiciously low variance (AI indicator)."""
    lengths = get_sentence_lengths(text)
    if len(lengths) < 5:
        return False
    return sentence_length_variance(lengths) < threshold

# ─────────────────────────────────────────────
# CONTRACTION COUNT
# ─────────────────────────────────────────────

CONTRACTION_PATTERNS = [
    r"\b\w+'(t|s|re|ve|ll|d|m)\b",
    r"\b(I'm|you're|he's|she's|it's|we're|they're|I've|you've|we've|they've)\b",
    r"\b(I'll|you'll|he'll|she'll|we'll|they'll|I'd|you'd|he'd|she'd|we'd|they'd)\b",
    r"\b(can't|won't|don't|doesn't|didn't|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|wouldn't|couldn't|shouldn't)\b",
]


def count_contractions(text):
    """Count contractions in text."""
    count = 0
    for pattern in CONTRACTION_PATTERNS:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def word_count(text):
    """Simple word count."""
    return len(text.split())
