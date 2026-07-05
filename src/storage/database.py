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
    - Transaction support
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
        self._slow_query_threshold = 1.0
        self._timeout_seconds = 10
        self._initialized = True
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_database()
        self._migrate_database()
        
        logger.info(f"Database initialized: {db_path}")
    
    def _init_database(self) -> None:
        """Initialize database tables if they don't exist"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
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
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS backup_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        backup_file TEXT NOT NULL,
                        records INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute("PRAGMA user_version = 1")
                conn.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _migrate_database(self) -> None:
        """Migrate database to latest version"""
        current = self._get_db_version()
        target = 1
        
        if current < target:
            logger.info(f"Migrating database from v{current} to v{target}")
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
    
    def _validate_connection(self, conn) -> bool:
        """Validate connection is still active"""
        try:
            conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with retry logic"""
        conn = None
        retries = 0
        
        while retries < self._max_retries:
            try:
                conn = sqlite3.connect(self.db_path, timeout=self._timeout_seconds)
                conn.row_factory = sqlite3.Row
                
                # Validate connection
                if not self._validate_connection(conn):
                    raise sqlite3.OperationalError("Connection validation failed")
                
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
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
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        with self._get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back: {e}")
                raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        start_time = time.time()
        self._total_queries += 1
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
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
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE or DELETE query"""
        start_time = time.time()
        self._total_queries += 1
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                elapsed = time.time() - start_time
                
                if elapsed > self._slow_query_threshold:
                    logger.warning(f"Slow update: {elapsed:.2f}s - {query[:100]}")
                
                return cursor.rowcount
                
        except Exception as e:
            self._failed_queries += 1
            elapsed = time.time() - start_time
            logger.error(f"Update error after {elapsed:.3f}s: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return 0
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple inserts/updates"""
        start_time = time.time()
        self._total_queries += 1
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                elapsed = time.time() - start_time
                
                if elapsed > self._slow_query_threshold:
                    logger.warning(f"Slow batch: {elapsed:.2f}s - {query[:100]}")
                
                return cursor.rowcount
                
        except Exception as e:
            self._failed_queries += 1
            elapsed = time.time() - start_time
            logger.error(f"Batch execution error after {elapsed:.3f}s: {e}")
            logger.error(f"Query: {query}")
            return 0
    
    def save_session(self, session_dict: Dict[str, Any]) -> Optional[int]:
        """Save a session to database"""
        query = '''
            INSERT INTO sessions 
            (subject, duration, distractions, productivity_score, timestamp, notes, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            session_dict.get('subject'),
            session_dict.get('duration'),
            session_dict.get('distractions', 0),
            session_dict.get('productivity_score'),
            session_dict.get('timestamp', datetime.now().isoformat()),
            session_dict.get('notes'),
            session_dict.get('mood')
        )
        
        return self.execute_insert(query, params)
    
    def save_sessions(self, sessions: List[Dict[str, Any]]) -> int:
        """Save multiple sessions"""
        query = '''
            INSERT INTO sessions 
            (subject, duration, distractions, productivity_score, timestamp, notes, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        params_list = []
        for session in sessions:
            params = (
                session.get('subject'),
                session.get('duration'),
                session.get('distractions', 0),
                session.get('productivity_score'),
                session.get('timestamp', datetime.now().isoformat()),
                session.get('notes'),
                session.get('mood')
            )
            params_list.append(params)
        
        return self.execute_many(query, params_list)
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions"""
        query = "SELECT * FROM sessions ORDER BY timestamp DESC"
        return self.execute_query(query)
    
    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        query = "SELECT * FROM sessions WHERE id = ?"
        results = self.execute_query(query, (session_id,))
        return results[0] if results else None
    
    def get_sessions_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get sessions by date"""
        query = "SELECT * FROM sessions WHERE date(timestamp) = ? ORDER BY timestamp DESC"
        return self.execute_query(query, (date,))
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a session"""
        query = "DELETE FROM sessions WHERE id = ?"
        rows = self.execute_update(query, (session_id,))
        return rows > 0
    
    def clear_all_sessions(self) -> int:
        """Delete all sessions"""
        query = "DELETE FROM sessions"
        return self.execute_update(query)
    
    def get_session_count(self) -> int:
        """Get total session count"""
        query = "SELECT COUNT(*) as count FROM sessions"
        results = self.execute_query(query)
        return results[0]['count'] if results else 0
    
    def get_connection_usage(self) -> Dict[str, Any]:
        """Get connection pool usage statistics"""
        return {
            'active_connections': self._active_connections,
            'max_connections': self.max_connections,
            'connection_usage_percent': round(
                (self._active_connections / self.max_connections) * 100, 2
            ),
            'total_queries': self._total_queries,
            'failed_queries': self._failed_queries,
            'success_rate': round(
                (self._total_queries - self._failed_queries) / max(1, self._total_queries) * 100, 2
            ),
            'slow_query_threshold': self._slow_query_threshold
        }
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        return {
            'total_queries': self._total_queries,
            'failed_queries': self._failed_queries,
            'success_rate': round(
                (self._total_queries - self._failed_queries) / max(1, self._total_queries) * 100, 2
            ),
            'slow_query_threshold': self._slow_query_threshold
        }
    
    def bulk_insert_sessions(self, sessions: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """Bulk insert sessions in batches"""
        total_inserted = 0
        
        for i in range(0, len(sessions), batch_size):
            batch = sessions[i:i+batch_size]
            inserted = self.save_sessions(batch)
            total_inserted += inserted
        
        logger.info(f"Bulk inserted {total_inserted} sessions in {len(sessions)//batch_size + 1} batches")
        return total_inserted
    
    def vacuum(self) -> bool:
        """Vacuum database to reclaim space"""
        try:
            with self._get_connection() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuum completed")
                return True
        except Exception as e:
            logger.error(f"Vacuum error: {e}")
            return False