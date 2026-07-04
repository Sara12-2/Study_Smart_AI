"""
Validation Utilities
Comprehensive input validation with enhanced security
"""

import re
import os
from typing import Any, Optional, List
from datetime import datetime


class Validator:
    """Collection of validation methods with enhanced security"""
    
    # Constants
    MAX_NOTES_LENGTH = 500
    MAX_TAG_LENGTH = 20
    MIN_SUBJECT_LENGTH = 2
    MAX_SUBJECT_LENGTH = 50
    MIN_DURATION = 5
    MAX_DURATION = 240
    MIN_DISTRACTIONS = 0
    MAX_DISTRACTIONS = 20
    MIN_MOOD = 1
    MAX_MOOD = 5
    
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
        
        # Check length
        if not (Validator.MIN_SUBJECT_LENGTH <= len(subject) <= Validator.MAX_SUBJECT_LENGTH):
            return False
        
        # Check for allowed characters (alphanumeric, spaces, common punctuation)
        if not re.match(r'^[a-zA-Z0-9\s\-_.,:;()&]+$', subject):
            return False
        
        return True
    
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
            return Validator.MIN_DURATION <= duration <= Validator.MAX_DURATION
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
            return Validator.MIN_DISTRACTIONS <= distractions <= Validator.MAX_DISTRACTIONS
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
            return Validator.MIN_MOOD <= mood <= Validator.MAX_MOOD
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_rating(value: Any, min_val: int = 1, max_val: int = 5) -> bool:
        """
        Validate rating value
        
        Args:
            value: Rating value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            True if valid
        """
        if value is None:
            return True
        try:
            value = int(value)
            return min_val <= value <= max_val
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
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """
        Validate date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            True if valid
        """
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            return start <= end
        except:
            return False
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validate session ID format (UUID)
        
        Args:
            session_id: Session ID string (8-char hex)
            
        Returns:
            True if valid
        """
        if not session_id:
            return False
        pattern = r'^[a-f0-9]{8}$'
        return bool(re.match(pattern, session_id.lower()))
    
    @staticmethod
    def validate_tags(tags: List[str]) -> bool:
        """
        Validate tags list
        
        Args:
            tags: List of tags
            
        Returns:
            True if valid
        """
        if not tags:
            return True
        if not isinstance(tags, list):
            return False
        
        for tag in tags:
            if not isinstance(tag, str):
                return False
            if len(tag) > Validator.MAX_TAG_LENGTH:
                return False
            if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
                return False
        
        return True
    
    @staticmethod
    def validate_notes(notes: Optional[str]) -> bool:
        """
        Validate notes length
        
        Args:
            notes: Notes text
            
        Returns:
            True if valid
        """
        if notes is None:
            return True
        if not isinstance(notes, str):
            return False
        return len(notes) <= Validator.MAX_NOTES_LENGTH
    
    @staticmethod
    def validate_productivity_score(score: Any) -> bool:
        """
        Validate productivity score
        
        Args:
            score: Productivity score (0-100)
            
        Returns:
            True if valid
        """
        try:
            score = int(score)
            return 0 <= score <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Validate file path for security
        
        Args:
            file_path: File path
            
        Returns:
            True if valid
        """
        if not file_path:
            return False
        
        # Check for path traversal
        if '..' in file_path:
            return False
        
        # Check for absolute paths
        if os.path.isabs(file_path):
            return False
        
        # Check for allowed characters
        if not re.match(r'^[a-zA-Z0-9_\-./]+$', file_path):
            return False
        
        return True
    
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
        
        # Subject validation
        if 'subject' not in data or not Validator.validate_subject(data['subject']):
            errors.append(f'Subject must be {Validator.MIN_SUBJECT_LENGTH}-{Validator.MAX_SUBJECT_LENGTH} characters (alphanumeric, spaces, . , - _ : ; ( ) &)')
        
        # Duration validation
        if 'duration' not in data or not Validator.validate_duration(data['duration']):
            errors.append(f'Duration must be {Validator.MIN_DURATION}-{Validator.MAX_DURATION} minutes')
        
        # Distractions validation
        if 'distractions' in data and not Validator.validate_distractions(data['distractions']):
            errors.append(f'Distractions must be {Validator.MIN_DISTRACTIONS}-{Validator.MAX_DISTRACTIONS}')
        
        # Mood validation
        if 'mood' in data and not Validator.validate_mood(data['mood']):
            errors.append(f'Mood must be {Validator.MIN_MOOD}-{Validator.MAX_MOOD}')
        
        # Timestamp validation
        if 'timestamp' in data and not Validator.validate_timestamp(data['timestamp']):
            errors.append('Invalid timestamp format (use ISO format)')
        
        # Session ID validation
        if 'session_id' in data and not Validator.validate_session_id(data['session_id']):
            errors.append('Invalid session ID format')
        
        # Notes validation
        if 'notes' in data and not Validator.validate_notes(data['notes']):
            errors.append(f'Notes must be less than {Validator.MAX_NOTES_LENGTH} characters')
        
        # Tags validation
        if 'tags' in data and not Validator.validate_tags(data['tags']):
            errors.append('Tags must be alphanumeric, 1-20 characters')
        
        # Productivity score validation
        if 'productivity_score' in data and not Validator.validate_productivity_score(data['productivity_score']):
            errors.append('Productivity score must be 0-100')
        
        return errors
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize string input - removes dangerous characters
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not value:
            return ''
        
        # Remove special characters
        value = re.sub(r'[<>"\'/\\]', '', value)
        
        # Remove script tags
        value = re.sub(r'<script.*?>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags
        value = re.sub(r'<[^>]+>', '', value)
        
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
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number (basic)
        
        Args:
            phone: Phone number
            
        Returns:
            True if valid
        """
        if not phone:
            return True
        
        # Allow +, digits, spaces, -, (, )
        pattern = r'^[\+\d\s\-\(\)]{7,20}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL
        
        Args:
            url: URL string
            
        Returns:
            True if valid
        """
        if not url:
            return True
        
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w.-]*$'
        return bool(re.match(pattern, url))