import os

TEMPLATES_DIR = r"C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\app\templates\admin"
views = {}

# 2. users.html
views['users.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}User Management{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">User Directory</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">User Management & RBAC Directory</h4>
        <p class="text-muted small mb-0">Oversee all registered students, coordinators, and administrative privileges</p>
    </div>
    <div class="d-flex gap-2">
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createStudentModal">
            <i class="bi bi-person-plus me-1"></i> Add Student
        </button>
        <button class="btn btn-warning btn-sm text-dark fw-semibold" data-bs-toggle="modal" data-bs-target="#createCoordModal">
            <i class="bi bi-person-badge me-1"></i> Add Coordinator
        </button>
    </div>
</div>

<ul class="nav nav-tabs mb-4" id="userTabs" role="tablist">
    <li class="nav-item">
        <button class="nav-link active fw-semibold" id="students-tab" data-bs-toggle="tab" data-bs-target="#studentsTabPane">
            <i class="bi bi-mortarboard me-1"></i> Students ({{ students|length }})
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link fw-semibold" id="coords-tab" data-bs-toggle="tab" data-bs-target="#coordsTabPane">
            <i class="bi bi-person-badge me-1"></i> Coordinators ({{ coordinators|length }})
        </button>
    </li>
</ul>

<div class="tab-content" id="userTabsContent">
    <div class="tab-pane fade show active" id="studentsTabPane">
        <div class="card card-itsa overflow-hidden shadow-sm">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Student</th>
                            <th>Student ID</th>
                            <th>Department & Year</th>
                            <th>Points</th>
                            <th>Status</th>
                            <th class="text-end pe-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if students %}
                            {% for u in students %}
                            <tr>
                                <td class="ps-4">
                                    <div class="fw-bold text-dark">{{ u.full_name }}</div>
                                    <div class="small text-muted">{{ u.email }}</div>
                                </td>
                                <td class="font-monospace small">{{ u.student_profile.student_id if u.student_profile else '-' }}</td>
                                <td>
                                    <div>{{ u.student_profile.department if u.student_profile else '-' }}</div>
                                    <small class="text-muted">Year {{ u.student_profile.year_of_study if u.student_profile else '1' }}</small>
                                </td>
                                <td>
                                    <span class="points-pill">{{ u.student_profile.total_points if u.student_profile else 0 }} pts</span>
                                </td>
                                <td>
                                    {% if u.is_suspended %}
                                    <span class="badge bg-danger">Suspended</span>
                                    {% else %}
                                    <span class="badge bg-success">Active</span>
                                    {% endif %}
                                </td>
                                <td class="text-end pe-4">
                                    {% if u.is_suspended %}
                                    <button class="btn btn-sm btn-outline-success" onclick="toggleSuspend({{ u.id }}, false)">Reactivate</button>
                                    {% else %}
                                    <button class="btn btn-sm btn-outline-danger" onclick="toggleSuspend({{ u.id }}, true)">Suspend</button>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="6" class="text-center py-4 text-muted">No students found.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="tab-pane fade" id="coordsTabPane">
        <div class="card card-itsa overflow-hidden shadow-sm">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Coordinator</th>
                            <th>Employee ID</th>
                            <th>Designation</th>
                            <th>Department</th>
                            <th>Status</th>
                            <th class="text-end pe-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if coordinators %}
                            {% for c in coordinators %}
                            <tr>
                                <td class="ps-4">
                                    <div class="fw-bold text-dark">{{ c.full_name }}</div>
                                    <div class="small text-muted">{{ c.email }}</div>
                                </td>
                                <td class="font-monospace small">{{ c.coordinator_profile.employee_id if c.coordinator_profile else '-' }}</td>
                                <td>{{ c.coordinator_profile.designation if c.coordinator_profile else 'Coordinator' }}</td>
                                <td>{{ c.coordinator_profile.department if c.coordinator_profile else 'IT' }}</td>
                                <td><span class="badge bg-success">Active</span></td>
                                <td class="text-end pe-4">
                                    <button class="btn btn-sm btn-outline-danger" onclick="toggleSuspend({{ c.id }}, true)">Deactivate</button>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="6" class="text-center py-4 text-muted">No coordinators found.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="createStudentModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold">Provision Student Account</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="createStudentForm">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Full Name *</label>
                        <input type="text" class="form-control" name="full_name" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Student ID / Roll Number *</label>
                        <input type="text" class="form-control font-monospace" name="student_id" required placeholder="e.g. IT2026001">
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Email Address *</label>
                        <input type="email" class="form-control" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Password *</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Department</label>
                            <select class="form-select" name="department">
                                {% for d in departments %}<option value="{{ d }}">{{ d }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Year of Study</label>
                            <select class="form-select" name="year_of_study">
                                <option value="1">1st Year</option>
                                <option value="2">2nd Year</option>
                                <option value="3">3rd Year</option>
                                <option value="4">4th Year</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Student</button>
                </div>
            </form>
        </div>
    </div>
</div>

<div class="modal fade" id="createCoordModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold">Provision Coordinator Account</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="createCoordForm">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Full Name *</label>
                        <input type="text" class="form-control" name="full_name" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Email *</label>
                        <input type="email" class="form-control" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Password *</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Employee ID</label>
                            <input type="text" class="form-control" name="employee_id">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Designation</label>
                            <input type="text" class="form-control" name="designation" value="Event Coordinator">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Department</label>
                        <input type="text" class="form-control" name="department" value="Information Technology">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-warning text-dark fw-semibold">Create Coordinator</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function toggleSuspend(userId, suspend) {
    const action = suspend ? 'suspend' : 'unsuspend';
    if (!confirm(`Are you sure you want to ${action} this user?`)) return;
    try {
        await apiCall(`/api/v1/admin/users/${userId}/${action}`, 'POST', {});
        showToast(`User status updated.`, 'success');
        setTimeout(() => window.location.reload(), 600);
    } catch(err) {}
}

document.getElementById('createStudentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(this));
    try {
        await apiCall('/api/v1/admin/users/student', 'POST', data);
        showToast('Student account created successfully!', 'success');
        setTimeout(() => window.location.reload(), 600);
    } catch(err) {}
});

