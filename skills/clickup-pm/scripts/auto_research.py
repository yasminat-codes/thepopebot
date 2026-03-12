#!/usr/bin/env python3
"""
Automated research script - performs actual research using multiple APIs
and creates Google Docs with findings.

APIs Used:
- Perplexity (AI-synthesized answers)
- Brave Search (web results)
- Exa (neural search)
- Tavily (AI research)
- SERP API (Google results)
- Reddit (community insights)

Usage:
    python auto_research.py "dental practices" --type niche
    python auto_research.py "AI automation agencies" --type market
    python auto_research.py "VP of Marketing" --type persona
    python auto_research.py "SaaS founders" --type campaign
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Optional

# API Keys
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "")

# Skill paths
PERPLEXITY_SCRIPT = Path("/home/clawdbot/clawd/skills/perplexity/scripts/search.mjs")
BRAVE_SCRIPT = Path("/home/clawdbot/clawd/skills/brave-search/search.js")
EXA_SCRIPT = Path("/home/clawdbot/clawd/skills/exa/scripts/search.sh")
REDDIT_SCRIPT = Path("/home/clawdbot/clawd/skills/reddit/scripts/reddit.mjs")

def run_command(cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run shell command with timeout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"

def search_perplexity(query: str) -> dict:
    """Search using Perplexity API."""
    if not PERPLEXITY_SCRIPT.exists():
        return {"error": "Perplexity script not found"}
    
    cmd = f'node {PERPLEXITY_SCRIPT} "{query}"'
    code, stdout, stderr = run_command(cmd, timeout=30)
    
    if code != 0:
        return {"error": stderr or "Search failed"}
    
    return {"query": query, "result": stdout.strip(), "source": "perplexity"}

def search_brave(query: str) -> dict:
    """Search using Brave Search API."""
    if not BRAVE_SCRIPT.exists():
        return {"error": "Brave script not found"}
    
    cmd = f'{BRAVE_SCRIPT} "{query}" -n 5'
    code, stdout, stderr = run_command(cmd, timeout=30)
    
    if code != 0:
        return {"error": stderr or "Search failed"}
    
    return {"query": query, "result": stdout.strip(), "source": "brave"}

def search_exa(query: str) -> dict:
    """Search using Exa neural search."""
    if not EXA_SCRIPT.exists():
        return {"error": "Exa script not found"}
    
    cmd = f'bash {EXA_SCRIPT} "{query}" 5'
    code, stdout, stderr = run_command(cmd, timeout=30)
    
    if code != 0:
        return {"error": stderr or "Search failed"}
    
    return {"query": query, "result": stdout.strip(), "source": "exa"}

def search_tavily(query: str) -> dict:
    """Search using Tavily AI research API."""
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY not set"}
    
    try:
        url = "https://api.tavily.com/search"
        data = json.dumps({
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": 5
        }).encode()
        
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            
            # Format output
            output = []
            if result.get("answer"):
                output.append(f"**AI Answer:** {result['answer']}\n")
            
            for item in result.get("results", [])[:5]:
                output.append(f"- [{item.get('title', 'No title')}]({item.get('url', '')})")
                if item.get("content"):
                    output.append(f"  {item['content'][:200]}...")
            
            return {"query": query, "result": "\n".join(output), "source": "tavily"}
    except Exception as e:
        return {"error": str(e)}

def search_serpapi(query: str) -> dict:
    """Search using SERP API (Google results)."""
    if not SERPAPI_API_KEY:
        return {"error": "SERPAPI_API_KEY not set"}
    
    try:
        params = urllib.parse.urlencode({
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "engine": "google",
            "num": 5
        })
        url = f"https://serpapi.com/search?{params}"
        
        with urllib.request.urlopen(url, timeout=30) as response:
            result = json.loads(response.read().decode())
            
            output = []
            
            # Answer box if available
            if result.get("answer_box"):
                ab = result["answer_box"]
                if ab.get("answer"):
                    output.append(f"**Featured Answer:** {ab['answer']}\n")
                elif ab.get("snippet"):
                    output.append(f"**Featured Snippet:** {ab['snippet']}\n")
            
            # Organic results
            for item in result.get("organic_results", [])[:5]:
                output.append(f"- [{item.get('title', 'No title')}]({item.get('link', '')})")
                if item.get("snippet"):
                    output.append(f"  {item['snippet']}")
            
            # People also ask
            if result.get("related_questions"):
                output.append("\n**People Also Ask:**")
                for q in result["related_questions"][:3]:
                    output.append(f"- {q.get('question', '')}")
            
            return {"query": query, "result": "\n".join(output), "source": "google (serpapi)"}
    except Exception as e:
        return {"error": str(e)}

def search_reddit(query: str, subreddit: str = "all") -> dict:
    """Search Reddit for community discussions."""
    if not REDDIT_SCRIPT.exists():
        return {"error": "Reddit script not found"}
    
    cmd = f'node {REDDIT_SCRIPT} search {subreddit} "{query}" --limit 5'
    code, stdout, stderr = run_command(cmd, timeout=30)
    
    if code != 0:
        return {"error": stderr or "Search failed"}
    
    return {"query": query, "result": stdout.strip(), "source": f"reddit (r/{subreddit})"}

def multi_search(query: str, include_reddit: bool = False, reddit_sub: str = "all") -> list:
    """Search across multiple sources."""
    results = []
    
    print(f"    🔍 Searching: {query[:50]}...")
    
    # Perplexity (best for synthesized answers)
    perplexity_result = search_perplexity(query)
    if "error" not in perplexity_result:
        results.append(perplexity_result)
        print("      ✓ Perplexity")
    
    # Tavily (AI research)
    tavily_result = search_tavily(query)
    if "error" not in tavily_result:
        results.append(tavily_result)
        print("      ✓ Tavily")
    
    # SERP API (Google)
    serp_result = search_serpapi(query)
    if "error" not in serp_result:
        results.append(serp_result)
        print("      ✓ Google (SERP)")
    
    # Brave (web results)
    brave_result = search_brave(query)
    if "error" not in brave_result:
        results.append(brave_result)
        print("      ✓ Brave")
    
    # Reddit (community insights)
    if include_reddit:
        reddit_result = search_reddit(query, reddit_sub)
        if "error" not in reddit_result:
            results.append(reddit_result)
            print(f"      ✓ Reddit (r/{reddit_sub})")
    
    return results

def research_niche(niche: str) -> dict:
    """Comprehensive niche research."""
    print(f"\n🔍 Researching niche: {niche}")
    print("=" * 50)
    
    research = {
        "niche": niche,
        "timestamp": datetime.now().isoformat(),
        "sections": {}
    }
    
    sections = {
        "market_overview": {
            "queries": [
                f"{niche} market size 2024",
                f"{niche} industry overview trends",
            ],
            "reddit": False
        },
        "pain_points": {
            "queries": [
                f"{niche} biggest challenges problems",
                f"what frustrates {niche}",
            ],
            "reddit": True,
            "reddit_sub": "smallbusiness"
        },
        "where_they_hang_out": {
            "queries": [
                f"{niche} online communities forums",
                f"{niche} professional associations groups",
                f"{niche} podcasts newsletters influencers",
            ],
            "reddit": True
        },
        "competitors": {
            "queries": [
                f"software tools for {niche}",
                f"agencies serving {niche}",
            ],
            "reddit": False
        },
        "buying_behavior": {
            "queries": [
                f"how do {niche} make purchasing decisions",
                f"{niche} budget software services",
            ],
            "reddit": False
        }
    }
    
    for section_name, config in sections.items():
        print(f"\n📋 Section: {section_name}")
        section_results = []
        for query in config["queries"]:
            results = multi_search(
                query, 
                include_reddit=config.get("reddit", False),
                reddit_sub=config.get("reddit_sub", "all")
            )
            section_results.extend(results)
        research["sections"][section_name] = section_results
    
    return research

def research_persona(persona: str) -> dict:
    """Deep persona research."""
    print(f"\n🔍 Researching persona: {persona}")
    print("=" * 50)
    
    research = {
        "persona": persona,
        "timestamp": datetime.now().isoformat(),
        "sections": {}
    }
    
    sections = {
        "demographics": {
            "queries": [
                f"{persona} typical background career path",
                f"{persona} demographics profile",
            ],
            "reddit": False
        },
        "pain_points": {
            "queries": [
                f"{persona} biggest challenges daily frustrations",
                f"what keeps {persona} up at night",
            ],
            "reddit": True
        },
        "goals_aspirations": {
            "queries": [
                f"{persona} goals priorities KPIs",
                f"what does {persona} want to achieve",
            ],
            "reddit": False
        },
        "information_sources": {
            "queries": [
                f"{persona} favorite podcasts newsletters",
                f"{persona} thought leaders influencers",
            ],
            "reddit": True
        },
        "communities": {
            "queries": [
                f"{persona} communities professional groups",
                f"where do {persona} network online",
            ],
            "reddit": True
        },
        "buying_process": {
            "queries": [
                f"how do {persona} evaluate vendors",
                f"{persona} buying criteria decision process",
            ],
            "reddit": False
        }
    }
    
    for section_name, config in sections.items():
        print(f"\n📋 Section: {section_name}")
        section_results = []
        for query in config["queries"]:
            results = multi_search(
                query,
                include_reddit=config.get("reddit", False)
            )
            section_results.extend(results)
        research["sections"][section_name] = section_results
    
    return research

def research_market(market: str) -> dict:
    """Market research."""
    print(f"\n🔍 Researching market: {market}")
    print("=" * 50)
    
    research = {
        "market": market,
        "timestamp": datetime.now().isoformat(),
        "sections": {}
    }
    
    sections = {
        "market_size": {
            "queries": [
                f"{market} market size TAM 2024",
                f"{market} growth forecast projections",
            ]
        },
        "trends": {
            "queries": [
                f"{market} trends 2024 2025",
                f"{market} emerging technologies innovations",
            ]
        },
        "key_players": {
            "queries": [
                f"top companies in {market}",
                f"{market} market leaders startups",
            ]
        },
        "customer_segments": {
            "queries": [
                f"{market} customer segments buyers",
                f"who buys {market} solutions",
            ]
        },
        "competitive_landscape": {
            "queries": [
                f"{market} competitive landscape analysis",
                f"{market} market share distribution",
            ]
        }
    }
    
    for section_name, config in sections.items():
        print(f"\n📋 Section: {section_name}")
        section_results = []
        for query in config["queries"]:
            results = multi_search(query)
            section_results.extend(results)
        research["sections"][section_name] = section_results
    
    return research

def research_industry(industry: str) -> dict:
    """Industry insights research."""
    print(f"\n🔍 Researching industry: {industry}")
    print("=" * 50)
    
    research = {
        "industry": industry,
        "timestamp": datetime.now().isoformat(),
        "sections": {}
    }
    
    sections = {
        "overview": {
            "queries": [
                f"{industry} industry overview 2024",
                f"{industry} market landscape structure",
            ]
        },
        "trends": {
            "queries": [
                f"{industry} trends digital transformation",
                f"{industry} innovations technology",
            ]
        },
        "challenges": {
            "queries": [
                f"{industry} industry challenges problems",
                f"{industry} regulatory compliance issues",
            ]
        },
        "opportunities": {
            "queries": [
                f"{industry} growth opportunities gaps",
                f"{industry} untapped markets potential",
            ]
        },
        "technology": {
            "queries": [
                f"AI automation in {industry}",
                f"technology trends {industry}",
            ]
        }
    }
    
    for section_name, config in sections.items():
        print(f"\n📋 Section: {section_name}")
        section_results = []
        for query in config["queries"]:
            results = multi_search(query)
            section_results.extend(results)
        research["sections"][section_name] = section_results
    
    return research

def research_campaign(target: str) -> dict:
    """Campaign research - full research for launching a campaign."""
    print(f"\n🔍 Campaign research for: {target}")
    print("=" * 50)
    
    research = {
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "sections": {}
    }
    
    sections = {
        "industry_overview": {
            "queries": [
                f"{target} industry overview market",
                f"{target} business landscape trends",
            ],
            "reddit": False
        },
        "decision_makers": {
            "queries": [
                f"who makes buying decisions at {target}",
                f"{target} decision makers titles roles",
            ],
            "reddit": False
        },
        "pain_points": {
            "queries": [
                f"{target} biggest challenges problems",
                f"what frustrates {target}",
                f"{target} pain points complaints",
            ],
            "reddit": True
        },
        "aspirations": {
            "queries": [
                f"{target} goals priorities",
                f"what do {target} want to achieve",
            ],
            "reddit": False
        },
        "channels_communities": {
            "queries": [
                f"{target} online communities forums",
                f"{target} conferences events",
                f"{target} podcasts publications",
            ],
            "reddit": True
        },
        "competitors_alternatives": {
            "queries": [
                f"companies selling to {target}",
                f"{target} vendors service providers",
            ],
            "reddit": False
        },
        "messaging_language": {
            "queries": [
                f"how {target} talk about problems",
                f"{target} terminology jargon",
            ],
            "reddit": True
        }
    }
    
    for section_name, config in sections.items():
        print(f"\n📋 Section: {section_name}")
        section_results = []
        for query in config["queries"]:
            results = multi_search(
                query,
                include_reddit=config.get("reddit", False)
            )
            section_results.extend(results)
        research["sections"][section_name] = section_results
    
    return research

def research_competitors(company_or_space: str) -> dict:
    """Competitive research."""
    print(f"\n🔍 Competitor research: {company_or_space}")
    print("=" * 50)
    
    research = {
        "subject": company_or_space,
        "timestamp": datetime.now().isoformat(),
        "sections": {}
    }
    
    sections = {
        "direct_competitors": {
            "queries": [
                f"{company_or_space} competitors alternatives",
                f"companies like {company_or_space}",
            ]
        },
        "pricing": {
            "queries": [
                f"{company_or_space} pricing plans",
                f"{company_or_space} competitors pricing comparison",
            ]
        },
        "features": {
            "queries": [
                f"{company_or_space} features comparison",
                f"what makes {company_or_space} different",
            ]
        },
        "reviews_sentiment": {
            "queries": [
                f"{company_or_space} reviews pros cons",
                f"{company_or_space} customer complaints",
            ],
            "reddit": True
        },
        "market_position": {
            "queries": [
                f"{company_or_space} market position share",
                f"{company_or_space} vs competitors",
            ]
        }
    }
    
    for section_name, config in sections.items():
        print(f"\n📋 Section: {section_name}")
        section_results = []
        for query in config["queries"]:
            results = multi_search(
                query,
                include_reddit=config.get("reddit", False)
            )
            section_results.extend(results)
        research["sections"][section_name] = section_results
    
    return research

def format_research_as_markdown(research: dict, research_type: str) -> str:
    """Format research results as markdown."""
    subject = (research.get("niche") or research.get("persona") or 
               research.get("market") or research.get("industry") or 
               research.get("target") or research.get("subject", "Research"))
    
    md = f"""# {research_type.title()} Research: {subject}

