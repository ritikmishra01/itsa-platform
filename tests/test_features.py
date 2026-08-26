from app.models.event import Event
from app.models.user import User
from app.models.attendance import Attendance
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket

def test_certificate_public_verification(client):
    event = Event.query.first()
    # Student registers
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    reg_res = client.post(f'/api/v1/events/{event.id}/register')
    ticket_code = reg_res.get_json()['data']['ticket']['ticket_code']

    # Coordinator scans attendance
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_coord@itsa.edu', 'password': 'Coord@12345'})
    att_res = client.post('/api/v1/attendance/scan', json={'event_id': event.id, 'ticket_code': ticket_code})
    assert att_res.status_code == 200

    # Student checks certificate
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    certs_res = client.get('/api/v1/certificates/my')
    assert certs_res.status_code == 200
    certs = certs_res.get_json()['data']
    assert len(certs) >= 1
    cert_code = certs[0]['certificate_code']

    # Public unauthenticated verification
    client.post('/api/v1/auth/logout')
    verify_res = client.get(f'/api/v1/certificates/verify/{cert_code}')
    assert verify_res.status_code == 200
    assert verify_res.get_json()['data']['valid'] is True
    assert verify_res.get_json()['data']['student_name'] == 'Test Student'

def test_feedback_submission_and_points(client):
    event = Event.query.first()
    # 1. Student registers
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    reg_res = client.post(f'/api/v1/events/{event.id}/register')
    ticket_code = reg_res.get_json()['data']['ticket']['ticket_code']

    # 2. Coordinator scans attendance
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_coord@itsa.edu', 'password': 'Coord@12345'})
    client.post('/api/v1/attendance/scan', json={'event_id': event.id, 'ticket_code': ticket_code})

    # 3. Student submits feedback
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    fb_res = client.post('/api/v1/feedback', json={
        'event_id': event.id,
        'rating': 5,
        'content': 'Great workshop!'
    })
    assert fb_res.status_code == 201

    # Check points increased
    points_res = client.get('/api/v1/points/my')
    assert points_res.status_code == 200
    assert points_res.get_json()['data']['total_points'] >= 15 # +3 reg, +10 att, +5 fb

def test_admin_suspend_user(client):
    student = User.query.filter_by(role='STUDENT').first()
    # Admin logs in
    client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})
    sus_res = client.post(f'/api/v1/admin/users/{student.id}/suspend', json={'reason': 'Violation'})
    assert sus_res.status_code == 200
    assert sus_res.get_json()['data']['is_suspended'] is True

    # Suspended student cannot log in
    client.post('/api/v1/auth/logout')
    login_res = client.post('/api/v1/auth/login', json={'email': student.email, 'password': 'Student@12345'})
    assert login_res.status_code == 403
    assert "Your account has been suspended" in login_res.get_json()['error']['message']
