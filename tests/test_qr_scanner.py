import pytest
from app import db
from app.models.user import User, CoordinatorProfile
from app.models.event import Event, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.services.ticket_service import TicketService
from datetime import datetime, timedelta

def setup_registration_and_ticket(app, event_id, student_id):
    with app.app_context():
        reg = EventRegistration(
            event_id=event_id,
            user_id=student_id,
            registration_number=f"REG-TEST-{student_id}-{event_id}",
            status="CONFIRMED"
        )
        db.session.add(reg)
        db.session.flush()

        ticket = TicketService.generate_ticket(reg.id)
        ticket_code = ticket.ticket_code
        ticket_id = ticket.id
        reg_id = reg.id
        db.session.commit()
        return reg_id, ticket_id, ticket_code

def test_valid_qr_scan_by_assigned_coordinator(app, auth_client_coord):
    """Test 1: Valid QR scan by assigned coordinator marks attendance, awards +10 points, and returns student details."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        initial_points = student.student_profile.total_points
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })

    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'Attendance marked successfully' in data['message']
    assert data['data']['student_name'] == 'Test Student'
    assert data['data']['total_attendances'] == 1

    with app.app_context():
        att = Attendance.query.filter_by(event_id=event_id, user_id=student_id).first()
        assert att is not None
        assert att.status == 'PRESENT'
        assert att.ticket_id == ticket_id

        # Verify points awarded (+10)
        updated_student = User.query.get(student_id)
        assert updated_student.student_profile.total_points == initial_points + 10

def test_manual_ticket_code_entry(app, auth_client_coord):
    """Test 2: Manual ticket code entry works identically to camera QR scan."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': f"   {ticket_code}   ", # Extra whitespace
        'notes': 'Manual entry by gate coordinator'
    })

    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['notes'] == 'Manual entry by gate coordinator'

def test_duplicate_scan_prevention(app, auth_client_coord):
    """Test 3: Scanning the same QR code twice rejects with 'Already checked in' and does not create duplicate record."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

    # First scan: Success
    res1 = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res1.status_code == 200

    # Second scan: Rejected
    res2 = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res2.status_code == 400
    data2 = res2.get_json()
    assert data2['success'] is False
    assert 'Already checked in' in data2['error']['message']

    with app.app_context():
        att_count = Attendance.query.filter_by(event_id=event_id, user_id=student_id).count()
        assert att_count == 1

def test_ticket_for_different_event_rejected(app, auth_client_coord):
    """Test 4: Scanning a ticket issued for Event B at Event A's entrance is rejected with 'Ticket mismatch'."""
    with app.app_context():
        event1 = Event.query.first()
        event1_id = event1.id
        admin = User.query.filter_by(role='ADMIN').first()
        now = datetime.utcnow()

        event2 = Event(
            title='Second Event',
            description='Event 2 description',
            category_id=event1.category_id,
            venue_id=event1.venue_id,
            start_datetime=now + timedelta(days=3),
            end_datetime=now + timedelta(days=3, hours=2),
            registration_deadline=now + timedelta(days=2),
            status='REGISTRATION_OPEN',
            max_participants=30,
            created_by=admin.id
        )
        db.session.add(event2)
        db.session.flush()
        event2_id = event2.id

        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event2_id, student_id)

    # Coordinator at Event 1 scans Event 2's ticket
    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event1_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'Ticket mismatch' in data['error']['message']

    with app.app_context():
        assert Attendance.query.filter_by(event_id=event1_id, user_id=student_id).count() == 0

def test_invalid_ticket_code_rejected(app, auth_client_coord):
    """Test 5: Non-existent ticket code is rejected with 'Invalid ticket'."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': 'ITSA-TKT-FAKE-CODE-99999'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'Invalid ticket' in data['error']['message']

def test_cancelled_registration_rejected(app, auth_client_coord):
    """Test 6: Ticket belonging to a CANCELLED registration is rejected."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

        # Cancel the registration
        reg = EventRegistration.query.get(reg_id)
        reg.status = 'CANCELLED'
        db.session.commit()

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'cancelled' in data['error']['message'].lower()

    with app.app_context():
        assert Attendance.query.filter_by(event_id=event_id, user_id=student_id).count() == 0

