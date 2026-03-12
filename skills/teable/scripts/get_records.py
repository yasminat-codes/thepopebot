#!/usr/bin/env python3
"""
Get records from a Teable table
"""

import argparse
import json
from common import client, format_records_for_output

def main():
    parser = argparse.ArgumentParser(description='Get records from Teable table')
    
    # Required
    parser.add_argument('--table-id', required=True, help='Table ID (starts with tbl)')
    
    # Filtering/sorting
    parser.add_argument('--view-id', help='View ID to filter by')
    parser.add_argument('--filter', help='Filter JSON object')
    parser.add_argument('--order-by', help='Order by JSON array')
    parser.add_argument('--search', help='Search text')
    
    # Pagination
    parser.add_argument('--take', type=int, default=100, help='Number of records (max 1000)')
    parser.add_argument('--skip', type=int, default=0, help='Records to skip (pagination)')
    
    # Field selection
    parser.add_argument('--projection', help='Comma-separated field names to return')
    parser.add_argument('--field-key-type', choices=['name', 'id', 'dbFieldName'], default='name')
    parser.add_argument('--cell-format', choices=['json', 'text'], default='json')
    
    # Output
    parser.add_argument('--compact', action='store_true', help='Compact output format')
    parser.add_argument('--count-only', action='store_true', help='Return count only')
    
    args = parser.parse_args()
    
    # Parse JSON arguments
    filter_obj = json.loads(args.filter) if args.filter else None
    order_by = json.loads(args.order_by) if args.order_by else None
    projection = args.projection.split(',') if args.projection else None
    
    # Get records
    records = client.get_records(
        table_id=args.table_id,
        view_id=args.view_id,
        filter_obj=filter_obj,
        order_by=order_by,
        take=args.take,
        skip=args.skip,
        projection=projection,
        field_key_type=args.field_key_type,
        cell_format=args.cell_format
    )
    
    # Output
    if args.count_only:
        print(len(records))
    else:
        print(format_records_for_output(records, compact=args.compact))


if __name__ == '__main__':
    main()
