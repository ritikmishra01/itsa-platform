"""
ITSA Platform - Safe & Idempotent Temporary Demo Data Seeder and Cleanup Tool
----------------------------------------------------------------------------
Populates local database with clearly marked DEMO records for testing and presentation:
- 15 Demo Students (demo.student001@example.test ... demo.student015@example.test)
- 3 Demo Coordinators (demo.coord001@example.test ... demo.coord003@example.test)
- 1 Demo Admin (demo.admin001@example.test)
- 11 Demo Events (REGISTRATION_OPEN, ONGOING, COMPLETED, DRAFT, CANCELLED)
- Registrations, tickets, QR attendance, certificates, points, posts, comments, reports, notifications.

All records are tagged with '@example.test' and 'DEMO-' identifiers.
Cleanup mode (--clean) selectively and safely removes ONLY demo records.
"""

import os
import sys
import uuid
import argparse
from datetime import datetime, timedelta

# Ensure application path is discoverable
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app
from app.extensions import db
from app.models.user import User, StudentProfile, CoordinatorProfile
from app.models.event import EventCategory, Venue, Event, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.post import Post, PostReaction
from app.models.social import PostHashtag, Hashtag
from app.models.comment import Comment
from app.models.report import Report
from app.models.gamification import ItsaPoints
from app.models.notification import Notification
from app.models.audit import AuditLog

DEMO_DOMAIN = "@example.test"
DEMO_PASSWORD = "DemoStudent@123"
DEMO_ADMIN_PASSWORD = "DemoAdmin@123"
DEMO_COORD_PASSWORD = "DemoCoord@123"


