"""
AI Recommender Module
Personalized recommendations for better learning
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class AIRecommender:
    """
    AI-powered recommendation engine
    
    Features:
    - Personalized recommendations
    - Actionable suggestions
    - Progress tracking
    - Smart alerts
    """
    
    def __init__(self):
        """Initialize the recommender"""
        logger.info("AIRecommender initialized")
    
    def get_recommendations(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate personalized recommendations
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            List of recommendation dictionaries
        """
        if len(sessions) < 5:
            return [
                {
                    'type': 'info',
                    'title': '📚 Start Tracking',
                    'description': 'Add more sessions to get personalized recommendations!',
                    'action': 'Add 5+ sessions for insights'
                }
            ]
        
        recommendations = []
        
        # 1. Distraction recommendations
        dist_rec = self._recommend_distractions(sessions)
        if dist_rec:
            recommendations.append(dist_rec)
        
        # 2. Subject recommendations
        subj_rec = self._recommend_subjects(sessions)
        if subj_rec:
            recommendations.append(subj_rec)
        
        # 3. Time recommendations
        time_rec = self._recommend_time(sessions)
        if time_rec:
            recommendations.append(time_rec)
        
        # 4. Consistency recommendations
        cons_rec = self._recommend_consistency(sessions)
        if cons_rec:
            recommendations.append(cons_rec)
        
        # 5. Break recommendations
        break_rec = self._recommend_breaks(sessions)
        if break_rec:
            recommendations.append(break_rec)
        
        if not recommendations:
            recommendations.append({
                'type': 'info',
                'title': '💡 Keep Going',
                'description': 'You\'re doing great! Keep tracking to unlock more insights.',
                'action': 'Continue your learning journey'
            })
        
        return recommendations
    
    def _recommend_distractions(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Generate distraction recommendations"""
        recent = sessions[-10:] if len(sessions) > 10 else sessions
        avg_dist = sum(s.get('distractions', 0) for s in recent) / len(recent)
        
        if avg_dist > 5:
            return {
                'type': 'warning',
                'title': '⚠️ High Distractions',
                'description': f'You average {round(avg_dist, 1)} distractions per session. Try the Pomodoro technique!',
                'action': '25 min focus → 5 min break → Repeat'
            }
        elif avg_dist > 3:
            return {
                'type': 'info',
                'title': '📊 Moderate Distractions',
                'description': f'You average {round(avg_dist, 1)} distractions. Try to reduce by 1 per session.',
                'action': 'Aim for 3 or fewer distractions'
            }
        elif avg_dist < 1:
            return {
                'type': 'success',
                'title': '🎯 Great Focus',
                'description': 'You have minimal distractions! This is excellent for learning.',
                'action': 'Maintain this focus level'
            }
        return None
    
    def _recommend_subjects(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Generate subject recommendations"""
        if len(sessions) < 5:
            return None
        
        # Calculate subject performance
        subject_scores = defaultdict(list)
        for s in sessions:
            subject = s.get('subject', 'Unknown')
            score = s.get('productivity_score', 0)
            if score:
                subject_scores[subject].append(score)
        
        if not subject_scores:
            return None
        
        # Find best and worst subjects
        subject_avg = {
            subj: sum(scores) / len(scores)
            for subj, scores in subject_scores.items()
        }
        
        best = max(subject_avg.items(), key=lambda x: x[1])
        worst = min(subject_avg.items(), key=lambda x: x[1])
        
        if best[0] != worst[0]:
            return {
                'type': 'info',
                'title': '📚 Subject Focus',
                'description': f'You\'re best at {best[0]} ({round(best[1], 1)}%) but need improvement in {worst[0]} ({round(worst[1], 1)}%).',
                'action': f'Dedicate 30% more time to {worst[0]} this week'
            }
        return None
    
    def _recommend_time(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Generate time-based recommendations"""
        if len(sessions) < 7:
            return None
        
        # Find best time
        hour_scores = defaultdict(list)
        for s in sessions:
            if s.get('timestamp') and s.get('productivity_score'):
                hour = datetime.fromisoformat(s['timestamp']).hour
                hour_scores[hour].append(s['productivity_score'])
        
        if not hour_scores:
            return None
        
        best_hour = max(hour_scores.items(), key=lambda x: sum(x[1]) / len(x[1]))
        
        return {
            'type': 'success',
            'title': '🕐 Optimal Study Time',
            'description': f'Your best time is {best_hour[0]:02d}:00 ({round(sum(best_hour[1]) / len(best_hour[1]), 1)}% productivity).',
            'action': f'Study your hardest subjects at {best_hour[0]:02d}:00'
        }
    
    def _recommend_consistency(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Generate consistency recommendations"""
        if len(sessions) < 10:
            return None
        
        # Check daily consistency
        daily_sessions = defaultdict(int)
        for s in sessions:
            if s.get('timestamp'):
                date = datetime.fromisoformat(s['timestamp']).date()
                daily_sessions[date] += 1
        
        days = len(daily_sessions)
        avg = len(sessions) / days if days > 0 else 0
        
        if avg < 1.5:
            return {
                'type': 'warning',
                'title': '📅 Inconsistent Study',
                'description': f'You study only {round(avg, 1)} sessions per day. Try to be more consistent!',
                'action': 'Aim for at least 2 sessions per day'
            }
        elif avg >= 3:
            return {
                'type': 'success',
                'title': '🔥 Great Consistency',
                'description': f'You study {round(avg, 1)} sessions per day. Excellent consistency!',
                'action': 'Keep up the great habit!'
            }
        return None
    
    def _recommend_breaks(self, sessions: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Generate break recommendations"""
        if len(sessions) < 5:
            return None
        
        # Find long sessions
        long_sessions = [s for s in sessions if s.get('duration', 0) > 120]
        
        if long_sessions:
            return {
                'type': 'info',
                'title': '⏰ Take Breaks',
                'description': f'You have {len(long_sessions)} sessions over 2 hours. Long sessions can reduce focus.',
                'action': 'Take a 10-minute break every 45-60 minutes'
            }
        return None
    
    def get_motivational_messages(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Get motivational messages based on data"""
        messages = []
        
        if not sessions:
            messages.append("🌟 Start your learning journey today!")
            return messages
        
        # Count total time
        total_time = sum(s.get('duration', 0) for s in sessions)
        hours = total_time / 60
        
        if hours >= 10:
            messages.append(f"🚀 You've studied {round(hours, 1)} hours! Incredible dedication!")
        elif hours >= 5:
            messages.append(f"📚 {round(hours, 1)} hours studied! Keep building momentum!")
        elif hours >= 2:
            messages.append(f"💪 {round(hours, 1)} hours of learning! Every minute counts!")
        else:
            messages.append("🌟 Every journey starts with a single step. Keep going!")
        
        # Check streaks
        if len(sessions) >= 5:
            messages.append("🔥 You're building a learning streak! Stay consistent!")
        
        # Check improvements
        recent_avg = sum(s.get('productivity_score', 0) for s in sessions[-5:]) / min(5, len(sessions))
        overall_avg = sum(s.get('productivity_score', 0) for s in sessions) / len(sessions)
        
        if recent_avg > overall_avg:
            messages.append("📈 You're improving! Your recent sessions are better than average!")
        
        return messages