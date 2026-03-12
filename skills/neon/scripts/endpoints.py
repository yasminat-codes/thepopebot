#!/home/clawdbot/venvs/neon/bin/python3
"""
Neon Compute Endpoints Management
Start/stop/restart/suspend endpoints
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List

class NeonEndpointsAPI:
    """Client for Neon Endpoints API"""
    
    def __init__(self):
        self.api_key = os.getenv('NEON_API_KEY')
        self.project_id = os.getenv('NEON_PROJECT_ID')
        self.base_url = 'https://console.neon.tech/api/v2'
        
        if not self.api_key:
            raise ValueError("NEON_API_KEY not set")
        if not self.project_id:
            raise ValueError("NEON_PROJECT_ID not set")
    
    def _headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def list_endpoints(self, branch_id: str = None) -> List[Dict[str, Any]]:
        """List all endpoints"""
        if branch_id:
            url = f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/endpoints"
        else:
            url = f"{self.base_url}/projects/{self.project_id}/endpoints"
        
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()['endpoints']
    
    def get_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Get endpoint details"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/endpoints/{endpoint_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['endpoint']
    
    def create_endpoint(self, branch_id: str, endpoint_type: str = 'read_write',
                       autoscaling_limit_min_cu: float = 0.25,
                       autoscaling_limit_max_cu: float = 1.0) -> Dict[str, Any]:
        """Create compute endpoint"""
        data = {
            'endpoint': {
                'branch_id': branch_id,
                'type': endpoint_type,
                'autoscaling_limit_min_cu': autoscaling_limit_min_cu,
                'autoscaling_limit_max_cu': autoscaling_limit_max_cu
            }
        }
        
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/endpoints",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()['endpoint']
    
    def update_endpoint(self, endpoint_id: str, **kwargs) -> Dict[str, Any]:
        """Update endpoint settings"""
        data = {'endpoint': kwargs}
        
        response = requests.patch(
            f"{self.base_url}/projects/{self.project_id}/endpoints/{endpoint_id}",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()['endpoint']
    
    def delete_endpoint(self, endpoint_id: str) -> None:
        """Delete endpoint"""
        response = requests.delete(
            f"{self.base_url}/projects/{self.project_id}/endpoints/{endpoint_id}",
            headers=self._headers()
        )
        response.raise_for_status()
    
    def start_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Start endpoint"""
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/endpoints/{endpoint_id}/start",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['endpoint']
    
    def suspend_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Suspend endpoint"""
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/endpoints/{endpoint_id}/suspend",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['endpoint']
    
    def restart_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Restart endpoint"""
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/endpoints/{endpoint_id}/restart",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['endpoint']

def main():
    parser = argparse.ArgumentParser(description='Manage Neon compute endpoints')
    subparsers = parser.add_subparsers(dest='command')
    
    # List
    list_parser = subparsers.add_parser('list', help='List endpoints')
    list_parser.add_argument('--branch', help='Filter by branch ID')
    
    # Get
    get_parser = subparsers.add_parser('get', help='Get endpoint details')
    get_parser.add_argument('endpoint_id')
    
    # Create
    create_parser = subparsers.add_parser('create', help='Create endpoint')
    create_parser.add_argument('branch_id', help='Branch ID')
    create_parser.add_argument('--type', default='read_write', choices=['read_write', 'read_only'])
    create_parser.add_argument('--min-cu', type=float, default=0.25)
    create_parser.add_argument('--max-cu', type=float, default=1.0)
    
    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete endpoint')
    delete_parser.add_argument('endpoint_id')
    
    # Start
    start_parser = subparsers.add_parser('start', help='Start endpoint')
    start_parser.add_argument('endpoint_id')
    
    # Suspend
    suspend_parser = subparsers.add_parser('suspend', help='Suspend endpoint')
    suspend_parser.add_argument('endpoint_id')
    
    # Restart
    restart_parser = subparsers.add_parser('restart', help='Restart endpoint')
    restart_parser.add_argument('endpoint_id')
    
    parser.add_argument('--pretty', action='store_true')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = NeonEndpointsAPI()
        
        if args.command == 'list':
            endpoints = client.list_endpoints(args.branch if hasattr(args, 'branch') else None)
            for ep in endpoints:
                print(f"{ep['id']} - {ep['type']} ({ep['current_state']})")
        
        elif args.command == 'get':
            ep = client.get_endpoint(args.endpoint_id)
            print(json.dumps(ep, indent=2 if args.pretty else None))
        
        elif args.command == 'create':
            ep = client.create_endpoint(args.branch_id, args.type, args.min_cu, args.max_cu)
            print(f"Created endpoint: {ep['id']}")
        
        elif args.command == 'delete':
            client.delete_endpoint(args.endpoint_id)
            print(f"Deleted endpoint: {args.endpoint_id}")
        
        elif args.command == 'start':
            ep = client.start_endpoint(args.endpoint_id)
            print(f"Started: {ep['id']} ({ep['current_state']})")
        
        elif args.command == 'suspend':
            ep = client.suspend_endpoint(args.endpoint_id)
            print(f"Suspended: {ep['id']} ({ep['current_state']})")
        
        elif args.command == 'restart':
            ep = client.restart_endpoint(args.endpoint_id)
            print(f"Restarted: {ep['id']} ({ep['current_state']})")
    
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.response.text:
            print(e.response.text, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
