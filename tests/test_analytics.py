"""
Unit Tests for Analytics Module
Testing AI, storage, and helper utilities
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta

from src.core.session import StudySession
from src.core.productivity import ProductivityEngine
from src.storage.json_storage import JSONStorage
from src.ai.analyzer import AIAnalyzer
from src.ai.predictor import AIPredictor
from src.ai.recommender import AIRecommender
from src.utils.validators import Validator
from src.utils.helpers import Helpers, RateLimiter


class TestJSONStorage(unittest.TestCase):
    """Test JSONStorage class"""
    
    def setUp(self):
        """Setup before each test"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.storage = JSONStorage(self.temp_file.name)
    
    def tearDown(self):
        """Clean up after each test"""
        os.unlink(self.temp_file.name)
    
    def test_save_and_load_session(self):
        """Test saving and loading sessions"""
        session = StudySession("Python", 60, 2)
        session.calculate_productivity()
        
        self.storage.save_session(session.to_dict())
        sessions = self.storage.load_all_sessions()
        
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['subject'], "Python")
    
    def test_multiple_sessions(self):
        """Test multiple sessions"""
        for i in range(5):
            session = StudySession(f"Subject{i}", 30 + i, i % 3)
            session.calculate_productivity()
            self.storage.save_session(session.to_dict())
        
        sessions = self.storage.load_all_sessions()
        self.assertEqual(len(sessions), 5)
    
    def test_clear_sessions(self):
        """Test clearing sessions"""
        session = StudySession("Python", 30, 0)
        session.calculate_productivity()
        self.storage.save_session(session.to_dict())
        
        self.assertEqual(self.storage.get_session_count(), 1)
        self.storage.clear_all_sessions()
        self.assertEqual(self.storage.get_session_count(), 0)
    
    def test_session_count(self):
        """Test session count"""
        self.assertEqual(self.storage.get_session_count(), 0)
        
        for i in range(3):
            session = StudySession(f"Subject{i}", 30, 0)
            session.calculate_productivity()
            self.storage.save_session(session.to_dict())
        
        self.assertEqual(self.storage.get_session_count(), 3)
    
    def test_get_statistics(self):
        """Test storage statistics"""
        for i in range(3):
            session = StudySession(f"Subject{i}", 30, 0)
            session.calculate_productivity()
            self.storage.save_session(session.to_dict())
        
        stats = self.storage.get_statistics()
        self.assertEqual(stats['total_sessions'], 3)
        self.assertIn('file_size', stats)
        self.assertIn('subjects', stats)
    
    def test_get_sessions_by_date(self):
        """Test getting sessions by date"""
        session1 = StudySession("Python", 60, 0)
        session1.timestamp = "2026-01-15T10:00:00"
        session1.calculate_productivity()
        
        session2 = StudySession("Java", 45, 2)
        session2.timestamp = "2026-01-16T14:00:00"
        session2.calculate_productivity()
        
        self.storage.save_session(session1.to_dict())
        self.storage.save_session(session2.to_dict())
        
        sessions = self.storage.get_sessions_by_date("2026-01-15")
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['subject'], "Python")
    
    def test_delete_session(self):
        """Test deleting a session"""
        session = StudySession("Python", 60, 0)
        session.calculate_productivity()
        self.storage.save_session(session.to_dict())
        
        self.assertEqual(self.storage.get_session_count(), 1)
        self.storage.delete_session(0)
        self.assertEqual(self.storage.get_session_count(), 0)
    
    def test_create_backup(self):
        """Test creating backup"""
        session = StudySession("Python", 60, 0)
        session.calculate_productivity()
        self.storage.save_session(session.to_dict())
        
        backup_file = self.storage.create_backup()
        self.assertTrue(os.path.exists(backup_file))
        
        # Cleanup
        os.remove(backup_file)
    
    def test_export_import_csv(self):
        """Test CSV export and import"""
        session = StudySession("Python", 60, 0)
        session.calculate_productivity()
        self.storage.save_session(session.to_dict())
        
        csv_file = self.storage.export_to_csv("test_export.csv")
        self.assertTrue(os.path.exists(csv_file))
        
        # Import
        count = self.storage.import_from_csv(csv_file)
        self.assertEqual(count, 1)
        
        # Cleanup
        os.remove(csv_file)
        os.rmdir("exports")


