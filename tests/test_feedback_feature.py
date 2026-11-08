import pytest
from datetime import datetime, timedelta
from app import db
from app.models.user import User, StudentProfile
from app.models.event import Event, EventCategory, Venue, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.models.feedback import Feedback

def setup_completed_event_with_attendance(app):
    """Helper to create a completed event and mark student attendance."""
    with app.app_context():
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        admin = User.query.filter_by(email='test_admin@itsa.edu').first()
        cat = EventCategory.query.first()
        venue = Venue.query.first()

        completed_event = Event(
            title='Completed Python Bootcamp',
            description='A deep dive into Python',
            category_id=cat.id,
            venue_id=venue.id,
            start_datetime=datetime.utcnow() - timedelta(days=2),
            end_datetime=datetime.utcnow() - timedelta(days=2, hours=-3),
            registration_deadline=datetime.utcnow() - timedelta(days=3),
            status='COMPLETED',
            max_participants=50,
            created_by=admin.id
        )
        db.session.add(completed_event)
        db.session.flush()

        reg = EventRegistration(
            event_id=completed_event.id,
            user_id=student.id,
            registration_number=f"REG-COMP-{completed_event.id}-{student.id}",
            status='CONFIRMED'
        )
        db.session.add(reg)
        db.session.flush()

        ticket = EventTicket(
            registration_id=reg.id,
            ticket_code=f"ITSA-TKT-{completed_event.id}-{student.id}",
            is_valid=True
        )
        db.session.add(ticket)
        db.session.flush()

        att = Attendance(
            event_id=completed_event.id,
            user_id=student.id,
            registration_id=reg.id,
            ticket_id=ticket.id,
            scanned_by=admin.id,
            status='PRESENT'
        )
        db.session.add(att)
        db.session.commit()
        return completed_event.id, student.id


def test_scenario_1_attended_and_completed_allows_feedback(app, auth_client_student):
    """Scenario 1: Attended and completed event allows feedback submission (201)."""
    event_id, student_id = setup_completed_event_with_attendance(app)

    with app.app_context():
        sp_before = StudentProfile.query.filter_by(user_id=student_id).first()
        initial_points = sp_before.total_points

    res = auth_client_student.post('/api/v1/feedback', json={
        'event_id': event_id,
        'rating': 5,
        'speaker_rating': 5,
        'organization_rating': 4,
        'content_rating': 5,
        'content': 'Outstanding session, learned a lot!',
        'suggestions': 'Keep up the good work.'
    })

    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['rating'] == 5
    assert data['data']['content_rating'] == 5

    # Check gamification points awarded (+5)
    with app.app_context():
        sp_after = StudentProfile.query.filter_by(user_id=student_id).first()
        assert sp_after.total_points == initial_points + 5


def test_scenario_2_upcoming_event_rejects_feedback(app, auth_client_student):
    """Scenario 2: Upcoming or non-completed event disallows feedback (400)."""
    with app.app_context():
        upcoming_event = Event.query.filter_by(title='Test AI Workshop').first()
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        admin = User.query.filter_by(email='test_admin@itsa.edu').first()

        reg = EventRegistration(
            event_id=upcoming_event.id,
            user_id=student.id,
            registration_number=f"REG-UP-{upcoming_event.id}-{student.id}",
            status='CONFIRMED'
        )
        db.session.add(reg)
        db.session.flush()

        ticket = EventTicket(
            registration_id=reg.id,
            ticket_code=f"ITSA-TKT-UP-{upcoming_event.id}-{student.id}",
            is_valid=True
        )
        db.session.add(ticket)
        db.session.flush()

        att = Attendance(
            event_id=upcoming_event.id,
            user_id=student.id,
            registration_id=reg.id,
            ticket_id=ticket.id,
            scanned_by=admin.id,
            status='PRESENT'
        )
        db.session.add(att)
        db.session.commit()
        ev_id = upcoming_event.id

    res = auth_client_student.post('/api/v1/feedback', json={
        'event_id': ev_id,
        'rating': 5,
        'content': 'Loved it!'
    })

    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert "completed events" in data['error']['message'].lower()


