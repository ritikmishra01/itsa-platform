import os

TEMPLATES_DIR = r"C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\app\templates\admin"
views = {}

# 5. attendance.html
views['attendance.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}QR Attendance Center{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">QR Attendance Roster</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">QR Attendance Verification Records</h4>
        <p class="text-muted small mb-0">Audited check-in scans performed by authorized coordinators</p>
    </div>
    <a href="{{ url_for('api_admin.export_report_csv', report_type='attendance') }}" class="btn btn-outline-success btn-sm">
        <i class="bi bi-file-earmark-spreadsheet me-1"></i> Export Attendance CSV
    </a>
</div>

<!-- Attendance Stats -->
<div class="row g-3 mb-4">
    <div class="col-md-4">
        <div class="card card-itsa p-3 border-start border-4 border-success">
            <div class="text-muted small fw-semibold">Total Verified Attendees</div>
            <h3 class="fw-bold mb-0 text-success">{{ total_attended }}</h3>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-itsa p-3 border-start border-4 border-primary">
            <div class="text-muted small fw-semibold">Confirmed Registrations</div>
            <h3 class="fw-bold mb-0 text-primary">{{ total_registered }}</h3>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-itsa p-3 border-start border-4 border-info">
            <div class="text-muted small fw-semibold">Overall Attendance Rate</div>
            <h3 class="fw-bold mb-0 text-info">{{ attendance_rate }}%</h3>
        </div>
    </div>
</div>

<!-- Attendance Records Table -->
<div class="card card-itsa overflow-hidden shadow-sm">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4">Student</th>
                    <th>Student ID</th>
                    <th>Event</th>
                    <th>Ticket Code</th>
                    <th>Scanned By</th>
                    <th>Timestamp</th>
                    <th class="text-end pe-4">Status</th>
                </tr>
            </thead>
            <tbody>
                {% if records %}
                    {% for r in records %}
                    <tr>
                        <td class="ps-4">
                            <div class="fw-bold text-dark">{{ r.student.full_name }}</div>
                            <div class="small text-muted">{{ r.student.email }}</div>
                        </td>
                        <td class="font-monospace small">{{ r.student.student_profile.student_id if r.student.student_profile else '-' }}</td>
                        <td>{{ r.event.title }}</td>
                        <td class="font-monospace small text-muted">{{ r.ticket.ticket_code if r.ticket else '-' }}</td>
                        <td><span class="badge bg-warning text-dark">{{ r.coordinator.full_name if r.coordinator else 'Coordinator' }}</span></td>
                        <td class="small">{{ r.scanned_at.strftime('%b %d, %Y - %I:%M:%S %p') }}</td>
                        <td class="text-end pe-4"><span class="badge bg-success">{{ r.status }}</span></td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="7" class="text-center py-4 text-muted">No attendance scans recorded yet.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

# 6. certificates.html
views['certificates.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Certificate Center{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Certificate Center</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Certificate Management Center</h4>
        <p class="text-muted small mb-0">All automated ReportLab certificates issued for verified event attendance</p>
    </div>
    <a href="{{ url_for('api_admin.export_report_csv', report_type='certificates') }}" class="btn btn-outline-warning text-dark btn-sm fw-semibold">
        <i class="bi bi-download me-1"></i> Export Certificates CSV
    </a>
</div>

<!-- Certificates Table -->
<div class="card card-itsa overflow-hidden shadow-sm">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4">Recipient Student</th>
                    <th>Event</th>
                    <th>Certificate ID</th>
                    <th>Issue Date</th>
                    <th>Status</th>
                    <th class="text-end pe-4">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% if certificates %}
                    {% for c in certificates %}
                    <tr>
                        <td class="ps-4">
                            <div class="fw-bold text-dark">{{ c.user.full_name }}</div>
                            <div class="small text-muted">{{ c.user.email }}</div>
                        </td>
                        <td>{{ c.event.title }}</td>
                        <td class="font-monospace small text-primary fw-semibold">{{ c.certificate_code }}</td>
                        <td class="small">{{ c.issued_at.strftime('%b %d, %Y') }}</td>
                        <td><span class="badge bg-success">Verified & Valid</span></td>
                        <td class="text-end pe-4">
                            <a href="{{ url_for('pages.verify_certificate_page') }}?code={{ c.certificate_code }}" target="_blank" class="btn btn-sm btn-outline-primary me-1">
                                <i class="bi bi-patch-check me-1"></i> Verify
                            </a>
                            <a href="{{ url_for('api_certificates.download_certificate', cert_id=c.id) }}" class="btn btn-sm btn-light border">
                                <i class="bi bi-download"></i> PDF
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="6" class="text-center py-4 text-muted">No certificates generated yet.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

# 7. community.html
views['community.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Community & Content Moderation{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Community & Moderation</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Community Oversight & Content Moderation</h4>
        <p class="text-muted small mb-0">Manage social posts, comments, reports, and AI policy enforcement</p>
    </div>
</div>

<!-- Moderation Metrics -->
<div class="row g-3 mb-4">
    <div class="col-md-3">
        <div class="card card-itsa p-3 border-start border-4 border-primary">
            <div class="text-muted small">Total Posts</div>
            <h4 class="fw-bold mb-0 text-primary">{{ posts|length }}</h4>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-itsa p-3 border-start border-4 border-success">
            <div class="text-muted small">Total Comments</div>
            <h4 class="fw-bold mb-0 text-success">{{ comments|length }}</h4>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-itsa p-3 border-start border-4 border-warning">
            <div class="text-muted small">Total Reactions</div>
            <h4 class="fw-bold mb-0 text-warning">{{ reactions_count }}</h4>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-itsa p-3 border-start border-4 border-danger">
            <div class="text-muted small">Pending Reports</div>
            <h4 class="fw-bold mb-0 text-danger">{{ pending_reports|length }}</h4>
        </div>
    </div>
</div>

<!-- Tabs -->
<ul class="nav nav-tabs mb-4" id="communityTabs">
    <li class="nav-item">
        <button class="nav-link active fw-semibold" data-bs-toggle="tab" data-bs-target="#reportsTab">
            <i class="bi bi-shield-exclamation text-danger me-1"></i> Reports Queue ({{ reports|length }})
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link fw-semibold" data-bs-toggle="tab" data-bs-target="#postsTab">
            <i class="bi bi-chat-square-text me-1"></i> All Posts ({{ posts|length }})
        </button>
    </li>
</ul>

<div class="tab-content">
    <!-- Reports Tab -->
    <div class="tab-pane fade show active" id="reportsTab">
        <div class="card card-itsa overflow-hidden shadow-sm">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Reported Content</th>
                            <th>Reason</th>
                            <th>Reporter</th>
                            <th>Timestamp</th>
                            <th>Status</th>
                            <th class="text-end pe-4">Decision</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if reports %}
                            {% for r in reports %}
                            <tr>
                                <td class="ps-4">
                                    {% if r.reported_post %}
                                    <div class="small fw-semibold text-truncate" style="max-width: 280px;">{{ r.reported_post.content }}</div>
                                    <small class="text-muted">By: {{ r.reported_post.user.full_name }}</small>
                                    {% elif r.reported_comment %}
                                    <div class="small fw-semibold text-truncate" style="max-width: 280px;">{{ r.reported_comment.content }}</div>
                                    <small class="text-muted">By: {{ r.reported_comment.user.full_name }}</small>
                                    {% else %}
                                    <span class="text-muted small">Item removed</span>
                                    {% endif %}
                                </td>
                                <td><span class="badge bg-danger">{{ r.reason }}</span></td>
                                <td>{{ r.reporter.full_name if r.reporter else 'Anonymous' }}</td>
                                <td class="small">{{ r.created_at.strftime('%b %d, %H:%M') }}</td>
                                <td>
                                    <span class="badge {% if r.status == 'PENDING' %}bg-warning text-dark{% elif r.status == 'RESOLVED' %}bg-success{% else %}bg-secondary{% endif %}">
                                        {{ r.status }}
                                    </span>
                                </td>
                                <td class="text-end pe-4">
                                    {% if r.status == 'PENDING' %}
                                    <button class="btn btn-sm btn-danger me-1" onclick="resolveReport({{ r.id }}, 'REMOVE_POST')">Remove</button>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="resolveReport({{ r.id }}, 'DISMISSED')">Dismiss</button>
                                    {% else %}
                                    <span class="small text-muted">Handled</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="6" class="text-center py-4 text-muted">No content reports in queue.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Posts Tab -->
    <div class="tab-pane fade" id="postsTab">
        <div class="card card-itsa overflow-hidden shadow-sm">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Author</th>
                            <th>Content</th>
                            <th>Reactions & Comments</th>
                            <th>Date</th>
                            <th>Status</th>
                            <th class="text-end pe-4">Toggle</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if posts %}
                            {% for p in posts %}
                            <tr>
                                <td class="ps-4">
                                    <div class="fw-bold">{{ p.user.full_name }}</div>
                                    <small class="text-muted">{{ p.user.email }}</small>
                                </td>
                                <td><div class="small text-truncate" style="max-width: 320px;">{{ p.content }}</div></td>
                                <td>
                                    <span class="badge bg-light text-dark border me-1"><i class="bi bi-heart-fill text-danger me-1"></i> {{ p.reactions.count() }}</span>
                                    <span class="badge bg-light text-dark border"><i class="bi bi-chat-fill text-primary me-1"></i> {{ p.comments.count() }}</span>
                                </td>
                                <td class="small">{{ p.created_at.strftime('%b %d, %H:%M') }}</td>
                                <td>
                                    {% if p.is_active %}<span class="badge bg-success">Active</span>{% else %}<span class="badge bg-danger">Hidden</span>{% endif %}
                                </td>
                                <td class="text-end pe-4">
                                    <button class="btn btn-sm {% if p.is_active %}btn-outline-danger{% else %}btn-outline-success{% endif %}" onclick="togglePost({{ p.id }})">
                                        {% if p.is_active %}Hide{% else %}Restore{% endif %}
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="6" class="text-center py-4 text-muted">No posts available.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function resolveReport(reportId, action) {
    try {
        await apiCall(`/api/v1/admin/reports/${reportId}/resolve`, 'POST', { action: action });
        showToast('Report handled successfully.', 'success');
        setTimeout(() => window.location.reload(), 500);
    } catch(err) {}
}

