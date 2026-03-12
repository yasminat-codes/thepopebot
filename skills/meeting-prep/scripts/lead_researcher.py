#!/usr/bin/env python3
"""
Lead & Company Researcher
Deep research using Perplexity, SERP API, Tavily
"""
import os
import json
import subprocess
import requests

class LeadResearcher:
    """Research lead and company comprehensively"""
    
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY', '')
        self.serp_key = os.getenv('SERP_API_KEY', '')
        self.tavily_key = os.getenv('TAVILY_API_KEY', '')
    
    def research_lead(self, lead_name, company_name):
        """Complete research on lead and company"""
        print(f"\n🔍 Researching {lead_name} at {company_name}...")
        
        research = {
            'lead_name': lead_name,
            'company_name': company_name,
            'timestamp': subprocess.run(['date', '-Iseconds'], capture_output=True, text=True).stdout.strip()
        }
        
        # 1. Company Overview
        print("   📊 Company overview...")
        research['company_overview'] = self._research_company(company_name)
        
        # 2. Recent News
        print("   📰 Recent news...")
        research['recent_news'] = self._get_recent_news(company_name)
        
        # 3. Lead Background
        print("   👤 Lead background...")
        research['lead_background'] = self._research_person(lead_name, company_name)
        
        # 4. LinkedIn Activity
        print("   💼 LinkedIn presence...")
        research['linkedin_info'] = self._search_linkedin(lead_name, company_name)
        
        # 5. Twitter/X Posts
        print("   🐦 X/Twitter activity...")
        research['twitter_activity'] = self._search_twitter(lead_name, company_name)
        
        # 6. Industry Context
        print("   🏭 Industry context...")
        research['industry_context'] = self._get_industry_context(company_name)
        
        return research
    
    def _research_company(self, company_name):
        """Deep dive on company"""
        query = f"Comprehensive overview of {company_name}: what they do, size, funding, leadership, recent achievements, and business model"
        return self._perplexity_search(query)
    
    def _get_recent_news(self, company_name):
        """Get recent news about company"""
        try:
            response = requests.get(
                'https://serpapi.com/search',
                params={
                    'q': f'{company_name} news',
                    'api_key': self.serp_key,
                    'tbm': 'nws',  # News search
                    'num': 5
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                news = data.get('news_results', [])
                return [
                    {
                        'title': item.get('title'),
                        'source': item.get('source'),
                        'date': item.get('date'),
                        'link': item.get('link')
                    }
                    for item in news[:5]
                ]
        except:
            pass
        
        return []
    
    def _research_person(self, lead_name, company_name):
        """Research the specific person"""
        query = f"Background on {lead_name} at {company_name}: their role, experience, expertise, and recent activities"
        return self._perplexity_search(query)
    
    def _search_linkedin(self, lead_name, company_name):
        """Search for LinkedIn activity"""
        # Use SERP API to find LinkedIn profile and recent posts
        try:
            response = requests.get(
                'https://serpapi.com/search',
                params={
                    'q': f'{lead_name} {company_name} LinkedIn',
                    'api_key': self.serp_key,
                    'num': 3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('organic_results', [])
                linkedin_info = []
                
                for result in results:
                    if 'linkedin.com' in result.get('link', ''):
                        linkedin_info.append({
                            'title': result.get('title'),
                            'snippet': result.get('snippet'),
                            'link': result.get('link')
                        })
                
                return linkedin_info
        except:
            pass
        
        return []
    
    def _search_twitter(self, lead_name, company_name):
        """Search for Twitter/X activity"""
        try:
            response = requests.get(
                'https://serpapi.com/search',
                params={
                    'q': f'{lead_name} {company_name} twitter OR X.com',
                    'api_key': self.serp_key,
                    'num': 3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('organic_results', [])
                twitter_info = []
                
                for result in results:
                    if 'twitter.com' in result.get('link', '') or 'x.com' in result.get('link', ''):
                        twitter_info.append({
                            'title': result.get('title'),
                            'snippet': result.get('snippet'),
                            'link': result.get('link')
                        })
                
                return twitter_info
        except:
            pass
        
        return []
    
    def _get_industry_context(self, company_name):
        """Get industry trends and context"""
        # Use Tavily for curated industry insights
        try:
            response = requests.post(
                'https://api.tavily.com/search',
                json={
                    'api_key': self.tavily_key,
                    'query': f'{company_name} industry trends challenges opportunities 2026',
                    'search_depth': 'advanced',
                    'max_results': 3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
        except:
            pass
        
        return []
    
    def _perplexity_search(self, query):
        """Use Perplexity for AI research"""
        try:
            env = os.environ.copy()
            env['PERPLEXITY_API_KEY'] = self.perplexity_key
            
            result = subprocess.run(
                ['node', '/home/clawdbot/clawd/skills/perplexity/scripts/search.mjs', query],
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "Research unavailable"

# Test
if __name__ == '__main__':
    researcher = LeadResearcher()
    
    # Test with sample
    research = researcher.research_lead("John Smith", "Acme Corp")
    print(json.dumps(research, indent=2))
