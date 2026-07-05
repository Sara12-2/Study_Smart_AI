"""
Analytics Module - Advanced Analytics & Reporting
Extended analytics capabilities for the productivity engine
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, stdev
import numpy as np

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
    - Caching for performance
    """
    
    def __init__(self, storage, productivity_engine):
        """Initialize analytics engine with cache"""
        self.storage = storage
        self.engine = productivity_engine
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = timedelta(minutes=5)
        logger.info("AnalyticsEngine initialized")
    
    def _get_cached(self, key: str, func, *args, **kwargs):
        """Get cached data or compute fresh"""
        if key in self._cache:
            if datetime.now() - self._cache_time[key] < self._cache_ttl:
                return self._cache[key]
        result = func(*args, **kwargs)
        self._cache[key] = result
        self._cache_time[key] = datetime.now()
        return result
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics including advanced metrics"""
        cache_key = "comprehensive_stats"
        return self._get_cached(cache_key, self._get_comprehensive_stats)
    
    def _get_comprehensive_stats(self) -> Dict[str, Any]:
        """Internal method to get comprehensive stats"""
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        # Validate required fields
        required_fields = ['duration', 'productivity_score', 'timestamp']
        for field in required_fields:
            if field not in sessions[0]:
                return {'error': f'Missing required field: {field}'}
        
        total_sessions = len(sessions)
        total_time = sum(s['duration'] for s in sessions)
        total_distractions = sum(s.get('distractions', 0) for s in sessions)
        
        productivity_scores = [s['productivity_score'] for s in sessions]
        
        distribution = {
            'high': len([s for s in productivity_scores if s >= 80]),
            'medium': len([s for s in productivity_scores if 50 <= s < 80]),
            'low': len([s for s in productivity_scores if s < 50])
        }
        
        time_analysis = self._analyze_time_distribution(sessions)
        subject_analysis = self._analyze_subject_distribution(sessions)
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
        
        hour_distribution = defaultdict(int)
        day_distribution = defaultdict(int)
        month_distribution = defaultdict(int)
        
        for s in sessions:
            dt = datetime.fromisoformat(s['timestamp'])
            hour_distribution[dt.hour] += 1
            day_distribution[dt.weekday()] += 1
            month_distribution[dt.month] += 1
        
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
        
        sorted_sessions = sorted(sessions, key=lambda x: x['timestamp'])
        
        weekly_data = defaultdict(list)
        monthly_data = defaultdict(list)
        
        for s in sorted_sessions:
            dt = datetime.fromisoformat(s['timestamp'])
            week_key = dt.strftime('%Y-W%W')
            month_key = dt.strftime('%Y-%m')
            weekly_data[week_key].append(s['productivity_score'])
            monthly_data[month_key].append(s['productivity_score'])
        
        weekly_avg = {
            week: round(mean(scores), 2)
            for week, scores in weekly_data.items()
        }
        
        monthly_avg = {
            month: round(mean(scores), 2)
            for month, scores in monthly_data.items()
        }
        
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
        
        cv = (std / mean_val) * 100
        consistency = max(0, 100 - cv)
        return min(100, consistency)
    
    def prepare_chart_data(self, chart_type: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Prepare data for charts with configurable parameters"""
        if params is None:
            params = {}
        
        cache_key = f"chart_{chart_type}_{params.get('days', 30)}"
        return self._get_cached(cache_key, self._prepare_chart_data, chart_type, params)
    
    def _prepare_chart_data(self, chart_type: str, params: Dict) -> Dict[str, Any]:
        """Internal method to prepare chart data"""
        sessions = self.storage.load_all_sessions()
        sessions = self.engine._validate_sessions(sessions)
        
        if not sessions:
            return {'error': 'No sessions found'}
        
        if chart_type == 'daily':
            return self._prepare_daily_chart_data(sessions, params.get('days', 30))
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
    
    def _prepare_daily_chart_data(self, sessions: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
        """Prepare data for daily chart with configurable days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        daily_data = {}
        for i in range(days):
            date = (cutoff + timedelta(days=i)).strftime('%Y-%m-%d')
            daily_data[date] = {'sessions': 0, 'productivity': 0, 'time': 0}
        
        for s in sessions:
            date = datetime.fromisoformat(s['timestamp']).strftime('%Y-%m-%d')
            if date in daily_data:
                daily_data[date]['sessions'] += 1
                daily_data[date]['productivity'] += s['productivity_score']
                daily_data[date]['time'] += s['duration']
        
        for date, data in daily_data.items():
            data['avg_productivity'] = round(data['productivity'] / data['sessions'], 2) if data['sessions'] > 0 else 0
        
        return {
            'labels': list(daily_data.keys()),
            'datasets': {
                'sessions': [data['sessions'] for data in daily_data.values()],
                'productivity': [data['avg_productivity'] for data in daily_data.values()],
                'time': [data['time'] for data in daily_data.values()]
            }
        }
    
    # ... rest of methods remain similar with caching added
    
    def clear_all_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_time.clear()
        self.engine.clear_cache()
        logger.info("Analytics engine cache cleared")