class TestAIAnalyzer(unittest.TestCase):
    """Test AI Analyzer class"""
    
    def setUp(self):
        """Setup before each test"""
        self.analyzer = AIAnalyzer()
        self.sessions = []
        
        subjects = ["Python", "Java", "JavaScript", "SQL", "Python"]
        for i in range(10):
            session = StudySession(
                subject=subjects[i % len(subjects)],
                duration=30 + (i * 5),
                distractions=i % 4,
                mood=(i % 5) + 1,
                notes=f"Session {i+1}"
            )
            session.calculate_productivity()
            session.timestamp = f"2026-01-{str(15 + i).zfill(2)}T{str(8 + i % 8).zfill(2)}:00:00"
            self.sessions.append(session.to_dict())
    
    def test_prepare_dataframe(self):
        """Test DataFrame preparation"""
        df = self.analyzer.prepare_dataframe(self.sessions)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 10)
        self.assertIn('productivity_score', df.columns)
        self.assertIn('timestamp', df.columns)
    
    def test_analyze_patterns(self):
        """Test pattern analysis"""
        df = self.analyzer.prepare_dataframe(self.sessions)
        results = self.analyzer.analyze_productivity_patterns(df)
        
        self.assertIn('overall_stats', results)
        self.assertIn('daily_patterns', results)
        self.assertIn('hourly_patterns', results)
        self.assertIn('correlations', results)
    
    def test_detect_learning_patterns(self):
        """Test learning pattern detection"""
        df = self.analyzer.prepare_dataframe(self.sessions)
        patterns = self.analyzer.detect_learning_patterns(df)
        
        self.assertIn('best_learning_time', patterns)
        self.assertIn('most_consistent_subject', patterns)
        self.assertIn('distraction_patterns', patterns)
    
    def test_generate_insights(self):
        """Test insight generation"""
        insights = self.analyzer.generate_insights(self.sessions)
        
        self.assertIn('patterns', insights)
        self.assertIn('analysis', insights)
        self.assertIn('recommendations', insights)
        self.assertIn('ai_confidence', insights)
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        insights = self.analyzer.generate_insights(self.sessions[:3])
        self.assertIn('error', insights)
        self.assertIn('message', insights)
    
    def test_empty_data(self):
        """Test with empty data"""
        insights = self.analyzer.generate_insights([])
        self.assertIn('error', insights)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        self.analyzer.clear_cache()
        self.assertEqual(len(self.analyzer._cache), 0)


class TestAIPredictor(unittest.TestCase):
    """Test AI Predictor class"""
    
    def setUp(self):
        """Setup before each test"""
        self.predictor = AIPredictor()
        self.sessions = []
        
        for i in range(15):
            session = StudySession(
                subject="Python",
                duration=30 + (i * 5),
                distractions=i % 3
            )
            session.calculate_productivity()
            session.timestamp = f"2026-01-{str(10 + i).zfill(2)}T{str(9 + i % 6).zfill(2)}:00:00"
            self.sessions.append(session.to_dict())
    
    def test_predict_weekly_productivity(self):
        """Test weekly productivity prediction"""
        prediction = self.predictor.predict_weekly_productivity(self.sessions)
        
        self.assertIn('predicted_productivity', prediction)
        self.assertIn('confidence', prediction)
        self.assertIn('trend', prediction)
        self.assertGreater(prediction['predicted_productivity'], 0)
    
    def test_predict_session_count(self):
        """Test session count prediction"""
        prediction = self.predictor.predict_session_count(self.sessions)
        
        self.assertIn('predicted_sessions', prediction)
        self.assertIn('range', prediction)
        self.assertGreater(prediction['predicted_sessions'], 0)
    
    def test_predict_best_time(self):
        """Test best time prediction"""
        prediction = self.predictor.predict_best_time(self.sessions)
        
        self.assertIn('best_hours', prediction)
        self.assertIn('recommendation', prediction)
        self.assertGreater(len(prediction['best_hours']), 0)
    
    def test_predict_risk_score(self):
        """Test risk prediction"""
        prediction = self.predictor.predict_risk_score(self.sessions)
        
        self.assertIn('risk_score', prediction)
        self.assertIn('risk_level', prediction)
        self.assertIn('recommendation', prediction)
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        prediction = self.predictor.predict_all(self.sessions[:3])
        self.assertIn('error', prediction['productivity'])
    
    def test_predict_all(self):
        """Test all predictions"""
        predictions = self.predictor.predict_all(self.sessions)
        
        self.assertIn('productivity', predictions)
        self.assertIn('session_count', predictions)
        self.assertIn('best_time', predictions)
        self.assertIn('risk', predictions)
    
    def test_predict_optimal_session_length(self):
        """Test optimal session length prediction"""
        prediction = self.predictor.predict_optimal_session_length(self.sessions)
        
        if 'error' not in prediction:
            self.assertIn('optimal_duration', prediction)
            self.assertIn('avg_productivity', prediction)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        self.predictor.clear_cache()
        self.assertEqual(len(self.predictor._cache), 0)


