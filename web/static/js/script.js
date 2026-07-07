// ==========================================
// SMART STUDY SYSTEM - PREMIUM JAVASCRIPT v5.0
// FULLY FIXED - Navigation Working + Streak Fixed
// ==========================================

// ==========================================
// GLOBAL STATE
// ==========================================
let currentPage = 'dashboard';
let allSessions = [];
let settings = {};

// ==========================================
// DOM READY - Initialize Everything
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 StudySmart AI Loading...');
    
    // Update date
    updateDate();
    
    // Load dark mode preference
    loadDarkModePreference();
    
    // Load all data
    loadDashboard();
    loadStats();
    loadSessions();
    loadSettingsPage();
    
    // Setup all event listeners
    setupEventListeners();
    
    console.log('✅ StudySmart AI loaded successfully!');
    console.log('⌨️ Keyboard shortcuts: Ctrl+N, Ctrl+1-5, Escape');
});

// ==========================================
// SETUP EVENT LISTENERS - FIXED NAVIGATION
// ==========================================
function setupEventListeners() {
    console.log('🔧 Setting up event listeners...');
    
    // ===== NAVIGATION - FIXED =====
    // Method 1: Using data-page attribute
    document.querySelectorAll('.nav-item[data-page]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const page = this.dataset.page;
            console.log(`🔄 Navigating to: ${page}`);
            if (page) navigateTo(page);
        });
    });
    
    // Method 2: Direct ID based navigation (backup)
    const navMap = {
        'nav-dashboard': 'dashboard',
        'nav-sessions': 'sessions',
        'nav-subjects': 'subjects',
        'nav-insights': 'insights',
        'nav-settings': 'settings'
    };
    
    Object.entries(navMap).forEach(([id, page]) => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log(`🔄 Navigate (ID) to: ${page}`);
                navigateTo(page);
            });
        }
    });
    
    // ===== DARK MODE =====
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleDarkMode();
        });
    }
    
    // ===== ADD SESSION =====
    const addBtn = document.getElementById('addSessionBtn');
    if (addBtn) {
        addBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showAddModal();
        });
    }
    
    // ===== CLOSE MODAL =====
    const closeBtn = document.getElementById('closeModalBtn');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }
    
    // ===== EXPORT =====
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exportData();
        });
    }
    
    // ===== REFRESH BUTTONS =====
    const refreshWeekly = document.getElementById('refreshWeeklyBtn');
    if (refreshWeekly) {
        refreshWeekly.addEventListener('click', function(e) {
            e.preventDefault();
            loadWeeklyChart();
        });
    }
    
    const refreshTrends = document.getElementById('refreshTrendsBtn');
    if (refreshTrends) {
        refreshTrends.addEventListener('click', function(e) {
            e.preventDefault();
            loadTrends();
        });
    }
    
    const refreshSessions = document.getElementById('refreshSessionsBtn');
    if (refreshSessions) {
        refreshSessions.addEventListener('click', function(e) {
            e.preventDefault();
            loadSessions();
        });
    }
    
    const refreshSubjects = document.getElementById('refreshSubjectsBtn');
    if (refreshSubjects) {
        refreshSubjects.addEventListener('click', function(e) {
            e.preventDefault();
            loadSubjects();
        });
    }
    
    const refreshInsights = document.getElementById('refreshInsightsBtn');
    if (refreshInsights) {
        refreshInsights.addEventListener('click', function(e) {
            e.preventDefault();
            loadInsights();
        });
    }
    
    const refreshSettings = document.getElementById('refreshSettingsBtn');
    if (refreshSettings) {
        refreshSettings.addEventListener('click', function(e) {
            e.preventDefault();
            loadSettingsPage();
        });
    }
    
    // ===== FILTERS =====
    const filterDate = document.getElementById('filterDate');
    if (filterDate) {
        filterDate.addEventListener('change', applyFilters);
    }
    
    const filterSubject = document.getElementById('filterSubject');
    if (filterSubject) {
        filterSubject.addEventListener('change', applyFilters);
    }
    
    const searchSessions = document.getElementById('searchSessions');
    if (searchSessions) {
        searchSessions.addEventListener('keyup', applyFilters);
    }
    
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearFilters();
        });
    }
    
    // ===== SESSION FORM =====
    const sessionForm = document.getElementById('sessionForm');
    if (sessionForm) {
        sessionForm.addEventListener('submit', handleSessionSubmit);
    }
    
    // ===== MODAL OVERLAY =====
    const modal = document.getElementById('addModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
    }
    
    console.log('✅ All event listeners setup complete');
}

