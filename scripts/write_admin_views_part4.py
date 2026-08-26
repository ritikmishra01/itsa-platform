import os

TEMPLATES_DIR = r"C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\app\templates\admin"
views = {}

# 10. gamification.html
views['gamification.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Gamification & Points Ledger{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Gamification & Points</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Gamification & Points Operations</h4>
        <p class="text-muted small mb-0">Monitor total engagement points, student leaderboard rankings, and adjust points with auditing</p>
    </div>
    <button class="btn btn-warning text-dark fw-bold btn-sm" data-bs-toggle="modal" data-bs-target="#adjustPointsModal">
        <i class="bi bi-plus-slash-minus me-1"></i> Manual Point Adjustment
    </button>
</div>

<!-- Points Metrics -->
<div class="row g-3 mb-4">
    <div class="col-md-6">
        <div class="card card-itsa p-3 border-start border-4 border-warning">
            <div class="text-muted small fw-semibold">Total Points Distributed</div>
            <h3 class="fw-bold mb-0 text-warning">{{ total_points }} pts</h3>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card card-itsa p-3 border-start border-4 border-primary">
            <div class="text-muted small fw-semibold">Active Students with Points</div>
            <h3 class="fw-bold mb-0 text-primary">{{ active_students }}</h3>
        </div>
    </div>
</div>

<!-- Tabs -->
<ul class="nav nav-tabs mb-4" id="gameTabs">
    <li class="nav-item">
        <button class="nav-link active fw-semibold" data-bs-toggle="tab" data-bs-target="#leaderboardTab">
            <i class="bi bi-trophy text-warning me-1"></i> Top Student Leaderboard
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link fw-semibold" data-bs-toggle="tab" data-bs-target="#ledgerTab">
            <i class="bi bi-journal-text me-1"></i> Point Transaction Ledger
        </button>
    </li>
</ul>

<div class="tab-content">
    <div class="tab-pane fade show active" id="leaderboardTab">
        <div class="card card-itsa overflow-hidden shadow-sm">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Rank</th>
                            <th>Student</th>
                            <th>Student ID</th>
                            <th>Department & Year</th>
                            <th class="text-end pe-4">Total Points</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if leaderboard %}
                            {% for row in leaderboard %}
                            <tr>
                                <td class="ps-4">
                                    {% if row.rank == 1 %}🥇{% elif row.rank == 2 %}🥈{% elif row.rank == 3 %}🥉{% else %}#{{ row.rank }}{% endif %}
                                </td>
                                <td class="fw-bold text-dark">{{ row.full_name }}</td>
                                <td class="font-monospace small">{{ row.student_id or '-' }}</td>
                                <td>{{ row.department or '-' }} <small class="text-muted">(Yr {{ row.year_of_study or '1' }})</small></td>
                                <td class="text-end pe-4">
                                    <span class="points-pill">{{ row.total_points }} pts</span>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="5" class="text-center py-4 text-muted">No leaderboard entries available.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="tab-pane fade" id="ledgerTab">
        <div class="card card-itsa overflow-hidden shadow-sm">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Transaction ID</th>
                            <th>Student</th>
                            <th>Reason</th>
                            <th>Timestamp</th>
                            <th class="text-end pe-4">Points Delta</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if recent_transactions %}
                            {% for t in recent_transactions %}
                            <tr>
                                <td class="ps-4 font-monospace small">#TX-{{ t.id }}</td>
                                <td class="fw-semibold">{{ t.user.full_name }}</td>
                                <td><span class="badge bg-light text-dark border">{{ t.reason }}</span></td>
                                <td class="small">{{ t.created_at.strftime('%b %d, %H:%M:%S') }}</td>
                                <td class="text-end pe-4 fw-bold {% if t.points > 0 %}text-success{% else %}text-danger{% endif %}">
                                    {% if t.points > 0 %}+{% endif %}{{ t.points }} pts
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="5" class="text-center py-4 text-muted">No point transactions recorded yet.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- Adjust Points Modal -->
<div class="modal fade" id="adjustPointsModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold">Manual Point Adjustment</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="adjustPointsForm">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Select Student *</label>
                        <select class="form-select" name="user_id" required>
                            {% for u in users %}<option value="{{ u.id }}">{{ u.full_name }} ({{ u.email }})</option>{% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Points Delta (e.g. +15 or -5) *</label>
                        <input type="number" class="form-control" name="points" required placeholder="+10">
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Audit Reason *</label>
                        <input type="text" class="form-control" name="reason" required placeholder="e.g. Volunteer Service or Competition 1st Place">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-warning text-dark fw-bold">Apply Points Adjustment</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
document.getElementById('adjustPointsForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(this));
    try {
        await apiCall('/api/v1/admin/points/adjust', 'POST', data);
        showToast('Points adjustment applied and logged.', 'success');
        setTimeout(() => window.location.reload(), 600);
    } catch(err) {}
});
</script>
{% endblock %}
"""

# 11. ai_center.html
views['ai_center.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}AI Intelligence Center{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">AI Intelligence Center</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1"><i class="bi bi-robot text-primary me-2"></i> Gemini AI & ML Intelligence Hub</h4>
        <p class="text-muted small mb-0">Test LLM prompt pipelines, run automated sentiment analysis on feedback, and inspect recommendation vectors</p>
    </div>
</div>

<div class="row g-4">
    <!-- Feedback Sentiment Analyzer -->
    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm h-100">
            <h5 class="fw-bold mb-3"><i class="bi bi-bar-chart-steps text-success me-2"></i> Feedback Sentiment Analyzer</h5>
            <div class="mb-3">
                <label class="form-label small fw-semibold">Select Event to Analyze</label>
                <select class="form-select" id="aiFeedbackEventSelect">
                    {% for e in events %}<option value="{{ e.id }}">{{ e.title }}</option>{% endfor %}
                </select>
            </div>
            <button class="btn btn-success btn-sm w-100 mb-3" id="btnRunSentiment">
                <i class="bi bi-magic me-1"></i> Run Gemini Feedback Sentiment Engine
            </button>
            <div id="sentimentResult" class="p-3 bg-light rounded-3 small text-muted">
                Select an event above and click Run to generate sentiment breakdown and executive summary.
            </div>
        </div>
    </div>

    <!-- Registration Turnout Predictor -->
    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm h-100">
            <h5 class="fw-bold mb-3"><i class="bi bi-graph-up-arrow text-primary me-2"></i> ML Turnout Predictor</h5>
            <div class="mb-3">
                <label class="form-label small fw-semibold">Select Event for Turnout Regression</label>
                <select class="form-select" id="aiPredictEventSelect">
                    {% for e in events %}<option value="{{ e.id }}">{{ e.title }}</option>{% endfor %}
                </select>
            </div>
            <button class="btn btn-primary btn-sm w-100 mb-3" id="btnRunPredict">
                <i class="bi bi-cpu me-1"></i> Predict Registration Attendance
            </button>
            <div id="predictResult" class="p-3 bg-light rounded-3 small text-muted">
                Select an event above and click Predict to calculate estimated student registrations based on historical signals.
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
document.getElementById('btnRunSentiment').addEventListener('click', async function() {
    const eventId = document.getElementById('aiFeedbackEventSelect').value;
    if (!eventId) return;
    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Analyzing...';
    try {
        const res = await apiCall(`/api/v1/ai/analyze-feedback/${eventId}`, 'POST');
        document.getElementById('sentimentResult').innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge bg-${res.data.sentiment === 'POSITIVE' ? 'success' : (res.data.sentiment === 'NEGATIVE' ? 'danger' : 'warning')}">${res.data.sentiment}</span>
                <span class="fw-bold text-dark">${res.data.score}/100 Score</span>
            </div>
            <p class="mb-2"><strong>Summary:</strong> ${res.data.summary}</p>
        `;
        showToast('Gemini feedback analysis complete!', 'success');
    } catch(err) {
    } finally {
        this.disabled = false;
        this.innerHTML = '<i class="bi bi-magic me-1"></i> Run Gemini Feedback Sentiment Engine';
    }
});

document.getElementById('btnRunPredict').addEventListener('click', async function() {
    const eventId = document.getElementById('aiPredictEventSelect').value;
    if (!eventId) return;
    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Calculating ML regression...';
    try {
        const res = await apiCall(`/api/v1/ai/predict-registrations/${eventId}`, 'GET');
        document.getElementById('predictResult').innerHTML = `
            <div class="fw-bold fs-5 text-primary mb-1">Predicted Turnout: ${res.data.predicted_registrations} students</div>
            <div class="small text-muted mb-2">Confidence Level: <span class="badge bg-info text-dark">${res.data.confidence}</span></div>
            <p class="mb-0 small">${res.data.factors_considered.join(' &bull; ')}</p>
        `;
        showToast('Turnout prediction complete!', 'success');
    } catch(err) {
    } finally {
        this.disabled = false;
        this.innerHTML = '<i class="bi bi-cpu me-1"></i> Predict Registration Attendance';
    }
});
</script>
{% endblock %}
"""