def test_scenario_3_non_attended_event_rejects_feedback(app, auth_client_student):
    """Scenario 3: Non-attended completed event disallows feedback (400)."""
    with app.app_context():
        admin = User.query.filter_by(email='test_admin@itsa.edu').first()
        cat = EventCategory.query.first()
        venue = Venue.query.first()

        completed_unattended = Event(
            title='Unattended Completed Seminar',
            description='Seminar description',
            category_id=cat.id,
            venue_id=venue.id,
            start_datetime=datetime.utcnow() - timedelta(days=5),
            end_datetime=datetime.utcnow() - timedelta(days=5, hours=-2),
            registration_deadline=datetime.utcnow() - timedelta(days=6),
            status='COMPLETED',
            created_by=admin.id
        )
        db.session.add(completed_unattended)
        db.session.commit()
        ev_id = completed_unattended.id

    res = auth_client_student.post('/api/v1/feedback', json={
        'event_id': ev_id,
        'rating': 4,
        'content': 'I was not there.'
    })

    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert "attended" in data['error']['message'].lower()


def test_scenario_4_duplicate_submission_updates_without_duplicate_points(app, auth_client_student):
    """Scenario 4: Re-submitting feedback updates record (200) without awarding extra points."""
    event_id, student_id = setup_completed_event_with_attendance(app)

    # Initial submission
    res1 = auth_client_student.post('/api/v1/feedback', json={
        'event_id': event_id,
        'rating': 4,
        'content': 'Initial feedback'
    })
    assert res1.status_code == 201

    with app.app_context():
        sp = StudentProfile.query.filter_by(user_id=student_id).first()
        points_after_first = sp.total_points

    # Second submission (Edit / Update)
    res2 = auth_client_student.post('/api/v1/feedback', json={
        'event_id': event_id,
        'rating': 5,
        'content': 'Updated feedback after reflection'
    })
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2['success'] is True
    assert data2['data']['rating'] == 5
    assert data2['data']['content'] == 'Updated feedback after reflection'

    # Check that points did not increase again
    with app.app_context():
        sp_again = StudentProfile.query.filter_by(user_id=student_id).first()
        assert sp_again.total_points == points_after_first

        # Ensure database record count is still 1 (no duplicates)
        count = Feedback.query.filter_by(event_id=event_id, user_id=student_id).count()
        assert count == 1


def test_scenario_5_coordinator_and_admin_view_permissions(app):
    """Scenario 5: Admin and assigned coordinator can view feedback; unassigned coordinator is rejected."""
    event_id, _ = setup_completed_event_with_attendance(app)

    # 1. Login as Student and submit feedback
    client = app.test_client()
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    res_sub = client.post('/api/v1/feedback', json={
        'event_id': event_id,
        'rating': 5,
        'content': 'Superb workshop!'
    })
    assert res_sub.status_code == 201

    # 2. Login as Admin
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})

    # Admin access via API
    res_admin = client.get(f'/api/v1/feedback/event/{event_id}')
    assert res_admin.status_code == 200
    data_admin = res_admin.get_json()
    assert len(data_admin['data']['feedbacks']) == 1
    assert data_admin['data']['metrics']['avg_rating'] == 5.0

    # Admin access via Page
    res_admin_page = client.get('/admin/feedback')
    assert res_admin_page.status_code == 200
    assert b"Student Feedback Center" in res_admin_page.data

    # 3. Login as Coordinator (unassigned)
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_coord@itsa.edu', 'password': 'Coord@12345'})

    # Unassigned coordinator tries to access API -> 403
    res_coord_unassigned = client.get(f'/api/v1/feedback/event/{event_id}')
    assert res_coord_unassigned.status_code == 403

    # Now assign coordinator to this event
    with app.app_context():
        coord = User.query.filter_by(email='test_coord@itsa.edu').first()
        admin = User.query.filter_by(email='test_admin@itsa.edu').first()
        ec = EventCoordinator(event_id=event_id, coordinator_id=coord.id, assigned_by=admin.id)
        db.session.add(ec)
        db.session.commit()

    # Assigned coordinator tries again -> 200
    res_coord_assigned = client.get(f'/api/v1/feedback/event/{event_id}')
    assert res_coord_assigned.status_code == 200
    data_coord = res_coord_assigned.get_json()
    assert len(data_coord['data']['feedbacks']) == 1

    # Coordinator feedback page
    res_coord_page = client.get(f'/coordinator/events/{event_id}/feedback')
    assert res_coord_page.status_code == 200
    assert b"Superb workshop!" in res_coord_page.data


