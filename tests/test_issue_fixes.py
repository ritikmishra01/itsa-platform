import io
import pytest
from app.models.user import User, StudentProfile
from app.models.post import Post
from app.models.comment import Comment
from app.models.report import Report
from app.models.event import Event
from app.models.gallery import EventGallery
from app.models.notification import Notification

def test_1_student_logout_and_cache_protection(app):
    student_client = app.test_client()
    # 1. Student logs in
    login_res = student_client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    assert login_res.status_code == 200

    # 2. Access student dashboard & protected pages
    res_dash = student_client.get('/student/dashboard')
    assert res_dash.status_code == 200
    assert 'no-store' in res_dash.headers.get('Cache-Control', '')

    res_tickets = student_client.get('/student/tickets')
    assert res_tickets.status_code == 200

    # 3. Student logs out
    res_logout = student_client.get('/logout')
    assert res_logout.status_code == 302
    assert '/login' in res_logout.location

    # 4. Attempting to access protected student pages after logout must redirect to /login
    protected_urls = [
        '/dashboard',
        '/student/dashboard',
        '/profile',
        '/student/profile',
        '/my-tickets',
        '/student/tickets',
        '/my-attendance',
        '/student/attendance',
        '/my-certificates',
        '/student/certificates',
        '/notifications',
        '/student/notifications'
    ]
    for url in protected_urls:
        res = student_client.get(url)
        assert res.status_code == 302
        assert '/login' in res.location


def test_2_coordinator_logout_and_cache_protection(app):
    coord_client = app.test_client()
    # 1. Coordinator logs in
    login_res = coord_client.post('/api/v1/auth/login', json={'email': 'test_coord@itsa.edu', 'password': 'Coord@12345'})
    assert login_res.status_code == 200

    # 2. Access coordinator dashboard
    res_dash = coord_client.get('/coordinator/dashboard')
    assert res_dash.status_code == 200

    # 3. Coordinator logs out
    res_logout = coord_client.get('/logout')
    assert res_logout.status_code == 302
    assert '/login' in res_logout.location

    # 4. Protected coordinator pages must redirect to /login
    res_after = coord_client.get('/coordinator/dashboard')
    assert res_after.status_code == 302
    assert '/login' in res_after.location


def test_3_admin_logout_and_cache_protection(app):
    admin_client = app.test_client()
    # 1. Admin logs in
    login_res = admin_client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})
    assert login_res.status_code == 200

    # 2. Access admin dashboard & community
    res_dash = admin_client.get('/admin/dashboard')
    assert res_dash.status_code == 200
    assert 'no-store' in res_dash.headers.get('Cache-Control', '')

    res_comm = admin_client.get('/admin/community')
    assert res_comm.status_code == 200

    # 3. Admin logs out
    res_logout = admin_client.get('/logout')
    assert res_logout.status_code == 302
    assert '/login' in res_logout.location

    # 4. Protected admin pages must require login again
    res_after = admin_client.get('/admin/dashboard')
    assert res_after.status_code == 302
    assert '/login' in res_after.location


def test_4_admin_notifications_page_no_jinja_error(auth_client_admin, app):
    with app.app_context():
        admin = User.query.filter_by(role='ADMIN').first()
        student = User.query.filter_by(role='STUDENT').first()
        # Seed a test notification
        notif = Notification(
            user_id=student.id,
            type='ANNOUNCEMENT',
            title='Test Admin Notification',
            message='Testing Jinja rendering safety without user attribute mismatch'
        )
        from app.extensions import db
        db.session.add(notif)
        db.session.commit()

    # Admin Notifications view must load successfully with HTTP 200
    res = auth_client_admin.get('/admin/notifications')
    assert res.status_code == 200
    assert b'Test Admin Notification' in res.data
    assert b'Recipient:' in res.data


def test_5_and_6_broadcast_and_student_receives_broadcast(auth_client_admin, app):
    # Admin sends broadcast announcement to All Students
    payload = {
        'title': 'Hackathon Opening Ceremony Tomorrow',
        'message': 'Please report to the Main Auditorium at 9:00 AM sharp.',
        'audience': 'ALL_STUDENTS'
    }
    res = auth_client_admin.post('/api/v1/admin/notifications/broadcast', json=payload)
    assert res.status_code == 200
    assert res.get_json()['success'] is True
    assert res.get_json()['data']['sent_count'] >= 1

    # Verify notification record in database
    with app.app_context():
        student = User.query.filter_by(role='STUDENT').first()
        notif = Notification.query.filter_by(user_id=student.id, title='Hackathon Opening Ceremony Tomorrow').first()
        assert notif is not None
        assert notif.recipient.id == student.id
        assert notif.user.id == student.id

    # Student logs in and verifies notification appears in inbox
    student_client = app.test_client()
    student_client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    res_student_page = student_client.get('/student/notifications')
    assert res_student_page.status_code == 200
    assert b'Hackathon Opening Ceremony Tomorrow' in res_student_page.data

    res_student_api = student_client.get('/api/v1/notifications')
    assert res_student_api.status_code == 200
    notifs = res_student_api.get_json()['data']
    assert any(n['title'] == 'Hackathon Opening Ceremony Tomorrow' for n in notifs)


