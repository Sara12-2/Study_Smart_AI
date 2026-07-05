// ==========================================
// SMART STUDY SYSTEM - PREMIUM JAVASCRIPT
// ==========================================

// ==========================================
// TOAST NOTIFICATIONS - Premium
// ==========================================
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = `
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 420px;
            width: 100%;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }
    
    const config = {
        success: { color: '#2ECC71', icon: 'fa-check-circle', bg: 'rgba(46,204,113,0.1)' },
        error: { color: '#E74C3C', icon: 'fa-exclamation-circle', bg: 'rgba(231,76,60,0.1)' },
        warning: { color: '#F39C12', icon: 'fa-exclamation-triangle', bg: 'rgba(243,156,18,0.1)' },
        info: { color: '#3498DB', icon: 'fa-info-circle', bg: 'rgba(52,152,219,0.1)' }
    };
    
    const cfg = config[type] || config.info;
    const isDark = document.body.classList.contains('dark-mode');
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: ${isDark ? '#2d2d44' : '#ffffff'};
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
        backdrop-filter: blur(10px);
        border: 1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)'};
        max-width: 400px;
        width: 100%;
    `;
    
    toast.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;background:${cfg.bg};flex-shrink:0;">
            <i class="fas ${cfg.icon}" style="color:${cfg.color};font-size:16px;"></i>
        </div>
        <span style="flex:1;font-weight:500;line-height:1.4;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:${isDark ? '#95A5A6' : '#95A5A6'};cursor:pointer;font-size:16px;padding:4px;transition:color 0.3s;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Add animation styles if not exists
    if (!document.getElementById('toastStyles')) {
        const style = document.createElement('style');
        style.id = 'toastStyles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            @keyframes confettiFall {
                0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        setTimeout(() => toast.remove(), 350);
    }, 3500);
}

// ==========================================
// DARK MODE - Fixed (No Duplicate Calls)
// ==========================================
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    
    // Update moon/sun icon
    const moonIcon = document.querySelector('.nav-item .fa-moon, .nav-item .fa-sun');
    if (moonIcon) {
        moonIcon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    // Save preference via API
    fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme: isDark ? 'dark' : 'light' })
    }).catch(err => console.error('Error saving theme:', err));
    
    showToast(isDark ? '🌙 Dark mode enabled' : '☀️ Light mode enabled', 'info');
}

// Check saved preference on load
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        // Update icon if exists
        const moonIcon = document.querySelector('.nav-item .fa-moon, .nav-item .fa-sun');
        if (moonIcon) {
            moonIcon.className = 'fas fa-sun';
        }
    }
});

// ==========================================
// EXPORT DATA
// ==========================================
function exportData() {
    fetch('/api/analytics/export/csv')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.file;
                showToast('Data exported successfully', 'success');
            } else {
                showToast('No data to export', 'warning');
            }
        })
        .catch(() => showToast('Export failed', 'error'));
}

// ==========================================
// ACHIEVEMENTS - Premium
// ==========================================
function checkAchievements(sessions) {
    const achievements = [
        { threshold: 5, message: '5 Sessions - Great Start!', icon: 'fa-star' },
        { threshold: 10, message: '10 Sessions - Building Momentum!', icon: 'fa-rocket' },
        { threshold: 25, message: '25 Sessions - Consistency!', icon: 'fa-shield-alt' },
        { threshold: 50, message: '50 Sessions - On Fire!', icon: 'fa-fire' },
        { threshold: 100, message: '100 Sessions - Master Level!', icon: 'fa-crown' },
        { threshold: 200, message: '200 Sessions - Legendary!', icon: 'fa-gem' }
    ];
    
    let unlocked = false;
    for (const ach of achievements) {
        if (sessions >= ach.threshold) {
            unlocked = true;
            showAchievement(ach.message, ach.icon);
        }
    }
    
    if (!unlocked && sessions > 0) {
        const next = achievements.find(a => sessions < a.threshold);
        if (next) {
            const progress = Math.round((sessions / next.threshold) * 100);
            console.log(`Progress to next achievement: ${progress}%`);
        }
    }
}

