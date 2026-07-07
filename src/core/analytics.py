"""
Smart Study System - Web Application
Premium Flask application with interactive dashboard
"""

import os
import sys
import logging
import json
import csv
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, make_response
from flask_cors import CORS

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.session import StudySession
from src.core.productivity import ProductivityEngine
from src.storage.json_storage import JSONStorage
from src.ai.analyzer import AIAnalyzer
from src.ai.predictor import AIPredictor
from src.ai.recommender import AIRecommender
from src.utils.helpers import Helpers
from src.utils.validators import Validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== SECRET KEY FOR SESSION ====================
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production-2024')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

CORS(app)

# Initialize modules
storage = JSONStorage()
engine = ProductivityEngine(storage)
analyzer = AIAnalyzer()
predictor = AIPredictor()
recommender = AIRecommender()

# ==================== USER SETTINGS HELPER ====================

def get_user_settings():
    """Load user settings from file or session"""
    try:
        if 'user_settings' in session:
            return session['user_settings']
        
        settings_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_settings.json')
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                session['user_settings'] = settings
                return settings
    except Exception as e:
        logger.error(f"Error loading user settings: {e}")
    
    return get_default_settings()

def get_default_settings():
    """Get default settings"""
    return {
        'theme': 'light',
        'notifications': True,
        'study_reminder': True,
        'reminder_interval': 60,
        'default_subject': '',
        'daily_goal': 120,
        'weekly_goal': 600,
        'language': 'en',
        'time_format': '24h',
        'sound_effects': True,
        'auto_backup': True,
        'backup_interval': 7
    }

def save_user_settings(settings_data):
    """Save user settings to file and session"""
    try:
        valid_keys = ['theme', 'notifications', 'study_reminder', 'reminder_interval', 
                     'default_subject', 'daily_goal', 'weekly_goal', 'language', 
                     'time_format', 'sound_effects', 'auto_backup', 'backup_interval']
        
        filtered_data = {k: v for k, v in settings_data.items() if k in valid_keys}
        existing = get_user_settings()
        existing.update(filtered_data)
        
        settings_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_settings.json')
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2)
        
        session['user_settings'] = existing
        logger.info("User settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving user settings: {e}")
        return False


# ==================== PAGE ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/sessions')
def sessions_page():
    return render_template('index.html')

@app.route('/settings')
def settings_page():
    settings = get_user_settings()
    return render_template('settings.html', settings=settings)


