#!/home/clawdbot/venvs/neon/bin/python3
"""
Neon Data API Query Tool
Query PostgreSQL via REST API (no connection pooling needed)
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any, List

class NeonDataAPI:
    """Client for Neon Data API"""
    
    def __init__(self):
        self.base_url = os.getenv('NEON_DATA_API_URL')
        self.jwt_token = os.getenv('NEON_JWT_TOKEN')
        
        if not self.base_url:
            raise ValueError("NEON_DATA_API_URL not set in environment")
        if not self.jwt_token:
            raise ValueError("NEON_JWT_TOKEN not set in environment")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers with JWT"""
        return {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        }
    
    def _build_url(self, table: str, filters: List[str] = None, 
                   select: str = '*', order: str = None, 
                   limit: int = None, offset: int = None,
                   single: bool = False) -> str:
        """Build Data API URL with query parameters"""
        url = f"{self.base_url}/{table}"
        params = []
        
        # Select columns
        if select and select != '*':
            params.append(f"select={select}")
        
        # Filters
        if filters:
            for f in filters:
                params.append(f)
        
        # Ordering
        if order:
            params.append(f"order={order}")
        
        # Limit
        if limit:
            params.append(f"limit={limit}")
        
        # Offset
        if offset:
            params.append(f"offset={offset}")
        
        if params:
            url += '?' + '&'.join(params)
        
        return url
    
    def select(self, table: str, select: str = '*', filters: List[str] = None,
               order: str = None, limit: int = None, offset: int = None,
               single: bool = False) -> Any:
        """SELECT query"""
        url = self._build_url(table, filters, select, order, limit, offset, single)
        
        headers = self._headers()
        if single:
            headers['Accept'] = 'application/vnd.pgrst.object+json'
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """INSERT query"""
        url = f"{self.base_url}/{table}"
        
        response = requests.post(
            url,
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        
        return response.json()
    
    def update(self, table: str, data: Dict[str, Any], 
               filters: List[str]) -> List[Dict[str, Any]]:
        """UPDATE query"""
        if not filters:
            raise ValueError("UPDATE requires filters (safety check)")
        
        url = self._build_url(table, filters)
        
        response = requests.patch(
            url,
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        
        return response.json()
    
    def delete(self, table: str, filters: List[str]) -> None:
        """DELETE query"""
        if not filters:
            raise ValueError("DELETE requires filters (safety check)")
        
        url = self._build_url(table, filters)
        
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()

def main():
    parser = argparse.ArgumentParser(
        description='Query Neon PostgreSQL via Data API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SELECT all leads
  %(prog)s leads --select "*"
  
  # Filter qualified leads
  %(prog)s leads --select "name,email" --filter "status=eq.qualified"
  
  # Complex query
  %(prog)s leads --select "*" --filter "status=eq.qualified" --order "created_at.desc" --limit 10
  
  # INSERT
  %(prog)s leads --insert '{"name": "John", "email": "john@example.com"}'
  
  # UPDATE
  %(prog)s leads --update '{"status": "qualified"}' --filter "id=eq.123"
  
  # DELETE
  %(prog)s leads --delete --filter "id=eq.123"
        """
    )
    
    parser.add_argument('table', help='Table name')
    parser.add_argument('--select', default='*', help='Columns to select (default: *)')
    parser.add_argument('--filter', action='append', help='Filter (e.g., status=eq.qualified)')
    parser.add_argument('--order', help='Order by (e.g., created_at.desc)')
    parser.add_argument('--limit', type=int, help='Limit rows')
    parser.add_argument('--offset', type=int, help='Offset rows')
    parser.add_argument('--single', action='store_true', help='Return single row as object')
    parser.add_argument('--insert', help='JSON data to insert')
    parser.add_argument('--update', help='JSON data to update')
    parser.add_argument('--delete', action='store_true', help='Delete rows')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    
    args = parser.parse_args()
    
    try:
        client = NeonDataAPI()
        
        # INSERT
        if args.insert:
            data = json.loads(args.insert)
            result = client.insert(args.table, data)
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
        
        # UPDATE
        if args.update:
            if not args.filter:
                print("Error: UPDATE requires --filter", file=sys.stderr)
                sys.exit(1)
            data = json.loads(args.update)
            result = client.update(args.table, data, args.filter)
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
        
        # DELETE
        if args.delete:
            if not args.filter:
                print("Error: DELETE requires --filter", file=sys.stderr)
                sys.exit(1)
            client.delete(args.table, args.filter)
            print("Deleted successfully")
            return
        
        # SELECT (default)
        result = client.select(
            args.table,
            select=args.select,
            filters=args.filter,
            order=args.order,
            limit=args.limit,
            offset=args.offset,
            single=args.single
        )
        
        print(json.dumps(result, indent=2 if args.pretty else None))
    
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
