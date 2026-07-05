#!/usr/bin/env python3
"""
Smart Study System - Command Line Interface
Premium CLI with rich formatting and interactive experience
"""

import sys
import os
import logging
import codecs
from datetime import datetime
from typing import Optional

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.session import StudySession
from src.core.productivity import ProductivityEngine
from src.storage.json_storage import JSONStorage
from src.ai.analyzer import AIAnalyzer
from src.ai.predictor import AIPredictor
from src.ai.recommender import AIRecommender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cli.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StudyCLI:
    """
    Premium Command Line Interface for Smart Study System
    Features:
    - Interactive menu
    - Rich formatting
    - Error handling
    - Session management
    - Analytics dashboard
    - AI insights
    - Backup & Restore
    - Session edit & search
    """
    
    def __init__(self):
        """Initialize CLI with storage and engine"""
        self.storage = JSONStorage()
        self.engine = ProductivityEngine(self.storage)
        self.analyzer = AIAnalyzer()
        self.predictor = AIPredictor()
        self.recommender = AIRecommender()
        self.current_user = None
        self.is_running = True
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        logger.info("StudyCLI initialized")
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print application header"""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("  🧠 SMART STUDY SYSTEM - Premium Edition")
        print("  " + "=" * 54)
        print("  📊 Track | 📈 Analyze | 🤖 Predict | 💡 Improve")
        print("=" * 60 + "\n")
    
    def print_menu(self):
        """Print main menu"""
        self.print_header()
        print("  📋 MAIN MENU")
        print("  " + "-" * 50)
        print("  1. 📚  Add Study Session")
        print("  2. 📊  View Today's Dashboard")
        print("  3. 📈  Weekly Report")
        print("  4. 📉  Subject Analysis")
        print("  5. 🤖  AI Insights & Recommendations")
        print("  6. 📁  Manage Sessions")
        print("  7. ✏️  Edit Session")
        print("  8. 🔍  Search Sessions")
        print("  9. 🗂️  Backup & Restore")
        print("  10. ℹ️  Statistics")
        print("  0. 🚪  Exit")
        print("  " + "-" * 50)
    
    def get_input(self, prompt: str, input_type: type = str, required: bool = True, 
                  min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[str]:
        """
        Get validated user input
        
        Args:
            prompt: Input prompt
            input_type: Type to cast to
            required: Whether input is required
            min_val: Minimum value (for numbers)
            max_val: Maximum value (for numbers)
            
        Returns:
            Validated input or None
        """
        while True:
            try:
                value = input(prompt).strip()
                
                if not value and not required:
                    return None
                
                if not value and required:
                    print("  ❌ Input is required. Please try again.")
                    continue
                
                if input_type == int:
                    value = int(value)
                    if min_val is not None and value < min_val:
                        print(f"  ❌ Value must be at least {min_val}")
                        continue
                    if max_val is not None and value > max_val:
                        print(f"  ❌ Value must be at most {max_val}")
                        continue
                elif input_type == float:
                    value = float(value)
                    if min_val is not None and value < min_val:
                        print(f"  ❌ Value must be at least {min_val}")
                        continue
                    if max_val is not None and value > max_val:
                        print(f"  ❌ Value must be at most {max_val}")
                        continue
                
                return value
                
            except ValueError:
                print(f"  ❌ Please enter a valid {input_type.__name__}")
                continue
            except KeyboardInterrupt:
                print("\n  ⚠️ Operation cancelled")
                return None
    
    def add_session(self):
        """Add a new study session"""
        print("\n  📚 ADD STUDY SESSION")
        print("  " + "-" * 40)
        
        # Get subject
        subject = self.get_input("  Subject (e.g., Python): ", str, required=True)
        if subject is None:
            return
        
        # Get duration
        duration = self.get_input("  Duration (minutes, 5-240): ", int, required=True, min_val=5, max_val=240)
        if duration is None:
            return
        
        # Get distractions
        distractions = self.get_input("  Distractions (0-20): ", int, required=True, min_val=0, max_val=20)
        if distractions is None:
            return
        
        # Get optional mood
        print("  Mood (optional - 1=Very Bad, 5=Excellent)")
        mood = self.get_input("  Mood (1-5, press Enter to skip): ", int, required=False, min_val=1, max_val=5)
        
        # Get optional notes
        notes = input("  Notes (optional): ").strip()
        
        try:
            # Create session
            session = StudySession(
                subject=subject,
                duration=duration,
                distractions=distractions,
                notes=notes if notes else None,
                mood=mood
            )
            
            # Save session
            if self.storage.save_session(session.to_dict()):
                print("\n  ✅ Session saved successfully!")
                print(f"  📊 Productivity Score: {session.productivity_score}%")
                print(f"  💬 {session.get_productivity_message()}")
                logger.info(f"Session added: {subject} - {duration}min")
            else:
                print("\n  ❌ Failed to save session. Please try again.")
                
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            logger.error(f"Error adding session: {e}")
        
        input("\n  Press Enter to continue...")
    
    def view_dashboard(self):
        """View today's dashboard"""
        print("\n  📊 TODAY'S DASHBOARD")
        print("  " + "-" * 40)
        
        summary = self.engine.calculate_daily_summary()
        
        if not summary:
            print("\n  📭 No sessions recorded today.")
            print("  💡 Start tracking your study sessions to see insights!")
        else:
            print(f"\n  📅 Date: {summary['date']}")
            print(f"  📚 Total Sessions: {summary['total_sessions']}")
            print(f"  ⏱️  Total Time: {summary['total_time']} minutes")
            print(f"  📈 Avg Productivity: {summary['avg_productivity']}%")
            print(f"  ⚠️  Total Distractions: {summary['total_distractions']}")
            print(f"  🎯 Consistency Score: {summary['consistency_score']}%")
            print(f"  🏆 Overall Score: {summary['score']}%")
            
            print("\n  📚 Subjects:")
            for subject, time in summary['subjects'].items():
                print(f"    • {subject}: {time} minutes")
            
            if summary['best_subject']['name']:
                print(f"\n  🌟 Best Subject: {summary['best_subject']['name']} ({summary['best_subject']['score']}%)")
            
            if summary['worst_subject']['name']:
                print(f"  ⚠️  Worst Subject: {summary['worst_subject']['name']} ({summary['worst_subject']['score']}%)")
            
            if summary['peak_hour']:
                print(f"  🕐 Peak Hour: {summary['peak_hour']:02d}:00")
            
            trend_emoji = "📈" if summary['productivity_trend'] == 'improving' else "📉" if summary['productivity_trend'] == 'declining' else "➡️"
            print(f"  {trend_emoji} Trend: {summary['productivity_trend'].capitalize()}")
        
        input("\n  Press Enter to continue...")
    
    def view_weekly_report(self):
        """View weekly report"""
        print("\n  📈 WEEKLY REPORT")
        print("  " + "-" * 40)
        
        report = self.engine.generate_weekly_report()
        
        if 'error' in report:
            print(f"\n  ❌ {report['error']}")
        else:
            print(f"\n  📊 Total Weeks: {report['total_weeks']}")
            print(f"  📚 Total Sessions: {report['total_sessions']}")
            print(f"  ⏱️  Total Time: {report['total_time']} minutes")
            print(f"  📈 Overall Productivity: {report['overall_productivity']}%")
            print(f"  📉 Trend: {report['trend'].capitalize()}")
            
            if report['best_week']['week']:
                print(f"\n  🌟 Best Week: {report['best_week']['week']} ({report['best_week']['score']}%)")
            
            if report['worst_week']['week']:
                print(f"  ⚠️  Worst Week: {report['worst_week']['week']} ({report['worst_week']['score']}%)")
            
            print(f"\n  📅 Current Week: {report['current_week']}")
            print(f"  📚 Sessions: {report['current_week_sessions']}")
            print(f"  ⏱️  Time: {report['current_week_time']} minutes")
            print(f"  📈 Productivity: {report['current_week_productivity']}%")
        
        input("\n  Press Enter to continue...")
    
    def view_subject_analysis(self):
        """View subject-wise analysis"""
        print("\n  📉 SUBJECT ANALYSIS")
        print("  " + "-" * 40)
        
        analysis = self.engine.analyze_subject_performance()
        
        if 'error' in analysis:
            print(f"\n  ❌ {analysis['error']}")
        else:
            print(f"\n  📚 Total Subjects: {analysis['total_subjects']}")
            
            print("\n  📊 Subject Rankings:")
            for i, (subject, metrics) in enumerate(analysis['subjects'], 1):
                print(f"\n  {i}. {subject}")
                print(f"     Sessions: {metrics['sessions']}")
                print(f"     Time: {metrics['total_time']} minutes")
                print(f"     Avg Productivity: {metrics['avg_productivity']}%")
                print(f"     Best: {metrics['max_productivity']}% | Worst: {metrics['min_productivity']}%")
                print(f"     Avg Distractions: {metrics['avg_distractions']}")
            
            if analysis['best_subject']:
                subject, metrics = analysis['best_subject']
                print(f"\n  🌟 Best Subject: {subject} ({metrics['avg_productivity']}%)")
            
            if analysis['worst_subject']:
                subject, metrics = analysis['worst_subject']
                print(f"  ⚠️  Worst Subject: {subject} ({metrics['avg_productivity']}%)")
        
        input("\n  Press Enter to continue...")
    
    def view_ai_insights(self):
        """View AI-powered insights"""
        print("\n  🤖 AI INSIGHTS & RECOMMENDATIONS")
        print("  " + "-" * 40)
        
        sessions = self.storage.load_all_sessions()
        
        # Get insights from analyzer
        insights = self.analyzer.generate_insights(sessions)
        
        # Get trends
        trends = self.engine.get_productivity_trends(30)
        
        # Get optimal times
        optimal_times = self.engine.get_optimal_study_times()
        
        print("\n  🕐 OPTIMAL STUDY TIMES")
        if 'error' in optimal_times:
            print(f"  ❌ {optimal_times['error']}")
        else:
            print(f"  🌟 Best Hour: {optimal_times['best_hour']:02d}:00")
            print(f"  📊 Best Hour Productivity: {optimal_times['best_hour_productivity']}%")
            
            if optimal_times['peak_periods']:
                print("\n  🎯 Peak Study Periods:")
                for period in optimal_times['peak_periods'][:3]:
                    print(f"    • {period['time_range']} (Score: {period['avg_score']}%)")
            
            print(f"\n  💡 Recommendation: {optimal_times['recommendation']}")
        
        # Show recommendations if available
        if insights and not insights.get('error'):
            recommendations = insights.get('recommendations', [])
            if recommendations:
                print("\n  💡 AI RECOMMENDATIONS")
                print("  " + "-" * 40)
                for rec in recommendations[:5]:
                    print(f"  • {rec}")
        
        print("\n  📈 PRODUCTIVITY TRENDS (30 days)")
        if 'error' in trends:
            print(f"  ❌ {trends['error']}")
        else:
            print(f"  📊 Days Analyzed: {trends['days_analyzed']}")
            print(f"  📈 Trend: {trends['trend_direction'].capitalize()}")
            print(f"  📉 Slope: {trends['trend_slope']}%")
            print(f"  🎯 Avg Productivity: {trends['avg_productivity']}%")
            print(f"  🏆 Max Productivity: {trends['max_productivity']}%")
            print(f"  💪 Consistency: {trends['consistency']}%")
        
        input("\n  Press Enter to continue...")
    
    def manage_sessions(self):
        """Manage sessions (view, delete)"""
        print("\n  📁 MANAGE SESSIONS")
        print("  " + "-" * 40)
        
        sessions = self.storage.load_all_sessions()
        
        if not sessions:
            print("\n  📭 No sessions found.")
            input("\n  Press Enter to continue...")
            return
        
        print(f"\n  📚 Total Sessions: {len(sessions)}")
        print("\n  Recent Sessions:")
        print("  " + "-" * 40)
        
        # Show last 10 sessions
        recent = sessions[-10:]
        for i, session in enumerate(recent, 1):
            date = session.get('timestamp', '')[:10]
            subject = session.get('subject', 'Unknown')
            duration = session.get('duration', 0)
            productivity = session.get('productivity_score', 0)
            print(f"  {i}. {date} - {subject} ({duration}min) - {productivity}%")
        
        print("\n  Options:")
        print("  1. Delete a session")
        print("  2. Clear all sessions")
        print("  3. Return to main menu")
        
        choice = self.get_input("  Choose option (1-3): ", int, min_val=1, max_val=3)
        
        if choice == 1:
            session_id = self.get_input("  Enter session number to delete: ", int, min_val=1, max_val=len(recent))
            if session_id is not None:
                actual_id = len(sessions) - session_id
                if self.storage.delete_session(actual_id):
                    print("  ✅ Session deleted successfully!")
                else:
                    print("  ❌ Failed to delete session.")
        elif choice == 2:
            confirm = input("  ⚠️ Are you sure? This cannot be undone! (yes/no): ")
            if confirm.lower() == 'yes':
                if self.storage.clear_all_sessions():
                    print("  ✅ All sessions cleared!")
                else:
                    print("  ❌ Failed to clear sessions.")
        
        input("\n  Press Enter to continue...")
    
    def edit_session(self):
        """Edit an existing session"""
        print("\n  ✏️ EDIT SESSION")
        print("  " + "-" * 40)
        
        sessions = self.storage.load_all_sessions()
        if not sessions:
            print("\n  📭 No sessions found.")
            input("\n  Press Enter to continue...")
            return
        
        # Show sessions
        print("\n  Recent Sessions:")
        print("  " + "-" * 40)
        recent = sessions[-10:]
        for i, session in enumerate(recent, 1):
            date = session.get('timestamp', '')[:10]
            subject = session.get('subject', 'Unknown')
            duration = session.get('duration', 0)
            productivity = session.get('productivity_score', 0)
            print(f"  {i}. {date} - {subject} ({duration}min) - {productivity}%")
        
        choice = self.get_input("\n  Select session to edit (1-10): ", int, min_val=1, max_val=len(recent))
        if choice is None:
            return
        
        actual_index = len(sessions) - 10 + choice - 1
        if actual_index < 0:
            actual_index = choice - 1
        session = sessions[actual_index]
        
        print(f"\n  Editing: {session.get('subject')} - {session.get('duration')}min")
        print("  " + "-" * 40)
        
        # Get new values (press Enter to keep current)
        subject = self.get_input(f"  Subject ({session.get('subject')}): ", str, required=False)
        duration = self.get_input(f"  Duration ({session.get('duration')}min): ", int, required=False, min_val=5, max_val=240)
        distractions = self.get_input(f"  Distractions ({session.get('distractions')}): ", int, required=False, min_val=0, max_val=20)
        mood = self.get_input(f"  Mood ({session.get('mood', 'N/A')}): ", int, required=False, min_val=1, max_val=5)
        
        # Update session
        if subject:
            session['subject'] = subject
        if duration:
            session['duration'] = duration
        if distractions is not None:
            session['distractions'] = distractions
        if mood is not None:
            session['mood'] = mood
        
        # Recalculate productivity
        temp_session = StudySession(
            subject=session['subject'],
            duration=session['duration'],
            distractions=session.get('distractions', 0)
        )
        temp_session.calculate_productivity()
        session['productivity_score'] = temp_session.productivity_score
        
        # Save
        self.storage._write_data(sessions)
        print("\n  ✅ Session updated successfully!")
        logger.info(f"Session edited: {session['subject']}")
        
        input("\n  Press Enter to continue...")
    
    def search_sessions(self):
        """Search sessions by subject"""
        print("\n  🔍 SEARCH SESSIONS")
        print("  " + "-" * 40)
        
        query = input("  Enter subject to search: ").strip().lower()
        if not query:
            print("\n  ❌ Search query cannot be empty.")
            input("\n  Press Enter to continue...")
            return
        
        sessions = self.storage.load_all_sessions()
        results = [s for s in sessions if query in s.get('subject', '').lower()]
        
        if not results:
            print(f"\n  ❌ No sessions found for '{query}'")
        else:
            print(f"\n  📚 Found {len(results)} sessions:")
            print("  " + "-" * 40)
            for i, session in enumerate(results, 1):
                date = session.get('timestamp', '')[:10]
                subject = session.get('subject', 'Unknown')
                duration = session.get('duration', 0)
                productivity = session.get('productivity_score', 0)
                print(f"  {i}. {date} - {subject} ({duration}min) - {productivity}%")
        
        input("\n  Press Enter to continue...")
    
    def backup_restore(self):
        """Backup and restore functionality"""
        print("\n  🗂️ BACKUP & RESTORE")
        print("  " + "-" * 40)
        
        print("\n  Options:")
        print("  1. Create backup")
        print("  2. Restore from backup")
        print("  3. View backup statistics")
        print("  4. Return to main menu")
        
        choice = self.get_input("  Choose option (1-4): ", int, min_val=1, max_val=4)
        
        if choice == 1:
            backup_file = self.storage.create_backup()
            print(f"  ✅ Backup created: {backup_file}")
        
        elif choice == 2:
            # Get available backups
            backup_dir = 'data/backups'
            backups = []
            if os.path.exists(backup_dir):
                backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.json')], reverse=True)
            
            if not backups:
                print("\n  ❌ No backups found.")
                input("\n  Press Enter to continue...")
                return
            
            print("\n  📋 Available Backups:")
            for i, backup in enumerate(backups, 1):
                file_path = os.path.join(backup_dir, backup)
                size = os.path.getsize(file_path)
                print(f"  {i}. {backup} ({size} bytes)")
            
            choice_num = self.get_input("\n  Select backup to restore: ", int, min_val=1, max_val=len(backups))
            if choice_num is None:
                return
            
            backup_file = os.path.join(backup_dir, backups[choice_num - 1])
            
            print("  ⚠️ Restoring will replace current data!")
            confirm = input("  Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                if self.storage.restore_from_backup(backup_file):
                    print("  ✅ Data restored successfully!")
                else:
                    print("  ❌ Restore failed.")
        
        elif choice == 3:
            stats = self.storage.get_statistics()
            print(f"\n  📊 Storage Statistics:")
            print(f"  Total Sessions: {stats['total_sessions']}")
            print(f"  File Size: {stats['file_size']} bytes")
            print(f"  Subjects: {stats['subjects']}")
            print(f"  Backups: {stats['backup_count']}")
        
        input("\n  Press Enter to continue...")
    
    def view_statistics(self):
        """View overall statistics"""
        print("\n  ℹ️ SYSTEM STATISTICS")
        print("  " + "-" * 40)
        
        stats = self.storage.get_statistics()
        sessions = self.storage.load_all_sessions()
        
        print(f"\n  📊 Database Statistics:")
        print(f"  Total Sessions: {stats['total_sessions']}")
        print(f"  File Size: {stats['file_size']} bytes")
        print(f"  Subjects: {stats['subjects']}")
        print(f"  Backups: {stats['backup_count']}")
        
        if sessions:
            # Calculate additional stats
            total_time = sum(s.get('duration', 0) for s in sessions)
            avg_productivity = sum(s.get('productivity_score', 0) for s in sessions) / len(sessions)
            total_distractions = sum(s.get('distractions', 0) for s in sessions)
            
            print(f"\n  📈 Session Statistics:")
            print(f"  Total Time: {total_time} minutes")
            print(f"  Avg Productivity: {round(avg_productivity, 2)}%")
            print(f"  Total Distractions: {total_distractions}")
            print(f"  First Session: {sessions[0].get('timestamp', 'N/A')[:10]}")
            print(f"  Last Session: {sessions[-1].get('timestamp', 'N/A')[:10]}")
        
        input("\n  Press Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while self.is_running:
            try:
                self.print_menu()
                choice = self.get_input("  Enter your choice: ", int, min_val=0, max_val=10)
                
                if choice == 0:
                    print("\n  👋 Thank you for using Smart Study System!")
                    print("  📊 Keep tracking, keep improving!")
                    self.is_running = False
                
                elif choice == 1:
                    self.add_session()
                elif choice == 2:
                    self.view_dashboard()
                elif choice == 3:
                    self.view_weekly_report()
                elif choice == 4:
                    self.view_subject_analysis()
                elif choice == 5:
                    self.view_ai_insights()
                elif choice == 6:
                    self.manage_sessions()
                elif choice == 7:
                    self.edit_session()
                elif choice == 8:
                    self.search_sessions()
                elif choice == 9:
                    self.backup_restore()
                elif choice == 10:
                    self.view_statistics()
                
            except KeyboardInterrupt:
                print("\n\n  👋 Goodbye! Keep studying!")
                self.is_running = False
            except Exception as e:
                print(f"\n  ❌ An error occurred: {e}")
                logger.error(f"Application error: {e}")
                input("\n  Press Enter to continue...")
    
    @staticmethod
    def main():
        """Entry point"""
        try:
            cli = StudyCLI()
            cli.run()
        except Exception as e:
            print(f"\n  ❌ Fatal error: {e}")
            logger.critical(f"Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    StudyCLI.main()