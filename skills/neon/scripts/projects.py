#!/home/clawdbot/venvs/neon/bin/python3
"""
Neon Projects Management
Complete project lifecycle operations
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List, Optional

class NeonProjectsAPI:
    """Client for Neon Projects API"""
    
    def __init__(self):
        self.api_key = os.getenv('NEON_API_KEY')
        self.base_url = 'https://console.neon.tech/api/v2'
        
        if not self.api_key:
            raise ValueError("NEON_API_KEY not set in environment")
    
    def _headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        response = requests.get(f"{self.base_url}/projects", headers=self._headers())
        response.raise_for_status()
        return response.json()['projects']
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        response = requests.get(f"{self.base_url}/projects/{project_id}", headers=self._headers())
        response.raise_for_status()
        return response.json()['project']
    
    def create_project(self, name: str, region: str = None, pg_version: int = None) -> Dict[str, Any]:
        """Create new project"""
        data = {'project': {'name': name}}
        if region:
            data['project']['region_id'] = region
        if pg_version:
            data['project']['pg_version'] = pg_version
        
        response = requests.post(f"{self.base_url}/projects", headers=self._headers(), json=data)
        response.raise_for_status()
        return response.json()['project']
    
    def update_project(self, project_id: str, name: str = None, settings: Dict = None) -> Dict[str, Any]:
        """Update project"""
        data = {'project': {}}
        if name:
            data['project']['name'] = name
        if settings:
            data['project']['settings'] = settings
        
        response = requests.patch(f"{self.base_url}/projects/{project_id}", 
                                 headers=self._headers(), json=data)
        response.raise_for_status()
        return response.json()['project']
    
    def delete_project(self, project_id: str) -> None:
        """Delete project"""
        response = requests.delete(f"{self.base_url}/projects/{project_id}", headers=self._headers())
        response.raise_for_status()
    
    def list_operations(self, project_id: str) -> List[Dict[str, Any]]:
        """List project operations"""
        response = requests.get(f"{self.base_url}/projects/{project_id}/operations", 
                               headers=self._headers())
        response.raise_for_status()
        return response.json()['operations']
    
    def get_operation(self, project_id: str, operation_id: str) -> Dict[str, Any]:
        """Get operation details"""
        response = requests.get(f"{self.base_url}/projects/{project_id}/operations/{operation_id}", 
                               headers=self._headers())
        response.raise_for_status()
        return response.json()['operation']

def main():
    parser = argparse.ArgumentParser(description='Manage Neon projects')
    subparsers = parser.add_subparsers(dest='command')
    
    # List
    list_parser = subparsers.add_parser('list', help='List all projects')
    
    # Get
    get_parser = subparsers.add_parser('get', help='Get project details')
    get_parser.add_argument('project_id', help='Project ID')
    
    # Create
    create_parser = subparsers.add_parser('create', help='Create project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('--region', help='Region (e.g., aws-us-east-1)')
    create_parser.add_argument('--pg-version', type=int, help='PostgreSQL version')
    
    # Update
    update_parser = subparsers.add_parser('update', help='Update project')
    update_parser.add_argument('project_id', help='Project ID')
    update_parser.add_argument('--name', help='New name')
    
    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete project')
    delete_parser.add_argument('project_id', help='Project ID')
    
    # Operations
    ops_parser = subparsers.add_parser('operations', help='List operations')
    ops_parser.add_argument('project_id', help='Project ID')
    
    parser.add_argument('--pretty', action='store_true')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = NeonProjectsAPI()
        
        if args.command == 'list':
            projects = client.list_projects()
            for p in projects:
                print(f"{p['name']} (id: {p['id']}, region: {p['region_id']})")
        
        elif args.command == 'get':
            project = client.get_project(args.project_id)
            print(json.dumps(project, indent=2 if args.pretty else None))
        
        elif args.command == 'create':
            project = client.create_project(args.name, args.region, args.pg_version)
            print(f"Created: {project['name']} (id: {project['id']})")
        
        elif args.command == 'update':
            project = client.update_project(args.project_id, args.name)
            print(f"Updated: {project['name']}")
        
        elif args.command == 'delete':
            client.delete_project(args.project_id)
            print(f"Deleted project: {args.project_id}")
        
        elif args.command == 'operations':
            ops = client.list_operations(args.project_id)
            for op in ops:
                print(f"{op['action']} - {op['status']} (id: {op['id']})")
    
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.response.text:
            print(e.response.text, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
