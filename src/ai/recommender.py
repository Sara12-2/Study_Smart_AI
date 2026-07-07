"""
AI Recommender Module - Personalized Recommendation Engine
Version: 2.0.0
Author: Your Name
Description: Provides personalized recommendations, study tips, and 
             progress tracking based on productivity session data.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
import time
import json

# Configure logging
logger = logging.getLogger(__name__)


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to decorate
    
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug(f"{func.__name__} executed in {end-start:.3f}s")
        return result
    return wrapper


def validate_sessions(min_count: int = 3):
    """
    Decorator to validate session data.
    
    Args:
        min_count: Minimum number of sessions required
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, sessions: List[Dict[str, Any]], *args, **kwargs):
            if not sessions:
                logger.warning(f"{func.__name__}: Empty sessions list")
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    'No sessions provided for recommendations'
                )
            
            if not isinstance(sessions, list):
                logger.error(f"{func.__name__}: Invalid sessions type - {type(sessions)}")
                return self._error_response(
                    'INVALID_INPUT',
                    f'Sessions must be a list, got {type(sessions).__name__}'
                )
            
            if not all(isinstance(s, dict) for s in sessions):
                return self._error_response(
                    'INVALID_INPUT',
                    'All sessions must be dictionaries'
                )
            
            if len(sessions) < min_count:
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    f'Need at least {min_count} sessions for recommendations, have {len(sessions)}'
                )
            
            return func(self, sessions, *args, **kwargs)
        return wrapper
    return decorator


