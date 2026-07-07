# 🧠 StudySmart AI - Intelligent Study Tracking System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Flask Version](https://img.shields.io/badge/flask-2.3.2-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)]()

> **AI-Powered Study Tracker with Smart Analytics & Personalized Recommendations**

---
## 📸 **Screenshots**

### 🖥️ **Dashboard**
![Dashboard](web/static/images/dashboard.jpg)

### 📊 **Sessions Management**
![Sessions](web/static/images/sessions.jpg)

### 🤖 **AI Insights**
![AI Insights](web/static/images/ai-insights.jpg)

### 🌙 **Dark Mode**
![Dark Mode](web/static/images/Dark-mode.jpg)

### 📱 **Add Session**
![Add Session](web/static/images/add-session.jpg)

### 📚 **Subject Analysis**
![Subjects](web/static/images/subjects.jpg)

### ⚙️ **Settings**
![Settings](web/static/images/settings.jpg)

### 🏆 **Banner**
![Banner](web/static/images/Banner.jpg)
## 📖 **Project Overview**

**StudySmart AI** is an intelligent study tracking system that helps students optimize their learning habits through AI-powered analytics. It tracks study sessions, analyzes productivity patterns, and provides personalized recommendations to improve learning efficiency.

### 🎯 **What Problem Does It Solve?**

| **Problem** | **Solution** |
|-------------|--------------|
| ❌ Students don't track study time effectively | ✅ Automated session tracking with duration & distractions |
| ❌ No visibility into productivity patterns | ✅ AI-powered analytics with visual charts & insights |
| ❌ Difficult to identify best study times | ✅ Smart detection of optimal learning hours |
| ❌ No personalized study recommendations | ✅ AI recommender system with actionable tips |
| ❌ Data loss risk | ✅ Automatic backups with recovery system |
| ❌ No progress tracking | ✅ Streak tracking, achievements & weekly reports |

---

## ✨ **Key Features**

### 🎨 **User Experience**
- 🌙 **Dark/Light Mode** - Eye-friendly themes with persistence
- 📱 **Responsive Design** - Works on mobile, tablet & desktop
- ⌨️ **Keyboard Shortcuts** - Ctrl+N (new), Ctrl+1-5 (navigate), Esc (close)
- 🎯 **Achievement System** - Gamification with confetti celebrations
- 🔔 **Toast Notifications** - Real-time feedback on actions

### 📊 **Study Analytics**
- 📈 **Productivity Tracking** - Score based on distractions & duration
- 📊 **Weekly Charts** - Visual productivity trends
- 📚 **Subject Analysis** - Best/worst subjects with progress bars
- ⏰ **Optimal Study Times** - AI-detected peak productivity hours
- 🔥 **Streak Tracking** - Current & best study streaks

### 🤖 **AI Intelligence**
- 🧠 **Pattern Analysis** - Detects learning patterns & habits
- 📈 **Productivity Predictions** - Future performance forecasting
- 💡 **Smart Recommendations** - Personalized study tips
- 🎯 **Risk Assessment** - Identifies low productivity risks
- 📊 **Confidence Scoring** - AI confidence level for predictions

### 💾 **Data Management**
- 💾 **JSON Storage** - Lightweight, human-readable data
- 🗄️ **SQLite Database** - Robust relational database option
- 📁 **Auto Backups** - Regular backups with cleanup
- 📤 **CSV Export** - Download data for external analysis
- 🔄 **Data Recovery** - Restore from backups

### ⚙️ **Customization**
- 🎨 **Theme Settings** - Light, Dark, Auto (system preference)
- 🌐 **Multi-language** - English, Urdu, Hindi support
- ⏰ **Time Format** - 12h/24h toggle
- 📅 **Study Goals** - Daily & weekly targets
- 🔔 **Notification Preferences** - Reminders & alerts

---

## 🛠️ **Tech Stack**

### **Backend**
| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **Flask 2.3.2** | Web framework |
| **SQLite3** | Relational database |
| **JSON** | Session storage |
| **Pandas 2.0.3** | Data analysis & manipulation |
| **NumPy 1.24.3** | Numerical computations |
| **Scikit-learn 1.3.0** | AI/ML algorithms |

### **Frontend**
| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling with glass-morphism |
| **JavaScript** | Interactivity & API calls |
| **Font Awesome 6.5.0** | Premium icons |
| **Google Fonts (Inter)** | Modern typography |

---

## 📁 **Project Structure**

```bash
StudySmart_AI/
├── 📂 web/                          # Web Application
│   ├── 📂 static/
│   │   ├── 📂 css/
│   │   │   └── style.css            # Premium styling
│   │   └── 📂 js/
│   │       └── script.js            # Interactive logic
│   ├── 📂 templates/
│   │   ├── index.html               # Main dashboard
│   │   ├── dashboard.html           # Dashboard view
│   │   └── settings.html            # Settings page
│   ├── app.py                       # Flask application entry
│   └── routes.py                    # API routes
│
├── 📂 src/                          # Core Source Code
│   ├── 📂 ai/
│   │   ├── analyzer.py              # Pattern analysis & insights
│   │   ├── predictor.py             # Future performance predictions
│   │   └── recommender.py           # Personalized recommendations
│   │
│   ├── 📂 core/
│   │   ├── session.py               # Session data model
│   │   ├── productivity.py          # Productivity engine
│   │   └── analytics.py             # Advanced analytics
│   │
│   ├── 📂 storage/
│   │   ├── json_storage.py          # JSON file operations
│   │   └── database.py              # SQLite database operations
│   │
│   └── 📂 utils/
│       ├── helpers.py               # Utility functions
│       └── validators.py            # Input validation
│
├── 📂 data/                         # User Data
│   ├── sessions.json                # Study sessions
│   ├── user_settings.json           # User preferences
│   ├── study.db                     # SQLite database
│   └── 📂 backups/                  # Automatic backups
│
├── 📂 exports/                      # Exported data (CSV)
├── 📂 logs/                         # Application logs
├── 📂 tests/                        # Unit tests
│   ├── test_analytics.py
│   ├── test_productivity.py
│   └── test_session.py
│
├── main.py                          # CLI application
├── .env                             # Environment variables
├── .gitignore                       # Git ignore file
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```
