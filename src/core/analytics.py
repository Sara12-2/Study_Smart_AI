"""
Analytics Module - Advanced Analytics & Reporting
Extended analytics capabilities for the productivity engine
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, stdev
import json
import os

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Advanced analytics engine for study data
    
    Features:
    - Advanced statistical analysis
    - Data visualization preparation
    - Report generation
    - Data export (JSON, CSV)
    - Insight generation
    - Performance benchmarking
    """
    
    def __init__(self, storage, productivity_engine):
        """
        Initialize analytics engine
        
        Args:
            storage: Storage instance for data access
            productivity_engine: ProductivityEngine instance
        """
        self.storage = storage
        self.engine = productivity_engine
        logger.info("AnalyticsEngine initialized")
    
    # ==========================================
    # ADVANCED STATISTICAL ANALYSIS
    # ==========================================
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics including advanced metrics
        
        Returns:
            Dictionary with comprehensive stats
        """
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        # Basic stats
        total_sessions = len(sessions)
        total_time = sum(s['duration'] for s in sessions)
        total_distractions = sum(s.get('distractions', 0) for s in sessions)
        
        # Productivity stats
        productivity_scores = [s['productivity_score'] for s in sessions]
        
        # Distribution analysis
        distribution = {
            'high': len([s for s in productivity_scores if s >= 80]),
            'medium': len([s for s in productivity_scores if 50 <= s < 80]),
            'low': len([s for s in productivity_scores if s < 50])
        }
        
        # Time analysis
        time_analysis = self._analyze_time_distribution(sessions)
        
        # Subject analysis
        subject_analysis = self._analyze_subject_distribution(sessions)
        
        # Trend analysis
        trend_analysis = self._analyze_trends(sessions)
        
        return {
            'overview': {
                'total_sessions': total_sessions,
                'total_time': total_time,
                'total_distractions': total_distractions,
                'avg_time_per_session': round(total_time / total_sessions, 2) if total_sessions > 0 else 0,
                'avg_distractions_per_session': round(total_distractions / total_sessions, 2) if total_sessions > 0 else 0
            },
            'productivity': {
                'mean': round(mean(productivity_scores), 2),
                'median': round(median(productivity_scores), 2),
                'std': round(stdev(productivity_scores), 2) if len(productivity_scores) > 1 else 0,
                'min': min(productivity_scores),
                'max': max(productivity_scores),
                'distribution': distribution
            },
            'time_distribution': time_analysis,
            'subject_distribution': subject_analysis,
            'trends': trend_analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_time_distribution(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze time distribution of sessions"""
        if not sessions:
            return {}
        
        # Hour distribution
        hour_distribution = defaultdict(int)
        for s in sessions:
            hour = datetime.fromisoformat(s['timestamp']).hour
            hour_distribution[hour] += 1
        
        # Day of week distribution
        day_distribution = defaultdict(int)
        for s in sessions:
            day = datetime.fromisoformat(s['timestamp']).weekday()
            day_distribution[day] += 1
        
        # Month distribution
        month_distribution = defaultdict(int)
        for s in sessions:
            month = datetime.fromisoformat(s['timestamp']).month
            month_distribution[month] += 1
        
        return {
            'hourly': dict(sorted(hour_distribution.items())),
            'daily': dict(sorted(day_distribution.items())),
            'monthly': dict(sorted(month_distribution.items())),
            'peak_hour': max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else None,
            'peak_day': max(day_distribution.items(), key=lambda x: x[1])[0] if day_distribution else None
        }
    
    def _analyze_subject_distribution(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze subject distribution"""
        if not sessions:
            return {}
        
        subject_data = defaultdict(lambda: {
            'sessions': 0,
            'time': 0,
            'productivity': [],
            'distractions': []
        })
        
        for s in sessions:
            subject = s.get('subject', 'Unknown')
            subject_data[subject]['sessions'] += 1
            subject_data[subject]['time'] += s['duration']
            subject_data[subject]['productivity'].append(s['productivity_score'])
            subject_data[subject]['distractions'].append(s.get('distractions', 0))
        
        # Calculate metrics
        metrics = {}
        for subject, data in subject_data.items():
            metrics[subject] = {
                'sessions': data['sessions'],
                'time': data['time'],
                'avg_time': round(data['time'] / data['sessions'], 2),
                'avg_productivity': round(mean(data['productivity']), 2),
                'max_productivity': max(data['productivity']),
                'min_productivity': min(data['productivity']),
                'avg_distractions': round(mean(data['distractions']), 2),
                'consistency': round(self._calculate_consistency(data['productivity']), 2)
            }
        
        return metrics
    
    def _analyze_trends(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends over time"""
        if len(sessions) < 3:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Sort by timestamp
        sorted_sessions = sorted(sessions, key=lambda x: x['timestamp'])
        
        # Weekly trends
        weekly_data = defaultdict(list)
        for s in sorted_sessions:
            week = datetime.fromisoformat(s['timestamp']).isocalendar()[1]
            weekly_data[week].append(s['productivity_score'])
        
        weekly_avg = {
            week: round(mean(scores), 2)
            for week, scores in weekly_data.items()
        }
        
        # Monthly trends
        monthly_data = defaultdict(list)
        for s in sorted_sessions:
            month = datetime.fromisoformat(s['timestamp']).strftime('%Y-%m')
            monthly_data[month].append(s['productivity_score'])
        
        monthly_avg = {
            month: round(mean(scores), 2)
            for month, scores in monthly_data.items()
        }
        
        # Overall trend
        values = [s['productivity_score'] for s in sorted_sessions]
        
        return {
            'weekly': dict(sorted(weekly_avg.items())),
            'monthly': dict(sorted(monthly_avg.items())),
            'overall_trend': self.engine._calculate_trend(values),
            'sessions_count': len(sorted_sessions),
            'time_span': {
                'first': sorted_sessions[0]['timestamp'],
                'last': sorted_sessions[-1]['timestamp'],
                'days': (datetime.fromisoformat(sorted_sessions[-1]['timestamp']) - 
                        datetime.fromisoformat(sorted_sessions[0]['timestamp'])).days + 1
            }
        }
    
    def _calculate_consistency(self, values: List[float]) -> float:
        """Calculate consistency score (0-100)"""
        if len(values) < 2:
            return 100
        
        std = stdev(values)
        mean_val = mean(values)
        
        if mean_val == 0:
            return 0
        
        # Coefficient of variation (lower = more consistent)
        cv = (std / mean_val) * 100
        consistency = max(0, 100 - cv)
        return min(100, consistency)
    
    # ==========================================
    # VISUALIZATION DATA PREPARATION
    # ==========================================
    
    def prepare_chart_data(self, chart_type: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Prepare data for charts
        
        Args:
            chart_type: Type of chart ('daily', 'weekly', 'subject', 'trend')
            params: Additional parameters
            
        Returns:
            Dictionary with chart-ready data
        """
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        if chart_type == 'daily':
            return self._prepare_daily_chart_data(sessions)
        elif chart_type == 'weekly':
            return self._prepare_weekly_chart_data(sessions)
        elif chart_type == 'subject':
            return self._prepare_subject_chart_data(sessions)
        elif chart_type == 'trend':
            return self._prepare_trend_chart_data(sessions)
        elif chart_type == 'distribution':
            return self._prepare_distribution_chart_data(sessions)
        else:
            return {'error': f'Unknown chart type: {chart_type}'}
    
    def _prepare_daily_chart_data(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for daily chart"""
        # Get last 30 days
        days = 30
        cutoff = datetime.now() - timedelta(days=days)
        
        # Initialize with all days
        daily_data = {}
        for i in range(days):
            date = (cutoff + timedelta(days=i)).strftime('%Y-%m-%d')
            daily_data[date] = {'sessions': 0, 'productivity': 0, 'time': 0}
        
        # Fill with actual data
        for s in sessions:
            date = datetime.fromisoformat(s['timestamp']).strftime('%Y-%m-%d')
            if date in daily_data:
                daily_data[date]['sessions'] += 1
                daily_data[date]['productivity'] += s['productivity_score']
                daily_data[date]['time'] += s['duration']
        
        # Calculate averages
        for date, data in daily_data.items():
            if data['sessions'] > 0:
                data['avg_productivity'] = round(data['productivity'] / data['sessions'], 2)
            else:
                data['avg_productivity'] = 0
        
        return {
            'labels': list(daily_data.keys()),
            'datasets': {
                'sessions': [data['sessions'] for data in daily_data.values()],
                'productivity': [data['avg_productivity'] for data in daily_data.values()],
                'time': [data['time'] for data in daily_data.values()]
            }
        }
    
    def _prepare_weekly_chart_data(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for weekly chart"""
        weekly_data = defaultdict(lambda: {'sessions': 0, 'productivity': [], 'time': 0})
        
        for s in sessions:
            week = datetime.fromisoformat(s['timestamp']).isocalendar()[1]
            year = datetime.fromisoformat(s['timestamp']).year
            key = f"{year}-W{week:02d}"
            
            weekly_data[key]['sessions'] += 1
            weekly_data[key]['productivity'].append(s['productivity_score'])
            weekly_data[key]['time'] += s['duration']
        
        # Calculate averages
        labels = sorted(weekly_data.keys())
        datasets = {
            'sessions': [],
            'productivity': [],
            'time': []
        }
        
        for label in labels:
            data = weekly_data[label]
            datasets['sessions'].append(data['sessions'])
            datasets['productivity'].append(
                round(mean(data['productivity']), 2) if data['productivity'] else 0
            )
            datasets['time'].append(data['time'])
        
        return {
            'labels': labels,
            'datasets': datasets
        }
    
    def _prepare_subject_chart_data(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for subject chart"""
        subject_data = defaultdict(lambda: {'sessions': 0, 'productivity': [], 'time': 0})
        
        for s in sessions:
            subject = s.get('subject', 'Unknown')
            subject_data[subject]['sessions'] += 1
            subject_data[subject]['productivity'].append(s['productivity_score'])
            subject_data[subject]['time'] += s['duration']
        
        labels = []
        datasets = {
            'sessions': [],
            'productivity': [],
            'time': []
        }
        
        for subject, data in sorted(subject_data.items(), key=lambda x: -x[1]['sessions']):
            labels.append(subject)
            datasets['sessions'].append(data['sessions'])
            datasets['productivity'].append(
                round(mean(data['productivity']), 2) if data['productivity'] else 0
            )
            datasets['time'].append(data['time'])
        
        return {
            'labels': labels,
            'datasets': datasets
        }
    
    def _prepare_trend_chart_data(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for trend chart"""
        sorted_sessions = sorted(sessions, key=lambda x: x['timestamp'])
        
        return {
            'labels': [s['timestamp'][:10] for s in sorted_sessions],
            'datasets': {
                'productivity': [s['productivity_score'] for s in sorted_sessions],
                'duration': [s['duration'] for s in sorted_sessions],
                'distractions': [s.get('distractions', 0) for s in sorted_sessions]
            }
        }
    
    def _prepare_distribution_chart_data(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for distribution chart"""
        # Productivity distribution
        productivity_scores = [s['productivity_score'] for s in sessions]
        
        # Create bins
        bins = [0, 20, 40, 60, 80, 100]
        labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
        distribution = [0] * len(labels)
        
        for score in productivity_scores:
            for i, (low, high) in enumerate(zip(bins[:-1], bins[1:])):
                if low <= score < high:
                    distribution[i] += 1
                    break
            if score == 100:
                distribution[-1] += 1
        
        # Duration distribution
        durations = [s['duration'] for s in sessions]
        duration_bins = [0, 15, 30, 45, 60, 120, 240]
        duration_labels = ['0-15', '16-30', '31-45', '46-60', '61-120', '121-240']
        duration_dist = [0] * len(duration_labels)
        
        for duration in durations:
            for i, (low, high) in enumerate(zip(duration_bins[:-1], duration_bins[1:])):
                if low <= duration < high:
                    duration_dist[i] += 1
                    break
            if duration >= 240:
                duration_dist[-1] += 1
        
        return {
            'productivity': {
                'labels': labels,
                'values': distribution
            },
            'duration': {
                'labels': duration_labels,
                'values': duration_dist
            }
        }
    
    # ==========================================
    # REPORT GENERATION
    # ==========================================
    
    def generate_report(self, report_type: str = 'summary') -> Dict[str, Any]:
        """
        Generate a comprehensive report
        
        Args:
            report_type: Type of report ('summary', 'detailed', 'weekly', 'monthly')
            
        Returns:
            Dictionary with report data
        """
        if report_type == 'summary':
            return self._generate_summary_report()
        elif report_type == 'detailed':
            return self._generate_detailed_report()
        elif report_type == 'weekly':
            return self._generate_weekly_report_data()
        elif report_type == 'monthly':
            return self._generate_monthly_report_data()
        else:
            return {'error': f'Unknown report type: {report_type}'}
    
    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary report"""
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        # Basic metrics
        total_sessions = len(sessions)
        total_time = sum(s['duration'] for s in sessions)
        avg_productivity = mean(s['productivity_score'] for s in sessions)
        
        # Subject count
        subjects = len(set(s.get('subject', 'Unknown') for s in sessions))
        
        # Time span
        sorted_sessions = sorted(sessions, key=lambda x: x['timestamp'])
        first_date = sorted_sessions[0]['timestamp'][:10]
        last_date = sorted_sessions[-1]['timestamp'][:10]
        
        return {
            'title': 'Study Summary Report',
            'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_sessions': total_sessions,
                'total_hours': round(total_time / 60, 2),
                'avg_productivity': round(avg_productivity, 2),
                'total_subjects': subjects,
                'time_span': f"{first_date} to {last_date}",
                'avg_sessions_per_day': round(total_sessions / max(1, (datetime.now() - datetime.fromisoformat(sorted_sessions[0]['timestamp'])).days + 1), 2)
            }
        }
    
    def _generate_detailed_report(self) -> Dict[str, Any]:
        """Generate detailed report"""
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        # Get all metrics
        stats = self.get_comprehensive_stats()
        subject_analysis = self.engine.analyze_subject_performance()
        weekly_report = self.engine.generate_weekly_report()
        
        return {
            'title': 'Detailed Study Report',
            'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': stats,
            'subjects': subject_analysis,
            'weekly': weekly_report,
            'optimal_times': self.engine.get_optimal_study_times(),
            'all_sessions': sessions[-20:]  # Last 20 sessions
        }
    
    def _generate_weekly_report_data(self) -> Dict[str, Any]:
        """Generate weekly report data"""
        return self.engine.generate_weekly_report()
    
    def _generate_monthly_report_data(self) -> Dict[str, Any]:
        """Generate monthly report data"""
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        # Group by month
        monthly_data = defaultdict(lambda: {'sessions': 0, 'time': 0, 'productivity': [], 'distractions': []})
        
        for s in sessions:
            month = datetime.fromisoformat(s['timestamp']).strftime('%Y-%m')
            monthly_data[month]['sessions'] += 1
            monthly_data[month]['time'] += s['duration']
            monthly_data[month]['productivity'].append(s['productivity_score'])
            monthly_data[month]['distractions'].append(s.get('distractions', 0))
        
        # Calculate averages
        months = sorted(monthly_data.keys())
        report_data = []
        
        for month in months:
            data = monthly_data[month]
            report_data.append({
                'month': month,
                'sessions': data['sessions'],
                'time': data['time'],
                'avg_productivity': round(mean(data['productivity']), 2),
                'avg_distractions': round(mean(data['distractions']), 2),
                'consistency': round(self._calculate_consistency(data['productivity']), 2)
            })
        
        return {
            'total_months': len(report_data),
            'months': report_data,
            'total_sessions': sum(r['sessions'] for r in report_data),
            'total_time': sum(r['time'] for r in report_data),
            'avg_productivity': round(mean([r['avg_productivity'] for r in report_data]), 2) if report_data else 0
        }
    
    # ==========================================
    # INSIGHT GENERATION
    # ==========================================
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """
        Generate actionable insights from data
        
        Returns:
            List of insight dictionaries
        """
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if len(sessions) < 3:
            return [{
                'type': 'info',
                'title': 'Need More Data',
                'description': 'Add at least 3 sessions to get insights!',
                'priority': 'low'
            }]
        
        insights = []
        
        # 1. Productivity trend insight
        trend = self.engine._calculate_trend([s['productivity_score'] for s in sessions])
        if trend == 'improving':
            insights.append({
                'type': 'positive',
                'title': '📈 Your Productivity is Improving!',
                'description': 'Your productivity trend is going up. Keep up the great work!',
                'priority': 'high'
            })
        elif trend == 'declining':
            insights.append({
                'type': 'warning',
                'title': '⚠️ Productivity is Declining',
                'description': 'Your productivity has been decreasing. Try changing your study habits!',
                'priority': 'high'
            })
        
        # 2. Best time insight
        optimal = self.engine.get_optimal_study_times()
        if optimal.get('best_hour') is not None:
            insights.append({
                'type': 'recommendation',
                'title': '🕐 Best Time to Study',
                'description': f"Your peak productivity is at {optimal['best_hour']:02d}:00. Schedule important topics then!",
                'priority': 'medium'
            })
        
        # 3. Subject insight
        subject_analysis = self.engine.analyze_subject_performance()
        if subject_analysis.get('best_subject'):
            best = subject_analysis['best_subject']
            insights.append({
                'type': 'positive',
                'title': f'🌟 Best Subject: {best[0]}',
                'description': f"You perform best in {best[0]} with {best[1]['avg_productivity']}% productivity.",
                'priority': 'medium'
            })
        
        # 4. Consistency insight
        if len(sessions) > 3:
            scores = [s['productivity_score'] for s in sessions]
            std = stdev(scores) if len(scores) > 1 else 0
            if std < 10:
                insights.append({
                    'type': 'positive',
                    'title': '🎯 Very Consistent!',
                    'description': 'Your productivity is very consistent. This is excellent for learning!',
                    'priority': 'low'
                })
            elif std > 20:
                insights.append({
                    'type': 'warning',
                    'title': '📊 Inconsistent Performance',
                    'description': 'Your productivity varies a lot. Try to maintain a consistent routine!',
                    'priority': 'medium'
                })
        
        # 5. Streak insight
        streak = self.engine.calculate_streak(sessions)
        if streak.get('current_streak', 0) >= 3:
            insights.append({
                'type': 'positive',
                'title': f'🔥 {streak["current_streak"]}-Day Streak!',
                'description': f"You've studied for {streak['current_streak']} days in a row. Keep the momentum going!",
                'priority': 'high'
            })
        
        return insights
    
    # ==========================================
    # DATA EXPORT
    # ==========================================
    
    def export_data(self, format_type: str = 'json') -> Optional[str]:
        """
        Export all data in specified format
        
        Args:
            format_type: 'json' or 'csv'
            
        Returns:
            Path to exported file or None
        """
        sessions = self.storage.load_all_sessions()
        
        if not sessions:
            logger.warning("No data to export")
            return None
        
        os.makedirs('exports', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'json':
            filename = f'export_data_{timestamp}.json'
            filepath = os.path.join('exports', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2)
            
            logger.info(f"Exported {len(sessions)} sessions to {filepath}")
            return filepath
        
        elif format_type == 'csv':
            return self.engine.export_to_csv(sessions, f'export_data_{timestamp}.csv')
        
        else:
            logger.error(f"Unsupported export format: {format_type}")
            return None
    
    # ==========================================
    # COMPARISON ANALYSIS
    # ==========================================
    
    def compare_subjects(self, subject1: str, subject2: str) -> Dict[str, Any]:
        """
        Compare performance between two subjects
        
        Args:
            subject1: First subject name
            subject2: Second subject name
            
        Returns:
            Comparison results
        """
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        s1_sessions = [s for s in sessions if s.get('subject', '').lower() == subject1.lower()]
        s2_sessions = [s for s in sessions if s.get('subject', '').lower() == subject2.lower()]
        
        if not s1_sessions or not s2_sessions:
            return {'error': 'One or both subjects not found'}
        
        s1_avg = mean([s['productivity_score'] for s in s1_sessions])
        s2_avg = mean([s['productivity_score'] for s in s2_sessions])
        
        return {
            'subject1': {
                'name': subject1,
                'sessions': len(s1_sessions),
                'avg_productivity': round(s1_avg, 2)
            },
            'subject2': {
                'name': subject2,
                'sessions': len(s2_sessions),
                'avg_productivity': round(s2_avg, 2)
            },
            'difference': round(s1_avg - s2_avg, 2),
            'better_subject': subject1 if s1_avg > s2_avg else subject2
        }
    
    # ==========================================
    # CACHE MANAGEMENT
    # ==========================================
    
    def clear_all_cache(self) -> None:
        """Clear all cached data"""
        self.engine.clear_cache()
        logger.info("Analytics engine cache cleared")