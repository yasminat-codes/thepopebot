#!/usr/bin/env python3
"""
Common utilities for Teable API integration
"""

import os
import requests
from typing import Dict, List, Optional, Any
import json

# Configuration
TEABLE_API_TOKEN = os.environ.get('TEABLE_API_TOKEN')
TEABLE_BASE_URL = os.environ.get('TEABLE_BASE_URL', 'https://app.teable.ai')

if not TEABLE_API_TOKEN:
    raise ValueError("TEABLE_API_TOKEN environment variable not set")


class TeableClient:
    """Teable API client"""
    
    def __init__(self, api_token: str = None, base_url: str = None):
        self.api_token = api_token or TEABLE_API_TOKEN
        self.base_url = (base_url or TEABLE_BASE_URL).rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None
    ) -> Dict:
        """Make HTTP request to Teable API"""
        
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {}
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise Exception(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}") from e
    
    def get_records(
        self,
        table_id: str,
        view_id: Optional[str] = None,
        filter_obj: Optional[Dict] = None,
        order_by: Optional[List[Dict]] = None,
        take: int = 100,
        skip: int = 0,
        projection: Optional[List[str]] = None,
        field_key_type: str = "name",
        cell_format: str = "json"
    ) -> List[Dict]:
        """
        Get records from a table
        
        Args:
            table_id: Table ID (starts with 'tbl')
            view_id: Optional view ID to filter by
            filter_obj: Filter conditions object
            order_by: Sort specification
            take: Number of records to return (max 1000)
            skip: Number of records to skip (pagination)
            projection: List of field names/IDs to return
            field_key_type: 'name', 'id', or 'dbFieldName'
            cell_format: 'json' or 'text'
        
        Returns:
            List of record dictionaries
        """
        
        params = {
            'take': min(take, 1000),
            'skip': skip,
            'fieldKeyType': field_key_type,
            'cellFormat': cell_format
        }
        
        if view_id:
            params['viewId'] = view_id
        
        if filter_obj:
            params['filter'] = json.dumps(filter_obj)
        
        if order_by:
            params['orderBy'] = json.dumps(order_by)
        
        if projection:
            params['projection'] = json.dumps(projection)
        
        result = self._make_request('GET', f'/table/{table_id}/record', params=params)
        return result.get('records', [])
    
    def get_record(
        self,
        table_id: str,
        record_id: str,
        field_key_type: str = "name",
        cell_format: str = "json"
    ) -> Dict:
        """
        Get a single record by ID
        
        Args:
            table_id: Table ID
            record_id: Record ID (starts with 'rec')
            field_key_type: 'name', 'id', or 'dbFieldName'
            cell_format: 'json' or 'text'
        
        Returns:
            Record dictionary
        """
        
        params = {
            'fieldKeyType': field_key_type,
            'cellFormat': cell_format
        }
        
        return self._make_request('GET', f'/table/{table_id}/record/{record_id}', params=params)
    
    def create_records(
        self,
        table_id: str,
        records: List[Dict],
        typecast: bool = False,
        field_key_type: str = "name"
    ) -> Dict:
        """
        Create one or more records
        
        Args:
            table_id: Table ID
            records: List of record objects with 'fields' key
            typecast: Auto-convert field value types
            field_key_type: 'name', 'id', or 'dbFieldName'
        
        Returns:
            Response with created records
        """
        
        data = {
            'records': records,
            'fieldKeyType': field_key_type
        }
        
        if typecast:
            data['typecast'] = True
        
        return self._make_request('POST', f'/table/{table_id}/record', data=data)
    
    def update_record(
        self,
        table_id: str,
        record_id: str,
        fields: Dict,
        typecast: bool = False,
        field_key_type: str = "name"
    ) -> Dict:
        """
        Update a single record
        
        Args:
            table_id: Table ID
            record_id: Record ID
            fields: Dictionary of field names/IDs to values
            typecast: Auto-convert field value types
            field_key_type: 'name', 'id', or 'dbFieldName'
        
        Returns:
            Updated record
        """
        
        record = {
            'fields': fields,
            'fieldKeyType': field_key_type
        }

        if typecast:
            record['typecast'] = True

        data = {'record': record}

        return self._make_request('PATCH', f'/table/{table_id}/record/{record_id}', data=data)
    
    def update_records(
        self,
        table_id: str,
        records: List[Dict],
        typecast: bool = False,
        field_key_type: str = "name"
    ) -> Dict:
        """
        Update multiple records in one request
        
        Args:
            table_id: Table ID
            records: List of records with 'id' and 'fields' keys
            typecast: Auto-convert field value types
            field_key_type: 'name', 'id', or 'dbFieldName'
        
        Returns:
            Response with updated records
        """
        
        data = {
            'records': records,
            'fieldKeyType': field_key_type
        }
        
        if typecast:
            data['typecast'] = True
        
        return self._make_request('PATCH', f'/table/{table_id}/record', data=data)
    
    def delete_records(
        self,
        table_id: str,
        record_ids: List[str]
    ) -> Dict:
        """
        Delete one or more records
        
        Args:
            table_id: Table ID
            record_ids: List of record IDs to delete
        
        Returns:
            Response confirming deletion
        """
        
        data = {'recordIds': record_ids}
        return self._make_request('DELETE', f'/table/{table_id}/record', data=data)


def format_records_for_output(records: List[Dict], compact: bool = False) -> str:
    """Format records for human-readable output"""
    
    if not records:
        return "No records found."
    
    if compact:
        # Compact format - one line per record
        lines = []
        for rec in records:
            fields_str = ", ".join(f"{k}: {v}" for k, v in rec.get('fields', {}).items())
            lines.append(f"[{rec['id']}] {fields_str}")
        return "\n".join(lines)
    else:
        # Full format - JSON pretty print
        return json.dumps(records, indent=2)


def build_filter(conditions: List[Dict], conjunction: str = "and") -> Dict:
    """
    Helper to build filter objects
    
    Args:
        conditions: List of condition dicts
        conjunction: 'and' or 'or'
    
    Returns:
        Filter object
    
    Example:
        build_filter([
            {"fieldId": "fldStatus", "operator": "is", "value": "Open"},
            {"fieldId": "fldPriority", "operator": "isGreater", "value": 2}
        ])
    """
    
    return {
        "conjunction": conjunction,
        "filterSet": conditions
    }


def build_order_by(field_id: str, order: str = "asc") -> List[Dict]:
    """
    Helper to build orderBy arrays
    
    Args:
        field_id: Field ID or name
        order: 'asc' or 'desc'
    
    Returns:
        orderBy array
    """
    
    return [{"fieldId": field_id, "order": order}]


# Global client instance
client = TeableClient()
