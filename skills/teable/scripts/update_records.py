#!/usr/bin/env python3
"""
Update records in a Teable table
"""

import argparse
import json
from common import client

def main():
    parser = argparse.ArgumentParser(description='Update records in Teable table')
    
    # Single record update
    parser.add_argument('--table-id', required=True, help='Table ID (starts with tbl)')
    parser.add_argument('--record-id', help='Single record ID to update')
    parser.add_argument('--fields', help='JSON object of fields to update')
    
    # Batch update
    parser.add_argument('--records', help='JSON array of records (with id and fields)')
    
    # Options
    parser.add_argument('--typecast', action='store_true', help='Auto-convert field types')
    parser.add_argument('--field-key-type', choices=['name', 'id', 'dbFieldName'], default='name')
    
    args = parser.parse_args()
    
    # Single or batch update
    if args.record_id and args.fields:
        # Single record update
        fields = json.loads(args.fields)
        result = client.update_record(
            table_id=args.table_id,
            record_id=args.record_id,
            fields=fields,
            typecast=args.typecast,
            field_key_type=args.field_key_type
        )
    elif args.records:
        # Batch update
        records = json.loads(args.records)
        result = client.update_records(
            table_id=args.table_id,
            records=records,
            typecast=args.typecast,
            field_key_type=args.field_key_type
        )
    else:
        parser.error('Either --record-id + --fields OR --records required')
    
    # Output
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
