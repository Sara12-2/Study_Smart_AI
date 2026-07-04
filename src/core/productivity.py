"""
Productivity Engine - Advanced Analytics Module
Enterprise-grade productivity calculations with statistical analysis
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, stdev
from enum import Enum
import math
import numpy as np
from functools import lru_cache

logger = logging.getLogger(__name__)


class PerformanceGrade(Enum):
    """Performance grades"""
    A = (90, "🌟 Outstanding performance! Keep it up!")
    B = (80, "👏 Great performance! You're doing well!")
    C = (70, "📈 Good performance! Keep pushing!")
    D = (60, "📊 Average performance. Room for improvement!")
    F = (0, "⚠️ Needs improvement. Let's focus!")

    def __init__(self, threshold: int, message: str):
        self.threshold = threshold
        self.message = message


class ProductivityEngine:
    """
    Advanced productivity analytics engine with caching
    
    Features:
    - Statistical analysis
    - Trend detection
    - Performance metrics
    - Subject-wise analytics
    - Time-based insights
    - Session streaks
    - Performance grading
    - Data export
    """
    
    def __init__(self, storage):
        """
        Initialize productivity engine
        
        Args:
            storage: Storage instance for data access
        """
        self.storage = storage
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = timedelta(minutes=5)
        logger.info("ProductivityEngine initialized")
    
    def _get_cached(self, key: str, func, *args, **kwargs):
        """Get cached data or compute fresh"""
        if key in self._cache:
            if datetime.now() - self._cache_time[key] < self._cache_ttl:
                return self._cache[key]
        
        result = func(*args, **kwargs)
        self._cache[key] = result
        self._cache_time[key] = datetime.now()
        return result
    
    def _validate_sessions(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and filter sessions"""
        return [
            s for s in sessions
            if isinstance(s.get('duration'), (int, float))
            and isinstance(s.get('productivity_score'), (int, float))
            and s.get('timestamp')
        ]
    
    def _get_date_key(self, timestamp: str, period: str = 'day') -> str:
        """Extract date key based on period"""
        date_obj = datetime.fromisoformat(timestamp)
        if period == 'day':
            return date_obj.strftime('%Y-%m-%d')
        elif period == 'week':
            return date_obj.strftime('%Y-W%W')
        elif period == 'month':
            return date_obj.strftime('%Y-%m')
        elif period == 'hour':
            return date_obj.strftime('%Y-%m-%d %H:00')
        return date_obj.strftime('%Y-%m-%d')
    
    def calculate_detailed_stats(self, values: List[float]) -> Dict[str, Any]:
        """Calculate detailed statistics"""
        if not values:
            return {}
        
        return {
            'mean': round(mean(values), 2),
            'median': round(median(values), 2),
            'std': round(stdev(values), 2) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'range': round(max(values) - min(values), 2),
            'q1': round(np.percentile(values, 25), 2) if len(values) > 1 else 0,
            'q3': round(np.percentile(values, 75), 2) if len(values) > 1 else 0,
            'iqr': round(np.percentile(values, 75) - np.percentile(values, 25), 2) if len(values) > 1 else 0,
            'skewness': round(self._calculate_skewness(values), 2),
            'kurtosis': round(self._calculate_kurtosis(values), 2),
            'count': len(values)
        }
    
    def _calculate_skewness(self, values: List[float]) -> float:
        """Calculate skewness of distribution"""
        if len(values) < 3:
            return 0
        n = len(values)
        mean_val = mean(values)
        std_val = stdev(values)
        if std_val == 0:
            return 0
        return (sum((x - mean_val) ** 3 for x in values) / n) / (std_val ** 3)
    
    def _calculate_kurtosis(self, values: List[float]) -> float:
        """Calculate kurtosis of distribution"""
        if len(values) < 4:
            return 0
        n = len(values)
        mean_val = mean(values)
        std_val = stdev(values)
        if std_val == 0:
            return 0
        return (sum((x - mean_val) ** 4 for x in values) / n) / (std_val ** 4) - 3
    
    def get_performance_grade(self, score: float) -> Dict[str, Any]:
        """Get performance grade"""
        if score >= 90:
            return {'grade': 'A', 'message': PerformanceGrade.A.message}
        elif score >= 80:
            return {'grade': 'B', 'message': PerformanceGrade.B.message}
        elif score >= 70:
            return {'grade': 'C', 'message': PerformanceGrade.C.message}
        elif score >= 60:
            return {'grade': 'D', 'message': PerformanceGrade.D.message}
        else:
            return {'grade': 'F', 'message': PerformanceGrade.F.message}
    
    def calculate_streak(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate current study streak
        
        Returns:
            Dictionary with streak information
        """
        if not sessions:
            return {'current_streak': 0, 'best_streak': 0, 'streak_status': '🌱 Starting'}
        
        # Group by date
        dates = set()
        for s in sessions:
            if s.get('timestamp'):
                date = datetime.fromisoformat(s['timestamp']).date()
                dates.add(date)
        
        sorted_dates = sorted(dates)
        
        # Calculate current streak
        current_streak = 0
        best_streak = 0
        streak = 0
        
        for i, date in enumerate(sorted_dates):
            if i == 0:
                streak = 1
            else:
                if (date - sorted_dates[i-1]).days == 1:
                    streak += 1
                else:
                    if streak > best_streak:
                        best_streak = streak
                    streak = 1
        
        if streak > best_streak:
            best_streak = streak
        
        # Check if today has sessions
        today = datetime.now().date()
        if today in dates:
            current_streak = streak
        else:
            yesterday = today - timedelta(days=1)
            if yesterday in dates:
                current_streak = streak
            else:
                current_streak = 0
        
        return {
            'current_streak': current_streak,
            'best_streak': best_streak,
            'total_days': len(dates),
            'streak_status': '🔥 On fire!' if current_streak >= 5 else '💪 Building' if current_streak >= 2 else '🌱 Starting'
        }
    
    def calculate_daily_summary(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Calculate comprehensive daily summary"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cache_key = f"daily_summary_{date}"
        return self._get_cached(cache_key, self._calculate_daily_summary, date)
    
    def _calculate_daily_summary(self, date: str) -> Optional[Dict[str, Any]]:
        """Internal method to calculate daily summary"""
        sessions = self.storage.get_sessions_by_date(date)
        sessions = self._validate_sessions(sessions)
        
        if not sessions:
            return None
        
        total_time = sum(s['duration'] for s in sessions)
        total_distractions = sum(s.get('distractions', 0) for s in sessions)
        avg_productivity = mean(s['productivity_score'] for s in sessions)
        
        # Subject distribution
        subjects = defaultdict(int)
        subject_productivity = defaultdict(list)
        for s in sessions:
            subjects[s.get('subject', 'Unknown')] += s['duration']
            subject_productivity[s.get('subject', 'Unknown')].append(s['productivity_score'])
        
        best_subject = max(subject_productivity.items(), key=lambda x: mean(x[1])) if subject_productivity else None
        worst_subject = min(subject_productivity.items(), key=lambda x: mean(x[1])) if subject_productivity else None
        
        # Session timing analysis
        hour_distribution = defaultdict(int)
        for s in sessions:
            hour = datetime.fromisoformat(s['timestamp']).hour
            hour_distribution[hour] += 1
        
        peak_hour = max(hour_distribution.items(), key=lambda x: x[1]) if hour_distribution else None
        
        # Calculate consistency score
        if len(sessions) > 1:
            productivity_values = [s['productivity_score'] for s in sessions]
            consistency = 100 - (stdev(productivity_values) / 100 * 100)
            consistency = max(0, min(100, consistency))
        else:
            consistency = 100
        
        # Get grade
        grade = self.get_performance_grade(avg_productivity)
        
        return {
            'date': date,
            'total_sessions': len(sessions),
            'total_time': total_time,
            'avg_productivity': round(avg_productivity, 2),
            'total_distractions': total_distractions,
            'subjects': dict(subjects),
            'best_subject': {
                'name': best_subject[0] if best_subject else None,
                'score': round(mean(best_subject[1]), 2) if best_subject else None
            },
            'worst_subject': {
                'name': worst_subject[0] if worst_subject else None,
                'score': round(mean(worst_subject[1]), 2) if worst_subject else None
            },
            'peak_hour': peak_hour[0] if peak_hour else None,
            'consistency_score': round(consistency, 2),
            'avg_session_time': round(total_time / len(sessions), 2),
            'productivity_trend': self._calculate_trend([s['productivity_score'] for s in sessions]),
            'score': self._calculate_productivity_score(sessions),
            'grade': grade,
            'streak': self.calculate_streak(sessions)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'neutral'
        
        first_half = mean(values[:len(values)//2])
        second_half = mean(values[len(values)//2:])
        
        if second_half > first_half * 1.05:
            return 'improving'
        elif second_half < first_half * 0.95:
            return 'declining'
        return 'stable'
    
    def _calculate_productivity_score(self, sessions: List[Dict[str, Any]]) -> int:
        """Calculate overall productivity score"""
        if not sessions:
            return 0
        
        avg_score = mean(s['productivity_score'] for s in sessions)
        consistency = min(100, max(0, len(sessions) / 10 * 10))
        
        # Weighted scoring
        score = (avg_score * 0.7) + (consistency * 0.3)
        return round(score)
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate comprehensive weekly report"""
        cache_key = "weekly_report"
        return self._get_cached(cache_key, self._generate_weekly_report)
    
    def _generate_weekly_report(self) -> Dict[str, Any]:
        """Internal method to generate weekly report"""
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found', 'total_sessions': 0}
        
        # Group by week
        weekly_data = defaultdict(list)
        for s in sessions:
            week_key = self._get_date_key(s['timestamp'], 'week')
            weekly_data[week_key].append(s)
        
        current_week = datetime.now().strftime('%Y-W%W')
        current_week_sessions = weekly_data.get(current_week, [])
        
        reports = []
        for week, week_sessions in weekly_data.items():
            total_time = sum(s['duration'] for s in week_sessions)
            avg_productivity = mean(s['productivity_score'] for s in week_sessions)
            
            reports.append({
                'week': week,
                'total_sessions': len(week_sessions),
                'total_time': total_time,
                'avg_productivity': round(avg_productivity, 2),
                'sessions': week_sessions,
                'grade': self.get_performance_grade(avg_productivity)
            })
        
        reports = sorted(reports, key=lambda x: x['week'])
        
        if len(reports) >= 2:
            trend = self._calculate_trend([r['avg_productivity'] for r in reports])
        else:
            trend = 'neutral'
        
        best_week = max(reports, key=lambda x: x['avg_productivity']) if reports else None
        worst_week = min(reports, key=lambda x: x['avg_productivity']) if reports else None
        
        return {
            'total_weeks': len(reports),
            'current_week': current_week,
            'current_week_sessions': len(current_week_sessions),
            'current_week_time': sum(s['duration'] for s in current_week_sessions),
            'current_week_productivity': round(mean([s['productivity_score'] for s in current_week_sessions]), 2) if current_week_sessions else 0,
            'trend': trend,
            'best_week': {
                'week': best_week['week'] if best_week else None,
                'score': best_week['avg_productivity'] if best_week else None
            },
            'worst_week': {
                'week': worst_week['week'] if worst_week else None,
                'score': worst_week['avg_productivity'] if worst_week else None
            },
            'weekly_reports': reports,
            'total_sessions': len(sessions),
            'total_time': sum(s['duration'] for s in sessions),
            'overall_productivity': round(mean([s['productivity_score'] for s in sessions]), 2),
            'overall_grade': self.get_performance_grade(mean([s['productivity_score'] for s in sessions]))
        }
    
    def analyze_subject_performance(self) -> Dict[str, Any]:
        """Analyze performance by subject"""
        cache_key = "subject_performance"
        return self._get_cached(cache_key, self._analyze_subject_performance)
    
    def _analyze_subject_performance(self) -> Dict[str, Any]:
        """Internal method to analyze subject performance"""
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        subject_data = defaultdict(lambda: {
            'sessions': 0,
            'total_time': 0,
            'productivity_scores': [],
            'distractions': []
        })
        
        for s in sessions:
            subject = s.get('subject', 'Unknown')
            subject_data[subject]['sessions'] += 1
            subject_data[subject]['total_time'] += s['duration']
            subject_data[subject]['productivity_scores'].append(s['productivity_score'])
            subject_data[subject]['distractions'].append(s.get('distractions', 0))
        
        subject_metrics = {}
        for subject, data in subject_data.items():
            subject_metrics[subject] = {
                'sessions': data['sessions'],
                'total_time': data['total_time'],
                'avg_productivity': round(mean(data['productivity_scores']), 2),
                'max_productivity': max(data['productivity_scores']),
                'min_productivity': min(data['productivity_scores']),
                'avg_distractions': round(mean(data['distractions']), 2),
                'total_distractions': sum(data['distractions']),
                'grade': self.get_performance_grade(mean(data['productivity_scores']))
            }
        
        sorted_subjects = sorted(
            subject_metrics.items(),
            key=lambda x: x[1]['avg_productivity'],
            reverse=True
        )
        
        return {
            'subjects': sorted_subjects,
            'best_subject': sorted_subjects[0] if sorted_subjects else None,
            'worst_subject': sorted_subjects[-1] if sorted_subjects else None,
            'total_subjects': len(subject_metrics)
        }
    
    def get_productivity_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get productivity trends for the last N days"""
        cache_key = f"trends_{days}"
        return self._get_cached(cache_key, self._get_productivity_trends, days)
    
    def _get_productivity_trends(self, days: int) -> Dict[str, Any]:
        """Internal method to get productivity trends"""
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_sessions = [
            s for s in sessions
            if datetime.fromisoformat(s['timestamp']) >= cutoff_date
        ]
        
        if not filtered_sessions:
            return {'error': 'No sessions in range', 'total_sessions': 0}
        
        daily_data = defaultdict(list)
        for s in filtered_sessions:
            day = self._get_date_key(s['timestamp'], 'day')
            daily_data[day].append(s['productivity_score'])
        
        daily_averages = {
            day: round(mean(scores), 2)
            for day, scores in sorted(daily_data.items())
        }
        
        days_list = list(range(len(daily_averages)))
        values = list(daily_averages.values())
        
        if len(days_list) > 1:
            n = len(days_list)
            sum_x = sum(days_list)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(days_list, values))
            sum_x2 = sum(x ** 2 for x in days_list)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
            
            trend_direction = 'improving' if slope > 0.5 else 'declining' if slope < -0.5 else 'stable'
            slope_percentage = round(slope * 100 / (max(values) if max(values) > 0 else 1), 2)
        else:
            trend_direction = 'insufficient_data'
            slope_percentage = 0
        
        return {
            'days_analyzed': len(daily_averages),
            'total_sessions': len(filtered_sessions),
            'daily_productivity': daily_averages,
            'trend_direction': trend_direction,
            'trend_slope': slope_percentage,
            'avg_productivity': round(mean(values), 2) if values else 0,
            'max_productivity': max(values) if values else 0,
            'min_productivity': min(values) if values else 0,
            'consistency': round(100 - (stdev(values) / 100 * 100), 2) if len(values) > 1 else 100,
            'stats': self.calculate_detailed_stats(values)
        }
    
    def get_optimal_study_times(self) -> Dict[str, Any]:
        """Find optimal study times based on historical data"""
        cache_key = "optimal_times"
        return self._get_cached(cache_key, self._get_optimal_study_times)
    
    def _get_optimal_study_times(self) -> Dict[str, Any]:
        """Internal method to find optimal study times"""
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found', 'total_sessions': 0}
        
        hour_data = defaultdict(list)
        for s in sessions:
            hour = datetime.fromisoformat(s['timestamp']).hour
            hour_data[hour].append({
                'productivity': s['productivity_score'],
                'duration': s['duration'],
                'subject': s.get('subject', 'Unknown')
            })
        
        hour_metrics = {}
        for hour, data in hour_data.items():
            avg_productivity = mean(d['productivity'] for d in data)
            avg_duration = mean(d['duration'] for d in data)
            total_sessions = len(data)
            
            hour_metrics[hour] = {
                'avg_productivity': round(avg_productivity, 2),
                'avg_duration': round(avg_duration, 2),
                'total_sessions': total_sessions,
                'score': round((avg_productivity * 0.6) + (min(100, total_sessions * 10) * 0.4), 2),
                'grade': self.get_performance_grade(avg_productivity)
            }
        
        sorted_hours = sorted(
            hour_metrics.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        peak_periods = []
        current_period = []
        
        for hour, metrics in sorted_hours[:6]:
            if not current_period or hour == current_period[-1][0] + 1:
                current_period.append((hour, metrics))
            else:
                if current_period:
                    peak_periods.append(current_period)
                current_period = [(hour, metrics)]
        
        if current_period:
            peak_periods.append(current_period)
        
        formatted_periods = []
        for period in peak_periods:
            if len(period) > 1:
                start_hour = period[0][0]
                end_hour = period[-1][0]
                avg_score = mean(m[1]['score'] for _, m in period)
                formatted_periods.append({
                    'time_range': f"{start_hour:02d}:00 - {end_hour + 1:02d}:00",
                    'hours': [h for h, _ in period],
                    'avg_score': round(avg_score, 2)
                })
        
        return {
            'optimal_hours': sorted_hours[:5],
            'peak_periods': formatted_periods,
            'best_hour': sorted_hours[0][0] if sorted_hours else None,
            'best_hour_productivity': sorted_hours[0][1]['avg_productivity'] if sorted_hours else 0,
            'best_hour_grade': sorted_hours[0][1]['grade'] if sorted_hours else None,
            'recommendation': self._generate_recommendation(sorted_hours)
        }
    
    def _generate_recommendation(self, sorted_hours: List[Tuple[int, Dict]]) -> str:
        """Generate human-readable recommendation"""
        if not sorted_hours:
            return "No data available for recommendations. Start tracking your sessions!"
        
        best_hour = sorted_hours[0][0]
        best_score = sorted_hours[0][1]['avg_productivity']
        
        if best_hour < 12:
            time_period = "morning"
        elif best_hour < 17:
            time_period = "afternoon"
        elif best_hour < 21:
            time_period = "evening"
        else:
            time_period = "night"
        
        return f"Your peak productivity time is {best_hour:02d}:00 ({time_period}) with {best_score}% average productivity. Schedule your most important tasks during this time for optimal results!"
    
    def export_to_csv(self, sessions: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export sessions to CSV
        
        Args:
            sessions: List of session dictionaries
            filename: Optional filename
            
        Returns:
            Path to exported file
        """
        import csv
        import os
        
        if not sessions:
            raise ValueError("No sessions to export")
        
        if filename is None:
            filename = f"study_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        os.makedirs('exports', exist_ok=True)
        filepath = os.path.join('exports', filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sessions[0].keys())
            writer.writeheader()
            writer.writerows(sessions)
        
        logger.info(f"Exported {len(sessions)} sessions to {filepath}")
        return filepath
    
    def compare_periods(self, period1: str, period2: str, period_type: str = 'week') -> Dict[str, Any]:
        """
        Compare two time periods
        
        Args:
            period1: First period (YYYY-MM-DD or YYYY-WW)
            period2: Second period (YYYY-MM-DD or YYYY-WW)
            period_type: 'day' or 'week'
            
        Returns:
            Comparison results
        """
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        p1_sessions = [s for s in sessions if self._get_date_key(s['timestamp'], period_type) == period1]
        p2_sessions = [s for s in sessions if self._get_date_key(s['timestamp'], period_type) == period2]
        
        p1_avg = mean([s['productivity_score'] for s in p1_sessions]) if p1_sessions else 0
        p2_avg = mean([s['productivity_score'] for s in p2_sessions]) if p2_sessions else 0
        
        improvement = ((p2_avg - p1_avg) / p1_avg * 100) if p1_avg > 0 else 0
        
        return {
            'period1': {
                'label': period1,
                'avg_productivity': round(p1_avg, 2),
                'sessions': len(p1_sessions),
                'total_time': sum(s['duration'] for s in p1_sessions)
            },
            'period2': {
                'label': period2,
                'avg_productivity': round(p2_avg, 2),
                'sessions': len(p2_sessions),
                'total_time': sum(s['duration'] for s in p2_sessions)
            },
            'improvement': round(improvement, 2),
            'improvement_text': '📈 Improved' if improvement > 0 else '📉 Declined' if improvement < 0 else '➡️ Stable',
            'grade1': self.get_performance_grade(p1_avg),
            'grade2': self.get_performance_grade(p2_avg)
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_time.clear()
        logger.info("Cache cleared")