async function togglePost(postId) {
    try {
        await apiCall(`/api/v1/admin/posts/${postId}/toggle-active`, 'POST', {});
        showToast('Post status toggled.', 'success');
        setTimeout(() => window.location.reload(), 500);
    } catch(err) {}
}
</script>
{% endblock %}
"""

# 8. gallery.html
views['gallery.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Media & Event Gallery{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Media & Event Gallery</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Event Media & Gallery Management</h4>
        <p class="text-muted small mb-0">Browse and curate photos and videos uploaded for ITSA events</p>
    </div>
</div>

<div class="row g-4">
    {% if gallery_items %}
        {% for item in gallery_items %}
        <div class="col-sm-6 col-md-4 col-lg-3">
            <div class="card card-itsa overflow-hidden h-100 shadow-sm">
                <img src="/{{ item.file_path }}" class="card-img-top" style="height: 180px; object-fit: cover;" alt="Gallery Media">
                <div class="card-body p-3 d-flex flex-column justify-content-between">
                    <div>
                        <div class="small fw-bold text-truncate">{{ item.event.title }}</div>
                        <p class="small text-muted mb-2 text-truncate">{{ item.caption or 'No caption' }}</p>
                    </div>
                    <div class="d-flex justify-content-between align-items-center border-top pt-2">
                        <small class="text-muted">{{ item.uploaded_at.strftime('%b %d, %Y') }}</small>
                        <button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="deleteGalleryItem({{ item.id }})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="col-12 text-center py-5 text-muted">
            <i class="bi bi-images fs-1 d-block mb-2"></i>
            No event gallery media uploaded yet.
        </div>
    {% endif %}
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function deleteGalleryItem(id) {
    if (!confirm('Are you sure you want to delete this media item?')) return;
    try {
        await apiCall(`/api/v1/admin/gallery/${id}`, 'POST', {});
        showToast('Media item deleted.', 'success');
        setTimeout(() => window.location.reload(), 500);
    } catch(err) {}
}
</script>
{% endblock %}
"""

