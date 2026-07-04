"""
Study Session Management Module
Enterprise-grade session handling with validation and tracking
"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class ProductivityLevel(Enum):
    """Productivity levels based on distraction count"""
    EXCELLENT = (95, "🌟 Excellent focus - Perfect session!")
    GOOD = (85, "👍 Good focus - Minimal distractions")
    ABOVE_AVERAGE = (75, "📈 Above average - Keep going!")
    MODERATE = (65, "📊 Moderate focus - Some distractions")
    BELOW_AVERAGE = (55, "📉 Below average - Try to focus more")
    LOW = (40, "⚠️ Low focus - Too many distractions")
    
    def __init__(self, score: int, message: str):
        self.score = score
        self.message = message


class SessionStatus(Enum):
    """Session status"""
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    IN_PROGRESS = "in_progress"


@dataclass
class StudySession:
    """
    Enterprise-grade Study Session with validation and tracking
    
    Attributes:
        subject: Subject name (min 2 chars, max 50) - REQUIRED
        duration: Duration in minutes (5-240 minutes) - REQUIRED
        session_id: Unique session identifier (auto-generated)
        distractions: Number of distractions (0-20)
        productivity_score: Calculated score (0-100)
        timestamp: ISO format timestamp
        notes: Optional session notes
        mood: Optional mood rating (1-5)
        status: Session status
    """
    
    # ==========================================
    # NON-DEFAULT FIELDS FIRST (no default values)
    # These MUST come before any field with default
    # ==========================================
    subject: str
    duration: int
    
    # ==========================================
    # DEFAULT FIELDS SECOND (with default values)
    # ==========================================
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    distractions: int = 0
    productivity_score: Optional[int] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[int] = None
    status: SessionStatus = SessionStatus.COMPLETED
    
    def __post_init__(self):
        """Validate data after initialization"""
        self._validate_subject()
        self._validate_duration()
        self._validate_distractions()
        self._validate_mood()
        self._set_timestamp()
        self._calculate_productivity()
        logger.info(f"Session created: {self.session_id} - {self.subject} - {self.duration}min")
    
    def _validate_subject(self) -> None:
        """Validate subject name"""
        if not self.subject or len(self.subject.strip()) < 2:
            raise ValueError("Subject must be at least 2 characters")
        if len(self.subject) > 50:
            raise ValueError("Subject must be less than 50 characters")
        self.subject = self.subject.strip().title()
    
    def _validate_duration(self) -> None:
        """Validate duration with warning for long sessions"""
        if not isinstance(self.duration, int):
            raise TypeError("Duration must be an integer")
        if self.duration < 5:
            raise ValueError("Duration must be at least 5 minutes")
        if self.duration > 240:
            raise ValueError("Duration cannot exceed 240 minutes (4 hours)")
        if self.duration > 120:
            logger.warning(f"Long session: {self.duration}min - consider taking a break")
    
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
        # Base productivity
        base_score = 100
        
        # Distraction penalty (exponential)
        if self.distractions > 0:
            penalty = min(80, (self.distractions ** 1.5) * 5)
            base_score -= penalty
        
        # Duration bonus (optimal is 45-60 min)
        duration_factor = 1.0
        if 45 <= self.duration <= 60:
            duration_factor = 1.1  # 10% bonus for optimal duration
        elif self.duration > 120:
            duration_factor = 0.9  # 10% penalty for long sessions
        
        self.productivity_score = max(10, min(100, int(base_score * duration_factor)))
        
        # Assign level
        if self.productivity_score >= 90:
            self._productivity_message = ProductivityLevel.EXCELLENT.message
        elif self.productivity_score >= 80:
            self._productivity_message = ProductivityLevel.GOOD.message
        elif self.productivity_score >= 70:
            self._productivity_message = ProductivityLevel.ABOVE_AVERAGE.message
        elif self.productivity_score >= 60:
            self._productivity_message = ProductivityLevel.MODERATE.message
        elif self.productivity_score >= 50:
            self._productivity_message = ProductivityLevel.BELOW_AVERAGE.message
        else:
            self._productivity_message = ProductivityLevel.LOW.message
        
        logger.debug(f"Productivity calculated: {self.productivity_score}%")
    
    def get_productivity_level(self) -> ProductivityLevel:
        """Get productivity level enum"""
        if self.productivity_score >= 90:
            return ProductivityLevel.EXCELLENT
        elif self.productivity_score >= 80:
            return ProductivityLevel.GOOD
        elif self.productivity_score >= 70:
            return ProductivityLevel.ABOVE_AVERAGE
        elif self.productivity_score >= 60:
            return ProductivityLevel.MODERATE
        elif self.productivity_score >= 50:
            return ProductivityLevel.BELOW_AVERAGE
        else:
            return ProductivityLevel.LOW
    
    def get_productivity_message(self) -> str:
        """Get productivity feedback message"""
        return getattr(self, '_productivity_message', "Productivity calculated")
    
    def get_formatted_duration(self) -> str:
        """Get human-readable duration"""
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours == 0:
            return f"{minutes} min"
        elif minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        return f"{hours}h {minutes}min"
    
    def is_today(self) -> bool:
        """Check if session is from today"""
        try:
            return datetime.now().date() == datetime.fromisoformat(self.timestamp).date()
        except:
            return False
    
    def is_this_week(self) -> bool:
        """Check if session is from this week"""
        try:
            now = datetime.now()
            session_date = datetime.fromisoformat(self.timestamp)
            return session_date.isocalendar()[1] == now.isocalendar()[1]
        except:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for JSON serialization
        
        Returns:
            Dict with all session data
        """
        data = asdict(self)
        
        # Convert enum to string for JSON serialization
        if 'status' in data and hasattr(data['status'], 'value'):
            data['status'] = data['status'].value
        
        data['productivity_level'] = self.get_productivity_level().name
        data['productivity_message'] = self.get_productivity_message()
        data['formatted_duration'] = self.get_formatted_duration()
        data['is_today'] = self.is_today()
        data['is_this_week'] = self.is_this_week()
        
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
            session_id=data.get('session_id', str(uuid.uuid4())[:8]),
            subject=data['subject'],
            duration=data['duration'],
            distractions=data.get('distractions', 0),
            timestamp=data.get('timestamp'),
            notes=data.get('notes'),
            mood=data.get('mood'),
            status=SessionStatus(data.get('status', 'completed'))
        )
    
    def __str__(self) -> str:
        return f"📚 {self.subject} | {self.get_formatted_duration()} | {self.productivity_score}% productive"
    
    def __repr__(self) -> str:
        return f"StudySession(id='{self.session_id}', subject='{self.subject}', duration={self.duration}, distractions={self.distractions})"