class AIRecommender:
    """
    AI-powered recommendation engine for personalized learning suggestions.
    
    This class provides personalized recommendations, study tips, and
    progress tracking based on analysis of session data. Recommendations
    are generated using statistical analysis of productivity patterns.
    
    Features:
        - Personalized recommendations
        - Actionable suggestions
        - Progress tracking
        - Smart alerts
        - Study tips
        - Motivational messages
        
    Attributes:
        min_sessions (int): Minimum sessions for recommendations
        high_distraction_threshold (int): Threshold for high distraction
        moderate_distraction_threshold (int): Threshold for moderate distraction
        perfect_distraction_threshold (int): Threshold for perfect focus
        low_consistency_threshold (float): Threshold for low consistency
        high_consistency_threshold (float): Threshold for high consistency
        long_session_threshold (int): Threshold for long sessions
        cache_ttl (timedelta): Cache time-to-live
        feature_status (Dict): Status of all features
    """
    
    def __init__(
        self,
        min_sessions: int = 5,
        high_distraction_threshold: int = 5,
        moderate_distraction_threshold: int = 3,
        perfect_distraction_threshold: int = 1,
        low_consistency_threshold: float = 1.5,
        high_consistency_threshold: float = 3.0,
        long_session_threshold: int = 120,
        cache_ttl_minutes: int = 5
    ) -> None:
        """
        Initialize the AI Recommender.
        
        Args:
            min_sessions: Minimum sessions required for recommendations (default: 5)
            high_distraction_threshold: Threshold for high distraction (default: 5)
            moderate_distraction_threshold: Threshold for moderate distraction (default: 3)
            perfect_distraction_threshold: Threshold for perfect focus (default: 1)
            low_consistency_threshold: Threshold for low consistency (default: 1.5)
            high_consistency_threshold: Threshold for high consistency (default: 3.0)
            long_session_threshold: Threshold for long sessions in minutes (default: 120)
            cache_ttl_minutes: Cache time-to-live in minutes (default: 5)
        
        Raises:
            ValueError: If invalid parameters are provided
        """
        if min_sessions < 3:
            raise ValueError("min_sessions must be >= 3")
        if high_distraction_threshold < 0:
            raise ValueError("high_distraction_threshold must be >= 0")
        if moderate_distraction_threshold < 0:
            raise ValueError("moderate_distraction_threshold must be >= 0")
        if perfect_distraction_threshold < 0:
            raise ValueError("perfect_distraction_threshold must be >= 0")
        if low_consistency_threshold < 0:
            raise ValueError("low_consistency_threshold must be >= 0")
        if high_consistency_threshold <= low_consistency_threshold:
            raise ValueError("high_consistency_threshold must be > low_consistency_threshold")
        if long_session_threshold < 30:
            raise ValueError("long_session_threshold must be >= 30")
        
        self.min_sessions = min_sessions
        self.high_distraction_threshold = high_distraction_threshold
        self.moderate_distraction_threshold = moderate_distraction_threshold
        self.perfect_distraction_threshold = perfect_distraction_threshold
        self.low_consistency_threshold = low_consistency_threshold
        self.high_consistency_threshold = high_consistency_threshold
        self.long_session_threshold = long_session_threshold
        
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=cache_ttl_minutes)
        
        self.feature_status = {
            'distraction_recommendations': True,
            'subject_recommendations': True,
            'time_recommendations': True,
            'consistency_recommendations': True,
            'break_recommendations': True,
            'motivational_messages': True,
            'study_tips': True,
            'progress_tracking': True,
            'caching': True
        }
        
        # Priority order for recommendations
        self._priority_order = {
            'critical': 1,
            'warning': 2,
            'info': 3,
            'success': 4
        }
        
        logger.info(
            f"AIRecommender initialized with min_sessions={min_sessions}, "
            f"distraction_thresholds=({high_distraction_threshold}, {moderate_distraction_threshold}, {perfect_distraction_threshold})"
        )
    
    def _error_response(self, error_type: str, message: str) -> Dict[str, Any]:
        """
        Generate standardized error response.
        
        Args:
            error_type: Type of error
            message: Human-readable error message
        
        Returns:
            Dictionary with error details
        """
        return {
            'success': False,
            'error': error_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'feature_status': self.feature_status
        }
    
    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate standardized success response.
        
        Args:
            data: Response data
        
        Returns:
            Dictionary with success response
        """
        return {
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'feature_status': self.feature_status
        }
    
    @log_execution_time
    def _get_cached(self, key: str, func: Callable, *args, **kwargs) -> Any:
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
        if not self.feature_status['caching']:
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
    
    def _safe_parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """
        Safely parse timestamp with multiple formats.
        
        Args:
            timestamp: Timestamp string or object
        
        Returns:
            Datetime object or None if parsing fails
        """
        if not timestamp:
            return None
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S.%f'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(timestamp), fmt)
            except (ValueError, TypeError):
                continue
        
        try:
            return datetime.fromisoformat(str(timestamp))
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _extract_scores(self, sessions: List[Dict[str, Any]]) -> List[float]:
        """
        Extract and clean productivity scores from sessions.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            List of valid productivity scores
        """
        scores = []
        for s in sessions:
            score = s.get('productivity_score')
            if score is not None:
                try:
                    score_float = float(score)
                    if not np.isnan(score_float):
                        scores.append(max(0, min(100, score_float)))
                except (ValueError, TypeError):
                    continue
        return scores
    
    @validate_sessions(min_count=3)
    @log_execution_time
    def get_recommendations(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate personalized recommendations.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with recommendations list
        
        Example:
            >>> recommender = AIRecommender()
            >>> result = recommender.get_recommendations(sessions)
            >>> for rec in result['data']['recommendations']:
            ...     print(rec['title'])
        """
        cache_key = f"recommendations_{len(sessions)}_{id(sessions)}"
        
        if self.feature_status['caching']:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        
        try:
            recommendations = []
            
            # Generate recommendations by type
            if self.feature_status['distraction_recommendations']:
                dist_rec = self._recommend_distractions(sessions)
                if dist_rec:
                    recommendations.append(dist_rec)
            
            if self.feature_status['subject_recommendations']:
                subj_rec = self._recommend_subjects(sessions)
                if subj_rec:
                    recommendations.append(subj_rec)
            
            if self.feature_status['time_recommendations']:
                time_rec = self._recommend_time(sessions)
                if time_rec:
                    recommendations.append(time_rec)
            
            if self.feature_status['consistency_recommendations']:
                cons_rec = self._recommend_consistency(sessions)
                if cons_rec:
                    recommendations.append(cons_rec)
            
            if self.feature_status['break_recommendations']:
                break_rec = self._recommend_breaks(sessions)
                if break_rec:
                    recommendations.append(break_rec)
            
            # Sort by priority
            recommendations.sort(
                key=lambda x: self._priority_order.get(x.get('priority', 'info'), 3)
            )
            
            # Add default recommendation if none
            if not recommendations:
                recommendations.append({
                    'type': 'info',
                    'priority': 'info',
                    'title': '💡 Keep Going',
                    'description': 'You\'re doing great! Keep tracking to unlock more insights.',
                    'action': 'Continue your learning journey'
                })
            
            result = {
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'generated_at': datetime.now().isoformat()
            }
            
            response = self._success_response(result)
            
            if self.feature_status['caching']:
                self._cache[cache_key] = response
                self._cache_time[cache_key] = datetime.now()
            
            return response
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}", exc_info=True)
            return self._error_response('RECOMMENDATION_ERROR', str(e))
    
    def _recommend_distractions(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """
        Generate distraction-based recommendations.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Recommendation dictionary or None
        """
        recent = sessions[-10:] if len(sessions) > 10 else sessions
        distractions = [s.get('distractions', 0) for s in recent]
        avg_dist = sum(distractions) / len(distractions) if distractions else 0
        
        if avg_dist > self.high_distraction_threshold:
            return {
                'type': 'warning',
                'priority': 'warning',
                'title': '⚠️ High Distractions Detected',
                'description': f'You average {round(avg_dist, 1)} distractions per session. This is affecting your focus!',
                'action': '🎯 Try the Pomodoro technique: 25 min focus → 5 min break → Repeat',
                'icon': '⚠️'
            }
        elif avg_dist > self.moderate_distraction_threshold:
            return {
                'type': 'info',
                'priority': 'info',
                'title': '📊 Moderate Distractions',
                'description': f'You average {round(avg_dist, 1)} distractions. Try to reduce by 1 per session.',
                'action': '🎯 Aim for 3 or fewer distractions per session',
                'icon': '📊'
            }
        elif avg_dist < self.perfect_distraction_threshold and len(recent) >= 5:
            return {
                'type': 'success',
                'priority': 'success',
                'title': '🎯 Excellent Focus!',
                'description': 'You have minimal distractions! This is excellent for deep learning.',
                'action': '💪 Maintain this focus level for best results',
                'icon': '🎯'
            }
        return None
    
    def _recommend_subjects(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """
        Generate subject-based recommendations.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Recommendation dictionary or None
        """
        if len(sessions) < 5:
            return None
        
        subject_scores = defaultdict(list)
        for s in sessions:
            subject = s.get('subject', 'Unknown')
            score = s.get('productivity_score', 0)
            if score is not None:
                try:
                    score_float = float(score)
                    if not np.isnan(score_float):
                        subject_scores[subject].append(max(0, min(100, score_float)))
                except (ValueError, TypeError):
                    continue
        
        if len(subject_scores) < 2:
            return {
                'type': 'info',
                'priority': 'info',
                'title': '📚 Diversify Your Subjects',
                'description': 'You\'re focusing on only one subject. Try diversifying your learning!',
                'action': 'Add 1-2 new subjects to your study routine',
                'icon': '📚'
            }
        
        subject_avg = {
            subj: sum(scores) / len(scores)
            for subj, scores in subject_scores.items()
            if scores
        }
        
        if not subject_avg:
            return None
        
        best = max(subject_avg.items(), key=lambda x: x[1])
        worst = min(subject_avg.items(), key=lambda x: x[1])
        
        if best[0] != worst[0] and abs(best[1] - worst[1]) > 10:
            return {
                'type': 'info',
                'priority': 'info',
                'title': '📊 Subject Performance Gap',
                'description': f'You\'re best at {best[0]} ({round(best[1], 1)}%) but need improvement in {worst[0]} ({round(worst[1], 1)}%).',
                'action': f'📖 Dedicate 30% more time to {worst[0]} this week',
                'icon': '📊'
            }
        return None
    
    def _recommend_time(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """
        Generate time-based recommendations.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Recommendation dictionary or None
        """
        if len(sessions) < 7:
            return None
        
        hour_scores = defaultdict(list)
        for s in sessions:
            timestamp = s.get('timestamp')
            score = s.get('productivity_score')
            if timestamp and score is not None:
                date = self._safe_parse_timestamp(timestamp)
                if date:
                    try:
                        score_float = float(score)
                        if not np.isnan(score_float):
                            hour = date.hour
                            hour_scores[hour].append(max(0, min(100, score_float)))
                    except (ValueError, TypeError):
                        continue
        
        if not hour_scores:
            return None
        
        best_hour = max(
            hour_scores.items(),
            key=lambda x: sum(x[1]) / len(x[1])
        )
        avg_productivity = sum(best_hour[1]) / len(best_hour[1])
        
        return {
            'type': 'success',
            'priority': 'success',
            'title': '🕐 Your Optimal Study Time',
            'description': f'Your best study time is {best_hour[0]:02d}:00 with {round(avg_productivity, 1)}% productivity.',
            'action': f'⏰ Schedule your hardest subjects at {best_hour[0]:02d}:00',
            'icon': '🕐'
        }
    
    def _recommend_consistency(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """
        Generate consistency-based recommendations.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Recommendation dictionary or None
        """
        if len(sessions) < 10:
            return None
        
        daily_sessions = defaultdict(int)
        for s in sessions:
            timestamp = s.get('timestamp')
            if timestamp:
                date = self._safe_parse_timestamp(timestamp)
                if date:
                    daily_sessions[date.date()] += 1
        
        if not daily_sessions:
            return None
        
        days = len(daily_sessions)
        avg = len(sessions) / days if days > 0 else 0
        
        if avg < self.low_consistency_threshold:
            return {
                'type': 'warning',
                'priority': 'warning',
                'title': '📅 Inconsistent Study Pattern',
                'description': f'You study only {round(avg, 1)} sessions per day. Consistency is key for learning!',
                'action': '🎯 Aim for at least 2 sessions per day, 5 days a week',
                'icon': '📅'
            }
        elif avg >= self.high_consistency_threshold:
            return {
                'type': 'success',
                'priority': 'success',
                'title': '🔥 Excellent Consistency!',
                'description': f'You study {round(avg, 1)} sessions per day. This is outstanding!',
                'action': '💪 Keep up this great habit!',
                'icon': '🔥'
            }
        return None
    
    def _recommend_breaks(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """
        Generate break recommendations.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Recommendation dictionary or None
        """
        if len(sessions) < 5:
            return None
        
        long_sessions = [
            s for s in sessions 
            if s.get('duration', 0) and int(s.get('duration', 0)) > self.long_session_threshold
        ]
        
        if long_sessions:
            return {
                'type': 'info',
                'priority': 'info',
                'title': '⏰ Take Regular Breaks',
                'description': f'You have {len(long_sessions)} sessions over {self.long_session_threshold} minutes. Long sessions can reduce focus.',
                'action': '🧘 Take a 10-minute break every 45-60 minutes',
                'icon': '⏰'
            }
        return None
    
    @validate_sessions(min_count=1)
    @log_execution_time
    def get_motivational_messages(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get motivational messages based on session data.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with motivational messages
        
        Example:
            >>> recommender = AIRecommender()
            >>> result = recommender.get_motivational_messages(sessions)
            >>> for msg in result['data']['messages']:
            ...     print(msg)
        """
        cache_key = f"motivational_{len(sessions)}_{id(sessions)}"
        
        if self.feature_status['caching']:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        
        try:
            messages = self._generate_motivational_messages(sessions)
            result = {
                'messages': messages,
                'count': len(messages),
                'generated_at': datetime.now().isoformat()
            }
            
            response = self._success_response(result)
            
            if self.feature_status['caching']:
                self._cache[cache_key] = response
                self._cache_time[cache_key] = datetime.now()
            
            return response
            
        except Exception as e:
            logger.error(f"Motivational messages error: {e}", exc_info=True)
            return self._error_response('MOTIVATIONAL_ERROR', str(e))
    
    def _generate_motivational_messages(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """
        Internal method to generate motivational messages.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            List of motivational messages
        """
        messages = []
        
        if not sessions:
            messages.append("🌟 Start your learning journey today!")
            return messages
        
        # Total study time
        total_time = 0
        for s in sessions:
            duration = s.get('duration', 0)
            if duration is not None:
                try:
                    total_time += float(duration)
                except (ValueError, TypeError):
                    continue
        
        hours = total_time / 60
        
        if hours >= 10:
            messages.append(f"🚀 You've studied {round(hours, 1)} hours! Incredible dedication!")
        elif hours >= 5:
            messages.append(f"📚 {round(hours, 1)} hours studied! Keep building momentum!")
        elif hours >= 2:
            messages.append(f"💪 {round(hours, 1)} hours of learning! Every minute counts!")
        else:
            messages.append("🌟 Every journey starts with a single step. Keep going!")
        
        # Session count
        if len(sessions) >= 5:
            messages.append("🔥 You're building a learning streak! Stay consistent!")
        
        # Productivity improvement
        if len(sessions) >= 10:
            scores = self._extract_scores(sessions)
            if len(scores) >= 10:
                recent_avg = sum(scores[-5:]) / 5
                overall_avg = sum(scores) / len(scores)
                if recent_avg > overall_avg:
                    messages.append("📈 You're improving! Your recent sessions are better than average!")
        
        if len(messages) == 1 and "Start your learning journey" in messages[0]:
            messages.append("💡 Track at least 5 sessions for personalized motivation!")
        
        return messages
    
    @validate_sessions(min_count=3)
    @log_execution_time
    def get_study_tips(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate general study tips based on session data.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with study tips
        
        Example:
            >>> recommender = AIRecommender()
            >>> result = recommender.get_study_tips(sessions)
            >>> for tip in result['data']['tips']:
            ...     print(tip)
        """
        try:
            tips = []
            
            # Check for optimal session length
            durations = []
            for s in sessions:
                duration = s.get('duration', 0)
                if duration is not None:
                    try:
                        durations.append(float(duration))
                    except (ValueError, TypeError):
                        continue
            
            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > 90:
                    tips.append("⏱️ Your sessions are longer than 90 minutes on average. Consider taking breaks every 45-60 minutes to maintain focus.")
                elif avg_duration < 25:
                    tips.append("⏱️ Your sessions are short. Try extending them to 30-60 minutes for better focus and deeper learning.")
            
            # Check for subject variety
            subjects = list(set(
                s.get('subject', '') for s in sessions if s.get('subject')
            ))
            
            if len(subjects) < 2:
                tips.append("📚 You're focusing on only one subject. Try diversifying your study topics to broaden your knowledge!")
            
            # Check for consistency
            if len(sessions) > 5:
                dates = set()
                for s in sessions:
                    timestamp = s.get('timestamp')
                    if timestamp:
                        date = self._safe_parse_timestamp(timestamp)
                        if date:
                            dates.add(date.date())
                
                if dates and len(dates) < len(sessions) * 0.5:
                    tips.append("📅 You have multiple sessions on some days. Try to spread your study throughout the week for better retention.")
            
            # Check for optimal session time
            if len(sessions) >= 7:
                hour_counts = defaultdict(int)
                for s in sessions:
                    timestamp = s.get('timestamp')
                    if timestamp:
                        date = self._safe_parse_timestamp(timestamp)
                        if date:
                            hour_counts[date.hour] += 1
                
                if hour_counts:
                    peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
                    tips.append(f"🕐 You study most often at {peak_hour:02d}:00. Try to schedule important topics at this time!")
            
            if not tips:
                tips.append("🌟 You're doing great! Keep up your current study habits!")
            
            result = {
                'tips': tips,
                'count': len(tips),
                'generated_at': datetime.now().isoformat()
            }
            
            return self._success_response(result)
            
        except Exception as e:
            logger.error(f"Study tips generation error: {e}", exc_info=True)
            return self._error_response('TIP_GENERATION_ERROR', str(e))
    
    @validate_sessions(min_count=10)
    @log_execution_time
    def get_recommendation_progress(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Track progress on recommendations.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with progress metrics
        
        Example:
            >>> recommender = AIRecommender()
            >>> result = recommender.get_recommendation_progress(sessions)
            >>> print(result['data']['distractions']['improvement'])
            15.5
        """
        try:
            if len(sessions) < 10:
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    f'Need at least 10 sessions for progress tracking, have {len(sessions)}'
                )
            
            recent = sessions[-5:] if len(sessions) > 5 else sessions
            older = sessions[:-5] if len(sessions) > 5 else []
            
            progress = {}
            
            # Distraction progress
            if recent:
                recent_dist = [s.get('distractions', 0) for s in recent if s.get('distractions') is not None]
                older_dist = [s.get('distractions', 0) for s in older if s.get('distractions') is not None] if older else recent_dist
                
                if recent_dist:
                    recent_avg = sum(recent_dist) / len(recent_dist)
                    older_avg = sum(older_dist) / len(older_dist) if older_dist else recent_avg
                    
                    improvement = ((older_avg - recent_avg) / max(older_avg, 1)) * 100
                    progress['distractions'] = {
                        'improvement': round(improvement, 2),
                        'current_avg': round(recent_avg, 2),
                        'previous_avg': round(older_avg, 2),
                        'status': 'improving' if recent_avg < older_avg else 'declining' if recent_avg > older_avg else 'stable',
                        'trend_emoji': '📈' if recent_avg < older_avg else '📉' if recent_avg > older_avg else '➡️'
                    }
            
            # Productivity progress
            if recent:
                recent_scores = self._extract_scores(recent)
                older_scores = self._extract_scores(older) if older else recent_scores
                
                if recent_scores and older_scores:
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    older_avg = sum(older_scores) / len(older_scores)
                    
                    improvement = ((recent_avg - older_avg) / max(older_avg, 1)) * 100
                    progress['productivity'] = {
                        'improvement': round(improvement, 2),
                        'current_avg': round(recent_avg, 2),
                        'previous_avg': round(older_avg, 2),
                        'status': 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable',
                        'trend_emoji': '📈' if recent_avg > older_avg else '📉' if recent_avg < older_avg else '➡️'
                    }
            
            # Overall progress summary
            summary = []
            if 'distractions' in progress:
                status = progress['distractions']['status']
                if status == 'improving':
                    summary.append("✅ Distractions are decreasing - Great job!")
                elif status == 'declining':
                    summary.append("⚠️ Distractions are increasing - Focus on reducing them!")
                else:
                    summary.append("➡️ Distractions are stable - Keep working on improvement!")
            
            if 'productivity' in progress:
                status = progress['productivity']['status']
                if status == 'improving':
                    summary.append("📈 Productivity is improving - Excellent work!")
                elif status == 'declining':
                    summary.append("📉 Productivity is declining - Review your study habits!")
                else:
                    summary.append("➡️ Productivity is stable - Maintain your routine!")
            
            result = {
                'progress': progress,
                'summary': summary,
                'total_sessions': len(sessions),
                'sessions_analyzed': len(recent),
                'generated_at': datetime.now().isoformat()
            }
            
            return self._success_response(result)
            
        except Exception as e:
            logger.error(f"Progress tracking error: {e}", exc_info=True)
            return self._error_response('PROGRESS_ERROR', str(e))
    
    @log_execution_time
    def clear_cache(self) -> Dict[str, Any]:
        """
        Clear all cached data.
        
        Returns:
            Dictionary with cache clearing status
        """
        cache_size = len(self._cache)
        self._cache.clear()
        self._cache_time.clear()
        logger.info(f"Cache cleared ({cache_size} items)")
        
        return {
            'success': True,
            'message': f'Cache cleared successfully ({cache_size} items removed)',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_feature_status(self) -> Dict[str, bool]:
        """
        Get status of all features.
        
        Returns:
            Dictionary with feature status
        """
        return self.feature_status.copy()
    
    def toggle_feature(self, feature_name: str, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable a specific feature.
        
        Args:
            feature_name: Name of the feature
            enabled: True to enable, False to disable
        
        Returns:
            Dictionary with toggle status
        
        Raises:
            KeyError: If feature doesn't exist
        """
        if feature_name in self.feature_status:
            self.feature_status[feature_name] = enabled
            logger.info(f"Feature {feature_name} {'enabled' if enabled else 'disabled'}")
            
            if not enabled:
                self.clear_cache()
            
            return {
                'success': True,
                'feature': feature_name,
                'enabled': enabled,
                'message': f"Feature '{feature_name}' {'enabled' if enabled else 'disabled'} successfully"
            }
        else:
            logger.warning(f"Feature {feature_name} not found")
            return {
                'success': False,
                'error': 'FEATURE_NOT_FOUND',
                'message': f"Feature '{feature_name}' not found",
                'available_features': list(self.feature_status.keys())
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get recommender statistics.
        
        Returns:
            Dictionary with recommender statistics
        """
        return {
            'cache_size': len(self._cache),
            'cache_ttl_minutes': self._cache_ttl.total_seconds() / 60,
            'min_sessions_required': self.min_sessions,
            'distraction_thresholds': {
                'high': self.high_distraction_threshold,
                'moderate': self.moderate_distraction_threshold,
                'perfect': self.perfect_distraction_threshold
            },
            'consistency_thresholds': {
                'low': self.low_consistency_threshold,
                'high': self.high_consistency_threshold
            },
            'long_session_threshold': self.long_session_threshold,
            'feature_status': self.feature_status,
            'timestamp': datetime.now().isoformat()
        }