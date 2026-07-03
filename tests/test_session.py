"""
Unit Tests for Session Module
Testing StudySession class functionality
"""

import unittest
from datetime import datetime
from src.core.session import StudySession, ProductivityLevel


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
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'subject': 'Data Science',
            'duration': 120,
            'distractions': 3,
            'timestamp': '2026-01-15T10:00:00',
            'notes': 'Worked on pandas',
            'mood': 5
        }
        session = StudySession.from_dict(data)
        
        self.assertEqual(session.subject, 'Data Science')
        self.assertEqual(session.duration, 120)
        self.assertEqual(session.distractions, 3)
        self.assertEqual(session.notes, 'Worked on pandas')
        self.assertEqual(session.mood, 5)
    
    def test_string_representation(self):
        """Test string representation"""
        self.session.calculate_productivity()
        str_repr = str(self.session)
        self.assertIn("Python Programming", str_repr)
        self.assertIn("60", str_repr)
    
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
    
    def test_productivity_message(self):
        """Test productivity message"""
        session = StudySession("Python", 30, 0)
        session.calculate_productivity()
        self.assertIn("Excellent", session.get_productivity_message())
        
        session = StudySession("Python", 30, 8)
        session.calculate_productivity()
        self.assertIn("Low", session.get_productivity_message())


if __name__ == '__main__':
    unittest.main()