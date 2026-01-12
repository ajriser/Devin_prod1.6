import os
import pandas as pd
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class SnowflakeTool:
    """Tool for connecting to and querying Snowflake data warehouse."""
    
    name = "snowflake_connector"
    description = "Connect to Snowflake and execute SQL queries to retrieve structured data"
    
    def __init__(self):
        self.connection = None
        self.config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT', ''),
            'user': os.getenv('SNOWFLAKE_USER', ''),
            'password': os.getenv('SNOWFLAKE_PASSWORD', ''),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', ''),
            'database': os.getenv('SNOWFLAKE_DATABASE', ''),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', '')
        }
    
    def connect(self, config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Establish connection to Snowflake."""
        try:
            import snowflake.connector
            
            conn_config = config if config else self.config
            
            if not conn_config.get('account') or not conn_config.get('user'):
                return {
                    'success': False,
                    'error': 'Missing required Snowflake configuration (account, user)',
                    'message': 'Please provide Snowflake connection details'
                }
            
            self.connection = snowflake.connector.connect(
                account=conn_config['account'],
                user=conn_config['user'],
                password=conn_config['password'],
                warehouse=conn_config['warehouse'],
                database=conn_config['database'],
                schema=conn_config['schema']
            )
            
            return {
                'success': True,
                'message': f"Connected to Snowflake account: {conn_config['account']}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to Snowflake'
            }
    
    def disconnect(self) -> Dict[str, Any]:
        """Close Snowflake connection."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            return {'success': True, 'message': 'Disconnected from Snowflake'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results as DataFrame."""
        try:
            if not self.connection:
                connect_result = self.connect()
                if not connect_result['success']:
                    return connect_result
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            df = pd.DataFrame(rows, columns=columns)
            cursor.close()
            
            return {
                'success': True,
                'data': df,
                'row_count': len(df),
                'columns': columns,
                'message': f"Query executed successfully. Retrieved {len(df)} rows."
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Query execution failed'
            }
    
    def get_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> Dict[str, Any]:
        """Get list of tables in the specified database/schema."""
        try:
            db = database or self.config['database']
            sch = schema or self.config['schema']
            
            query = f"""
                SELECT TABLE_NAME, TABLE_TYPE, ROW_COUNT, CREATED
                FROM {db}.INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{sch}'
                ORDER BY TABLE_NAME
            """
            
            return self.execute_query(query)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        try:
            query = f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """
            
            return self.execute_query(query)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def preview_table(self, table_name: str, limit: int = 100) -> Dict[str, Any]:
        """Preview data from a table."""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for the tool."""
        actions = {
            'connect': self.connect,
            'disconnect': self.disconnect,
            'query': lambda: self.execute_query(kwargs.get('query', '')),
            'tables': lambda: self.get_tables(kwargs.get('database'), kwargs.get('schema')),
            'schema': lambda: self.get_table_schema(kwargs.get('table_name', '')),
            'preview': lambda: self.preview_table(kwargs.get('table_name', ''), kwargs.get('limit', 100))
        }
        
        if action not in actions:
            return {'success': False, 'error': f'Unknown action: {action}'}
        
        return actions[action]() if callable(actions[action]) else actions[action]