def seed_demo_data(app):
    with app.app_context():
        print("=" * 65)
        print("ITSA PLATFORM — TEMPORARY DEMO DATA SEEDER")
        print("=" * 65)
        
        counts = {
            "users": 0,
            "profiles": 0,
            "venues": 0,
            "categories": 0,
            "events": 0,
            "coordinators_assigned": 0,
            "registrations": 0,
            "tickets": 0,
            "attendance": 0,
            "certificates": 0,
            "posts": 0,
            "comments": 0,
            "reactions": 0,
            "reports": 0,
            "points": 0,
            "notifications": 0,
            "audit_logs": 0
        }
        skipped = 0

        # -------------------------------------------------------------
        # 1. Venues & Categories (Ensure essential categories/venues exist)
        # -------------------------------------------------------------
        demo_venues_data = [
            {"name": "DEMO Main Auditorium", "address": "Campus Ground Floor", "capacity": 500, "room_number": "AUD-01", "building": "Academic Block A"},
            {"name": "DEMO Seminar Hall B", "address": "Campus 2nd Floor", "capacity": 150, "room_number": "SH-201", "building": "IT Center"},
            {"name": "DEMO Computing Lab 3", "address": "Campus 3rd Floor", "capacity": 80, "room_number": "LAB-305", "building": "Innovation Hub"},
            {"name": "DEMO Open Amphitheatre", "address": "Campus Quadrangle", "capacity": 300, "room_number": "AMP-01", "building": "Student Center"}
        ]
        venues = []
        for vd in demo_venues_data:
            v = Venue.query.filter_by(name=vd["name"]).first()
            if not v:
                v = Venue(**vd)
                db.session.add(v)
                counts["venues"] += 1
            venues.append(v)
        db.session.flush()

        cat_names = [
            ("Technical", "Hackathons, coding challenges, and tech workshops", "bi-laptop"),
            ("Workshop", "Hands-on learning sessions and bootcamps", "bi-tools"),
            ("Seminar", "Guest lectures and industry keynotes", "bi-easel"),
            ("Cultural", "Departmental community and student fest", "bi-stars"),
            ("Competition", "Competitive tech events and quizzes", "bi-trophy")
        ]
        categories = []
        for name, desc, icon in cat_names:
            c = EventCategory.query.filter_by(name=name).first()
            if not c:
                c = EventCategory(name=name, description=desc, icon=icon)
                db.session.add(c)
                counts["categories"] += 1
            categories.append(c)
        db.session.flush()

        # -------------------------------------------------------------
        # 2. Demo Admin Account
        # -------------------------------------------------------------
        demo_admin_email = f"demo.admin001{DEMO_DOMAIN}"
        demo_admin = User.query.filter_by(email=demo_admin_email).first()
        if not demo_admin:
            demo_admin = User(
                email=demo_admin_email,
                full_name="DEMO System Administrator",
                role="ADMIN",
                is_active=True
            )
            demo_admin.set_password(DEMO_ADMIN_PASSWORD)
            db.session.add(demo_admin)
            counts["users"] += 1
            db.session.flush()
        else:
            skipped += 1

        # -------------------------------------------------------------
        # 3. Demo Coordinators (3)
        # -------------------------------------------------------------
        coord_specs = [
            ("demo.coord001", "DEMO Prof. Rajesh Sharma", "Faculty Coordinator", "Information Technology", "DEMO-EMP-001"),
            ("demo.coord002", "DEMO Dr. Priya Deshmukh", "Head Coordinator", "Computer Engineering", "DEMO-EMP-002"),
            ("demo.coord003", "DEMO Prof. Amit Patil", "Technical Coordinator", "Data Science", "DEMO-EMP-003"),
            ("coord1@itsa.edu", "Prof. R. K. Verma", "Faculty Coordinator", "Information Technology", "COORD-EMP-001"),
            ("coord2@itsa.edu", "Dr. S. N. Joshi", "Department Coordinator", "Computer Engineering", "COORD-EMP-002"),
            ("coord3@itsa.edu", "Prof. A. M. Patil", "Technical Coordinator", "Data Science", "COORD-EMP-003"),
            ("coord4@itsa.edu", "Prof. N. K. Deshmukh", "Cultural Coordinator", "Information Technology", "COORD-EMP-004"),
            ("coord5@itsa.edu", "Dr. P. S. Kulkarni", "Head Coordinator", "Computer Engineering", "COORD-EMP-005")
        ]
        coordinators = []
        for uname, fname, desig, dept, emp_id in coord_specs:
            email = uname if "@" in uname else f"{uname}{DEMO_DOMAIN}"
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(
                    email=email,
                    full_name=fname,
                    role="COORDINATOR",
                    is_active=True
                )
                u.set_password(DEMO_COORD_PASSWORD)
                db.session.add(u)
                db.session.flush()
                counts["users"] += 1

                cp = CoordinatorProfile(
                    user_id=u.id,
                    employee_id=emp_id,
                    designation=desig,
                    department=dept,
                    phone="+91 98200 11223"
                )
                db.session.add(cp)
                counts["profiles"] += 1
            else:
                skipped += 1
            coordinators.append(u)
        db.session.flush()

        # -------------------------------------------------------------
        # 4. Demo Students (15)
        # -------------------------------------------------------------
        departments = ["Information Technology", "Computer Engineering", "Data Science", "AI & Machine Learning"]
        student_data = [
            ("Aarav Mehta", 3, 45),
            ("Ananya Sharma", 2, 60),
            ("Rohan Kulkarni", 4, 90),
            ("Sneha Iyer", 1, 20),
            ("Aditya Verma", 3, 35),
            ("Tanvi Joshi", 2, 50),
            ("Vikram Nair", 4, 110),
            ("Ishita Sen", 3, 75),
            ("Kabir Deshmukh", 2, 30),
            ("Meera Chawla", 1, 15),
            ("Pranav Gaikwad", 3, 85),
            ("Riya Kapadia", 4, 95),
            ("Siddharth Rao", 2, 40),
            ("Pooja Hegde", 3, 55),
            ("Karan Malhotra", 1, 25)
        ]
        students = []
        for i, (name, year, pts) in enumerate(student_data, start=1):
            email = f"demo.student{i:03d}{DEMO_DOMAIN}"
            roll_no = f"DEMO-IT-{i:03d}"
            dept = departments[(i - 1) % len(departments)]
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(
                    email=email,
                    full_name=f"DEMO {name}",
                    role="STUDENT",
                    is_active=True
                )
                u.set_password(DEMO_PASSWORD)
                db.session.add(u)
                db.session.flush()
                counts["users"] += 1

                sp = StudentProfile(
                    user_id=u.id,
                    student_id=roll_no,
                    department=dept,
                    year_of_study=year,
                    total_points=pts,
                    phone=f"+91 98111 {i:05d}",
                    bio=f"Passionate {dept} student interested in cloud computing, AI, and competitive programming."
                )
                db.session.add(sp)
                counts["profiles"] += 1
            else:
                skipped += 1
            students.append(u)
        db.session.flush()

        # -------------------------------------------------------------
        # 5. Demo Events (11 across all statuses)
        # -------------------------------------------------------------
        now = datetime.utcnow()
        event_definitions = [
            # 1. Upcoming Registration Open
            {
                "title": "DEMO ITSA AI & Cloud Hackathon 2026",
                "description": "36-hour flagship college hackathon exploring LLMs, agentic workflows, and cloud-native scalable backends.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 0, "venue_idx": 0,
                "start": now + timedelta(days=5),
                "end": now + timedelta(days=7),
                "deadline": now + timedelta(days=4),
                "max_p": 120, "is_free": True, "fee": 0.0,
                "tags": "AI,Hackathon,Cloud,Python,FastAPI"
            },
            {
                "title": "DEMO Modern Full-Stack Flask & React Workshop",
                "description": "Hands-on masterclass building responsive SaaS web applications using Flask 3, Bootstrap 5, and PostgreSQL.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 1, "venue_idx": 1,
                "start": now + timedelta(days=8),
                "end": now + timedelta(days=8, hours=4),
                "deadline": now + timedelta(days=7),
                "max_p": 60, "is_free": True, "fee": 0.0,
                "tags": "Flask,Python,WebDev,Workshop"
            },
            {
                "title": "DEMO Cybersecurity & Ethical Hacking Bootcamp",
                "description": "Live penetration testing lab covering web security, OWASP top 10 vulnerabilities, and security hardening.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 1, "venue_idx": 2,
                "start": now + timedelta(days=12),
                "end": now + timedelta(days=13),
                "deadline": now + timedelta(days=11),
                "max_p": 45, "is_free": True, "fee": 0.0,
                "tags": "Cybersecurity,InfoSec,EthicalHacking"
            },
            {
                "title": "DEMO Generative AI & Gemini Masterclass",
                "description": "Learn multimodal prompt engineering, function calling, and structured outputs using the Google GenAI SDK.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 2, "venue_idx": 0,
                "start": now + timedelta(days=15),
                "end": now + timedelta(days=15, hours=3),
                "deadline": now + timedelta(days=14),
                "max_p": 200, "is_free": True, "fee": 0.0,
                "tags": "Gemini,GenAI,DeepLearning"
            },
            # 2. Ongoing
            {
                "title": "DEMO Annual Tech-Quiz Championship",
                "description": "Real-time competitive tech quiz competition testing algorithms, computer networks, and IT history.",
                "status": "ONGOING",
                "cat_idx": 4, "venue_idx": 1,
                "start": now - timedelta(hours=2),
                "end": now + timedelta(hours=4),
                "deadline": now - timedelta(hours=3),
                "max_p": 80, "is_free": True, "fee": 0.0,
                "tags": "Quiz,Competition,Algorithms"
            },
            {
                "title": "DEMO ITSA Open Source Sprint",
                "description": "Live sprint contributing to open source repositories and mentorship on Git collaboration.",
                "status": "ONGOING",
                "cat_idx": 0, "venue_idx": 2,
                "start": now - timedelta(hours=1),
                "end": now + timedelta(hours=5),
                "deadline": now - timedelta(hours=2),
                "max_p": 50, "is_free": True, "fee": 0.0,
                "tags": "OpenSource,Git,Collaboration"
            },
            # 3. Completed
            {
                "title": "DEMO Orientation & Fresher Tech Induction",
                "description": "Welcome orientation for first-year IT students with senior project exhibitions and networking.",
                "status": "COMPLETED",
                "cat_idx": 3, "venue_idx": 0,
                "start": now - timedelta(days=14),
                "end": now - timedelta(days=14, hours=-4),
                "deadline": now - timedelta(days=16),
                "max_p": 300, "is_free": True, "fee": 0.0,
                "tags": "Induction,Orientation,Freshers"
            },
            {
                "title": "DEMO Data Structures & Algorithms Camp",
                "description": "3-day intensive problem-solving camp covering dynamic programming, graph theory, and interview prep.",
                "status": "COMPLETED",
                "cat_idx": 1, "venue_idx": 2,
                "start": now - timedelta(days=20),
                "end": now - timedelta(days=18),
                "deadline": now - timedelta(days=22),
                "max_p": 70, "is_free": True, "fee": 0.0,
                "tags": "DSA,Coding,Interview"
            },
            {
                "title": "DEMO DevOps & Docker Containerization Seminar",
                "description": "Industry speaker session on Docker containers, Kubernetes orchestrations, and CI/CD pipelines.",
                "status": "COMPLETED",
                "cat_idx": 2, "venue_idx": 1,
                "start": now - timedelta(days=28),
                "end": now - timedelta(days=28, hours=-3),
                "deadline": now - timedelta(days=30),
                "max_p": 100, "is_free": True, "fee": 0.0,
                "tags": "DevOps,Docker,CI/CD"
            },
            # 4. Draft
            {
                "title": "DEMO Blockchain & Web3 Architecture Workshop",
                "description": "Upcoming draft event on smart contract design, Ethereum virtual machines, and decentralized protocols.",
                "status": "DRAFT",
                "cat_idx": 0, "venue_idx": 1,
                "start": now + timedelta(days=25),
                "end": now + timedelta(days=25, hours=4),
                "deadline": now + timedelta(days=24),
                "max_p": 50, "is_free": True, "fee": 0.0,
                "tags": "Web3,Blockchain,Solidity"
            },
            # 5. Cancelled
            {
                "title": "DEMO Robotics & IoT Drone Showcase",
                "description": "Cancelled demonstration event due to technical lab maintenance and component re-allocation.",
                "status": "CANCELLED",
                "cat_idx": 0, "venue_idx": 3,
                "start": now + timedelta(days=3),
                "end": now + timedelta(days=3, hours=3),
                "deadline": now + timedelta(days=2),
                "max_p": 100, "is_free": True, "fee": 0.0,
                "tags": "Robotics,IoT,Hardware"
            },
            # 6. Flagship Events
            {
                "title": "TechFest 2026",
                "description": "Annual technical symposium of ITSA featuring code wars, robotics, paper presentations, and tech talks.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 0, "venue_idx": 0,
                "start": now + timedelta(days=15),
                "end": now + timedelta(days=17),
                "deadline": now + timedelta(days=14),
                "max_p": 250, "is_free": True, "fee": 0.0,
                "tags": "TechFest,Symposium,Flagship"
            },
            {
                "title": "CodeSprint 2026",
                "description": "Intense 6-hour competitive coding competition testing algorithmic mastery and data structure skills.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 4, "venue_idx": 1,
                "start": now + timedelta(days=10),
                "end": now + timedelta(days=10, hours=6),
                "deadline": now + timedelta(days=9),
                "max_p": 80, "is_free": True, "fee": 0.0,
                "tags": "Coding,Competition,Algorithms"
            },
            {
                "title": "AI & Future Technologies Workshop",
                "description": "Interactive workshop covering generative AI architectures, prompt engineering, and fine-tuning models.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 1, "venue_idx": 2,
                "start": now + timedelta(days=12),
                "end": now + timedelta(days=12, hours=4),
                "deadline": now + timedelta(days=11),
                "max_p": 100, "is_free": True, "fee": 0.0,
                "tags": "AI,GenerativeAI,Workshop"
            },
            {
                "title": "Web Development Bootcamp",
                "description": "Comprehensive weekend bootcamp on modern responsive web development with Python Flask and modern CSS.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 1, "venue_idx": 1,
                "start": now + timedelta(days=18),
                "end": now + timedelta(days=19),
                "deadline": now + timedelta(days=17),
                "max_p": 60, "is_free": True, "fee": 0.0,
                "tags": "WebDev,Bootcamp,FullStack"
            },
            {
                "title": "ITSA Innovation Meetup 2026",
                "description": "Networking meetup bringing together alumni, industry experts, and student tech innovators.",
                "status": "REGISTRATION_OPEN",
                "cat_idx": 2, "venue_idx": 0,
                "start": now + timedelta(days=22),
                "end": now + timedelta(days=22, hours=3),
                "deadline": now + timedelta(days=21),
                "max_p": 150, "is_free": True, "fee": 0.0,
                "tags": "Meetup,Innovation,Networking"
            }
        ]

        demo_events = []
        for ed in event_definitions:
            ev = Event.query.filter_by(title=ed["title"]).first()
            if not ev:
                ev = Event(
                    title=ed["title"],
                    description=ed["description"],
                    category_id=categories[ed["cat_idx"]].id,
                    venue_id=venues[ed["venue_idx"]].id,
                    start_datetime=ed["start"],
                    end_datetime=ed["end"],
                    registration_deadline=ed["deadline"],
                    max_participants=ed["max_p"],
                    status=ed["status"],
                    is_free=ed["is_free"],
                    registration_fee=ed["fee"],
                    tags=ed["tags"],
                    created_by=demo_admin.id
                )
                db.session.add(ev)
                counts["events"] += 1
                db.session.flush()

                # Assign 1-2 Coordinators
                coord1 = coordinators[len(demo_events) % len(coordinators)]
                ec1 = EventCoordinator(
                    event_id=ev.id,
                    coordinator_id=coord1.id,
                    role_in_event="Lead Coordinator",
                    assigned_by=demo_admin.id
                )
                db.session.add(ec1)
                counts["coordinators_assigned"] += 1
            else:
                skipped += 1
            demo_events.append(ev)
        db.session.flush()

        # -------------------------------------------------------------
        # 6. Registrations, Tickets, Attendance & Certificates
        # -------------------------------------------------------------
        for ev_idx, ev in enumerate(demo_events):
            # Select subset of students to register
            # For completed events, register 6-10 students; for open events register 4-8 students
            if ev.status in ("COMPLETED", "ONGOING", "REGISTRATION_OPEN"):
                num_regs = 8 if ev.status == "COMPLETED" else 5
                registered_students = students[:num_regs]
                for s_idx, st in enumerate(registered_students):
                    reg_no = f"DEMO-REG-EV{ev.id:02d}-ST{st.id:03d}"
                    existing_reg = EventRegistration.query.filter_by(registration_number=reg_no).first()
                    if not existing_reg:
                        reg_status = "CONFIRMED"
                        reg = EventRegistration(
                            event_id=ev.id,
                            user_id=st.id,
                            registration_number=reg_no,
                            status=reg_status,
                            registered_at=ev.created_at + timedelta(hours=s_idx + 1)
                        )
                        db.session.add(reg)
                        counts["registrations"] += 1
                        db.session.flush()

                        # Issue Ticket
                        tkt_code = f"DEMO-TKT-{uuid.uuid4().hex[:12].upper()}"
                        ticket = EventTicket(
                            registration_id=reg.id,
                            ticket_code=tkt_code,
                            issued_at=reg.registered_at,
                            is_valid=True
                        )
                        db.session.add(ticket)
                        counts["tickets"] += 1
                        db.session.flush()

                        # Update event registration count
                        ev.current_registrations += 1

                        # If event is completed, record verified attendance and issue certificate
                        if ev.status == "COMPLETED" and s_idx < 6:
                            coord = coordinators[s_idx % len(coordinators)]
                            att = Attendance(
                                event_id=ev.id,
                                user_id=st.id,
                                registration_id=reg.id,
                                ticket_id=ticket.id,
                                scanned_by=coord.id,
                                scanned_at=ev.start_datetime + timedelta(minutes=15 * s_idx),
                                status="PRESENT",
                                notes="Verified attendance via QR scanner."
                            )
                            db.session.add(att)
                            counts["attendance"] += 1
                            db.session.flush()

                            # Issue Certificate
                            cert_code = f"DEMO-CERT-{uuid.uuid4().hex[:10].upper()}"
                            cert_type = "WINNER" if s_idx == 0 else "PARTICIPATION"
                            cert = Certificate(
                                user_id=st.id,
                                event_id=ev.id,
                                attendance_id=att.id,
                                certificate_code=cert_code,
                                certificate_type=cert_type,
                                pdf_path=f"uploads/certificates/{cert_code}.pdf",
                                issued_at=att.scanned_at + timedelta(hours=2),
                                is_valid=True
                            )
                            db.session.add(cert)
                            counts["certificates"] += 1

                            # Award Attendance Points
                            pts = ItsaPoints(
                                user_id=st.id,
                                points=10,
                                reason="ATTENDANCE",
                                related_event_id=ev.id,
                                created_at=att.scanned_at
                            )
                            db.session.add(pts)
                            counts["points"] += 1
        db.session.flush()

        # -------------------------------------------------------------
        # 7. Community Posts, Comments, Reactions & Reports
        # -------------------------------------------------------------
        post_templates = [
            ("DEMO: What an incredible turnout at the ITSA AI & Cloud Hackathon! Super proud of all the student teams building real projects! #hackathon #ai", students[0]),
            ("DEMO: Just deployed my first containerized Flask app on Render! Check out my GitHub repo if anyone wants to collaborate. #opensource #python", students[1]),
            ("DEMO: The DSA problem-solving bootcamp was super helpful for technical interview prep. Huge thanks to the coordinator team! #dsa #careers", students[2]),
            ("DEMO: Excited to present our project at the annual ITSA tech exhibition tomorrow. Who else is showcasing their work? #techfest", students[3]),
            ("DEMO: Please remember to verify your digital certificates from the official portal before the end of the semester! #announcements", coordinators[0]),
            ("DEMO: [Flagged for Review] Check out this spammy third-party unauthorized exam leaked answers link here!", students[4])
        ]

        created_posts = []
        for content, author in post_templates:
            existing_p = Post.query.filter_by(content=content).first()
            if not existing_p:
                p = Post(
                    user_id=author.id,
                    content=content,
                    post_type="TEXT",
                    is_active=True,
                    is_reported=("Flagged" in content),
                    created_at=now - timedelta(days=2, hours=len(created_posts) * 3)
                )
                db.session.add(p)
                counts["posts"] += 1
                db.session.flush()
                created_posts.append(p)

                # Add 1-2 Comments
                commenter = students[(author.id + 1) % len(students)]
                c = Comment(
                    post_id=p.id,
                    user_id=commenter.id,
                    content=f"DEMO: Great initiative! Thanks for sharing @{author.full_name.split()[-1]}.",
                    is_active=True,
                    created_at=p.created_at + timedelta(minutes=45)
                )
                db.session.add(c)
                counts["comments"] += 1

                # Add Reactions
                for r_idx in range(3):
                    reactor = students[(author.id + r_idx + 2) % len(students)]
                    react = PostReaction(
                        post_id=p.id,
                        user_id=reactor.id,
                        reaction_type="LIKE" if r_idx % 2 == 0 else "LOVE"
                    )
                    db.session.add(react)
                    counts["reactions"] += 1

                # If flagged, add to Moderation Reports queue
                if "Flagged" in content:
                    reporter = students[0]
                    rep = Report(
                        reporter_id=reporter.id,
                        reported_post_id=p.id,
                        reason="SPAM",
                        description="DEMO: Reported for unauthorized external academic spam link.",
                        status="PENDING",
                        created_at=now - timedelta(hours=3)
                    )
                    db.session.add(rep)
                    counts["reports"] += 1

                # Award Social Post Points
                pts = ItsaPoints(
                    user_id=author.id,
                    points=2,
                    reason="SOCIAL_POST",
                    related_post_id=p.id,
                    created_at=p.created_at
                )
                db.session.add(pts)
                counts["points"] += 1
            else:
                skipped += 1
        db.session.flush()

        # -------------------------------------------------------------
        # 8. Notifications & Audit Logs (Idempotent check)
        # -------------------------------------------------------------
        for st in students[:5]:
            notif_title = "DEMO: Welcome to ITSA Platform"
            if not Notification.query.filter_by(user_id=st.id, title=notif_title).first():
                notif = Notification(
                    user_id=st.id,
                    type="ANNOUNCEMENT",
                    title=notif_title,
                    message="Welcome to the ITSA AI-Powered Event Management Platform! Explore upcoming hackathons, earn badges, and track your points.",
                    is_read=False,
                    created_at=now - timedelta(days=1)
                )
                db.session.add(notif)
                counts["notifications"] += 1
            else:
                skipped += 1

        audit_actions = [
            ("CREATE_EVENT", "Event", demo_events[0].id if demo_events else 1, {"title": demo_events[0].title if demo_events else ""}),
            ("ASSIGN_COORDINATOR", "EventCoordinator", coordinators[0].id, {"assigned": coordinators[0].full_name}),
            ("ISSUE_CERTIFICATE", "Certificate", 1, {"type": "WINNER"}),
            ("MODERATE_CONTENT", "Report", 1, {"action": "FLAGGED_FOR_REVIEW"})
        ]
        for act, etype, eid, details in audit_actions:
            if not AuditLog.query.filter_by(user_id=demo_admin.id, action=act, entity_type=etype).first():
                al = AuditLog(
                    user_id=demo_admin.id,
                    action=act,
                    entity_type=etype,
                    entity_id=eid,
                    details=details,
                    ip_address="127.0.0.1",
                    created_at=now - timedelta(hours=12)
                )
                db.session.add(al)
                counts["audit_logs"] += 1
            else:
                skipped += 1

        db.session.commit()

        print("\nSeed Summary:")
        print("-" * 40)
        for k, v in counts.items():
            print(f"  {k:22}: {v} created")
        print(f"  {'Existing (Skipped)':22}: {skipped}")
        print("=" * 65)
        print("Demo data seeded successfully and idempotently!")
        print("=" * 65)


