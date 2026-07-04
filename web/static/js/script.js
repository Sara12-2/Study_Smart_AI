// ==========================================
// SMART STUDY SYSTEM - PREMIUM JAVASCRIPT
// ==========================================

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        document.body.appendChild(container);
    }
    
    const colors = {
        success: '#2ECC71',
        error: '#E74C3C',
        warning: '#F39C12',
        info: '#3498DB'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        ${message}
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==========================================
// DARK MODE
// ==========================================
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    showToast(document.body.classList.contains('dark-mode') ? '🌙 Dark mode enabled' : '☀️ Light mode enabled', 'info');
}

// Check saved preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// ==========================================
// EXPORT DATA
// ==========================================
function exportData() {
    fetch('/api/analytics/export/csv')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.file;
                showToast('✅ Data exported successfully!', 'success');
            } else {
                showToast('⚠️ No data to export', 'warning');
            }
        })
        .catch(() => showToast('❌ Export failed', 'error'));
}

// ==========================================
// ACHIEVEMENTS
// ==========================================
function checkAchievements(sessions) {
    const achievements = {
        5: '🎯 5 Sessions - Great Start!',
        10: '🔥 10 Sessions - Building Momentum!',
        25: '💪 25 Sessions - Consistency!',
        50: '🏆 50 Sessions - You\'re on Fire!',
        100: '🌟 100 Sessions - Master Level!'
    };
    
    for (const [count, message] of Object.entries(achievements)) {
        if (sessions >= parseInt(count)) {
            // Confetti effect
            const colors = ['#6C63FF', '#2ECC71', '#F39C12', '#FF6584', '#3498DB'];
            for (let i = 0; i < 50; i++) {
                const confetti = document.createElement('div');
                confetti.style.cssText = `
                    position: fixed;
                    top: -10px;
                    left: ${Math.random() * 100}vw;
                    width: ${5 + Math.random() * 10}px;
                    height: ${5 + Math.random() * 10}px;
                    background: ${colors[Math.floor(Math.random() * colors.length)]};
                    border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
                    animation: confettiFall ${2 + Math.random() * 2}s ease-in forwards;
                    z-index: 9999;
                `;
                document.body.appendChild(confetti);
                setTimeout(() => confetti.remove(), 4000);
            }
            showToast(`🏆 ${message}`, 'success');
            break;
        }
    }
}

// ==========================================
// GLOBAL STATE
// ==========================================
let currentPage = 'dashboard';
let allSessions = [];

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    updateDate();
    loadDashboard();
    loadStats();
    loadSessions();
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            if (page) {
                navigateTo(page);
            }
        });
    });
    
    // Form submission
    document.getElementById('sessionForm').addEventListener('submit', addSession);
    
    // Dark mode toggle in sidebar
    const darkModeToggle = document.querySelector('.nav-item[onclick="toggleDarkMode()"]');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
});

// ==========================================
// NAVIGATION
// ==========================================
function navigateTo(page) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const navItem = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
    
    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    const pageElement = document.getElementById(`page-${page}`);
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    // Update title
    const titles = {
        dashboard: 'Dashboard',
        sessions: 'Sessions',
        subjects: 'Subjects',
        insights: 'AI Insights',
        settings: 'Settings'
    };
    const icons = {
        dashboard: 'fa-chart-pie',
        sessions: 'fa-book-open',
        subjects: 'fa-layer-group',
        insights: 'fa-robot',
        settings: 'fa-cog'
    };
    
    const titleElement = document.getElementById('pageTitle');
    if (titleElement) {
        titleElement.innerHTML = `
            <i class="fas ${icons[page]}"></i> ${titles[page]}
        `;
    }
    
    // Load content
    currentPage = page;
    switch(page) {
        case 'dashboard':
            loadDashboard();
            loadStats();
            break;
        case 'sessions':
            loadSessions();
            break;
        case 'subjects':
            loadSubjects();
            break;
        case 'insights':
            loadInsights();
            break;
        case 'settings':
            // Settings page loads its own data
            break;
    }
}

