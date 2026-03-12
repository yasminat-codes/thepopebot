#!/home/clawdbot/venvs/neon/bin/python3
"""
Neon Direct SQL Execution
Execute raw SQL queries via psycopg2
"""

import os
import sys
import json
import argparse
import psycopg2
import psycopg2.extras
from typing import Any, List, Dict

class NeonSQL:
    """Direct SQL execution client"""
    
    def __init__(self, pooled: bool = False):
        env_var = 'NEON_DATABASE_URL_POOLED' if pooled else 'NEON_DATABASE_URL'
        self.connection_string = os.getenv(env_var)
        
        if not self.connection_string:
            raise ValueError(f"{env_var} not set in environment")
    
    def execute(self, sql: str, params: tuple = None, 
                fetch: bool = True) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                
                if fetch and cur.description:
                    # Query returns rows
                    results = [dict(row) for row in cur.fetchall()]
                    conn.commit()
                    return results
                else:
                    # Mutation or no return
                    conn.commit()
                    return [{"rows_affected": cur.rowcount}]
        
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        
        finally:
            if conn:
                conn.close()

def main():
    parser = argparse.ArgumentParser(
        description='Execute raw SQL on Neon PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SELECT
  %(prog)s "SELECT * FROM leads WHERE status = 'qualified' LIMIT 5"
  
  # INSERT
  %(prog)s "INSERT INTO leads (name, email) VALUES ('John', 'john@example.com') RETURNING id"
  
  # UPDATE
  %(prog)s "UPDATE leads SET status = 'qualified' WHERE id = 123"
  
  # CREATE TABLE
  %(prog)s "CREATE TABLE IF NOT EXISTS test (id serial PRIMARY KEY, name text)"
  
  # From file
  %(prog)s --file migrations/001_create_leads.sql
        """
    )
    
    parser.add_argument('sql', nargs='?', help='SQL query to execute')
    parser.add_argument('--file', help='Read SQL from file')
    parser.add_argument('--pooled', action='store_true', 
                       help='Use pooled connection (for serverless)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    parser.add_argument('--no-fetch', action='store_true', 
                       help='Do not fetch results (for mutations)')
    
    args = parser.parse_args()
    
    # Get SQL from args or file
    if args.file:
        with open(args.file, 'r') as f:
            sql = f.read()
    elif args.sql:
        sql = args.sql
    else:
        print("Error: Provide SQL query or --file", file=sys.stderr)
        sys.exit(1)
    
    try:
        client = NeonSQL(pooled=args.pooled)
        results = client.execute(sql, fetch=not args.no_fetch)
        
        print(json.dumps(results, indent=2 if args.pretty else None, default=str))
    
    except psycopg2.Error as e:
        print(f"Database Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
