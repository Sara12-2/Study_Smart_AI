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
    - Configurable TTL
    """
    
    _instance = None
    _lock = threading.Lock()
    _data_version = 2
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, file_path: str = 'data/sessions.json', 
                 backup_dir: str = 'data/backups',
                 max_backups: int = 20,
                 cache_ttl_seconds: int = 5):
        """
        Initialize storage with file path and backup directory
        
        Args:
            file_path: Path to main JSON file
            backup_dir: Directory for backups
            max_backups: Maximum number of backups to keep
            cache_ttl_seconds: Cache TTL in seconds
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.file_path = file_path
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self._cache = None
        self._cache_timestamp = None
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._initialized = True
        
        self._ensure_directories()
        self._migrate_data_if_needed()
        self._create_backup_if_needed()
        self._cleanup_old_backups()
        
        # Auto-migrate productivity scores on startup
        migrated = self.migrate_add_productivity_score()
        if migrated > 0:
            logger.info(f"✅ Auto-migrated {migrated} sessions with productivity_score")
        
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
            
            if isinstance(data, dict) and '_version' in data:
                version = data.get('_version', 1)
                sessions = data.get('sessions', [])
            else:
                version = 1
                sessions = data if isinstance(data, list) else []
            
            if version < self._data_version:
                logger.info(f"Migrating data from v{version} to v{self._data_version}")
                sessions = self._migrate_data(sessions, version, self._data_version)
                self._write_data(sessions)
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
        """Read data from file with caching"""
        if self._cache and self._cache_timestamp:
            if datetime.now() - self._cache_timestamp < self._cache_ttl:
                return self._cache
        
        try:
            with self._file_lock():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
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
        """Write data to file with atomic operation"""
        try:
            versioned_data = {
                '_version': self._data_version,
                'sessions': data,
                'updated_at': datetime.now().isoformat(),
                'total_sessions': len(data)
            }
            
            temp_file = f"{self.file_path}.tmp"
            with self._file_lock():
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(versioned_data, f, indent=2, ensure_ascii=False, default=str)
                
                shutil.move(temp_file, self.file_path)
                
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
        required_fields = ['subject', 'duration', 'timestamp']
        
        for field in required_fields:
            if field not in session_dict:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(session_dict['duration'], (int, float)):
            raise TypeError("Duration must be a number")
        
        if 'productivity_score' in session_dict and session_dict['productivity_score'] is not None:
            if not isinstance(session_dict['productivity_score'], (int, float)):
                raise TypeError("Productivity score must be a number")
            if not (0 <= session_dict['productivity_score'] <= 100):
                raise ValueError("Productivity score must be between 0 and 100")
        
        if not (5 <= session_dict['duration'] <= 240):
            raise ValueError("Duration must be between 5 and 240 minutes")
        
        # Validate session_id if present
        if 'session_id' in session_dict:
            if not isinstance(session_dict['session_id'], str) or len(session_dict['session_id']) != 8:
                raise ValueError("session_id must be an 8-character string")
        
        return True
    
    # ==========================================
    # MIGRATION METHODS
    # ==========================================
    
    def migrate_add_productivity_score(self) -> int:
        """
        Add productivity_score to existing sessions that don't have it
        
        Returns:
            Number of sessions migrated
        """
        from src.core.session import StudySession
        
        sessions = self.load_all_sessions()
        migrated = 0
        
        for session in sessions:
            if 'productivity_score' not in session or session.get('productivity_score') is None:
                try:
                    # Create temp session to calculate score
                    temp = StudySession(
                        subject=session.get('subject', 'Unknown'),
                        duration=session.get('duration', 30),
                        distractions=session.get('distractions', 0),
                        notes=session.get('notes'),
                        mood=session.get('mood')
                    )
                    session['productivity_score'] = temp.productivity_score
                    migrated += 1
                except Exception as e:
                    logger.error(f"Failed to migrate session {session.get('id', 'unknown')}: {e}")
                    session['productivity_score'] = 50  # Default fallback
        
        if migrated > 0:
            self._write_data(sessions)
            logger.info(f"✅ Migrated {migrated} sessions with productivity_score")
        
        return migrated
    
    def add_session_id_to_old_sessions(self) -> int:
        """Add session_id to old sessions that don't have it"""
        sessions = self.load_all_sessions()
        migrated = 0
        
        for session in sessions:
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())[:8]
                migrated += 1
        
        if migrated > 0:
            self._write_data(sessions)
            logger.info(f"✅ Added session_id to {migrated} sessions")
        
        return migrated
    
    # ==========================================
    # USER SETTINGS METHODS (NEW)
    # ==========================================
    
    def load_user_settings(self) -> Dict[str, Any]:
        """
        Load user settings from file
        
        Returns:
            Dictionary with user settings
        """
        try:
            settings_file = os.path.join(os.path.dirname(self.file_path), 'user_settings.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading user settings: {e}")
        return {}
    
    def save_user_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save user settings to file
        
        Args:
            settings: Dictionary with user settings
            
        Returns:
            True if saved successfully
        """
        try:
            settings_file = os.path.join(os.path.dirname(self.file_path), 'user_settings.json')
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info(f"User settings saved: {settings_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving user settings: {e}")
            return False
    
    # ==========================================
    # PUBLIC METHODS
    # ==========================================
    
    def save_session(self, session_dict: Dict[str, Any]) -> bool:
        """Save a single session"""
        try:
            self._validate_session_data(session_dict)
            
            if 'session_id' not in session_dict:
                session_dict['session_id'] = str(uuid.uuid4())[:8]
            
            if 'status' in session_dict and hasattr(session_dict['status'], 'value'):
                session_dict['status'] = session_dict['status'].value
            
            sessions = self._read_data()
            sessions.append(session_dict)
            self._write_data(sessions)
            logger.info(f"Session saved: {session_dict.get('subject')} (ID: {session_dict.get('session_id')})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def save_sessions(self, sessions: List[Dict[str, Any]]) -> bool:
        """Save multiple sessions at once"""
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
        """Load all sessions"""
        return self._read_data()
    
    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get session by index/id"""
        sessions = self._read_data()
        if 0 <= session_id < len(sessions):
            return sessions[session_id]
        return None
    
    def get_sessions_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get sessions for a specific date"""
        sessions = self._read_data()
        return [
            s for s in sessions
            if s.get('timestamp', '').startswith(date)
        ]
    
    def get_sessions_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Get sessions for a specific subject"""
        sessions = self._read_data()
        return [
            s for s in sessions
            if s.get('subject', '').lower() == subject.lower()
        ]
    
    def get_sessions_in_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get sessions in a date range"""
        sessions = self._read_data()
        return [
            s for s in sessions
            if start_date <= s.get('timestamp', '')[:10] <= end_date
        ]
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a session by index"""
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
        """Clear all sessions"""
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
        """Get storage statistics"""
        sessions = self._read_data()
        return {
            'total_sessions': len(sessions),
            'file_size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0,
            'subjects': len(set(s.get('subject', '') for s in sessions)),
            'backup_count': len([f for f in os.listdir(self.backup_dir) if f.endswith('.json')])
        }
    
    def create_backup(self) -> str:
        """Create manual backup"""
        backup_file = os.path.join(
            self.backup_dir,
            f"sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        shutil.copy2(self.file_path, backup_file)
        logger.info(f"Manual backup created: {backup_file}")
        return backup_file
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """Restore data from a backup file"""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, dict) and 'sessions' in data:
                    sessions = data['sessions']
                else:
                    sessions = data if isinstance(data, list) else []
                
                self._write_data(sessions)
                logger.info(f"Restored from backup: {backup_file}")
                return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
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
                if 'duration' in row:
                    row['duration'] = int(row['duration'])
                if 'distractions' in row:
                    row['distractions'] = int(row['distractions'])
                if 'productivity_score' in row and row['productivity_score']:
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