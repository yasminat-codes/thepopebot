#!/home/clawdbot/venvs/neon/bin/python3
"""
Neon Management API
Manage projects, branches, databases
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List

class NeonManagementAPI:
    """Client for Neon Management API"""
    
    def __init__(self):
        self.api_key = os.getenv('NEON_API_KEY')
        self.project_id = os.getenv('NEON_PROJECT_ID')
        self.base_url = 'https://console.neon.tech/api/v2'
        
        if not self.api_key:
            raise ValueError("NEON_API_KEY not set in environment")
        if not self.project_id:
            raise ValueError("NEON_PROJECT_ID not set in environment")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def list_branches(self) -> List[Dict[str, Any]]:
        """List all branches"""
        url = f"{self.base_url}/projects/{self.project_id}/branches"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()['branches']
    
    def create_branch(self, name: str, parent: str = 'main') -> Dict[str, Any]:
        """Create new branch"""
        url = f"{self.base_url}/projects/{self.project_id}/branches"
        
        # Get parent branch ID
        branches = self.list_branches()
        parent_branch = next((b for b in branches if b['name'] == parent), None)
        
        if not parent_branch:
            raise ValueError(f"Parent branch '{parent}' not found")
        
        data = {
            'branch': {
                'name': name,
                'parent_id': parent_branch['id']
            }
        }
        
        response = requests.post(url, headers=self._headers(), json=data)
        response.raise_for_status()
        return response.json()['branch']
    
    def delete_branch(self, name: str) -> None:
        """Delete branch"""
        branches = self.list_branches()
        branch = next((b for b in branches if b['name'] == name), None)
        
        if not branch:
            raise ValueError(f"Branch '{name}' not found")
        
        if name == 'main':
            raise ValueError("Cannot delete main branch")
        
        url = f"{self.base_url}/projects/{self.project_id}/branches/{branch['id']}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
    
    def get_connection_string(self, branch: str = 'main', 
                             pooled: bool = False) -> str:
        """Get connection string for branch"""
        branches = self.list_branches()
        branch_obj = next((b for b in branches if b['name'] == branch), None)
        
        if not branch_obj:
            raise ValueError(f"Branch '{branch}' not found")
        
        url = f"{self.base_url}/projects/{self.project_id}/connection_uri"
        params = {
            'branch_id': branch_obj['id'],
            'pooled': 'true' if pooled else 'false'
        }
        
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()['uri']

def main():
    parser = argparse.ArgumentParser(
        description='Manage Neon resources (branches, connection strings)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List branches
  %(prog)s branches --list
  
  # Create branch
  %(prog)s branches --create "dev-feature-x"
  
  # Create branch from specific parent
  %(prog)s branches --create "staging" --from "main"
  
  # Delete branch
  %(prog)s branches --delete "old-feature"
  
  # Get connection string
  %(prog)s connection-string
  
  # Get pooled connection string
  %(prog)s connection-string --pooled
  
  # Get connection for specific branch
  %(prog)s connection-string --branch "dev"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Branches command
    branches_parser = subparsers.add_parser('branches', help='Manage branches')
    branches_parser.add_argument('--list', action='store_true', help='List all branches')
    branches_parser.add_argument('--create', metavar='NAME', help='Create new branch')
    branches_parser.add_argument('--from', dest='parent', default='main', help='Parent branch (default: main)')
    branches_parser.add_argument('--delete', metavar='NAME', help='Delete branch')
    
    # Connection string command
    conn_parser = subparsers.add_parser('connection-string', help='Get connection string')
    conn_parser.add_argument('--branch', default='main', help='Branch name (default: main)')
    conn_parser.add_argument('--pooled', action='store_true', help='Get pooled connection')
    
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = NeonManagementAPI()
        
        # Branches
        if args.command == 'branches':
            if args.list:
                branches = client.list_branches()
                for b in branches:
                    print(f"{b['name']} (id: {b['id']}, created: {b['created_at']})")
            
            elif args.create:
                branch = client.create_branch(args.create, args.parent)
                print(f"Created branch: {branch['name']} (id: {branch['id']})")
            
            elif args.delete:
                client.delete_branch(args.delete)
                print(f"Deleted branch: {args.delete}")
            
            else:
                branches_parser.print_help()
        
        # Connection string
        elif args.command == 'connection-string':
            conn_str = client.get_connection_string(args.branch, args.pooled)
            print(conn_str)
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        if e.response.text:
            print(e.response.text, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