function showAchievement(message, icon = 'fa-trophy') {
    // Confetti effect
    const colors = ['#6C63FF', '#2ECC71', '#F39C12', '#FF6584', '#3498DB', '#E74C3C'];
    for (let i = 0; i < 60; i++) {
        const confetti = document.createElement('div');
        const size = 6 + Math.random() * 10;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const duration = 2 + Math.random() * 2;
        const delay = Math.random() * 0.5;
        confetti.style.cssText = `
            position: fixed;
            top: -10px;
            left: ${Math.random() * 100}vw;
            width: ${size}px;
            height: ${size * 0.6}px;
            background: ${color};
            border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
            animation: confettiFall ${duration}s ease-in ${delay}s forwards;
            z-index: 9999;
            transform: rotate(${Math.random() * 360}deg);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        document.body.appendChild(confetti);
        setTimeout(() => confetti.remove(), 4000);
    }
    
    // Show achievement toast
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const isDark = document.body.classList.contains('dark-mode');
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: ${isDark ? '#2d2d44' : '#ffffff'};
        color: ${isDark ? '#e0e0e0' : '#2D3436'};
        padding: 18px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(108, 99, 255, 0.2);
        border-left: 4px solid #6C63FF;
        animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        display: flex;
        align-items: center;
        gap: 14px;
        pointer-events: auto;
        background: ${isDark ? 'linear-gradient(135deg, #2d2d44, #3d3d54)' : 'linear-gradient(135deg, #ffffff, #f8f9fa)'};
        border: 1px solid rgba(108, 99, 255, 0.15);
        font-weight: 600;
    `;
    
    toast.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#6C63FF,#8B83FF);flex-shrink:0;box-shadow:0 4px 12px rgba(108,99,255,0.3);">
            <i class="fas ${icon}" style="color:white;font-size:18px;"></i>
        </div>
        <span style="flex:1;line-height:1.4;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:${isDark ? '#95A5A6' : '#95A5A6'};cursor:pointer;font-size:16px;padding:4px;transition:color 0.3s;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.prepend(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        setTimeout(() => toast.remove(), 350);
    }, 4000);
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
    const form = document.getElementById('sessionForm');
    if (form) {
        form.addEventListener('submit', addSession);
    }
    
    // ==========================================
    // REMOVED: Duplicate dark mode event listener
    // onclick is already in HTML, so no need for addEventListener
    // ==========================================
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            showAddModal();
        }
        if (e.key === 'Escape') {
            closeModal();
        }
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
});

// ==========================================
// NAVIGATION - UPDATED WITH SETTINGS
// ==========================================
function navigateTo(page) {
    // Page title mapping
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
    const titleElement = document.getElementById('pageTitle');
    if (titleElement && titles[page]) {
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
            loadSettingsPage();
            break;
    }
}

// ==========================================
// SETTINGS PAGE
// ==========================================

