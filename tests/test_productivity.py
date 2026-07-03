"""
Unit Tests for Productivity Engine
Testing ProductivityEngine class functionality
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta

from src.core.session import StudySession
from src.core.productivity import ProductivityEngine
from src.storage.json_storage import JSONStorage


class TestProductivityEngine(unittest.TestCase):
    """Test ProductivityEngine class"""
    
    def setUp(self):
        """Setup before each test"""
        # Create temporary storage
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.storage = JSONStorage(self.temp_file.name)
        self.engine = ProductivityEngine(self.storage)
        
        # Add test sessions
        self._add_test_sessions()
    
    def tearDown(self):
        """Clean up after each test"""
        os.unlink(self.temp_file.name)
    
    def _add_test_sessions(self):
        """Add test sessions to storage"""
        sessions_data = [
            ("Python", 60, 0, "2026-01-15T09:00:00"),
            ("Java", 45, 2, "2026-01-15T14:00:00"),
            ("Python", 30, 1, "2026-01-16T10:00:00"),
            ("JavaScript", 90, 5, "2026-01-16T15:00:00"),
            ("Python", 120, 3, "2026-01-17T11:00:00"),
            ("SQL", 60, 0, "2026-01-17T16:00:00"),
            ("Java", 45, 4, "2026-01-18T09:30:00"),
            ("Python", 60, 2, "2026-01-18T14:30:00"),
        ]
        
        for subject, duration, distractions, timestamp in sessions_data:
            session = StudySession(subject, duration, distractions)
            session.calculate_productivity()
            session.timestamp = timestamp
            self.storage.save_session(session.to_dict())
    
    def test_calculate_daily_summary(self):
        """Test daily summary calculation"""
        summary = self.engine.calculate_daily_summary("2026-01-15")
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary['total_sessions'], 2)
        self.assertEqual(summary['total_time'], 105)  # 60 + 45
        self.assertGreater(summary['avg_productivity'], 0)
        self.assertEqual(len(summary['subjects']), 2)  # Python, Java
    
    def test_calculate_daily_summary_no_sessions(self):
        """Test daily summary with no sessions"""
        summary = self.engine.calculate_daily_summary("2026-01-20")
        self.assertIsNone(summary)
    
    def test_generate_weekly_report(self):
        """Test weekly report generation"""
        report = self.engine.generate_weekly_report()
        
        self.assertIsNotNone(report)
        self.assertIn('total_weeks', report)
        self.assertIn('total_sessions', report)
        self.assertIn('total_time', report)
        self.assertIn('overall_productivity', report)
        self.assertIn('weekly_reports', report)
        
        self.assertEqual(report['total_sessions'], 8)
    
    def test_analyze_subject_performance(self):
        """Test subject performance analysis"""
        analysis = self.engine.analyze_subject_performance()
        
        self.assertIsNotNone(analysis)
        self.assertIn('subjects', analysis)
        self.assertIn('total_subjects', analysis)
        
        # Python should have most sessions
        subjects = dict(analysis['subjects'])
        python_data = subjects.get('Python')
        self.assertIsNotNone(python_data)
        self.assertEqual(python_data['sessions'], 4)  # Python sessions
    
    def test_get_productivity_trends(self):
        """Test productivity trends"""
        trends = self.engine.get_productivity_trends(30)
        
        self.assertIsNotNone(trends)
        self.assertIn('total_sessions', trends)
        self.assertIn('daily_productivity', trends)
        self.assertIn('trend_direction', trends)
        self.assertIn('avg_productivity', trends)
    
    def test_get_optimal_study_times(self):
        """Test optimal study times analysis"""
        optimal = self.engine.get_optimal_study_times()
        
        self.assertIsNotNone(optimal)
        self.assertIn('optimal_hours', optimal)
        self.assertIn('recommendation', optimal)
        
        # Should have some recommendation
        self.assertIsInstance(optimal['recommendation'], str)
        self.assertGreater(len(optimal['recommendation']), 0)
    
    def test_empty_storage_handling(self):
        """Test handling with empty storage"""
        # Clear storage
        self.storage.clear_all_sessions()
        
        summary = self.engine.calculate_daily_summary()
        self.assertIsNone(summary)
        
        report = self.engine.generate_weekly_report()
        self.assertEqual(report['total_sessions'], 0)
        
        analysis = self.engine.analyze_subject_performance()
        self.assertIn('error', analysis)
    
    def test_weekly_report_structure(self):
        """Test weekly report structure"""
        report = self.engine.generate_weekly_report()
        
        # Check current week data
        self.assertIn('current_week', report)
        self.assertIn('current_week_sessions', report)
        self.assertIn('current_week_time', report)
        
        # Check best/worst week
        self.assertIn('best_week', report)
        self.assertIn('worst_week', report)
    
    def test_trend_detection(self):
        """Test trend detection"""
        trends = self.engine.get_productivity_trends(30)
        
        # Trend should be one of: improving, declining, stable, or insufficient_data
        valid_trends = ['improving', 'declining', 'stable', 'insufficient_data']
        self.assertIn(trends['trend_direction'], valid_trends)
    
    def test_subject_metrics(self):
        """Test subject metrics calculation"""
        analysis = self.engine.analyze_subject_performance()
        
        subjects = dict(analysis['subjects'])
        
        # Check each subject has required metrics
        for subject, metrics in subjects.items():
            self.assertIn('sessions', metrics)
            self.assertIn('total_time', metrics)
            self.assertIn('avg_productivity', metrics)
            self.assertIn('max_productivity', metrics)
            self.assertIn('min_productivity', metrics)
            self.assertIn('avg_distractions', metrics)


if __name__ == '__main__':
    unittest.main()