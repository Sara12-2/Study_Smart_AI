"""
Smart Study System - Web Application
Premium Flask application with interactive dashboard
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# ==========================================
# FIX: Unicode/Emoji Logging for Windows
# ==========================================
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.session import StudySession
from src.core.productivity import ProductivityEngine
from src.storage.json_storage import JSONStorage
# from src.storage.database import Database  # Optional - uncomment if using SQLite
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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize modules
storage = JSONStorage()
# db = Database()  # Optional - uncomment if using SQLite
engine = ProductivityEngine(storage)
analyzer = AIAnalyzer()
predictor = AIPredictor()
recommender = AIRecommender()


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


@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')


# ==================== SESSION ROUTES ====================

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """
    Get all sessions
    Query params:
        - limit: Max number of sessions (default: all)
        - subject: Filter by subject
        - date: Filter by date (YYYY-MM-DD)
    """
    try:
        sessions = storage.load_all_sessions()
        
        # Apply filters
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions', methods=['POST'])
def add_session():
    """Add a new session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('subject'):
            return jsonify({
                'success': False,
                'error': 'Subject is required'
            }), 400
        
        if not data.get('duration'):
            return jsonify({
                'success': False,
                'error': 'Duration is required'
            }), 400
        
        # Validate data
        errors = Validator.validate_session_data({
            'subject': data['subject'],
            'duration': data['duration'],
            'distractions': data.get('distractions', 0),
            'mood': data.get('mood')
        })
        
        if errors:
            return jsonify({
                'success': False,
                'errors': errors
            }), 400
        
        # Create session
        session = StudySession(
            subject=data['subject'],
            duration=int(data['duration']),
            distractions=int(data.get('distractions', 0)),
            notes=data.get('notes'),
            mood=int(data.get('mood')) if data.get('mood') else None
        )
        
        # Save session
        if storage.save_session(session.to_dict()):
            logger.info(f"Session added via web: {data['subject']}")
            return jsonify({
                'success': True,
                'message': 'Session saved successfully',
                'data': session.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save session'
            }), 500
            
    except Exception as e:
        logger.error(f"Error adding session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get a specific session by ID"""
    try:
        session = storage.get_session_by_id(session_id)
        
        if session:
            return jsonify({
                'success': True,
                'data': session
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    """Update a session"""
    try:
        data = request.get_json()
        sessions = storage.load_all_sessions()
        
        if session_id >= len(sessions):
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Update session
        session = sessions[session_id]
        
        if data.get('subject'):
            session['subject'] = data['subject']
        if data.get('duration'):
            session['duration'] = int(data['duration'])
        if data.get('distractions') is not None:
            session['distractions'] = int(data['distractions'])
        if data.get('mood') is not None:
            session['mood'] = int(data['mood'])
        if data.get('notes') is not None:
            session['notes'] = data['notes']
        
        # Recalculate productivity
        temp_session = StudySession(
            subject=session['subject'],
            duration=session['duration'],
            distractions=session.get('distractions', 0)
        )
        temp_session.calculate_productivity()
        session['productivity_score'] = temp_session.productivity_score
        
        # Save updated sessions
        storage._write_data(sessions)
        
        logger.info(f"Session updated: {session['subject']}")
        return jsonify({
            'success': True,
            'message': 'Session updated successfully',
            'data': session
        })
        
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session by ID"""
    try:
        if storage.delete_session(session_id):
            logger.info(f"Session deleted: {session_id}")
            return jsonify({
                'success': True,
                'message': 'Session deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ANALYTICS ROUTES ====================

@app.route('/api/dashboard')
def get_dashboard():
    """
    Get today's dashboard data
    Query params:
        - date: Date in YYYY-MM-DD format (default: today)
    """
    try:
        date = request.args.get('date')
        
        if date:
            summary = engine.calculate_daily_summary(date)
        else:
            summary = engine.calculate_daily_summary()
        
        if summary:
            return jsonify({
                'success': True,
                'data': summary
            })
        else:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No sessions for this date'
            })
            
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/weekly')
def get_weekly():
    """Get weekly report"""
    try:
        report = engine.generate_weekly_report()
        
        return jsonify({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        logger.error(f"Error getting weekly report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/subjects')
def get_subjects():
    """Get subject analysis"""
    try:
        analysis = engine.analyze_subject_performance()
        
        return jsonify({
            'success': True,
            'data': analysis
        })
        
    except Exception as e:
        logger.error(f"Error getting subject analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/trends')
def get_trends():
    """Get productivity trends"""
    try:
        days = int(request.args.get('days', 30))
        trends = engine.get_productivity_trends(days)
        
        return jsonify({
            'success': True,
            'data': trends
        })
        
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/optimal-times')
def get_optimal_times():
    """Get optimal study times"""
    try:
        optimal = engine.get_optimal_study_times()
        
        return jsonify({
            'success': True,
            'data': optimal
        })
        
    except Exception as e:
        logger.error(f"Error getting optimal times: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== AI ROUTES ====================

@app.route('/api/insights')
def get_insights():
    """Get AI insights"""
    try:
        sessions = storage.load_all_sessions()
        insights = analyzer.generate_insights(sessions)
        
        return jsonify({
            'success': True,
            'data': insights
        })
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/predictions')
def get_predictions():
    """Get AI predictions"""
    try:
        sessions = storage.load_all_sessions()
        predictions = predictor.predict_all(sessions)
        
        return jsonify({
            'success': True,
            'data': predictions
        })
        
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommendations')
def get_recommendations():
    """Get AI recommendations"""
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== STATISTICS ROUTES ====================

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        stats = storage.get_statistics()
        sessions = storage.load_all_sessions()
        
        if sessions:
            total_time = sum(s.get('duration', 0) for s in sessions)
            avg_productivity = sum(s.get('productivity_score', 0) for s in sessions) / len(sessions)
            total_distractions = sum(s.get('distractions', 0) for s in sessions)
            
            # Calculate consistency
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== BACKUP ROUTES ====================

@app.route('/api/backup', methods=['POST'])
def create_backup():
    """Create a backup"""
    try:
        backup_file = storage.create_backup()
        
        return jsonify({
            'success': True,
            'message': 'Backup created successfully',
            'data': {'backup_file': backup_file}
        })
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/backup', methods=['GET'])
def list_backups():
    """List all backups"""
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/backup/<backup_name>', methods=['POST'])
def restore_backup(backup_name):
    """Restore from backup"""
    try:
        backup_path = os.path.join('data/backups', backup_name)
        
        if not os.path.exists(backup_path):
            return jsonify({
                'success': False,
                'error': 'Backup file not found'
            }), 404
        
        if storage.restore_from_backup(backup_path):
            logger.info(f"Backup restored: {backup_name}")
            return jsonify({
                'success': True,
                'message': 'Backup restored successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to restore backup'
            }), 500
            
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== CLEANUP ROUTES ====================

@app.route('/api/clear', methods=['DELETE'])
def clear_sessions():
    """Clear all sessions"""
    try:
        confirm = request.args.get('confirm', 'false')
        
        if confirm != 'true':
            return jsonify({
                'success': False,
                'error': 'Confirmation required. Use ?confirm=true'
            }), 400
        
        if storage.clear_all_sessions():
            logger.info("All sessions cleared via API")
            return jsonify({
                'success': True,
                'message': 'All sessions cleared'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear sessions'
            }), 500
            
    except Exception as e:
        logger.error(f"Error clearing sessions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ANALYTICS EXPORT ROUTE ====================

@app.route('/api/analytics/export/<format_type>')
def export_analytics(format_type):
    """Export data in specified format"""
    try:
        from src.core.analytics import AnalyticsEngine
        analytics = AnalyticsEngine(storage, engine)
        
        filepath = analytics.export_data(format_type)
        if filepath:
            return jsonify({
                'success': True,
                'file': f'/{filepath}',
                'message': f'Data exported as {format_type.upper()}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No data to export'
            }), 404
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': Helpers.get_current_time(),
        'sessions': storage.get_session_count(),
        'version': '1.0.0'
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    
    # Use simple logging messages without emojis (fix Windows encoding)
    logger.info("Starting Smart Study System Web Application")
    logger.info(f"Storage: {storage.file_path}")
    logger.info(f"Server: http://localhost:5000")
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
    logger.info("  GET  /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)