function loadSettingsPage() {
    const container = document.getElementById('settingsContent');
    if (!container) return;
    
    // Show loading
    container.innerHTML = `
        <div class="skeleton-wrapper">
            <div class="skeleton-line long"></div>
            <div class="skeleton-line medium"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line long"></div>
            <div class="skeleton-line medium"></div>
        </div>
    `;
    
    // Fetch settings from API
    fetch('/api/settings')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderSettingsForm(data.data);
            } else {
                container.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Failed to load settings: ${data.error || 'Unknown error'}</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading settings. Please try again.</p>
                </div>
            `;
        });
}

function renderSettingsForm(settings) {
    const container = document.getElementById('settingsContent');
    if (!container) return;
    
    // Default settings if not provided
    const s = settings || {
        theme: 'light',
        notifications: true,
        study_reminder: true,
        reminder_interval: 60,
        default_subject: '',
        daily_goal: 120,
        weekly_goal: 600,
        language: 'en',
        time_format: '24h',
        sound_effects: true,
        auto_backup: true,
        backup_interval: 7
    };
    
    container.innerHTML = `
        <form id="settingsForm" onsubmit="saveSettings(event)">
            <div class="settings-grid">
                <!-- Theme -->
                <div class="settings-group">
                    <label>Theme</label>
                    <select id="settingTheme" class="settings-input">
                        <option value="light" ${s.theme === 'light' ? 'selected' : ''}>☀️ Light</option>
                        <option value="dark" ${s.theme === 'dark' ? 'selected' : ''}>🌙 Dark</option>
                        <option value="auto" ${s.theme === 'auto' ? 'selected' : ''}>🔄 Auto</option>
                    </select>
                </div>
                
                <!-- Language -->
                <div class="settings-group">
                    <label>Language</label>
                    <select id="settingLanguage" class="settings-input">
                        <option value="en" ${s.language === 'en' ? 'selected' : ''}>🇬🇧 English</option>
                        <option value="ur" ${s.language === 'ur' ? 'selected' : ''}>🇵🇰 Urdu</option>
                        <option value="hi" ${s.language === 'hi' ? 'selected' : ''}>🇮🇳 Hindi</option>
                    </select>
                </div>
                
                <!-- Time Format -->
                <div class="settings-group">
                    <label>Time Format</label>
                    <select id="settingTimeFormat" class="settings-input">
                        <option value="12h" ${s.time_format === '12h' ? 'selected' : ''}>12-hour (AM/PM)</option>
                        <option value="24h" ${s.time_format === '24h' ? 'selected' : ''}>24-hour</option>
                    </select>
                </div>
                
                <!-- Daily Goal -->
                <div class="settings-group">
                    <label>Daily Goal (minutes)</label>
                    <input type="number" id="settingDailyGoal" class="settings-input" 
                           value="${s.daily_goal}" min="30" max="480">
                    <span class="help-text">Recommended: 120 min</span>
                </div>
                
                <!-- Weekly Goal -->
                <div class="settings-group">
                    <label>Weekly Goal (minutes)</label>
                    <input type="number" id="settingWeeklyGoal" class="settings-input" 
                           value="${s.weekly_goal}" min="120" max="1680">
                    <span class="help-text">Recommended: 600 min</span>
                </div>
                
                <!-- Default Subject -->
                <div class="settings-group">
                    <label>Default Subject</label>
                    <input type="text" id="settingDefaultSubject" class="settings-input" 
                           value="${s.default_subject || ''}" placeholder="e.g., Python">
                </div>
                
                <!-- Reminder Interval -->
                <div class="settings-group">
                    <label>Reminder Interval (minutes)</label>
                    <input type="number" id="settingReminderInterval" class="settings-input" 
                           value="${s.reminder_interval}" min="15" max="180">
                </div>
                
                <!-- Backup Interval -->
                <div class="settings-group">
                    <label>Auto Backup (days)</label>
                    <input type="number" id="settingBackupInterval" class="settings-input" 
                           value="${s.backup_interval || 7}" min="1" max="30">
                </div>
            </div>
            
            <!-- Toggle Switches -->
            <div class="settings-toggles">
                <div class="toggle-group">
                    <label class="toggle-label">
                        <span><i class="fas fa-bell"></i> Notifications</span>
                        <div class="toggle-switch ${s.notifications ? 'active' : ''}" 
                             onclick="toggleSwitch(this)">
                            <input type="hidden" id="settingNotifications" value="${s.notifications}">
                            <span class="toggle-slider"></span>
                        </div>
                    </label>
                </div>
                
                <div class="toggle-group">
                    <label class="toggle-label">
                        <span><i class="fas fa-clock"></i> Study Reminder</span>
                        <div class="toggle-switch ${s.study_reminder ? 'active' : ''}" 
                             onclick="toggleSwitch(this)">
                            <input type="hidden" id="settingStudyReminder" value="${s.study_reminder}">
                            <span class="toggle-slider"></span>
                        </div>
                    </label>
                </div>
                
                <div class="toggle-group">
                    <label class="toggle-label">
                        <span><i class="fas fa-volume-up"></i> Sound Effects</span>
                        <div class="toggle-switch ${s.sound_effects ? 'active' : ''}" 
                             onclick="toggleSwitch(this)">
                            <input type="hidden" id="settingSoundEffects" value="${s.sound_effects}">
                            <span class="toggle-slider"></span>
                        </div>
                    </label>
                </div>
                
                <div class="toggle-group">
                    <label class="toggle-label">
                        <span><i class="fas fa-database"></i> Auto Backup</span>
                        <div class="toggle-switch ${s.auto_backup ? 'active' : ''}" 
                             onclick="toggleSwitch(this)">
                            <input type="hidden" id="settingAutoBackup" value="${s.auto_backup}">
                            <span class="toggle-slider"></span>
                        </div>
                    </label>
                </div>
            </div>
            
            <div class="settings-actions">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> Save Settings
                </button>
                <button type="button" class="btn btn-secondary" onclick="resetSettings()">
                    <i class="fas fa-undo"></i> Reset to Default
                </button>
            </div>
            
            <div id="settingsMessage" class="settings-message"></div>
        </form>
    `;
}

// ==========================================
// TOGGLE SWITCH
// ==========================================
function toggleSwitch(element) {
    element.classList.toggle('active');
    const hiddenInput = element.querySelector('input[type="hidden"]');
    if (hiddenInput) {
        hiddenInput.value = element.classList.contains('active');
    }
}

// ==========================================
// SAVE SETTINGS
// ==========================================
function saveSettings(event) {
    event.preventDefault();
    
    const settings = {
        theme: document.getElementById('settingTheme')?.value || 'light',
        language: document.getElementById('settingLanguage')?.value || 'en',
        time_format: document.getElementById('settingTimeFormat')?.value || '24h',
        daily_goal: parseInt(document.getElementById('settingDailyGoal')?.value) || 120,
        weekly_goal: parseInt(document.getElementById('settingWeeklyGoal')?.value) || 600,
        default_subject: document.getElementById('settingDefaultSubject')?.value || '',
        reminder_interval: parseInt(document.getElementById('settingReminderInterval')?.value) || 60,
        backup_interval: parseInt(document.getElementById('settingBackupInterval')?.value) || 7,
        notifications: document.getElementById('settingNotifications')?.value === 'true',
        study_reminder: document.getElementById('settingStudyReminder')?.value === 'true',
        sound_effects: document.getElementById('settingSoundEffects')?.value === 'true',
        auto_backup: document.getElementById('settingAutoBackup')?.value === 'true'
    };
    
    const messageEl = document.getElementById('settingsMessage');
    
    messageEl.innerHTML = `
        <div class="info-message">
            <i class="fas fa-spinner fa-spin"></i> Saving settings...
        </div>
    `;
    
    fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageEl.innerHTML = `
                <div class="success-message">
                    <i class="fas fa-check-circle"></i> Settings saved successfully!
                </div>
            `;
            
            // Apply theme immediately
            applyTheme(settings.theme);
            
            // Update dark mode icon
            const isDark = settings.theme === 'dark';
            const moonIcon = document.querySelector('.nav-item .fa-moon, .nav-item .fa-sun');
            if (moonIcon) {
                moonIcon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
            }
            
            showToast('Settings saved successfully!', 'success');
            
            setTimeout(() => {
                messageEl.innerHTML = '';
            }, 3000);
        } else {
            messageEl.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i> ${data.error || 'Failed to save settings'}
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        messageEl.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i> Error saving settings
            </div>
        `;
    });
}

