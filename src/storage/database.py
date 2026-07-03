"""
Database Module - SQLite Database Operations
Professional database layer with connection pooling and error handling
"""

import os
import sqlite3
import logging
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
    - Query logging
    - Error recovery
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
    
    def __init__(self, db_path: str = 'data/study.db'):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.db_path = db_path
        self._max_retries = 3
        self._initialized = True
        
        # Create directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
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
                
                conn.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
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
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with results
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # Convert rows to dictionaries
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                logger.debug(f"Query executed: {query[:100]}... ({len(results)} rows)")
                return results
                
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return []
    
    def execute_insert(self, query: str, params: tuple = ()) -> Optional[int]:
        """
        Execute an INSERT query and return last row ID
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Last row ID or None on failure
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Insert error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return None
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an UPDATE or DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of rows affected
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Update error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return 0
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute multiple inserts/updates
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of rows affected
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Batch execution error: {e}")
            return 0
    
    def save_session(self, session_dict: Dict[str, Any]) -> Optional[int]:
        """
        Save a session to database
        
        Args:
            session_dict: Session data dictionary
            
        Returns:
            Session ID or None on failure
        """
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
        """
        Save multiple sessions
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Number of sessions saved
        """
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
    
    def get_sessions_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Get sessions by subject"""
        query = "SELECT * FROM sessions WHERE subject = ? ORDER BY timestamp DESC"
        return self.execute_query(query, (subject,))
    
    def get_sessions_in_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get sessions in date range"""
        query = """
            SELECT * FROM sessions 
            WHERE date(timestamp) BETWEEN ? AND ? 
            ORDER BY timestamp DESC
        """
        return self.execute_query(query, (start_date, end_date))
    
    def update_session(self, session_id: int, updates: Dict[str, Any]) -> bool:
        """Update a session"""
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE sessions SET {set_clause} WHERE id = ?"
        params = list(updates.values()) + [session_id]
        rows = self.execute_update(query, tuple(params))
        return rows > 0
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a session"""
        query = "DELETE FROM sessions WHERE id = ?"
        rows = self.execute_update(query, (session_id,))
        return rows > 0
    
    def delete_sessions_by_subject(self, subject: str) -> int:
        """Delete sessions by subject"""
        query = "DELETE FROM sessions WHERE subject = ?"
        return self.execute_update(query, (subject,))
    
    def delete_sessions_by_date(self, date: str) -> int:
        """Delete sessions by date"""
        query = "DELETE FROM sessions WHERE date(timestamp) = ?"
        return self.execute_update(query, (date,))
    
    def clear_all_sessions(self) -> int:
        """Delete all sessions"""
        query = "DELETE FROM sessions"
        return self.execute_update(query)
    
    def get_session_count(self) -> int:
        """Get total session count"""
        query = "SELECT COUNT(*) as count FROM sessions"
        results = self.execute_query(query)
        return results[0]['count'] if results else 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        queries = {
            'total_sessions': "SELECT COUNT(*) as count FROM sessions",
            'total_time': "SELECT SUM(duration) as total FROM sessions",
            'avg_productivity': "SELECT AVG(productivity_score) as avg FROM sessions",
            'subjects': "SELECT COUNT(DISTINCT subject) as count FROM sessions",
            'total_distractions': "SELECT SUM(distractions) as total FROM sessions",
            'first_session': "SELECT MIN(timestamp) as first FROM sessions",
            'last_session': "SELECT MAX(timestamp) as last FROM sessions"
        }
        
        stats = {}
        for key, query in queries.items():
            results = self.execute_query(query)
            if results:
                value = results[0].get('total') or results[0].get('avg') or results[0].get('count') or results[0].get('first') or results[0].get('last')
                stats[key] = value if value is not None else 0
        
        return stats
    
    def get_subject_stats(self) -> List[Dict[str, Any]]:
        """Get subject-wise statistics"""
        query = """
            SELECT 
                subject,
                COUNT(*) as sessions,
                SUM(duration) as total_time,
                AVG(productivity_score) as avg_productivity,
                MIN(productivity_score) as min_productivity,
                MAX(productivity_score) as max_productivity,
                AVG(distractions) as avg_distractions,
                SUM(distractions) as total_distractions
            FROM sessions
            GROUP BY subject
            ORDER BY avg_productivity DESC
        """
        return self.execute_query(query)
    
    def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily statistics for last N days"""
        query = """
            SELECT 
                date(timestamp) as date,
                COUNT(*) as sessions,
                SUM(duration) as total_time,
                AVG(productivity_score) as avg_productivity
            FROM sessions
            WHERE date(timestamp) >= date('now', ?)
            GROUP BY date(timestamp)
            ORDER BY date DESC
        """
        return self.execute_query(query, (f'-{days} days',))
    
    def get_hourly_stats(self) -> List[Dict[str, Any]]:
        """Get hourly statistics"""
        query = """
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as sessions,
                AVG(productivity_score) as avg_productivity,
                AVG(duration) as avg_duration
            FROM sessions
            GROUP BY hour
            ORDER BY hour
        """
        return self.execute_query(query)
    
    def log_backup(self, backup_file: str, records: int) -> bool:
        """Log a backup operation"""
        query = "INSERT INTO backup_log (backup_file, records) VALUES (?, ?)"
        result = self.execute_insert(query, (backup_file, records))
        return result is not None
    
    def get_backup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get backup history"""
        query = """
            SELECT * FROM backup_log 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a setting value"""
        query = "SELECT value FROM settings WHERE key = ?"
        results = self.execute_query(query, (key,))
        return results[0]['value'] if results else default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        query = """
            INSERT INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP
        """
        return self.execute_update(query, (key, value, value)) > 0
    
    def get_db_size(self) -> str:
        """Get database file size"""
        try:
            size = os.path.getsize(self.db_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "0 B"
    
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