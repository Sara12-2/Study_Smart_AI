"""
Helper Utilities
Common helper functions for the application
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import hashlib


class Helpers:
    """Collection of helper functions"""
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def hash_string(text: str) -> str:
        """Hash a string using SHA256"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    @staticmethod
    def get_current_time() -> str:
        """Get current time in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date string"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%B %d, %Y')
        except:
            return date_str
    
    @staticmethod
    def format_time(date_str: str) -> str:
        """Format time string"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%I:%M %p')
        except:
            return date_str
    
    @staticmethod
    def format_datetime(date_str: str) -> str:
        """Format date and time"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return date_str
    
    @staticmethod
    def days_between(date1: str, date2: str) -> int:
        """Calculate days between two dates"""
        try:
            d1 = datetime.fromisoformat(date1).date()
            d2 = datetime.fromisoformat(date2).date()
            return abs((d2 - d1).days)
        except:
            return 0
    
    @staticmethod
    def get_week_number(date_str: str) -> int:
        """Get week number from date"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.isocalendar().week
        except:
            return 0
    
    @staticmethod
    def get_day_name(date_str: str) -> str:
        """Get day name from date"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%A')
        except:
            return ''
    
    @staticmethod
    def is_today(date_str: str) -> bool:
        """Check if date is today"""
        try:
            dt = datetime.fromisoformat(date_str).date()
            return dt == datetime.now().date()
        except:
            return False
    
    @staticmethod
    def safe_json_loads(json_str: str) -> Optional[Dict]:
        """Safely load JSON string"""
        try:
            return json.loads(json_str)
        except:
            return None
    
    @staticmethod
    def safe_json_dumps(data: Any) -> str:
        """Safely dump to JSON string"""
        try:
            return json.dumps(data, indent=2, default=str)
        except:
            return '{}'
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 50) -> str:
        """Truncate string to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'
    
    @staticmethod
    def list_to_string(items: List[str], separator: str = ', ') -> str:
        """Convert list to string"""
        return separator.join(items) if items else ''
    
    @staticmethod
    def dict_to_string(d: Dict, separator: str = ', ') -> str:
        """Convert dictionary to string"""
        return separator.join(f"{k}: {v}" for k, v in d.items())
    
    @staticmethod
    def calculate_percentage(value: float, total: float) -> float:
        """Calculate percentage"""
        if total == 0:
            return 0
        return round((value / total) * 100, 2)
    
    @staticmethod
    def round_to_nearest(value: float, multiple: float = 5) -> float:
        """Round to nearest multiple"""
        return round(value / multiple) * multiple
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """Format duration in minutes to human readable"""
        if minutes < 60:
            return f"{minutes} min"
        hours = minutes // 60
        remaining = minutes % 60
        if remaining == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        return f"{hours}h {remaining}min"
    
    @staticmethod
    def get_file_size(file_path: str) -> str:
        """Get human readable file size"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return '0 B'