"""
Study Session Management Module
Enterprise-grade session handling with validation and tracking
"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)


class ProductivityLevel(Enum):
    """Productivity levels based on distraction count"""
    EXCELLENT = (100, "🌟 Excellent focus - Zero distractions!")
    GOOD = (80, "👍 Good focus - Minimal distractions")
    MODERATE = (60, "📊 Moderate focus - Some distractions")
    LOW = (40, "⚠️ Low focus - Too many distractions")
    
    def __init__(self, score: int, message: str):
        self.score = score
        self.message = message


@dataclass
class StudySession:
    """
    Enterprise-grade Study Session with validation and tracking
    
    Attributes:
        subject: Subject name (min 2 chars, max 50)
        duration: Duration in minutes (5-240 minutes)
        distractions: Number of distractions (0-20)
        productivity_score: Calculated score (0-100)
        timestamp: ISO format timestamp
        notes: Optional session notes
        mood: Optional mood rating (1-5)
    """
    
    subject: str
    duration: int
    distractions: int = 0
    productivity_score: Optional[int] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[int] = None
    
    def __post_init__(self):
        """Validate data after initialization"""
        self._validate_subject()
        self._validate_duration()
        self._validate_distractions()
        self._validate_mood()
        self._set_timestamp()
        self._calculate_productivity()
        logger.info(f"Session created: {self.subject} - {self.duration}min")
    
    def _validate_subject(self) -> None:
        """Validate subject name"""
        if not self.subject or len(self.subject.strip()) < 2:
            raise ValueError("Subject must be at least 2 characters")
        if len(self.subject) > 50:
            raise ValueError("Subject must be less than 50 characters")
        self.subject = self.subject.strip().title()
    
    def _validate_duration(self) -> None:
        """Validate duration"""
        if not isinstance(self.duration, int):
            raise TypeError("Duration must be an integer")
        if self.duration < 5:
            raise ValueError("Duration must be at least 5 minutes")
        if self.duration > 240:
            raise ValueError("Duration cannot exceed 240 minutes (4 hours)")
    
    def _validate_distractions(self) -> None:
        """Validate distraction count"""
        if not isinstance(self.distractions, int):
            raise TypeError("Distractions must be an integer")
        if self.distractions < 0:
            raise ValueError("Distractions cannot be negative")
        if self.distractions > 20:
            raise ValueError("Distractions cannot exceed 20")
    
    def _validate_mood(self) -> None:
        """Validate mood rating"""
        if self.mood is not None:
            if not isinstance(self.mood, int):
                raise TypeError("Mood must be an integer")
            if self.mood < 1 or self.mood > 5:
                raise ValueError("Mood must be between 1 and 5")
    
    def _set_timestamp(self) -> None:
        """Set current timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def _calculate_productivity(self) -> None:
        """
        Calculate productivity score based on distractions
        Uses exponential decay model for realistic scoring
        """
        if self.distractions == 0:
            self.productivity_score = ProductivityLevel.EXCELLENT.score
            self._productivity_message = ProductivityLevel.EXCELLENT.message
        elif self.distractions <= 2:
            self.productivity_score = ProductivityLevel.GOOD.score
            self._productivity_message = ProductivityLevel.GOOD.message
        elif self.distractions <= 5:
            self.productivity_score = ProductivityLevel.MODERATE.score
            self._productivity_message = ProductivityLevel.MODERATE.message
        else:
            # Exponential decay for high distractions
            base_score = ProductivityLevel.LOW.score
            penalty = min(20, (self.distractions - 5) * 2)
            self.productivity_score = max(10, base_score - penalty)
            self._productivity_message = ProductivityLevel.LOW.message
        
        logger.debug(f"Productivity calculated: {self.productivity_score}%")
    
    def get_productivity_level(self) -> ProductivityLevel:
        """Get productivity level enum"""
        if self.productivity_score >= 90:
            return ProductivityLevel.EXCELLENT
        elif self.productivity_score >= 70:
            return ProductivityLevel.GOOD
        elif self.productivity_score >= 50:
            return ProductivityLevel.MODERATE
        else:
            return ProductivityLevel.LOW
    
    def get_productivity_message(self) -> str:
        """Get productivity feedback message"""
        return getattr(self, '_productivity_message', "Productivity calculated")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for JSON serialization
        
        Returns:
            Dict with all session data
        """
        data = asdict(self)
        data['productivity_level'] = self.get_productivity_level().name
        data['productivity_message'] = self.get_productivity_message()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudySession':
        """
        Create Session from dictionary
        
        Args:
            data: Dictionary containing session data
            
        Returns:
            StudySession instance
        """
        return cls(
            subject=data['subject'],
            duration=data['duration'],
            distractions=data.get('distractions', 0),
            timestamp=data.get('timestamp'),
            notes=data.get('notes'),
            mood=data.get('mood')
        )
    
    def __str__(self) -> str:
        return f"📚 {self.subject} | {self.duration}min | {self.productivity_score}% productive"
    
    def __repr__(self) -> str:
        return f"StudySession(subject='{self.subject}', duration={self.duration}, distractions={self.distractions})"