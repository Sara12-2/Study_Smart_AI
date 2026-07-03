"""
Productivity Engine - Advanced Analytics Module
Enterprise-grade productivity calculations with statistical analysis
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, stdev
import math

logger = logging.getLogger(__name__)


class ProductivityEngine:
    """
    Advanced productivity analytics engine
    
    Features:
    - Statistical analysis
    - Trend detection
    - Performance metrics
    - Subject-wise analytics
    - Time-based insights
    """
    
    def __init__(self, storage):
        """
        Initialize productivity engine
        
        Args:
            storage: Storage instance for data access
        """
        self.storage = storage
        logger.info("ProductivityEngine initialized")
    
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
    
    def calculate_daily_summary(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Calculate comprehensive daily summary
        
        Args:
            date: Date string (YYYY-MM-DD) or None for today
            
        Returns:
            Dictionary with daily metrics or None
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
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
        
        # Find peak productivity hour
        peak_hour = max(hour_distribution.items(), key=lambda x: x[1]) if hour_distribution else None
        
        # Calculate consistency score
        if len(sessions) > 1:
            productivity_values = [s['productivity_score'] for s in sessions]
            consistency = 100 - (stdev(productivity_values) / 100 * 100)
            consistency = max(0, min(100, consistency))
        else:
            consistency = 100
        
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
            'score': self._calculate_productivity_score(sessions)
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
        """
        Generate comprehensive weekly report
        
        Returns:
            Dictionary with weekly metrics and insights
        """
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found', 'total_sessions': 0}
        
        # Group by week
        weekly_data = defaultdict(list)
        for s in sessions:
            week_key = self._get_date_key(s['timestamp'], 'week')
            weekly_data[week_key].append(s)
        
        # Get current week
        current_week = datetime.now().strftime('%Y-W%W')
        current_week_sessions = weekly_data.get(current_week, [])
        
        # Calculate weekly metrics
        reports = []
        for week, week_sessions in weekly_data.items():
            total_time = sum(s['duration'] for s in week_sessions)
            avg_productivity = mean(s['productivity_score'] for s in week_sessions)
            
            reports.append({
                'week': week,
                'total_sessions': len(week_sessions),
                'total_time': total_time,
                'avg_productivity': round(avg_productivity, 2),
                'sessions': week_sessions
            })
        
        # Sort by week
        reports = sorted(reports, key=lambda x: x['week'])
        
        # Analyze trends
        if len(reports) >= 2:
            trend = self._calculate_trend([r['avg_productivity'] for r in reports])
        else:
            trend = 'neutral'
        
        # Find best week
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
            'overall_productivity': round(mean([s['productivity_score'] for s in sessions]), 2)
        }
    
    def analyze_subject_performance(self) -> Dict[str, Any]:
        """
        Analyze performance by subject
        
        Returns:
            Dictionary with subject-wise analysis
        """
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
        
        # Calculate metrics for each subject
        subject_metrics = {}
        for subject, data in subject_data.items():
            subject_metrics[subject] = {
                'sessions': data['sessions'],
                'total_time': data['total_time'],
                'avg_productivity': round(mean(data['productivity_scores']), 2),
                'max_productivity': max(data['productivity_scores']),
                'min_productivity': min(data['productivity_scores']),
                'avg_distractions': round(mean(data['distractions']), 2),
                'total_distractions': sum(data['distractions'])
            }
        
        # Sort by productivity
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
        """
        Get productivity trends for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        # Filter for last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_sessions = [
            s for s in sessions
            if datetime.fromisoformat(s['timestamp']) >= cutoff_date
        ]
        
        if not filtered_sessions:
            return {'error': 'No sessions in range', 'total_sessions': 0}
        
        # Daily averages
        daily_data = defaultdict(list)
        for s in filtered_sessions:
            day = self._get_date_key(s['timestamp'], 'day')
            daily_data[day].append(s['productivity_score'])
        
        daily_averages = {
            day: round(mean(scores), 2)
            for day, scores in sorted(daily_data.items())
        }
        
        # Calculate trend line
        days_list = list(range(len(daily_averages)))
        values = list(daily_averages.values())
        
        if len(days_list) > 1:
            # Simple linear regression
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
            'consistency': round(100 - (stdev(values) / 100 * 100), 2) if len(values) > 1 else 100
        }
    
    def get_optimal_study_times(self) -> Dict[str, Any]:
        """
        Find optimal study times based on historical data
        
        Returns:
            Dictionary with optimal time recommendations
        """
        sessions = self.storage.load_all_sessions()
        sessions = self._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found', 'total_sessions': 0}
        
        # Group by hour
        hour_data = defaultdict(list)
        for s in sessions:
            hour = datetime.fromisoformat(s['timestamp']).hour
            hour_data[hour].append({
                'productivity': s['productivity_score'],
                'duration': s['duration'],
                'subject': s.get('subject', 'Unknown')
            })
        
        # Calculate metrics per hour
        hour_metrics = {}
        for hour, data in hour_data.items():
            avg_productivity = mean(d['productivity'] for d in data)
            avg_duration = mean(d['duration'] for d in data)
            total_sessions = len(data)
            
            hour_metrics[hour] = {
                'avg_productivity': round(avg_productivity, 2),
                'avg_duration': round(avg_duration, 2),
                'total_sessions': total_sessions,
                'score': round((avg_productivity * 0.6) + (min(100, total_sessions * 10) * 0.4), 2)
            }
        
        # Find best hours
        sorted_hours = sorted(
            hour_metrics.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Identify peak periods (group consecutive hours)
        peak_periods = []
        current_period = []
        
        for hour, metrics in sorted_hours[:6]:  # Top 6 hours
            if not current_period or hour == current_period[-1][0] + 1:
                current_period.append((hour, metrics))
            else:
                if current_period:
                    peak_periods.append(current_period)
                current_period = [(hour, metrics)]
        
        if current_period:
            peak_periods.append(current_period)
        
        # Format peak periods
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
            'recommendation': self._generate_recommendation(sorted_hours)
        }
    
    def _generate_recommendation(self, sorted_hours: List[Tuple[int, Dict]]) -> str:
        """Generate human-readable recommendation"""
        if not sorted_hours:
            return "No data available for recommendations. Start tracking your sessions!"
        
        best_hour = sorted_hours[0][0]
        best_score = sorted_hours[0][1]['avg_productivity']
        
        # Time formatting
        if best_hour < 12:
            time_period = "morning"
        elif best_hour < 17:
            time_period = "afternoon"
        elif best_hour < 21:
            time_period = "evening"
        else:
            time_period = "night"
        
        return f"Your peak productivity time is {best_hour:02d}:00 ({time_period}) with {best_score}% average productivity. Schedule your most important tasks during this time for optimal results!"