import os
import sys
from datetime import datetime, timedelta

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models.user import User, StudentProfile, CoordinatorProfile
from app.models.event import EventCategory, Venue, Event, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import Feedback
from app.models.post import Post, PostMedia, PostReaction
from app.models.comment import Comment
from app.models.gamification import ItsaPoints
from app.models.notification import Notification
from app.services.ticket_service import TicketService
from app.services.certificate_service import CertificateService

def seed_database():
    app = create_app('development')
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()

        # 1. Categories
        categories_data = [
            ("Technical", "Hackathons, coding contests, and developer challenges", "bi-code-slash"),
            ("Workshop", "Hands-on engineering workshops and bootcamps", "bi-tools"),
            ("Seminar", "Guest lectures by tech industry experts", "bi-mic"),
            ("Cultural", "Music, dance, drama, and artistic performances", "bi-music-note"),
            ("Sports", "Inter-department sports and athletic competitions", "bi-trophy"),
            ("Competition", "Quizzes, project expos, and debates", "bi-award"),
            ("Community Service", "Social outreach and teaching initiatives", "bi-heart"),
            ("Other", "General meetups and informal gatherings", "bi-three-dots")
        ]
        cat_map = {}
        for name, desc, icon in categories_data:
            cat = EventCategory.query.filter_by(name=name).first()
            if not cat:
                cat = EventCategory(name=name, description=desc, icon=icon)
                db.session.add(cat)
                db.session.flush()
            cat_map[name] = cat

        # 2. Venues
        venues_data = [
            ("Main University Auditorium", "Campus Central Building", 500, "Aud-1", "Block A"),
            ("Advanced Computer Lab 1", "Department of IT", 60, "Lab-101", "IT Wing"),
            ("Seminar Hall B", "Research Complex", 150, "SH-202", "Block C"),
            ("Campus Sports Complex", "West Campus Ground", 300, "Ground", "Sports Complex")
        ]
        venue_map = {}
        for name, addr, cap, room, bldg in venues_data:
            v = Venue.query.filter_by(name=name).first()
            if not v:
                v = Venue(name=name, address=addr, capacity=cap, room_number=room, building=bldg)
                db.session.add(v)
                db.session.flush()
            venue_map[name] = v

        # 3. Users
        # Admin
        admin = User.query.filter_by(email="admin@itsa.edu").first()
        if not admin:
            admin = User(
                email="admin@itsa.edu",
                full_name="ITSA Administrator",
                role="ADMIN",
                is_active=True
            )
            admin.set_password("Admin@12345")
            db.session.add(admin)
            db.session.flush()
            print("Admin created: admin@itsa.edu / Admin@12345")

        # Coordinator
        coord = User.query.filter_by(email="coordinator@itsa.edu").first()
        if not coord:
            coord = User(
                email="coordinator@itsa.edu",
                full_name="Vikram Mehta",
                role="COORDINATOR",
                is_active=True
            )
            coord.set_password("Coord@12345")
            db.session.add(coord)
            db.session.flush()
            coord_prof = CoordinatorProfile(
                user_id=coord.id,
                employee_id="ITSA-COORD-01",
                designation="Lead Event Coordinator",
                department="Information Technology",
                phone="+91 9876543210"
            )
            db.session.add(coord_prof)
            print("Coordinator created: coordinator@itsa.edu / Coord@12345")

        # Students
        students_data = [
            ("rahul@itsa.edu", "Rahul Sharma", "CS2023001", "Computer Science", 3, "AI & Web Dev Enthusiast", "Python, Machine Learning, Web Dev"),
            ("priya@itsa.edu", "Priya Patel", "IT2023042", "Information Technology", 2, "Cybersecurity & Cloud Computing", "Security, AWS, Linux"),
            ("amit@itsa.edu", "Amit Verma", "DS2024015", "Data Science", 1, "Data Science and Statistics", "Data Analysis, Python, SQL")
        ]
        student_users = []
        for email, name, roll, dept, yr, bio, interests in students_data:
            st = User.query.filter_by(email=email).first()
            if not st:
                st = User(
                    email=email,
                    full_name=name,
                    role="STUDENT",
                    is_active=True
                )
                st.set_password("Student@12345")
                db.session.add(st)
                db.session.flush()
                sp = StudentProfile(
                    user_id=st.id,
                    student_id=roll,
                    department=dept,
                    year_of_study=yr,
                    bio=bio,
                    interests=interests,
                    total_points=25
                )
                db.session.add(sp)
                print(f"Student created: {email} / Student@12345")
            student_users.append(st)

        db.session.commit()

        # 4. Events
        now = datetime.utcnow()
        events_seed = [
            {
                "title": "AI & Generative Tech Hackathon 2026",
                "description": "A 24-hour flagship hackathon organized by ITSA to build innovative applications using cutting-edge LLMs and computer vision. Includes industry mentorship and certificates.",
                "category": cat_map["Technical"],
                "venue": venue_map["Advanced Computer Lab 1"],
                "start": now + timedelta(days=5, hours=9),
                "end": now + timedelta(days=6, hours=17),
                "deadline": now + timedelta(days=4, hours=23),
                "status": "REGISTRATION_OPEN",
                "max": 60,
                "tags": "AI,Hackathon,Python,Gemini"
            },
            {
                "title": "Full-Stack Modern Web Workshop",
                "description": "Hands-on masterclass on building modern web applications with Flask, Bootstrap, responsive design, and REST APIs.",
                "category": cat_map["Workshop"],
                "venue": venue_map["Seminar Hall B"],
                "start": now + timedelta(days=12, hours=10),
                "end": now + timedelta(days=12, hours=16),
                "deadline": now + timedelta(days=10, hours=18),
                "status": "REGISTRATION_OPEN",
                "max": 80,
                "tags": "Flask,WebDev,JavaScript,Python"
            },
            {
                "title": "Cloud Computing & DevOps Masterclass",
                "description": "Learn cloud infrastructure, containerization, and modern CI/CD deployment pipelines directly from leading cloud architects.",
                "category": cat_map["Seminar"],
                "venue": venue_map["Main University Auditorium"],
                "start": now - timedelta(days=3, hours=4),
                "end": now - timedelta(days=3, hours=1),
                "deadline": now - timedelta(days=5),
                "status": "COMPLETED",
                "max": 150,
                "tags": "Cloud,DevOps,Docker,Architecture"
            }
        ]

        created_events = []
        for e_info in events_seed:
            ev = Event.query.filter_by(title=e_info["title"]).first()
            if not ev:
                ev = Event(
                    title=e_info["title"],
                    description=e_info["description"],
                    category_id=e_info["category"].id,
                    venue_id=e_info["venue"].id,
                    start_datetime=e_info["start"],
                    end_datetime=e_info["end"],
                    registration_deadline=e_info["deadline"],
                    max_participants=e_info["max"],
                    current_registrations=0,
                    status=e_info["status"],
                    tags=e_info["tags"],
                    created_by=admin.id
                )
                db.session.add(ev)
                db.session.flush()

                # Assign coordinator
                ec = EventCoordinator(
                    event_id=ev.id,
                    coordinator_id=coord.id,
                    role_in_event="Lead Coordinator",
                    assigned_by=admin.id
                )
                db.session.add(ec)
            created_events.append(ev)

        db.session.commit()

        # 5. Registrations & Attendance for Completed Event
        completed_event = created_events[2] # Cloud Masterclass
        primary_student = student_users[0] # Rahul

        existing_reg = EventRegistration.query.filter_by(event_id=completed_event.id, user_id=primary_student.id).first()
        if not existing_reg:
            reg = EventRegistration(
                event_id=completed_event.id,
                user_id=primary_student.id,
                registration_number=f"ITSA-{completed_event.id}-2026-0001",
                status="CONFIRMED"
            )
            db.session.add(reg)
            db.session.flush()

            # Ticket
            ticket = TicketService.generate_ticket(reg.id)

            # Attendance
            att = Attendance(
                event_id=completed_event.id,
                user_id=primary_student.id,
                registration_id=reg.id,
                ticket_id=ticket.id,
                scanned_by=coord.id,
                scanned_at=completed_event.start_datetime + timedelta(minutes=15),
                status="PRESENT"
            )
            db.session.add(att)
            db.session.flush()

            # Certificate
            CertificateService.generate_certificate(primary_student.id, completed_event.id, att.id)

            # Feedback
            fb = Feedback(
                event_id=completed_event.id,
                user_id=primary_student.id,
                rating=5,
                content="Exceptional session! The cloud architecture diagrams and practical demonstrations were brilliant.",
                suggestions="Please conduct a follow-up hands-on Kubernetes lab."
            )
            db.session.add(fb)

            # Points
            p1 = ItsaPoints(user_id=primary_student.id, points=10, reason='ATTENDANCE', related_event_id=completed_event.id)
            p2 = ItsaPoints(user_id=primary_student.id, points=5, reason='FEEDBACK', related_event_id=completed_event.id)
            db.session.add_all([p1, p2])

        # 6. Social Feed Posts
        if Post.query.count() == 0:
            post1 = Post(
                user_id=primary_student.id,
                content="Excited to participate in the upcoming #AI Hackathon! Looking for a teammate with frontend UI skills. DM or reply here! 🚀 #ITSA #Hackathon2026",
                post_type='TEXT',
                event_id=created_events[0].id
            )
            db.session.add(post1)
            db.session.flush()

            comm1 = Comment(
                post_id=post1.id,
                user_id=student_users[1].id,
                content="Hey Rahul! I'd love to team up, I'm working on Bootstrap 5 and React."
            )
            react1 = PostReaction(post_id=post1.id, user_id=student_users[1].id, reaction_type='LOVE')
            react2 = PostReaction(post_id=post1.id, user_id=coord.id, reaction_type='CELEBRATE')
            db.session.add_all([comm1, react1, react2])

        db.session.commit()
        print("Database seeded successfully with users, categories, venues, events, tickets, attendance, and feed posts!")

if __name__ == '__main__':
    seed_database()
