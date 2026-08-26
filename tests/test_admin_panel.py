import pytest
from app.models.user import User

def test_admin_can_access_all_admin_views(auth_client_admin):
    admin_routes = [
        '/admin/dashboard',
        '/admin/users',
        '/admin/events',
        '/admin/coordinators',
        '/admin/registrations',
        '/admin/attendance',
        '/admin/certificates',
        '/admin/community',
        '/admin/gallery',
        '/admin/notifications',
        '/admin/gamification',
        '/admin/ai-center',
        '/admin/analytics',
        '/admin/reports',
        '/admin/audit-logs',
        '/admin/settings',
        '/admin/search?q=test'
    ]

    for route in admin_routes:
        res = auth_client_admin.get(route)
        assert res.status_code == 200, f"Failed accessing {route} with status {res.status_code}"

def test_student_and_coordinator_cannot_access_admin_panel(auth_client_student, auth_client_coord):
    # Student and Coordinator cannot access admin HTML views (redirected to home with flash message)
    res_student_page = auth_client_student.get('/admin/dashboard')
    assert res_student_page.status_code == 302

    res_coord_page = auth_client_coord.get('/admin/dashboard')
    assert res_coord_page.status_code == 302

    # Student and Coordinator cannot access admin API endpoints (403 Forbidden)
    res_student_api = auth_client_student.get('/api/v1/admin/users')
    assert res_student_api.status_code == 403

    res_coord_api = auth_client_coord.get('/api/v1/admin/users')
    assert res_coord_api.status_code == 403

def test_admin_create_student_api(auth_client_admin):
    payload = {
        'full_name': 'Admin Provisioned Student',
        'email': 'admin_student@college.edu',
        'student_id': 'ADM2026999',
        'password': 'SecureStudentPassword123!',
        'department': 'Computer Science',
        'year_of_study': 2
    }
    res = auth_client_admin.post('/api/v1/admin/users/student', json=payload)
    assert res.status_code == 201
    assert res.get_json()['success'] is True

def test_admin_broadcast_notification(auth_client_admin):
    payload = {
        'title': 'Emergency Campus Announcement',
        'message': 'All classes are online today due to weather conditions.',
        'audience': 'ALL'
    }
    res = auth_client_admin.post('/api/v1/admin/notifications/broadcast', json=payload)
    assert res.status_code == 200
    assert res.get_json()['success'] is True
    assert 'sent_count' in res.get_json()['data']

def test_admin_export_csv_reports(auth_client_admin):
    report_types = ['events', 'registrations', 'attendance', 'certificates', 'points', 'users']

    for r_type in report_types:
        res = auth_client_admin.get(f'/api/v1/admin/reports/export/{r_type}')
        assert res.status_code == 200
        assert 'text/csv' in res.content_type
        assert len(res.data) > 0