// ==========================================
// NAVIGATION - FIXED
// ==========================================
function navigateTo(page) {
    console.log(`📍 Navigating to: ${page}`);
    currentPage = page;
    
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
        p.style.display = 'none';
    });
    
    // Show target page
    const targetPage = document.getElementById(`page-${page}`);
    if (targetPage) {
        targetPage.style.display = 'block';
        // Small delay for smooth transition
        setTimeout(() => {
            targetPage.classList.add('active');
        }, 10);
        console.log(`✅ Page ${page} displayed`);
    } else {
        console.error(`❌ Page ${page} not found`);
    }
    
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navItem = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (navItem) {
        navItem.classList.add('active');
        console.log(`✅ Nav item ${page} activated`);
    }
    
    // Update page title
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
    
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle && titles[page]) {
        pageTitle.innerHTML = `<i class="fas ${icons[page]}"></i> ${titles[page]}`;
    }
    
    closeModal();
    
    // Load page content
    if (page === 'dashboard') {
        loadDashboard();
        loadStats();
        loadWeeklyChart();
        loadTrends();
        loadStreak();
        loadAIInsight();
    } else if (page === 'sessions') {
        loadSessions();
    } else if (page === 'subjects') {
        loadSubjects();
    } else if (page === 'insights') {
        loadInsights();
    } else if (page === 'settings') {
        loadSettingsPage();
    }
}

// ==========================================
// SHOW TOAST
// ==========================================
function showToast(message, type) {
    type = type || 'success';
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position:fixed;top:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;max-width:420px;width:100%;pointer-events:none;';
        document.body.appendChild(container);
    }
    
    const config = {
        success: { color: '#2ECC71', icon: 'fa-check-circle' },
        error: { color: '#E74C3C', icon: 'fa-exclamation-circle' },
        warning: { color: '#F39C12', icon: 'fa-exclamation-triangle' },
        info: { color: '#3498DB', icon: 'fa-info-circle' }
    };
    const cfg = config[type] || config.info;
    const isDark = document.body.classList.contains('dark-mode');
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: ${isDark ? 'rgba(45,45,68,0.95)' : 'rgba(255,255,255,0.95)'};
        color: ${isDark ? '#e0e0e0' : '#2D3436'};
        padding: 14px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        border-left: 4px solid ${cfg.color};
        animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        pointer-events: auto;
        backdrop-filter: blur(20px);
        border: 1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.2)'};
        max-width: 400px;
        width: 100%;
    `;
    toast.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;background:${cfg.color}22;flex-shrink:0;">
            <i class="fas ${cfg.icon}" style="color:${cfg.color};font-size:16px;"></i>
        </div>
        <span style="flex:1;font-weight:500;line-height:1.4;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:#95A5A6;cursor:pointer;font-size:16px;padding:4px;">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        setTimeout(() => toast.remove(), 350);
    }, 3500);
}

// ==========================================
// KEYBOARD SHORTCUTS
// ==========================================
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('addModal');
    const isModalOpen = modal && modal.style.display === 'flex';
    
    // Ctrl+N - New Session
    if (e.ctrlKey && (e.key === 'n' || e.key === 'N')) {
        e.preventDefault();
        showAddModal();
        return;
    }
    
    // Ctrl+1-5 - Navigation
    if (e.ctrlKey && e.key >= '1' && e.key <= '5') {
        e.preventDefault();
        const pages = ['dashboard', 'sessions', 'subjects', 'insights', 'settings'];
        const idx = parseInt(e.key) - 1;
        if (idx < pages.length) navigateTo(pages[idx]);
        return;
    }
    
    // Escape - Close Modal
    if (e.key === 'Escape' || e.key === 'Esc') {
        if (isModalOpen) {
            e.preventDefault();
            closeModal();
        }
    }
});

// ==========================================
// DARK MODE
// ==========================================
function loadDarkModePreference() {
    try {
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            const icon = document.getElementById('darkModeIcon');
            if (icon) icon.className = 'fas fa-sun';
        }
    } catch(e) {}
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    
    const icon = document.getElementById('darkModeIcon');
    if (icon) icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    
    showToast(isDark ? '🌙 Dark mode enabled' : '☀️ Light mode enabled', 'info');
}

// ==========================================
// MODAL
// ==========================================
function showAddModal() {
    const modal = document.getElementById('addModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
        document.getElementById('sessionForm').reset();
        setTimeout(() => {
            const input = document.getElementById('subjectInput');
            if (input) input.focus();
        }, 100);
    }
}

function closeModal() {
    const modal = document.getElementById('addModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

// ==========================================
// HANDLE SESSION SUBMIT
// ==========================================
function handleSessionSubmit(e) {
    e.preventDefault();
    
    const subject = document.getElementById('subjectInput').value.trim();
    const duration = parseInt(document.getElementById('durationInput').value);
    const distractions = parseInt(document.getElementById('distractionsInput').value) || 0;
    const mood = parseInt(document.getElementById('moodInput').value) || null;
    const notes = document.getElementById('notesInput').value.trim() || null;
    
    if (!subject || !duration) {
        showToast('Please fill in subject and duration', 'warning');
        return;
    }
    
    const data = { subject, duration, distractions, mood, notes };
    
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    
    fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => {
        if (!res.ok) throw new Error('Network error');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            closeModal();
            showToast('✅ Session added successfully!', 'success');
            loadDashboard();
            loadSessions();
            loadSubjects();
            loadInsights();
            loadStats();
        } else {
            showToast('❌ Error: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(() => showToast('❌ Error adding session', 'error'))
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-save"></i> Save Session';
    });
}

// ==========================================
// DASHBOARD
// ==========================================
function loadDashboard() {
    const today = new Date();
    const todayDate = document.getElementById('todayDate');
    if (todayDate) {
        todayDate.textContent = today.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    
    fetch('/api/dashboard')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            const container = document.getElementById('todaySummary');
            if (data.success && data.data) {
                const d = data.data;
                container.innerHTML = `
                    <div class="summary-row">
                        <span><i class="fas fa-book"></i>Sessions</span>
                        <strong>${d.total_sessions || 0}</strong>
                    </div>
                    <div class="summary-row">
                        <span><i class="fas fa-clock"></i>Total Time</span>
                        <strong>${d.total_time || 0} min</strong>
                    </div>
                    <div class="summary-row">
                        <span><i class="fas fa-rocket"></i>Avg Productivity</span>
                        <strong style="color:${d.avg_productivity >= 70 ? '#2ECC71' : d.avg_productivity >= 50 ? '#F39C12' : '#E74C3C'}">${d.avg_productivity || 0}%</strong>
                    </div>
                    <div class="summary-row">
                        <span><i class="fas fa-exclamation-triangle"></i>Distractions</span>
                        <strong>${d.total_distractions || 0}</strong>
                    </div>
                    ${d.best_subject && d.best_subject.name ? `
                        <div class="summary-row">
                            <span><i class="fas fa-trophy"></i>Best Subject</span>
                            <strong>${d.best_subject.name} (${d.best_subject.score}%)</strong>
                        </div>
                    ` : ''}
                    ${d.peak_hour ? `
                        <div class="summary-row">
                            <span><i class="fas fa-clock"></i>Peak Hour</span>
                            <strong>${String(d.peak_hour).padStart(2, '0')}:00</strong>
                        </div>
                    ` : ''}
                `;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>No sessions today. Start tracking!</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            document.getElementById('todaySummary').innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading dashboard</p>
                </div>
            `;
        });
    
    loadSubjectBreakdown();
}

