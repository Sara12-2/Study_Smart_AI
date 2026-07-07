"""
AI Predictor Module - Predictive Analytics Engine
Version: 2.0.0
Author: Your Name
Description: Provides predictive analytics for productivity including 
             performance forecasting, risk assessment, and optimization
             recommendations using statistical methods.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
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


def validate_sessions(min_count: int = 5):
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
                    'No sessions provided for analysis'
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
                    f'Need at least {min_count} sessions, have {len(sessions)}'
                )
            
            return func(self, sessions, *args, **kwargs)
        return wrapper
    return decorator


class AIPredictor:
    """
    AI-powered predictor for future performance analytics.
    
    This class provides predictive analytics using statistical methods
    including linear regression, trend analysis, and risk assessment.
    All predictions are based on historical session data.
    
    Features:
        - Performance prediction with confidence intervals
        - Session count forecasting
        - Optimal study time prediction
        - Risk assessment
        - Optimal session length prediction
        - Combined predictions
        
    Attributes:
        min_sessions (int): Minimum sessions required for predictions
        prediction_window (int): Number of recent sessions to consider
        confidence_base (float): Base confidence score
        high_distraction_threshold (int): Threshold for high distraction
        low_productivity_threshold (int): Threshold for low productivity
        cache_ttl (timedelta): Cache time-to-live
        feature_status (Dict): Status of all features
    """
    
    def __init__(
        self,
        min_sessions: int = 5,
        prediction_window: int = 5,
        confidence_base: float = 70.0,
        high_distraction_threshold: int = 5,
        low_productivity_threshold: int = 50,
        cache_ttl_minutes: int = 5
    ) -> None:
        """
        Initialize the AI Predictor.
        
        Args:
            min_sessions: Minimum sessions required for predictions (default: 5)
            prediction_window: Number of recent sessions to analyze (default: 5)
            confidence_base: Base confidence score (default: 70.0)
            high_distraction_threshold: Threshold for high distraction (default: 5)
            low_productivity_threshold: Threshold for low productivity (default: 50)
            cache_ttl_minutes: Cache time-to-live in minutes (default: 5)
        
        Raises:
            ValueError: If invalid parameters are provided
        """
        if min_sessions < 3:
            raise ValueError("min_sessions must be >= 3")
        if prediction_window < 2:
            raise ValueError("prediction_window must be >= 2")
        if not 0 <= confidence_base <= 100:
            raise ValueError("confidence_base must be between 0 and 100")
        if high_distraction_threshold < 0:
            raise ValueError("high_distraction_threshold must be >= 0")
        if not 0 <= low_productivity_threshold <= 100:
            raise ValueError("low_productivity_threshold must be between 0 and 100")
        
        self.min_sessions = min_sessions
        self.prediction_window = prediction_window
        self.confidence_base = confidence_base
        self.high_distraction_threshold = high_distraction_threshold
        self.low_productivity_threshold = low_productivity_threshold
        
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=cache_ttl_minutes)
        
        self.feature_status = {
            'weekly_prediction': True,
            'session_count_prediction': True,
            'best_time_prediction': True,
            'risk_assessment': True,
            'optimal_session_length': True,
            'caching': True,
            'all_predictions': True
        }
        
        logger.info(
            f"AIPredictor initialized with min_sessions={min_sessions}, "
            f"prediction_window={prediction_window}, "
            f"confidence_base={confidence_base}"
        )
    
    def _error_response(self, error_type: str, message: str) -> Dict[str, Any]:
        """
        Generate standardized error response.
        
        Args:
            error_type: Type of error (e.g., 'INSUFFICIENT_DATA')
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
    
    def _extract_durations(self, sessions: List[Dict[str, Any]]) -> List[Tuple[int, float]]:
        """
        Extract duration and productivity pairs from sessions.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            List of (duration, productivity) tuples
        """
        pairs = []
        for s in sessions:
            duration = s.get('duration')
            score = s.get('productivity_score')
            if duration is not None and score is not None:
                try:
                    duration_int = int(duration)
                    score_float = float(score)
                    if duration_int > 0 and not np.isnan(score_float):
                        pairs.append((duration_int, max(0, min(100, score_float))))
                except (ValueError, TypeError):
                    continue
        return pairs
    
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
        
        # If already datetime object
        if isinstance(timestamp, datetime):
            return timestamp
        
        # Try different formats
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
        
        # Try ISO format
        try:
            return datetime.fromisoformat(str(timestamp))
        except (ValueError, TypeError):
            pass
        
        return None
    
    @validate_sessions(min_count=5)
    @log_execution_time
    def predict_weekly_productivity(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict next week's productivity.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with prediction results
        
        Example:
            >>> predictor = AIPredictor()
            >>> result = predictor.predict_weekly_productivity(sessions)
            >>> print(result['data']['predicted_productivity'])
            72.5
        """
        cache_key = f"weekly_prediction_{len(sessions)}_{id(sessions)}"
        
        if self.feature_status['caching']:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        
        try:
            scores = self._extract_scores(sessions)
            
            if len(scores) < 3:
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    f'Need at least 3 productivity scores, have {len(scores)}'
                )
            
            # Use recent scores for prediction
            window = min(self.prediction_window, len(scores) // 2 + 1)
            recent_scores = scores[-window:] if window > 0 else scores
            
            # Calculate prediction using linear regression
            predicted = sum(recent_scores) / len(recent_scores)
            slope = 0
            
            if len(recent_scores) > 1:
                x = np.arange(len(recent_scores))
                y = np.array(recent_scores)
                z = np.polyfit(x, y, 1)
                slope = z[0]
                intercept = z[1]
                next_x = len(recent_scores)
                predicted = slope * next_x + intercept
                predicted = max(0, min(100, predicted))
            
            # Calculate confidence
            std = np.std(recent_scores) if len(recent_scores) > 1 else 10
            confidence = self.confidence_base - (std / 2)
            confidence = max(40, min(95, confidence))
            
            # Determine trend
            if slope > 1:
                trend = 'improving'
                trend_emoji = '📈'
                trend_message = 'Your productivity trend is improving. Keep up the good work!'
            elif slope < -1:
                trend = 'declining'
                trend_emoji = '📉'
                trend_message = 'Your productivity trend is declining. Consider changing your study habits!'
            else:
                trend = 'stable'
                trend_emoji = '➡️'
                trend_message = 'Your productivity trend is stable. Consistency is key!'
            
            # Generate explanation
            if predicted >= 80:
                prediction_message = '🌟 You\'re likely to maintain high productivity next week!'
            elif predicted >= 60:
                prediction_message = '📊 You\'re likely to have moderate productivity next week.'
            else:
                prediction_message = '💡 Consider adjusting your study routine for better productivity.'
            
            result = {
                'predicted_productivity': round(predicted, 2),
                'confidence': round(confidence, 2),
                'trend': trend,
                'trend_emoji': trend_emoji,
                'trend_message': trend_message,
                'based_on': len(recent_scores),
                'current_avg': round(np.mean(scores), 2),
                'prediction_message': prediction_message,
                'explanation': f"{trend_emoji} {trend_message} 🎯 Confidence: {confidence:.1f}% {prediction_message}"
            }
            
            response = self._success_response(result)
            
            if self.feature_status['caching']:
                self._cache[cache_key] = response
                self._cache_time[cache_key] = datetime.now()
            
            return response
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            return self._error_response('PREDICTION_ERROR', str(e))
    
    @validate_sessions(min_count=5)
    @log_execution_time
    def predict_session_count(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict next week's session count.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with session count prediction
        
        Example:
            >>> predictor = AIPredictor()
            >>> result = predictor.predict_session_count(sessions)
            >>> print(result['data']['predicted_sessions'])
            12.5
        """
        try:
            weekly_counts = defaultdict(int)
            
            for s in sessions:
                timestamp = s.get('timestamp')
                if timestamp:
                    date = self._safe_parse_timestamp(timestamp)
                    if date:
                        week_key = date.strftime('%Y-W%W')
                        weekly_counts[week_key] += 1
            
            if not weekly_counts:
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    'No weekly data available for prediction'
                )
            
            counts = list(weekly_counts.values())
            avg_count = np.mean(counts)
            std_count = np.std(counts) if len(counts) > 1 else 0
            
            predicted = avg_count
            predicted_min = max(0, round(predicted - std_count, 1))
            predicted_max = round(predicted + std_count, 1)
            
            # Determine trend
            if len(counts) > 1:
                if counts[-1] > counts[0]:
                    trend = 'increasing'
                    trend_message = 'Your session count is increasing. Great consistency!'
                elif counts[-1] < counts[0]:
                    trend = 'decreasing'
                    trend_message = 'Your session count is decreasing. Try to be more consistent!'
                else:
                    trend = 'stable'
                    trend_message = 'Your session count is stable. Keep it up!'
            else:
                trend = 'insufficient'
                trend_message = 'Need more weekly data for trend analysis'
            
            result = {
                'predicted_sessions': round(predicted, 1),
                'range': {
                    'min': predicted_min,
                    'max': predicted_max
                },
                'current_avg': round(avg_count, 1),
                'based_on': len(weekly_counts),
                'trend': trend,
                'trend_message': trend_message,
                'explanation': f"📅 Expected sessions next week: {round(predicted, 1)} ({predicted_min}-{predicted_max})"
            }
            
            return self._success_response(result)
            
        except Exception as e:
            logger.error(f"Session count prediction error: {e}", exc_info=True)
            return self._error_response('PREDICTION_ERROR', str(e))
    
    @validate_sessions(min_count=8)
    @log_execution_time
    def predict_best_time(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict best study time based on patterns.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with best time predictions
        
        Example:
            >>> predictor = AIPredictor()
            >>> result = predictor.predict_best_time(sessions)
            >>> print(result['data']['best_hours'][0]['hour'])
            14
        """
        try:
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
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    'No hourly data available for analysis'
                )
            
            hourly_avg = {}
            for hour, scores_list in hour_scores.items():
                hourly_avg[hour] = np.mean(scores_list)
            
            sorted_hours = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)
            best_hours = sorted_hours[:3]
            
            # Calculate confidence
            total_sessions = sum(len(scores_list) for scores_list in hour_scores.values())
            confidence = min(95, 60 + (total_sessions / 10))
            
            result = {
                'best_hours': [
                    {
                        'hour': hour,
                        'productivity': round(avg, 2),
                        'time_slot': f"{hour:02d}:00 - {hour+1:02d}:00",
                        'sessions_count': len(hour_scores[hour])
                    }
                    for hour, avg in best_hours
                ],
                'recommendation': f"Your peak productivity is at {best_hours[0][0]:02d}:00 ({round(best_hours[0][1], 2)}% productivity)",
                'confidence': round(confidence, 2),
                'based_on': len(hour_scores),
                'total_sessions': total_sessions,
                'explanation': f"⏰ Best time to study: {best_hours[0][0]:02d}:00 - {best_hours[0][0]+1:02d}:00 with {round(best_hours[0][1], 2)}% productivity"
            }
            
            return self._success_response(result)
            
        except Exception as e:
            logger.error(f"Best time prediction error: {e}", exc_info=True)
            return self._error_response('PREDICTION_ERROR', str(e))
    
    @validate_sessions(min_count=5)
    @log_execution_time
    def predict_risk_score(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict risk of low productivity.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with risk assessment
        
        Example:
            >>> predictor = AIPredictor()
            >>> result = predictor.predict_risk_score(sessions)
            >>> print(result['data']['risk_level'])
            'Medium'
        """
        try:
            recent = sessions[-10:] if len(sessions) > 10 else sessions
            
            # Calculate distraction risk
            distractions = [s.get('distractions', 0) for s in recent]
            high_distraction = sum(1 for d in distractions if d > self.high_distraction_threshold)
            distraction_risk = high_distraction / len(recent) if recent else 0
            
            # Calculate productivity risk
            scores = self._extract_scores(recent)
            if scores:
                low_productivity = sum(1 for s in scores if s < self.low_productivity_threshold)
                productivity_risk = low_productivity / len(scores) if scores else 0
            else:
                productivity_risk = 0
            
            # Calculate overall risk
            risk_score = (distraction_risk * 0.4 + productivity_risk * 0.6) * 100
            
            # Determine risk level and recommendations
            if risk_score > 60:
                risk_level = "High"
                risk_emoji = "🔴"
                recommendation = "High risk of low productivity. Focus on reducing distractions and maintaining focus!"
            elif risk_score > 30:
                risk_level = "Medium"
                risk_emoji = "🟡"
                recommendation = "Medium risk. You're doing okay but could improve consistency!"
            else:
                risk_level = "Low"
                risk_emoji = "🟢"
                recommendation = "Low risk. Keep up the good work and maintain your routine!"
            
            result = {
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'risk_emoji': risk_emoji,
                'distraction_risk': round(distraction_risk * 100, 2),
                'productivity_risk': round(productivity_risk * 100, 2),
                'recommendation': recommendation,
                'based_on': len(recent),
                'explanation': f"{risk_emoji} Risk Level: {risk_level} ({risk_score:.1f}%) - {recommendation}"
            }
            
            return self._success_response(result)
            
        except Exception as e:
            logger.error(f"Risk prediction error: {e}", exc_info=True)
            return self._error_response('PREDICTION_ERROR', str(e))
    
    @validate_sessions(min_count=5)
    @log_execution_time
    def predict_optimal_session_length(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict optimal session length based on productivity data.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with optimal session length prediction
        
        Example:
            >>> predictor = AIPredictor()
            >>> result = predictor.predict_optimal_session_length(sessions)
            >>> print(result['data']['optimal_duration'])
            45
        """
        try:
            duration_pairs = self._extract_durations(sessions)
            
            if not duration_pairs:
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    'No valid duration-productivity data available'
                )
            
            # Group by 5-minute bins
            duration_scores = defaultdict(list)
            for duration, score in duration_pairs:
                duration_bin = round(duration / 5) * 5
                duration_scores[duration_bin].append(score)
            
            # Calculate average productivity for each duration
            duration_avg = {
                dur: np.mean(scores) 
                for dur, scores in duration_scores.items()
                if len(scores) >= 2  # Minimum 2 sessions per duration
            }
            
            if not duration_avg:
                return self._error_response(
                    'INSUFFICIENT_DATA',
                    'Need at least 2 sessions per duration for analysis'
                )
            
            # Find optimal duration
            optimal_duration = max(duration_avg.items(), key=lambda x: x[1])
            
            # Calculate confidence
            total_sessions = sum(len(scores) for scores in duration_scores.values())
            confidence = min(90, 50 + (total_sessions / 5))
            
            result = {
                'optimal_duration': optimal_duration[0],
                'avg_productivity': round(optimal_duration[1], 2),
                'based_on': len(duration_avg),
                'total_sessions': total_sessions,
                'confidence': round(confidence, 2),
                'duration_range': f"{optimal_duration[0]-5} - {optimal_duration[0]+5} minutes",
                'recommendation': f"📚 Optimal session length: {optimal_duration[0]} minutes ({round(optimal_duration[1], 2)}% productivity)",
                'explanation': f"Based on {total_sessions} sessions, your optimal study duration is {optimal_duration[0]} minutes"
            }
            
            return self._success_response(result)
            
        except Exception as e:
            logger.error(f"Optimal session length prediction error: {e}", exc_info=True)
            return self._error_response('PREDICTION_ERROR', str(e))
    
    @validate_sessions(min_count=5)
    @log_execution_time
    def predict_all(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate all predictions at once.
        
        Args:
            sessions: List of session dictionaries
        
        Returns:
            Dictionary with all predictions
        
        Example:
            >>> predictor = AIPredictor()
            >>> results = predictor.predict_all(sessions)
            >>> print(results['data']['productivity']['predicted_productivity'])
            72.5
        """
        try:
            results = {}
            
            if self.feature_status['weekly_prediction']:
                results['productivity'] = self.predict_weekly_productivity(sessions)
            
            if self.feature_status['session_count_prediction']:
                results['session_count'] = self.predict_session_count(sessions)
            
            if self.feature_status['best_time_prediction']:
                results['best_time'] = self.predict_best_time(sessions)
            
            if self.feature_status['risk_assessment']:
                results['risk'] = self.predict_risk_score(sessions)
            
            if self.feature_status['optimal_session_length']:
                results['optimal_session_length'] = self.predict_optimal_session_length(sessions)
            
            # Summary
            summary = []
            if 'productivity' in results and results['productivity'].get('success'):
                data = results['productivity']['data']
                summary.append(f"📊 Predicted productivity: {data['predicted_productivity']}%")
            
            if 'best_time' in results and results['best_time'].get('success'):
                data = results['best_time']['data']
                summary.append(f"⏰ Best time: {data['best_hours'][0]['hour']:02d}:00")
            
            if 'risk' in results and results['risk'].get('success'):
                data = results['risk']['data']
                summary.append(f"⚠️ Risk level: {data['risk_level']}")
            
            if 'optimal_session_length' in results and results['optimal_session_length'].get('success'):
                data = results['optimal_session_length']['data']
                summary.append(f"📚 Optimal duration: {data['optimal_duration']}min")
            
            result = {
                'all_predictions': results,
                'summary': summary,
                'total_sessions': len(sessions),
                'features_analyzed': list(self.feature_status.keys()),
                'generated_at': datetime.now().isoformat()
            }
            
            return self._success_response(result)
            
        except Exception as e:
            logger.error(f"All predictions error: {e}", exc_info=True)
            return self._error_response('PREDICTION_ERROR', str(e))
    
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
            
            # Clear cache when toggling features
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
        Get predictor statistics.
        
        Returns:
            Dictionary with predictor statistics
        """
        return {
            'cache_size': len(self._cache),
            'cache_ttl_minutes': self._cache_ttl.total_seconds() / 60,
            'min_sessions_required': self.min_sessions,
            'prediction_window': self.prediction_window,
            'confidence_base': self.confidence_base,
            'high_distraction_threshold': self.high_distraction_threshold,
            'low_productivity_threshold': self.low_productivity_threshold,
            'feature_status': self.feature_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_predictions(self, sessions: List[Dict[str, Any]], format: str = 'json') -> Union[Dict[str, Any], str]:
        """
        Export predictions in different formats.
        
        Args:
            sessions: List of session dictionaries
            format: Export format ('json' or 'dict')
        
        Returns:
            Predictions in requested format
        
        Example:
            >>> predictor = AIPredictor()
            >>> json_output = predictor.export_predictions(sessions, 'json')
        """
        predictions = self.predict_all(sessions)
        
        if format.lower() == 'json':
            return json.dumps(predictions, indent=2, default=str)
        elif format.lower() == 'dict':
            return predictions
        else:
            return self._error_response('INVALID_FORMAT', f"Format '{format}' not supported. Use 'json' or 'dict'")