def test_scenario_6_student_cannot_access_admin_or_coordinator_feedback(app, auth_client_student):
    """Scenario 6: Student role cannot access admin feedback or coordinator feedback views."""
    event_id, _ = setup_completed_event_with_attendance(app)

    # Student accessing admin feedback HTML page -> redirected (302)
    res_admin_page = auth_client_student.get('/admin/feedback')
    assert res_admin_page.status_code == 302

    # Student accessing coordinator event feedback HTML page -> redirected (302)
    res_coord_page = auth_client_student.get(f'/coordinator/events/{event_id}/feedback')
    assert res_coord_page.status_code == 302

    # Student accessing coordinator feedback API -> 403
    res_api = auth_client_student.get(f'/api/v1/feedback/event/{event_id}')
    assert res_api.status_code == 403


def test_scenario_7_feedback_persistence_and_retrieval(app, auth_client_student):
    """Scenario 7: Feedback persists and is retrievable via /api/v1/feedback/my/<id>."""
    event_id, student_id = setup_completed_event_with_attendance(app)

    # Check before submission
    res_before = auth_client_student.get(f'/api/v1/feedback/my/{event_id}')
    assert res_before.status_code == 200
    assert res_before.get_json()['data']['submitted'] is False

    # Submit feedback
    auth_client_student.post('/api/v1/feedback', json={
        'event_id': event_id,
        'rating': 4,
        'speaker_rating': 5,
        'organization_rating': 4,
        'content_rating': 4,
        'content': 'Great insights into ML pipelines.',
        'suggestions': 'Add more hands-on exercises.'
    })

    # Check after submission
    res_after = auth_client_student.get(f'/api/v1/feedback/my/{event_id}')
    assert res_after.status_code == 200
    data = res_after.get_json()['data']
    assert data['submitted'] is True
    assert data['feedback']['rating'] == 4
    assert data['feedback']['content'] == 'Great insights into ML pipelines.'
    assert data['feedback']['suggestions'] == 'Add more hands-on exercises.'

    # Event detail page renders submitted state
    res_detail = auth_client_student.get(f'/events/{event_id}')
    assert res_detail.status_code == 200
    assert b"Your Feedback is Recorded" in res_detail.data
    assert b"Great insights into ML pipelines." in res_detail.data


def test_feedback_validation_limits(app, auth_client_student):
    """Validation test: Rating must be 1-5 and comments cannot exceed 1000 chars."""
    event_id, _ = setup_completed_event_with_attendance(app)

    # Invalid rating > 5
    res_high = auth_client_student.post('/api/v1/feedback', json={'event_id': event_id, 'rating': 6})
    assert res_high.status_code == 400

    # Invalid rating < 1
    res_low = auth_client_student.post('/api/v1/feedback', json={'event_id': event_id, 'rating': 0})
    assert res_low.status_code == 400

    # Comment over 1000 chars
    long_comment = "A" * 1001
    res_long = auth_client_student.post('/api/v1/feedback', json={
        'event_id': event_id,
        'rating': 5,
        'content': long_comment
    })
    assert res_long.status_code == 400
    assert "1000 characters" in res_long.get_json()['error']['message']


def test_admin_feedback_csv_export(app):
    """Admin CSV export includes feedback report type."""
    event_id, _ = setup_completed_event_with_attendance(app)

    client = app.test_client()
    client.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    client.post('/api/v1/feedback', json={
        'event_id': event_id,
        'rating': 5,
        'content': 'Export test comment'
    })

    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})

    res = client.get('/api/v1/admin/reports/export/feedback')
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    assert b"Export test comment" in res.data
    assert b"Overall Rating" in res.data