class TestAIRecommender(unittest.TestCase):
    """Test AI Recommender class"""
    
    def setUp(self):
        """Setup before each test"""
        self.recommender = AIRecommender()
        self.sessions = []
        
        for i in range(12):
            distractions = i % 6
            session = StudySession(
                subject=["Python", "Java", "SQL"][i % 3],
                duration=30 + (i * 5),
                distractions=distractions,
                mood=(i % 5) + 1
            )
            session.calculate_productivity()
            session.timestamp = f"2026-01-{str(10 + i).zfill(2)}T{str(8 + i % 10).zfill(2)}:00:00"
            self.sessions.append(session.to_dict())
    
    def test_get_recommendations(self):
        """Test recommendation generation"""
        recommendations = self.recommender.get_recommendations(self.sessions)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        for rec in recommendations:
            self.assertIn('type', rec)
            self.assertIn('title', rec)
            self.assertIn('description', rec)
            self.assertIn('action', rec)
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        recommendations = self.recommender.get_recommendations(self.sessions[:3])
        
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['type'], 'info')
        self.assertIn('Start Tracking', recommendations[0]['title'])
    
    def test_motivational_messages(self):
        """Test motivational messages"""
        messages = self.recommender.get_motivational_messages(self.sessions)
        
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)
        
        for msg in messages:
            self.assertIsInstance(msg, str)
            self.assertGreater(len(msg), 0)
    
    def test_empty_sessions(self):
        """Test with empty sessions"""
        messages = self.recommender.get_motivational_messages([])
        
        self.assertIsInstance(messages, list)
        self.assertEqual(len(messages), 1)
        self.assertIn('Start your learning journey', messages[0])
    
    def test_study_tips(self):
        """Test study tips generation"""
        tips = self.recommender.get_study_tips(self.sessions)
        
        self.assertIsInstance(tips, list)
        self.assertGreater(len(tips), 0)
    
    def test_recommendation_progress(self):
        """Test recommendation progress tracking"""
        progress = self.recommender.get_recommendation_progress(self.sessions)
        
        if 'message' not in progress:
            self.assertIn('distractions', progress)
            self.assertIn('productivity', progress)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        self.recommender.clear_cache()
        self.assertEqual(len(self.recommender._cache), 0)