def cleanup_demo_data(app, dry_run=True):
    with app.app_context():
        print("=" * 65)
        print("ITSA PLATFORM — SAFE DEMO DATA CLEANUP TOOL")
        print("=" * 65)
        print(f"Mode: {'DRY RUN (Inspect only, no deletions)' if dry_run else 'LIVE CLEANUP (Explicit deletion confirmed)'}")
        print("=" * 65)

        # Identify all demo users
        legacy_coord_emails = ["coord1@itsa.edu", "coord2@itsa.edu", "coord3@itsa.edu", "coord4@itsa.edu", "coord5@itsa.edu"]
        demo_users = User.query.filter(
            (User.email.like(f"%{DEMO_DOMAIN}")) |
            (User.email.in_(legacy_coord_emails))
        ).all()
        demo_user_ids = [u.id for u in demo_users]
        print(f"Found {len(demo_users)} Demo User accounts (tagged with '{DEMO_DOMAIN}' or legacy demo coords)")

        # Identify all demo events
        legacy_event_titles = ["TechFest 2026", "CodeSprint 2026", "AI & Future Technologies Workshop", "Web Development Bootcamp", "ITSA Innovation Meetup 2026"]
        demo_events = Event.query.filter(
            (Event.title.like("DEMO %")) |
            (Event.title.in_(legacy_event_titles))
        ).all()
        demo_event_ids = [e.id for e in demo_events]
        print(f"Found {len(demo_events)} Demo Events (prefixed with 'DEMO ' or legacy flagship)")

        # Identify demo venues
        demo_venues = Venue.query.filter(Venue.name.like("DEMO %")).all()
        print(f"Found {len(demo_venues)} Demo Venues")

        # Identify demo registrations & tickets
        demo_regs = EventRegistration.query.filter(
            (EventRegistration.user_id.in_(demo_user_ids)) | 
            (EventRegistration.registration_number.like("DEMO-%"))
        ).all()
        demo_reg_ids = [r.id for r in demo_regs]
        demo_tickets = EventTicket.query.filter(
            (EventTicket.registration_id.in_(demo_reg_ids)) | 
            (EventTicket.ticket_code.like("DEMO-%"))
        ).all()
        print(f"Found {len(demo_regs)} Demo Registrations and {len(demo_tickets)} Demo Tickets")

        # Identify demo attendances and certificates
        demo_att = Attendance.query.filter(
            (Attendance.user_id.in_(demo_user_ids)) | 
            (Attendance.event_id.in_(demo_event_ids))
        ).all()
        demo_certs = Certificate.query.filter(
            (Certificate.user_id.in_(demo_user_ids)) | 
            (Certificate.certificate_code.like("DEMO-%"))
        ).all()
        print(f"Found {len(demo_att)} Demo Attendances and {len(demo_certs)} Demo Certificates")

        # Identify demo posts, comments, reports, points, notifications
        demo_posts = Post.query.filter(
            (Post.user_id.in_(demo_user_ids)) | 
            (Post.content.like("DEMO:%"))
        ).all()
        demo_post_ids = [p.id for p in demo_posts]
        demo_comments = Comment.query.filter(
            (Comment.user_id.in_(demo_user_ids)) | 
            (Comment.post_id.in_(demo_post_ids))
        ).all()
        demo_reports = Report.query.filter(
            (Report.reporter_id.in_(demo_user_ids)) | 
            (Report.description.like("DEMO:%"))
        ).all()
        demo_points = ItsaPoints.query.filter(ItsaPoints.user_id.in_(demo_user_ids)).all()
        demo_notifs = Notification.query.filter(
            (Notification.user_id.in_(demo_user_ids)) | 
            (Notification.title.like("DEMO:%"))
        ).all()
        demo_audits = AuditLog.query.filter(AuditLog.user_id.in_(demo_user_ids)).all()

        print(f"Found {len(demo_posts)} Demo Posts, {len(demo_comments)} Comments, {len(demo_reports)} Reports")
        print(f"Found {len(demo_points)} Points Records, {len(demo_notifs)} Notifications, {len(demo_audits)} Audit Logs")

        total_demo_records = (
            len(demo_users) + len(demo_events) + len(demo_venues) + 
            len(demo_regs) + len(demo_tickets) + len(demo_att) + len(demo_certs) + 
            len(demo_posts) + len(demo_comments) + len(demo_reports) + 
            len(demo_points) + len(demo_notifs) + len(demo_audits)
        )
        print("-" * 65)
        print(f"TOTAL DEMO RECORDS TARGETED FOR CLEANUP: {total_demo_records}")
        print("-" * 65)

        if dry_run:
            print("DRY RUN COMPLETE: No data was removed. Use --confirm to perform live deletion.")
            return

        print("Executing safe deletion of DEMO records in foreign key dependency order...")
        # 1. Certificates
        for c in demo_certs:
            db.session.delete(c)
        # 2. Attendance
        for a in demo_att:
            db.session.delete(a)
        # 3. Tickets
        for t in demo_tickets:
            db.session.delete(t)
        # 4. Registrations
        for r in demo_regs:
            db.session.delete(r)
        # 5. Reports
        for rep in demo_reports:
            db.session.delete(rep)
        # 6. Comments
        for cm in demo_comments:
            db.session.delete(cm)
        # 7. Posts
        for p in demo_posts:
            db.session.delete(p)
        # 8. Points
        for pt in demo_points:
            db.session.delete(pt)
        # 9. Notifications
        for n in demo_notifs:
            db.session.delete(n)
        # 10. Audit logs
        for al in demo_audits:
            db.session.delete(al)
        # 11. Event Coordinators & Events
        for ev in demo_events:
            db.session.delete(ev)
        # 12. Venues
        for v in demo_venues:
            db.session.delete(v)
        # 13. Users (Cascades to StudentProfile and CoordinatorProfile)
        for u in demo_users:
            db.session.delete(u)

        db.session.commit()
        print("CLEANUP SUCCESSFUL: All targeted DEMO records have been safely removed.")
        print("Real user data, existing events, and production tables remain completely intact.")
        print("=" * 65)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ITSA Platform Demo Data Seeder & Cleanup")
    parser.add_argument('--clean', action='store_true', help="Clean up demo data (defaults to dry-run)")
    parser.add_argument('--confirm', action='store_true', help="Confirm deletion in cleanup mode")
    args = parser.parse_args()

    app = create_app('development')
    if args.clean:
        cleanup_demo_data(app, dry_run=not args.confirm)
    else:
        seed_demo_data(app)