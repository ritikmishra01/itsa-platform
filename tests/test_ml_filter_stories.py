import io
from datetime import datetime, timedelta
import pytest
from app.extensions import db
from app.models.story import Story, StoryView
from app.models.user import User, StudentProfile
from app.models.event import Event
from app.ai.turnout_predictor import EventTurnoutPredictor


def test_ml_turnout_model_loading_and_prediction(app, auth_client_admin):
    """Verify ML predictor loads Scikit-learn model and produces realistic turnout forecasts."""
    with app.app_context():
        event = Event.query.first()
        assert event is not None

        predictor = EventTurnoutPredictor.get_instance()
        assert predictor.model is not None

        res = predictor.predict(event, historical_avg=30)
        assert 'predicted_registrations' in res
        assert 'predicted_count' in res
        assert 'factors_considered' in res
        assert 'confidence' in res
        assert isinstance(res['predicted_registrations'], int)
        assert res['predicted_registrations'] > 0
        assert len(res['factors_considered']) > 0

    # Test via HTTP endpoint
    resp = auth_client_admin.get(f'/api/v1/ai/predict-registrations/{event.id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'predicted_registrations' in data['data']
    assert data['data']['predicted_registrations'] > 0
    assert 'factors_considered' in data['data']


def test_admin_events_filter(app, auth_client_admin):
    """Verify admin events filter by category, status, search keyword."""
    with app.app_context():
        event = Event.query.first()
        cat_id = event.category_id

    # Filter by category
    resp = auth_client_admin.get(f'/admin/events?category_id={cat_id}')
    assert resp.status_code == 200
    assert b'Test AI Workshop' in resp.data

    # Filter by non-existent category
    resp = auth_client_admin.get('/admin/events?category_id=9999')
    assert resp.status_code == 200
    assert b'No matching events found' in resp.data

    # Filter by status
    resp = auth_client_admin.get('/admin/events?status=REGISTRATION_OPEN')
    assert resp.status_code == 200
    assert b'Test AI Workshop' in resp.data

    # Filter by search keyword
    resp = auth_client_admin.get('/admin/events?search=Workshop')
    assert resp.status_code == 200
    assert b'Test AI Workshop' in resp.data


def test_admin_users_filter(app, auth_client_admin):
    """Verify admin users filter by role, department, and search text."""
    # Search by name
    resp = auth_client_admin.get('/admin/users?search=Student')
    assert resp.status_code == 200
    assert b'test_student@itsa.edu' in resp.data

    # Filter by department
    resp = auth_client_admin.get('/admin/users?department=Computer+Science')
    assert resp.status_code == 200
    assert b'Test Student' in resp.data

    # Filter by role
    resp = auth_client_admin.get('/admin/users?role=COORDINATOR')
    assert resp.status_code == 200
    assert b'Test Coord' in resp.data


def test_admin_registrations_and_attendance_filter(app, auth_client_admin):
    """Verify admin registrations and attendance filter routes accept parameters."""
    with app.app_context():
        event = Event.query.first()

    resp_reg = auth_client_admin.get(f'/admin/registrations?event_id={event.id}&status=CONFIRMED')
    assert resp_reg.status_code == 200

    resp_att = auth_client_admin.get(f'/admin/attendance?event_id={event.id}')
    assert resp_att.status_code == 200


def test_community_route_alias(app, auth_client_student):
    """Verify /community is an accessible alias for the community social feed."""
    resp = auth_client_student.get('/community')
    assert resp.status_code == 200
    assert b'storiesTrayList' in resp.data
    assert b'storyViewerModal' in resp.data


def test_story_creation_and_expiration(app, auth_client_student):
    """Verify creating a text story with 24-hour expiration."""
    resp = auth_client_student.post('/api/v1/stories', data={
        'text_content': 'Excited for the upcoming Hackathon!',
        'caption': 'Join our team #code',
        'background_style': 'linear-gradient(135deg, #10b981, #06b6d4)'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True
    story_data = data['data']
    assert story_data['media_type'] == 'TEXT'
    assert story_data['text_content'] == 'Excited for the upcoming Hackathon!'
    assert story_data['caption'] == 'Join our team #code'

    with app.app_context():
        story = Story.query.get(story_data['id'])
        assert story is not None
        # Verify 24-hour expiration window
        expected_expiry = story.created_at + timedelta(hours=24)
        assert abs((story.expires_at - expected_expiry).total_seconds()) < 5
        assert not story.is_expired


def test_story_image_creation(app, auth_client_student):
    """Verify uploading an image story."""
    mock_img = (io.BytesIO(b'fake-image-bytes'), 'story_pic.jpg')
    resp = auth_client_student.post(
        '/api/v1/stories',
        data={'media_file': mock_img, 'caption': 'Campus morning vibes'},
        content_type='multipart/form-data'
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True
    assert data['data']['media_type'] == 'IMAGE'
    assert 'uploads/stories' in data['data']['media_url']


def test_story_views_and_viewer_privacy(app, client):
    """Verify view tracking and privacy control for viewers list."""
    # 1. Login as Student A and post a story
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    resp_create = client.post('/api/v1/stories', data={
        'text_content': 'Hello ITSA Community!'
    })
    assert resp_create.status_code == 201
    story_id = resp_create.get_json()['data']['id']

    # 2. Create another student user (Student B)
    with app.app_context():
        user_b = User(email='student_b@itsa.edu', full_name='Student B', role='STUDENT', is_active=True)
        user_b.set_password('Pass@12345')
        db.session.add(user_b)
        db.session.commit()
        b_id = user_b.id

    # 3. Login as Student B
    client.post('/api/v1/auth/login', json={'email': 'student_b@itsa.edu', 'password': 'Pass@12345'})

    # Student B checks stories feed
    feed_resp = client.get('/api/v1/stories')
    assert feed_resp.status_code == 200
    feed_data = feed_resp.get_json()['data']
    # Student A's group should have has_unseen == True for Student B
    author_group = next(g for g in feed_data['user_groups'] if not g['is_own'])
    assert author_group['has_unseen'] is True

    # 4. Student B views the story
    view_resp = client.post(f'/api/v1/stories/{story_id}/view')
    assert view_resp.status_code == 200
    assert view_resp.get_json()['data']['view_count'] == 1

    # Idempotent view call (viewing again should not double count)
    view_resp_again = client.post(f'/api/v1/stories/{story_id}/view')
    assert view_resp_again.status_code == 200
    assert view_resp_again.get_json()['data']['view_count'] == 1

    # 5. Privacy control check: Student B (not author, not admin) -> must get 403 Forbidden!
    forbidden_resp = client.get(f'/api/v1/stories/{story_id}/viewers')
    assert forbidden_resp.status_code == 403

    # 6. Login back as Student A (Author) -> gets 200 OK with viewer details
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    author_viewers_resp = client.get(f'/api/v1/stories/{story_id}/viewers')
    assert author_viewers_resp.status_code == 200
    viewers_data = author_viewers_resp.get_json()['data']
    assert viewers_data['total_views'] == 1
    assert viewers_data['viewers'][0]['user_id'] == b_id

    # 7. Login as Admin -> also gets 200 OK
    client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})
    admin_viewers_resp = client.get(f'/api/v1/stories/{story_id}/viewers')
    assert admin_viewers_resp.status_code == 200


def test_story_deletion_permissions(app, client):
    """Verify that only the story author or admin can delete a story."""
    # 1. Login as Student A and create story
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    resp = client.post('/api/v1/stories', data={'text_content': 'Temporary story'})
    assert resp.status_code == 201
    story_id = resp.get_json()['data']['id']

    # 2. Create another user (Student C)
    with app.app_context():
        user_c = User(email='student_c@itsa.edu', full_name='Student C', role='STUDENT', is_active=True)
        user_c.set_password('Pass@12345')
        db.session.add(user_c)
        db.session.commit()

    # 3. Login as Student C -> cannot delete it (403 Forbidden)
    client.post('/api/v1/auth/login', json={'email': 'student_c@itsa.edu', 'password': 'Pass@12345'})
    resp_del_unauth = client.delete(f'/api/v1/stories/{story_id}')
    assert resp_del_unauth.status_code == 403

    # 4. Login back as Student A (Author) -> can delete it (200 OK)
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    resp_del_author = client.delete(f'/api/v1/stories/{story_id}')
    assert resp_del_author.status_code == 200
    assert resp_del_author.get_json()['success'] is True

    # Confirm it is no longer in active stories
    feed_resp = client.get('/api/v1/stories')
    all_story_ids = [
        s['id']
        for g in feed_resp.get_json()['data']['user_groups']
        for s in g['stories']
    ]
    assert story_id not in all_story_ids


def test_expired_stories_filtered_out(app, auth_client_student):
    """Verify that expired stories (>24h old) are automatically omitted from feed."""
    with app.app_context():
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        expired_story = Story(
            user_id=student.id,
            media_type='TEXT',
            text_content='Old story from yesterday',
            created_at=datetime.utcnow() - timedelta(hours=25),
            expires_at=datetime.utcnow() - timedelta(hours=1),
            is_active=True
        )
        db.session.add(expired_story)
        db.session.commit()
        expired_id = expired_story.id

    resp = auth_client_student.get('/api/v1/stories')
    assert resp.status_code == 200
    all_story_ids = [
        s['id']
        for g in resp.get_json()['data']['user_groups']
        for s in g['stories']
    ]
    assert expired_id not in all_story_ids
