"""
Web Routes Module - REST API Endpoints
All API routes for the Smart Study System web application
"""

import logging
from flask import request, jsonify, render_template
from datetime import datetime, timedelta
import sys
import os

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
    
    # ==================== SESSION ROUTES ====================
    
    @app.route('/api/sessions', methods=['GET'])
    def get_sessions():
        """
        Get all sessions
        GET /api/sessions
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
        """
        Add a new session
        POST /api/sessions
        Body: { subject, duration, distractions, mood, notes }
        """
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
                logger.info(f"Session added via API: {data['subject']} - {data['duration']}min")
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
        """
        Get a specific session by ID
        GET /api/sessions/{id}
        """
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
        """
        Update a session
        PUT /api/sessions/{id}
        Body: { subject, duration, distractions, mood, notes }
        """
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
        """
        Delete a session
        DELETE /api/sessions/{id}
        """
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
        GET /api/dashboard
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
        """
        Get weekly report
        GET /api/weekly
        """
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
        """
        Get subject analysis
        GET /api/subjects
        """
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
        """
        Get productivity trends
        GET /api/trends
        Query params:
            - days: Number of days to analyze (default: 30)
        """
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
        """
        Get optimal study times
        GET /api/optimal-times
        """
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
        """
        Get AI insights
        GET /api/insights
        """
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
        """
        Get AI predictions
        GET /api/predictions
        """
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
        """
        Get AI recommendations
        GET /api/recommendations
        """
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
        """
        Get system statistics
        GET /api/stats
        """
        try:
            stats = storage.get_statistics()
            sessions = storage.load_all_sessions()
            
            if sessions:
                total_time = sum(s.get('duration', 0) for s in sessions)
                avg_productivity = sum(s.get('productivity_score', 0) for s in sessions) / len(sessions)
                total_distractions = sum(s.get('distractions', 0) for s in sessions)
            else:
                total_time = 0
                avg_productivity = 0
                total_distractions = 0
            
            return jsonify({
                'success': True,
                'data': {
                    'total_sessions': stats['total_sessions'],
                    'total_time': total_time,
                    'avg_productivity': round(avg_productivity, 2) if avg_productivity else 0,
                    'total_distractions': total_distractions,
                    'subjects': stats['subjects'],
                    'backups': stats['backup_count'],
                    'file_size': stats['file_size']
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
        """
        Create a backup
        POST /api/backup
        """
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
        """
        List all backups
        GET /api/backup
        """
        try:
            import os
            backup_dir = 'data/backups'
            backups = []
            
            if os.path.exists(backup_dir):
                for f in os.listdir(backup_dir):
                    if f.endswith('.json'):
                        file_path = os.path.join(backup_dir, f)
                        backups.append({
                            'name': f,
                            'size': os.path.getsize(file_path),
                            'created': os.path.getctime(file_path)
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
        """
        Restore from backup
        POST /api/backup/{backup_name}
        """
        try:
            import os
            backup_path = os.path.join('data/backups', backup_name)
            
            if not os.path.exists(backup_path):
                return jsonify({
                    'success': False,
                    'error': 'Backup file not found'
                }), 404
            
            if storage.restore_from_backup(backup_path):
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
        """
        Clear all sessions
        DELETE /api/clear
        """
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
    
    # ==================== HEALTH CHECK ====================
    
    @app.route('/api/health')
    def health_check():
        """
        Health check endpoint
        GET /api/health
        """
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': Helpers.get_current_time(),
            'sessions': storage.get_session_count(),
            'version': '1.0.0'
        })
    
    logger.info("All routes registered successfully")