// ==========================================
// SUBJECT BREAKDOWN
// ==========================================
function loadSubjectBreakdown() {
    fetch('/api/subjects')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            const container = document.getElementById('subjectBreakdown');
            if (data.success && data.data && data.data.subjects) {
                let html = '<div class="subject-grid">';
                data.data.subjects.slice(0, 6).forEach(([subject, metrics]) => {
                    const pct = metrics.avg_productivity || 0;
                    const color = pct >= 70 ? '#2ECC71' : pct >= 50 ? '#F39C12' : '#E74C3C';
                    html += `
                        <div class="subject-card">
                            <div class="subject-card-icon" style="background:${color}20;color:${color};">
                                <i class="fas fa-book"></i>
                            </div>
                            <div class="subject-card-name">${subject}</div>
                            <div class="subject-card-score" style="color:${color};">${pct}%</div>
                            <div class="subject-card-stats">
                                <span><i class="fas fa-clock"></i> ${metrics.total_time || 0} min</span>
                                <span><i class="fas fa-layer-group"></i> ${metrics.sessions || 0}</span>
                            </div>
                            <div class="subject-card-progress">
                                <div class="progress-fill" style="width:${pct}%;background:${color};"></div>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
                
                const bestSubject = document.getElementById('statBestSubject');
                if (bestSubject && data.data.best_subject) {
                    bestSubject.textContent = data.data.best_subject[0];
                }
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-layer-group"></i>
                        <p>No subjects yet. Add sessions!</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            document.getElementById('subjectBreakdown').innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading subjects</p>
                </div>
            `;
        });
}

// ==========================================
// WEEKLY CHART
// ==========================================
function loadWeeklyChart() {
    const container = document.getElementById('weeklyChart');
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Loading chart...
        </div>
    `;
    
    fetch('/api/weekly')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success && data.data && data.data.weekly_reports) {
                const reports = data.data.weekly_reports.slice(-5);
                let bars = '';
                const maxScore = Math.max(...reports.map(r => r.avg_productivity), 1);
                
                reports.forEach(r => {
                    const height = (r.avg_productivity / maxScore) * 150;
                    const color = r.avg_productivity >= 70 ? '#2ECC71' : r.avg_productivity >= 50 ? '#F39C12' : '#E74C3C';
                    bars += `
                        <div style="flex:1;text-align:center;">
                            <div style="height:${height}px;background:${color};border-radius:6px 6px 0 0;transition:height 0.6s ease;position:relative;cursor:pointer;">
                                <span style="position:absolute;top:-22px;left:50%;transform:translateX(-50%);font-size:11px;font-weight:600;color:var(--text-primary);">${r.avg_productivity}%</span>
                            </div>
                            <div style="font-size:11px;color:var(--text-muted);margin-top:6px;">${r.week}</div>
                        </div>
                    `;
                });
                
                container.innerHTML = `
                    <div style="display:flex;align-items:flex-end;gap:12px;height:180px;padding:16px 0;">
                        ${bars}
                    </div>
                    <div style="text-align:center;font-size:13px;color:var(--text-muted);margin-top:8px;">
                        <i class="fas fa-chart-line"></i> Productivity trend over ${reports.length} weeks
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-chart-bar"></i>
                        <p>No weekly data available</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading weekly chart</p>
                </div>
            `;
        });
}

// ==========================================
// 30-DAY TRENDS
// ==========================================
function loadTrends() {
    const container = document.getElementById('trendsChart');
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Loading trends...
        </div>
    `;
    
    fetch('/api/trends')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success && data.data && data.data.daily_productivity) {
                const days = Object.keys(data.data.daily_productivity).slice(-30);
                const values = Object.values(data.data.daily_productivity).slice(-30);
                
                if (days.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-chart-line"></i>
                            <p>Not enough data for trends</p>
                        </div>
                    `;
                    return;
                }
                
                const maxVal = Math.max(...values, 1);
                let bars = '';
                days.forEach((day, i) => {
                    const height = (values[i] / maxVal) * 140;
                    const color = values[i] >= 70 ? '#2ECC71' : values[i] >= 50 ? '#F39C12' : '#E74C3C';
                    bars += `
                        <div style="flex:1;text-align:center;">
                            <div style="height:${height}px;background:${color};border-radius:4px 4px 0 0;transition:height 0.6s ease;position:relative;cursor:pointer;">
                                <span style="position:absolute;top:-18px;left:50%;transform:translateX(-50%);font-size:9px;font-weight:600;color:var(--text-primary);">${values[i]}%</span>
                            </div>
                            <div style="font-size:8px;color:var(--text-muted);margin-top:4px;">${day.slice(5)}</div>
                        </div>
                    `;
                });
                
                container.innerHTML = `
                    <div style="display:flex;align-items:flex-end;gap:4px;height:170px;padding:16px 0;">
                        ${bars}
                    </div>
                    <div style="text-align:center;font-size:13px;color:var(--text-muted);margin-top:8px;">
                        <i class="fas fa-chart-line"></i> ${data.data.trend_direction || 'Stable'} trend (${days.length} days)
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-chart-line"></i>
                        <p>Not enough data for trends</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading trends</p>
                </div>
            `;
        });
}

// ==========================================
// STREAK - FIXED VERSION
// ==========================================
function loadStreak() {
    const container = document.getElementById('streakDisplay');
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Loading streak...
        </div>
    `;
    
    // First get all sessions to calculate streak properly
    fetch('/api/sessions')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            let streak = 0;
            let sessions = data.data || [];
            
            if (sessions.length > 0) {
                // Extract unique dates
                const dates = new Set();
                sessions.forEach(s => {
                    if (s.timestamp) {
                        const date = s.timestamp.split('T')[0];
                        dates.add(date);
                    }
                });
                
                // Calculate streak from today backwards
                let checkDate = new Date();
                checkDate.setHours(0, 0, 0, 0);
                
                while (true) {
                    const dateStr = checkDate.toISOString().split('T')[0];
                    if (dates.has(dateStr)) {
                        streak++;
                        checkDate.setDate(checkDate.getDate() - 1);
                    } else {
                        break;
                    }
                }
            }
            
            // Determine status and color
            let status, statusColor, emoji;
            if (streak >= 5) {
                status = 'On Fire';
                statusColor = '#F39C12';
                emoji = '🔥';
            } else if (streak >= 3) {
                status = 'Building';
                statusColor = '#2ECC71';
                emoji = '💪';
            } else if (streak >= 1) {
                status = 'Starting';
                statusColor = '#3498DB';
                emoji = '🌱';
            } else {
                status = 'No Streak';
                statusColor = '#95A5A6';
                emoji = '📭';
            }
            
            container.innerHTML = `
                <div style="display:flex;align-items:center;gap:16px;padding:8px 0;">
                    <div style="width:56px;height:56px;border-radius:50%;background:${statusColor}22;display:flex;align-items:center;justify-content:center;font-size:28px;color:${statusColor};">
                        ${emoji}
                    </div>
                    <div>
                        <div style="font-size:28px;font-weight:800;color:${statusColor};">${streak} day${streak !== 1 ? 's' : ''}</div>
                        <div style="font-size:14px;color:var(--text-muted);">${status}</div>
                    </div>
                </div>
            `;
        })
        .catch(() => {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading streak</p>
                </div>
            `;
        });
}

// ==========================================
// AI INSIGHT (Dashboard)
// ==========================================
function loadAIInsight() {
    fetch('/api/optimal-times')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            const container = document.getElementById('aiInsight');
            if (data.success && data.data && !data.data.error) {
                const d = data.data;
                container.innerHTML = `
                    <div class="insight-box">
                        <h4><i class="fas fa-clock"></i> Best Time to Study</h4>
                        <p>${d.best_hour !== null ? String(d.best_hour).padStart(2, '0') + ':00' : 'N/A'}</p>
                        <div class="sub-text">${d.best_hour_productivity || 0}% productivity</div>
                    </div>
                    <div style="font-size:14px;color:var(--text-secondary);padding:4px 0;">
                        <p><i class="fas fa-lightbulb" style="color:#F39C12;margin-right:8px;"></i> ${d.recommendation || 'Keep tracking to get personalized recommendations!'}</p>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-robot"></i>
                        <p>Add more sessions for AI insights</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            document.getElementById('aiInsight').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot"></i>
                    <p>Add more sessions for AI insights</p>
                </div>
            `;
        });
}

// ==========================================
// SESSIONS
// ==========================================
function loadSessions() {
    const container = document.getElementById('sessionsList');
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Loading sessions...
        </div>
    `;
    
    fetch('/api/sessions')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success && data.data && data.data.length > 0) {
                allSessions = data.data;
                renderSessions(data.data);
                updateSubjectFilter(data.data);
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-book-open"></i>
                        <p>No sessions found. Start tracking!</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading sessions</p>
                </div>
            `;
        });
}

function renderSessions(sessions) {
    const container = document.getElementById('sessionsList');
    let html = '';
    sessions.slice().reverse().forEach((s, i) => {
        const score = s.productivity_score || 0;
        const scoreClass = score >= 70 ? 'high' : score >= 50 ? 'medium' : 'low';
        const date = s.timestamp ? s.timestamp.substring(0, 16).replace('T', ' ') : 'Unknown';
        const sessionId = s.id || s.session_id || i;
        
        html += `
            <div class="session-item" data-id="${sessionId}">
                <div class="session-info">
                    <div class="session-subject">${s.subject}</div>
                    <div class="session-meta">
                        <i class="fas fa-clock"></i> ${s.duration}min
                        <i class="fas fa-calendar-alt"></i> ${date}
                        ${s.distractions ? `<i class="fas fa-exclamation-triangle"></i> ${s.distractions}` : ''}
                        ${s.mood ? `<i class="fas fa-smile"></i> ${s.mood}/5` : ''}
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <span class="session-score ${scoreClass}">${score}%</span>
                    <div class="session-actions">
                        <button class="delete-session-btn" data-id="${sessionId}" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
    
    // Attach delete events
    document.querySelectorAll('.delete-session-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            deleteSession(id);
        });
    });
}

