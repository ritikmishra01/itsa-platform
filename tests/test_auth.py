def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'

def test_student_registration(client):
    res = client.post('/api/v1/auth/register', json={
        'email': 'new_student@itsa.edu',
        'password': 'Password@123',
        'full_name': 'New Student',
        'student_id': 'ST2026999',
        'department': 'Information Technology',
        'year_of_study': 2
    })
    assert res.status_code == 201
    assert res.get_json()['success'] is True

def test_login_success(client):
    res = client.post('/api/v1/auth/login', json={
        'email': 'test_student@itsa.edu',
        'password': 'Student@12345'
    })
    assert res.status_code == 200
    assert res.get_json()['data']['email'] == 'test_student@itsa.edu'

def test_login_wrong_password(client):
    res = client.post('/api/v1/auth/login', json={
        'email': 'test_student@itsa.edu',
        'password': 'WrongPassword123'
    })
    assert res.status_code == 401