# ==================== SESSION ROUTES ====================

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
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
    try:
        data = request.get_json()
        
        if not data.get('subject'):
            return jsonify({'success': False, 'error': 'Subject is required'}), 400
        if not data.get('duration'):
            return jsonify({'success': False, 'error': 'Duration is required'}), 400
        
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
            logger.info(f"Session added via web: {data['subject']}")
            return jsonify({
                'success': True,
                'message': 'Session saved successfully',
                'data': session.to_dict()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save session'}), 500
    except Exception as e:
        logger.error(f"Error adding session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        if storage.delete_session(session_id):
            logger.info(f"Session deleted: {session_id}")
            return jsonify({'success': True, 'message': 'Session deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== SETTINGS API ROUTES ====================

@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    try:
        settings = get_user_settings()
        return jsonify({'success': True, 'data': settings})
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['POST', 'PUT'])
def api_update_settings():
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if save_user_settings(data):
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully',
                'data': get_user_settings()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update settings'}), 500
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings/reset', methods=['POST'])
def api_reset_settings():
    try:
        default_settings = get_default_settings()
        if save_user_settings(default_settings):
            return jsonify({
                'success': True,
                'message': 'Settings reset to default',
                'data': default_settings
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to reset settings'}), 500
    except Exception as e:
        logger.error(f"Error resetting settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ANALYTICS ROUTES ====================

@app.route('/api/dashboard')
def get_dashboard():
    try:
        date = request.args.get('date')
        if date:
            summary = engine.calculate_daily_summary(date)
        else:
            summary = engine.calculate_daily_summary()
        
        if summary:
            return jsonify({'success': True, 'data': summary})
        else:
            return jsonify({'success': True, 'data': None, 'message': 'No sessions for this date'})
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/weekly')
def get_weekly():
    try:
        report = engine.generate_weekly_report()
        return jsonify({'success': True, 'data': report})
    except Exception as e:
        logger.error(f"Error getting weekly report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subjects')
def get_subjects():
    try:
        analysis = engine.analyze_subject_performance()
        return jsonify({'success': True, 'data': analysis})
    except Exception as e:
        logger.error(f"Error getting subject analysis: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trends')
def get_trends():
    try:
        days = int(request.args.get('days', 30))
        trends = engine.get_productivity_trends(days)
        return jsonify({'success': True, 'data': trends})
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimal-times')
def get_optimal_times():
    try:
        optimal = engine.get_optimal_study_times()
        return jsonify({'success': True, 'data': optimal})
    except Exception as e:
        logger.error(f"Error getting optimal times: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== AI ROUTES ====================

@app.route('/api/insights')
def get_insights():
    try:
        sessions = storage.load_all_sessions()
        insights = analyzer.generate_insights(sessions)
        return jsonify({'success': True, 'data': insights})
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predictions')
def get_predictions():
    try:
        sessions = storage.load_all_sessions()
        predictions = predictor.predict_all(sessions)
        return jsonify({'success': True, 'data': predictions})
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommendations')
def get_recommendations():
    try:
        sessions = storage.load_all_sessions()
        recommendations = recommender.get_recommendations(sessions)
        motivational = recommender.get_motivational_messages(sessions)
        return jsonify({
            'success': True,
            'data': {
                'recommendations': recommendations,
                'motivational': motivational
            }
        })
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== STATISTICS ====================

@app.route('/api/stats')
def get_stats():
    try:
        stats = storage.get_statistics()
        sessions = storage.load_all_sessions()
        
        if sessions:
            total_time = sum(s.get('duration', 0) for s in sessions)
            avg_productivity = sum(s.get('productivity_score', 0) for s in sessions) / len(sessions)
            total_distractions = sum(s.get('distractions', 0) for s in sessions)
            
            if len(sessions) > 1:
                scores = [s.get('productivity_score', 0) for s in sessions]
                from statistics import stdev
                consistency = 100 - (stdev(scores) / 100 * 100)
                consistency = max(0, min(100, consistency))
            else:
                consistency = 100
        else:
            total_time = 0
            avg_productivity = 0
            total_distractions = 0
            consistency = 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_sessions': stats['total_sessions'],
                'total_time': total_time,
                'avg_productivity': round(avg_productivity, 2) if avg_productivity else 0,
                'total_distractions': total_distractions,
                'subjects': stats['subjects'],
                'backups': stats['backup_count'],
                'file_size': stats['file_size'],
                'consistency': round(consistency, 2)
            }
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== BACKUP ROUTES ====================

@app.route('/api/backup', methods=['POST'])
def create_backup():
    try:
        backup_file = storage.create_backup()
        return jsonify({
            'success': True,
            'message': 'Backup created successfully',
            'data': {'backup_file': backup_file}
        })
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup', methods=['GET'])
def list_backups():
    try:
        backup_dir = 'data/backups'
        backups = []
        
        if os.path.exists(backup_dir):
            for f in os.listdir(backup_dir):
                if f.endswith('.json'):
                    file_path = os.path.join(backup_dir, f)
                    backups.append({
                        'name': f,
                        'size': os.path.getsize(file_path),
                        'created': os.path.getctime(file_path),
                        'date': datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return jsonify({
            'success': True,
            'data': sorted(backups, key=lambda x: x['created'], reverse=True)
        })
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/<backup_name>', methods=['POST'])
def restore_backup(backup_name):
    try:
        backup_path = os.path.join('data/backups', backup_name)
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'error': 'Backup file not found'}), 404
        
        if storage.restore_from_backup(backup_path):
            return jsonify({'success': True, 'message': 'Backup restored successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to restore backup'}), 500
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== EXPORT - FIXED ====================

@app.route('/api/analytics/export/csv', methods=['GET'])
def export_analytics_csv():
    """Export data as downloadable CSV file"""
    try:
        from io import StringIO
        from flask import make_response
        
        sessions = storage.load_all_sessions()
        
        if not sessions:
            return jsonify({
                'success': False,
                'error': 'No data to export'
            }), 404
        
        # Create CSV in memory
        output = StringIO()
        fieldnames = list(sessions[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sessions)
        
        # Create response with download headers
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=study_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        logger.info(f"Data exported: {len(sessions)} sessions")
        return response
            
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CLEANUP ====================

@app.route('/api/clear', methods=['DELETE'])
def clear_sessions():
    try:
        confirm = request.args.get('confirm', 'false')
        if confirm != 'true':
            return jsonify({
                'success': False,
                'error': 'Confirmation required. Use ?confirm=true'
            }), 400
        
        if storage.clear_all_sessions():
            return jsonify({'success': True, 'message': 'All sessions cleared'})
        else:
            return jsonify({'success': False, 'error': 'Failed to clear sessions'}), 500
    except Exception as e:
        logger.error(f"Error clearing sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health')
def health_check():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': Helpers.get_current_time(),
        'sessions': storage.get_session_count(),
        'version': '1.0.0',
        'settings_available': bool(get_user_settings())
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    logger.info("Starting Smart Study System Web Application")
    logger.info(f"Storage: {storage.file_path}")
    logger.info(f"Server: http://localhost:{PORT}")
    logger.info("API Endpoints available:")
    logger.info("  GET  /api/sessions - Get all sessions")
    logger.info("  POST /api/sessions - Add a session")
    logger.info("  GET  /api/dashboard - Today's dashboard")
    logger.info("  GET  /api/weekly - Weekly report")
    logger.info("  GET  /api/subjects - Subject analysis")
    logger.info("  GET  /api/insights - AI insights")
    logger.info("  GET  /api/predictions - AI predictions")
    logger.info("  GET  /api/recommendations - AI recommendations")
    logger.info("  GET  /api/stats - System statistics")
    logger.info("  GET  /api/settings - Get user settings")
    logger.info("  POST /api/settings - Update user settings")
    logger.info("  POST /api/settings/reset - Reset settings")
    logger.info("  GET  /api/analytics/export/csv - Export data (direct download)")
    logger.info("  GET  /api/health - Health check")
    
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)