class TestValidators(unittest.TestCase):
    """Test Validator class"""
    
    def test_validate_subject(self):
        """Test subject validation"""
        self.assertTrue(Validator.validate_subject("Python"))
        self.assertTrue(Validator.validate_subject("Machine Learning"))
        self.assertTrue(Validator.validate_subject("C++ Programming"))
        
        self.assertFalse(Validator.validate_subject(""))
        self.assertFalse(Validator.validate_subject("A"))
        self.assertFalse(Validator.validate_subject("A" * 51))
    
    def test_validate_duration(self):
        """Test duration validation"""
        self.assertTrue(Validator.validate_duration(5))
        self.assertTrue(Validator.validate_duration(30))
        self.assertTrue(Validator.validate_duration(240))
        
        self.assertFalse(Validator.validate_duration(1))
        self.assertFalse(Validator.validate_duration(300))
        self.assertFalse(Validator.validate_duration("abc"))
        self.assertFalse(Validator.validate_duration(None))
    
    def test_validate_distractions(self):
        """Test distraction validation"""
        self.assertTrue(Validator.validate_distractions(0))
        self.assertTrue(Validator.validate_distractions(10))
        self.assertTrue(Validator.validate_distractions(20))
        
        self.assertFalse(Validator.validate_distractions(-1))
        self.assertFalse(Validator.validate_distractions(21))
        self.assertFalse(Validator.validate_distractions("abc"))
    
    def test_validate_mood(self):
        """Test mood validation"""
        self.assertTrue(Validator.validate_mood(None))
        self.assertTrue(Validator.validate_mood(1))
        self.assertTrue(Validator.validate_mood(3))
        self.assertTrue(Validator.validate_mood(5))
        
        self.assertFalse(Validator.validate_mood(0))
        self.assertFalse(Validator.validate_mood(6))
        self.assertFalse(Validator.validate_mood("abc"))
    
    def test_validate_energy(self):
        """Test energy validation"""
        self.assertTrue(Validator.validate_energy(None))
        self.assertTrue(Validator.validate_energy(1))
        self.assertTrue(Validator.validate_energy(3))
        self.assertTrue(Validator.validate_energy(5))
        
        self.assertFalse(Validator.validate_energy(0))
        self.assertFalse(Validator.validate_energy(6))
        self.assertFalse(Validator.validate_energy("abc"))
    
    def test_validate_session_data(self):
        """Test complete session validation"""
        valid_data = {
            'subject': 'Python',
            'duration': 60,
            'distractions': 2,
            'timestamp': '2026-01-15T10:00:00'
        }
        errors = Validator.validate_session_data(valid_data)
        self.assertEqual(errors, [])
        
        invalid_data = {
            'subject': '',
            'duration': 300,
            'distractions': -1
        }
        errors = Validator.validate_session_data(invalid_data)
        self.assertGreater(len(errors), 0)
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        self.assertEqual(Validator.sanitize_string("  Python  "), "Python")
        self.assertEqual(Validator.sanitize_string("<script>"), "script")
        self.assertEqual(Validator.sanitize_string("Test'123"), "Test123")
    
    def test_validate_email(self):
        """Test email validation"""
        self.assertTrue(Validator.validate_email("test@example.com"))
        self.assertTrue(Validator.validate_email("user.name@domain.co"))
        self.assertFalse(Validator.validate_email("invalid"))
        self.assertFalse(Validator.validate_email("test@"))
        self.assertFalse(Validator.validate_email("@domain.com"))
    
    def test_validate_username(self):
        """Test username validation"""
        self.assertTrue(Validator.validate_username("john_doe"))
        self.assertTrue(Validator.validate_username("user123"))
        self.assertFalse(Validator.validate_username(""))
        self.assertFalse(Validator.validate_username("ab"))
        self.assertFalse(Validator.validate_username("user@name"))
    
    def test_validate_password(self):
        """Test password validation"""
        self.assertTrue(Validator.validate_password("Password123"))
        self.assertTrue(Validator.validate_password("SecurePass1"))
        self.assertFalse(Validator.validate_password("pass"))
        self.assertFalse(Validator.validate_password("password"))
        self.assertFalse(Validator.validate_password("PASSWORD123"))