// ==========================================
// DATE
// ==========================================
function updateDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    
    const dateElements = document.querySelectorAll('#currentDate, .date-display');
    dateElements.forEach(el => {
        if (el) {
            el.innerHTML = `<i class="far fa-calendar-alt"></i> ${now.toLocaleDateString('en-US', options)}`;
        }
    });
    
    const todayDate = document.getElementById('todayDate');
    if (todayDate) {
        todayDate.textContent = now.toLocaleDateString('en-US', options);
    }
}

// ==========================================
// STATS
// ==========================================
function loadStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const sessions = data.data.total_sessions || 0;
                
                // Update stats cards
                const statSessions = document.getElementById('statSessions');
                if (statSessions) statSessions.textContent = sessions;
                
                const statTime = document.getElementById('statTime');
                if (statTime) statTime.textContent = `${data.data.total_time || 0} min`;
                
                const statProductivity = document.getElementById('statProductivity');
                if (statProductivity) statProductivity.textContent = `${data.data.avg_productivity || 0}%`;
                
                const statConsistency = document.getElementById('statConsistency');
                if (statConsistency) statConsistency.textContent = '--';
                
                // Update sidebar and badge
                const totalSessions = document.getElementById('totalSessions');
                if (totalSessions) totalSessions.textContent = sessions;
                
                const sessionBadge = document.getElementById('sessionBadge');
                if (sessionBadge) sessionBadge.textContent = sessions;
                
                // Update settings page
                const totalSessionsValue = document.getElementById('totalSessionsValue');
                if (totalSessionsValue) totalSessionsValue.textContent = sessions;
                
                const fileSizeValue = document.getElementById('fileSizeValue');
                if (fileSizeValue) fileSizeValue.textContent = data.data.file_size || '0 B';
                
                // Check achievements
                checkAchievements(sessions);
            }
        })
        .catch(err => console.error('Error loading stats:', err));
}

// ==========================================
// DASHBOARD
// ==========================================
function loadDashboard() {
    fetch('/api/dashboard')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('todaySummary');
            if (!container) return;
            
            if (data.success && data.data) {
                const d = data.data;
                container.innerHTML = `
                    <div class="summary-row">
                        <span><i class="fas fa-book" style="color:var(--primary);"></i>Sessions</span>
                        <strong>${d.total_sessions}</strong>
                    </div>
                    <div class="summary-row">
                        <span><i class="fas fa-clock" style="color:#2ECC71;"></i>Total Time</span>
                        <strong>${d.total_time} min</strong>
                    </div>
                    <div class="summary-row">
                        <span><i class="fas fa-rocket" style="color:#F39C12;"></i>Avg Productivity</span>
                        <strong style="color: ${d.avg_productivity >= 70 ? '#2ECC71' : d.avg_productivity >= 50 ? '#F39C12' : '#E74C3C'}">
                            ${d.avg_productivity}%
                        </strong>
                    </div>
                    <div class="summary-row">
                        <span><i class="fas fa-exclamation-triangle" style="color:#E74C3C;"></i>Distractions</span>
                        <strong>${d.total_distractions}</strong>
                    </div>
                    <div class="summary-row">
                        <span><i class="fas fa-trophy" style="color:#F39C12;"></i>Score</span>
                        <strong>${d.score}%</strong>
                    </div>
                    ${d.best_subject && d.best_subject.name ? `
                        <div class="summary-row">
                            <span><i class="fas fa-star" style="color:#F39C12;"></i>Best Subject</span>
                            <strong>${d.best_subject.name} (${d.best_subject.score}%)</strong>
                        </div>
                    ` : ''}
                    ${d.peak_hour ? `
                        <div class="summary-row">
                            <span><i class="fas fa-clock" style="color:var(--primary);"></i>Peak Hour</span>
                            <strong>${String(d.peak_hour).padStart(2, '0')}:00</strong>
                        </div>
                    ` : ''}
                    ${d.consistency_score ? `
                        <div class="summary-row">
                            <span><i class="fas fa-balance-scale" style="color:var(--primary);"></i>Consistency</span>
                            <strong>${d.consistency_score}%</strong>
                        </div>
                    ` : ''}
                `;
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-inbox" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>No sessions today</p>
                        <p style="font-size:13px;margin-top:4px;">Start tracking your study sessions!</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error loading dashboard:', err);
            const container = document.getElementById('todaySummary');
            if (container) {
                container.innerHTML = `
                    <p style="color:#E74C3C;text-align:center;">
                        <i class="fas fa-exclamation-circle"></i> Error loading dashboard
                    </p>
                `;
            }
        });
    
    // Load subject breakdown for dashboard
    loadSubjectBreakdown();
}

