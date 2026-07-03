"""
JSON Storage Module - Repository Pattern Implementation
Enterprise-grade data persistence with backup and recovery
"""

import json
import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


class JSONStorage:
    """
    Thread-safe JSON storage with backup and recovery
    
    Implements Repository pattern for data persistence
    Features:
    - Automatic backups
    - Data validation
    - Thread-safe operations
    - Error recovery
    - Query methods
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, file_path: str = 'data/sessions.json', backup_dir: str = 'data/backups'):
        """
        Initialize storage with file path and backup directory
        
        Args:
            file_path: Path to main JSON file
            backup_dir: Directory for backups
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.file_path = file_path
        self.backup_dir = backup_dir
        self._cache = None
        self._cache_timestamp = None
        self._cache_ttl = timedelta(seconds=5)
        self._initialized = True
        
        self._ensure_directories()
        self._create_backup_if_needed()
        logger.info(f"Storage initialized: {file_path}")
    
    def _ensure_directories(self) -> None:
        """Ensure data and backup directories exist"""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)
            
            if not os.path.exists(self.file_path):
                self._write_data([])
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise RuntimeError(f"Failed to initialize storage: {e}")
    
    def _create_backup_if_needed(self) -> None:
        """Create backup if file exists"""
        if os.path.exists(self.file_path):
            backup_file = os.path.join(
                self.backup_dir,
                f"sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                shutil.copy2(self.file_path, backup_file)
                logger.info(f"Backup created: {backup_file}")
            except Exception as e:
                logger.warning(f"Backup creation failed: {e}")
    
    @contextmanager
    def _file_lock(self):
        """Context manager for file operations"""
        lock_file = f"{self.file_path}.lock"
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            yield
        finally:
            if os.path.exists(lock_file):
                os.remove(lock_file)
    
    def _read_data(self) -> List[Dict[str, Any]]:
        """
        Read data from file with caching
        
        Returns:
            List of session dictionaries
        """
        # Check cache
        if self._cache and self._cache_timestamp:
            if datetime.now() - self._cache_timestamp < self._cache_ttl:
                return self._cache
        
        try:
            with self._file_lock():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        raise ValueError("Invalid data format: expected list")
                    self._cache = data
                    self._cache_timestamp = datetime.now()
                    return data
        except FileNotFoundError:
            logger.warning(f"File not found: {self.file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._recover_from_backup()
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            return []
    
    def _write_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Write data to file with atomic operation
        
        Args:
            data: List of session dictionaries
        """
        try:
            # Write to temp file first (atomic operation)
            temp_file = f"{self.file_path}.tmp"
            with self._file_lock():
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Replace original with temp
                shutil.move(temp_file, self.file_path)
                
            # Update cache
            self._cache = data
            self._cache_timestamp = datetime.now()
            logger.debug(f"Data written successfully: {len(data)} records")
            
        except Exception as e:
            logger.error(f"Error writing data: {e}")
            raise RuntimeError(f"Failed to save data: {e}")
    
    def _recover_from_backup(self) -> List[Dict[str, Any]]:
        """
        Attempt to recover data from latest backup
        
        Returns:
            Recovered data or empty list
        """
        try:
            backups = sorted([f for f in os.listdir(self.backup_dir) if f.endswith('.json')])
            if backups:
                latest_backup = os.path.join(self.backup_dir, backups[-1])
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Recovered {len(data)} records from backup")
                    self._write_data(data)
                    return data
        except Exception as e:
            logger.error(f"Backup recovery failed: {e}")
        return []
    
    def save_session(self, session_dict: Dict[str, Any]) -> bool:
        """
        Save a single session
        
        Args:
            session_dict: Session data dictionary
            
        Returns:
            bool: True if successful
        """
        try:
            # Validate session data
            required_fields = ['subject', 'duration', 'productivity_score', 'timestamp']
            for field in required_fields:
                if field not in session_dict:
                    raise ValueError(f"Missing required field: {field}")
            
            sessions = self._read_data()
            sessions.append(session_dict)
            self._write_data(sessions)
            logger.info(f"Session saved: {session_dict.get('subject')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def save_sessions(self, sessions: List[Dict[str, Any]]) -> bool:
        """
        Save multiple sessions at once
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            bool: True if successful
        """
        try:
            current = self._read_data()
            current.extend(sessions)
            self._write_data(current)
            logger.info(f"Saved {len(sessions)} sessions")
            return True
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
            return False
    
    def load_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Load all sessions
        
        Returns:
            List of session dictionaries
        """
        return self._read_data()
    
    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get session by index/id
        
        Args:
            session_id: Index of session
            
        Returns:
            Session dictionary or None
        """
        sessions = self._read_data()
        if 0 <= session_id < len(sessions):
            return sessions[session_id]
        return None
    
    def get_sessions_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Get sessions for a specific date
        
        Args:
            date: Date string in 'YYYY-MM-DD' format
            
        Returns:
            List of sessions on that date
        """
        sessions = self._read_data()
        return [
            s for s in sessions
            if s.get('timestamp', '').startswith(date)
        ]
    
    def get_sessions_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """
        Get sessions for a specific subject
        
        Args:
            subject: Subject name
            
        Returns:
            List of sessions for that subject
        """
        sessions = self._read_data()
        return [
            s for s in sessions
            if s.get('subject', '').lower() == subject.lower()
        ]
    
    def get_sessions_in_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get sessions in a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of sessions in range
        """
        sessions = self._read_data()
        return [
            s for s in sessions
            if start_date <= s.get('timestamp', '')[:10] <= end_date
        ]
    
    def delete_session(self, session_id: int) -> bool:
        """
        Delete a session by index
        
        Args:
            session_id: Index of session to delete
            
        Returns:
            bool: True if successful
        """
        try:
            sessions = self._read_data()
            if 0 <= session_id < len(sessions):
                deleted = sessions.pop(session_id)
                self._write_data(sessions)
                logger.info(f"Session deleted: {deleted.get('subject')}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def clear_all_sessions(self) -> bool:
        """
        Clear all sessions
        
        Returns:
            bool: True if successful
        """
        try:
            self._write_data([])
            logger.info("All sessions cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing sessions: {e}")
            return False
    
    def get_session_count(self) -> int:
        """Get total number of sessions"""
        return len(self._read_data())
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        sessions = self._read_data()
        return {
            'total_sessions': len(sessions),
            'file_size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0,
            'subjects': len(set(s.get('subject', '') for s in sessions)),
            'backup_count': len([f for f in os.listdir(self.backup_dir) if f.endswith('.json')])
        }
    
    def create_backup(self) -> str:
        """
        Create manual backup
        
        Returns:
            Path to backup file
        """
        backup_file = os.path.join(
            self.backup_dir,
            f"sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        shutil.copy2(self.file_path, backup_file)
        logger.info(f"Manual backup created: {backup_file}")
        return backup_file
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """
        Restore data from a backup file
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            bool: True if successful
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._write_data(data)
                logger.info(f"Restored from backup: {backup_file}")
                return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False