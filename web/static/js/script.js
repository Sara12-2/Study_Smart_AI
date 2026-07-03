// ==========================================
// SMART STUDY SYSTEM - JavaScript
// ==========================================

// Global state
let currentPage = 'dashboard';

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    updateDate();
    loadDashboard();
    loadStats();
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            navigateTo(page);
        });
    });
    
    // Form submission
    document.getElementById('sessionForm').addEventListener('submit', addSession);
});

// ==========================================
// NAVIGATION
// ==========================================
function navigateTo(page) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`.nav-item[data-page="${page}"]`).classList.add('active');
    
    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    document.getElementById(`page-${page}`).classList.add('active');
    
    // Update title
    const titles = {
        dashboard: '📊 Dashboard',
        sessions: '📚 Sessions',
        subjects: '📖 Subjects',
        insights: '🤖 AI Insights',
        settings: '⚙️ Settings'
    };
    document.getElementById('pageTitle').textContent = titles[page] || page;
    
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
    }
}

// ==========================================
// DATE
// ==========================================
function updateDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', options);
    document.getElementById('todayDate').textContent = now.toLocaleDateString('en-US', options);
}

// ==========================================
// STATS
// ==========================================
function loadStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById('statSessions').textContent = data.data.total_sessions || 0;
                document.getElementById('statTime').textContent = `${data.data.total_time || 0} min`;
                document.getElementById('statProductivity').textContent = `${data.data.avg_productivity || 0}%`;
                document.getElementById('statConsistency').textContent = '--';
                document.getElementById('totalSessions').textContent = data.data.total_sessions || 0;
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
            if (data.success && data.data) {
                const d = data.data;
                container.innerHTML = `
                    <div class="dashboard-summary">
                        <div class="summary-row">
                            <span>📚 Sessions:</span>
                            <strong>${d.total_sessions}</strong>
                        </div>
                        <div class="summary-row">
                            <span>⏱️ Total Time:</span>
                            <strong>${d.total_time} minutes</strong>
                        </div>
                        <div class="summary-row">
                            <span>📈 Avg Productivity:</span>
                            <strong style="color: ${d.avg_productivity >= 70 ? '#2ECC71' : d.avg_productivity >= 50 ? '#F39C12' : '#E74C3C'}">
                                ${d.avg_productivity}%
                            </strong>
                        </div>
                        <div class="summary-row">
                            <span>⚠️ Distractions:</span>
                            <strong>${d.total_distractions}</strong>
                        </div>
                        <div class="summary-row">
                            <span>🏆 Score:</span>
                            <strong>${d.score}%</strong>
                        </div>
                        ${d.best_subject && d.best_subject.name ? `
                            <div class="summary-row">
                                <span>🌟 Best Subject:</span>
                                <strong>${d.best_subject.name} (${d.best_subject.score}%)</strong>
                            </div>
                        ` : ''}
                        ${d.peak_hour ? `
                            <div class="summary-row">
                                <span>🕐 Peak Hour:</span>
                                <strong>${String(d.peak_hour).padStart(2, '0')}:00</strong>
                            </div>
                        ` : ''}
                    </div>
                    <style>
                        .summary-row {
                            display: flex;
                            justify-content: space-between;
                            padding: 8px 0;
                            border-bottom: 1px solid #f0f0f0;
                        }
                        .summary-row:last-child {
                            border-bottom: none;
                        }
                    </style>
                `;
            } else {
                container.innerHTML = '<p style="text-align:center;color:#95A5A6;">📭 No sessions today. Start tracking!</p>';
            }
        })
        .catch(err => {
            console.error('Error loading dashboard:', err);
            document.getElementById('todaySummary').innerHTML = '<p style="color:#E74C3C;">❌ Error loading dashboard</p>';
        });
    
    // Load subject breakdown
    fetch('/api/subjects')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('subjectBreakdown');
            if (data.success && data.data && data.data.subjects) {
                let html = '<div class="subject-list">';
                data.data.subjects.forEach(([subject, metrics]) => {
                    const pct = metrics.avg_productivity;
                    const color = pct >= 70 ? '#2ECC71' : pct >= 50 ? '#F39C12' : '#E74C3C';
                    html += `
                        <div class="subject-item">
                            <span class="subject-name">${subject}</span>
                            <div class="subject-bar">
                                <div class="subject-fill" style="width: ${pct}%; background: ${color};"></div>
                            </div>
                            <span class="subject-score">${pct}%</span>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="text-align:center;color:#95A5A6;">📭 No subjects yet. Add sessions to see analysis!</p>';
            }
        })
        .catch(err => {
            console.error('Error loading subjects:', err);
            document.getElementById('subjectBreakdown').innerHTML = '<p style="color:#E74C3C;">❌ Error loading subject analysis</p>';
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
            if (data.success && data.data && data.data.length > 0) {
                let html = '';
                data.data.slice().reverse().forEach((session, index) => {
                    const score = session.productivity_score || 0;
                    const scoreClass = score >= 70 ? 'score-high' : score >= 50 ? 'score-medium' : 'score-low';
                    const date = session.timestamp ? session.timestamp.substring(0, 16).replace('T', ' ') : 'Unknown';
                    
                    html += `
                        <div class="session-item">
                            <div class="session-info">
                                <div class="session-subject">${session.subject}</div>
                                <div class="session-meta">
                                    ⏱️ ${session.duration}min • ${date}
                                    ${session.distractions ? ` • ⚠️ ${session.distractions} distractions` : ''}
                                    ${session.mood ? ` • 😊 ${session.mood}/5` : ''}
                                </div>
                            </div>
                            <div>
                                <span class="session-score ${scoreClass}">${score}%</span>
                                <button class="btn btn-sm btn-danger" onclick="deleteSession(${data.data.length - 1 - index})">🗑️</button>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="text-align:center;color:#95A5A6;">📭 No sessions found. Add your first session!</p>';
            }
        })
        .catch(err => {
            console.error('Error loading sessions:', err);
            document.getElementById('sessionsList').innerHTML = '<p style="color:#E74C3C;">❌ Error loading sessions</p>';
        });
}