// ==========================================
// SUBJECT BREAKDOWN (Dashboard)
// ==========================================
function loadSubjectBreakdown() {
    fetch('/api/subjects')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('subjectBreakdown');
            if (!container) return;
            
            if (data.success && data.data && data.data.subjects) {
                let html = '';
                data.data.subjects.slice(0, 5).forEach(([subject, metrics]) => {
                    const pct = metrics.avg_productivity;
                    const color = pct >= 70 ? '#2ECC71' : pct >= 50 ? '#F39C12' : '#E74C3C';
                    html += `
                        <div class="subject-item">
                            <div class="subject-header">
                                <span class="name"><i class="fas fa-book"></i>${subject}</span>
                                <span class="score" style="color:${color};">${pct}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="fill" style="width:0%;background:${color};"></div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
                
                // Animate bars
                setTimeout(() => {
                    document.querySelectorAll('#subjectBreakdown .fill').forEach((bar, index) => {
                        const subjectData = data.data.subjects[index];
                        if (subjectData) {
                            bar.style.width = `${subjectData[1].avg_productivity}%`;
                        }
                    });
                }, 300);
                
                // Update best subject stat
                const statBestSubject = document.getElementById('statBestSubject');
                if (statBestSubject) {
                    statBestSubject.textContent = data.data.best_subject ? data.data.best_subject[0] : '-';
                }
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:20px 0;">
                        <i class="fas fa-layer-group" style="font-size:32px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        No subjects yet. Add sessions!
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error loading subject breakdown:', err);
            const container = document.getElementById('subjectBreakdown');
            if (container) {
                container.innerHTML = `
                    <p style="color:#E74C3C;text-align:center;">
                        <i class="fas fa-exclamation-circle"></i> Error loading subjects
                    </p>
                `;
            }
        });
}

// ==========================================
// SESSIONS
// ==========================================
function loadSessions() {
    fetch('/api/sessions')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('sessionsList');
            if (!container) return;
            
            if (data.success && data.data && data.data.length > 0) {
                allSessions = data.data;
                let html = '';
                data.data.slice().reverse().forEach((session, index) => {
                    const score = session.productivity_score || 0;
                    const scoreClass = score >= 70 ? 'score-high' : score >= 50 ? 'score-medium' : 'score-low';
                    const date = session.timestamp ? session.timestamp.substring(0, 16).replace('T', ' ') : 'Unknown';
                    const actualIndex = data.data.length - 1 - index;
                    
                    html += `
                        <div class="session-item" data-index="${actualIndex}">
                            <div class="session-info">
                                <div class="session-subject">${session.subject}</div>
                                <div class="session-meta">
                                    <i class="fas fa-clock"></i> ${session.duration}min
                                    <i class="fas fa-calendar-alt" style="margin-left:12px;"></i> ${date}
                                    ${session.distractions ? ` <i class="fas fa-exclamation-triangle" style="margin-left:12px;color:#F39C12;"></i> ${session.distractions} distractions` : ''}
                                    ${session.mood ? ` <i class="fas fa-smile" style="margin-left:12px;"></i> ${session.mood}/5` : ''}
                                </div>
                            </div>
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span class="session-score ${scoreClass}">${score}%</span>
                                <button class="btn btn-secondary btn-sm" onclick="deleteSession(${actualIndex})" style="color:#E74C3C;border-color:#E74C3C;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
                
                // Update subject filter
                updateSubjectFilter(data.data);
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-book-open" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>No sessions found</p>
                        <p style="font-size:13px;margin-top:4px;">Start tracking your study sessions!</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error loading sessions:', err);
            const container = document.getElementById('sessionsList');
            if (container) {
                container.innerHTML = `
                    <p style="color:#E74C3C;text-align:center;">
                        <i class="fas fa-exclamation-circle"></i> Error loading sessions
                    </p>
                `;
            }
        });
}

function updateSubjectFilter(sessions) {
    const select = document.getElementById('filterSubject');
    if (!select) return;
    
    const subjects = [...new Set(sessions.map(s => s.subject))];
    const currentValue = select.value;
    select.innerHTML = '<option value="">All Subjects</option>';
    subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject;
        option.textContent = subject;
        select.appendChild(option);
    });
    select.value = currentValue;
}

