#!/usr/bin/env python3
"""
Autobound API Client
Get real-time meeting intelligence on contacts & companies
"""
# /// script
# dependencies = [
#   "requests",
# ]
# ///

import os
import requests
from typing import Dict, List, Optional

class AutoboundClient:
    """Autobound API for meeting intelligence"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('AUTOBOUND_API_KEY')
        if not self.api_key:
            raise ValueError("AUTOBOUND_API_KEY not set")
        
        self.base_url = 'https://api.autobound.ai/api/external'
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_insights(
        self, 
        contact_email: Optional[str] = None,
        contact_linkedin: Optional[str] = None,
        company_domain: Optional[str] = None,
        company_name: Optional[str] = None,
        limit: int = 20
    ) -> Dict:
        """
        Get ranked insights on contact/company
        
        Args:
            contact_email: Contact's email
            contact_linkedin: LinkedIn URL
            company_domain: Company website domain
            company_name: Company name
            limit: Max insights to return (default 20)
        
        Returns:
            Dict with ranked insights
        """
        url = f"{self.base_url}/generate-insights/v1.4"
        
        data = {}
        if contact_email:
            data['contactEmail'] = contact_email
        if contact_linkedin:
            data['contactLinkedin'] = contact_linkedin
        if company_domain:
            data['companyDomain'] = company_domain
        if company_name:
            data['companyName'] = company_name
        
        if not data:
            raise ValueError("Must provide at least one identifier")
        
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract insights
        insights = result.get('insights', [])[:limit]
        
        return {
            'contact': result.get('contact', {}),
            'company': result.get('company', {}),
            'insights': insights,
            'total_insights': len(insights)
        }
    
    def generate_call_script(
        self,
        contact_email: str,
        user_email: str,
        value_proposition: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict:
        """
        Generate personalized call script
        
        Args:
            contact_email: Prospect's email
            user_email: Your email (for personalization)
            value_proposition: What you're selling
            additional_context: Extra context for personalization
        
        Returns:
            Dict with call script
        """
        url = f"{self.base_url}/generate-content/v3.6"
        
        data = {
            'contactEmail': contact_email,
            'userEmail': user_email,
            'contentType': 'call_script'
        }
        
        if value_proposition:
            data['valueProposition'] = value_proposition
        if additional_context:
            data['additionalContext'] = additional_context
        
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def generate_email_opener(
        self,
        contact_email: str,
        user_email: str,
        value_proposition: Optional[str] = None
    ) -> Dict:
        """
        Generate personalized email opener
        
        Args:
            contact_email: Prospect's email
            user_email: Your email
            value_proposition: What you're selling
        
        Returns:
            Dict with email opener
        """
        url = f"{self.base_url}/generate-content/v3.6"
        
        data = {
            'contactEmail': contact_email,
            'userEmail': user_email,
            'contentType': 'opener'
        }
        
        if value_proposition:
            data['valueProposition'] = value_proposition
        
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def format_insights_for_prep(self, insights_data: Dict) -> Dict:
        """
        Format Autobound insights for meeting prep
        
        Args:
            insights_data: Raw insights from get_insights()
        
        Returns:
            Formatted dict ready for meeting prep
        """
        contact = insights_data.get('contact', {})
        company = insights_data.get('company', {})
        insights = insights_data.get('insights', [])
        
        # Categorize insights
        categorized = {
            'recent_news': [],
            'hiring_signals': [],
            'tech_stack': [],
            'linkedin_activity': [],
            'job_changes': [],
            'funding': [],
            'other': []
        }
        
        for insight in insights:
            insight_type = insight.get('type', '').lower()
            
            if 'news' in insight_type or 'announcement' in insight_type:
                categorized['recent_news'].append({
                    'type': insight.get('type'),
                    'title': insight.get('title', ''),
                    'description': insight.get('description', ''),
                    'date': insight.get('date', ''),
                    'source': insight.get('source', '')
                })
            elif 'hiring' in insight_type or 'job' in insight_type:
                categorized['hiring_signals'].append({
                    'type': insight.get('type'),
                    'description': insight.get('description', '')
                })
            elif 'tech' in insight_type or 'stack' in insight_type:
                categorized['tech_stack'].append({
                    'technology': insight.get('title', ''),
                    'description': insight.get('description', '')
                })
            elif 'linkedin' in insight_type or 'social' in insight_type:
                categorized['linkedin_activity'].append({
                    'type': insight.get('type'),
                    'content': insight.get('description', ''),
                    'date': insight.get('date', '')
                })
            elif 'funding' in insight_type or 'investment' in insight_type:
                categorized['funding'].append({
                    'type': insight.get('type'),
                    'description': insight.get('description', ''),
                    'date': insight.get('date', '')
                })
            else:
                categorized['other'].append({
                    'type': insight.get('type'),
                    'description': insight.get('description', '')
                })
        
        return {
            'contact': {
                'name': contact.get('name', ''),
                'title': contact.get('title', ''),
                'email': contact.get('email', ''),
                'linkedin': contact.get('linkedin', '')
            },
            'company': {
                'name': company.get('name', ''),
                'domain': company.get('domain', ''),
                'description': company.get('description', ''),
                'industry': company.get('industry', ''),
                'size': company.get('size', ''),
                'location': company.get('location', '')
            },
            'insights': categorized,
            'total_insights': len(insights)
        }

# Test
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python autobound_client.py <contact_email> [company_domain]")
        sys.exit(1)
    
    client = AutoboundClient()
    
    contact_email = sys.argv[1]
    company_domain = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔍 Getting Autobound insights for {contact_email}...")
    
    insights = client.get_insights(
        contact_email=contact_email,
        company_domain=company_domain
    )
    
    formatted = client.format_insights_for_prep(insights)
    
    print(f"\n✅ Found {formatted['total_insights']} insights")
    print(f"\n👤 Contact: {formatted['contact']['name']}")
    print(f"   Title: {formatted['contact']['title']}")
    print(f"\n🏢 Company: {formatted['company']['name']}")
    print(f"   Industry: {formatted['company']['industry']}")
    
    print(f"\n📊 Insights breakdown:")
    for category, items in formatted['insights'].items():
        if items:
            print(f"   {category}: {len(items)} items")
