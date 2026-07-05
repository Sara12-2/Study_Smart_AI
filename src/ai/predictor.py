"""
AI Predictor Module
Predictive analytics for future performance
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class AIPredictor:
    """
    AI-powered predictor for future performance
    
    Features:
    - Performance prediction
    - Trend forecasting
    - Session count prediction
    - Risk assessment
    - Optimal session length prediction
    """
    
    def __init__(self):
        """Initialize the predictor with cache"""
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = timedelta(minutes=5)
        logger.info("AIPredictor initialized")
    
    def _get_cached(self, key: str, func, *args, **kwargs):
        """Get cached data or compute fresh"""
        if key in self._cache:
            if datetime.now() - self._cache_time[key] < self._cache_ttl:
                return self._cache[key]
        
        result = func(*args, **kwargs)
        self._cache[key] = result
        self._cache_time[key] = datetime.now()
        return result
    
    def predict_weekly_productivity(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict next week's productivity
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with predictions
        """
        # Reduce minimum sessions to 5
        if len(sessions) < 5:
            return {
                'error': 'Insufficient data',
                'message': f'Need at least 5 sessions, have {len(sessions)}'
            }
        
        try:
            scores = [s.get('productivity_score', 0) for s in sessions if s.get('productivity_score') is not None]
            
            if len(scores) < 3:
                return {'error': 'Insufficient productivity data'}
            
            window = min(5, len(scores) // 2)
            recent_scores = scores[-window:]
            
            slope = 0
            predicted = sum(recent_scores) / len(recent_scores)
            
            if len(recent_scores) > 1:
                x = np.arange(len(recent_scores))
                y = np.array(recent_scores)
                z = np.polyfit(x, y, 1)
                slope = z[0]
                intercept = z[1]
                next_x = len(recent_scores)
                predicted = slope * next_x + intercept
                predicted = max(0, min(100, predicted))
            
            std = np.std(recent_scores) if len(recent_scores) > 1 else 10
            confidence = 70 - (std / 2)
            confidence = max(40, min(95, confidence))
            
            # Trend interpretation
            if slope > 1:
                trend = 'improving'
            elif slope < -1:
                trend = 'declining'
            else:
                trend = 'stable'
            
            return {
                'predicted_productivity': round(predicted, 2),
                'confidence': round(confidence, 2),
                'trend': trend,
                'based_on': len(recent_scores),
                'current_avg': round(np.mean(scores), 2),
                'explanation': self._explain_prediction(predicted, confidence, trend)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'error': str(e)}
    
    def predict_session_count(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict next week's session count
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with predictions
        """
        if len(sessions) < 5:
            return {
                'error': 'Insufficient data',
                'message': f'Need at least 5 sessions, have {len(sessions)}'
            }
        
        try:
            # Group by week with year to avoid boundary issues
            weekly_counts = defaultdict(int)
            for s in sessions:
                if s.get('timestamp'):
                    date = datetime.fromisoformat(s['timestamp'])
                    week_key = date.strftime('%Y-W%W')  # Include year
                    weekly_counts[week_key] += 1
            
            if not weekly_counts:
                return {'error': 'No weekly data'}
            
            counts = list(weekly_counts.values())
            avg_count = np.mean(counts)
            std_count = np.std(counts) if len(counts) > 1 else 0
            
            predicted = avg_count
            trend = 'increasing' if avg_count > (avg_count - std_count) else 'stable'
            
            return {
                'predicted_sessions': round(predicted, 1),
                'range': {
                    'min': max(0, round(predicted - std_count, 1)),
                    'max': round(predicted + std_count, 1)
                },
                'current_avg': round(avg_count, 1),
                'based_on': len(weekly_counts),
                'trend': trend
            }
            
        except Exception as e:
            logger.error(f"Session count prediction error: {e}")
            return {'error': str(e)}
    
    def predict_best_time(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict best study time based on patterns
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with time predictions
        """
        if len(sessions) < 8:
            return {
                'error': 'Insufficient data',
                'message': f'Need 8 sessions, have {len(sessions)}'
            }
        
        try:
            hour_scores = defaultdict(list)
            for s in sessions:
                if s.get('timestamp') and s.get('productivity_score'):
                    hour = datetime.fromisoformat(s['timestamp']).hour
                    hour_scores[hour].append(s['productivity_score'])
            
            if not hour_scores:
                return {'error': 'No hourly data'}
            
            hourly_avg = {}
            for hour, scores in hour_scores.items():
                hourly_avg[hour] = np.mean(scores)
            
            sorted_hours = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)
            best_hours = sorted_hours[:3]
            
            return {
                'best_hours': [
                    {
                        'hour': hour,
                        'productivity': round(avg, 2),
                        'time_slot': f"{hour:02d}:00 - {hour+1:02d}:00"
                    }
                    for hour, avg in best_hours
                ],
                'recommendation': f"Your peak productivity is at {best_hours[0][0]:02d}:00 ({round(best_hours[0][1], 2)}%)",
                'based_on': len(hour_scores)
            }
            
        except Exception as e:
            logger.error(f"Best time prediction error: {e}")
            return {'error': str(e)}
    
    def predict_risk_score(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict risk of low productivity
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with risk assessment
        """
        if len(sessions) < 5:
            return {
                'error': 'Insufficient data',
                'message': f'Need 5 sessions, have {len(sessions)}'
            }
        
        try:
            recent = sessions[-10:] if len(sessions) > 10 else sessions
            
            distractions = [s.get('distractions', 0) for s in recent]
            high_distraction = sum(1 for d in distractions if d > 5)
            distraction_risk = high_distraction / len(recent) if recent else 0
            
            scores = [s.get('productivity_score', 0) for s in recent if s.get('productivity_score') is not None]
            if scores:
                low_productivity = sum(1 for s in scores if s < 50)
                productivity_risk = low_productivity / len(scores) if scores else 0
            else:
                productivity_risk = 0
            
            risk_score = (distraction_risk * 0.4 + productivity_risk * 0.6) * 100
            
            if risk_score > 60:
                risk_level = "High"
                recommendation = "⚠️ High risk of low productivity. Focus on reducing distractions!"
            elif risk_score > 30:
                risk_level = "Medium"
                recommendation = "📊 Medium risk. You're doing okay but could improve!"
            else:
                risk_level = "Low"
                recommendation = "✅ Low risk. Keep up the good work!"
            
            return {
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'distraction_risk': round(distraction_risk * 100, 2),
                'productivity_risk': round(productivity_risk * 100, 2),
                'recommendation': recommendation,
                'based_on': len(recent)
            }
            
        except Exception as e:
            logger.error(f"Risk prediction error: {e}")
            return {'error': str(e)}
    
    def predict_optimal_session_length(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict optimal session length based on productivity data
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with optimal session length prediction
        """
        if len(sessions) < 5:
            return {'error': 'Insufficient data', 'message': 'Need at least 5 sessions'}
        
        try:
            duration_scores = defaultdict(list)
            for s in sessions:
                if s.get('duration') and s.get('productivity_score'):
                    duration = s['duration']
                    duration_bin = round(duration / 5) * 5
                    duration_scores[duration_bin].append(s['productivity_score'])
            
            duration_avg = {
                dur: np.mean(scores) 
                for dur, scores in duration_scores.items()
            }
            
            if duration_avg:
                optimal_duration = max(duration_avg.items(), key=lambda x: x[1])
                return {
                    'optimal_duration': optimal_duration[0],
                    'avg_productivity': round(optimal_duration[1], 2),
                    'based_on': len(duration_scores)
                }
            return {'error': 'No valid duration data'}
            
        except Exception as e:
            logger.error(f"Optimal session length prediction error: {e}")
            return {'error': str(e)}
    
    def _explain_prediction(self, predicted: float, confidence: float, trend: str) -> str:
        """Generate human-readable explanation of prediction"""
        explanation = []
        
        if trend == 'improving':
            explanation.append("📈 Your productivity trend is improving. Keep up the good work!")
        elif trend == 'declining':
            explanation.append("📉 Your productivity trend is declining. Consider changing your study habits!")
        else:
            explanation.append("➡️ Your productivity trend is stable. Consistency is key!")
        
        explanation.append(f"🎯 Prediction confidence: {confidence}%")
        
        if predicted >= 80:
            explanation.append("🌟 You're likely to maintain high productivity next week!")
        elif predicted >= 60:
            explanation.append("📊 You're likely to have moderate productivity next week.")
        else:
            explanation.append("💡 Consider adjusting your study routine for better productivity.")
        
        return " ".join(explanation)
    
    def predict_all(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate all predictions
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with all predictions
        """
        return {
            'productivity': self.predict_weekly_productivity(sessions),
            'session_count': self.predict_session_count(sessions),
            'best_time': self.predict_best_time(sessions),
            'risk': self.predict_risk_score(sessions),
            'optimal_session_length': self.predict_optimal_session_length(sessions)
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_time.clear()
        logger.info("Cache cleared")