# 12. reports.html
views['reports.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Centralized Reports Export{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Export Reports</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Centralized Data Reports Hub</h4>
        <p class="text-muted small mb-0">Generate and download standard CSV reports for audit and faculty presentations</p>
    </div>
</div>

<div class="row g-4">
    <div class="col-md-4">
        <div class="card card-itsa p-4 text-center h-100 shadow-sm">
            <i class="bi bi-calendar-event text-primary fs-1 mb-2"></i>
            <h5 class="fw-bold mb-1">Events Directory Report</h5>
            <p class="small text-muted mb-3">{{ counts.events }} total scheduled events</p>
            <a href="{{ url_for('api_admin.export_report_csv', report_type='events') }}" class="btn btn-outline-primary btn-sm mt-auto">
                <i class="bi bi-download me-1"></i> Download Events CSV
            </a>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card card-itsa p-4 text-center h-100 shadow-sm">
            <i class="bi bi-ticket-perforated text-info fs-1 mb-2"></i>
            <h5 class="fw-bold mb-1">Registrations Report</h5>
            <p class="small text-muted mb-3">{{ counts.registrations }} student registrations</p>
            <a href="{{ url_for('api_admin.export_report_csv', report_type='registrations') }}" class="btn btn-outline-info btn-sm mt-auto">
                <i class="bi bi-download me-1"></i> Download Registrations CSV
            </a>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card card-itsa p-4 text-center h-100 shadow-sm">
            <i class="bi bi-qr-code-scan text-success fs-1 mb-2"></i>
            <h5 class="fw-bold mb-1">QR Attendance Report</h5>
            <p class="small text-muted mb-3">{{ counts.attendance }} verified check-in records</p>
            <a href="{{ url_for('api_admin.export_report_csv', report_type='attendance') }}" class="btn btn-outline-success btn-sm mt-auto">
                <i class="bi bi-download me-1"></i> Download Attendance CSV
            </a>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card card-itsa p-4 text-center h-100 shadow-sm">
            <i class="bi bi-award text-warning fs-1 mb-2"></i>
            <h5 class="fw-bold mb-1">Certificates Issued Report</h5>
            <p class="small text-muted mb-3">{{ counts.certificates }} certified students</p>
            <a href="{{ url_for('api_admin.export_report_csv', report_type='certificates') }}" class="btn btn-outline-warning text-dark btn-sm fw-semibold mt-auto">
                <i class="bi bi-download me-1"></i> Download Certificates CSV
            </a>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card card-itsa p-4 text-center h-100 shadow-sm">
            <i class="bi bi-trophy text-danger fs-1 mb-2"></i>
            <h5 class="fw-bold mb-1">ITSA Points Ledger Report</h5>
            <p class="small text-muted mb-3">{{ counts.points }} transaction events</p>
            <a href="{{ url_for('api_admin.export_report_csv', report_type='points') }}" class="btn btn-outline-danger btn-sm mt-auto">
                <i class="bi bi-download me-1"></i> Download Points CSV
            </a>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card card-itsa p-4 text-center h-100 shadow-sm">
            <i class="bi bi-people text-secondary fs-1 mb-2"></i>
            <h5 class="fw-bold mb-1">User Accounts Directory</h5>
            <p class="small text-muted mb-3">{{ counts.users }} total accounts</p>
            <a href="{{ url_for('api_admin.export_report_csv', report_type='users') }}" class="btn btn-outline-secondary btn-sm mt-auto">
                <i class="bi bi-download me-1"></i> Download Users CSV
            </a>
        </div>
    </div>
</div>
{% endblock %}
"""

# 13. audit_logs.html
views['audit_logs.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}System Audit Logs{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Audit Logs</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Security & Administrative Audit Logs</h4>
        <p class="text-muted small mb-0">Immutable records of administrative actions, user state changes, and security operations</p>
    </div>
</div>

<div class="card card-itsa overflow-hidden shadow-sm">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4">Timestamp</th>
                    <th>Admin / Operator</th>
                    <th>Action</th>
                    <th>Entity Type</th>
                    <th>Target ID</th>
                    <th class="pe-4">Details</th>
                </tr>
            </thead>
            <tbody>
                {% if logs %}
                    {% for l in logs %}
                    <tr>
                        <td class="ps-4 small text-muted">{{ l.created_at.strftime('%b %d, %Y - %H:%M:%S') }}</td>
                        <td class="fw-semibold">{{ l.user.full_name if l.user else 'System' }}</td>
                        <td><span class="badge bg-primary">{{ l.action }}</span></td>
                        <td>{{ l.entity_type }}</td>
                        <td class="font-monospace small">#{{ l.entity_id or '-' }}</td>
                        <td class="pe-4 small text-muted font-monospace">{{ l.details | tojson if l.details else '-' }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="6" class="text-center py-4 text-muted">No audit logs recorded yet.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

# 14. settings.html
views['settings.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Platform Settings{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Platform Settings</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">ITSA Platform Configuration</h4>
        <p class="text-muted small mb-0">System configuration, AI model parameters, and platform branding</p>
    </div>
</div>

<div class="row g-4">
    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm">
            <h5 class="fw-bold mb-3"><i class="bi bi-robot text-primary me-2"></i> AI & Gemini Configuration</h5>
            <div class="mb-3">
                <label class="form-label small fw-semibold">Active LLM Model</label>
                <input type="text" class="form-control" value="gemini-2.5-flash" readonly>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-semibold">Gemini API Status</label>
                <input type="text" class="form-control text-success fw-bold" value="Configured via Environment Variables" readonly>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-semibold">AI Assistant Rate Limit</label>
                <input type="text" class="form-control" value="20 requests/minute per user" readonly>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm">
            <h5 class="fw-bold mb-3"><i class="bi bi-shield-check text-success me-2"></i> Security & RBAC Rules</h5>
            <div class="mb-3">
                <label class="form-label small fw-semibold">Attendance Scanning Rule</label>
                <input type="text" class="form-control" value="Coordinator-only scan validation" readonly>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-semibold">Certificate Generation</label>
                <input type="text" class="form-control" value="Automated ReportLab PDF on verified scan" readonly>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-semibold">Public Verification</label>
                <input type="text" class="form-control" value="Enabled at /certificates/verify/{code}" readonly>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# 15. search.html
views['search.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Admin Search Results{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Search: "{{ search_query }}"</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Global Admin Search Results</h4>
        <p class="text-muted small mb-0">Found {{ total_matches }} matching items for <span class="badge bg-primary">{{ search_query }}</span></p>
    </div>
</div>

<!-- Categorized Search Results -->
{% if students %}
<div class="card card-itsa overflow-hidden shadow-sm mb-4">
    <div class="card-header bg-white py-3 fw-bold"><i class="bi bi-mortarboard text-primary me-2"></i> Matching Students ({{ students|length }})</div>
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <tbody>
                {% for s in students %}
                <tr>
                    <td class="ps-4 fw-bold">{{ s.full_name }}</td>
                    <td>{{ s.email }}</td>
                    <td class="font-monospace small">{{ s.student_profile.student_id if s.student_profile else '-' }}</td>
                    <td>{{ s.student_profile.department if s.student_profile else '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endif %}

{% if events %}
<div class="card card-itsa overflow-hidden shadow-sm mb-4">
    <div class="card-header bg-white py-3 fw-bold"><i class="bi bi-calendar-event text-success me-2"></i> Matching Events ({{ events|length }})</div>
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <tbody>
                {% for e in events %}
                <tr>
                    <td class="ps-4 fw-bold">{{ e.title }}</td>
                    <td>{{ e.category.name if e.category else 'General' }}</td>
                    <td>{{ e.start_datetime.strftime('%b %d, %Y') }}</td>
                    <td><span class="badge bg-light text-dark border">{{ e.status }}</span></td>
                    <td class="text-end pe-4"><a href="{{ url_for('pages.event_detail', event_id=e.id) }}" class="btn btn-sm btn-light">View</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endif %}

{% if registrations %}
<div class="card card-itsa overflow-hidden shadow-sm mb-4">
    <div class="card-header bg-white py-3 fw-bold"><i class="bi bi-ticket-perforated text-info me-2"></i> Matching Registrations ({{ registrations|length }})</div>
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <tbody>
                {% for r in registrations %}
                <tr>
                    <td class="ps-4 font-monospace small text-primary">{{ r.registration_number }}</td>
                    <td class="fw-bold">{{ r.user.full_name }}</td>
                    <td>{{ r.event.title }}</td>
                    <td><span class="badge bg-success">{{ r.status }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endif %}

{% if not students and not events and not registrations and not coordinators and not tickets and not certificates and not posts %}
<div class="card card-itsa p-5 text-center shadow-sm">
    <i class="bi bi-search fs-1 text-muted mb-2"></i>
    <h5>No results matching "{{ search_query }}"</h5>
    <p class="text-muted small">Try searching with a student name, email, event title, or registration number.</p>
</div>
{% endif %}
{% endblock %}
"""

for fname, content in views.items():
    with open(os.path.join(TEMPLATES_DIR, fname), 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Wrote {len(views)} admin view templates in part 4.")
