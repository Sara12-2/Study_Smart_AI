"""
AI Analyzer Module - Advanced Statistical Analysis Engine
Version: 2.0.0
Author: Your Name
Description: Provides statistical analysis, pattern detection, and 
             recommendations for productivity data using real-time 
             statistical methods (not traditional AI/ML)
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from statistics import mean, median, stdev
from functools import wraps
import time

# Configure logging
logger = logging.getLogger(__name__)


def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug(f"{func.__name__} executed in {end-start:.3f}s")
        return result
    return wrapper


def validate_sessions(func):
    """Decorator to validate sessions data"""
    @wraps(func)
    def wrapper(self, sessions: List[Dict[str, Any]], *args, **kwargs):
        if not sessions:
            logger.warning(f"{func.__name__}: Empty sessions list")
            return self._empty_response()
        
        if not isinstance(sessions, list):
            logger.error(f"{func.__name__}: Invalid sessions type - {type(sessions)}")
            return self._empty_response()
        
        return func(self, sessions, *args, **kwargs)
    return wrapper


class AIAnalyzer:
    """
    AI-powered data analyzer with advanced statistical methods.
    
    This class provides real-time statistical analysis of productivity data
    including pattern detection, anomaly detection, and personalized 
    recommendations. All analysis is performed using statistical methods
    rather than machine learning models.
    
    Features:
        - Real-time statistical analysis
        - Pattern detection (daily, weekly, hourly)
        - Anomaly detection using Z-score
        - Correlation analysis
        - Time series trend detection
        - Performance caching
        - Personalized recommendations
    
    Attributes:
        cache_ttl (int): Cache time-to-live in minutes
        min_sessions (int): Minimum sessions required for analysis
        confidence_threshold (float): Minimum confidence for recommendations
    """
    
    def __init__(
        self, 
        cache_ttl_minutes: int = 5,
        min_sessions_for_analysis: int = 5,
        confidence_threshold: float = 0.3
    ) -> None:
        """
        Initialize the AI Analyzer.
        
        Args:
            cache_ttl_minutes: Cache time-to-live in minutes (default: 5)
            min_sessions_for_analysis: Minimum sessions required for analysis (default: 5)
            confidence_threshold: Minimum confidence for recommendations (default: 0.3)
        
        Raises:
            ValueError: If invalid parameters are provided
        """
        if cache_ttl_minutes < 1:
            raise ValueError("cache_ttl_minutes must be >= 1")
        if min_sessions_for_analysis < 3:
            raise ValueError("min_sessions_for_analysis must be >= 3")
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._min_sessions = min_sessions_for_analysis
        self._confidence_threshold = confidence_threshold
        self._feature_status = {
            'statistical_analysis': True,
            'pattern_detection': True,
            'anomaly_detection': True,
            'correlation_analysis': True,
            'time_series': True,
            'caching': True,
            'recommendations': True
        }
        
        logger.info(
            f"AIAnalyzer initialized with cache_ttl={cache_ttl_minutes}min, "
            f"min_sessions={min_sessions_for_analysis}"
        )
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response structure for invalid data"""
        return {
            'patterns': {},
            'analysis': {
                'overall_stats': {
                    'mean': 0, 'median': 0, 'std': 0, 
                    'min': 0, 'max': 0, 'q1': 0, 'q3': 0
                },
                'consistency': 0,
                'daily_patterns': {},
                'hourly_patterns': {},
                'weekly_patterns': {},
                'correlations': {},
                'anomalies': []
            },
            'total_sessions': 0,
            'ai_confidence': 0,
            'consistency': 0,
            'recommendations': ['Add at least 5 sessions to get personalized insights!'],
            'feature_status': self._feature_status
        }
    
    @log_execution_time
    def _get_cached(
        self, 
        key: str, 
        func: callable, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Get cached data or compute fresh.
        
        Args:
            key: Cache key
            func: Function to compute data
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Cached or freshly computed data
        """
        if not self._feature_status['caching']:
            return func(*args, **kwargs)
        
        if key in self._cache:
            if datetime.now() - self._cache_time[key] < self._cache_ttl:
                logger.debug(f"Cache hit for key: {key}")
                return self._cache[key]
        
        logger.debug(f"Cache miss for key: {key}")
        result = func(*args, **kwargs)
        self._cache[key] = result
        self._cache_time[key] = datetime.now()
        return result
    
    @log_execution_time
    def prepare_dataframe(
        self, 
        sessions: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Convert sessions to pandas DataFrame for analysis.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Pandas DataFrame with processed data
        
        Raises:
            ValueError: If sessions is not a valid list
        """
        if not sessions:
            return pd.DataFrame()
        
        if not all(isinstance(s, dict) for s in sessions):
            raise ValueError("All sessions must be dictionaries")
        
        try:
            df = pd.DataFrame(sessions)
            
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['timestamp'])
                df['date'] = df['timestamp'].dt.date
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['week'] = df['timestamp'].dt.isocalendar().week
                df['month'] = df['timestamp'].dt.month
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing dataframe: {e}")
            return pd.DataFrame()
    
    @log_execution_time
    def analyze_productivity_patterns(
        self, 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyze productivity patterns using statistical methods.
        
        Args:
            df: DataFrame with productivity data
        
        Returns:
            Dictionary with analysis results
        
        Raises:
            ValueError: If df is invalid
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame")
        
        if df.empty:
            return self._empty_response()['analysis']
        
        # Clean data
        df = df.copy()
        if 'productivity_score' not in df.columns:
            logger.warning("Missing productivity_score column")
            return self._empty_response()['analysis']
        
        df['productivity_score'] = pd.to_numeric(
            df['productivity_score'], 
            errors='coerce'
        )
        df = df.dropna(subset=['productivity_score'])
        
        if df.empty:
            logger.warning("No valid productivity scores after cleaning")
            return self._empty_response()['analysis']
        
        # Clip scores to valid range
        df['productivity_score'] = df['productivity_score'].clip(0, 100)
        
        # Initialize results
        results = {
            'overall_stats': self._calculate_stats(df['productivity_score']),
            'daily_patterns': {},
            'weekly_patterns': {},
            'hourly_patterns': {},
            'correlations': {},
            'anomalies': [],
            'consistency': 0
        }
        
        # Calculate patterns if enough data
        if len(df) >= 2:
            results['consistency'] = self._calculate_consistency(
                df['productivity_score']
            )
            
            if self._feature_status['pattern_detection']:
                results['daily_patterns'] = self._analyze_daily_patterns(df)
                results['weekly_patterns'] = self._analyze_weekly_patterns(df)
                results['hourly_patterns'] = self._analyze_hourly_patterns(df)
            
            if self._feature_status['correlation_analysis']:
                results['correlations'] = self._calculate_correlations(df)
            
            if self._feature_status['anomaly_detection'] and len(df) > 5:
                results['anomalies'] = self._detect_anomalies(df)
        
        return results
    
    def _calculate_stats(self, scores: pd.Series) -> Dict[str, float]:
        """Calculate statistical measures for scores"""
        scores = scores.dropna()
        if scores.empty:
            return {'mean': 0, 'median': 0, 'std': 0, 'min': 0, 'max': 0, 'q1': 0, 'q3': 0}
        
        return {
            'mean': round(float(scores.mean()), 2),
            'median': round(float(scores.median()), 2),
            'std': round(float(scores.std()), 2) if len(scores) > 1 else 0,
            'min': float(scores.min()),
            'max': float(scores.max()),
            'q1': round(float(scores.quantile(0.25)), 2) if len(scores) > 1 else 0,
            'q3': round(float(scores.quantile(0.75)), 2) if len(scores) > 1 else 0
        }
    
    def _calculate_consistency(self, scores: pd.Series) -> float:
        """Calculate consistency score (0-100)"""
        scores = scores.dropna()
        if len(scores) < 2:
            return 100
        
        mean_score = scores.mean()
        if mean_score == 0:
            return 0
        
        cv = (scores.std() / mean_score) * 100
        return round(max(0, min(100, 100 - cv)), 2)
    
    def _analyze_daily_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze daily patterns"""
        if 'day_of_week' not in df.columns:
            return {}
        
        daily_avg = df.groupby('day_of_week')['productivity_score'].mean()
        daily_counts = df.groupby('day_of_week').size()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        result = {
            'avg_productivity': {
                day: round(float(daily_avg.get(i, 0)), 2)
                for i, day in enumerate(days)
            },
            'session_counts': {
                day: int(daily_counts.get(i, 0))
                for i, day in enumerate(days)
            }
        }
        
        if not daily_avg.empty:
            max_idx = daily_avg.idxmax()
            min_idx = daily_avg.idxmin()
            result['best_day'] = days[max_idx] if not pd.isna(max_idx) else None
            result['worst_day'] = days[min_idx] if not pd.isna(min_idx) else None
        
        return result
    
    def _analyze_weekly_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze weekly patterns"""
        if 'week' not in df.columns:
            return {}
        
        weekly_avg = df.groupby('week')['productivity_score'].mean()
        
        return {
            'avg_productivity': {
                int(k): round(float(v), 2) 
                for k, v in weekly_avg.to_dict().items()
            },
            'trend': self._calculate_trend(weekly_avg.values.tolist()) 
            if len(weekly_avg) > 1 else 'insufficient'
        }
    
    def _analyze_hourly_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze hourly patterns"""
        if 'hour' not in df.columns:
            return {}
        
        hourly_avg = df.groupby('hour')['productivity_score'].mean()
        hourly_counts = df.groupby('hour').size()
        
        result = {
            'avg_productivity': {
                int(k): round(float(v), 2) 
                for k, v in hourly_avg.to_dict().items()
            },
            'session_counts': {
                int(k): int(v) 
                for k, v in hourly_counts.to_dict().items()
            }
        }
        
        if not hourly_avg.empty:
            max_hour = hourly_avg.idxmax()
            min_hour = hourly_avg.idxmin()
            result['peak_hour'] = int(max_hour) if not pd.isna(max_hour) else None
            result['low_hour'] = int(min_hour) if not pd.isna(min_hour) else None
        
        return result
    
    def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate correlations between variables"""
        correlations = {}
        
        if len(df) < 5:
            return correlations
        
        score_col = 'productivity_score'
        
        for col in ['duration', 'distractions', 'hour']:
            if col in df.columns:
                corr = df[col].corr(df[score_col])
                if not pd.isna(corr) and not np.isnan(corr):
                    correlations[f'{col}_productivity'] = round(float(corr), 3)
        
        return correlations
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score method"""
        scores = df['productivity_score']
        mean_score = scores.mean()
        std_score = scores.std()
        
        if std_score == 0:
            return []
        
        z_scores = (scores - mean_score) / std_score
        anomalies = df[abs(z_scores) > 2]
        
        result = []
        for idx, row in anomalies.iterrows():
            result.append({
                'subject': row.get('subject', 'Unknown'),
                'productivity': float(row['productivity_score']),
                'timestamp': str(row.get('timestamp', '')),
                'z_score': round(float(z_scores[idx]), 2)
            })
        
        return result
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'insufficient'
        
        clean_values = [v for v in values if not pd.isna(v) and not np.isnan(v)]
        if len(clean_values) < 2:
            return 'insufficient'
        
        mid = len(clean_values) // 2
        first_half = mean(clean_values[:mid])
        second_half = mean(clean_values[mid:])
        
        if second_half > first_half * 1.05:
            return 'improving'
        elif second_half < first_half * 0.95:
            return 'declining'
        return 'stable'
    
    @log_execution_time
    def detect_learning_patterns(
        self, 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Detect learning patterns and habits from session data.
        
        Args:
            df: DataFrame with session data
        
        Returns:
            Dictionary with learning pattern analysis
        """
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
        
        # Clean data
        df = df.copy()
        df['productivity_score'] = pd.to_numeric(
            df['productivity_score'], 
            errors='coerce'
        )
        df = df.dropna(subset=['productivity_score'])
        
        if df.empty:
            return patterns
        
        # Find best learning time
        if 'hour' in df.columns:
            hourly_avg = df.groupby('hour')['productivity_score'].mean()
            if not hourly_avg.empty:
                best_hour = hourly_avg.idxmax()
                if not pd.isna(best_hour):
                    patterns['best_learning_time'] = {
                        'hour': int(best_hour),
                        'avg_productivity': round(float(hourly_avg[best_hour]), 2)
                    }
        
        # Find subject consistency
        if 'subject' in df.columns:
            subject_stats = df.groupby('subject')['productivity_score'].agg(['mean', 'std'])
            subject_stats = subject_stats.dropna()
            
            if not subject_stats.empty:
                most_consistent = subject_stats.loc[subject_stats['std'].idxmin()]
                if not pd.isna(most_consistent['mean']):
                    patterns['most_consistent_subject'] = {
                        'subject': subject_stats['std'].idxmin(),
                        'avg': round(float(most_consistent['mean']), 2),
                        'std': round(float(most_consistent['std']), 2)
                    }
                
                least_consistent = subject_stats.loc[subject_stats['std'].idxmax()]
                if not pd.isna(least_consistent['mean']):
                    patterns['least_consistent_subject'] = {
                        'subject': subject_stats['std'].idxmax(),
                        'avg': round(float(least_consistent['mean']), 2),
                        'std': round(float(least_consistent['std']), 2)
                    }
        
        # Find optimal session length
        if 'duration' in df.columns:
            bins = [0, 15, 30, 45, 60, 90, 120, 240]
            df['duration_bin'] = pd.cut(df['duration'], bins)
            duration_scores = df.groupby('duration_bin')['productivity_score'].mean()
            duration_scores = duration_scores.dropna()
            
            if not duration_scores.empty:
                best_bin = duration_scores.idxmax()
                if not pd.isna(best_bin):
                    patterns['optimal_session_length'] = {
                        'range': str(best_bin),
                        'avg_productivity': round(float(duration_scores[best_bin]), 2)
                    }
        
        # Analyze distractions
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
        
        # Analyze mood correlation
        if 'mood' in df.columns:
            mood_df = df[df['mood'].notna()]
            if len(mood_df) > 3:
                corr = mood_df['mood'].corr(mood_df['productivity_score'])
                if not pd.isna(corr) and not np.isnan(corr):
                    patterns['mood_productivity_correlation'] = round(float(corr), 3)
        
        return patterns
    
    @log_execution_time
    @validate_sessions
    def generate_insights(
        self, 
        sessions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights from session data.
        
        This is the main entry point for analysis. It processes session data
        and returns comprehensive insights including patterns, statistics,
        and recommendations.
        
        Args:
            sessions: List of session dictionaries with productivity data
        
        Returns:
            Dictionary containing:
                - patterns: Learning patterns
                - analysis: Statistical analysis
                - total_sessions: Number of valid sessions
                - ai_confidence: Confidence score (0-100)
                - consistency: Consistency score (0-100)
                - recommendations: List of personalized recommendations
                - feature_status: Status of all features
        
        Raises:
            ValueError: If sessions is not a valid list
        """
        if not sessions:
            return self._empty_response()
        
        try:
            # Validate and clean sessions
            valid_sessions = self._clean_sessions(sessions)
            
            if len(valid_sessions) < self._min_sessions:
                return self._empty_response()
            
            # Prepare data
            df = self.prepare_dataframe(valid_sessions)
            
            if df.empty:
                return self._empty_response()
            
            # Generate insights
            patterns = self.detect_learning_patterns(df)
            analysis = self.analyze_productivity_patterns(df)
            
            # Clean results
            patterns = self._clean_nan(patterns)
            analysis = self._clean_nan(analysis)
            
            # Calculate confidence
            confidence = self._calculate_confidence(df)
            consistency = analysis.get('consistency', 0)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                patterns, 
                analysis,
                confidence
            )
            
            return {
                'patterns': patterns,
                'analysis': analysis,
                'total_sessions': len(valid_sessions),
                'ai_confidence': confidence,
                'consistency': consistency,
                'recommendations': recommendations,
                'feature_status': self._feature_status,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}", exc_info=True)
            return self._empty_response()
    
    def _clean_sessions(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate sessions data"""
        valid_sessions = []
        
        for s in sessions:
            if not isinstance(s, dict):
                continue
            
            score = s.get('productivity_score')
            if score is None:
                continue
            
            try:
                score_float = float(score)
                if pd.isna(score_float) or np.isnan(score_float):
                    continue
                
                # Clean and clip score
                s['productivity_score'] = max(0, min(100, score_float))
                valid_sessions.append(s)
                
            except (ValueError, TypeError):
                continue
        
        return valid_sessions
    
    def _clean_nan(self, obj: Any) -> Any:
        """Recursively clean NaN values from objects"""
        if isinstance(obj, dict):
            return {k: self._clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_nan(v) for v in obj]
        elif isinstance(obj, float):
            if pd.isna(obj) or np.isnan(obj):
                return 0
            return obj
        elif isinstance(obj, (int, str, bool)):
            return obj
        elif obj is None:
            return 0
        else:
            return 0
    
    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """
        Calculate AI confidence score based on data quality and quantity.
        
        Args:
            df: DataFrame with session data
        
        Returns:
            Confidence score (0-100)
        """
        n = len(df)
        
        if n < self._min_sessions:
            return 0
        elif n < 10:
            return round(30 + (n - 5) * 6, 2)
        elif n < 20:
            return round(60 + (n - 10) * 2, 2)
        elif n < 50:
            return round(80 + (n - 20) * 0.5, 2)
        else:
            return min(95, 85 + (n - 50) * 0.2)
    
    def _generate_recommendations(
        self, 
        patterns: Dict[str, Any], 
        analysis: Dict[str, Any],
        confidence: float
    ) -> List[str]:
        """
        Generate personalized recommendations based on analysis.
        
        Args:
            patterns: Pattern analysis results
            analysis: Statistical analysis results
            confidence: Confidence score
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check if we have enough confidence
        if confidence < self._confidence_threshold * 100:
            return ['📊 Add more sessions for better insights!']
        
        # Time-based recommendations
        if patterns.get('best_learning_time'):
            hour = patterns['best_learning_time']['hour']
            productivity = patterns['best_learning_time']['avg_productivity']
            recommendations.append(
                f"⏰ Schedule your study sessions around {hour:02d}:00 - "
                f"you're {productivity}% productive then!"
            )
        
        # Session length recommendations
        if patterns.get('optimal_session_length'):
            range_str = patterns['optimal_session_length']['range']
            productivity = patterns['optimal_session_length']['avg_productivity']
            recommendations.append(
                f"📚 Optimal session length: {range_str} - "
                f"{productivity}% average productivity"
            )
        
        # Subject-based recommendations
        if patterns.get('most_consistent_subject'):
            subject = patterns['most_consistent_subject']['subject']
            recommendations.append(
                f"📖 You're most consistent with {subject} - keep it up!"
            )
        
        if patterns.get('least_consistent_subject'):
            subject = patterns['least_consistent_subject']['subject']
            recommendations.append(
                f"⚠️ You're least consistent with {subject}. "
                "Try breaking it into shorter sessions!"
            )
        
        # Distraction recommendations
        if patterns.get('distraction_patterns'):
            rate = patterns['distraction_patterns'].get('distraction_rate', 0)
            zero_sessions = patterns['distraction_patterns'].get('zero_distraction_sessions', 0)
            
            if rate > 50:
                recommendations.append(
                    "🧘 You have distractions in most sessions. "
                    "Try the Pomodoro technique (25 min focus, 5 min break)!"
                )
            elif zero_sessions > 0:
                recommendations.append(
                    f"🎯 {zero_sessions} distraction-free sessions! "
                    "Try to increase this!"
                )
        
        # Mood recommendations
        if patterns.get('mood_productivity_correlation'):
            corr = patterns['mood_productivity_correlation']
            if corr > 0.5:
                recommendations.append(
                    "😊 Your mood strongly affects your productivity. "
                    "Study when you're in a good mood!"
                )
            elif corr < -0.3:
                recommendations.append(
                    "🤔 Your mood seems to inversely affect productivity. "
                    "Try studying regardless of mood!"
                )
        
        # Day-based recommendations
        if analysis.get('daily_patterns'):
            best_day = analysis['daily_patterns'].get('best_day')
            if best_day:
                recommendations.append(
                    f"📅 Your best day is {best_day}. "
                    "Plan important topics for this day!"
                )
        
        # Consistency recommendations
        consistency = analysis.get('consistency', 0)
        if consistency < 50:
            recommendations.append(
                "📈 Your productivity is inconsistent. "
                "Try to maintain a regular study schedule!"
            )
        elif consistency > 80:
            recommendations.append(
                "🌟 Your productivity is very consistent! Excellent work!"
            )
        
        # Fallback recommendation
        if not recommendations:
            recommendations.append(
                "💡 Keep tracking your sessions for personalized recommendations!"
            )
        
        return recommendations
    
    @log_execution_time
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_time.clear()
        logger.info("Cache cleared")
    
    def get_feature_status(self) -> Dict[str, bool]:
        """
        Get status of all features.
        
        Returns:
            Dictionary with feature status
        """
        return self._feature_status.copy()
    
    def toggle_feature(self, feature_name: str, enabled: bool) -> bool:
        """
        Enable or disable a specific feature.
        
        Args:
            feature_name: Name of the feature
            enabled: True to enable, False to disable
        
        Returns:
            True if feature was toggled, False if feature doesn't exist
        
        Raises:
            KeyError: If feature doesn't exist
        """
        if feature_name in self._feature_status:
            self._feature_status[feature_name] = enabled
            logger.info(f"Feature {feature_name} {'enabled' if enabled else 'disabled'}")
            return True
        else:
            logger.warning(f"Feature {feature_name} not found")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get analyzer statistics.
        
        Returns:
            Dictionary with analyzer statistics
        """
        return {
            'cache_size': len(self._cache),
            'cache_ttl_minutes': self._cache_ttl.total_seconds() / 60,
            'min_sessions_required': self._min_sessions,
            'confidence_threshold': self._confidence_threshold,
            'feature_status': self._feature_status
        }