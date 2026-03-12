#!/home/clawdbot/venvs/neon/bin/python3
"""
Neon Snapshots Management
Create/restore/delete backups
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List

class NeonSnapshotsAPI:
    """Client for Neon Snapshots API"""
    
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
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all snapshots"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/snapshots",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()['snapshots']
    
    def create_snapshot(self, branch_id: str, name: str = None) -> Dict[str, Any]:
        """Create snapshot"""
        data = {
            'snapshot': {
                'branch_id': branch_id
            }
        }
        if name:
            data['snapshot']['name'] = name
        
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/snapshots",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()['snapshot']
    
    def update_snapshot(self, snapshot_id: str, name: str) -> Dict[str, Any]:
        """Update snapshot name"""
        data = {
            'snapshot': {
                'name': name
            }
        }
        
        response = requests.patch(
            f"{self.base_url}/projects/{self.project_id}/snapshots/{snapshot_id}",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()['snapshot']
    
    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete snapshot"""
        response = requests.delete(
            f"{self.base_url}/projects/{self.project_id}/snapshots/{snapshot_id}",
            headers=self._headers()
        )
        response.raise_for_status()
    
    def restore_snapshot(self, snapshot_id: str, target_branch_id: str = None) -> Dict[str, Any]:
        """Restore snapshot"""
        data = {}
        if target_branch_id:
            data['target_branch_id'] = target_branch_id
        
        response = requests.post(
            f"{self.base_url}/projects/{self.project_id}/snapshots/{snapshot_id}/restore",
            headers=self._headers(),
            json=data if data else None
        )
        response.raise_for_status()
        return response.json()
    
    def get_snapshot_schedule(self, branch_id: str) -> Dict[str, Any]:
        """Get backup schedule"""
        response = requests.get(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/snapshot_schedule",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def set_snapshot_schedule(self, branch_id: str, enabled: bool = True, 
                            frequency: str = 'daily', retention_days: int = 7) -> Dict[str, Any]:
        """Set backup schedule"""
        data = {
            'enabled': enabled,
            'frequency': frequency,
            'retention_days': retention_days
        }
        
        response = requests.put(
            f"{self.base_url}/projects/{self.project_id}/branches/{branch_id}/snapshot_schedule",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()

def main():
    parser = argparse.ArgumentParser(description='Manage Neon snapshots')
    subparsers = parser.add_subparsers(dest='command')
    
    # List
    list_parser = subparsers.add_parser('list', help='List snapshots')
    
    # Create
    create_parser = subparsers.add_parser('create', help='Create snapshot')
    create_parser.add_argument('branch_id', help='Branch ID')
    create_parser.add_argument('--name', help='Snapshot name')
    
    # Update
    update_parser = subparsers.add_parser('update', help='Update snapshot name')
    update_parser.add_argument('snapshot_id')
    update_parser.add_argument('name', help='New name')
    
    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete snapshot')
    delete_parser.add_argument('snapshot_id')
    
    # Restore
    restore_parser = subparsers.add_parser('restore', help='Restore snapshot')
    restore_parser.add_argument('snapshot_id')
    restore_parser.add_argument('--target-branch', help='Target branch ID')
    
    # Schedule
    schedule_parser = subparsers.add_parser('schedule', help='Manage backup schedule')
    schedule_parser.add_argument('action', choices=['get', 'set'])
    schedule_parser.add_argument('branch_id', help='Branch ID')
    schedule_parser.add_argument('--enabled', type=bool, help='Enable backups')
    schedule_parser.add_argument('--frequency', choices=['daily', 'weekly'], help='Backup frequency')
    schedule_parser.add_argument('--retention', type=int, help='Retention days')
    
    parser.add_argument('--pretty', action='store_true')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = NeonSnapshotsAPI()
        
        if args.command == 'list':
            snapshots = client.list_snapshots()
            for snap in snapshots:
                print(f"{snap['id']} - {snap.get('name', 'unnamed')} (created: {snap['created_at']})")
        
        elif args.command == 'create':
            snap = client.create_snapshot(args.branch_id, args.name)
            print(f"Created snapshot: {snap['id']}")
        
        elif args.command == 'update':
            snap = client.update_snapshot(args.snapshot_id, args.name)
            print(f"Updated snapshot: {snap['id']}")
        
        elif args.command == 'delete':
            client.delete_snapshot(args.snapshot_id)
            print(f"Deleted snapshot: {args.snapshot_id}")
        
        elif args.command == 'restore':
            result = client.restore_snapshot(args.snapshot_id, args.target_branch)
            print(f"Restore initiated: {result}")
        
        elif args.command == 'schedule':
            if args.action == 'get':
                schedule = client.get_snapshot_schedule(args.branch_id)
                print(json.dumps(schedule, indent=2 if args.pretty else None))
            
            elif args.action == 'set':
                schedule = client.set_snapshot_schedule(
                    args.branch_id,
                    args.enabled,
                    args.frequency,
                    args.retention
                )
                print("Backup schedule updated")
    
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.response.text:
            print(e.response.text, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