**Generated:** {research.get('timestamp', datetime.now().isoformat())}
**Research Type:** {research_type}
**APIs Used:** Perplexity, Tavily, Google (SERP), Brave, Exa, Reddit

---

"""
    
    section_titles = {
        "market_overview": "📊 Market Overview",
        "market_size": "📈 Market Size & Growth",
        "pain_points": "😤 Pain Points & Challenges",
        "where_they_hang_out": "🎯 Where They Hang Out",
        "communities": "👥 Communities & Networks",
        "competitors": "⚔️ Competitive Landscape",
        "buying_behavior": "💰 Buying Behavior",
        "demographics": "👤 Demographics",
        "goals_aspirations": "🎯 Goals & Aspirations",
        "information_sources": "📚 Information Sources",
        "buying_process": "🛒 Buying Process",
        "trends": "📈 Trends & Outlook",
        "key_players": "🏆 Key Players",
        "customer_segments": "👥 Customer Segments",
        "competitive_landscape": "⚔️ Competitive Landscape",
        "overview": "📋 Overview",
        "challenges": "⚠️ Challenges",
        "opportunities": "💡 Opportunities",
        "technology": "🔧 Technology",
        "industry_overview": "🏭 Industry Overview",
        "decision_makers": "👔 Decision Makers",
        "aspirations": "🎯 Aspirations",
        "channels_communities": "📢 Channels & Communities",
        "competitors_alternatives": "⚔️ Competitors & Alternatives",
        "messaging_language": "💬 Messaging & Language",
        "direct_competitors": "🎯 Direct Competitors",
        "pricing": "💲 Pricing",
        "features": "✨ Features",
        "reviews_sentiment": "⭐ Reviews & Sentiment",
        "market_position": "📊 Market Position",
    }
    
    for section_key, results in research.get("sections", {}).items():
        section_title = section_titles.get(section_key, section_key.replace("_", " ").title())
        md += f"## {section_title}\n\n"
        
        for result in results:
            if "error" in result:
                continue
            
            source = result.get('source', 'unknown')
            md += f"### Source: {source}\n"
            md += f"**Query:** {result.get('query', 'N/A')}\n\n"
            
            content = result.get("result", "No results")
            md += f"{content}\n\n"
            md += "---\n\n"
    
    md += """
