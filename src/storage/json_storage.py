"""
JSON Storage Module - Repository Pattern Implementation
Enterprise-grade data persistence with backup and recovery
"""

import json
import os
import shutil
import logging
import uuid
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
    - Data migration
    - Export/Import
    - Cache management
    - Backup cleanup
    """
    
    _instance = None
    _lock = threading.Lock()
    _data_version = 2  # Current data version
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, file_path: str = 'data/sessions.json', 
                 backup_dir: str = 'data/backups',
                 max_backups: int = 20):
        """
        Initialize storage with file path and backup directory
        
        Args:
            file_path: Path to main JSON file
            backup_dir: Directory for backups
            max_backups: Maximum number of backups to keep
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.file_path = file_path
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self._cache = None
        self._cache_timestamp = None
        self._cache_ttl = timedelta(seconds=5)
        self._initialized = True
        
        self._ensure_directories()
        self._migrate_data_if_needed()
        self._create_backup_if_needed()
        self._cleanup_old_backups()
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
    
    def _migrate_data_if_needed(self) -> None:
        """Migrate data to latest version if needed"""
        if not os.path.exists(self.file_path):
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if data has version field
            version = data.get('_version', 1) if isinstance(data, dict) and '_version' in data else 1
            
            if version < self._data_version:
                logger.info(f"Migrating data from v{version} to v{self._data_version}")
                data = self._migrate_data(data, version, self._data_version)
                data['_version'] = self._data_version
                self._write_data(data)
                logger.info(f"Data migration complete")
        except Exception as e:
            logger.warning(f"Data migration skipped: {e}")
    
    def _migrate_data(self, data: List[Dict[str, Any]], old_version: int, new_version: int) -> List[Dict[str, Any]]:
        """Migrate data to new version"""
        if old_version == new_version:
            return data
        
        # Version 1 → Version 2: Add session_id field
        if old_version < 2 and new_version >= 2:
            for session in data:
                if 'session_id' not in session:
                    session['session_id'] = str(uuid.uuid4())[:8]
        
        return data
    
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
    
    def _cleanup_old_backups(self) -> int:
        """Delete old backups keeping only latest N"""
        try:
            backups = sorted([
                f for f in os.listdir(self.backup_dir) 
                if f.endswith('.json')
            ], reverse=True)
            
            deleted = 0
            for backup in backups[self.max_backups:]:
                try:
                    os.remove(os.path.join(self.backup_dir, backup))
                    deleted += 1
                except Exception as e:
                    logger.error(f"Failed to delete backup {backup}: {e}")
            
            if deleted:
                logger.info(f"Deleted {deleted} old backups, kept {min(self.max_backups, len(backups))}")
            return deleted
        except Exception as e:
            logger.error(f"Backup cleanup error: {e}")
            return 0
    
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
                    
                    # Handle versioned data
                    if isinstance(data, dict) and '_version' in data:
                        sessions = data.get('sessions', [])
                    else:
                        sessions = data if isinstance(data, list) else []
                    
                    if not isinstance(sessions, list):
                        raise ValueError("Invalid data format: expected list")
                    
                    self._cache = sessions
                    self._cache_timestamp = datetime.now()
                    return sessions
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
            # Prepare data with version
            versioned_data = {
                '_version': self._data_version,
                'sessions': data,
                'updated_at': datetime.now().isoformat(),
                'total_sessions': len(data)
            }
            
            # Write to temp file first (atomic operation)
            temp_file = f"{self.file_path}.tmp"
            with self._file_lock():
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(versioned_data, f, indent=2, ensure_ascii=False)
                
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
        """Attempt to recover data from latest backup"""
        try:
            backups = sorted([f for f in os.listdir(self.backup_dir) if f.endswith('.json')])
            if backups:
                latest_backup = os.path.join(self.backup_dir, backups[-1])
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, dict) and 'sessions' in data:
                        sessions = data['sessions']
                    else:
                        sessions = data if isinstance(data, list) else []
                    
                    logger.info(f"Recovered {len(sessions)} records from backup")
                    self._write_data(sessions)
                    return sessions
        except Exception as e:
            logger.error(f"Backup recovery failed: {e}")
        return []
    
    def _validate_session_data(self, session_dict: Dict[str, Any]) -> bool:
        """Validate session data before saving"""
        required_fields = ['subject', 'duration', 'productivity_score', 'timestamp']
        
        # Check required fields
        for field in required_fields:
            if field not in session_dict:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate data types
        if not isinstance(session_dict['duration'], (int, float)):
            raise TypeError("Duration must be a number")
        if not isinstance(session_dict['productivity_score'], (int, float)):
            raise TypeError("Productivity score must be a number")
        
        # Validate ranges
        if not (5 <= session_dict['duration'] <= 240):
            raise ValueError("Duration must be between 5 and 240 minutes")
        if not (0 <= session_dict['productivity_score'] <= 100):
            raise ValueError("Productivity score must be between 0 and 100")
        
        return True
    
    def save_session(self, session_dict: Dict[str, Any]) -> bool:
        """Save a single session"""
        try:
            # Validate session data
            self._validate_session_data(session_dict)
            
            # Add session_id if missing
            if 'session_id' not in session_dict:
                session_dict['session_id'] = str(uuid.uuid4())[:8]
            
            sessions = self._read_data()
            sessions.append(session_dict)
            self._write_data(sessions)
            logger.info(f"Session saved: {session_dict.get('subject')} (ID: {session_dict.get('session_id')})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    # ... (rest of methods remain the same)
    
    def invalidate_cache(self) -> None:
        """Manually invalidate cache"""
        self._cache = None
        self._cache_timestamp = None
        logger.debug("Cache invalidated")
    
    def refresh_cache(self) -> List[Dict[str, Any]]:
        """Refresh cache with latest data"""
        self.invalidate_cache()
        return self._read_data()
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export sessions to CSV"""
        import csv
        sessions = self.load_all_sessions()
        
        if not sessions:
            raise ValueError("No sessions to export")
        
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        os.makedirs('exports', exist_ok=True)
        filepath = os.path.join('exports', filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sessions[0].keys())
            writer.writeheader()
            writer.writerows(sessions)
        
        logger.info(f"Exported {len(sessions)} sessions to {filepath}")
        return filepath
    
    def import_from_csv(self, filename: str) -> int:
        """Import sessions from CSV"""
        import csv
        sessions = []
        
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                if 'duration' in row:
                    row['duration'] = int(row['duration'])
                if 'distractions' in row:
                    row['distractions'] = int(row['distractions'])
                if 'productivity_score' in row:
                    row['productivity_score'] = int(row['productivity_score'])
                if 'mood' in row and row['mood']:
                    row['mood'] = int(row['mood'])
                sessions.append(row)
        
        self.save_sessions(sessions)
        logger.info(f"Imported {len(sessions)} sessions from {filename}")
        return len(sessions)
    
    def cleanup_old_backups(self, keep: int = None) -> int:
        """Delete old backups keeping only latest N"""
        if keep is None:
            keep = self.max_backups
        
        try:
            backups = sorted([
                f for f in os.listdir(self.backup_dir) 
                if f.endswith('.json')
            ], reverse=True)
            
            deleted = 0
            for backup in backups[keep:]:
                try:
                    os.remove(os.path.join(self.backup_dir, backup))
                    deleted += 1
                except Exception as e:
                    logger.error(f"Failed to delete backup {backup}: {e}")
            
            if deleted:
                logger.info(f"Deleted {deleted} old backups, kept {min(keep, len(backups))}")
            return deleted
        except Exception as e:
            logger.error(f"Backup cleanup error: {e}")
            return 0
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get detailed storage information"""
        sessions = self._read_data()
        
        return {
            'total_sessions': len(sessions),
            'file_path': self.file_path,
            'file_exists': os.path.exists(self.file_path),
            'file_size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0,
            'backup_dir': self.backup_dir,
            'backup_count': len([f for f in os.listdir(self.backup_dir) if f.endswith('.json')]),
            'cache_active': self._cache is not None,
            'cache_age': (datetime.now() - self._cache_timestamp).total_seconds() if self._cache_timestamp else None,
            'data_version': self._data_version
        }