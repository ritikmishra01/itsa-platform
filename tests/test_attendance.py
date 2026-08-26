from app.models.event import Event

def test_full_registration_and_coordinator_qr_attendance_flow(client):
    # 1. Login as student
    login_st = client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    assert login_st.status_code == 200

    # Get event ID
    event = Event.query.first()
    event_id = event.id

    # 2. Student registers for event
    reg_res = client.post(f'/api/v1/events/{event_id}/register')
    assert reg_res.status_code == 201
    ticket_code = reg_res.get_json()['data']['ticket']['ticket_code']
    assert ticket_code.startswith('ITSA-TKT-')

    # 3. Student cannot mark their own attendance (student is not a coordinator)
    student_scan = client.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert student_scan.status_code == 403 # Only coordinator or admin can scan

    # 4. Login as Coordinator
    client.post('/api/v1/auth/logout')
    login_coord = client.post('/api/v1/auth/login', json={'email': 'test_coord@itsa.edu', 'password': 'Coord@12345'})
    assert login_coord.status_code == 200

    # 5. Coordinator scans the student's QR code
    coord_scan = client.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert coord_scan.status_code == 200
    assert coord_scan.get_json()['data']['status'] == 'PRESENT'

    # 6. Duplicate scan attempt is rejected
    dup_scan = client.post('/api/v1/attendance/scan', json={
        'event_id': event_id,
        'ticket_code': ticket_code
    })
    assert dup_scan.status_code == 400
