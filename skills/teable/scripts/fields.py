#!/usr/bin/env python3
"""
Field operations CLI
"""

import argparse
import json
from extended import extended_client as client

def main():
    parser = argparse.ArgumentParser(description='Teable field operations')
    parser.add_argument('action', choices=['list', 'get', 'create', 'update', 'delete', 'convert', 'duplicate'])
    parser.add_argument('--table-id', required=True, help='Table ID')
    parser.add_argument('--field-id', help='Field ID (for get/update/delete/convert/duplicate)')
    parser.add_argument('--name', help='Field name')
    parser.add_argument('--type', help='Field type (singleLineText, longText, number, singleSelect, etc.)')
    parser.add_argument('--description', help='Field description')
    parser.add_argument('--options', help='Field options JSON')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        result = client.list_fields(args.table_id)
    elif args.action == 'get':
        if not args.field_id:
            parser.error('--field-id required for get')
        result = client.get_field(args.table_id, args.field_id)
    elif args.action == 'create':
        if not args.name or not args.type:
            parser.error('--name and --type required for create')
        options = json.loads(args.options) if args.options else None
        result = client.create_field(
            args.table_id,
            args.name,
            args.type,
            options=options,
            description=args.description
        )
    elif args.action == 'update':
        if not args.field_id:
            parser.error('--field-id required for update')
        result = client.update_field(
            args.table_id,
            args.field_id,
            name=args.name,
            description=args.description
        )
    elif args.action == 'convert':
        if not args.field_id or not args.type:
            parser.error('--field-id and --type required for convert')
        options = json.loads(args.options) if args.options else None
        result = client.convert_field(
            args.table_id,
            args.field_id,
            args.type,
            options=options
        )
    elif args.action == 'delete':
        if not args.field_id:
            parser.error('--field-id required for delete')
        result = client.delete_field(args.table_id, args.field_id)
    elif args.action == 'duplicate':
        if not args.field_id:
            parser.error('--field-id required for duplicate')
        result = client.duplicate_field(args.table_id, args.field_id)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