// ==========================================
// RESET SETTINGS
// ==========================================
function resetSettings() {
    if (!confirm('⚠️ Are you sure you want to reset all settings to default?')) {
        return;
    }
    
    const messageEl = document.getElementById('settingsMessage');
    
    messageEl.innerHTML = `
        <div class="info-message">
            <i class="fas fa-spinner fa-spin"></i> Resetting settings...
        </div>
    `;
    
    fetch('/api/settings/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageEl.innerHTML = `
                <div class="success-message">
                    <i class="fas fa-check-circle"></i> Settings reset to default!
                </div>
            `;
            // Reload settings
            loadSettingsPage();
            showToast('Settings reset to default', 'info');
        } else {
            messageEl.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i> ${data.error || 'Failed to reset settings'}
                </div>
            `;
        }
        
        setTimeout(() => {
            messageEl.innerHTML = '';
        }, 3000);
    })
    .catch(error => {
        console.error('Error resetting settings:', error);
        messageEl.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i> Error resetting settings
            </div>
        `;
    });
}

// ==========================================
// APPLY THEME
// ==========================================
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'true');
    } else if (theme === 'auto') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (isDark) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'true');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'false');
        }
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'false');
    }
}

// ==========================================
// NAVIGATE TO SETTINGS (Helper)
// ==========================================
function navigateToSettings(event) {
    if (event) event.preventDefault();
    navigateTo('settings');
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
                
                // Update stats cards with animation
                const statElements = {
                    'statSessions': sessions,
                    'statTime': `${data.data.total_time || 0} min`,
                    'statProductivity': `${data.data.avg_productivity || 0}%`,
                    'totalSessions': sessions,
                    'sessionBadge': sessions
                };
                
                Object.entries(statElements).forEach(([id, value]) => {
                    const el = document.getElementById(id);
                    if (el) {
                        el.textContent = value;
                        // Animation effect
                        el.style.transition = 'transform 0.3s ease';
                        el.style.transform = 'scale(1.1)';
                        setTimeout(() => {
                            el.style.transform = 'scale(1)';
                        }, 200);
                    }
                });
                
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
                    ${d.best_subject && d.best_subject.name ? `
                        <div class="summary-row">
                            <span><i class="fas fa-trophy" style="color:#F39C12;"></i>Best Subject</span>
                            <strong>${d.best_subject.name} (${d.best_subject.score}%)</strong>
                        </div>
                    ` : ''}
                    ${d.peak_hour ? `
                        <div class="summary-row">
                            <span><i class="fas fa-clock" style="color:var(--primary);"></i>Peak Hour</span>
                            <strong>${String(d.peak_hour).padStart(2, '0')}:00</strong>
                        </div>
                    ` : ''}
                `;
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-inbox" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>No sessions today</p>
                        <p style="font-size:13px;margin-top:4px;">Start tracking your study sessions</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            document.getElementById('todaySummary').innerHTML = `
                <p style="color:#E74C3C;text-align:center;">
                    <i class="fas fa-exclamation-circle"></i> Error loading dashboard
                </p>
            `;
        });
    
    loadSubjectBreakdown();
}