function refreshSessions() {
    loadSessions();
}

function deleteSession(id) {
    if (confirm('Delete this session?')) {
        fetch(`/api/sessions/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    loadSessions();
                    loadStats();
                    loadDashboard();
                } else {
                    alert('Error deleting session');
                }
            })
            .catch(err => console.error('Error:', err));
    }
}

// ==========================================
// SUBJECTS
// ==========================================
function loadSubjects() {
    fetch('/api/subjects')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('subjectAnalysis');
            if (data.success && data.data && data.data.subjects) {
                let html = `
                    <div style="margin-bottom:16px;">
                        <strong>📊 Total Subjects:</strong> ${data.data.total_subjects}
                    </div>
                    <div style="margin-bottom:16px;">
                        <strong>🌟 Best:</strong> ${data.data.best_subject ? `${data.data.best_subject[0]} (${data.data.best_subject[1].avg_productivity}%)` : 'N/A'}
                    </div>
                    <div style="margin-bottom:24px;">
                        <strong>⚠️ Worst:</strong> ${data.data.worst_subject ? `${data.data.worst_subject[0]} (${data.data.worst_subject[1].avg_productivity}%)` : 'N/A'}
                    </div>
                `;
                
                data.data.subjects.forEach(([subject, metrics]) => {
                    html += `
                        <div style="padding:12px 16px; background:#f8f9fa; border-radius:8px; margin-bottom:8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong>${subject}</strong>
                                <span style="color:#2D3436;">${metrics.avg_productivity}%</span>
                            </div>
                            <div style="font-size:13px; color:#95A5A6; margin-top:4px;">
                                📚 ${metrics.sessions} sessions • ⏱️ ${metrics.total_time} min • ⚠️ ${metrics.avg_distractions} distractions
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="text-align:center;color:#95A5A6;">📭 No subjects yet.</p>';
            }
        })
        .catch(err => {
            console.error('Error loading subjects:', err);
            document.getElementById('subjectAnalysis').innerHTML = '<p style="color:#E74C3C;">❌ Error loading subject analysis</p>';
        });
}