def test_waitlisted_registration_rejected(app, auth_client_coord):
    """Test 7: Ticket belonging to a WAITLISTED registration is rejected."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

        # Set waitlisted
        reg = EventRegistration.query.get(reg_id)
        reg.status = 'WAITLISTED'
        db.session.commit()

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'waitlist' in data['error']['message'].lower()

def test_revoked_ticket_rejected(app, auth_client_coord):
    """Test 8: Revoked or invalidated ticket (is_valid=False) is rejected."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

        # Revoke ticket
        ticket = EventTicket.query.get(ticket_id)
        ticket.is_valid = False
        db.session.commit()

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'revoked' in data['error']['message'].lower() or 'invalid' in data['error']['message'].lower()

def test_cancelled_event_rejected(app, auth_client_coord):
    """Test 9: Attendance cannot be scanned for a cancelled event."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

        event.status = 'CANCELLED'
        db.session.commit()

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'cancelled' in data['error']['message'].lower()

def test_unassigned_coordinator_rejected(app):
    """Test 10: Coordinator who is not assigned to the event cannot scan tickets for it."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

        # Create unassigned coordinator
        other_coord = User(email='unassigned_coord@itsa.edu', full_name='Other Coord', role='COORDINATOR', is_active=True)
        other_coord.set_password('OtherCoord@123')
        db.session.add(other_coord)
        db.session.flush()
        cp = CoordinatorProfile(user_id=other_coord.id, employee_id='CR099', designation='Coordinator', department='IT')
        db.session.add(cp)
        db.session.commit()

    c = app.test_client()
    c.post('/api/v1/auth/login', json={'email': 'unassigned_coord@itsa.edu', 'password': 'OtherCoord@123'})

    res = c.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'Unauthorized' in data['error']['message']

    with app.app_context():
        assert Attendance.query.filter_by(event_id=event_id, user_id=student_id).count() == 0

def test_admin_can_scan_any_event(app, auth_client_admin):
    """Test 11: Admin has universal authority to scan attendance for any event."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

    res = auth_client_admin.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'Attendance marked successfully' in data['message']

def test_student_cannot_scan_attendance(app, auth_client_student):
    """Test 12: Students are strictly forbidden from scanning tickets (RBAC 403)."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

    res = auth_client_student.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert res.status_code == 403

def test_unauthenticated_cannot_scan_attendance(app, client):
    """Test 13: Guests cannot access scan API (401)."""
    res = client.post('/api/v1/attendance/scan', json={
        'event_id': 1,
        'ticket_code': 'ITSA-TKT-1234'
    })
    assert res.status_code == 401

def test_qr_code_with_url_wrapper_sanitization(app, auth_client_coord):
    """Test 14: QR codes embedded in full URLs or JSON are sanitized and processed properly."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

    # Scanned QR contains full URL
    wrapped_qr = f"https://itsa.edu/verify/ticket?code={ticket_code}&source=qr_camera"

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': wrapped_qr
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

    with app.app_context():
        att = Attendance.query.filter_by(event_id=event_id, user_id=student_id).first()
        assert att is not None
        assert att.ticket_id == ticket_id

def test_coordinator_scanner_page_access(app, auth_client_coord):
    """Test 15: Assigned coordinator accesses scanner page and sees live attendance counter."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id

    res = auth_client_coord.get(f'/coordinator/events/{event_id}/scan', follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'QR Check-in' in html
    assert 'attendanceCount' in html

def test_student_blocked_from_scanner_page(app, auth_client_student):
    """Test 16: Students are blocked from the coordinator scanner page."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id

    res = auth_client_student.get(f'/coordinator/events/{event_id}/scan', follow_redirects=False)
    assert res.status_code in (302, 403)

def test_lowercase_ticket_code_scan(app, auth_client_coord):
    """Test 17: Ticket codes provided in lowercase or mixed case are properly normalized and accepted."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        reg_id, ticket_id, ticket_code = setup_registration_and_ticket(app, event_id, student_id)

    res = auth_client_coord.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code.lower()
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'Attendance marked successfully' in data['message']

def test_coordinator_scanner_page_ui_elements(app, auth_client_coord):
    """Test 18: Scanner page includes offline vendor bundle, camera selection, and file scan fallback."""
    with app.app_context():
        event = Event.query.first()
        event_id = event.id

    res = auth_client_coord.get(f'/coordinator/events/{event_id}/scan', follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'vendor/js/html5-qrcode.min.js' in html
    assert 'cameraSelect' in html
    assert 'btnSwitchCamera' in html
    assert 'qrFileInput' in html
    assert 'btnStartScan' in html
    assert 'btnStopScan' in html
    assert 'scanResultAlert' in html

