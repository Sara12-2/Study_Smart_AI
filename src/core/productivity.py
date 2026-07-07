"""
Productivity Engine - Advanced Analytics Module
Enterprise-grade productivity calculations with statistical analysis
"""

import logging
import csv
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, stdev
from enum import Enum
import math
import numpy as np

logger = logging.getLogger(__name__)


class PerformanceGrade(Enum):
    """Performance grades with internationalization support"""
    A = (90, "🌟 Outstanding performance! Keep it up!")
    B = (80, "👏 Great performance! You're doing well!")
    C = (70, "📈 Good performance! Keep pushing!")
    D = (60, "📊 Average performance. Room for improvement!")
    F = (0, "⚠️ Needs improvement. Let's focus!")

    def __init__(self, threshold: int, message: str):
        self.threshold = threshold
        self.message = message


class ProductivityWeights:
    """Configuration constants for productivity calculations"""
    PERFORMANCE_WEIGHT = 0.7
    CONSISTENCY_WEIGHT = 0.3
    PRODUCTIVITY_SCORE_WEIGHT = 0.6
    SESSION_COUNT_WEIGHT = 0.4
    
    # Trend detection thresholds
    TREND_IMPROVING_THRESHOLD = 1.05
    TREND_DECLINING_THRESHOLD = 0.95
    
    # Streak thresholds
    STREAK_ON_FIRE_THRESHOLD = 5
    STREAK_BUILDING_THRESHOLD = 2
    
    # Limits
    OPTIMAL_HOURS_LIMIT = 6
    MAX_SESSIONS_FOR_ANALYSIS = 1000
    CACHE_TTL_MINUTES = 5


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
    
    def __init__(self, storage, locale: str = 'en'):
        """
        Initialize productivity engine
        
        Args:
            storage: Storage backend for session data
            locale: Language locale for messages (default: 'en')
        """
        self.storage = storage
        self.locale = locale
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = timedelta(minutes=ProductivityWeights.CACHE_TTL_MINUTES)
        
        # Initialize translations
        self._init_translations()
        
        logger.info(f"ProductivityEngine initialized with locale: {locale}")
    
    def _init_translations(self):
        """Initialize multi-language support"""
        self.translations = {
            'en': {
                'streak_on_fire': '🔥 On fire!',
                'streak_building': '💪 Building',
                'streak_starting': '🌱 Starting',
                'trend_improving': '📈 Improving',
                'trend_declining': '📉 Declining',
                'trend_stable': '➡️ Stable',
                'trend_neutral': 'neutral',
                'comparison_improved': '📈 Improved',
                'comparison_declined': '📉 Declined',
                'comparison_stable': '➡️ Stable',
                'recommendation': 'Your peak productivity time is {hour}:00 ({period}) with {score}% average productivity. Schedule your most important tasks during this time for optimal results!',
                'no_data': 'No data available for recommendations. Start tracking your sessions!',
                'time_period_morning': 'morning',
                'time_period_afternoon': 'afternoon',
                'time_period_evening': 'evening',
                'time_period_night': 'night',
                'error_no_sessions': 'No sessions found',
                'total_sessions': 'Total Sessions',
                'avg_productivity': 'Average Productivity',
                'best_session': 'Best Session',
                'worst_session': 'Worst Session',
                'total_time': 'Total Time',
                'subjects': 'Subjects',
                'consistency': 'Consistency Score',
                'grade_message': 'Grade: {grade} - {message}'
            },
            'es': {
                'streak_on_fire': '🔥 ¡En llamas!',
                'streak_building': '💪 Construyendo',
                'streak_starting': '🌱 Comenzando',
                'trend_improving': '📈 Mejorando',
                'trend_declining': '📉 Declinando',
                'trend_stable': '➡️ Estable',
                'trend_neutral': 'neutral',
                'comparison_improved': '📈 Mejorado',
                'comparison_declined': '📉 Disminuido',
                'comparison_stable': '➡️ Estable',
                'recommendation': 'Tu hora pico de productividad es a las {hour}:00 ({period}) con un {score}% de productividad promedio. ¡Programa tus tareas más importantes durante este tiempo para obtener resultados óptimos!',
                'no_data': 'No hay datos disponibles para recomendaciones. ¡Comienza a registrar tus sesiones!',
                'time_period_morning': 'mañana',
                'time_period_afternoon': 'tarde',
                'time_period_evening': 'noche',
                'time_period_night': 'madrugada',
                'error_no_sessions': 'No se encontraron sesiones',
                'total_sessions': 'Sesiones Totales',
                'avg_productivity': 'Productividad Promedio',
                'best_session': 'Mejor Sesión',
                'worst_session': 'Peor Sesión',
                'total_time': 'Tiempo Total',
                'subjects': 'Asignaturas',
                'consistency': 'Puntuación de Consistencia',
                'grade_message': 'Calificación: {grade} - {message}'
            },
            'fr': {
                'streak_on_fire': '🔥 En feu !',
                'streak_building': '💪 En construction',
                'streak_starting': '🌱 Début',
                'trend_improving': '📈 Amélioration',
                'trend_declining': '📉 Déclin',
                'trend_stable': '➡️ Stable',
                'trend_neutral': 'neutre',
                'comparison_improved': '📈 Amélioré',
                'comparison_declined': '📉 Diminué',
                'comparison_stable': '➡️ Stable',
                'recommendation': 'Votre heure de productivité maximale est {hour}:00 ({period}) avec {score}% de productivité moyenne. Planifiez vos tâches les plus importantes pendant cette période pour des résultats optimaux!',
                'no_data': 'Aucune donnée disponible pour les recommandations. Commencez à suivre vos sessions!',
                'time_period_morning': 'matin',
                'time_period_afternoon': 'après-midi',
                'time_period_evening': 'soir',
                'time_period_night': 'nuit',
                'error_no_sessions': 'Aucune session trouvée',
                'total_sessions': 'Sessions Totales',
                'avg_productivity': 'Productivité Moyenne',
                'best_session': 'Meilleure Session',
                'worst_session': 'Pire Session',
                'total_time': 'Temps Total',
                'subjects': 'Sujets',
                'consistency': 'Score de Cohérence',
                'grade_message': 'Note: {grade} - {message}'
            }
        }
    
    def _translate(self, key: str, **kwargs) -> str:
        """Get translated message"""
        translation = self.translations.get(self.locale, self.translations['en']).get(key, key)
        if kwargs:
            return translation.format(**kwargs)
        return translation
    
    def _get_validated_sessions(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load and validate sessions with optional time filter
        
        Args:
            days: Optional number of days to filter (None for all)
        
        Returns:
            List of validated sessions
        """
        sessions = self.storage.load_all_sessions()
        
        # Apply time filter if specified
        if days is not None:
            cutoff = datetime.now() - timedelta(days=days)
            filtered = []
            for s in sessions:
                try:
                    if datetime.fromisoformat(s.get('timestamp', '')) >= cutoff:
                        filtered.append(s)
                except (ValueError, TypeError):
                    continue
            sessions = filtered
        
        # Validate and limit sessions
        if len(sessions) > ProductivityWeights.MAX_SESSIONS_FOR_ANALYSIS:
            logger.warning(f"Large dataset: {len(sessions)} sessions. Limiting to {ProductivityWeights.MAX_SESSIONS_FOR_ANALYSIS}")
            sessions = sessions[-ProductivityWeights.MAX_SESSIONS_FOR_ANALYSIS:]
        
        valid_sessions = []
        for s in sessions:
            try:
                duration = s.get('duration')
                score = s.get('productivity_score')
                timestamp = s.get('timestamp')
                
                if (isinstance(duration, (int, float)) and 
                    isinstance(score, (int, float)) and 
                    timestamp and
                    not math.isnan(float(score)) and
                    not math.isnan(float(duration))):
                    valid_sessions.append(s)
            except (ValueError, TypeError):
                continue
        
        return valid_sessions
    
    def _get_date_key(self, timestamp: str, period: str = 'day') -> str:
        """Extract date key based on period"""
        try:
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
        except (ValueError, TypeError):
            return timestamp
    
    def _get_cached(self, key: str, func, *args, **kwargs):
        """Get cached data or compute fresh"""
        if key in self._cache:
            if datetime.now() - self._cache_time[key] < self._cache_ttl:
                return self._cache[key]
        
        result = func(*args, **kwargs)
        self._cache[key] = result
        self._cache_time[key] = datetime.now()
        return result
    
    def calculate_detailed_stats(self, values: List[float]) -> Dict[str, Any]:
        """Calculate detailed statistics"""
        if not values:
            return {
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'range': 0,
                'q1': 0,
                'q3': 0,
                'iqr': 0,
                'skewness': 0,
                'kurtosis': 0,
                'count': 0
            }
        
        clean_values = [v for v in values if not math.isnan(float(v))]
        
        if not clean_values:
            return {
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'range': 0,
                'q1': 0,
                'q3': 0,
                'iqr': 0,
                'skewness': 0,
                'kurtosis': 0,
                'count': 0
            }
        
        return {
            'mean': round(mean(clean_values), 2),
            'median': round(median(clean_values), 2),
            'std': round(stdev(clean_values), 2) if len(clean_values) > 1 else 0,
            'min': min(clean_values),
            'max': max(clean_values),
            'range': round(max(clean_values) - min(clean_values), 2),
            'q1': round(np.percentile(clean_values, 25), 2) if len(clean_values) > 1 else 0,
            'q3': round(np.percentile(clean_values, 75), 2) if len(clean_values) > 1 else 0,
            'iqr': round(np.percentile(clean_values, 75) - np.percentile(clean_values, 25), 2) if len(clean_values) > 1 else 0,
            'skewness': round(self._calculate_skewness(clean_values), 2),
            'kurtosis': round(self._calculate_kurtosis(clean_values), 2),
            'count': len(clean_values)
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
        """Get performance grade with localized message"""
        try:
            score = float(score)
            if math.isnan(score):
                return {
                    'grade': 'F', 
                    'message': PerformanceGrade.F.message,
                    'localized_message': self._translate('grade_message', 
                                                       grade='F', 
                                                       message=PerformanceGrade.F.message)
                }
        except (ValueError, TypeError):
            return {
                'grade': 'F', 
                'message': PerformanceGrade.F.message,
                'localized_message': self._translate('grade_message', 
                                                   grade='F', 
                                                   message=PerformanceGrade.F.message)
            }
        
        if score >= 90:
            grade_data = PerformanceGrade.A
        elif score >= 80:
            grade_data = PerformanceGrade.B
        elif score >= 70:
            grade_data = PerformanceGrade.C
        elif score >= 60:
            grade_data = PerformanceGrade.D
        else:
            grade_data = PerformanceGrade.F
        
        return {
            'grade': grade_data.name,
            'message': grade_data.message,
            'localized_message': self._translate('grade_message', 
                                               grade=grade_data.name, 
                                               message=grade_data.message)
        }
    
    def calculate_streak(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate current study streak"""
        if not sessions:
            return {
                'current_streak': 0, 
                'best_streak': 0, 
                'streak_status': self._translate('streak_starting'),
                'total_days': 0
            }
        
        dates = set()
        for s in sessions:
            if s.get('timestamp'):
                try:
                    date = datetime.fromisoformat(s['timestamp']).date()
                    dates.add(date)
                except (ValueError, TypeError):
                    continue
        
        if not dates:
            return {
                'current_streak': 0, 
                'best_streak': 0, 
                'streak_status': self._translate('streak_starting'),
                'total_days': 0
            }
        
        sorted_dates = sorted(dates)
        
        # Calculate best streak
        best_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 1
        
        # Calculate current streak from today backwards
        current_streak_count = 0
        check_date = datetime.now().date()
        
        while check_date in dates:
            current_streak_count += 1
            check_date -= timedelta(days=1)
        
        # Determine streak status
        if current_streak_count >= ProductivityWeights.STREAK_ON_FIRE_THRESHOLD:
            status = self._translate('streak_on_fire')
        elif current_streak_count >= ProductivityWeights.STREAK_BUILDING_THRESHOLD:
            status = self._translate('streak_building')
        else:
            status = self._translate('streak_starting')
        
        return {
            'current_streak': current_streak_count,
            'best_streak': best_streak,
            'total_days': len(dates),
            'streak_status': status
        }
    
    def calculate_daily_summary(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Calculate comprehensive daily summary"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cache_key = f"daily_summary_{date}_{self.locale}"
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
        
        subjects = defaultdict(int)
        subject_productivity = defaultdict(list)
        for s in sessions:
            subjects[s.get('subject', 'Unknown')] += s['duration']
            subject_productivity[s.get('subject', 'Unknown')].append(s['productivity_score'])
        
        best_subject = max(subject_productivity.items(), key=lambda x: mean(x[1])) if subject_productivity else None
        worst_subject = min(subject_productivity.items(), key=lambda x: mean(x[1])) if subject_productivity else None
        
        hour_distribution = defaultdict(int)
        for s in sessions:
            try:
                hour = datetime.fromisoformat(s['timestamp']).hour
                hour_distribution[hour] += 1
            except (ValueError, TypeError):
                continue
        
        peak_hour = max(hour_distribution.items(), key=lambda x: x[1]) if hour_distribution else None
        
        if len(sessions) > 1:
            productivity_values = [s['productivity_score'] for s in sessions]
            consistency = 100 - (stdev(productivity_values) / 100 * 100)
            consistency = max(0, min(100, consistency))
        else:
            consistency = 100
        
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
        """Calculate trend direction with localization"""
        if len(values) < 2:
            return self._translate('trend_neutral')
        
        clean_values = [v for v in values if not math.isnan(float(v))]
        if len(clean_values) < 2:
            return self._translate('trend_neutral')
        
        first_half = mean(clean_values[:len(clean_values)//2])
        second_half = mean(clean_values[len(clean_values)//2:])
        
        if second_half > first_half * ProductivityWeights.TREND_IMPROVING_THRESHOLD:
            return self._translate('trend_improving')
        elif second_half < first_half * ProductivityWeights.TREND_DECLINING_THRESHOLD:
            return self._translate('trend_declining')
        return self._translate('trend_stable')
    
    def _calculate_productivity_score(self, sessions: List[Dict[str, Any]]) -> int:
        """Calculate overall productivity score"""
        if not sessions:
            return 0
        
        avg_score = mean(s['productivity_score'] for s in sessions)
        consistency = min(100, max(0, len(sessions) / 10 * 10))
        
        score = (avg_score * ProductivityWeights.PERFORMANCE_WEIGHT) + (consistency * ProductivityWeights.CONSISTENCY_WEIGHT)
        return round(score)
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate comprehensive weekly report"""
        cache_key = f"weekly_report_{self.locale}"
        return self._get_cached(cache_key, self._generate_weekly_report)
    
    def _generate_weekly_report(self) -> Dict[str, Any]:
        """Internal method to generate weekly report"""
        sessions = self._get_validated_sessions()
        
        if not sessions:
            return {
                'error': self._translate('error_no_sessions'), 
                'total_sessions': 0,
                'total_weeks': 0
            }
        
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
            trend = self._translate('trend_neutral')
        
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
        sessions = self._get_validated_sessions()
        
        if not sessions:
            return {
                'error': self._translate('error_no_sessions'), 
                'subjects': [], 
                'total_subjects': 0
            }
        
        subject_data = defaultdict(lambda: {
            'sessions': 0,
            'total_time': 0,
            'productivity_scores': [],
            'distractions': []
        })
        
        for s in sessions:
            subject = s.get('subject', 'Unknown')
            if not subject:
                subject = 'Unknown'
            subject_data[subject]['sessions'] += 1
            subject_data[subject]['total_time'] += s.get('duration', 0)
            subject_data[subject]['productivity_scores'].append(s.get('productivity_score', 0))
            subject_data[subject]['distractions'].append(s.get('distractions', 0))
        
        subject_metrics = {}
        for subject, data in subject_data.items():
            if data['productivity_scores']:
                avg_prod = mean(data['productivity_scores'])
                max_prod = max(data['productivity_scores'])
                min_prod = min(data['productivity_scores'])
                avg_dist = mean(data['distractions'])
            else:
                avg_prod = 0
                max_prod = 0
                min_prod = 0
                avg_dist = 0
            
            subject_metrics[subject] = {
                'sessions': data['sessions'],
                'total_time': data['total_time'],
                'avg_productivity': round(avg_prod, 2),
                'max_productivity': round(max_prod, 2),
                'min_productivity': round(min_prod, 2),
                'avg_distractions': round(avg_dist, 2),
                'total_distractions': sum(data['distractions'])
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
        cache_key = f"trends_{days}_{self.locale}"
        return self._get_cached(cache_key, self._get_productivity_trends, days)
    
    def _get_productivity_trends(self, days: int) -> Dict[str, Any]:
        """Internal method to get productivity trends"""
        sessions = self._get_validated_sessions(days=days)
        
        if not sessions:
            return {
                'error': self._translate('error_no_sessions'), 
                'total_sessions': 0,
                'days_analyzed': 0
            }
        
        daily_data = defaultdict(list)
        for s in sessions:
            try:
                day = self._get_date_key(s['timestamp'], 'day')
                daily_data[day].append(s['productivity_score'])
            except (ValueError, TypeError):
                continue
        
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
            
            trend_direction = self._translate('trend_improving') if slope > 0.5 else \
                            self._translate('trend_declining') if slope < -0.5 else \
                            self._translate('trend_stable')
            slope_percentage = round(slope * 100 / (max(values) if max(values) > 0 else 1), 2)
        else:
            trend_direction = self._translate('trend_neutral')
            slope_percentage = 0
        
        return {
            'days_analyzed': len(daily_averages),
            'total_sessions': len(sessions),
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
        cache_key = f"optimal_times_{self.locale}"
        return self._get_cached(cache_key, self._get_optimal_study_times)
    
    def _get_optimal_study_times(self) -> Dict[str, Any]:
        """Internal method to find optimal study times"""
        sessions = self._get_validated_sessions()
        
        if not sessions:
            return {
                'error': self._translate('error_no_sessions'), 
                'total_sessions': 0
            }
        
        hour_data = defaultdict(list)
        for s in sessions:
            try:
                hour = datetime.fromisoformat(s['timestamp']).hour
                hour_data[hour].append({
                    'productivity': s['productivity_score'],
                    'duration': s['duration'],
                    'subject': s.get('subject', 'Unknown')
                })
            except (ValueError, TypeError):
                continue
        
        hour_metrics = {}
        for hour, data in hour_data.items():
            avg_productivity = mean(d['productivity'] for d in data)
            avg_duration = mean(d['duration'] for d in data)
            total_sessions = len(data)
            
            hour_metrics[hour] = {
                'avg_productivity': round(avg_productivity, 2),
                'avg_duration': round(avg_duration, 2),
                'total_sessions': total_sessions,
                'score': round((avg_productivity * ProductivityWeights.PRODUCTIVITY_SCORE_WEIGHT) + 
                             (min(100, total_sessions * 10) * ProductivityWeights.SESSION_COUNT_WEIGHT), 2),
                'grade': self.get_performance_grade(avg_productivity)
            }
        
        sorted_hours = sorted(
            hour_metrics.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        peak_periods = []
        current_period = []
        
        for hour, metrics in sorted_hours[:ProductivityWeights.OPTIMAL_HOURS_LIMIT]:
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
        """Generate human-readable recommendation with localization"""
        if not sorted_hours:
            return self._translate('no_data')
        
        best_hour = sorted_hours[0][0]
        best_score = sorted_hours[0][1]['avg_productivity']
        
        if best_hour < 12:
            time_period = self._translate('time_period_morning')
        elif best_hour < 17:
            time_period = self._translate('time_period_afternoon')
        elif best_hour < 21:
            time_period = self._translate('time_period_evening')
        else:
            time_period = self._translate('time_period_night')
        
        return self._translate(
            'recommendation',
            hour=best_hour,
            period=time_period,
            score=best_score
        )
    
    def export_to_csv(self, sessions: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export sessions to CSV with sanitized filename
        
        Args:
            sessions: List of session dictionaries
            filename: Optional filename (will be sanitized)
        
        Returns:
            Path to exported file
        """
        if not sessions:
            raise ValueError("No sessions to export")
        
        if filename is None:
            filename = f"study_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        else:
            # Sanitize filename to prevent path traversal
            filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
            if not filename.endswith('.csv'):
                filename += '.csv'
        
        os.makedirs('exports', exist_ok=True)
        filepath = os.path.join('exports', filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sessions[0].keys())
                writer.writeheader()
                writer.writerows(sessions)
            
            logger.info(f"Exported {len(sessions)} sessions to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            raise
    
    def compare_periods(self, period1: str, period2: str, period_type: str = 'week') -> Dict[str, Any]:
        """Compare two time periods with localization"""
        sessions = self._get_validated_sessions()
        
        p1_sessions = [s for s in sessions if self._get_date_key(s['timestamp'], period_type) == period1]
        p2_sessions = [s for s in sessions if self._get_date_key(s['timestamp'], period_type) == period2]
        
        p1_avg = mean([s['productivity_score'] for s in p1_sessions]) if p1_sessions else 0
        p2_avg = mean([s['productivity_score'] for s in p2_sessions]) if p2_sessions else 0
        
        improvement = ((p2_avg - p1_avg) / p1_avg * 100) if p1_avg > 0 else 0
        
        if improvement > 0:
            improvement_text = self._translate('comparison_improved')
        elif improvement < 0:
            improvement_text = self._translate('comparison_declined')
        else:
            improvement_text = self._translate('comparison_stable')
        
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
            'improvement_text': improvement_text,
            'grade1': self.get_performance_grade(p1_avg),
            'grade2': self.get_performance_grade(p2_avg)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a quick performance summary with localization"""
        sessions = self._get_validated_sessions()
        
        if not sessions:
            return {
                'error': self._translate('error_no_sessions'),
                'total_sessions': 0
            }
        
        scores = [s.get('productivity_score', 0) for s in sessions if s.get('productivity_score') is not None]
        
        if not scores:
            return {
                'error': self._translate('error_no_sessions'),
                'total_sessions': len(sessions)
            }
        
        avg_score = mean(scores)
        grade = self.get_performance_grade(avg_score)
        
        return {
            'total_sessions': len(sessions),
            'avg_productivity': round(avg_score, 2),
            'best_session': max(scores),
            'worst_session': min(scores),
            'grade': grade,
            'streak': self.calculate_streak(sessions),
            'total_time': sum(s.get('duration', 0) for s in sessions),
            'subjects': len(set(s.get('subject', 'Unknown') for s in sessions)),
            'localized_labels': {
                'total_sessions': self._translate('total_sessions'),
                'avg_productivity': self._translate('avg_productivity'),
                'best_session': self._translate('best_session'),
                'worst_session': self._translate('worst_session'),
                'total_time': self._translate('total_time'),
                'subjects': self._translate('subjects'),
                'consistency': self._translate('consistency')
            }
        }
    
    def export_to_excel(self, sessions: List[Dict[str, Any]], filename: str = None) -> Optional[str]:
        """
        Export sessions to Excel with sanitized filename
        
        Args:
            sessions: List of session dictionaries
            filename: Optional filename (will be sanitized)
        
        Returns:
            Path to exported file or None if pandas not available
        """
        try:
            import pandas as pd
            
            if not sessions:
                raise ValueError("No sessions to export")
            
            if filename is None:
                filename = f"study_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            else:
                # Sanitize filename
                filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
            
            os.makedirs('exports', exist_ok=True)
            filepath = os.path.join('exports', filename)
            
            df = pd.DataFrame(sessions)
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"Exported {len(sessions)} sessions to {filepath}")
            return filepath
            
        except ImportError:
            logger.warning("pandas or openpyxl not installed. Install with: pip install pandas openpyxl")
            return None
        except Exception as e:
            logger.error(f"Failed to export Excel: {e}")
            return None
    
    def set_locale(self, locale: str) -> None:
        """
        Change the language locale
        
        Args:
            locale: Language code ('en', 'es', 'fr')
        """
        if locale in self.translations:
            self.locale = locale
            self.clear_cache()  # Clear cache to refresh translations
            logger.info(f"Locale changed to: {locale}")
        else:
            raise ValueError(f"Unsupported locale: {locale}. Available: {list(self.translations.keys())}")
    
    def get_available_locales(self) -> List[str]:
        """Get list of available locales"""
        return list(self.translations.keys())
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_time.clear()
        logger.info("Cache cleared")

    def _validate_sessions(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Legacy method for backward compatibility"""
        return self._get_validated_sessions()