document.getElementById('createCoordForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(this));
    try {
        await apiCall('/api/v1/admin/coordinators', 'POST', data);
        showToast('Coordinator account created!', 'success');
        setTimeout(() => window.location.reload(), 600);
    } catch(err) {}
});
</script>
{% endblock %}
"""

# 3. events.html
views['events.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Event Management{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Event Lifecycle</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Event Lifecycle & Scheduling</h4>
        <p class="text-muted small mb-0">Create, edit, assign coordinators, and manage lifecycle states of ITSA events</p>
    </div>
    <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createEventModal">
        <i class="bi bi-plus-lg me-1"></i> Create New Event
    </button>
</div>

<div class="card card-itsa overflow-hidden shadow-sm">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4">Title</th>
                    <th>Category</th>
                    <th>Date & Time</th>
                    <th>Venue</th>
                    <th>Registrations</th>
                    <th>Status</th>
                    <th class="text-end pe-4">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% if events %}
                    {% for event in events %}
                    <tr>
                        <td class="ps-4">
                            <div class="fw-bold text-dark">{{ event.title }}</div>
                            <small class="text-muted font-monospace">ID: #{{ event.id }}</small>
                        </td>
                        <td><span class="badge bg-light text-dark border">{{ event.category.name if event.category else 'General' }}</span></td>
                        <td>{{ event.start_datetime.strftime('%b %d, %Y - %I:%M %p') }}</td>
                        <td>{{ event.venue.name if event.venue else 'TBA' }}</td>
                        <td>
                            <span class="fw-semibold">{{ event.current_registrations }}</span> / {{ event.max_participants if event.max_participants else '∞' }}
                        </td>
                        <td>
                            <select class="form-select form-select-sm" style="width: 170px;" onchange="updateStatus({{ event.id }}, this.value)">
                                {% for s in ['DRAFT', 'PUBLISHED', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'ONGOING', 'COMPLETED', 'CANCELLED'] %}
                                <option value="{{ s }}" {% if event.status == s %}selected{% endif %}>{{ s }}</option>
                                {% endfor %}
                            </select>
                        </td>
                        <td class="text-end pe-4">
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="openAssignCoordModal({{ event.id }})" title="Assign Coordinator">
                                <i class="bi bi-person-plus"></i> Coord
                            </button>
                            <a href="{{ url_for('pages.event_detail', event_id=event.id) }}" class="btn btn-sm btn-light border" title="View Public Page">
                                <i class="bi bi-eye"></i>
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="7" class="text-center py-4 text-muted">No events found.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>

<div class="modal fade" id="createEventModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold">Create New ITSA Event</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="createEventForm" enctype="multipart/form-data">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Event Title *</label>
                        <input type="text" class="form-control" name="title" id="eventTitleInput" required placeholder="e.g. AI & Cloud Architecture Summit 2026">
                    </div>

                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Category *</label>
                            <select class="form-select" name="category_id" id="eventCategorySelect" required>
                                {% for c in categories %}
                                <option value="{{ c.id }}">{{ c.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Venue *</label>
                            <select class="form-select" name="venue_id" id="eventVenueSelect" required>
                                {% for v in venues %}
                                <option value="{{ v.id }}">{{ v.name }} (Cap: {{ v.capacity }})</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold mb-0">Description *</label>
                            <button type="button" class="btn btn-sm btn-outline-primary py-0" id="btnAIGenDesc">
                                <i class="bi bi-magic me-1"></i> Generate with Gemini AI
                            </button>
                        </div>
                        <textarea class="form-control" name="description" id="eventDescriptionInput" rows="3" required placeholder="Event details, schedule, and expectations..."></textarea>
                    </div>

                    <div class="row g-3 mb-3">
                        <div class="col-md-4">
                            <label class="form-label small fw-semibold">Start Date & Time *</label>
                            <input type="datetime-local" class="form-control" name="start_datetime" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label small fw-semibold">End Date & Time *</label>
                            <input type="datetime-local" class="form-control" name="end_datetime" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label small fw-semibold">Registration Deadline *</label>
                            <input type="datetime-local" class="form-control" name="registration_deadline" required>
                        </div>
                    </div>

                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Max Participants (Optional)</label>
                            <input type="number" class="form-control" name="max_participants" placeholder="Leave blank for unlimited">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Initial Status</label>
                            <select class="form-select" name="status">
                                <option value="REGISTRATION_OPEN">REGISTRATION_OPEN</option>
                                <option value="PUBLISHED">PUBLISHED</option>
                                <option value="DRAFT">DRAFT</option>
                            </select>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Tags (Comma-separated)</label>
                        <input type="text" class="form-control" name="tags" placeholder="e.g. Python, AI, Cloud, Workshop">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Event</button>
                </div>
            </form>
        </div>
    </div>
</div>

<div class="modal fade" id="assignCoordModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold">Assign Event Coordinator</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="assignCoordForm">
                <input type="hidden" id="assignEventId" name="event_id">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Select Coordinator *</label>
                        <select class="form-select" name="coordinator_id" required>
                            {% for c in coordinators %}
                            <option value="{{ c.id }}">{{ c.full_name }} ({{ c.email }})</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Role in Event</label>
                        <input type="text" class="form-control" name="role_in_event" value="Lead Coordinator" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="submit" class="btn btn-primary">Confirm Assignment</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function updateStatus(eventId, newStatus) {
    try {
        await apiCall(`/api/v1/events/${eventId}/status`, 'POST', { status: newStatus });
        showToast(`Event status updated to ${newStatus}`, 'success');
    } catch(err) {}
}

function openAssignCoordModal(eventId) {
    document.getElementById('assignEventId').value = eventId;
    new bootstrap.Modal(document.getElementById('assignCoordModal')).show();
}

document.getElementById('assignCoordForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const eventId = document.getElementById('assignEventId').value;
    const data = Object.fromEntries(new FormData(this));
    try {
        await apiCall(`/api/v1/events/${eventId}/coordinators`, 'POST', data);
        showToast('Coordinator assigned successfully.', 'success');
        bootstrap.Modal.getInstance(document.getElementById('assignCoordModal')).hide();
    } catch(err) {}
});

document.getElementById('createEventForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    try {
        await apiCall('/api/v1/events', 'POST', formData, true);
        showToast('Event created successfully!', 'success');
        setTimeout(() => window.location.reload(), 600);
    } catch(err) {}
});

document.getElementById('btnAIGenDesc').addEventListener('click', async function() {
    const title = document.getElementById('eventTitleInput').value.trim();
    if (!title) {
        showToast('Please enter an event title first.', 'warning');
        return;
    }
    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Generating...';

    const catSelect = document.getElementById('eventCategorySelect');
    const catName = catSelect.options[catSelect.selectedIndex].text;
    const venueSelect = document.getElementById('eventVenueSelect');
    const venueName = venueSelect.options[venueSelect.selectedIndex].text;

    try {
        const res = await apiCall('/api/v1/ai/generate-description', 'POST', {
            title: title,
            category_name: catName,
            venue_name: venueName,
            start_datetime: 'Upcoming'
        });
        document.getElementById('eventDescriptionInput').value = res.data.description;
        showToast('Gemini generated event description!', 'success');
    } catch(err) {
    } finally {
        this.disabled = false;
        this.innerHTML = '<i class="bi bi-magic me-1"></i> Generate with Gemini AI';
    }
});
</script>
{% endblock %}
"""

