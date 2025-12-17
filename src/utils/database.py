"""
Database Connection Utilities
==============================
Database connection and query utilities.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from .config import Config
from .logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """PostgreSQL database connection manager."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            connection_string: PostgreSQL connection string. 
                             If None, uses Config.database_url
        """
        self.connection_string = connection_string or Config().database_url
        self._engine: Optional[Engine] = None
        logger.info("Database connection initialized")
    
    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine (lazy initialization)."""
        if self._engine is None:
            self._engine = create_engine(
                self.connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                echo=False
            )
            logger.info("Database engine created")
        return self._engine
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = self.engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> pd.DataFrame:
        """
        Execute a SELECT query and return results as DataFrame.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Query results as pandas DataFrame
        """
        try:
            with self.get_connection() as conn:
                if params:
                    result = pd.read_sql(text(query), conn, params=params)
                else:
                    result = pd.read_sql(query, conn)
                
                logger.info(f"Query executed successfully, returned {len(result)} rows")
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def execute_sql(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL statement
            params: Optional query parameters
        """
        try:
            with self.get_connection() as conn:
                if params:
                    conn.execute(text(query), params)
                else:
                    conn.execute(text(query))
                
                logger.info("SQL statement executed successfully")
        except Exception as e:
            logger.error(f"SQL execution failed: {str(e)}")
            raise
    
    def insert_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: str = "public",
        if_exists: str = "append"
    ) -> int:
        """
        Insert a pandas DataFrame into a database table.
        
        Args:
            df: DataFrame to insert
            table_name: Target table name
            schema: Database schema
            if_exists: What to do if table exists ('fail', 'replace', 'append')
            
        Returns:
            Number of rows inserted
        """
        try:
            rows_inserted = df.to_sql(
                name=table_name,
                con=self.engine,
                schema=schema,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            logger.info(
                f"Inserted {len(df)} rows into {schema}.{table_name}"
            )
            return len(df)
        except Exception as e:
            logger.error(f"DataFrame insertion failed: {str(e)}")
            raise
    
    def close(self):
        """Close database connection."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection closed")