function updateSubjectFilter(sessions) {
    const select = document.getElementById('filterSubject');
    if (!select) return;
    const current = select.value;
    const subjects = [...new Set(sessions.map(s => s.subject))];
    select.innerHTML = '<option value="">All Subjects</option>';
    subjects.forEach(s => {
        select.innerHTML += `<option value="${s}">${s}</option>`;
    });
    select.value = current;
}

function applyFilters() {
    const date = document.getElementById('filterDate').value;
    const subject = document.getElementById('filterSubject').value;
    const search = document.getElementById('searchSessions').value.toLowerCase();
    
    let filtered = [...allSessions];
    if (date) filtered = filtered.filter(s => s.timestamp && s.timestamp.startsWith(date));
    if (subject) filtered = filtered.filter(s => s.subject === subject);
    if (search) filtered = filtered.filter(s => 
        s.subject.toLowerCase().includes(search) || 
        (s.notes && s.notes.toLowerCase().includes(search))
    );
    renderSessions(filtered);
}

function clearFilters() {
    document.getElementById('filterDate').value = '';
    document.getElementById('filterSubject').value = '';
    document.getElementById('searchSessions').value = '';
    renderSessions(allSessions);
    showToast('Filters cleared', 'info');
}

function deleteSession(id) {
    if (!confirm('Delete this session?')) return;
    
    fetch(`/api/sessions/${id}`, { method: 'DELETE' })
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success) {
                showToast('Session deleted', 'warning');
                loadSessions();
                loadDashboard();
                loadSubjects();
                loadInsights();
                loadStats();
            } else {
                showToast('Error deleting session', 'error');
            }
        })
        .catch(() => showToast('Error deleting session', 'error'));
}

