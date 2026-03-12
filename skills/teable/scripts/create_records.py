#!/usr/bin/env python3
"""
Create records in a Teable table
"""

import argparse
import json
from common import client

def main():
    parser = argparse.ArgumentParser(description='Create records in Teable table')
    
    # Required
    parser.add_argument('--table-id', required=True, help='Table ID (starts with tbl)')
    parser.add_argument('--records', required=True, help='JSON array of records with fields')
    
    # Options
    parser.add_argument('--typecast', action='store_true', help='Auto-convert field types')
    parser.add_argument('--field-key-type', choices=['name', 'id', 'dbFieldName'], default='name')
    
    args = parser.parse_args()
    
    # Parse records JSON
    records = json.loads(args.records)
    
    # Ensure records is a list
    if isinstance(records, dict):
        records = [records]
    
    # Create records
    result = client.create_records(
        table_id=args.table_id,
        records=records,
        typecast=args.typecast,
        field_key_type=args.field_key_type
    )
    
    # Output
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