# 9. notifications.html
views['notifications.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Notifications & Broadcast{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Broadcast & Notifications</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Broadcast & Notification Center</h4>
        <p class="text-muted small mb-0">Dispatch official announcements to all students, specific branches, or event attendees</p>
    </div>
</div>

<div class="row g-4">
    <!-- Broadcast Form Card -->
    <div class="col-lg-5">
        <div class="card card-itsa p-4 shadow-sm">
            <h5 class="fw-bold mb-3"><i class="bi bi-megaphone text-danger me-2"></i> Compose Announcement</h5>
            <form id="broadcastForm">
                <div class="mb-3">
                    <label class="form-label small fw-semibold">Notification Title *</label>
                    <input type="text" class="form-control" name="title" required placeholder="e.g. ITSA Flagship Hackathon Registrations Open!">
                </div>
                <div class="mb-3">
                    <label class="form-label small fw-semibold">Target Audience *</label>
                    <select class="form-select" name="audience" id="audienceSelect" onchange="toggleAudienceOptions(this.value)">
                        <option value="ALL">All Active Students (Broadcast)</option>
                        <option value="DEPT">Specific Department</option>
                        <option value="YEAR">Specific Year of Study</option>
                        <option value="EVENT">Event Registered Participants</option>
                    </select>
                </div>

                <div class="mb-3" id="deptSelectWrap" style="display: none;">
                    <label class="form-label small fw-semibold">Select Department</label>
                    <select class="form-select" name="department">
                        {% for d in departments %}<option value="{{ d }}">{{ d }}</option>{% endfor %}
                    </select>
                </div>

                <div class="mb-3" id="yearSelectWrap" style="display: none;">
                    <label class="form-label small fw-semibold">Select Year</label>
                    <select class="form-select" name="year">
                        <option value="1">1st Year</option>
                        <option value="2">2nd Year</option>
                        <option value="3">3rd Year</option>
                        <option value="4">4th Year</option>
                    </select>
                </div>

                <div class="mb-3" id="eventSelectWrap" style="display: none;">
                    <label class="form-label small fw-semibold">Select Event</label>
                    <select class="form-select" name="event_id">
                        {% for e in events %}<option value="{{ e.id }}">{{ e.title }}</option>{% endfor %}
                    </select>
                </div>

                <div class="mb-3">
                    <label class="form-label small fw-semibold">Message Body *</label>
                    <textarea class="form-control" name="message" rows="4" required placeholder="Type the full announcement details here..."></textarea>
                </div>

                <button type="submit" class="btn btn-danger w-100 fw-semibold">
                    <i class="bi bi-send-fill me-1"></i> Send Announcement Broadcast
                </button>
            </form>
        </div>
    </div>

    <!-- Notification Log -->
    <div class="col-lg-7">
        <div class="card card-itsa p-4 shadow-sm h-100">
            <h5 class="fw-bold mb-3"><i class="bi bi-clock-history text-primary me-2"></i> Recent Sent Notifications</h5>
            <div class="list-group list-group-flush">
                {% if notifications %}
                    {% for n in notifications %}
                    <div class="list-group-item px-0 py-2 border-bottom">
                        <div class="d-flex justify-content-between align-items-start">
                            <h6 class="fw-bold mb-1">{{ n.title }}</h6>
                            <span class="badge bg-light text-dark border">{{ n.type }}</span>
                        </div>
                        <p class="small text-muted mb-1">{{ n.message }}</p>
                        <div class="d-flex justify-content-between align-items-center text-muted" style="font-size: 0.75rem;">
                            <span>Recipient: {{ n.user.full_name }}</span>
                            <span>{{ n.created_at.strftime('%b %d, %H:%M') }}</span>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="text-center py-5 text-muted small">No notifications sent yet.</div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
function toggleAudienceOptions(val) {
    document.getElementById('deptSelectWrap').style.display = (val === 'DEPT') ? 'block' : 'none';
    document.getElementById('yearSelectWrap').style.display = (val === 'YEAR') ? 'block' : 'none';
    document.getElementById('eventSelectWrap').style.display = (val === 'EVENT') ? 'block' : 'none';
}

document.getElementById('broadcastForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!confirm('Are you sure you want to broadcast this announcement to the selected students?')) return;
    const data = Object.fromEntries(new FormData(this));
    try {
        const res = await apiCall('/api/v1/admin/notifications/broadcast', 'POST', data);
        showToast(res.message || 'Broadcast dispatched successfully!', 'success');
        setTimeout(() => window.location.reload(), 600);
    } catch(err) {}
});
</script>
{% endblock %}
"""

for fname, content in views.items():
    with open(os.path.join(TEMPLATES_DIR, fname), 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Wrote {len(views)} admin view templates in part 3.")