// ==========================================
// SUBJECT BREAKDOWN
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
                    document.querySelectorAll('.subject-item .fill').forEach((bar, index) => {
                        const pct = data.data.subjects[index]?.[1]?.avg_productivity || 0;
                        bar.style.width = `${pct}%`;
                    });
                }, 300);
                
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
            document.getElementById('subjectBreakdown').innerHTML = `
                <p style="color:#E74C3C;text-align:center;">
                    <i class="fas fa-exclamation-circle"></i> Error loading subjects
                </p>
            `;
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
                
                updateSubjectFilter(data.data);
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-book-open" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>No sessions found</p>
                        <p style="font-size:13px;margin-top:4px;">Start tracking your study sessions</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            document.getElementById('sessionsList').innerHTML = `
                <p style="color:#E74C3C;text-align:center;">
                    <i class="fas fa-exclamation-circle"></i> Error loading sessions
                </p>
            `;
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
    showToast('Sessions refreshed', 'info');
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
                showToast('Session deleted successfully', 'success');
            } else {
                showToast('Error deleting session', 'error');
            }
        })
        .catch(err => showToast('Error deleting session', 'error'));
}

// ==========================================
// SESSION FILTERS
// ==========================================
function applyFilters() {
    const date = document.getElementById('filterDate').value;
    const subject = document.getElementById('filterSubject').value;
    
    fetch(`/api/sessions?date=${date}&subject=${subject}`)
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
        .catch(err => console.error('Error:', err));
}

function clearFilters() {
    document.getElementById('filterDate').value = '';
    document.getElementById('filterSubject').value = '';
    document.getElementById('searchSessions').value = '';
    loadSessions();
    showToast('Filters cleared', 'info');
}

