#!/home/clawdbot/venvs/neon/bin/python3
"""
Neon Databases & Roles Management
Create/delete databases and roles
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List

class NeonDatabasesAPI:
    """Client for Neon Databases & Roles API"""
    
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
    
    # Databases
    def list_databases(self, branch_id: str) -> List[Dict[str, Any]]:
        """List databases in branch"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/databases",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['databases']
    
    def get_database(self, branch_id: str, database_name: str) -> Dict[str, Any]:
        """Get database details"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/databases/{database_name}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['database']
    
    def create_database(self, branch_id: str, database_name: str, owner_name: str) -> Dict[str, Any]:
        """Create database"""
        data = {
            'database': {
                'name': database_name,
                'owner_name': owner_name
            }
        }
        
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/databases",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()['database']
    
    def update_database(self, branch_id: str, database_name: str, new_owner: str) -> Dict[str, Any]:
        """Update database owner"""
        data = {
            'database': {
                'owner_name': new_owner
            }
        }
        
        response = requests.patch(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/databases/{database_name}",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()['database']
    
    def delete_database(self, branch_id: str, database_name: str) -> None:
        """Delete database"""
        response = requests.delete(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/databases/{database_name}",
            headers=self._headers()
        )
        response.raise_for_status()
    
    # Roles
    def list_roles(self, branch_id: str) -> List[Dict[str, Any]]:
        """List roles in branch"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/roles",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['roles']
    
    def get_role(self, branch_id: str, role_name: str) -> Dict[str, Any]:
        """Get role details"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/roles/{role_name}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['role']
    
    def create_role(self, branch_id: str, role_name: str) -> Dict[str, Any]:
        """Create role"""
        data = {
            'role': {
                'name': role_name
            }
        }
        
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/roles",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()['role']
    
    def delete_role(self, branch_id: str, role_name: str) -> None:
        """Delete role"""
        response = requests.delete(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/roles/{role_name}",
            headers=self._headers()
        )
        response.raise_for_status()
    
    def get_role_password(self, branch_id: str, role_name: str) -> str:
        """Get role password"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/roles/{role_name}/reveal_password",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['password']
    
    def reset_role_password(self, branch_id: str, role_name: str) -> str:
        """Reset role password"""
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/roles/{role_name}/reset_password",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['role']

def main():
    parser = argparse.ArgumentParser(description='Manage Neon databases and roles')
    parser.add_argument('type', choices=['database', 'role'], help='Resource type')
    parser.add_argument('action', choices=['list', 'get', 'create', 'delete', 'update', 'password', 'reset-password'])
    parser.add_argument('branch_id', help='Branch ID')
    parser.add_argument('name', nargs='?', help='Database or role name')
    parser.add_argument('--owner', help='Owner name (for create database)')
    parser.add_argument('--new-owner', help='New owner (for update database)')
    parser.add_argument('--pretty', action='store_true')
    
    args = parser.parse_args()
    
    try:
        client = NeonDatabasesAPI()
        
        if args.type == 'database':
            if args.action == 'list':
                dbs = client.list_databases(args.branch_id)
                for db in dbs:
                    print(f"{db['name']} (owner: {db['owner_name']})")
            
            elif args.action == 'get':
                db = client.get_database(args.branch_id, args.name)
                print(json.dumps(db, indent=2 if args.pretty else None))
            
            elif args.action == 'create':
                if not args.owner:
                    print("Error: --owner required for create", file=sys.stderr)
                    sys.exit(1)
                db = client.create_database(args.branch_id, args.name, args.owner)
                print(f"Created database: {db['name']}")
            
            elif args.action == 'update':
                if not args.new_owner:
                    print("Error: --new-owner required for update", file=sys.stderr)
                    sys.exit(1)
                db = client.update_database(args.branch_id, args.name, args.new_owner)
                print(f"Updated database: {db['name']}")
            
            elif args.action == 'delete':
                client.delete_database(args.branch_id, args.name)
                print(f"Deleted database: {args.name}")
        
        elif args.type == 'role':
            if args.action == 'list':
                roles = client.list_roles(args.branch_id)
                for role in roles:
                    print(f"{role['name']} (protected: {role.get('protected', False)})")
            
            elif args.action == 'get':
                role = client.get_role(args.branch_id, args.name)
                print(json.dumps(role, indent=2 if args.pretty else None))
            
            elif args.action == 'create':
                role = client.create_role(args.branch_id, args.name)
                print(f"Created role: {role['name']}")
                print(f"Password: {role.get('password', 'N/A')}")
            
            elif args.action == 'delete':
                client.delete_role(args.branch_id, args.name)
                print(f"Deleted role: {args.name}")
            
            elif args.action == 'password':
                password = client.get_role_password(args.branch_id, args.name)
                print(f"Password: {password}")
            
            elif args.action == 'reset-password':
                role = client.reset_role_password(args.branch_id, args.name)
                print(f"Reset password for: {role['name']}")
                print(f"New password: {role.get('password', 'check manually')}")
    
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.response.text:
            print(e.response.text, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
