#!/usr/bin/env python3
"""
Neon Integration Patterns

Real-world integration examples for common use cases.
"""

import os
import json
from typing import Dict, List, Optional
import psycopg2
import psycopg2.extras
import requests


# =============================================================================
# PATTERN 1: API Endpoint with Neon Data API
# =============================================================================

def api_endpoint_example():
    """
    Example: FastAPI endpoint using Neon Data API
    """
    from fastapi import FastAPI, HTTPException, Header
    from pydantic import BaseModel
    
    app = FastAPI()
    
    class Post(BaseModel):
        title: str
        content: str
        is_published: bool = False
    
    @app.post("/posts")
    async def create_post(
        post: Post,
        authorization: str = Header(...)
    ):
        """Create a new post using Data API."""
        # Authorization header contains JWT token
        token = authorization.replace("Bearer ", "")
        
        response = requests.post(
            f"{os.getenv('NEON_DATA_API_URL')}/posts",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            json={
                'title': post.title,
                'content': post.content,
                'is_published': post.is_published
            }
        )
        
        if response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
        
        return response.json()[0]
    
    @app.get("/posts")
    async def list_posts(
        limit: int = 10,
        offset: int = 0,
        authorization: str = Header(...)
    ):
        """List published posts."""
        token = authorization.replace("Bearer ", "")
        
        response = requests.get(
            f"{os.getenv('NEON_DATA_API_URL')}/posts",
            headers={'Authorization': f'Bearer {token}'},
            params={
                'is_published': 'eq.true',
                'order': 'created_at.desc',
                'limit': limit,
                'offset': offset
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
        
        return response.json()


# =============================================================================
# PATTERN 2: Background Worker with Direct SQL
# =============================================================================

def background_worker_example():
    """
    Example: Celery worker processing posts with direct SQL
    """
    from celery import Celery
    
    app = Celery('tasks', broker='redis://localhost:6379')
    
    @app.task
    def process_post(post_id: int):
        """Process a post (e.g., generate summary, extract keywords)."""
        conn = psycopg2.connect(
            os.getenv('NEON_DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cur = conn.cursor()
        
        try:
            # Get post
            cur.execute("""
                SELECT id, content, title
                FROM posts
                WHERE id = %s
            """, (post_id,))
            
            post = cur.fetchone()
            if not post:
                return {'error': 'Post not found'}
            
            # Process content (example: extract keywords)
            keywords = extract_keywords(post['content'])
            
            # Update post with keywords
            cur.execute("""
                UPDATE posts
                SET metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{keywords}',
                    %s::jsonb
                )
                WHERE id = %s
            """, (json.dumps(keywords), post_id))
            
            conn.commit()
            
            return {
                'post_id': post_id,
                'keywords': keywords
            }
        
        except Exception as e:
            conn.rollback()
            raise
        
        finally:
            cur.close()
            conn.close()
    
    def extract_keywords(text: str) -> List[str]:
        """Dummy keyword extraction."""
        # In production, use NLP library
        words = text.lower().split()
        return list(set(w for w in words if len(w) > 5))[:10]


# =============================================================================
# PATTERN 3: Webhook Handler with Transaction
# =============================================================================

def webhook_handler_example():
    """
    Example: Handle incoming webhooks with transactional processing
    """
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    @app.route('/webhook/stripe', methods=['POST'])
    def stripe_webhook():
        """Handle Stripe payment webhook."""
        payload = request.json
        
        conn = psycopg2.connect(os.getenv('NEON_DATABASE_URL'))
        cur = conn.cursor()
        
        try:
            if payload['type'] == 'payment_intent.succeeded':
                payment_intent = payload['data']['object']
                user_id = payment_intent['metadata']['user_id']
                amount = payment_intent['amount'] / 100  # Convert cents to dollars
                
                # Credit user account
                cur.execute("""
                    UPDATE users
                    SET credits = credits + %s
                    WHERE id = %s
                """, (amount, user_id))
                
                # Log transaction
                cur.execute("""
                    INSERT INTO transactions (user_id, type, amount, stripe_payment_id)
                    VALUES (%s, 'credit', %s, %s)
                """, (user_id, amount, payment_intent['id']))
                
                # Send notification
                cur.execute("""
                    INSERT INTO notifications (user_id, type, message)
                    VALUES (%s, 'payment_success', %s)
                """, (
                    user_id,
                    f'Payment of ${amount:.2f} received. Your account has been credited.'
                ))
                
                conn.commit()
                
                return jsonify({'success': True})
        
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        
        finally:
            cur.close()
            conn.close()


# =============================================================================
# PATTERN 4: Real-time Sync (Change Data Capture)
# =============================================================================

def cdc_example():
    """
    Example: Listen to database changes using PostgreSQL NOTIFY/LISTEN
    """
    import select
    
    conn = psycopg2.connect(os.getenv('NEON_DATABASE_URL'))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Create notification trigger
    cur.execute("""
        CREATE OR REPLACE FUNCTION notify_post_changes()
        RETURNS trigger AS $$
        DECLARE
          payload json;
        BEGIN
          payload = json_build_object(
            'table', TG_TABLE_NAME,
            'action', TG_OP,
            'id', NEW.id,
            'user_id', NEW.user_id,
            'timestamp', now()
          );
          
          PERFORM pg_notify('post_changes', payload::text);
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS post_changes_trigger ON posts;
        CREATE TRIGGER post_changes_trigger
        AFTER INSERT OR UPDATE OR DELETE ON posts
        FOR EACH ROW EXECUTE FUNCTION notify_post_changes();
    """)
    
    # Listen for notifications
    cur.execute("LISTEN post_changes;")
    
    print("Listening for post changes...")
    
    while True:
        if select.select([conn], [], [], 5) == ([], [], []):
            # Timeout, check if still connected
            continue
        
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            payload = json.loads(notify.payload)
            
            print(f"Change detected: {payload}")
            
            # Process the change (e.g., update cache, send to queue, etc.)
            handle_post_change(payload)


def handle_post_change(payload: Dict):
    """Handle post change notification."""
    # Example: Invalidate cache, send to message queue, etc.
    print(f"Processing {payload['action']} on post {payload['id']}")


# =============================================================================
# PATTERN 5: Multi-tenancy with Branch per Tenant
# =============================================================================

class TenantManager:
    """Manage multi-tenant setup using Neon branches."""
    
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = 'https://console.neon.tech/api/v2'
    
    def create_tenant(self, tenant_name: str) -> Dict:
        """Create a new tenant with dedicated branch."""
        # Create branch for tenant
        response = requests.post(
            f'{self.base_url}/projects/{self.project_id}/branches',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'branch': {
                    'name': f'tenant-{tenant_name}'
                },
                'endpoints': [{'type': 'read_write'}]
            }
        )
        
        response.raise_for_status()
        branch = response.json()['branch']
        
        # Get connection string
        conn_response = requests.get(
            f'{self.base_url}/projects/{self.project_id}/connection_uri',
            headers={'Authorization': f'Bearer {self.api_key}'},
            params={'branch_id': branch['id']}
        )
        
        connection_uri = conn_response.json()['uri']
        
        # Run tenant initialization SQL
        self._initialize_tenant_schema(connection_uri)
        
        return {
            'tenant_name': tenant_name,
            'branch_id': branch['id'],
            'connection_uri': connection_uri
        }
    
    def _initialize_tenant_schema(self, connection_uri: str):
        """Initialize schema for new tenant."""
        conn = psycopg2.connect(connection_uri)
        cur = conn.cursor()
        
        try:
            # Run initialization SQL (tables, RLS, etc.)
            with open('migrations/001_initial_schema.sql', 'r') as f:
                cur.execute(f.read())
            
            conn.commit()
        
        finally:
            cur.close()
            conn.close()
    
    def get_tenant_connection(self, tenant_name: str) -> str:
        """Get connection string for a tenant."""
        # In production, cache this mapping
        response = requests.get(
            f'{self.base_url}/projects/{self.project_id}/branches',
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        branches = response.json()['branches']
        for branch in branches:
            if branch['name'] == f'tenant-{tenant_name}':
                # Get connection string
                conn_response = requests.get(
                    f'{self.base_url}/projects/{self.project_id}/connection_uri',
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    params={'branch_id': branch['id']}
                )
                return conn_response.json()['uri']
        
        raise ValueError(f'Tenant {tenant_name} not found')


# =============================================================================
# PATTERN 6: Connection Pool Manager
# =============================================================================

class ConnectionPoolManager:
    """Manage connection pools for multiple databases."""
    
    def __init__(self):
        self.pools: Dict[str, psycopg2.pool.SimpleConnectionPool] = {}
    
    def get_pool(self, connection_url: str, min_conn: int = 1, max_conn: int = 10):
        """Get or create connection pool."""
        if connection_url not in self.pools:
            self.pools[connection_url] = psycopg2.pool.SimpleConnectionPool(
                minconn=min_conn,
                maxconn=max_conn,
                dsn=connection_url
            )
        
        return self.pools[connection_url]
    
    def execute_query(self, connection_url: str, query: str, params=None):
        """Execute query using pooled connection."""
        pool = self.get_pool(connection_url)
        conn = pool.getconn()
        
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cur.fetchall()
                return [dict(row) for row in result]
            else:
                conn.commit()
                return {'rowcount': cur.rowcount}
        
        finally:
            pool.putconn(conn)
    
    def close_all(self):
        """Close all pools."""
        for pool in self.pools.values():
            pool.closeall()


# =============================================================================
# PATTERN 7: ETL Pipeline
# =============================================================================

def etl_pipeline_example():
    """
    Example: ETL pipeline extracting data from external source to Neon
    """
    import pandas as pd
    
    # Extract: Get data from external source (API, CSV, etc.)
    def extract_from_api() -> pd.DataFrame:
        response = requests.get('https://api.example.com/data')
        return pd.DataFrame(response.json())
    
    # Transform: Clean and transform data
    def transform_data(df: pd.DataFrame) -> pd.DataFrame:
        # Clean column names
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        
        # Handle nulls
        df = df.fillna('')
        
        # Add metadata
        df['imported_at'] = pd.Timestamp.now()
        
        return df
    
    # Load: Insert into Neon
    def load_to_neon(df: pd.DataFrame):
        conn = psycopg2.connect(os.getenv('NEON_DATABASE_URL'))
        cur = conn.cursor()
        
        try:
            # Bulk insert using execute_values
            from psycopg2.extras import execute_values
            
            values = [tuple(row) for row in df.values]
            
            execute_values(
                cur,
                """
                INSERT INTO imported_data (field1, field2, field3, imported_at)
                VALUES %s
                ON CONFLICT (field1) DO UPDATE SET
                    field2 = EXCLUDED.field2,
                    field3 = EXCLUDED.field3,
                    imported_at = EXCLUDED.imported_at
                """,
                values
            )
            
            conn.commit()
            print(f"Loaded {len(df)} rows")
        
        except Exception as e:
            conn.rollback()
            raise
        
        finally:
            cur.close()
            conn.close()
    
    # Run pipeline
    df = extract_from_api()
    df = transform_data(df)
    load_to_neon(df)


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == '__main__':
    print("Neon Integration Patterns")
    print("=" * 50)
    
    # Uncomment to test specific patterns
    # api_endpoint_example()
    # background_worker_example()
    # webhook_handler_example()
    # cdc_example()
    
    # Multi-tenancy example
    # manager = TenantManager(
    #     api_key=os.getenv('NEON_API_KEY'),
    #     project_id='your-project-id'
    # )
    # tenant_info = manager.create_tenant('acme-corp')
    # print(tenant_info)
    
    # Connection pool example
    # pool_manager = ConnectionPoolManager()
    # result = pool_manager.execute_query(
    #     os.getenv('NEON_DATABASE_URL'),
    #     'SELECT * FROM posts WHERE is_published = %s LIMIT 10',
    #     (True,)
    # )
    # print(result)
    
    # ETL example
    # etl_pipeline_example()
    
    print("\nTo run an example, uncomment it in the __main__ section")
