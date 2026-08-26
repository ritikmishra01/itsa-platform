import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from app import create_app, db
from app.models.user import User, StudentProfile, CoordinatorProfile
from app.models.event import EventCategory, Venue, Event, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()

        # Seed essential test fixtures
        admin = User(email='test_admin@itsa.edu', full_name='Test Admin', role='ADMIN', is_active=True)
        admin.set_password('Admin@12345')

        coord = User(email='test_coord@itsa.edu', full_name='Test Coord', role='COORDINATOR', is_active=True)
        coord.set_password('Coord@12345')

        student = User(email='test_student@itsa.edu', full_name='Test Student', role='STUDENT', is_active=True)
        student.set_password('Student@12345')

        db.session.add_all([admin, coord, student])
        db.session.flush()

        sp = StudentProfile(user_id=student.id, student_id='ST2026001', department='Computer Science', year_of_study=3, total_points=10)
        cp = CoordinatorProfile(user_id=coord.id, employee_id='CR001', designation='Coordinator', department='IT')
        cat = EventCategory(name='Technical', description='Tech events')
        venue = Venue(name='Hall A', capacity=100)
        db.session.add_all([sp, cp, cat, venue])
        db.session.flush()

        now = datetime.utcnow()
        event = Event(
            title='Test AI Workshop',
            description='Test event description',
            category_id=cat.id,
            venue_id=venue.id,
            start_datetime=now + timedelta(days=2),
            end_datetime=now + timedelta(days=2, hours=3),
            registration_deadline=now + timedelta(days=1),
            status='REGISTRATION_OPEN',
            max_participants=50,
            created_by=admin.id
        )
        db.session.add(event)
        db.session.flush()

        ec = EventCoordinator(event_id=event.id, coordinator_id=coord.id, assigned_by=admin.id)
        db.session.add(ec)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client_student(app):
    c = app.test_client()
    c.post('/api/v1/auth/login', json={'email': 'test_student@itsa.edu', 'password': 'Student@12345'})
    return c

@pytest.fixture
def auth_client_coord(app):
    c = app.test_client()
    c.post('/api/v1/auth/login', json={'email': 'test_coord@itsa.edu', 'password': 'Coord@12345'})
    return c

@pytest.fixture
def auth_client_admin(app):
    c = app.test_client()
    c.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})
    return c
