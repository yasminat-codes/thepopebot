#!/usr/bin/env python3
"""
Extended Teable API Client - All Endpoints

Covers fields, views, comments, attachments, SQL, aggregations, sharing, and more
"""

from common import TeableClient
from typing import Dict, List, Optional, Any
import json


class TeableExtendedClient(TeableClient):
    """Extended Teable API client with all endpoints"""
    
    # ==================== FIELD OPERATIONS ====================
    
    def list_fields(
        self,
        table_id: str,
        view_id: Optional[str] = None
    ) -> List[Dict]:
        """
        List all fields in a table
        
        Args:
            table_id: Table ID
            view_id: Optional view ID to filter fields
        
        Returns:
            List of field objects
        """
        
        params = {}
        if view_id:
            params['viewId'] = view_id
        
        return self._make_request('GET', f'/table/{table_id}/field', params=params)
    
    def get_field(
        self,
        table_id: str,
        field_id: str
    ) -> Dict:
        """
        Get a specific field by ID
        
        Args:
            table_id: Table ID
            field_id: Field ID (starts with 'fld')
        
        Returns:
            Field object
        """
        
        return self._make_request('GET', f'/table/{table_id}/field/{field_id}')
    
    def create_field(
        self,
        table_id: str,
        name: str,
        field_type: str,
        options: Optional[Dict] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Create a new field in a table
        
        Args:
            table_id: Table ID
            name: Field name
            field_type: Field type (singleLineText, longText, number, singleSelect, etc.)
            options: Field-specific options
            description: Field description
        
        Returns:
            Created field object
        """
        
        data = {
            'name': name,
            'type': field_type
        }
        
        if options:
            data['options'] = options
        
        if description:
            data['description'] = description
        
        return self._make_request('POST', f'/table/{table_id}/field', data=data)
    
    def update_field(
        self,
        table_id: str,
        field_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Update field properties (name, description only)
        
        For type changes, use convert_field()
        
        Args:
            table_id: Table ID
            field_id: Field ID
            name: New field name
            description: New description
        
        Returns:
            Updated field object
        """
        
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        
        return self._make_request('PATCH', f'/table/{table_id}/field/{field_id}', data=data)
    
    def convert_field(
        self,
        table_id: str,
        field_id: str,
        new_type: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Convert field to a different type
        
        Args:
            table_id: Table ID
            field_id: Field ID
            new_type: New field type
            options: New field options
        
        Returns:
            Converted field object
        """
        
        data = {'type': new_type}
        if options:
            data['options'] = options
        
        return self._make_request('PUT', f'/table/{table_id}/field/{field_id}/convert', data=data)
    
    def delete_field(
        self,
        table_id: str,
        field_id: str
    ) -> Dict:
        """
        Delete a field
        
        Args:
            table_id: Table ID
            field_id: Field ID
        
        Returns:
            Deletion confirmation
        """
        
        return self._make_request('DELETE', f'/table/{table_id}/field/{field_id}')
    
    def duplicate_field(
        self,
        table_id: str,
        field_id: str
    ) -> Dict:
        """
        Duplicate a field
        
        Args:
            table_id: Table ID
            field_id: Field ID to duplicate
        
        Returns:
            New field object
        """
        
        return self._make_request('POST', f'/table/{table_id}/field/{field_id}/duplicate')
    
    # ==================== VIEW OPERATIONS ====================
    
    def list_views(
        self,
        table_id: str
    ) -> List[Dict]:
        """
        List all views in a table
        
        Args:
            table_id: Table ID
        
        Returns:
            List of view objects
        """
        
        return self._make_request('GET', f'/table/{table_id}/view')
    
    def get_view(
        self,
        table_id: str,
        view_id: str
    ) -> Dict:
        """
        Get a specific view
        
        Args:
            table_id: Table ID
            view_id: View ID
        
        Returns:
            View object
        """
        
        return self._make_request('GET', f'/table/{table_id}/view/{view_id}')
    
    def create_view(
        self,
        table_id: str,
        name: str,
        view_type: str = "grid",
        description: Optional[str] = None
    ) -> Dict:
        """
        Create a new view
        
        Args:
            table_id: Table ID
            name: View name
            view_type: grid, form, kanban, gallery, calendar
            description: View description
        
        Returns:
            Created view object
        """
        
        data = {
            'name': name,
            'type': view_type
        }
        
        if description:
            data['description'] = description
        
        return self._make_request('POST', f'/table/{table_id}/view', data=data)
    
    def update_view(
        self,
        table_id: str,
        view_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        filter: Optional[Dict] = None,
        sort: Optional[List[Dict]] = None,
        group: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Update view properties
        
        Args:
            table_id: Table ID
            view_id: View ID
            name: New name
            description: New description
            filter: Filter configuration
            sort: Sort configuration
            group: Group configuration
        
        Returns:
            Updated view object
        """
        
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if filter:
            data['filter'] = filter
        if sort:
            data['sort'] = sort
        if group:
            data['group'] = group
        
        return self._make_request('PATCH', f'/table/{table_id}/view/{view_id}', data=data)
    
    def delete_view(
        self,
        table_id: str,
        view_id: str
    ) -> Dict:
        """
        Delete a view
        
        Args:
            table_id: Table ID
            view_id: View ID
        
        Returns:
            Deletion confirmation
        """
        
        return self._make_request('DELETE', f'/table/{table_id}/view/{view_id}')
    
    # ==================== COMMENTS ====================
    
    def list_comments(
        self,
        table_id: str,
        record_id: str
    ) -> List[Dict]:
        """
        List all comments on a record
        
        Args:
            table_id: Table ID
            record_id: Record ID
        
        Returns:
            List of comment objects
        """
        
        return self._make_request('GET', f'/comment/{table_id}/{record_id}/list')
    
    def get_comment(
        self,
        comment_id: str
    ) -> Dict:
        """
        Get a specific comment
        
        Args:
            comment_id: Comment ID
        
        Returns:
            Comment object
        """
        
        return self._make_request('GET', f'/comment/{comment_id}')
    
    def create_comment(
        self,
        table_id: str,
        record_id: str,
        content: str
    ) -> Dict:
        """
        Create a comment on a record
        
        Args:
            table_id: Table ID
            record_id: Record ID
            content: Comment text
        
        Returns:
            Created comment object
        """
        
        data = {'content': content}
        return self._make_request('POST', f'/comment/{table_id}/{record_id}/create', data=data)
    
    def update_comment(
        self,
        comment_id: str,
        content: str
    ) -> Dict:
        """
        Update a comment
        
        Args:
            comment_id: Comment ID
            content: New comment text
        
        Returns:
            Updated comment object
        """
        
        data = {'content': content}
        return self._make_request('PATCH', f'/comment/{comment_id}', data=data)
    
    def delete_comment(
        self,
        comment_id: str
    ) -> Dict:
        """
        Delete a comment
        
        Args:
            comment_id: Comment ID
        
        Returns:
            Deletion confirmation
        """
        
        return self._make_request('DELETE', f'/comment/{comment_id}')
    
    # ==================== ATTACHMENTS ====================
    
    def upload_attachment(
        self,
        table_id: str,
        record_id: str,
        field_id: str,
        file_path: Optional[str] = None,
        url: Optional[str] = None
    ) -> Dict:
        """
        Upload attachment to a record
        
        Either file_path OR url must be provided
        
        Args:
            table_id: Table ID
            record_id: Record ID
            field_id: Attachment field ID
            file_path: Local file path
            url: URL to download file from
        
        Returns:
            Upload result
        """
        
        if file_path:
            # TODO: Implement file upload
            raise NotImplementedError("File upload from local path not yet implemented")
        elif url:
            data = {'url': url}
            return self._make_request(
                'POST',
                f'/table/{table_id}/record/{record_id}/attachments',
                data=data,
                params={'fieldId': field_id}
            )
        else:
            raise ValueError("Either file_path or url must be provided")
    
    # ==================== SQL QUERY ====================
    
    def sql_query(
        self,
        base_id: str,
        sql: str
    ) -> Dict:
        """
        Execute SQL query on base
        
        Args:
            base_id: Base ID
            sql: SQL query string
        
        Returns:
            Query results
        """
        
        data = {'sql': sql}
        return self._make_request('POST', f'/base/{base_id}/sql-query', data=data)
    
    # ==================== AGGREGATIONS ====================
    
    def get_aggregation(
        self,
        table_id: str,
        view_id: str,
        aggregation_field_id: str,
        aggregation_func: str = "sum"
    ) -> Dict:
        """
        Get aggregation statistics
        
        Args:
            table_id: Table ID
            view_id: View ID
            aggregation_field_id: Field to aggregate
            aggregation_func: sum, avg, min, max, count, etc.
        
        Returns:
            Aggregation results
        """
        
        params = {
            'viewId': view_id,
            'fieldId': aggregation_field_id,
            'func': aggregation_func
        }
        
        return self._make_request('GET', f'/table/{table_id}/aggregation', params=params)
    
    def get_row_count(
        self,
        table_id: str,
        view_id: str
    ) -> Dict:
        """
        Get total row count in a view
        
        Args:
            table_id: Table ID
            view_id: View ID
        
        Returns:
            Row count
        """
        
        params = {'viewId': view_id}
        return self._make_request('GET', f'/aggregation/{table_id}/{view_id}/row-count', params=params)
    
    def get_group_points(
        self,
        table_id: str,
        view_id: str
    ) -> Dict:
        """
        Get group points (record distribution by groups)
        
        Args:
            table_id: Table ID
            view_id: View ID with grouping
        
        Returns:
            Group distribution data
        """
        
        return self._make_request('GET', f'/aggregation/{table_id}/{view_id}/group-points')
    
    # ==================== BASE & TABLE OPERATIONS ====================
    
    def list_bases(
        self,
        space_id: str
    ) -> List[Dict]:
        """
        List all bases in a space
        
        Args:
            space_id: Space ID
        
        Returns:
            List of base objects
        """
        
        return self._make_request('GET', f'/space/{space_id}/base')
    
    def get_base(
        self,
        base_id: str
    ) -> Dict:
        """
        Get base information
        
        Args:
            base_id: Base ID
        
        Returns:
            Base object
        """
        
        return self._make_request('GET', f'/base/{base_id}')
    
    def create_table(
        self,
        base_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Dict:
        """
        Create a new table in a base
        
        Args:
            base_id: Base ID
            name: Table name
            description: Table description
        
        Returns:
            Created table object
        """
        
        data = {'name': name}
        if description:
            data['description'] = description
        
        return self._make_request('POST', f'/base/{base_id}/table', data=data)
    
    def update_table(
        self,
        table_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Update table properties
        
        Args:
            table_id: Table ID
            name: New name
            description: New description
        
        Returns:
            Updated table object
        """
        
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        
        return self._make_request('PATCH', f'/table/{table_id}', data=data)
    
    def delete_table(
        self,
        table_id: str
    ) -> Dict:
        """
        Delete a table
        
        Args:
            table_id: Table ID
        
        Returns:
            Deletion confirmation
        """
        
        return self._make_request('DELETE', f'/table/{table_id}')
    
    # ==================== SHARING ====================
    
    def create_share_view(
        self,
        table_id: str,
        view_id: str,
        password: Optional[str] = None
    ) -> Dict:
        """
        Create a shareable link for a view
        
        Args:
            table_id: Table ID
            view_id: View ID
            password: Optional password protection
        
        Returns:
            Share link object
        """
        
        data = {'viewId': view_id}
        if password:
            data['password'] = password
        
        return self._make_request('POST', f'/share/{table_id}/view', data=data)
    
    def get_share_view(
        self,
        share_id: str
    ) -> Dict:
        """
        Get shared view information
        
        Args:
            share_id: Share ID
        
        Returns:
            Share view object
        """
        
        return self._make_request('GET', f'/share/{share_id}/view')
    
    def delete_share_view(
        self,
        share_id: str
    ) -> Dict:
        """
        Delete a shared view
        
        Args:
            share_id: Share ID
        
        Returns:
            Deletion confirmation
        """
        
        return self._make_request('DELETE', f'/share/{share_id}')


# Global extended client instance
extended_client = TeableExtendedClient()


if __name__ == "__main__":
    print("Teable Extended API Client")
    print("=" * 50)
    print("\nAvailable operations:")
    print("\n🗂️  Fields:")
    print("  - list_fields, get_field, create_field")
    print("  - update_field, convert_field, delete_field, duplicate_field")
    print("\n👁️  Views:")
    print("  - list_views, get_view, create_view")
    print("  - update_view, delete_view")
    print("\n💬 Comments:")
    print("  - list_comments, get_comment, create_comment")
    print("  - update_comment, delete_comment")
    print("\n📎 Attachments:")
    print("  - upload_attachment")
    print("\n🔍 SQL:")
    print("  - sql_query")
    print("\n📊 Aggregations:")
    print("  - get_aggregation, get_row_count, get_group_points")
    print("\n🗄️  Bases & Tables:")
    print("  - list_bases, get_base")
    print("  - create_table, update_table, delete_table")
    print("\n🔗 Sharing:")
    print("  - create_share_view, get_share_view, delete_share_view")