# 4. registrations.html
views['registrations.html'] = """{% extends "admin/base_admin.html" %}
{% block title %}Registrations & Tickets{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Registrations & Tickets</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Registration & Ticket Management</h4>
        <p class="text-muted small mb-0">Monitor student registrations, digital ticket codes, and seat bookings</p>
    </div>
    <a href="{{ url_for('api_admin.export_report_csv', report_type='registrations') }}" class="btn btn-outline-primary btn-sm">
        <i class="bi bi-download me-1"></i> Export CSV
    </a>
</div>

<!-- Metrics Row -->
<div class="row g-3 mb-4">
    <div class="col-md-4">
        <div class="card card-itsa p-3 border-start border-4 border-primary">
            <div class="text-muted small fw-semibold">Total Registrations</div>
            <h3 class="fw-bold mb-0 text-primary">{{ total_count }}</h3>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-itsa p-3 border-start border-4 border-success">
            <div class="text-muted small fw-semibold">Confirmed Bookings</div>
            <h3 class="fw-bold mb-0 text-success">{{ confirmed_count }}</h3>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-itsa p-3 border-start border-4 border-danger">
            <div class="text-muted small fw-semibold">Cancelled</div>
            <h3 class="fw-bold mb-0 text-danger">{{ cancelled_count }}</h3>
        </div>
    </div>
</div>

<!-- Registrations Table -->
<div class="card card-itsa overflow-hidden shadow-sm">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4">Student</th>
                    <th>Event</th>
                    <th>Reg Number</th>
                    <th>Ticket Code</th>
                    <th>Date</th>
                    <th class="text-end pe-4">Status</th>
                </tr>
            </thead>
            <tbody>
                {% if registrations %}
                    {% for r in registrations %}
                    <tr>
                        <td class="ps-4">
                            <div class="fw-bold text-dark">{{ r.user.full_name }}</div>
                            <div class="small text-muted">{{ r.user.email }}</div>
                        </td>
                        <td>
                            <div class="fw-semibold">{{ r.event.title }}</div>
                            <small class="text-muted">{{ r.event.start_datetime.strftime('%b %d, %Y') }}</small>
                        </td>
                        <td class="font-monospace small text-primary">{{ r.registration_number }}</td>
                        <td class="font-monospace small text-muted">{{ r.ticket.ticket_code if r.ticket else '-' }}</td>
                        <td class="small">{{ r.registered_at.strftime('%b %d, %H:%M') }}</td>
                        <td class="text-end pe-4">
                            <span class="badge {% if r.status == 'CONFIRMED' %}bg-success{% else %}bg-secondary{% endif %}">
                                {{ r.status }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="6" class="text-center py-4 text-muted">No registrations found.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

for fname, content in views.items():
    with open(os.path.join(TEMPLATES_DIR, fname), 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Wrote {len(views)} admin view templates in part 2.")