function refreshSessions() {
    loadSessions();
    showToast('🔄 Sessions refreshed', 'info');
}

function deleteSession(id) {
    if (!confirm('Delete this session?')) return;
    
    fetch(`/api/sessions/${id}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadSessions();
                loadStats();
                loadDashboard();
                loadSubjectBreakdown();
                showToast('✅ Session deleted successfully', 'success');
            } else {
                showToast('❌ Error deleting session', 'error');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showToast('❌ Error deleting session', 'error');
        });
}

// ==========================================
// SESSION FILTERS
// ==========================================
function applyFilters() {
    const date = document.getElementById('filterDate');
    const subject = document.getElementById('filterSubject');
    
    if (!date || !subject) return;
    
    const dateValue = date.value;
    const subjectValue = subject.value;
    
    fetch(`/api/sessions?date=${dateValue}&subject=${subjectValue}`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('sessionsList');
            if (!container) return;
            
            if (data.success && data.data && data.data.length > 0) {
                let html = '';
                data.data.slice().reverse().forEach((session, index) => {
                    const score = session.productivity_score || 0;
                    const scoreClass = score >= 70 ? 'score-high' : score >= 50 ? 'score-medium' : 'score-low';
                    const dateStr = session.timestamp ? session.timestamp.substring(0, 16).replace('T', ' ') : 'Unknown';
                    const actualIndex = data.data.length - 1 - index;
                    
                    html += `
                        <div class="session-item">
                            <div class="session-info">
                                <div class="session-subject">${session.subject}</div>
                                <div class="session-meta">
                                    <i class="fas fa-clock"></i> ${session.duration}min
                                    <i class="fas fa-calendar-alt" style="margin-left:12px;"></i> ${dateStr}
                                    ${session.distractions ? ` <i class="fas fa-exclamation-triangle" style="margin-left:12px;color:#F39C12;"></i> ${session.distractions} distractions` : ''}
                                    ${session.mood ? ` <i class="fas fa-smile" style="margin-left:12px;"></i> ${session.mood}/5` : ''}
                                </div>
                            </div>
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span class="session-score ${scoreClass}">${score}%</span>
                                <button class="btn btn-secondary btn-sm" onclick="deleteSession(${actualIndex})" style="color:#E74C3C;border-color:#E74C3C;">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-search" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>No sessions found with current filters</p>
                    </div>
                `;
            }
        })
        .catch(err => console.error('Error applying filters:', err));
}

function clearFilters() {
    const date = document.getElementById('filterDate');
    const subject = document.getElementById('filterSubject');
    const search = document.getElementById('searchSessions');
    
    if (date) date.value = '';
    if (subject) subject.value = '';
    if (search) search.value = '';
    
    loadSessions();
    showToast('🧹 Filters cleared', 'info');
}

function searchSessions() {
    const query = document.getElementById('searchSessions');
    if (!query) return;
    
    const searchTerm = query.value.toLowerCase();
    const items = document.querySelectorAll('#sessionsList .session-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(searchTerm) ? 'flex' : 'none';
    });
}

// ==========================================
// SUBJECTS (Page)
// ==========================================
function loadSubjects() {
    fetch('/api/subjects')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('subjectAnalysis');
            if (!container) return;
            
            if (data.success && data.data && data.data.subjects) {
                let html = `
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
                        <div style="background:linear-gradient(135deg,#2ECC71,#27AE60);color:white;padding:16px;border-radius:12px;text-align:center;">
                            <div style="font-size:12px;opacity:0.8;">Best Subject</div>
                            <div style="font-size:20px;font-weight:700;margin-top:4px;">
                                ${data.data.best_subject ? data.data.best_subject[0] : '-'}
                            </div>
                            <div style="font-size:14px;opacity:0.9;">
                                ${data.data.best_subject ? data.data.best_subject[1].avg_productivity + '%' : ''}
                            </div>
                        </div>
                        <div style="background:linear-gradient(135deg,#E74C3C,#C0392B);color:white;padding:16px;border-radius:12px;text-align:center;">
                            <div style="font-size:12px;opacity:0.8;">Worst Subject</div>
                            <div style="font-size:20px;font-weight:700;margin-top:4px;">
                                ${data.data.worst_subject ? data.data.worst_subject[0] : '-'}
                            </div>
                            <div style="font-size:14px;opacity:0.9;">
                                ${data.data.worst_subject ? data.data.worst_subject[1].avg_productivity + '%' : ''}
                            </div>
                        </div>
                    </div>
                `;
                
                data.data.subjects.forEach(([subject, metrics]) => {
                    const pct = metrics.avg_productivity;
                    const color = pct >= 70 ? '#2ECC71' : pct >= 50 ? '#F39C12' : '#E74C3C';
                    html += `
                        <div class="subject-item">
                            <div class="subject-header">
                                <span class="name"><i class="fas fa-book" style="color:${color};"></i>${subject}</span>
                                <span class="score" style="color:${color};">${pct}%</span>
                            </div>
                            <div style="display:flex;justify-content:space-between;font-size:12px;color:#95A5A6;margin-top:2px;">
                                <span><i class="fas fa-clock"></i> ${metrics.total_time} min</span>
                                <span><i class="fas fa-layer-group"></i> ${metrics.sessions} sessions</span>
                                <span><i class="fas fa-exclamation-triangle"></i> ${metrics.avg_distractions} distractions</span>
                            </div>
                            <div class="progress-bar" style="margin-top:4px;">
                                <div class="fill" style="width:0%;background:${color};"></div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
                
                // Animate bars
                setTimeout(() => {
                    document.querySelectorAll('#subjectAnalysis .fill').forEach((bar, index) => {
                        const subjectData = data.data.subjects[index];
                        if (subjectData) {
                            bar.style.width = `${subjectData[1].avg_productivity}%`;
                        }
                    });
                }, 300);
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-layer-group" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>No subjects yet</p>
                        <p style="font-size:13px;margin-top:4px;">Add sessions to see subject analysis!</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error loading subjects:', err);
            const container = document.getElementById('subjectAnalysis');
            if (container) {
                container.innerHTML = `
                    <p style="color:#E74C3C;text-align:center;">
                        <i class="fas fa-exclamation-circle"></i> Error loading subject analysis
                    </p>
                `;
            }
        });
}

