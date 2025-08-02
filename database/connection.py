import sqlite3
import logging
from contextlib import contextmanager
from config.settings import Settings

class DatabaseManager:
    def __init__(self, db_path: str = Settings.DATABASE_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a single query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_queries(self, queries: list):
        """Execute multiple queries in a transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            results = []
            for query, params in queries:
                cursor.execute(query, params)
                results.append(cursor.fetchall())
            conn.commit()
            return results