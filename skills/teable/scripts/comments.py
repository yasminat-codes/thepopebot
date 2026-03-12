#!/usr/bin/env python3
"""
Comment operations CLI
"""

import argparse
import json
from extended import extended_client as client

def main():
    parser = argparse.ArgumentParser(description='Teable comment operations')
    parser.add_argument('action', choices=['list', 'get', 'create', 'update', 'delete'])
    parser.add_argument('--table-id', help='Table ID (for list/create)')
    parser.add_argument('--record-id', help='Record ID (for list/create)')
    parser.add_argument('--comment-id', help='Comment ID (for get/update/delete)')
    parser.add_argument('--content', help='Comment content')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        if not args.table_id or not args.record_id:
            parser.error('--table-id and --record-id required for list')
        result = client.list_comments(args.table_id, args.record_id)
    elif args.action == 'get':
        if not args.comment_id:
            parser.error('--comment-id required for get')
        result = client.get_comment(args.comment_id)
    elif args.action == 'create':
        if not args.table_id or not args.record_id or not args.content:
            parser.error('--table-id, --record-id, and --content required for create')
        result = client.create_comment(args.table_id, args.record_id, args.content)
    elif args.action == 'update':
        if not args.comment_id or not args.content:
            parser.error('--comment-id and --content required for update')
        result = client.update_comment(args.comment_id, args.content)
    elif args.action == 'delete':
        if not args.comment_id:
            parser.error('--comment-id required for delete')
        result = client.delete_comment(args.comment_id)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