## 📋 Key Takeaways

*[To be filled in after review]*

1. 
2. 
3. 

## 🎯 Recommended Actions

*[To be filled in after review]*

- [ ] 
- [ ] 
- [ ] 

---

*Generated by Smarterflo ClickUp PM - Automated Research*
"""
    
    return md

def create_research_doc(title: str, content: str) -> dict:
    """Save research document."""
    output_dir = Path("/home/clawdbot/clawd/research_output")
    output_dir.mkdir(exist_ok=True)
    
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{safe_title}_{timestamp}.md"
    
    output_path = output_dir / filename
    output_path.write_text(content)
    
    print(f"\n📄 Research saved to: {output_path}")
    
    return {"path": str(output_path), "title": title}

def main():
    parser = argparse.ArgumentParser(description="Automated multi-source research")
    parser.add_argument("subject", nargs="?", help="Subject to research")
    parser.add_argument("--type", "-t", 
                        choices=["niche", "persona", "market", "industry", "campaign", "competitor"],
                        default="niche", help="Type of research")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    if not args.subject:
        parser.print_help()
        print("\n" + "=" * 50)
        print("EXAMPLES:")
        print("=" * 50)
        print('  python auto_research.py "dental practices" --type niche')
        print('  python auto_research.py "VP of Marketing" --type persona')
        print('  python auto_research.py "AI automation" --type market')
        print('  python auto_research.py "healthcare" --type industry')
        print('  python auto_research.py "SaaS founders" --type campaign')
        print('  python auto_research.py "HubSpot" --type competitor')
        return
    
    subject = args.subject
    
    # Run research
    if args.type == "niche":
        research = research_niche(subject)
    elif args.type == "persona":
        research = research_persona(subject)
    elif args.type == "market":
        research = research_market(subject)
    elif args.type == "industry":
        research = research_industry(subject)
    elif args.type == "campaign":
        research = research_campaign(subject)
    elif args.type == "competitor":
        research = research_competitors(subject)
    else:
        research = research_niche(subject)
    
    if args.json:
        print(json.dumps(research, indent=2))
        return
    
    # Format as markdown
    markdown = format_research_as_markdown(research, args.type)
    
    # Save
    title = f"{args.type.title()} Research - {subject}"
    doc = create_research_doc(title, markdown)
    
    # Summary
    total_results = sum(len(s) for s in research.get("sections", {}).values())
    
    print("\n" + "=" * 50)
    print("✅ RESEARCH COMPLETE")
    print("=" * 50)
    print(f"Subject: {subject}")
    print(f"Type: {args.type}")
    print(f"Sections: {len(research.get('sections', {}))}")
    print(f"Total results: {total_results}")
    print(f"Output: {doc['path']}")

if __name__ == "__main__":
    main()
