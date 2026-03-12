#!/usr/bin/env python3
"""
SQL Query CLI - Execute SQL directly on Teable base
"""

import argparse
import json
from extended import extended_client as client

def main():
    parser = argparse.ArgumentParser(description='Execute SQL query on Teable base')
    parser.add_argument('--base-id', required=True, help='Base ID')
    parser.add_argument('--sql', required=True, help='SQL query')
    parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    result = client.sql_query(args.base_id, args.sql)
    
    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        # Table format (simple)
        rows = result.get('rows', [])
        columns = result.get('columns', [])
        
        if not rows:
            print("No results")
            return
        
        # Print header
        print(" | ".join(columns))
        print("-" * (len(" | ".join(columns))))
        
        # Print rows
        for row in rows:
            print(" | ".join(str(v) for v in row))

if __name__ == '__main__':
    main()
