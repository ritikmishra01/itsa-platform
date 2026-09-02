import os
import sys
from datetime import datetime, timedelta

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models.user import User, CoordinatorProfile
from app.models.event import EventCategory, Venue, Event, EventCoordinator

def seed_demo_data(app=None):
    """
    Idempotently seeds 5 demo coordinators and 5 realistic ITSA events.
    Safe to run repeatedly without creating duplicates.
    """
    env = os.environ.get('FLASK_ENV', 'production')
    if app is None:
        app = create_app(env)

    with app.app_context():
        print("[*] Seeding demo coordinators and events...")
        db.create_all()

        # 1. Ensure Admin exists for created_by / assigned_by foreign keys
        admin = User.query.filter_by(role='ADMIN').first()
        if not admin:
            admin = User.query.filter_by(email='admin@itsa.edu').first()
        if not admin:
            admin = User(
                email='admin@itsa.edu',
                full_name='ITSA Administrator',
                role='ADMIN',
                is_active=True,
                is_suspended=False
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'Admin#2026'))
            db.session.add(admin)
            db.session.commit()

        # 2. Ensure Categories exist
        categories_def = {
            "Technical": ("Hackathons, coding contests, and developer challenges", "bi-code-slash"),
            "Competition": ("Quizzes, project expos, and debates", "bi-award"),
            "Workshop": ("Hands-on engineering workshops and bootcamps", "bi-tools"),
            "Seminar": ("Guest lectures by tech industry experts", "bi-mic"),
        }
        category_objs = {}
        for cat_name, (cat_desc, cat_icon) in categories_def.items():
            cat = EventCategory.query.filter_by(name=cat_name).first()
            if not cat:
                cat = EventCategory(name=cat_name, description=cat_desc, icon=cat_icon)
                db.session.add(cat)
                db.session.flush()
            category_objs[cat_name] = cat

        # 3. Ensure Venues exist
        venue = Venue.query.filter_by(name="Main University Auditorium").first()
        if not venue:
            venue = Venue(
                name="Main University Auditorium",
                address="Central University Campus, Block A",
                capacity=500,
                room_number="Aud-1",
                building="Main Block"
            )
            db.session.add(venue)
            db.session.flush()

        lab_venue = Venue.query.filter_by(name="Advanced Computing Laboratory").first()
        if not lab_venue:
            lab_venue = Venue(
                name="Advanced Computing Laboratory",
                address="IT Department, 2nd Floor",
                capacity=120,
                room_number="Lab-204",
                building="IT Wing"
            )
            db.session.add(lab_venue)
            db.session.flush()

        db.session.commit()

        # 4. Exactly 5 Coordinators (Unique, Active, Real-world College Faculty/Mentors)
        default_coord_password = os.environ.get('COORDINATOR_PASSWORD', 'Coord#2026')
        coordinators_data = [
            {
                "name": "Prof. Rajesh Kulkarni",
                "email": "coord1@itsa.edu",
                "employee_id": "ITSA-FAC-01",
                "designation": "Assistant Professor & Faculty Coordinator",
                "department": "Information Technology",
                "phone": "+91 9820123401"
            },
            {
                "name": "Dr. Sunita Patil",
                "email": "coord2@itsa.edu",
                "employee_id": "ITSA-FAC-02",
                "designation": "Associate Professor & Technical Head",
                "department": "Computer Science",
                "phone": "+91 9820123402"
            },
            {
                "name": "Prof. Amit Deshmukh",
                "email": "coord3@itsa.edu",
                "employee_id": "ITSA-FAC-03",
                "designation": "Assistant Professor & Coding Club Lead",
                "department": "Artificial Intelligence & DS",
                "phone": "+91 9820123403"
            },
            {
                "name": "Dr. Neha Sharma",
                "email": "coord4@itsa.edu",
                "employee_id": "ITSA-FAC-04",
                "designation": "Assistant Professor & Workshop Convener",
                "department": "Information Technology",
                "phone": "+91 9820123404"
            },
            {
                "name": "Prof. Vikram Joshi",
                "email": "coord5@itsa.edu",
                "employee_id": "ITSA-FAC-05",
                "designation": "Lecturer & Student Outreach Coordinator",
                "department": "Electronics & Telecom",
                "phone": "+91 9820123405"
            }
        ]

        coord_user_map = {}
        for c_data in coordinators_data:
            user = User.query.filter_by(email=c_data["email"]).first()
            if not user:
                user = User(
                    email=c_data["email"],
                    full_name=c_data["name"],
                    role='COORDINATOR',
                    is_active=True,
                    is_suspended=False
                )
                user.set_password(default_coord_password)
                db.session.add(user)
                db.session.flush()

                profile = CoordinatorProfile(
                    user_id=user.id,
                    employee_id=c_data["employee_id"],
                    designation=c_data["designation"],
                    department=c_data["department"],
                    phone=c_data["phone"]
                )
                db.session.add(profile)
                print(f"[+] Coordinator created: {c_data['name']} ({c_data['email']})")
            else:
                user.role = 'COORDINATOR'
                user.is_active = True
                user.is_suspended = False
                if not user.coordinator_profile:
                    profile = CoordinatorProfile(
                        user_id=user.id,
                        employee_id=c_data["employee_id"],
                        designation=c_data["designation"],
                        department=c_data["department"],
                        phone=c_data["phone"]
                    )
                    db.session.add(profile)
            coord_user_map[c_data["email"]] = user

        db.session.commit()

        # 5. Exactly 5 Realistic ITSA Events (Future Dates, Open Registration)
        base_time = datetime.utcnow()
        events_data = [
            {
                "title": "TechFest 2026",
                "category": "Technical",
                "description": "Annual ITSA technical festival featuring coding, technology exhibits, hackathons and innovation activities across departments.",
                "days_ahead": 14,
                "duration_hours": 8,
                "venue_id": venue.id,
                "max_participants": 300,
                "tags": "techfest,hackathon,innovation,coding",
                "coord_email": "coord1@itsa.edu"
            },
            {
                "title": "CodeSprint 2026",
                "category": "Competition",
                "description": "Competitive programming and problem-solving hackathon for students testing algorithmic agility and software problem-solving skills.",
                "days_ahead": 18,
                "duration_hours": 5,
                "venue_id": lab_venue.id,
                "max_participants": 120,
                "tags": "competitive-programming,algorithms,codesprint,challenges",
                "coord_email": "coord2@itsa.edu"
            },
            {
                "title": "AI & Future Technologies Workshop",
                "category": "Workshop",
                "description": "Hands-on engineering workshop exploring Large Language Models, Agentic Workflows, Neural Networks, and practical Generative AI implementations.",
                "days_ahead": 21,
                "duration_hours": 6,
                "venue_id": venue.id,
                "max_participants": 150,
                "tags": "ai,machine-learning,future-tech,hands-on",
                "coord_email": "coord3@itsa.edu"
            },
            {
                "title": "Web Development Bootcamp",
                "category": "Workshop",
                "description": "Practical full-stack web engineering masterclass covering modern web development, REST APIs, responsive UI design, and cloud deployments.",
                "days_ahead": 25,
                "duration_hours": 6,
                "venue_id": lab_venue.id,
                "max_participants": 100,
                "tags": "webdev,fullstack,flask,javascript,apis",
                "coord_email": "coord4@itsa.edu"
            },
            {
                "title": "ITSA Innovation Meetup 2026",
                "category": "Seminar",
                "description": "Student-focused technology and innovation networking event featuring talks by alumni in tech industry and collaborative project showcases.",
                "days_ahead": 30,
                "duration_hours": 4,
                "venue_id": venue.id,
                "max_participants": 200,
                "tags": "networking,innovation,meetup,entrepreneurship",
                "coord_email": "coord5@itsa.edu"
            }
        ]

        for e_data in events_data:
            event = Event.query.filter_by(title=e_data["title"]).first()
            start_dt = base_time + timedelta(days=e_data["days_ahead"])
            end_dt = start_dt + timedelta(hours=e_data["duration_hours"])
            deadline_dt = start_dt - timedelta(days=2)
            cat_id = category_objs[e_data["category"]].id

            if not event:
                event = Event(
                    title=e_data["title"],
                    description=e_data["description"],
                    category_id=cat_id,
                    venue_id=e_data["venue_id"],
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    registration_deadline=deadline_dt,
                    max_participants=e_data["max_participants"],
                    status='REGISTRATION_OPEN',
                    is_free=True,
                    registration_fee=0.0,
                    tags=e_data["tags"],
                    created_by=admin.id
                )
                db.session.add(event)
                db.session.flush()
                print(f"[+] Event created: {e_data['title']}")
            else:
                event.status = 'REGISTRATION_OPEN'
                event.start_datetime = start_dt
                event.end_datetime = end_dt
                event.registration_deadline = deadline_dt
                event.category_id = cat_id

            coord_user = coord_user_map[e_data["coord_email"]]
            ec = EventCoordinator.query.filter_by(event_id=event.id, coordinator_id=coord_user.id).first()
            if not ec:
                ec = EventCoordinator(
                    event_id=event.id,
                    coordinator_id=coord_user.id,
                    role_in_event='Lead Coordinator',
                    assigned_by=admin.id
                )
                db.session.add(ec)
                print(f"[+] Assigned {coord_user.full_name} to {event.title}")

        db.session.commit()
        print("[OK] Demo coordinators and events seeded successfully (5 coordinators, 5 events).")

if __name__ == '__main__':
    seed_demo_data()