// ==========================================
// INSIGHTS
// ==========================================
function loadInsights() {
    fetch('/api/insights')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('aiInsights');
            if (data.success && data.data) {
                const insights = data.data;
                let html = '';
                
                // Optimal times
                if (insights.optimal_times && !insights.optimal_times.error) {
                    html += `
                        <div style="margin-bottom:24px; padding:16px; background:#F0F4FF; border-radius:12px;">
                            <h4 style="margin-bottom:12px;">🕐 Optimal Study Times</h4>
                            <div style="font-size:14px;">
                                <p><strong>Best Hour:</strong> ${String(insights.optimal_times.best_hour).padStart(2, '0')}:00 (${insights.optimal_times.best_hour_productivity}% productivity)</p>
                                <p style="margin-top:8px;"><strong>💡 Recommendation:</strong> ${insights.optimal_times.recommendation}</p>
                            </div>
                        </div>
                    `;
                }
                
                // Trends
                if (insights.trends && !insights.trends.error) {
                    const trendEmoji = insights.trends.trend_direction === 'improving' ? '📈' : 
                                      insights.trends.trend_direction === 'declining' ? '📉' : '➡️';
                    html += `
                        <div style="padding:16px; background:#f8f9fa; border-radius:12px;">
                            <h4 style="margin-bottom:12px;">📈 Productivity Trends (30 days)</h4>
                            <div style="font-size:14px;">
                                <p><strong>${trendEmoji} Trend:</strong> ${insights.trends.trend_direction}</p>
                                <p><strong>🎯 Avg Productivity:</strong> ${insights.trends.avg_productivity}%</p>
                                <p><strong>🏆 Max:</strong> ${insights.trends.max_productivity}%</p>
                                <p><strong>💪 Consistency:</strong> ${insights.trends.consistency}%</p>
                            </div>
                        </div>
                    `;
                }
                
                container.innerHTML = html || '<p style="text-align:center;color:#95A5A6;">Add more sessions for AI insights!</p>';
            } else {
                container.innerHTML = '<p style="text-align:center;color:#95A5A6;">📭 Add more sessions for AI insights!</p>';
            }
        })
        .catch(err => {
            console.error('Error loading insights:', err);
            document.getElementById('aiInsights').innerHTML = '<p style="color:#E74C3C;">❌ Error loading insights</p>';
        });
}

// ==========================================
// MODAL
// ==========================================
function showAddModal() {
    document.getElementById('addModal').style.display = 'block';
    document.getElementById('sessionForm').reset();
}

function closeModal() {
    document.getElementById('addModal').style.display = 'none';
}

function addSession(e) {
    e.preventDefault();
    
    const data = {
        subject: document.getElementById('subject').value.trim(),
        duration: parseInt(document.getElementById('duration').value),
        distractions: parseInt(document.getElementById('distractions').value) || 0,
        mood: parseInt(document.getElementById('mood').value) || null,
        notes: document.getElementById('notes').value.trim() || null
    };
    
    if (!data.subject || !data.duration) {
        alert('Please fill in subject and duration');
        return;
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
            loadDashboard();
            loadStats();
            if (currentPage === 'sessions') loadSessions();
            alert('✅ Session added successfully!');
        } else {
            alert('❌ Error: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('❌ Error adding session');
    });
}

// Click outside modal to close
window.onclick = function(event) {
    const modal = document.getElementById('addModal');
    if (event.target === modal) {
        closeModal();
    }
}