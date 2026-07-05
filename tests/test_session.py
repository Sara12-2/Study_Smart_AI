"""
Unit Tests for Session Module
Testing StudySession class functionality
"""

import unittest
from datetime import datetime
from src.core.session import StudySession, ProductivityLevel, SessionStatus


class TestStudySession(unittest.TestCase):
    """Test StudySession class"""
    
    def setUp(self):
        """Setup before each test"""
        self.session = StudySession("Python Programming", 60, 2)
    
    def test_session_creation(self):
        """Test session creation with valid data"""
        self.assertEqual(self.session.subject, "Python Programming")
        self.assertEqual(self.session.duration, 60)
        self.assertEqual(self.session.distractions, 2)
        self.assertIsNotNone(self.session.timestamp)
        self.assertIsNotNone(self.session.productivity_score)
        self.assertIsNotNone(self.session.session_id)
        self.assertEqual(self.session.status, SessionStatus.COMPLETED)
    
    def test_session_creation_with_notes(self):
        """Test session creation with notes and mood"""
        session = StudySession(
            subject="Machine Learning",
            duration=90,
            distractions=1,
            notes="Studied neural networks",
            mood=4
        )
        self.assertEqual(session.notes, "Studied neural networks")
        self.assertEqual(session.mood, 4)
    
    def test_session_creation_with_energy(self):
        """Test session creation with energy level"""
        session = StudySession(
            subject="Data Science",
            duration=60,
            distractions=0,
            energy=5,
            tags=["python", "pandas"]
        )
        self.assertEqual(session.energy, 5)
        self.assertEqual(session.tags, ["python", "pandas"])
    
    def test_productivity_calculation(self):
        """Test productivity score calculation"""
        # Zero distractions - Perfect focus
        session = StudySession("Math", 30, 0)
        session.calculate_productivity()
        self.assertEqual(session.productivity_score, 100)
        self.assertEqual(session.get_productivity_level(), ProductivityLevel.EXCELLENT)
        
        # Few distractions - Good focus
        session = StudySession("Physics", 45, 2)
        session.calculate_productivity()
        self.assertEqual(session.productivity_score, 80)
        self.assertEqual(session.get_productivity_level(), ProductivityLevel.GOOD)
        
        # Moderate distractions
        session = StudySession("Chemistry", 60, 4)
        session.calculate_productivity()
        self.assertEqual(session.productivity_score, 60)
        self.assertEqual(session.get_productivity_level(), ProductivityLevel.MODERATE)
        
        # Many distractions - Low focus
        session = StudySession("Biology", 90, 7)
        session.calculate_productivity()
        self.assertEqual(session.productivity_score, 40)
        self.assertEqual(session.get_productivity_level(), ProductivityLevel.LOW)
    
    def test_productivity_with_duration_bonus(self):
        """Test productivity with duration bonus"""
        # Optimal duration (45-60 min) should get bonus
        session = StudySession("Python", 50, 0)
        session.calculate_productivity()
        self.assertEqual(session.productivity_score, 110)  # 100 * 1.1
        
        # Long duration penalty
        session = StudySession("Python", 150, 0)
        session.calculate_productivity()
        self.assertEqual(session.productivity_score, 90)  # 100 * 0.9
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        self.session.calculate_productivity()
        data = self.session.to_dict()
        
        self.assertEqual(data['subject'], "Python Programming")
        self.assertEqual(data['duration'], 60)
        self.assertEqual(data['distractions'], 2)
        self.assertIn('productivity_score', data)
        self.assertIn('timestamp', data)
        self.assertIn('productivity_level', data)
        self.assertIn('productivity_message', data)
        self.assertIn('session_id', data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], "completed")
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'session_id': 'abc12345',
            'subject': 'Data Science',
            'duration': 120,
            'distractions': 3,
            'timestamp': '2026-01-15T10:00:00',
            'notes': 'Worked on pandas',
            'mood': 5,
            'energy': 4,
            'tags': ['data', 'python'],
            'status': 'completed'
        }
        session = StudySession.from_dict(data)
        
        self.assertEqual(session.session_id, 'abc12345')
        self.assertEqual(session.subject, 'Data Science')
        self.assertEqual(session.duration, 120)
        self.assertEqual(session.distractions, 3)
        self.assertEqual(session.notes, 'Worked on pandas')
        self.assertEqual(session.mood, 5)
        self.assertEqual(session.energy, 4)
        self.assertEqual(session.tags, ['data', 'python'])
        self.assertEqual(session.status, SessionStatus.COMPLETED)
    
    def test_string_representation(self):
        """Test string representation"""
        self.session.calculate_productivity()
        str_repr = str(self.session)
        self.assertIn("Python Programming", str_repr)
        self.assertIn("60", str_repr)
    
    def test_repr_representation(self):
        """Test repr representation"""
        repr_str = repr(self.session)
        self.assertIn("StudySession", repr_str)
        self.assertIn("Python Programming", repr_str)
        self.assertIn("60", repr_str)
    
    def test_invalid_subject(self):
        """Test invalid subject validation"""
        with self.assertRaises(ValueError):
            StudySession("", 60)
        
        with self.assertRaises(ValueError):
            StudySession("A" * 51, 60)
    
    def test_invalid_duration(self):
        """Test invalid duration validation"""
        with self.assertRaises(ValueError):
            StudySession("Python", 1)  # Too short
        
        with self.assertRaises(ValueError):
            StudySession("Python", 300)  # Too long
        
        with self.assertRaises(TypeError):
            StudySession("Python", "abc")  # Wrong type
    
    def test_invalid_distractions(self):
        """Test invalid distractions validation"""
        with self.assertRaises(ValueError):
            StudySession("Python", 30, -1)  # Negative
        
        with self.assertRaises(ValueError):
            StudySession("Python", 30, 25)  # Too many
    
    def test_invalid_mood(self):
        """Test invalid mood validation"""
        with self.assertRaises(ValueError):
            StudySession("Python", 30, 0, mood=0)  # Too low
        
        with self.assertRaises(ValueError):
            StudySession("Python", 30, 0, mood=6)  # Too high
        
        with self.assertRaises(TypeError):
            StudySession("Python", 30, 0, mood="abc")  # Wrong type
    
    def test_invalid_energy(self):
        """Test invalid energy validation"""
        with self.assertRaises(ValueError):
            StudySession("Python", 30, 0, energy=0)  # Too low
        
        with self.assertRaises(ValueError):
            StudySession("Python", 30, 0, energy=6)  # Too high
        
        with self.assertRaises(TypeError):
            StudySession("Python", 30, 0, energy="abc")  # Wrong type
    
    def test_productivity_message(self):
        """Test productivity message"""
        session = StudySession("Python", 30, 0)
        session.calculate_productivity()
        self.assertIn("Excellent", session.get_productivity_message())
        
        session = StudySession("Python", 30, 8)
        session.calculate_productivity()
        self.assertIn("Low", session.get_productivity_message())
    
    def test_get_formatted_duration(self):
        """Test formatted duration"""
        session = StudySession("Python", 30, 0)
        self.assertEqual(session.get_formatted_duration(), "30 min")
        
        session = StudySession("Python", 60, 0)
        self.assertEqual(session.get_formatted_duration(), "1 hour")
        
        session = StudySession("Python", 90, 0)
        self.assertEqual(session.get_formatted_duration(), "1h 30min")
        
        session = StudySession("Python", 120, 0)
        self.assertEqual(session.get_formatted_duration(), "2 hours")
    
    def test_is_today(self):
        """Test is_today method"""
        # Session with today's date
        today = datetime.now().isoformat()
        session = StudySession("Python", 30, 0, timestamp=today)
        self.assertTrue(session.is_today())
        
        # Session with yesterday's date
        yesterday = datetime.now().replace(day=datetime.now().day - 1).isoformat()
        session = StudySession("Python", 30, 0, timestamp=yesterday)
        self.assertFalse(session.is_today())
    
    def test_add_tag(self):
        """Test adding tags"""
        session = StudySession("Python", 30, 0)
        session.add_tag("python")
        session.add_tag("programming")
        
        self.assertIn("python", session.tags)
        self.assertIn("programming", session.tags)
        self.assertEqual(len(session.tags), 2)
    
    def test_remove_tag(self):
        """Test removing tags"""
        session = StudySession("Python", 30, 0)
        session.add_tag("python")
        session.add_tag("programming")
        
        session.remove_tag("python")
        self.assertNotIn("python", session.tags)
        self.assertIn("programming", session.tags)
    
    def test_calculate_focus_score(self):
        """Test focus score calculation"""
        session = StudySession("Python", 50, 0, mood=5)
        session.calculate_productivity()
        focus_score = session.calculate_focus_score()
        
        self.assertGreaterEqual(focus_score, 0)
        self.assertLessEqual(focus_score, 100)
    
    def test_get_summary(self):
        """Test session summary"""
        self.session.calculate_productivity()
        summary = self.session.get_summary()
        
        self.assertIn('id', summary)
        self.assertIn('subject', summary)
        self.assertIn('duration', summary)
        self.assertIn('formatted_duration', summary)
        self.assertIn('productivity', summary)
        self.assertIn('level', summary)
        self.assertIn('message', summary)
        self.assertIn('date', summary)
        self.assertIn('status', summary)


if __name__ == '__main__':
    unittest.main()