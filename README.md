# 🧠 StudySmart AI - Intelligent Study Tracking System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Flask Version](https://img.shields.io/badge/flask-2.3.2-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-development-yellow.svg)]()

> **AI-Powered Study Tracker with Smart Analytics & Personalized Recommendations**

---

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
| **Matplotlib 3.7.2** | Chart generation |

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
├── 📂 web/ # Web Application
│ ├── 📂 static/
│ │ ├── 📂 css/
│ │ │ └── style.css # Premium styling
│ │ └── 📂 js/
│ │ └── script.js # Interactive logic
│ ├── 📂 templates/
│ │ ├── index.html # Main dashboard
│ │ ├── dashboard.html # Dashboard view
│ │ └── settings.html # Settings page
│ ├── app.py # Flask application entry
│ └── routes.py # API routes
│
├── 📂 src/ # Core Source Code
│ ├── 📂 ai/
│ │ ├── analyzer.py # Pattern analysis & insights
│ │ ├── predictor.py # Future performance predictions
│ │ └── recommender.py # Personalized recommendations
│ │
│ ├── 📂 core/
│ │ ├── session.py # Session data model
│ │ ├── productivity.py # Productivity engine
│ │ └── analytics.py # Advanced analytics
│ │
│ ├── 📂 storage/
│ │ ├── json_storage.py # JSON file operations
│ │ └── database.py # SQLite database operations
│ │
│ └── 📂 utils/
│ ├── helpers.py # Utility functions
│ └── validators.py # Input validation
│
├── 📂 data/ # User Data
│ ├── sessions.json # Study sessions
│ ├── user_settings.json # User preferences
│ ├── study.db # SQLite database
│ └── 📂 backups/ # Automatic backups
│
├── 📂 exports/ # Exported data (CSV)
├── 📂 logs/ # Application logs
├── 📂 tests/ # Unit tests
│
├── .env # Environment variables
├── .gitignore # Git ignore file
├── requirements.txt # Python dependencies
└── README.md # This file
```


---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sara12-2/Study_Smart_AI
cd Study_Smart_AI
```

### 2. Create Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```


### 4. Run the Application

#### Development Mode

```bash
python web/app.py
```

#### Using Flask

```bash
flask run --host=0.0.0.0 --port=5000
```

### 5. Access the Application

Open your browser and visit:

```text
http://localhost:5000
```

---

# 📖 How to Use

## 1. Add a Study Session

Click the **"Add Session"** button or press **Ctrl + N**.

Fill in:

- 📚 **Subject** — What you studied
- ⏱️ **Duration** — Minutes spent
- 📱 **Distractions** — Number of interruptions
- 😊 **Mood** — How you felt (1–5)
- 📝 **Notes** — What you learned

Click **"Save Session"**.

---

## 2. Track Your Progress

- 📊 **Dashboard** — View today's summary & stats
- 📈 **Weekly Charts** — See productivity trends
- 📚 **Subjects** — Analyze performance by subject
- 🏆 **Achievements** — Unlock milestones as you study

---

## 3. Get AI Insights

- 🤖 **AI Insights** — View personalized recommendations
- 📊 **Productivity Analysis** — See patterns & trends
- 🎯 **Optimal Times** — Know when you study best
- 💡 **Smart Tips** — Get actionable advice

---

## 4. Customize Settings

- 🌙 **Theme** — Switch between Light / Dark / Auto
- 🌐 **Language** — Choose English, Urdu, or Hindi
- ⏰ **Time Format** — 12-hour or 24-hour
- 📅 **Goals** — Set daily/weekly study targets
- 🔔 **Notifications** — Enable or disable reminders

---

# ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl + 1** | Navigate to Dashboard |
| **Ctrl + 2** | Navigate to Sessions |
| **Ctrl + 3** | Navigate to Subjects |
| **Ctrl + 4** | Navigate to AI Insights |
| **Ctrl + 5** | Navigate to Settings |


---

# 🧪 Running Tests

Run all tests:

```bash
python -m pytest tests/
```

Run a specific test file:

```bash
python -m pytest tests/test_session.py
```

Run tests with coverage:

```bash
python -m pytest --cov=src tests/
```

---

# 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions` | Get all sessions |
| POST | `/api/sessions` | Add new session |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/api/stats` | Get statistics |
| GET | `/api/dashboard` | Dashboard data |
| GET | `/api/weekly` | Weekly report |
| GET | `/api/subjects` | Subject analysis |
| GET | `/api/insights` | AI insights |
| GET | `/api/predictions` | AI predictions |
| GET | `/api/recommendations` | Recommendations |
| GET | `/api/settings` | Get settings |
| POST | `/api/settings` | Update settings |
| POST | `/api/settings/reset` | Reset settings |
| GET | `/api/analytics/export/csv` | Export data |
| GET | `/api/health` | Health check |

---

# 🧑‍💻 Contributing

1. Fork the repository.

2. Create a feature branch:

```bash
git checkout -b feature/amazing-feature
```

3. Commit your changes:

```bash
git commit -m "Add amazing feature"
```

4. Push your branch:

```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request.

---

# 🙏 Acknowledgments

- Font Awesome — Premium icon library
- Google Fonts — Inter typography
- Flask Community — Web framework
- Scikit-learn — Machine learning algorithms

---

# 📞 Contact

**Project Maintainer:** [Sara Manzoor]

**Email:** saramanzoor76@gmail.com

**GitHub:** https://github.com/Sara12-2

---

# ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub!

---
