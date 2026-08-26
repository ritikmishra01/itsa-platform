import pytest
from app.models.event import Event
from app.models.user import User
from app.models.post import Post
from app.utils.file_utils import is_allowed_file
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

def test_registration_deadline_enforcement(client):
    # Student logs in
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    
    # Event with past deadline
    admin = User.query.filter_by(role='ADMIN').first()
    from app import db
    past_event = Event(
        title='Past Deadline Event',
        description='Event whose registration has passed',
        start_datetime=datetime.utcnow() + timedelta(days=1),
        end_datetime=datetime.utcnow() + timedelta(days=1, hours=2),
        registration_deadline=datetime.utcnow() - timedelta(days=1), # in past
        status='REGISTRATION_OPEN',
        created_by=admin.id
    )
    db.session.add(past_event)
    db.session.commit()

    reg_res = client.post(f'/api/v1/events/{past_event.id}/register')
    assert reg_res.status_code == 400
    assert 'deadline' in reg_res.get_json()['error']['message'].lower()

def test_file_upload_security():
    # Valid files
    assert is_allowed_file('poster.jpg', {'jpg', 'png', 'jpeg'}) is True
    assert is_allowed_file('avatar.png', {'jpg', 'png', 'jpeg'}) is True

    # Malicious extensions
    assert is_allowed_file('malicious.php', {'jpg', 'png', 'jpeg'}) is False
    assert is_allowed_file('exploit.exe', {'jpg', 'png', 'jpeg'}) is False
    assert is_allowed_file('script.sh', {'jpg', 'png', 'jpeg'}) is False
    assert is_allowed_file('.htaccess', {'jpg', 'png', 'jpeg'}) is False

    # Filename sanitization
    sanitized = secure_filename('../../etc/passwd.jpg')
    assert '/' not in sanitized and '..' not in sanitized
    assert sanitized.endswith('passwd.jpg')

def test_admin_content_moderation_flow(client):
    # Student creates post
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    post_res = client.post('/api/v1/posts', data={'content': 'Inappropriate text for audit test'})
    post_id = post_res.get_json()['data']['id']

    # Another student reports post
    report_res = client.post(f'/api/v1/posts/{post_id}/report', json={'reason': 'INAPPROPRIATE', 'description': 'Testing report'})
    assert report_res.status_code == 200

    # Admin reviews report
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})
    reports_res = client.get('/api/v1/admin/reports')
    assert reports_res.status_code == 200
    reports = reports_res.get_json()['data']
    assert len(reports) >= 1
    report_id = reports[0]['id']

    # Admin removes post
    resolve_res = client.post(f'/api/v1/admin/reports/{report_id}/resolve', json={'action': 'REMOVE_POST'})
    assert resolve_res.status_code == 200
    
    # Check post is now inactive
    from app import db
    post = db.session.get(Post, post_id)
    assert post.is_active is False
