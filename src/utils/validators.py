"""
Validation Utilities
Comprehensive input validation
"""

import re
from typing import Any, Optional, List
from datetime import datetime


class Validator:
    """Collection of validation methods"""
    
    @staticmethod
    def validate_subject(subject: str) -> bool:
        """
        Validate subject name
        
        Args:
            subject: Subject name
            
        Returns:
            True if valid
        """
        if not subject:
            return False
        subject = subject.strip()
        return 2 <= len(subject) <= 50
    
    @staticmethod
    def validate_duration(duration: Any) -> bool:
        """
        Validate duration
        
        Args:
            duration: Duration in minutes
            
        Returns:
            True if valid
        """
        try:
            duration = int(duration)
            return 5 <= duration <= 240
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_distractions(distractions: Any) -> bool:
        """
        Validate distraction count
        
        Args:
            distractions: Number of distractions
            
        Returns:
            True if valid
        """
        try:
            distractions = int(distractions)
            return 0 <= distractions <= 20
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_mood(mood: Any) -> bool:
        """
        Validate mood rating
        
        Args:
            mood: Mood rating 1-5
            
        Returns:
            True if valid
        """
        if mood is None:
            return True
        try:
            mood = int(mood)
            return 1 <= mood <= 5
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_timestamp(timestamp: str) -> bool:
        """
        Validate timestamp format
        
        Args:
            timestamp: ISO format timestamp
            
        Returns:
            True if valid
        """
        try:
            datetime.fromisoformat(timestamp)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_session_data(data: dict) -> List[str]:
        """
        Validate complete session data
        
        Args:
            data: Session dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if 'subject' not in data or not Validator.validate_subject(data['subject']):
            errors.append('Subject must be 2-50 characters')
        
        if 'duration' not in data or not Validator.validate_duration(data['duration']):
            errors.append('Duration must be 5-240 minutes')
        
        if 'distractions' in data and not Validator.validate_distractions(data['distractions']):
            errors.append('Distractions must be 0-20')
        
        if 'mood' in data and not Validator.validate_mood(data['mood']):
            errors.append('Mood must be 1-5')
        
        if 'timestamp' in data and not Validator.validate_timestamp(data['timestamp']):
            errors.append('Invalid timestamp format')
        
        return errors
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize string input
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not value:
            return ''
        
        # Remove special characters
        value = re.sub(r'[<>"\'/]', '', value)
        
        # Trim whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address
            
        Returns:
            True if valid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) if email else False