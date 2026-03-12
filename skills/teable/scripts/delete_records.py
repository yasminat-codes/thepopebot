#!/usr/bin/env python3
"""
Delete records from a Teable table
"""

import argparse
import json
from common import client

def main():
    parser = argparse.ArgumentParser(description='Delete records from Teable table')
    
    parser.add_argument('--table-id', required=True, help='Table ID (starts with tbl)')
    parser.add_argument('--record-ids', required=True, nargs='+', help='Record IDs to delete')
    parser.add_argument('--confirm', action='store_true', help='Confirm deletion (required)')
    
    args = parser.parse_args()
    
    if not args.confirm:
        print("⚠️  Deletion requires --confirm flag")
        print(f"   This will permanently delete {len(args.record_ids)} record(s)")
        return 1
    
    # Delete records
    result = client.delete_records(
        table_id=args.table_id,
        record_ids=args.record_ids
    )
    
    # Output
    print(f"✅ Deleted {len(args.record_ids)} record(s)")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