// ==========================================
// SUBJECTS (Page)
// ==========================================
function loadSubjects() {
    const container = document.getElementById('subjectAnalysis');
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Loading subjects...
        </div>
    `;
    
    fetch('/api/subjects')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success && data.data && data.data.subjects) {
                let html = '';
                data.data.subjects.forEach(([subject, metrics]) => {
                    const pct = metrics.avg_productivity || 0;
                    const color = pct >= 70 ? '#2ECC71' : pct >= 50 ? '#F39C12' : '#E74C3C';
                    html += `
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid var(--border);">
                            <div>
                                <div style="font-weight:600;color:var(--text-primary);">${subject}</div>
                                <div style="font-size:12px;color:var(--text-muted);">
                                    <i class="fas fa-clock"></i> ${metrics.total_time || 0} min
                                    <i class="fas fa-layer-group" style="margin-left:12px;"></i> ${metrics.sessions || 0} sessions
                                </div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:24px;font-weight:800;color:${color};">${pct}%</div>
                                <div style="font-size:11px;color:var(--text-muted);">
                                    <i class="fas fa-exclamation-triangle"></i> ${metrics.avg_distractions || 0} distractions
                                </div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-layer-group"></i>
                        <p>No subjects yet. Add sessions!</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            container.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading subjects</p>
                </div>
            `;
        });
}

// ==========================================
// AI INSIGHTS (Page)
// ==========================================
function loadInsights() {
    const container = document.getElementById('aiInsights');
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Loading insights...
        </div>
    `;
    
    fetch('/api/insights')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success && data.data) {
                const insights = data.data;
                let html = '';
                
                if (insights.analysis && insights.analysis.overall_stats) {
                    const stats = insights.analysis.overall_stats;
                    html += `
                        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;">
                            <div style="background:var(--bg);padding:12px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);">Mean</div>
                                <div style="font-size:20px;font-weight:800;color:var(--text-primary);">${stats.mean || 0}%</div>
                            </div>
                            <div style="background:var(--bg);padding:12px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);">Median</div>
                                <div style="font-size:20px;font-weight:800;color:var(--text-primary);">${stats.median || 0}%</div>
                            </div>
                            <div style="background:var(--bg);padding:12px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);">Consistency</div>
                                <div style="font-size:20px;font-weight:800;color:var(--text-primary);">${insights.analysis.consistency || 0}%</div>
                            </div>
                            <div style="background:var(--bg);padding:12px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);">Sessions</div>
                                <div style="font-size:20px;font-weight:800;color:var(--text-primary);">${insights.total_sessions || 0}</div>
                            </div>
                        </div>
                    `;
                }
                
                if (insights.recommendations && insights.recommendations.length > 0) {
                    html += `
                        <div style="background:var(--bg);padding:16px 20px;border-radius:12px;border-left:4px solid var(--primary);">
                            <div style="font-weight:600;color:var(--text-primary);margin-bottom:8px;"><i class="fas fa-lightbulb" style="color:#F39C12;margin-right:8px;"></i>Recommendations</div>
                            <ul style="list-style:none;padding:0;margin:0;">
                    `;
                    insights.recommendations.forEach(rec => {
                        html += `<li style="padding:4px 0;color:var(--text-secondary);font-size:14px;"><i class="fas fa-arrow-right" style="color:var(--primary);margin-right:8px;"></i>${rec}</li>`;
                    });
                    html += `
                            </ul>
                        </div>
                    `;
                }
                
                if (!html) {
                    html = `
                        <div class="empty-state">
                            <i class="fas fa-robot"></i>
                            <p>Add more sessions for AI insights</p>
                        </div>
                    `;
                }
                
                container.innerHTML = html;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-robot"></i>
                        <p>Add more sessions for AI insights</p>
                    </div>
                `;
            }
        })
        .catch(() => {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot"></i>
                    <p>Add more sessions for AI insights</p>
                </div>
            `;
        });
}

