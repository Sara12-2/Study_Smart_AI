"""
Helper Utilities
Common helper functions for the application with enhanced features
"""

import os
import json
import re
import time
import threading
from typing import Any, Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import uuid
import hashlib


class Helpers:
    """Collection of helper functions with enhanced utilities"""
    
    # Constants
    DATE_FORMAT = '%B %d, %Y'
    TIME_FORMAT = '%I:%M %p'
    DATETIME_FORMAT = '%B %d, %Y at %I:%M %p'
    TRUNCATE_LENGTH = 50
    ROUND_MULTIPLE = 5
    
    # Month names
    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    # Weekdays
    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # ==========================================
    # ID & HASHING
    # ==========================================
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID (8 characters)"""
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate full UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def hash_string(text: str) -> str:
        """Hash a string using SHA256"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    @staticmethod
    def is_valid_uuid(uuid_str: str) -> bool:
        """Check if string is a valid UUID"""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_str.lower()))
    
    # ==========================================
    # DATE & TIME
    # ==========================================
    
    @staticmethod
    def get_current_time() -> str:
        """Get current time in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date string"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime(Helpers.DATE_FORMAT)
        except:
            return date_str
    
    @staticmethod
    def format_time(date_str: str) -> str:
        """Format time string"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime(Helpers.TIME_FORMAT)
        except:
            return date_str
    
    @staticmethod
    def format_datetime(date_str: str) -> str:
        """Format date and time"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime(Helpers.DATETIME_FORMAT)
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
    def get_day_index(date_str: str) -> int:
        """Get day index (0-6, Monday=0)"""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.weekday()
        except:
            return -1
    
    @staticmethod
    def get_month_name(month: int) -> str:
        """Get month name from month number"""
        return Helpers.MONTHS[month - 1] if 1 <= month <= 12 else ''
    
    @staticmethod
    def get_week_range(date_str: str) -> Tuple[str, str]:
        """Get start and end of week for a date"""
        try:
            dt = datetime.fromisoformat(date_str)
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
            return (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        except:
            return ('', '')
    
    @staticmethod
    def get_date_range(start_date: str, end_date: str) -> List[str]:
        """Get list of dates between start and end"""
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            
            dates = []
            current = start
            while current <= end:
                dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
            return dates
        except:
            return []
    
    @staticmethod
    def is_today(date_str: str) -> bool:
        """Check if date is today"""
        try:
            dt = datetime.fromisoformat(date_str).date()
            return dt == datetime.now().date()
        except:
            return False
    
    @staticmethod
    def is_this_week(date_str: str) -> bool:
        """Check if date is in current week"""
        try:
            dt = datetime.fromisoformat(date_str)
            now = datetime.now()
            return dt.isocalendar()[1] == now.isocalendar()[1]
        except:
            return False
    
    # ==========================================
    # JSON
    # ==========================================
    
    @staticmethod
    def safe_json_loads(json_str: str) -> Optional[Dict]:
        """Safely load JSON string"""
        try:
            return json.loads(json_str)
        except:
            return None
    
    @staticmethod
    def safe_json_dumps(data: Any, indent: int = 2) -> str:
        """Safely dump to JSON string"""
        try:
            return json.dumps(data, indent=indent, default=str)
        except:
            return '{}'
    
    @staticmethod
    def pretty_print_json(data: Any, indent: int = 2) -> str:
        """
        Pretty print JSON data with colors
        
        Args:
            data: Data to pretty print
            indent: Indentation level
            
        Returns:
            Pretty printed JSON string
        """
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
        except:
            return str(data)
    
    # ==========================================
    # STRING
    # ==========================================
    
    @staticmethod
    def truncate_string(text: str, max_length: int = TRUNCATE_LENGTH) -> str:
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
    def pluralize(count: int, singular: str, plural: str = None) -> str:
        """Pluralize a word based on count"""
        if plural is None:
            plural = singular + 's'
        return singular if count == 1 else plural
    
    @staticmethod
    def title_case(text: str) -> str:
        """Convert text to title case"""
        return text.title()
    
    @staticmethod
    def snake_case(text: str) -> str:
        """Convert text to snake_case"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '_', text)
        text = re.sub(r'_+', '_', text)
        return text.strip('_')
    
    @staticmethod
    def camel_case(text: str) -> str:
        """Convert text to camelCase"""
        parts = text.split()
        if not parts:
            return ''
        result = parts[0].lower()
        for part in parts[1:]:
            result += part.title()
        return result
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address
            
        Returns:
            True if valid
        """
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    # ==========================================
    # MATH
    # ==========================================
    
    @staticmethod
    def calculate_percentage(value: float, total: float) -> float:
        """Calculate percentage"""
        if total == 0:
            return 0
        return round((value / total) * 100, 2)
    
    @staticmethod
    def round_to_nearest(value: float, multiple: float = ROUND_MULTIPLE) -> float:
        """Round to nearest multiple"""
        return round(value / multiple) * multiple
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max"""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def is_valid_number(value: Any) -> bool:
        """Check if value is a valid number"""
        try:
            float(value)
            return True
        except:
            return False
    
    # ==========================================
    # FORMATTING
    # ==========================================
    
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
    def format_timestamp(timestamp: float) -> str:
        """Format timestamp to human-readable"""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(timestamp)
    
    @staticmethod
    def time_delta(start_time: datetime, end_time: datetime) -> str:
        """Get human-readable time difference"""
        delta = end_time - start_time
        total_seconds = delta.total_seconds()
        
        if total_seconds < 60:
            return f"{int(total_seconds)} seconds"
        elif total_seconds < 3600:
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format size in bytes to human readable
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human readable size
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / 1024**2:.1f} MB"
        elif size_bytes < 1024**4:
            return f"{size_bytes / 1024**3:.1f} GB"
        else:
            return f"{size_bytes / 1024**4:.1f} TB"
    
    # ==========================================
    # COLORS
    # ==========================================
    
    @staticmethod
    def get_productivity_color(score: float) -> str:
        """Get color based on productivity score"""
        if score >= 80:
            return '#2ECC71'  # Green
        elif score >= 60:
            return '#F39C12'  # Orange
        elif score >= 40:
            return '#F1C40F'  # Yellow
        else:
            return '#E74C3C'  # Red
    
    @staticmethod
    def get_gradient_color(score: float, min_score: float = 0, max_score: float = 100) -> str:
        """Get gradient color between red and green"""
        ratio = (score - min_score) / (max_score - min_score)
        ratio = max(0, min(1, ratio))
        
        red = int(255 - (ratio * 255))
        green = int(ratio * 255)
        blue = 0
        
        return f'#{red:02x}{green:02x}{blue:02x}'
    
    @staticmethod
    def get_mood_color(mood: int) -> str:
        """Get color based on mood rating"""
        colors = {
            1: '#E74C3C',  # Red
            2: '#F39C12',  # Orange
            3: '#F1C40F',  # Yellow
            4: '#2ECC71',  # Green
            5: '#3498DB'   # Blue
        }
        return colors.get(mood, '#95A5A6')  # Gray default
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple
        
        Args:
            hex_color: Hex color string (e.g., '#2ECC71')
            
        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        Convert RGB tuple to hex color
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            
        Returns:
            Hex color string
        """
        return f'#{r:02x}{g:02x}{b:02x}'
    
    # ==========================================
    # FILE
    # ==========================================
    
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
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def get_filename_without_extension(filename: str) -> str:
        """Get filename without extension"""
        return os.path.splitext(filename)[0]
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except:
            return False
    
    @staticmethod
    def get_file_creation_date(file_path: str) -> Optional[str]:
        """Get file creation date"""
        try:
            timestamp = os.path.getctime(file_path)
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return None
    
    # ==========================================
    # DECORATORS
    # ==========================================
    
    @staticmethod
    def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """
        Decorator to retry a function on failure
        
        Args:
            max_attempts: Maximum number of attempts
            delay: Initial delay in seconds
            backoff: Multiplier for delay after each attempt
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                attempt = 0
                current_delay = delay
                while attempt < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempt += 1
                        if attempt >= max_attempts:
                            raise
                        time.sleep(current_delay)
                        current_delay *= backoff
                return None
            return wrapper
        return decorator


class RateLimiter:
    """
    Simple rate limiter for API calls
    
    Features:
    - Per-call rate limiting
    - Per-second limits
    - Thread-safe
    """
    
    def __init__(self, max_calls: int = 10, period: float = 1.0):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)
        self._lock = threading.Lock()
    
    def __call__(self, key: str = "default") -> bool:
        """Check if rate limit is exceeded"""
        with self._lock:
            now = time.time()
            self.calls[key] = [t for t in self.calls[key] if now - t < self.period]
            
            if len(self.calls[key]) >= self.max_calls:
                return False
            
            self.calls[key].append(now)
            return True
    
    def reset(self, key: str = "default") -> None:
        """Reset rate limit for a key"""
        with self._lock:
            self.calls[key] = []
    
    def get_remaining(self, key: str = "default") -> int:
        """Get remaining calls allowed"""
        with self._lock:
            now = time.time()
            self.calls[key] = [t for t in self.calls[key] if now - t < self.period]
            return max(0, self.max_calls - len(self.calls[key]))