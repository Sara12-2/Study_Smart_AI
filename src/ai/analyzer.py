"""
AI Analyzer Module
Advanced data analysis with statistical methods
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from collections import defaultdict
from statistics import mean, median, stdev, mode

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
    """
    
    def __init__(self):
        """Initialize the analyzer"""
        logger.info("AIAnalyzer initialized")
    
    def prepare_dataframe(self, sessions: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert sessions to pandas DataFrame for analysis
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            DataFrame with processed data
        """
        if not sessions:
            return pd.DataFrame()
        
        df = pd.DataFrame(sessions)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['week'] = df['timestamp'].dt.isocalendar().week
            df['month'] = df['timestamp'].dt.month
        
        return df
    
    def analyze_productivity_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze productivity patterns using statistical methods
        
        Returns:
            Dictionary with pattern analysis
        """
        if df.empty:
            return {'error': 'No data available'}
        
        results = {
            'overall_stats': {},
            'daily_patterns': {},
            'weekly_patterns': {},
            'hourly_patterns': {},
            'correlations': {},
            'anomalies': []
        }
        
        # Overall statistics
        if 'productivity_score' in df.columns:
            scores = df['productivity_score']
            results['overall_stats'] = {
                'mean': round(mean(scores), 2),
                'median': round(median(scores), 2),
                'std': round(stdev(scores), 2) if len(scores) > 1 else 0,
                'min': min(scores),
                'max': max(scores),
                'q1': round(np.percentile(scores, 25), 2),
                'q3': round(np.percentile(scores, 75), 2)
            }
        
        # Daily patterns
        if 'day_of_week' in df.columns:
            daily_avg = df.groupby('day_of_week')['productivity_score'].mean()
            daily_counts = df.groupby('day_of_week').size()
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            results['daily_patterns'] = {
                'avg_productivity': {
                    day: round(daily_avg.get(i, 0), 2)
                    for i, day in enumerate(days)
                },
                'session_counts': {
                    day: int(daily_counts.get(i, 0))
                    for i, day in enumerate(days)
                },
                'best_day': days[int(daily_avg.idxmax())] if not daily_avg.empty else None,
                'worst_day': days[int(daily_avg.idxmin())] if not daily_avg.empty else None
            }
        
        # Hourly patterns
        if 'hour' in df.columns:
            hourly_avg = df.groupby('hour')['productivity_score'].mean()
            hourly_counts = df.groupby('hour').size()
            
            results['hourly_patterns'] = {
                'avg_productivity': hourly_avg.to_dict(),
                'session_counts': hourly_counts.to_dict(),
                'peak_hour': int(hourly_avg.idxmax()) if not hourly_avg.empty else None,
                'low_hour': int(hourly_avg.idxmin()) if not hourly_avg.empty else None
            }
        
        # Weekly patterns
        if 'week' in df.columns:
            weekly_avg = df.groupby('week')['productivity_score'].mean()
            results['weekly_patterns'] = {
                'avg_productivity': weekly_avg.to_dict(),
                'trend': self._calculate_trend(weekly_avg.values.tolist()) if len(weekly_avg) > 1 else 'insufficient'
            }
        
        # Correlations
        if len(df) > 5:
            correlations = {}
            
            # Duration vs Productivity
            if 'duration' in df.columns and 'productivity_score' in df.columns:
                correlations['duration_productivity'] = round(
                    df['duration'].corr(df['productivity_score']), 3
                )
            
            # Distractions vs Productivity
            if 'distractions' in df.columns and 'productivity_score' in df.columns:
                correlations['distractions_productivity'] = round(
                    df['distractions'].corr(df['productivity_score']), 3
                )
            
            # Hour vs Productivity
            if 'hour' in df.columns and 'productivity_score' in df.columns:
                correlations['hour_productivity'] = round(
                    df['hour'].corr(df['productivity_score']), 3
                )
            
            results['correlations'] = correlations
        
        # Anomaly detection (Z-score method)
        if 'productivity_score' in df.columns and len(df) > 10:
            scores = df['productivity_score']
            mean_score = mean(scores)
            std_score = stdev(scores) if len(scores) > 1 else 1
            
            # Find sessions with Z-score > 2 (unusual)
            z_scores = (scores - mean_score) / std_score
            anomalies = df[abs(z_scores) > 2]
            
            if not anomalies.empty:
                for _, row in anomalies.iterrows():
                    results['anomalies'].append({
                        'subject': row.get('subject', 'Unknown'),
                        'productivity': row.get('productivity_score', 0),
                        'timestamp': str(row.get('timestamp', '')),
                        'z_score': round(z_scores[_], 2)
                    })
        
        return results
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'insufficient'
        
        first_half = mean(values[:len(values)//2])
        second_half = mean(values[len(values)//2:])
        
        if second_half > first_half * 1.05:
            return 'improving'
        elif second_half < first_half * 0.95:
            return 'declining'
        return 'stable'
    
    def detect_learning_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect learning patterns and habits
        
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
        
        # Best learning time from hourly patterns
        if 'hour' in df.columns and 'productivity_score' in df.columns:
            hourly_avg = df.groupby('hour')['productivity_score'].mean()
            if not hourly_avg.empty:
                best_hour = hourly_avg.idxmax()
                patterns['best_learning_time'] = {
                    'hour': int(best_hour),
                    'avg_productivity': round(hourly_avg[best_hour], 2)
                }
        
        # Subject consistency
        if 'subject' in df.columns and 'productivity_score' in df.columns:
            subject_stats = df.groupby('subject')['productivity_score'].agg(['mean', 'std'])
            
            if not subject_stats.empty:
                # Most consistent (lowest std)
                most_consistent = subject_stats.loc[subject_stats['std'].idxmin()]
                patterns['most_consistent_subject'] = {
                    'subject': subject_stats['std'].idxmin(),
                    'avg': round(most_consistent['mean'], 2),
                    'std': round(most_consistent['std'], 2)
                }
                
                # Least consistent (highest std)
                least_consistent = subject_stats.loc[subject_stats['std'].idxmax()]
                patterns['least_consistent_subject'] = {
                    'subject': subject_stats['std'].idxmax(),
                    'avg': round(least_consistent['mean'], 2),
                    'std': round(least_consistent['std'], 2)
                }
        
        # Optimal session length
        if 'duration' in df.columns and 'productivity_score' in df.columns:
            # Group duration into bins
            bins = [0, 15, 30, 45, 60, 90, 120, 240]
            df['duration_bin'] = pd.cut(df['duration'], bins)
            duration_scores = df.groupby('duration_bin')['productivity_score'].mean()
            
            if not duration_scores.empty:
                best_bin = duration_scores.idxmax()
                patterns['optimal_session_length'] = {
                    'range': str(best_bin),
                    'avg_productivity': round(duration_scores[best_bin], 2)
                }
        
        # Distraction patterns
        if 'distractions' in df.columns:
            patterns['distraction_patterns'] = {
                'avg_distractions': round(df['distractions'].mean(), 2),
                'max_distractions': int(df['distractions'].max()),
                'zero_distraction_sessions': int((df['distractions'] == 0).sum()),
                'high_distraction_sessions': int((df['distractions'] > 5).sum()),
                'distraction_rate': round(
                    (df['distractions'] > 0).sum() / len(df) * 100, 2
                )
            }
        
        # Mood vs Productivity correlation
        if 'mood' in df.columns and 'productivity_score' in df.columns:
            mood_df = df[df['mood'].notna()]
            if len(mood_df) > 3:
                patterns['mood_productivity_correlation'] = round(
                    mood_df['mood'].corr(mood_df['productivity_score']), 3
                )
        
        return patterns
    
    def generate_insights(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with AI insights
        """
        df = self.prepare_dataframe(sessions)
        
        if df.empty:
            return {
                'error': 'Insufficient data',
                'message': 'Add at least 5 sessions for AI insights'
            }
        
        if len(sessions) < 5:
            return {
                'error': 'Insufficient data',
                'message': f'Add {5 - len(sessions)} more sessions for AI insights',
                'current_sessions': len(sessions)
            }
        
        try:
            patterns = self.detect_learning_patterns(df)
            analysis = self.analyze_productivity_patterns(df)
            
            insights = {
                'patterns': patterns,
                'analysis': analysis,
                'total_sessions': len(sessions),
                'ai_confidence': self._calculate_confidence(df)
            }
            
            # Add recommendations
            insights['recommendations'] = self._generate_recommendations(patterns, analysis)
            
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
        
        # Best time recommendation
        if patterns.get('best_learning_time'):
            hour = patterns['best_learning_time']['hour']
            productivity = patterns['best_learning_time']['avg_productivity']
            recommendations.append(
                f"🌟 Schedule your study sessions around {hour:02d}:00 - you're {productivity}% productive then!"
            )
        
        # Session length recommendation
        if patterns.get('optimal_session_length'):
            range_str = patterns['optimal_session_length']['range']
            productivity = patterns['optimal_session_length']['avg_productivity']
            recommendations.append(
                f"⏱️ Optimal session length: {range_str} - {productivity}% average productivity"
            )
        
        # Consistency recommendation
        if patterns.get('most_consistent_subject'):
            subject = patterns['most_consistent_subject']['subject']
            recommendations.append(
                f"📚 You're most consistent with {subject} - keep it up!"
            )
        
        # Distraction recommendation
        if patterns.get('distraction_patterns'):
            rate = patterns['distraction_patterns']['distraction_rate']
            if rate > 50:
                recommendations.append(
                    "⚠️ You have distractions in most sessions. Try the Pomodoro technique (25 min focus, 5 min break)!"
                )
            elif patterns['distraction_patterns']['zero_distraction_sessions'] > 0:
                recommendations.append(
                    f"🎯 {patterns['distraction_patterns']['zero_distraction_sessions']} distraction-free sessions! Try to increase this!"
                )
        
        # Mood recommendation
        if patterns.get('mood_productivity_correlation'):
            corr = patterns['mood_productivity_correlation']
            if corr > 0.5:
                recommendations.append(
                    "😊 Your mood strongly affects your productivity. Study when you're in a good mood!"
                )
        
        # Best day recommendation
        if analysis.get('daily_patterns'):
            best_day = analysis['daily_patterns'].get('best_day')
            if best_day:
                recommendations.append(
                    f"📅 Your best day is {best_day}. Plan important topics for this day!"
                )
        
        if not recommendations:
            recommendations.append(
                "💡 Keep tracking your sessions for personalized recommendations!"
            )
        
        return recommendations