def test_7_coordinator_receives_broadcast(auth_client_admin, app):
    # Admin sends broadcast announcement to All Coordinators
    payload = {
        'title': 'Coordinators Briefing Meeting at 5 PM',
        'message': 'All event coordinators must attend the scanner sync meeting.',
        'audience': 'ALL_COORDINATORS'
    }
    res = auth_client_admin.post('/api/v1/admin/notifications/broadcast', json=payload)
    assert res.status_code == 200
    assert res.get_json()['success'] is True
    assert res.get_json()['data']['sent_count'] >= 1

    # Verify notification record in database for coordinator
    with app.app_context():
        coord = User.query.filter_by(role='COORDINATOR').first()
        notif = Notification.query.filter_by(user_id=coord.id, title='Coordinators Briefing Meeting at 5 PM').first()
        assert notif is not None
        assert notif.recipient.id == coord.id

    # Coordinator logs in and verifies notification is visible
    coord_client = app.test_client()
    coord_client.post('/api/v1/auth/login', json={'email': 'test_coord@itsa.edu', 'password': 'Coord@12345'})
    res_coord_page = coord_client.get('/coordinator/notifications')
    assert res_coord_page.status_code == 200
    assert b'Coordinators Briefing Meeting at 5 PM' in res_coord_page.data


def test_community_moderation_full_flow(auth_client_admin, app):
    with app.app_context():
        student = User.query.filter_by(role='STUDENT').first()
        admin = User.query.filter_by(role='ADMIN').first()

        post = Post(user_id=student.id, content='Community post for moderation audit', is_active=True)
        from app.extensions import db
        db.session.add(post)
        db.session.flush()

        comment = Comment(post_id=post.id, user_id=student.id, content='A test comment to moderate', is_active=True)
        db.session.add(comment)
        db.session.flush()

        report_post = Report(reporter_id=admin.id, reported_post_id=post.id, reason='SPAM', status='PENDING')
        report_comment = Report(reporter_id=admin.id, reported_comment_id=comment.id, reason='INAPPROPRIATE', status='PENDING')
        db.session.add_all([report_post, report_comment])
        db.session.commit()

        post_id = post.id
        comment_id = comment.id
        rep_p_id = report_post.id
        rep_c_id = report_comment.id

    res_page = auth_client_admin.get('/admin/community')
    assert res_page.status_code == 200

    res_mod_post = auth_client_admin.post(f'/api/v1/admin/reports/{rep_p_id}/resolve', json={'action': 'REMOVE_POST'})
    assert res_mod_post.status_code == 200

    with app.app_context():
        assert Post.query.get(post_id).is_active is False
        assert Report.query.get(rep_p_id).status == 'RESOLVED'

    res_mod_comm = auth_client_admin.post(f'/api/v1/admin/reports/{rep_c_id}/resolve', json={'action': 'REMOVE_COMMENT'})
    assert res_mod_comm.status_code == 200

    with app.app_context():
        assert Comment.query.get(comment_id).is_active is False

    res_toggle = auth_client_admin.post(f'/api/v1/admin/posts/{post_id}/toggle-active')
    assert res_toggle.status_code == 200
    with app.app_context():
        assert Post.query.get(post_id).is_active is True

    res_toggle_c = auth_client_admin.post(f'/api/v1/admin/comments/{comment_id}/toggle-active')
    assert res_toggle_c.status_code == 200
    with app.app_context():
        assert Comment.query.get(comment_id).is_active is True


def test_user_suspension_and_active_session_guard(auth_client_admin, app):
    with app.app_context():
        student = User.query.filter_by(role='STUDENT').first()
        student_id = student.id
        student_email = student.email

    suspend_res = auth_client_admin.post(f'/api/v1/admin/users/{student_id}/suspend', json={'reason': 'Violation of ITSA guidelines'})
    assert suspend_res.status_code == 200

    client = app.test_client()
    new_login_res = client.post('/api/v1/auth/login', json={'email': student_email, 'password': 'Student@12345'})
    assert new_login_res.status_code == 403
    assert "Your account has been suspended. Please contact ITSA administration." in new_login_res.get_json()['error']['message']

    unsuspend_res = auth_client_admin.post(f'/api/v1/admin/users/{student_id}/unsuspend')
    assert unsuspend_res.status_code == 200

    restored_login = client.post('/api/v1/auth/login', json={'email': student_email, 'password': 'Student@12345'})
    assert restored_login.status_code == 200


def test_media_gallery_upload_and_serving(auth_client_admin, app):
    with app.app_context():
        event = Event.query.first()
        event_id = event.id

    image_data = (io.BytesIO(b"fake_image_bytes_png"), 'test_keynote.png')
    data = {
        'event_id': str(event_id),
        'caption': 'Opening keynote and welcome address',
        'file': image_data,
        'is_featured': 'true'
    }
    res = auth_client_admin.post('/api/v1/admin/gallery/upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 201
    gallery_item = res.get_json()['data']
    file_path = gallery_item['file_path']
    gallery_id = gallery_item['id']

    res_img = auth_client_admin.get(f'/{file_path}')
    assert res_img.status_code == 200

    res_missing = auth_client_admin.get('/uploads/gallery/non_existent_file.png')
    assert res_missing.status_code == 200
    assert 'image/svg+xml' in res_missing.content_type

    res_del = auth_client_admin.post(f'/api/v1/admin/gallery/{gallery_id}')
    assert res_del.status_code == 200
