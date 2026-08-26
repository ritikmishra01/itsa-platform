def test_get_events_list(client):
    res = client.get('/api/v1/events')
    assert res.status_code == 200
    assert len(res.get_json()['data']) >= 1

def test_create_event_coordinator(auth_client_coord):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    res = auth_client_coord.post('/api/v1/events', data={
        'title': 'New Coord Event',
        'description': 'Description here',
        'start_datetime': (now + timedelta(days=5)).isoformat(),
        'end_datetime': (now + timedelta(days=5, hours=2)).isoformat(),
        'registration_deadline': (now + timedelta(days=4)).isoformat(),
        'status': 'DRAFT'
    })
    assert res.status_code == 201

def test_student_cannot_create_event(auth_client_student):
    res = auth_client_student.post('/api/v1/events', json={'title': 'Hacked Event'})
    assert res.status_code == 403