class TestHelpers(unittest.TestCase):
    """Test Helpers class"""
    
    def test_generate_id(self):
        """Test ID generation"""
        id1 = Helpers.generate_id()
        id2 = Helpers.generate_id()
        self.assertNotEqual(id1, id2)
        self.assertEqual(len(id1), 8)
    
    def test_hash_string(self):
        """Test string hashing"""
        hash1 = Helpers.hash_string("test")
        hash2 = Helpers.hash_string("test")
        hash3 = Helpers.hash_string("different")
        
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
    
    def test_get_current_time(self):
        """Test current time"""
        time1 = Helpers.get_current_time()
        time2 = Helpers.get_current_time()
        self.assertIsInstance(time1, str)
        self.assertNotEqual(time1, time2)
    
    def test_format_date(self):
        """Test date formatting"""
        date_str = "2026-01-15T14:30:00"
        formatted = Helpers.format_date(date_str)
        self.assertEqual(formatted, "January 15, 2026")
    
    def test_format_time(self):
        """Test time formatting"""
        date_str = "2026-01-15T14:30:00"
        formatted = Helpers.format_time(date_str)
        self.assertEqual(formatted, "02:30 PM")
    
    def test_days_between(self):
        """Test days between calculation"""
        date1 = "2026-01-01T00:00:00"
        date2 = "2026-01-10T00:00:00"
        days = Helpers.days_between(date1, date2)
        self.assertEqual(days, 9)
    
    def test_format_duration(self):
        """Test duration formatting"""
        self.assertEqual(Helpers.format_duration(30), "30 min")
        self.assertEqual(Helpers.format_duration(60), "1 hour")
        self.assertEqual(Helpers.format_duration(90), "1h 30min")
        self.assertEqual(Helpers.format_duration(120), "2 hours")
    
    def test_truncate_string(self):
        """Test string truncation"""
        text = "This is a very long string that should be truncated"
        truncated = Helpers.truncate_string(text, 20)
        self.assertTrue(len(truncated) <= 23)
        self.assertTrue(truncated.endswith("..."))
    
    def test_calculate_percentage(self):
        """Test percentage calculation"""
        self.assertEqual(Helpers.calculate_percentage(25, 100), 25.0)
        self.assertEqual(Helpers.calculate_percentage(0, 100), 0.0)
        self.assertEqual(Helpers.calculate_percentage(50, 0), 0.0)
    
    def test_list_to_string(self):
        """Test list to string conversion"""
        items = ['a', 'b', 'c']
        result = Helpers.list_to_string(items)
        self.assertEqual(result, "a, b, c")
        
        result = Helpers.list_to_string(items, " | ")
        self.assertEqual(result, "a | b | c")
        
        empty = Helpers.list_to_string([])
        self.assertEqual(empty, "")
    
    def test_round_to_nearest(self):
        """Test rounding to nearest multiple"""
        self.assertEqual(Helpers.round_to_nearest(23, 5), 25)
        self.assertEqual(Helpers.round_to_nearest(22, 5), 20)
        self.assertEqual(Helpers.round_to_nearest(7, 10), 10)
    
    def test_get_week_number(self):
        """Test week number extraction"""
        date_str = "2026-01-15T00:00:00"
        week = Helpers.get_week_number(date_str)
        self.assertIsInstance(week, int)
    
    def test_get_day_name(self):
        """Test day name extraction"""
        date_str = "2026-01-15T00:00:00"
        day = Helpers.get_day_name(date_str)
        self.assertEqual(day, "Thursday")
    
    def test_is_today(self):
        """Test today check"""
        today = datetime.now().isoformat()
        self.assertTrue(Helpers.is_today(today))
        
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        self.assertFalse(Helpers.is_today(yesterday))
    
    def test_safe_json_loads(self):
        """Test safe JSON loading"""
        valid_json = '{"key": "value"}'
        invalid_json = '{invalid}'
        
        result = Helpers.safe_json_loads(valid_json)
        self.assertEqual(result, {"key": "value"})
        
        result = Helpers.safe_json_loads(invalid_json)
        self.assertIsNone(result)
    
    def test_get_file_size(self):
        """Test file size formatting"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello World")
            f.close()
            
            size = Helpers.get_file_size(f.name)
            self.assertIsInstance(size, str)
            self.assertIn("B", size)
            
            os.unlink(f.name)
    
    def test_validate_email(self):
        """Test email validation helper"""
        self.assertTrue(Helpers.validate_email("test@example.com"))
        self.assertTrue(Helpers.validate_email("user.name@domain.co"))
        self.assertFalse(Helpers.validate_email("invalid"))
        self.assertFalse(Helpers.validate_email(""))
    
    def test_format_size(self):
        """Test size formatting"""
        self.assertEqual(Helpers.format_size(500), "500 B")
        self.assertEqual(Helpers.format_size(1024), "1.0 KB")
        self.assertEqual(Helpers.format_size(1024**2), "1.0 MB")
    
    def test_slugify(self):
        """Test slugify"""
        self.assertEqual(Helpers.slugify("Hello World"), "hello-world")
        self.assertEqual(Helpers.slugify("Python 3.9"), "python-3-9")
        self.assertEqual(Helpers.slugify("Test!!"), "test")


class TestRateLimiter(unittest.TestCase):
    """Test RateLimiter class"""
    
    def setUp(self):
        """Setup before each test"""
        self.limiter = RateLimiter(max_calls=3, period=1.0)
    
    def test_rate_limit(self):
        """Test rate limiting"""
        # First 3 calls should pass
        self.assertTrue(self.limiter())
        self.assertTrue(self.limiter())
        self.assertTrue(self.limiter())
        
        # 4th call should fail
        self.assertFalse(self.limiter())
    
    def test_rate_limit_reset(self):
        """Test rate limit reset"""
        for _ in range(3):
            self.limiter()
        
        self.assertFalse(self.limiter())
        
        self.limiter.reset()
        self.assertTrue(self.limiter())
    
    def test_get_remaining(self):
        """Test remaining calls"""
        self.assertEqual(self.limiter.get_remaining(), 3)
        
        self.limiter()
        self.assertEqual(self.limiter.get_remaining(), 2)


def run_all_tests():
    """Run all test suites"""
    import unittest
    
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestJSONStorage)
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIAnalyzer))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIPredictor))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIRecommender))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestValidators))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHelpers))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRateLimiter))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "="*60)
    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failed: {len(result.failures)}")
    print(f"   ⚠️ Errors: {len(result.errors)}")
    print("="*60)
    
    return result


if __name__ == '__main__':
    run_all_tests()