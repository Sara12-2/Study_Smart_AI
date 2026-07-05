"""
AI Analyzer Module
Advanced data analysis with statistical methods
"""

import logging
import math
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    AI-powered data analyzer with advanced statistical methods
    
    Features:
    - Statistical analysis
    - Pattern detection
    - Anomaly detection
    - Correlation analysis
    - Time series analysis
    - Caching for performance
    """
    
    def __init__(self):
        """Initialize the analyzer with cache"""
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = timedelta(minutes=5)
        logger.info("AIAnalyzer initialized")
    
    def _get_cached(self, key: str, func, *args, **kwargs):
        """Get cached data or compute fresh"""
        if key in self._cache:
            if datetime.now() - self._cache_time[key] < self._cache_ttl:
                return self._cache[key]
        
        result = func(*args, **kwargs)
        self._cache[key] = result
        self._cache_time[key] = datetime.now()
        return result
    
    def prepare_dataframe(self, sessions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert sessions to pandas DataFrame for analysis"""
        if not sessions:
            return pd.DataFrame()
        
        df = pd.DataFrame(sessions)
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['week'] = df['timestamp'].dt.isocalendar().week
            df['month'] = df['timestamp'].dt.month
        
        return df
    
    def analyze_productivity_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze productivity patterns using statistical methods"""
        if df.empty:
            return {'error': 'No data available'}
        
        if 'productivity_score' not in df.columns:
            return {'error': 'Missing productivity_score column'}
        
        # 🔥 FIX: Clean NaN values from productivity_score
        df = df.copy()
        df['productivity_score'] = df['productivity_score'].fillna(0)
        
        results = {
            'overall_stats': {},
            'daily_patterns': {},
            'weekly_patterns': {},
            'hourly_patterns': {},
            'correlations': {},
            'anomalies': [],
            'consistency': 0
        }
        
        scores = df['productivity_score'].dropna()
        if len(scores) == 0:
            return {'error': 'No valid productivity scores'}
        
        results['overall_stats'] = {
            'mean': round(float(mean(scores)), 2),
            'median': round(float(median(scores)), 2),
            'std': round(float(stdev(scores)), 2) if len(scores) > 1 else 0,
            'min': float(min(scores)),
            'max': float(max(scores)),
            'q1': round(float(np.percentile(scores, 25)), 2) if len(scores) > 1 else 0,
            'q3': round(float(np.percentile(scores, 75)), 2) if len(scores) > 1 else 0
        }
        
        if len(scores) > 1:
            results['consistency'] = round(100 - (float(stdev(scores)) / 100 * 100), 2)
            results['consistency'] = max(0, min(100, results['consistency']))
        else:
            results['consistency'] = 100
        
        if 'day_of_week' in df.columns:
            daily_avg = df.groupby('day_of_week')['productivity_score'].mean()
            daily_counts = df.groupby('day_of_week').size()
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            results['daily_patterns'] = {
                'avg_productivity': {
                    day: round(float(daily_avg.get(i, 0)), 2)
                    for i, day in enumerate(days)
                },
                'session_counts': {
                    day: int(daily_counts.get(i, 0))
                    for i, day in enumerate(days)
                },
                'best_day': days[int(daily_avg.idxmax())] if not daily_avg.empty else None,
                'worst_day': days[int(daily_avg.idxmin())] if not daily_avg.empty else None
            }
        
        if 'hour' in df.columns:
            hourly_avg = df.groupby('hour')['productivity_score'].mean()
            hourly_counts = df.groupby('hour').size()
            
            results['hourly_patterns'] = {
                'avg_productivity': {int(k): round(float(v), 2) for k, v in hourly_avg.to_dict().items()},
                'session_counts': {int(k): int(v) for k, v in hourly_counts.to_dict().items()},
                'peak_hour': int(hourly_avg.idxmax()) if not hourly_avg.empty else None,
                'low_hour': int(hourly_avg.idxmin()) if not hourly_avg.empty else None
            }
        
        if 'week' in df.columns:
            weekly_avg = df.groupby('week')['productivity_score'].mean()
            results['weekly_patterns'] = {
                'avg_productivity': {int(k): round(float(v), 2) for k, v in weekly_avg.to_dict().items()},
                'trend': self._calculate_trend(weekly_avg.values.tolist()) if len(weekly_avg) > 1 else 'insufficient'
            }
        
        if len(df) > 5:
            correlations = {}
            
            if 'duration' in df.columns and 'productivity_score' in df.columns:
                corr = df['duration'].corr(df['productivity_score'])
                if not math.isnan(corr):
                    correlations['duration_productivity'] = round(float(corr), 3)
            
            if 'distractions' in df.columns and 'productivity_score' in df.columns:
                corr = df['distractions'].corr(df['productivity_score'])
                if not math.isnan(corr):
                    correlations['distractions_productivity'] = round(float(corr), 3)
            
            if 'hour' in df.columns and 'productivity_score' in df.columns:
                corr = df['hour'].corr(df['productivity_score'])
                if not math.isnan(corr):
                    correlations['hour_productivity'] = round(float(corr), 3)
            
            results['correlations'] = correlations
        
        if len(df) > 10:
            mean_score = float(mean(scores))
            std_score = float(stdev(scores)) if len(scores) > 1 else 1
            
            z_scores = (scores - mean_score) / std_score
            anomalies = df[abs(z_scores) > 2]
            
            if not anomalies.empty:
                for idx, row in anomalies.iterrows():
                    results['anomalies'].append({
                        'subject': row.get('subject', 'Unknown'),
                        'productivity': float(row.get('productivity_score', 0)),
                        'timestamp': str(row.get('timestamp', '')),
                        'z_score': round(float(z_scores[idx]), 2)
                    })
        
        return results
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'insufficient'
        
        clean_values = [v for v in values if not math.isnan(v)]
        if len(clean_values) < 2:
            return 'insufficient'
        
        first_half = mean(clean_values[:len(clean_values)//2])
        second_half = mean(clean_values[len(clean_values)//2:])
        
        if second_half > first_half * 1.05:
            return 'improving'
        elif second_half < first_half * 0.95:
            return 'declining'
        return 'stable'
    
    def detect_learning_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect learning patterns and habits"""
        if df.empty:
            return {'error': 'No data available'}
        
        patterns = {
            'best_learning_time': None,
            'most_consistent_subject': None,
            'least_consistent_subject': None,
            'optimal_session_length': None,
            'distraction_patterns': {},
            'mood_productivity_correlation': None
        }
        
        if 'hour' in df.columns and 'productivity_score' in df.columns:
            hourly_avg = df.groupby('hour')['productivity_score'].mean()
            if not hourly_avg.empty:
                best_hour = hourly_avg.idxmax()
                if not math.isnan(hourly_avg[best_hour]):
                    patterns['best_learning_time'] = {
                        'hour': int(best_hour),
                        'avg_productivity': round(float(hourly_avg[best_hour]), 2)
                    }
        
        if 'subject' in df.columns and 'productivity_score' in df.columns:
            subject_stats = df.groupby('subject')['productivity_score'].agg(['mean', 'std'])
            
            if not subject_stats.empty:
                most_consistent = subject_stats.loc[subject_stats['std'].idxmin()]
                if not math.isnan(most_consistent['mean']):
                    patterns['most_consistent_subject'] = {
                        'subject': subject_stats['std'].idxmin(),
                        'avg': round(float(most_consistent['mean']), 2),
                        'std': round(float(most_consistent['std']), 2)
                    }
                
                least_consistent = subject_stats.loc[subject_stats['std'].idxmax()]
                if not math.isnan(least_consistent['mean']):
                    patterns['least_consistent_subject'] = {
                        'subject': subject_stats['std'].idxmax(),
                        'avg': round(float(least_consistent['mean']), 2),
                        'std': round(float(least_consistent['std']), 2)
                    }
        
        if 'duration' in df.columns and 'productivity_score' in df.columns:
            bins = [0, 15, 30, 45, 60, 90, 120, 240]
            df['duration_bin'] = pd.cut(df['duration'], bins)
            duration_scores = df.groupby('duration_bin')['productivity_score'].mean()
            
            if not duration_scores.empty:
                best_bin = duration_scores.idxmax()
                if not math.isnan(duration_scores[best_bin]):
                    patterns['optimal_session_length'] = {
                        'range': str(best_bin),
                        'avg_productivity': round(float(duration_scores[best_bin]), 2)
                    }
        
        if 'distractions' in df.columns:
            patterns['distraction_patterns'] = {
                'avg_distractions': round(float(df['distractions'].mean()), 2),
                'max_distractions': int(df['distractions'].max()),
                'zero_distraction_sessions': int((df['distractions'] == 0).sum()),
                'high_distraction_sessions': int((df['distractions'] > 5).sum()),
                'distraction_rate': round(
                    float((df['distractions'] > 0).sum()) / len(df) * 100, 2
                )
            }
        
        if 'mood' in df.columns and 'productivity_score' in df.columns:
            mood_df = df[df['mood'].notna()]
            if len(mood_df) > 3:
                corr = mood_df['mood'].corr(mood_df['productivity_score'])
                if not math.isnan(corr):
                    patterns['mood_productivity_correlation'] = round(float(corr), 3)
        
        return patterns
    
    def generate_insights(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive AI insights"""
        import math
        import numpy as np
        
        # Filter out invalid sessions
        valid_sessions = []
        for s in sessions:
            score = s.get('productivity_score')
            if score is not None:
                try:
                    score_float = float(score)
                    if not math.isnan(score_float) and not np.isnan(score_float):
                        # Ensure score is within valid range
                        if 0 <= score_float <= 100:
                            s['productivity_score'] = score_float
                            valid_sessions.append(s)
                        else:
                            # Clamp to valid range
                            s['productivity_score'] = max(0, min(100, score_float))
                            valid_sessions.append(s)
                except (ValueError, TypeError):
                    continue
        
        if len(valid_sessions) < 5:
            return {
                'error': 'Insufficient data',
                'message': f'Need 5 valid sessions, have {len(valid_sessions)}',
                'current_sessions': len(valid_sessions)
            }
        
        df = self.prepare_dataframe(valid_sessions)
        
        if df.empty:
            return {
                'error': 'Insufficient data',
                'message': 'No valid data found'
            }
        
        if 'productivity_score' not in df.columns:
            return {
                'error': 'Missing productivity scores',
                'message': 'Sessions must have productivity_score field'
            }
        
        try:
            patterns = self.detect_learning_patterns(df)
            analysis = self.analyze_productivity_patterns(df)
            
            def clean_nan(obj):
                if isinstance(obj, dict):
                    return {k: clean_nan(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_nan(v) for v in obj]
                elif isinstance(obj, float):
                    if math.isnan(obj) or np.isnan(obj):
                        return 0
                    return obj
                elif isinstance(obj, (int, str, bool)):
                    return obj
                elif obj is None:
                    return 0
                else:
                    return 0
            
            patterns = clean_nan(patterns) if patterns else {}
            analysis = clean_nan(analysis) if analysis else {}
            
            # Ensure analysis has required fields
            if analysis and isinstance(analysis, dict):
                if 'overall_stats' not in analysis or not analysis['overall_stats']:
                    analysis['overall_stats'] = {'mean': 0, 'median': 0, 'std': 0, 'min': 0, 'max': 0, 'q1': 0, 'q3': 0}
                if 'consistency' not in analysis:
                    analysis['consistency'] = 0
            
            insights = {
                'patterns': patterns,
                'analysis': analysis,
                'total_sessions': len(valid_sessions),
                'ai_confidence': self._calculate_confidence(df),
                'consistency': analysis.get('consistency', 0) if analysis else 0,
                'recommendations': self._generate_recommendations(patterns, analysis)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                'error': 'Analysis failed',
                'message': str(e)
            }
    
    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """Calculate AI confidence score based on data amount"""
        n = len(df)
        if n < 5:
            return 0
        elif n < 10:
            return round(30 + (n - 5) * 6, 2)
        elif n < 20:
            return round(60 + (n - 10) * 2, 2)
        else:
            return min(95, 80 + (n - 20) * 0.5)
    
    def _generate_recommendations(self, patterns: Dict, analysis: Dict) -> List[str]:
        """Generate human-readable recommendations"""
        recommendations = []
        
        if patterns and patterns.get('best_learning_time'):
            hour = patterns['best_learning_time']['hour']
            productivity = patterns['best_learning_time']['avg_productivity']
            recommendations.append(
                f"Schedule your study sessions around {hour:02d}:00 - you're {productivity}% productive then!"
            )
        
        if patterns and patterns.get('optimal_session_length'):
            range_str = patterns['optimal_session_length']['range']
            productivity = patterns['optimal_session_length']['avg_productivity']
            recommendations.append(
                f"Optimal session length: {range_str} - {productivity}% average productivity"
            )
        
        if patterns and patterns.get('most_consistent_subject'):
            subject = patterns['most_consistent_subject']['subject']
            recommendations.append(
                f"You're most consistent with {subject} - keep it up!"
            )
        
        if patterns and patterns.get('distraction_patterns'):
            rate = patterns['distraction_patterns'].get('distraction_rate', 0)
            zero_sessions = patterns['distraction_patterns'].get('zero_distraction_sessions', 0)
            if rate > 50:
                recommendations.append(
                    "You have distractions in most sessions. Try the Pomodoro technique (25 min focus, 5 min break)!"
                )
            elif zero_sessions > 0:
                recommendations.append(
                    f"{zero_sessions} distraction-free sessions! Try to increase this!"
                )
        
        if patterns and patterns.get('mood_productivity_correlation'):
            corr = patterns['mood_productivity_correlation']
            if corr > 0.5:
                recommendations.append(
                    "Your mood strongly affects your productivity. Study when you're in a good mood!"
                )
        
        if analysis and analysis.get('daily_patterns'):
            best_day = analysis['daily_patterns'].get('best_day')
            if best_day:
                recommendations.append(
                    f"Your best day is {best_day}. Plan important topics for this day!"
                )
        
        consistency = analysis.get('consistency', 0) if analysis else 0
        if consistency < 50:
            recommendations.append(
                "Your productivity is inconsistent. Try to maintain a regular study schedule!"
            )
        elif consistency > 80:
            recommendations.append(
                "Your productivity is very consistent! Excellent work!"
            )
        
        if not recommendations:
            recommendations.append(
                "Keep tracking your sessions for personalized recommendations!"
            )
        
        return recommendations
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_time.clear()
        logger.info("Cache cleared")