// ==========================================
// AI INSIGHTS
// ==========================================
function loadInsights() {
    fetch('/api/insights')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('aiInsights');
            if (!container) return;
            
            if (data.success && data.data) {
                const insights = data.data;
                let html = '';
                
                // Optimal Times
                if (insights.optimal_times && !insights.optimal_times.error) {
                    const ot = insights.optimal_times;
                    html += `
                        <div class="insight-box">
                            <h4><i class="fas fa-clock"></i> Best Time to Study</h4>
                            <p>${String(ot.best_hour).padStart(2, '0')}:00</p>
                            <div class="sub-text">${ot.best_hour_productivity}% average productivity</div>
                        </div>
                        <div style="padding:4px 0;margin-bottom:16px;">
                            <p style="font-size:14px;color:var(--dark);">
                                <i class="fas fa-lightbulb" style="color:#F39C12;margin-right:8px;"></i>
                                ${ot.recommendation || 'Keep tracking to get personalized recommendations!'}
                            </p>
                        </div>
                    `;
                }
                
                // Trends
                if (insights.trends && !insights.trends.error) {
                    const trendEmoji = insights.trends.trend_direction === 'improving' ? '📈' : 
                                      insights.trends.trend_direction === 'declining' ? '📉' : '➡️';
                    const trendColor = insights.trends.trend_direction === 'improving' ? '#2ECC71' : 
                                     insights.trends.trend_direction === 'declining' ? '#E74C3C' : '#F39C12';
                    html += `
                        <div style="background:#f8f9fa;padding:16px;border-radius:12px;margin-top:16px;">
                            <h4 style="margin-bottom:8px;font-size:14px;">
                                <i class="fas fa-chart-line" style="color:${trendColor};"></i> 
                                Productivity Trends (30 days)
                            </h4>
                            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center;">
                                <div>
                                    <div style="font-size:11px;color:#95A5A6;">Trend</div>
                                    <div style="font-size:16px;font-weight:700;color:${trendColor};">
                                        ${trendEmoji} ${insights.trends.trend_direction}
                                    </div>
                                </div>
                                <div>
                                    <div style="font-size:11px;color:#95A5A6;">Avg</div>
                                    <div style="font-size:16px;font-weight:700;">${insights.trends.avg_productivity}%</div>
                                </div>
                                <div>
                                    <div style="font-size:11px;color:#95A5A6;">Consistency</div>
                                    <div style="font-size:16px;font-weight:700;">${insights.trends.consistency}%</div>
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                // Recommendations
                if (insights.recommendations && insights.recommendations.length > 0) {
                    html += `
                        <div style="margin-top:16px;padding:16px;border-radius:12px;border:1px solid rgba(108,99,255,0.2);">
                            <h4 style="margin-bottom:8px;font-size:14px;">
                                <i class="fas fa-lightbulb" style="color:#F39C12;"></i> Recommendations
                            </h4>
                            <ul style="list-style:none;padding:0;">
                    `;
                    insights.recommendations.slice(0, 3).forEach(rec => {
                        html += `
                            <li style="padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.05);font-size:13px;">
                                <i class="fas fa-arrow-right" style="color:var(--primary);margin-right:8px;"></i>
                                ${rec}
                            </li>
                        `;
                    });
                    html += `
                            </ul>
                        </div>
                    `;
                }
                
                container.innerHTML = html || `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-robot" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>Add more sessions for AI insights!</p>
                        <p style="font-size:13px;margin-top:4px;">Need at least 5 sessions for analysis</p>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-robot" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>Add more sessions for AI insights!</p>
                        <p style="font-size:13px;margin-top:4px;">Need at least 5 sessions for analysis</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error loading insights:', err);
            const container = document.getElementById('aiInsights');
            if (container) {
                container.innerHTML = `
                    <p style="color:#E74C3C;text-align:center;">
                        <i class="fas fa-exclamation-circle"></i> Error loading AI insights
                    </p>
                `;
            }
        });
}