// ==========================================
// SETTINGS
// ==========================================
function loadSettingsPage() {
    const container = document.getElementById('settingsContent');
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Loading settings...
        </div>
    `;
    
    fetch('/api/settings')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success) {
                settings = { ...settings, ...data.data };
                renderSettingsForm(settings);
            } else {
                renderSettingsForm(settings);
            }
        })
        .catch(() => renderSettingsForm(settings));
}

function renderSettingsForm(s) {
    const container = document.getElementById('settingsContent');
    container.innerHTML = `
        <form id="settingsForm">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:16px;">
                <div class="settings-group">
                    <label><i class="fas fa-calendar-day"></i> Daily Goal (min)</label>
                    <input type="number" id="settingDailyGoal" class="settings-input" value="${s.daily_goal || 120}" min="30" max="480">
                </div>
                <div class="settings-group">
                    <label><i class="fas fa-calendar-week"></i> Weekly Goal (min)</label>
                    <input type="number" id="settingWeeklyGoal" class="settings-input" value="${s.weekly_goal || 600}" min="120" max="1680">
                </div>
                <div class="settings-group">
                    <label><i class="fas fa-book"></i> Default Subject</label>
                    <input type="text" id="settingDefaultSubject" class="settings-input" value="${s.default_subject || ''}" placeholder="e.g., Python">
                </div>
                <div class="settings-group">
                    <label><i class="fas fa-clock"></i> Time Format</label>
                    <select id="settingTimeFormat" class="settings-input">
                        <option value="12h" ${s.time_format === '12h' ? 'selected' : ''}>12-hour (AM/PM)</option>
                        <option value="24h" ${s.time_format === '24h' ? 'selected' : ''}>24-hour</option>
                    </select>
                </div>
                <div class="settings-group">
                    <label><i class="fas fa-bell"></i> Reminder (min)</label>
                    <input type="number" id="settingReminderInterval" class="settings-input" value="${s.reminder_interval || 60}" min="15" max="180">
                </div>
                <div class="settings-group">
                    <label><i class="fas fa-database"></i> Backup (days)</label>
                    <input type="number" id="settingBackupInterval" class="settings-input" value="${s.backup_interval || 7}" min="1" max="30">
                </div>
            </div>
            
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
                ${['notifications', 'study_reminder', 'auto_backup'].map(f => {
                    const labels = {
                        notifications: '<i class="fas fa-bell"></i> Notifications',
                        study_reminder: '<i class="fas fa-clock"></i> Study Reminder',
                        auto_backup: '<i class="fas fa-database"></i> Auto Backup'
                    };
                    const val = s[f] !== undefined ? s[f] : true;
                    const id = 'setting' + f.charAt(0).toUpperCase() + f.slice(1);
                    return `
                        <div class="toggle-group">
                            <label class="toggle-label">
                                <span>${labels[f]}</span>
                                <div class="toggle-switch ${val ? 'active' : ''}" onclick="toggleSwitch(this)">
                                    <input type="hidden" id="${id}" value="${val}">
                                    <span class="toggle-slider"></span>
                                </div>
                            </label>
                        </div>
                    `;
                }).join('')}
            </div>
            
            <div class="settings-actions">
                <button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Save Settings</button>
                <button type="button" class="btn btn-secondary" onclick="resetSettings()"><i class="fas fa-undo"></i> Reset</button>
                <button type="button" class="btn btn-danger" onclick="clearAllData()"><i class="fas fa-trash"></i> Clear Data</button>
            </div>
            
            <div id="settingsMessage"></div>
        </form>
    `;
    
    // Attach settings form submit
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
        settingsForm.addEventListener('submit', saveSettings);
    }
}

function toggleSwitch(element) {
    element.classList.toggle('active');
    const hiddenInput = element.querySelector('input[type="hidden"]');
    if (hiddenInput) hiddenInput.value = element.classList.contains('active');
}

function saveSettings(event) {
    event.preventDefault();
    const newSettings = {
        daily_goal: parseInt(document.getElementById('settingDailyGoal').value) || 120,
        weekly_goal: parseInt(document.getElementById('settingWeeklyGoal').value) || 600,
        default_subject: document.getElementById('settingDefaultSubject').value || '',
        time_format: document.getElementById('settingTimeFormat').value || '24h',
        reminder_interval: parseInt(document.getElementById('settingReminderInterval').value) || 60,
        backup_interval: parseInt(document.getElementById('settingBackupInterval').value) || 7,
        notifications: document.getElementById('settingNotifications').value === 'true',
        study_reminder: document.getElementById('settingStudyReminder').value === 'true',
        auto_backup: document.getElementById('settingAutoBackup').value === 'true'
    };
    settings = { ...settings, ...newSettings };
    
    const messageEl = document.getElementById('settingsMessage');
    messageEl.innerHTML = `<div class="info-message"><i class="fas fa-spinner fa-spin"></i> Saving...</div>`;
    
    fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
    })
    .then(res => {
        if (!res.ok) throw new Error('Network error');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            messageEl.innerHTML = `<div class="success-message"><i class="fas fa-check-circle"></i> Settings saved!</div>`;
            showToast('✅ Settings saved successfully', 'success');
            setTimeout(() => messageEl.innerHTML = '', 3000);
        } else {
            messageEl.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-circle"></i> ${data.error || 'Failed to save'}</div>`;
        }
    })
    .catch(() => {
        messageEl.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-circle"></i> Error saving settings</div>`;
    });
}

