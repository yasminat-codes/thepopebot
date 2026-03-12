#!/usr/bin/env python3
"""
Neon CRUD Operations Examples
Demonstrates all basic operations with Data API
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from query import NeonDataAPI

def main():
    client = NeonDataAPI()
    
    print("=== Neon Data API CRUD Examples ===\n")
    
    # CREATE (INSERT)
    print("1. CREATE - Insert new lead")
    new_lead = {
        "name": "Jane Smith",
        "email": "jane@acme.com",
        "company": "Acme Corp",
        "status": "new",
        "source": "linkedin",
        "score": 75
    }
    
    result = client.insert("leads", new_lead)
    lead_id = result[0]['id'] if isinstance(result, list) else result['id']
    print(f"   Created lead with ID: {lead_id}\n")
    
    # READ (SELECT)
    print("2. READ - Get the lead we just created")
    lead = client.select("leads", filters=[f"id=eq.{lead_id}"], single=True)
    print(f"   Found: {lead['name']} ({lead['email']})\n")
    
    print("3. READ - Get all qualified leads")
    qualified = client.select("leads", 
                             select="name,email,score",
                             filters=["status=eq.qualified"],
                             order="score.desc",
                             limit=5)
    print(f"   Found {len(qualified)} qualified leads\n")
    
    # UPDATE
    print("4. UPDATE - Mark lead as qualified")
    updated = client.update("leads", 
                           {"status": "qualified", "score": 85},
                           [f"id=eq.{lead_id}"])
    print(f"   Updated {len(updated)} lead(s)\n")
    
    # READ again to verify
    print("5. READ - Verify update")
    lead = client.select("leads", filters=[f"id=eq.{lead_id}"], single=True)
    print(f"   Status: {lead['status']}, Score: {lead['score']}\n")
    
    # DELETE
    print("6. DELETE - Remove test lead")
    client.delete("leads", [f"id=eq.{lead_id}"])
    print(f"   Deleted lead {lead_id}\n")
    
    # Verify deletion
    print("7. VERIFY - Check lead is gone")
    try:
        lead = client.select("leads", filters=[f"id=eq.{lead_id}"], single=True)
        print("   Error: Lead still exists!")
    except:
        print("   Confirmed: Lead deleted\n")
    
    print("=== CRUD Examples Complete ===")

if __name__ == '__main__':
    main()