// ==========================================
// WEEKLY CHART
// ==========================================
function loadWeeklyChart() {
    fetch('/api/weekly')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('weeklyChart');
            if (!container) return;
            
            if (data.success && data.data && data.data.weekly_reports) {
                const reports = data.data.weekly_reports.slice(-5);
                let bars = '';
                const maxScore = Math.max(...reports.map(r => r.avg_productivity), 1);
                
                reports.forEach(r => {
                    const height = (r.avg_productivity / maxScore) * 150;
                    const color = r.avg_productivity >= 70 ? '#2ECC71' : r.avg_productivity >= 50 ? '#F39C12' : '#E74C3C';
                    bars += `
                        <div style="flex:1; text-align:center;">
                            <div class="chart-bar" style="height: ${height}px; background: ${color};">
                                <span class="tooltip">${r.avg_productivity}%</span>
                            </div>
                            <div class="chart-label">${r.week}</div>
                            <div style="font-size:11px; font-weight:600; color:var(--dark);">${r.avg_productivity}%</div>
                        </div>
                    `;
                });
                
                container.innerHTML = `
                    <div class="productivity-chart">${bars}</div>
                    <div style="text-align:center;font-size:13px;color:#95A5A6;margin-top:8px;">
                        <i class="fas fa-chart-line"></i> Productivity trend over last ${reports.length} weeks
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:20px 0;">
                        <i class="fas fa-chart-bar" style="font-size:32px;display:block;margin-bottom:12px;"></i>
                        No weekly data yet
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error loading weekly chart:', err);
            const container = document.getElementById('weeklyChart');
            if (container) {
                container.innerHTML = `
                    <p style="color:#E74C3C;text-align:center;">
                        <i class="fas fa-exclamation-circle"></i> Error loading chart
                    </p>
                `;
            }
        });
}

// ==========================================
// MODAL
// ==========================================
function showAddModal() {
    const modal = document.getElementById('addModal');
    if (modal) {
        modal.style.display = 'block';
        document.getElementById('sessionForm').reset();
    }
}

function closeModal() {
    const modal = document.getElementById('addModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function addSession(e) {
    e.preventDefault();
    
    const subject = document.getElementById('subject');
    const duration = document.getElementById('duration');
    const distractions = document.getElementById('distractions');
    const mood = document.getElementById('mood');
    const notes = document.getElementById('notes');
    
    if (!subject || !duration) return;
    
    const data = {
        subject: subject.value.trim(),
        duration: parseInt(duration.value),
        distractions: parseInt(distractions ? distractions.value : 0) || 0,
        mood: parseInt(mood ? mood.value : null) || null,
        notes: notes ? notes.value.trim() || null : null
    };
    
    if (!data.subject || !data.duration) {
        showToast('⚠️ Please fill in subject and duration', 'warning');
        return;
    }
    
    const btn = e.target.querySelector('button[type="submit"]');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    }
    
    fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            closeModal();
            loadStats();
            loadDashboard();
            loadSubjectBreakdown();
            loadSessions();
            loadInsights();
            loadSubjects();
            showToast('✅ Session added successfully!', 'success');
        } else {
            showToast('❌ Error: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        showToast('❌ Error adding session', 'error');
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-save"></i> Save Session';
        }
    });
}

// Click outside modal to close
window.onclick = function(event) {
    const modal = document.getElementById('addModal');
    if (modal && event.target === modal) {
        closeModal();
    }
}

// ==========================================
// AUTO REFRESH
// ==========================================
setInterval(() => {
    const activePage = document.querySelector('.page.active');
    if (activePage) {
        const id = activePage.id;
        if (id === 'page-dashboard') {
            loadStats();
            loadDashboard();
            loadSubjectBreakdown();
            loadWeeklyChart();
        } else if (id === 'page-sessions') {
            // Don't auto-refresh sessions to avoid UI flicker
        }
    }
}, 30000);

// ==========================================
// KEYBOARD SHORTCUTS
// ==========================================
document.addEventListener('keydown', function(e) {
    // Ctrl + N = New Session
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        showAddModal();
    }
    // Escape = Close Modal
    if (e.key === 'Escape') {
        closeModal();
    }
    // Ctrl + 1-5 = Navigate to pages
    if (e.ctrlKey && e.key >= '1' && e.key <= '5') {
        e.preventDefault();
        const pages = ['dashboard', 'sessions', 'subjects', 'insights', 'settings'];
        const page = pages[parseInt(e.key) - 1];
        if (page) {
            const navItem = document.querySelector(`.nav-item[data-page="${page}"]`);
            if (navItem) {
                navItem.click();
            }
        }
    }
});

console.log('🧠 Smart Study System loaded successfully!');
console.log('📚 Track your study sessions and get AI insights!');
console.log('⌨️ Keyboard Shortcuts:');
console.log('  Ctrl+N - New Session');
console.log('  Ctrl+1-5 - Navigate pages');
console.log('  Escape - Close modal');