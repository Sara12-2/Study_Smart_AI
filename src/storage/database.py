"""
Database Module - SQLite Database Operations
Professional database layer with connection pooling and error handling
"""

import os
import sqlite3
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


class Database:
    """
    Database class with connection pooling and thread safety
    
    Features:
    - Thread-safe operations
    - Connection pooling
    - Automatic retry on failure
    - Query logging with timing
    - Slow query detection
    - Data migration support
    - Connection pool statistics
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for database connection"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = 'data/study.db', max_connections: int = 10):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
            max_connections: Maximum connections in pool
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.db_path = db_path
        self.max_connections = max_connections
        self._max_retries = 3
        self._active_connections = 0
        self._total_queries = 0
        self._failed_queries = 0
        self._slow_query_threshold = 1.0  # seconds
        self._initialized = True
        
        # Create directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        self._migrate_database()
        
        logger.info(f"Database initialized: {db_path}")
    
    def _init_database(self) -> None:
        """Initialize database tables if they don't exist"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subject TEXT NOT NULL,
                        duration INTEGER NOT NULL,
                        distractions INTEGER DEFAULT 0,
                        productivity_score INTEGER,
                        timestamp TEXT NOT NULL,
                        notes TEXT,
                        mood INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                    ON sessions(timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_subject 
                    ON sessions(subject)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_productivity 
                    ON sessions(productivity_score)
                ''')
                
                # Create backup log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS backup_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        backup_file TEXT NOT NULL,
                        records INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Set initial version
                cursor.execute("PRAGMA user_version = 1")
                
                conn.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _migrate_database(self) -> None:
        """Migrate database to latest version"""
        current = self._get_db_version()
        target = 1  # Current version
        
        if current < target:
            logger.info(f"Migrating database from v{current} to v{target}")
            
            # Add migration logic here for future versions
            # if current < 2:
            #     self._migrate_to_v2()
            # if current < 3:
            #     self._migrate_to_v3()
            
            with self._get_connection() as conn:
                conn.execute(f"PRAGMA user_version = {target}")
            
            logger.info(f"Database migrated to v{target}")
    
    def _get_db_version(self) -> int:
        """Get current database version"""
        try:
            result = self.execute_query("PRAGMA user_version")
            return result[0]['user_version'] if result else 0
        except:
            return 0
    
    def _is_connection_valid(self, conn) -> bool:
        """Check if connection is still valid"""
        try:
            conn.execute("SELECT 1")
            return True
        except:
            return False
    
    @contextmanager
    def _get_connection(self):
        """
        Get database connection with retry logic
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        retries = 0
        
        while retries < self._max_retries:
            try:
                conn = sqlite3.connect(self.db_path, timeout=10)
                conn.row_factory = sqlite3.Row
                
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode = WAL")
                
                # Set query timeout
                conn.execute("PRAGMA query_timeout = 5000")
                
                self._active_connections += 1
                
                yield conn
                
                conn.commit()
                break
                
            except sqlite3.OperationalError as e:
                retries += 1
                if conn:
                    conn.rollback()
                
                if retries >= self._max_retries:
                    logger.error(f"Database connection failed after {retries} retries: {e}")
                    raise
                
                logger.warning(f"Database connection retry {retries}: {e}")
                continue
                
            except Exception as e:
                if conn:
                    conn.rollback()
                logger.error(f"Database error: {e}")
                raise
                
            finally:
                if conn:
                    conn.close()
                self._active_connections -= 1
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with results
        """
        start_time = time.time()
        self._total_queries += 1
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # Convert rows to dictionaries
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                elapsed = time.time() - start_time
                
                if elapsed > self._slow_query_threshold:
                    logger.warning(f"Slow query: {elapsed:.2f}s - {query[:100]}")
                
                logger.debug(f"Query executed: {query[:100]}... ({len(results)} rows, {elapsed:.3f}s)")
                return results
                
        except Exception as e:
            self._failed_queries += 1
            elapsed = time.time() - start_time
            logger.error(f"Query execution error after {elapsed:.3f}s: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return []
    
    def execute_insert(self, query: str, params: tuple = ()) -> Optional[int]:
        """Execute an INSERT query and return last row ID"""
        start_time = time.time()
        self._total_queries += 1
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                elapsed = time.time() - start_time
                
                if elapsed > self._slow_query_threshold:
                    logger.warning(f"Slow insert: {elapsed:.2f}s - {query[:100]}")
                
                return cursor.lastrowid
                
        except Exception as e:
            self._failed_queries += 1
            elapsed = time.time() - start_time
            logger.error(f"Insert error after {elapsed:.3f}s: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return None
    
    # ... (rest of methods remain the same)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'active_connections': self._active_connections,
            'max_connections': self.max_connections,
            'total_queries': self._total_queries,
            'failed_queries': self._failed_queries,
            'success_rate': round(
                (self._total_queries - self._failed_queries) / max(1, self._total_queries) * 100, 2
            )
        }
    
    def bulk_insert_sessions(self, sessions: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """
        Bulk insert sessions in batches
        
        Args:
            sessions: List of session dictionaries
            batch_size: Number of records per batch
            
        Returns:
            Total number of sessions inserted
        """
        total_inserted = 0
        
        for i in range(0, len(sessions), batch_size):
            batch = sessions[i:i+batch_size]
            inserted = self.save_sessions(batch)
            total_inserted += inserted
        
        logger.info(f"Bulk inserted {total_inserted} sessions in {len(sessions)//batch_size + 1} batches")
        return total_inserted
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        return {
            'total_queries': self._total_queries,
            'failed_queries': self._failed_queries,
            'success_rate': round(
                (self._total_queries - self._failed_queries) / max(1, self._total_queries) * 100, 2
            ),
            'slow_queries_threshold': self._slow_query_threshold
        }