function resetSettings() {
    if (!confirm('Reset all settings to default?')) return;
    const defaultSettings = {
        daily_goal: 120, weekly_goal: 600, default_subject: '',
        time_format: '24h', reminder_interval: 60, backup_interval: 7,
        notifications: true, study_reminder: true, auto_backup: true
    };
    settings = { ...settings, ...defaultSettings };
    
    fetch('/api/settings/reset', { method: 'POST' })
        .then(() => {
            showToast('Settings reset to default', 'info');
            loadSettingsPage();
        })
        .catch(() => loadSettingsPage());
}

function clearAllData() {
    if (!confirm('WARNING: Delete ALL sessions? This cannot be undone!')) return;
    if (!confirm('Are you absolutely sure?')) return;
    
    fetch('/api/clear?confirm=true', { method: 'DELETE' })
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success) {
                showToast('All data cleared', 'warning');
                loadDashboard();
                loadSessions();
                loadSubjects();
                loadInsights();
                loadStats();
            }
        })
        .catch(() => showToast('Error clearing data', 'error'));
}

// ==========================================
// EXPORT DATA
// ==========================================
function exportData() {
    const btn = document.getElementById('exportBtn');
    const originalText = btn ? btn.innerHTML : 'Export';
    if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        btn.disabled = true;
    }
    
    showToast('Preparing export...', 'info');
    
    fetch('/api/analytics/export/csv')
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Export failed'); });
            }
            return response.blob();
        })
        .then(blob => {
            if (blob.size === 0) throw new Error('No data to export');
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `study_data_${new Date().toISOString().slice(0,10)}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            showToast('✅ Data exported successfully!', 'success');
        })
        .catch(error => {
            showToast('❌ Export failed: ' + error.message, 'error');
        })
        .finally(() => {
            if (btn) {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
}

// ==========================================
// LOAD STATS
// ==========================================
function loadStats() {
    fetch('/api/stats')
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            if (data.success) {
                const sessions = data.data.total_sessions || 0;
                
                const statElements = {
                    'statSessions': sessions,
                    'statTime': (data.data.total_time || 0) + ' min',
                    'statProductivity': (data.data.avg_productivity || 0) + '%',
                    'totalSessions': sessions,
                    'sessionBadge': sessions
                };
                
                Object.entries(statElements).forEach(([id, value]) => {
                    const el = document.getElementById(id);
                    if (el) {
                        el.textContent = value;
                        el.style.transition = 'transform 0.3s ease';
                        el.style.transform = 'scale(1.1)';
                        setTimeout(() => {
                            el.style.transform = 'scale(1)';
                        }, 200);
                    }
                });
            }
        })
        .catch(() => {});
}

// ==========================================
// DATE
// ==========================================
function updateDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateEl = document.getElementById('currentDate');
    if (dateEl) {
        dateEl.innerHTML = `<i class="far fa-calendar-alt"></i> ${now.toLocaleDateString('en-US', options)}`;
    }
}