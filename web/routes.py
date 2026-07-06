"""
Web Routes Module - REST API Endpoints
All API routes for the Smart Study System web application
"""

import logging
import os
import sys
import uuid
import csv
from io import StringIO
from datetime import datetime, timedelta
from flask import request, jsonify, render_template, g, session, make_response

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.session import StudySession
from src.core.productivity import ProductivityEngine
from src.storage.json_storage import JSONStorage
from src.ai.analyzer import AIAnalyzer
from src.ai.predictor import AIPredictor
from src.ai.recommender import AIRecommender
from src.utils.validators import Validator
from src.utils.helpers import Helpers

logger = logging.getLogger(__name__)

# Initialize modules
storage = JSONStorage()
engine = ProductivityEngine(storage)
analyzer = AIAnalyzer()
predictor = AIPredictor()
recommender = AIRecommender()


def register_routes(app):
    """
    Register all routes with Flask app
    
    Args:
        app: Flask application instance
    """
    
    # ==================== REQUEST MIDDLEWARE ====================
    
    @app.before_request
    def before_request():
        """Add request ID for tracking"""
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4())[:8])
        g.request_id = request_id
    
    @app.after_request
    def after_request(response):
        """Add request ID to response headers"""
        response.headers['X-Request-ID'] = getattr(g, 'request_id', '')
        return response
    
    # ==================== PAGE ROUTES ====================
    
    @app.route('/')
    def index():
        """Home page - Dashboard"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/sessions')
    def sessions_page():
        """Sessions management page"""
        return render_template('index.html')
    
    # ==================== SETTINGS ROUTE ====================
    
    @app.route('/settings')
    def settings_page():
        """Settings page - User preferences and configuration"""
        user_settings = storage.load_user_settings() if hasattr(storage, 'load_user_settings') else {}
        
        default_settings = {
            'theme': 'light',
            'notifications': True,
            'study_reminder': True,
            'reminder_interval': 60,
            'default_subject': '',
            'daily_goal': 120,
            'weekly_goal': 600,
            'language': 'en',
            'time_format': '24h',
            'sound_effects': True
        }
        
        settings = {**default_settings, **user_settings}
        return render_template('settings.html', settings=settings)
    
    # ==================== SESSION ROUTES ====================
    
    @app.route('/api/sessions', methods=['GET'])
    def get_sessions():
        """Get all sessions"""
        try:
            sessions = storage.load_all_sessions()
            subject = request.args.get('subject')
            date = request.args.get('date')
            limit = request.args.get('limit')
            
            if subject:
                sessions = [s for s in sessions if s.get('subject', '').lower() == subject.lower()]
            if date:
                sessions = [s for s in sessions if s.get('timestamp', '').startswith(date)]
            if limit:
                sessions = sessions[-int(limit):]
            
            return jsonify({
                'success': True,
                'data': sessions,
                'count': len(sessions),
                'total': storage.get_session_count()
            })
        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/sessions', methods=['POST'])
    def add_session():
        """Add a new session"""
        try:
            if not request.is_json:
                return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data.get('subject') or not data.get('duration'):
                return jsonify({'success': False, 'error': 'Subject and duration are required'}), 400
            
            errors = Validator.validate_session_data({
                'subject': data['subject'],
                'duration': data['duration'],
                'distractions': data.get('distractions', 0),
                'mood': data.get('mood')
            })
            
            if errors:
                return jsonify({'success': False, 'errors': errors}), 400
            
            session = StudySession(
                subject=data['subject'],
                duration=int(data['duration']),
                distractions=int(data.get('distractions', 0)),
                notes=data.get('notes'),
                mood=int(data.get('mood')) if data.get('mood') else None
            )
            
            if storage.save_session(session.to_dict()):
                return jsonify({'success': True, 'message': 'Session saved successfully', 'data': session.to_dict()})
            return jsonify({'success': False, 'error': 'Failed to save session'}), 500
        except Exception as e:
            logger.error(f"Error adding session: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/sessions/<int:session_id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_session(session_id):
        """Handle individual session operations"""
        try:
            if request.method == 'GET':
                session_data = storage.get_session_by_id(session_id)
                if session_data:
                    return jsonify({'success': True, 'data': session_data})
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            elif request.method == 'PUT':
                if not request.is_json:
                    return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
                
                data = request.get_json()
                if storage.update_session(session_id, data):
                    return jsonify({'success': True, 'message': 'Session updated successfully'})
                return jsonify({'success': False, 'error': 'Failed to update session'}), 500
            
            elif request.method == 'DELETE':
                if storage.delete_session(session_id):
                    return jsonify({'success': True, 'message': 'Session deleted successfully'})
                return jsonify({'success': False, 'error': 'Failed to delete session'}), 500
                
        except Exception as e:
            logger.error(f"Error handling session {session_id}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==================== SETTINGS API ROUTES ====================
    
    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        """Get user settings"""
        try:
            settings = storage.load_user_settings() if hasattr(storage, 'load_user_settings') else {}
            return jsonify({'success': True, 'data': settings})
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/settings', methods=['POST', 'PUT'])
    def update_settings():
        """Update user settings"""
        try:
            if not request.is_json:
                return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            
            valid_keys = ['theme', 'notifications', 'study_reminder', 'reminder_interval', 
                         'default_subject', 'daily_goal', 'weekly_goal', 'language', 
                         'time_format', 'sound_effects']
            
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            
            if hasattr(storage, 'save_user_settings'):
                if storage.save_user_settings(filtered_data):
                    return jsonify({'success': True, 'message': 'Settings updated successfully', 'data': filtered_data})
            else:
                import json
                settings_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_settings.json')
                os.makedirs(os.path.dirname(settings_file), exist_ok=True)
                with open(settings_file, 'w') as f:
                    json.dump(filtered_data, f, indent=2)
                return jsonify({'success': True, 'message': 'Settings updated successfully', 'data': filtered_data})
            
            return jsonify({'success': False, 'error': 'Failed to update settings'}), 500
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/settings/reset', methods=['POST'])
    def reset_settings():
        """Reset settings to default"""
        try:
            default_settings = {
                'theme': 'light',
                'notifications': True,
                'study_reminder': True,
                'reminder_interval': 60,
                'default_subject': '',
                'daily_goal': 120,
                'weekly_goal': 600,
                'language': 'en',
                'time_format': '24h',
                'sound_effects': True
            }
            
            if hasattr(storage, 'save_user_settings'):
                if storage.save_user_settings(default_settings):
                    return jsonify({'success': True, 'message': 'Settings reset to default', 'data': default_settings})
            else:
                import json
                settings_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_settings.json')
                os.makedirs(os.path.dirname(settings_file), exist_ok=True)
                with open(settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                return jsonify({'success': True, 'message': 'Settings reset to default', 'data': default_settings})
            
            return jsonify({'success': False, 'error': 'Failed to reset settings'}), 500
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==================== ANALYTICS & AI ROUTES ====================
    
    @app.route('/api/dashboard')
    def get_dashboard_data():
        """Get dashboard overview data"""
        try:
            sessions = storage.load_all_sessions()
            
            total_sessions = len(sessions)
            total_study_time = sum(s.get('duration', 0) for s in sessions)
            
            week_ago = datetime.now() - timedelta(days=7)
            weekly_sessions = []
            for s in sessions:
                try:
                    if datetime.fromisoformat(s.get('timestamp', '')) >= week_ago:
                        weekly_sessions.append(s)
                except:
                    pass
            
            subjects = {}
            for s in sessions:
                subject = s.get('subject', 'Unknown')
                subjects[subject] = subjects.get(subject, 0) + 1
            
            return jsonify({
                'success': True,
                'data': {
                    'total_sessions': total_sessions,
                    'total_study_time': total_study_time,
                    'weekly_sessions': len(weekly_sessions),
                    'subjects': subjects,
                    'top_subject': max(subjects.items(), key=lambda x: x[1])[0] if subjects else 'None'
                }
            })
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/weekly')
    def get_weekly_stats():
        """Get weekly statistics"""
        try:
            sessions = storage.load_all_sessions()
            weekly_data = {}
            
            today = datetime.now().date()
            for i in range(7):
                date = today - timedelta(days=i)
                date_str = date.isoformat()
                daily_sessions = [s for s in sessions if s.get('timestamp', '').startswith(date_str)]
                weekly_data[date_str] = {
                    'date': date_str,
                    'sessions': len(daily_sessions),
                    'total_time': sum(s.get('duration', 0) for s in daily_sessions)
                }
            
            return jsonify({'success': True, 'data': weekly_data})
        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/subjects')
    def get_subject_analytics():
        """Get subject-wise analytics"""
        try:
            sessions = storage.load_all_sessions()
            subject_data = {}
            
            for s in sessions:
                subject = s.get('subject', 'Unknown')
                if subject not in subject_data:
                    subject_data[subject] = {
                        'sessions': 0,
                        'total_time': 0,
                        'avg_mood': 0,
                        'moods': []
                    }
                subject_data[subject]['sessions'] += 1
                subject_data[subject]['total_time'] += s.get('duration', 0)
                if s.get('mood'):
                    subject_data[subject]['moods'].append(s.get('mood'))
            
            for subject in subject_data:
                if subject_data[subject]['moods']:
                    subject_data[subject]['avg_mood'] = sum(subject_data[subject]['moods']) / len(subject_data[subject]['moods'])
                del subject_data[subject]['moods']
            
            return jsonify({'success': True, 'data': subject_data})
        except Exception as e:
            logger.error(f"Error getting subject analytics: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/trends')
    def get_trends():
        """Get study trends"""
        try:
            sessions = storage.load_all_sessions()
            
            trends = {
                'total_study_time': sum(s.get('duration', 0) for s in sessions),
                'average_session_duration': sum(s.get('duration', 0) for s in sessions) / len(sessions) if sessions else 0,
                'most_active_day': 'Monday',
                'productivity_score': 0
            }
            
            return jsonify({'success': True, 'data': trends})
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/optimal-times')
    def get_optimal_times():
        """Get optimal study times"""
        try:
            sessions = storage.load_all_sessions()
            
            hourly_activity = {}
            for s in sessions:
                timestamp = s.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        hour = dt.hour
                        hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
                    except:
                        pass
            
            optimal_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return jsonify({
                'success': True, 
                'data': {
                    'hourly_activity': hourly_activity,
                    'optimal_hours': [h for h, _ in optimal_hours]
                }
            })
        except Exception as e:
            logger.error(f"Error getting optimal times: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/insights')
    def get_insights():
        """Get AI insights"""
        try:
            sessions = storage.load_all_sessions()
            insights = analyzer.generate_insights(sessions) if hasattr(analyzer, 'generate_insights') else {
                'study_patterns': 'No data available',
                'recommendations': ['Start tracking your study sessions for personalized insights']
            }
            return jsonify({'success': True, 'data': insights})
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/predictions')
    def get_predictions():
        """Get AI predictions"""
        try:
            sessions = storage.load_all_sessions()
            predictions = predictor.predict_all(sessions) if hasattr(predictor, 'predict_all') else {
                'expected_hours': 0,
                'confidence': 0
            }
            return jsonify({'success': True, 'data': predictions})
        except Exception as e:
            logger.error(f"Error getting predictions: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/recommendations')
    def get_recommendations():
        """Get AI recommendations"""
        try:
            sessions = storage.load_all_sessions()
            recommendations = recommender.get_recommendations(sessions) if hasattr(recommender, 'get_recommendations') else {
                'subjects': [],
                'study_plan': 'Start tracking your sessions to get personalized recommendations'
            }
            return jsonify({'success': True, 'data': recommendations})
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/stats')
    def get_stats():
        """Get overall statistics"""
        try:
            sessions = storage.load_all_sessions()
            
            stats = {
                'total_sessions': len(sessions),
                'total_time': sum(s.get('duration', 0) for s in sessions),
                'average_per_session': sum(s.get('duration', 0) for s in sessions) / len(sessions) if sessions else 0,
                'subjects_studied': len(set(s.get('subject', 'Unknown') for s in sessions)),
                'total_distractions': sum(s.get('distractions', 0) for s in sessions),
                'average_mood': 0
            }
            
            mood_sessions = [s for s in sessions if s.get('mood')]
            if mood_sessions:
                stats['average_mood'] = sum(s.get('mood', 0) for s in mood_sessions) / len(mood_sessions)
            
            return jsonify({'success': True, 'data': stats})
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/backup', methods=['POST'])
    def create_backup():
        """Create a backup of all data"""
        try:
            if hasattr(storage, 'create_backup'):
                backup_file = storage.create_backup()
                return jsonify({'success': True, 'message': 'Backup created successfully', 'file': backup_file})
            return jsonify({'success': False, 'error': 'Backup functionality not available'}), 500
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/clear', methods=['POST'])
    def clear_data():
        """Clear all session data"""
        try:
            if request.is_json and request.get_json().get('confirm') == 'yes':
                if hasattr(storage, 'clear_all_sessions'):
                    storage.clear_all_sessions()
                    return jsonify({'success': True, 'message': 'All data cleared successfully'})
                return jsonify({'success': False, 'error': 'Clear functionality not available'}), 500
            return jsonify({'success': False, 'error': 'Confirmation required'}), 400
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ✅ FIXED: EXPORT ROUTE - FULLY WORKING ====================
    
    @app.route('/api/analytics/export/csv', methods=['GET'])
    def export_analytics_csv():
        """
        Export all sessions as CSV file with proper headers
        Returns: CSV file download
        """
        try:
            logger.info("📤 Export request received")
            sessions = storage.load_all_sessions()
            
            if not sessions:
                logger.warning("⚠️ No data to export")
                return jsonify({
                    'success': False,
                    'error': 'No data to export. Add some sessions first!'
                }), 404
            
            logger.info(f"📊 Exporting {len(sessions)} sessions")
            
            # Create CSV in memory
            output = StringIO()
            fieldnames = list(sessions[0].keys())
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sessions)
            
            csv_content = output.getvalue()
            output.close()
            
            # Generate filename with timestamp
            filename = f"study_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Create response with proper CSV headers
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            logger.info(f"✅ Export successful: {filename} ({len(sessions)} sessions, {len(csv_content)} bytes)")
            return response
            
        except Exception as e:
            logger.error(f"❌ Export error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Export failed: {str(e)}'
            }), 500
    
    # ==================== COMPARE ROUTE ====================
    
    @app.route('/api/compare')
    def compare_periods():
        """Compare study periods"""
        try:
            sessions = storage.load_all_sessions()
            
            today = datetime.now()
            current_week = []
            previous_week = []
            
            for s in sessions:
                try:
                    dt = datetime.fromisoformat(s.get('timestamp', ''))
                    if dt >= (today - timedelta(days=7)):
                        current_week.append(s)
                    elif (today - timedelta(days=14)) <= dt < (today - timedelta(days=7)):
                        previous_week.append(s)
                except:
                    pass
            
            return jsonify({
                'success': True,
                'data': {
                    'current_week': {
                        'sessions': len(current_week),
                        'total_time': sum(s.get('duration', 0) for s in current_week)
                    },
                    'previous_week': {
                        'sessions': len(previous_week),
                        'total_time': sum(s.get('duration', 0) for s in previous_week)
                    },
                    'improvement': {
                        'sessions': len(current_week) - len(previous_week),
                        'time': sum(s.get('duration', 0) for s in current_week) - sum(s.get('duration', 0) for s in previous_week)
                    }
                }
            })
        except Exception as e:
            logger.error(f"Error comparing periods: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==================== HEALTH CHECK ====================
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': Helpers.get_current_time(),
            'sessions': storage.get_session_count(),
            'version': '1.0.0',
            'routes_loaded': [
                '/', '/dashboard', '/sessions', '/settings',
                '/api/sessions', '/api/settings', '/api/settings/reset',
                '/api/dashboard', '/api/weekly', '/api/subjects', 
                '/api/trends', '/api/optimal-times', '/api/insights', 
                '/api/predictions', '/api/recommendations', '/api/stats', 
                '/api/backup', '/api/clear', '/api/compare', '/api/health',
                '/api/analytics/export/csv'  # ✅ Added export route to list
            ]
        })
    
    logger.info("✅ All routes registered successfully")