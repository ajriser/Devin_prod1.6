import os
import pandas as pd
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SQLServerTool:
    """Tool for connecting to and querying Microsoft SQL Server."""
    
    name = "sqlserver_connector"
    description = "Connect to Microsoft SQL Server and execute SQL queries to retrieve structured data"
    
    def __init__(self):
        self.connection = None
        self.config = {
            'host': os.getenv('SQLSERVER_HOST', ''),
            'port': os.getenv('SQLSERVER_PORT', '1433'),
            'database': os.getenv('SQLSERVER_DATABASE', ''),
            'user': os.getenv('SQLSERVER_USER', ''),
            'password': os.getenv('SQLSERVER_PASSWORD', '')
        }
    
    def connect(self, config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Establish connection to SQL Server."""
        try:
            import pymssql
            
            conn_config = config if config else self.config
            
            if not conn_config.get('host') or not conn_config.get('user'):
                return {
                    'success': False,
                    'error': 'Missing required SQL Server configuration (host, user)',
                    'message': 'Please provide SQL Server connection details'
                }
            
            self.connection = pymssql.connect(
                server=conn_config['host'],
                port=conn_config['port'],
                database=conn_config['database'],
                user=conn_config['user'],
                password=conn_config['password']
            )
            
            return {
                'success': True,
                'message': f"Connected to SQL Server: {conn_config['host']}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to SQL Server'
            }
    
    def disconnect(self) -> Dict[str, Any]:
        """Close SQL Server connection."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            return {'success': True, 'message': 'Disconnected from SQL Server'}
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
    
    def get_tables(self, database: Optional[str] = None) -> Dict[str, Any]:
        """Get list of tables in the database."""
        try:
            query = """
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
            
            return self.execute_query(query)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_table_schema(self, table_name: str, schema: str = 'dbo') -> Dict[str, Any]:
        """Get schema information for a specific table."""
        try:
            query = f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                AND TABLE_SCHEMA = '{schema}'
                ORDER BY ORDINAL_POSITION
            """
            
            return self.execute_query(query)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def preview_table(self, table_name: str, schema: str = 'dbo', limit: int = 100) -> Dict[str, Any]:
        """Preview data from a table."""
        query = f"SELECT TOP {limit} * FROM [{schema}].[{table_name}]"
        return self.execute_query(query)
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for the tool."""
        actions = {
            'connect': self.connect,
            'disconnect': self.disconnect,
            'query': lambda: self.execute_query(kwargs.get('query', '')),
            'tables': lambda: self.get_tables(kwargs.get('database')),
            'schema': lambda: self.get_table_schema(
                kwargs.get('table_name', ''),
                kwargs.get('schema', 'dbo')
            ),
            'preview': lambda: self.preview_table(
                kwargs.get('table_name', ''),
                kwargs.get('schema', 'dbo'),
                kwargs.get('limit', 100)
            )
        }
        
        if action not in actions:
            return {'success': False, 'error': f'Unknown action: {action}'}
        
        return actions[action]() if callable(actions[action]) else actions[action]
