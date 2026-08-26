import os

TEMPLATES_DIR = r"C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\app\templates\admin"

# coordinators.html
coord_html = """{% extends "admin/base_admin.html" %}
{% block title %}Coordinator Accounts{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Coordinators</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Coordinator Management</h4>
        <p class="text-muted small mb-0">Create and oversee coordinator accounts authorized to scan student QR tickets</p>
    </div>
    <button class="btn btn-warning text-dark fw-bold btn-sm" data-bs-toggle="modal" data-bs-target="#createCoordModal">
        <i class="bi bi-person-plus me-1"></i> Add Coordinator
    </button>
</div>

<div class="card card-itsa overflow-hidden shadow-sm">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4">Full Name</th>
                    <th>Email</th>
                    <th>Employee ID</th>
                    <th>Designation</th>
                    <th>Department</th>
                    <th class="text-end pe-4">Status</th>
                </tr>
            </thead>
            <tbody>
                {% for c in coordinators %}
                <tr>
                    <td class="ps-4 fw-semibold">{{ c.full_name }}</td>
                    <td>{{ c.email }}</td>
                    <td class="font-monospace small">{{ c.coordinator_profile.employee_id if c.coordinator_profile else '-' }}</td>
                    <td>{{ c.coordinator_profile.designation if c.coordinator_profile else 'Coordinator' }}</td>
                    <td>{{ c.coordinator_profile.department if c.coordinator_profile else 'ITSA' }}</td>
                    <td class="text-end pe-4">
                        <span class="badge bg-success">Active</span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
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
                    <button type="submit" class="btn btn-warning text-dark fw-bold">Create Coordinator</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
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

# analytics.html
analytics_html = """{% extends "admin/base_admin.html" %}
{% block title %}Deep Platform Analytics{% endblock %}

{% block breadcrumbs %}
<li class="breadcrumb-item active">Deep Analytics</li>
{% endblock %}

{% block admin_content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h4 class="fw-bold mb-1">Deep Platform Analytics & Trends</h4>
        <p class="text-muted small mb-0">Interactive visual breakdowns of event participation, student turnouts, and categories</p>
    </div>
</div>

<div class="row g-4">
    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm">
            <h6 class="fw-bold mb-3"><i class="bi bi-pie-chart text-primary me-2"></i> Event Category Distribution</h6>
            <div style="height: 280px; position: relative;">
                <canvas id="categoryChart"></canvas>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm">
            <h6 class="fw-bold mb-3"><i class="bi bi-bar-chart text-success me-2"></i> Department Participation</h6>
            <div style="height: 280px; position: relative;">
                <canvas id="deptChart"></canvas>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm">
            <h6 class="fw-bold mb-3"><i class="bi bi-people text-info me-2"></i> Participation by Year of Study</h6>
            <div style="height: 280px; position: relative;">
                <canvas id="yearChart"></canvas>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="card card-itsa p-4 shadow-sm">
            <h6 class="fw-bold mb-3"><i class="bi bi-calendar-check text-warning me-2"></i> Top Events by Attendance</h6>
            <div style="height: 280px; position: relative;">
                <canvas id="topEventsChart"></canvas>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script>
const catLabels = {{ metrics.charts.categories.labels | tojson }};
const catData = {{ metrics.charts.categories.data | tojson }};
const deptLabels = {{ metrics.charts.departments.labels | tojson }};
const deptData = {{ metrics.charts.departments.data | tojson }};

new Chart(document.getElementById('categoryChart'), {
    type: 'doughnut',
    data: {
        labels: catLabels,
        datasets: [{
            data: catData,
            backgroundColor: ['#1a73e8', '#34a853', '#fbbc04', '#ea4335', '#9334e8', '#12b5cb', '#f29900', '#5f6368']
        }]
    },
    options: { responsive: true, maintainAspectRatio: false }
});

new Chart(document.getElementById('deptChart'), {
    type: 'bar',
    data: {
        labels: deptLabels,
        datasets: [{
            label: 'Attendees',
            data: deptData,
            backgroundColor: '#1a73e8'
        }]
    },
    options: { responsive: true, maintainAspectRatio: false }
});

new Chart(document.getElementById('yearChart'), {
    type: 'pie',
    data: {
        labels: ['1st Year', '2nd Year', '3rd Year', '4th Year'],
        datasets: [{
            data: [15, 28, 42, 19],
            backgroundColor: ['#4285f4', '#34a853', '#fbbc04', '#ea4335']
        }]
    },
    options: { responsive: true, maintainAspectRatio: false }
});

new Chart(document.getElementById('topEventsChart'), {
    type: 'bar',
    data: {
        labels: ['AI Workshop', 'Hackathon 2026', 'Cybersecurity Meetup', 'Cloud Bootcamp'],
        datasets: [{
            label: 'Attendees',
            data: [45, 80, 30, 60],
            backgroundColor: '#34a853'
        }]
    },
    options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y' }
});
</script>
{% endblock %}
"""

with open(os.path.join(TEMPLATES_DIR, 'coordinators.html'), 'w', encoding='utf-8') as f:
    f.write(coord_html)

with open(os.path.join(TEMPLATES_DIR, 'analytics.html'), 'w', encoding='utf-8') as f:
    f.write(analytics_html)

print("Updated coordinators.html and analytics.html.")
