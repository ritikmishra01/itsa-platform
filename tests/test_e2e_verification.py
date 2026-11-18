import pytest
from datetime import datetime, timedelta
from app.models.user import User, StudentProfile, CoordinatorProfile
from app.models.event import Event, Venue, EventCategory
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.services.registration_service import RegistrationService
from app.extensions import db


def test_e2e_student_creation_and_persistence(auth_client_admin, app):
    """Test admin creates a student, verifies DB insertion, fields, and uniqueness."""
    payload = {
        'full_name': 'Aaradhya Joshi',
        'email': 'aaradhya.joshi@itsa.edu',
        'student_id': 'AJ2026888',
        'password': 'SecureStudentPass#2026',
        'department': 'Information Technology',
        'year_of_study': 3
    }
    res = auth_client_admin.post('/api/v1/admin/users/student', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['email'] == 'aaradhya.joshi@itsa.edu'

    with app.app_context():
        user = User.query.filter_by(email='aaradhya.joshi@itsa.edu').first()
        assert user is not None
        assert user.role == 'STUDENT'
        assert user.student_profile is not None
        assert user.student_profile.student_id == 'AJ2026888'
        assert user.student_profile.department == 'Information Technology'
        assert user.check_password('SecureStudentPass#2026') is True


def test_e2e_coordinator_creation_and_persistence(auth_client_admin, app):
    """Test admin creates a coordinator, verifies DB insertion, and login ability."""
    payload = {
        'full_name': 'Prof. Devendra Rathore',
        'email': 'devendra.r@itsa.edu',
        'password': 'CoordPass#2026',
        'employee_id': 'EMP888',
        'designation': 'Lead Technical Coordinator',
        'department': 'Computer Engineering'
    }
    res = auth_client_admin.post('/api/v1/admin/coordinators', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['email'] == 'devendra.r@itsa.edu'

    with app.app_context():
        user = User.query.filter_by(email='devendra.r@itsa.edu').first()
        assert user is not None
        assert user.role == 'COORDINATOR'
        assert user.coordinator_profile is not None
        assert user.coordinator_profile.employee_id == 'EMP888'
        assert user.check_password('CoordPass#2026') is True


def test_e2e_duplicate_and_invalid_user_rejection(auth_client_admin):
    """Test duplicate emails, duplicate student IDs, and invalid passwords."""
    # 1. First provision an initial student
    initial_payload = {
        'full_name': 'Original Student',
        'email': 'original.stu@itsa.edu',
        'student_id': 'ORIG2026',
        'password': 'ValidPassword123!',
        'department': 'Information Technology',
        'year_of_study': 1
    }
    res_init = auth_client_admin.post('/api/v1/admin/users/student', json=initial_payload)
    assert res_init.status_code == 201

    # 2. Duplicate email rejection
    duplicate_payload = {
        'full_name': 'Duplicate User',
        'email': 'original.stu@itsa.edu',
        'student_id': 'UNIQUE999',
        'password': 'ValidPassword123!',
        'department': 'Information Technology',
        'year_of_study': 1
    }
    res_dup = auth_client_admin.post('/api/v1/admin/users/student', json=duplicate_payload)
    assert res_dup.status_code == 400
    assert res_dup.get_json()['error']['code'] == 'USER_EXISTS'

    # 3. Duplicate student ID rejection
    duplicate_id_payload = {
        'full_name': 'Duplicate ID User',
        'email': 'unique.new@itsa.edu',
        'student_id': 'ORIG2026',
        'password': 'ValidPassword123!',
        'department': 'Information Technology',
        'year_of_study': 1
    }
    res_dup_id = auth_client_admin.post('/api/v1/admin/users/student', json=duplicate_id_payload)
    assert res_dup_id.status_code == 400
    assert res_dup_id.get_json()['error']['code'] == 'STUDENT_ID_EXISTS'

    # 4. Weak password rejection
    weak_pw_payload = {
        'full_name': 'Weak Password User',
        'email': 'weak.pw@itsa.edu',
        'student_id': 'WEAK001',
        'password': 'short',
        'department': 'Information Technology',
        'year_of_study': 1
    }
    res_weak = auth_client_admin.post('/api/v1/admin/users/student', json=weak_pw_payload)
    assert res_weak.status_code == 400
    assert res_weak.get_json()['error']['code'] == 'PASSWORD_ERROR'


def test_e2e_event_creation_and_registration_flow(app):
    """Test admin creates event, student registers, and prevents duplicate registration."""
    # 1. Admin logs in and creates event
    admin_client = app.test_client()
    login_admin = admin_client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})
    assert login_admin.status_code == 200

    with app.app_context():
        category = EventCategory.query.first()
        venue = Venue.query.first()
        cat_id = category.id if category else 1
        venue_id = venue.id if venue else 1

    event_payload = {
        'title': 'AI Innovations Symposium 2026',
        'description': 'Exploring cutting edge developments in LLMs and generative agents.',
        'category_id': str(cat_id),
        'venue_id': str(venue_id),
        'start_datetime': (datetime.utcnow() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M'),
        'end_datetime': (datetime.utcnow() + timedelta(days=10, hours=4)).strftime('%Y-%m-%dT%H:%M'),
        'registration_deadline': (datetime.utcnow() + timedelta(days=9)).strftime('%Y-%m-%dT%H:%M'),
        'max_participants': '75',
        'status': 'REGISTRATION_OPEN',
        'tags': 'AI, Innovation, LLM'
    }

    res_event = admin_client.post('/api/v1/events', data=event_payload)
    assert res_event.status_code in (200, 201)
    event_data = res_event.get_json()
    assert event_data['success'] is True
    event_id = event_data['data']['id']

    # 2. Student logs in and registers for event
    student_client = app.test_client()
    login_stu = student_client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    assert login_stu.status_code == 200

    res_reg = student_client.post(f'/api/v1/events/{event_id}/register', json={})
    assert res_reg.status_code in (200, 201)
    assert res_reg.get_json()['success'] is True

    # 3. Duplicate registration rejected
    res_dup = student_client.post(f'/api/v1/events/{event_id}/register', json={})
    assert res_dup.status_code == 400
    assert 'already registered' in res_dup.get_json()['error']['message'].lower()


def test_e2e_attendance_marking_and_duplicate_prevention(auth_client_coord, app):
    """Test coordinator marks attendance via QR ticket code and duplicate scan is rejected."""
    with app.app_context():
        event = Event.query.first()
        student = User.query.filter_by(role='STUDENT').first()
        assert event is not None and student is not None

        # Clean existing attendance if any
        existing_att = Attendance.query.filter_by(event_id=event.id, user_id=student.id).first()
        if existing_att:
            db.session.delete(existing_att)
            db.session.commit()

        # Ensure registration and ticket exists
        reg = EventRegistration.query.filter_by(event_id=event.id, user_id=student.id).first()
        if not reg:
            reg = RegistrationService.register_student(event.id, student)

        ticket = EventTicket.query.filter_by(registration_id=reg.id).first()
        assert ticket is not None
        ticket_code = ticket.ticket_code
        event_id = event.id

    # 1. Mark attendance via coordinator QR scan
    scan_payload = {
        'event_id': event_id,
        'ticket_code': ticket_code
    }
    res_scan = auth_client_coord.post('/api/v1/attendance/scan', json=scan_payload)
    assert res_scan.status_code in (200, 201)
    assert res_scan.get_json()['success'] is True
    assert res_scan.get_json()['data']['status'] == 'PRESENT'

    # 2. Duplicate attendance rejected
    res_dup = auth_client_coord.post('/api/v1/attendance/scan', json=scan_payload)
    assert res_dup.status_code == 400
    assert 'already' in res_dup.get_json()['error']['message'].lower()