function searchSessions() {
    const query = document.getElementById('searchSessions').value.toLowerCase();
    const items = document.querySelectorAll('#sessionsList .session-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? 'flex' : 'none';
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
                        <p style="font-size:13px;margin-top:4px;">Add sessions to see subject analysis</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            document.getElementById('subjectAnalysis').innerHTML = `
                <p style="color:#E74C3C;text-align:center;">
                    <i class="fas fa-exclamation-circle"></i> Error loading subject analysis
                </p>
            `;
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
                
                if (insights.patterns) {
                    const patterns = insights.patterns;
                    
                    if (patterns.best_learning_time && patterns.best_learning_time.hour !== undefined) {
                        const hour = patterns.best_learning_time.hour;
                        const productivity = patterns.best_learning_time.avg_productivity || 0;
                        html += `
                            <div class="insight-box">
                                <h4><i class="fas fa-clock"></i> Best Time to Study</h4>
                                <p>${String(hour).padStart(2, '0')}:00</p>
                                <div class="sub-text">${productivity}% average productivity</div>
                            </div>
                        `;
                    }
                    
                    if (patterns.most_consistent_subject) {
                        html += `
                            <div style="padding:12px 16px; background:#f8f9fa; border-radius:12px; margin-bottom:12px;">
                                <p style="font-size:14px;">
                                    <i class="fas fa-trophy" style="color:#F39C12;"></i>
                                    <strong>Most Consistent Subject:</strong> 
                                    ${patterns.most_consistent_subject.subject} 
                                    (${patterns.most_consistent_subject.avg}% avg)
                                </p>
                            </div>
                        `;
                    }
                    
                    if (patterns.distraction_patterns) {
                        const dp = patterns.distraction_patterns;
                        html += `
                            <div style="padding:12px 16px; background:#f8f9fa; border-radius:12px; margin-bottom:12px;">
                                <p style="font-size:14px;">
                                    <i class="fas fa-exclamation-triangle" style="color:#F39C12;"></i>
                                    <strong>Distraction Stats:</strong>
                                    Avg: ${dp.avg_distractions || 0} | 
                                    Zero-distraction sessions: ${dp.zero_distraction_sessions || 0}
                                </p>
                            </div>
                        `;
                    }
                }
                
                if (insights.analysis && insights.analysis.overall_stats) {
                    const stats = insights.analysis.overall_stats;
                    
                    let consistency = '--';
                    if (insights.analysis.consistency !== undefined) {
                        consistency = insights.analysis.consistency + '%';
                    }
                    
                    html += `
                        <div style="background:#f8f9fa;padding:16px;border-radius:12px;margin-top:12px;">
                            <h4 style="margin-bottom:8px;font-size:14px;">
                                <i class="fas fa-chart-line" style="color:var(--primary);"></i> 
                                Productivity Stats
                            </h4>
                            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center;">
                                <div>
                                    <div style="font-size:11px;color:#95A5A6;">Mean</div>
                                    <div style="font-size:16px;font-weight:700;">${stats.mean || 0}%</div>
                                </div>
                                <div>
                                    <div style="font-size:11px;color:#95A5A6;">Median</div>
                                    <div style="font-size:16px;font-weight:700;">${stats.median || 0}%</div>
                                </div>
                                <div>
                                    <div style="font-size:11px;color:#95A5A6;">Consistency</div>
                                    <div style="font-size:16px;font-weight:700;">${consistency}</div>
                                </div>
                            </div>
                            <div style="margin-top:8px;text-align:center;font-size:12px;color:#95A5A6;">
                                Based on ${insights.total_sessions || 0} sessions
                            </div>
                        </div>
                    `;
                }
                
                if (insights.recommendations && insights.recommendations.length > 0) {
                    html += `
                        <div style="margin-top:16px;padding:16px;border-radius:12px;border:1px solid rgba(108,99,255,0.2);">
                            <h4 style="margin-bottom:8px;font-size:14px;">
                                <i class="fas fa-lightbulb" style="color:#F39C12;"></i> Recommendations
                            </h4>
                            <ul style="list-style:none;padding:0;">
                    `;
                    insights.recommendations.slice(0, 5).forEach(rec => {
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
                
                if (insights.ai_confidence) {
                    html += `
                        <div style="margin-top:12px;text-align:center;font-size:12px;color:#95A5A6;">
                            AI Confidence: ${insights.ai_confidence}%
                        </div>
                    `;
                }
                
                container.innerHTML = html || `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-robot" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>Add more sessions for AI insights</p>
                        <p style="font-size:13px;margin-top:4px;">Need at least 5 sessions for analysis</p>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div style="text-align:center;color:#95A5A6;padding:30px 0;">
                        <i class="fas fa-robot" style="font-size:40px;display:block;margin-bottom:12px;color:var(--primary);"></i>
                        <p>${data.message || 'Add more sessions for AI insights'}</p>
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
function loadAIInsights() {
    loadInsights();
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
        showToast('Please fill in subject and duration', 'warning');
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
            showToast('Session added successfully', 'success');
        } else {
            showToast('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        showToast('Error adding session', 'error');
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
        }
    }
}, 30000);

console.log('🧠 Smart Study System loaded successfully!');
console.log('📚 Track your study sessions and get AI insights!');
console.log('⌨️ Keyboard Shortcuts:');
console.log('  Ctrl+N - New Session');
console.log('  Ctrl+1-5 - Navigate pages');
console.log('  Escape - Close modal');