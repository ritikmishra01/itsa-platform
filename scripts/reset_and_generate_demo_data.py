"""
ITSA Platform - Local Development Database Reset & Fresh Demo Data Generator
=============================================================================
Completely resets the local SQLite development database and generates fresh,
realistic, and internally consistent demo data for project demonstrations.

Safety Guard:
- Strictly operates on local SQLite database only.
- Never runs against PostgreSQL or production environments.
- Automatically creates a full timestamped backup of the local database before changes.
"""

import os
import sys
import shutil
import uuid
from datetime import datetime, timedelta

# Ensure application path is discoverable
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app
from app.extensions import db

from app.models import (
    User, StudentProfile, CoordinatorProfile,
    EventCategory, Venue, Event, EventCoordinator,
    EventRegistration, EventTicket, Attendance,
    Certificate, Feedback,
    Post, PostMedia, PostReaction,
    Comment, CommentReply,
    PostShare, SavedPost, Hashtag, PostHashtag, Mention,
    Notification, ItsaPoints,
    EventGallery, EventVolunteer,
    Report, AiRecommendation, AiAnalysis, AuditLog
)

# Services
from app.services.ticket_service import TicketService
from app.services.certificate_service import CertificateService

def run_reset_and_demo_seed():
    app = create_app('development')
    with app.app_context():
        # ── 1. Safety Guard Check ───────────────────────────────────────────
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not db_uri.startswith('sqlite:'):
            raise RuntimeError(
                f"SAFETY ABORT: Refusing to reset non-SQLite database! URI scheme: {db_uri.split('://')[0]}. "
                "This script is authorized for local SQLite development database only."
            )

        print("=" * 70)
        print("  ITSA PLATFORM - LOCAL DATABASE RESET & DEMO DATA GENERATION")
        print("=" * 70)
        print(f"Target Database URI: {db_uri}")
        print(f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 70)

        # ── 2. Backup Local Database ────────────────────────────────────────
        inst_db = os.path.join(basedir, 'instance', 'itsa_platform.db')
        root_db = os.path.join(basedir, 'itsa_platform.db')
        source_db = inst_db if os.path.exists(inst_db) and os.path.getsize(inst_db) > 0 else root_db

        backup_file_path = None
        if os.path.exists(source_db):
            backup_dir = os.path.join(basedir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_file_path = os.path.join(backup_dir, f"itsa_platform_backup_pre_reset_{ts}.db")
            shutil.copy2(source_db, backup_file_path)
            backup_size = os.path.getsize(backup_file_path)
            print(f"✅ Backup created successfully:")
            print(f"   Source: {source_db}")
            print(f"   Location: {backup_file_path}")
            print(f"   Size: {backup_size:,} bytes")
        else:
            print("⚠️ No existing database file found to backup; fresh database will be initialized.")

        # ── 3. Reset All Relational Records (Clean Deletion in FK Order) ────
        print("\n── Resetting Existing Records ─────────────────────────────────")
        deletion_order = [
            ("post_reactions", PostReaction),
            ("comment_replies", CommentReply),
            ("comments", Comment),
            ("post_media", PostMedia),
            ("post_hashtags", PostHashtag),
            ("post_shares", PostShare),
            ("saved_posts", SavedPost),
            ("reports", Report),
            ("mentions", Mention),
            ("posts", Post),
            ("hashtags", Hashtag),
            ("certificates", Certificate),
            ("attendance", Attendance),
            ("event_tickets", EventTicket),
            ("event_registrations", EventRegistration),
            ("feedback", Feedback),
            ("event_volunteers", EventVolunteer),
            ("event_gallery", EventGallery),
            ("event_coordinators", EventCoordinator),
            ("events", Event),
            ("venues", Venue),
            ("event_categories", EventCategory),
            ("itsa_points", ItsaPoints),
            ("notifications", Notification),
            ("ai_analysis", AiAnalysis),
            ("ai_recommendations", AiRecommendation),
            ("audit_logs", AuditLog),
            ("student_profiles", StudentProfile),
            ("coordinator_profiles", CoordinatorProfile),
            ("users", User)
        ]

        deleted_counts = {}
        for name, model in deletion_order:
            try:
                count = model.query.delete()
                deleted_counts[name] = count
            except Exception as e:
                # If table doesn't exist yet, pass
                deleted_counts[name] = 0

        db.session.commit()
        total_deleted = sum(deleted_counts.values())
        print(f"✅ Removed {total_deleted} existing records across {len(deletion_order)} tables.")

        # Ensure all tables exist
        db.create_all()

        # ── 4. Seed Standard Categories & Venues ─────────────────────────────
        print("\n── Seeding Categories & Venues ────────────────────────────────")
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
            cat = EventCategory(name=name, description=desc, icon=icon)
            db.session.add(cat)
            db.session.flush()
            cat_map[name] = cat

        venues_data = [
            ("Main University Auditorium", "Campus Central Building", 500, "AUD-01", "Academic Block A"),
            ("Advanced Computer Lab 1", "Department of IT", 60, "LAB-101", "IT Wing"),
            ("Seminar Hall B", "Campus 2nd Floor", 150, "SH-202", "IT Center"),
            ("Innovation & IoT Research Lab", "Department of IT", 40, "LAB-204", "Research Complex"),
            ("Campus Sports Pavilion", "West Campus Ground", 300, "GROUND-01", "Sports Wing")
        ]
        venue_map = {}
        for name, addr, cap, room, bldg in venues_data:
            v = Venue(name=name, address=addr, capacity=cap, room_number=room, building=bldg)
            db.session.add(v)
            db.session.flush()
            venue_map[name] = v

        print(f"✅ Seeded {len(cat_map)} categories and {len(venue_map)} venues.")

        # ── 5. Create Exactly 1 Admin, 5 Coordinators, 5 Students ───────────
        print("\n── Creating Standardized User Accounts ────────────────────────")
        
        # 5a. 1 Administrator
        admin = User(
            email="admin@itsa.edu",
            full_name="Prof. Rajeshwari Natarajan",
            role="ADMIN",
            is_active=True
        )
        admin.set_password("SecureLocalAdmin#2026")
        db.session.add(admin)
        db.session.flush()
        print("  [ADMIN]       admin@itsa.edu          / SecureLocalAdmin#2026 -> Prof. Rajeshwari Natarajan")

        # 5b. 5 Event Coordinators
        coordinator_specs = [
            ("coord1@itsa.edu", "Prof. Rajesh Kulkarni", "Lead Event Coordinator", "Information Technology", "COORD-EMP-001", "+91 98201 12341"),
            ("coord2@itsa.edu", "Dr. Sunita Patil", "Department Coordinator", "Computer Engineering", "COORD-EMP-002", "+91 98202 23452"),
            ("coord3@itsa.edu", "Prof. Amit Deshmukh", "Technical Workshop Coordinator", "Data Science", "COORD-EMP-003", "+91 98203 34563"),
            ("coord4@itsa.edu", "Dr. Neha Sharma", "Student Affairs & Cultural Lead", "Information Technology", "COORD-EMP-004", "+91 98204 45674"),
            ("coord5@itsa.edu", "Prof. Vikram Joshi", "Cloud & Infrastructure Coordinator", "Artificial Intelligence & Data Science", "COORD-EMP-005", "+91 98205 56785")
        ]
        coordinators = []
        for email, full_name, designation, dept, emp_id, phone in coordinator_specs:
            u = User(
                email=email,
                full_name=full_name,
                role="COORDINATOR",
                is_active=True
            )
            u.set_password("Coord#2026")
            db.session.add(u)
            db.session.flush()

            cp = CoordinatorProfile(
                user_id=u.id,
                employee_id=emp_id,
                designation=designation,
                department=dept,
                phone=phone
            )
            db.session.add(cp)
            coordinators.append(u)
            print(f"  [COORDINATOR] {email:23s} / Coord#2026          -> {full_name} ({dept})")

        # 5c. 5 Students
        student_specs = [
            ("student1@itsa.edu", "Aarav Sharma", "ST2026001", "Information Technology", 3,
             "Full-Stack Developer and Cloud Computing enthusiast. Active ITSA technical contributor.",
             "Python, Flask, Cloud Computing, Docker, REST APIs"),
            ("student2@itsa.edu", "Priya Patel", "ST2026002", "Computer Engineering", 2,
             "Passionate about competitive programming, data structures, and responsive web design.",
             "Data Structures, React, JavaScript, Competitive Programming"),
            ("student3@itsa.edu", "Rohan Kulkarni", "ST2026003", "Data Science", 4,
             "Senior year data science researcher focusing on machine learning, predictive modeling, and generative AI.",
             "Machine Learning, Python, Generative AI, Big Data, SQL"),
            ("student4@itsa.edu", "Ananya Deshmukh", "ST2026004", "Information Technology", 3,
             "UI/UX designer and frontend engineer passionate about accessible interfaces and student community platforms.",
             "UI/UX Design, Bootstrap, Web Accessibility, Mobile Apps"),
            ("student5@itsa.edu", "Aditya Verma", "ST2026005", "Artificial Intelligence & Data Science", 1,
             "First-year AI enthusiast eager to participate in hackathons, workshops, and departmental tech fests.",
             "Artificial Intelligence, Python, Linux, Open Source, Algorithms")
        ]
        students = []
        for email, full_name, roll, dept, yr, bio, interests in student_specs:
            u = User(
                email=email,
                full_name=full_name,
                role="STUDENT",
                is_active=True
            )
            u.set_password("Student@12345")
            db.session.add(u)
            db.session.flush()

            sp = StudentProfile(
                user_id=u.id,
                student_id=roll,
                department=dept,
                year_of_study=yr,
                bio=bio,
                interests=interests,
                total_points=0 # will be calculated accurately from point records
            )
            db.session.add(sp)
            students.append(u)
            print(f"  [STUDENT]     {email:23s} / Student@12345        -> {full_name} (Year {yr}, {dept})")

        db.session.commit()
        print(f"✅ User creation complete: Exactly 1 Admin, 5 Coordinators, 5 Students.")

        # ── 6. Create 5 Realistic Events ────────────────────────────────────
        print("\n── Creating 5 Core Events ─────────────────────────────────────")
        now = datetime.utcnow()
        events_spec = [
            {
                "title": "TechFest 2026",
                "description": "The premier annual technology festival of the Information Technology Department. Features technical symposiums, hackathon rounds, project showcases, and keynote speeches from leading industry engineers.",
                "category": cat_map["Technical"],
                "venue": venue_map["Main University Auditorium"],
                "start": now + timedelta(days=5, hours=9),
                "end": now + timedelta(days=6, hours=18),
                "deadline": now + timedelta(days=4, hours=23),
                "status": "REGISTRATION_OPEN",
                "max": 200,
                "tags": "TechFest,Hackathon,Coding,Innovation,ITSA",
                "coordinator": coordinators[0] # coord1
            },
            {
                "title": "CodeSprint 2026",
                "description": "An intensive competitive speed-coding challenge. Compete against the brightest minds to solve complex data structure and algorithm puzzles under strict time limits.",
                "category": cat_map["Competition"],
                "venue": venue_map["Advanced Computer Lab 1"],
                "start": now + timedelta(days=12, hours=10),
                "end": now + timedelta(days=12, hours=16),
                "deadline": now + timedelta(days=10, hours=18),
                "status": "REGISTRATION_OPEN",
                "max": 60,
                "tags": "CodeSprint,Algorithms,DataStructures,Python,CompetitiveProgramming",
                "coordinator": coordinators[1] # coord2
            },
            {
                "title": "AI & Machine Learning Masterclass",
                "description": "A comprehensive hands-on masterclass covering neural network architectures, predictive modeling with scikit-learn, and state-of-the-art Generative AI integrations using the Google Gemini SDK.",
                "category": cat_map["Workshop"],
                "venue": venue_map["Advanced Computer Lab 1"],
                "start": now - timedelta(days=4, hours=6),
                "end": now - timedelta(days=4, hours=1),
                "deadline": now - timedelta(days=6),
                "status": "COMPLETED",
                "max": 60,
                "tags": "AI,MachineLearning,Gemini,Python,DeepLearning",
                "coordinator": coordinators[2] # coord3
            },
            {
                "title": "Web Development Bootcamp",
                "description": "A full-day immersive bootcamp building scalable, production-ready web platforms with Python Flask, Bootstrap 5.3, SQLAlchemy ORM, and RESTful API architecture.",
                "category": cat_map["Workshop"],
                "venue": venue_map["Seminar Hall B"],
                "start": now - timedelta(days=10, hours=5),
                "end": now - timedelta(days=10, hours=1),
                "deadline": now - timedelta(days=12),
                "status": "COMPLETED",
                "max": 80,
                "tags": "WebDev,Flask,Bootstrap,JavaScript,REST",
                "coordinator": coordinators[3] # coord4
            },
            {
                "title": "Cloud Computing & DevOps Workshop",
                "description": "An interactive industry-oriented workshop covering Linux containers, Docker orchestration, microservices deployment, and automated CI/CD pipelines.",
                "category": cat_map["Seminar"],
                "venue": venue_map["Innovation & IoT Research Lab"],
                "start": now - timedelta(days=18, hours=4),
                "end": now - timedelta(days=18, hours=1),
                "deadline": now - timedelta(days=20),
                "status": "COMPLETED",
                "max": 40,
                "tags": "Cloud,DevOps,Docker,Kubernetes,CI/CD",
                "coordinator": coordinators[4] # coord5
            }
        ]

        created_events = []
        for esp in events_spec:
            ev = Event(
                title=esp["title"],
                description=esp["description"],
                category_id=esp["category"].id,
                venue_id=esp["venue"].id,
                start_datetime=esp["start"],
                end_datetime=esp["end"],
                registration_deadline=esp["deadline"],
                max_participants=esp["max"],
                current_registrations=0,
                status=esp["status"],
                tags=esp["tags"],
                created_by=admin.id
            )
            db.session.add(ev)
            db.session.flush()

            ec = EventCoordinator(
                event_id=ev.id,
                coordinator_id=esp["coordinator"].id,
                role_in_event="Lead Coordinator",
                assigned_by=admin.id
            )
            db.session.add(ec)
            created_events.append(ev)
            print(f"  [EVENT] #{ev.id} '{ev.title}' [{ev.status}] -> Assigned: {esp['coordinator'].full_name}")

        db.session.commit()

        # ── 7. Registrations, Digital QR Tickets, Attendance & Certificates ──
        print("\n── Processing Registrations, Tickets, Attendance & Certificates ─")
        # Ensure upload folders exist
        upload_base = os.path.abspath(app.config.get('UPLOAD_FOLDER', 'uploads'))
        for sub in ['tickets', 'certificates', 'profiles', 'events/posters']:
            os.makedirs(os.path.join(upload_base, sub), exist_ok=True)

        completed_events = [created_events[2], created_events[3], created_events[4]] # AI, WebDev, Cloud
        upcoming_events = [created_events[0], created_events[1]]                      # TechFest, CodeSprint

        total_regs = 0
        total_tickets = 0
        total_attendances = 0
        total_certificates = 0

        # 7a. Register all 5 students for the 3 Completed Events
        # All 5 students attended all 3 completed events -> 15 Attendances, 15 Certificates!
        for ev in completed_events:
            lead_coord = EventCoordinator.query.filter_by(event_id=ev.id).first()
            coord_user_id = lead_coord.coordinator_id if lead_coord else coordinators[0].id

            for idx, student in enumerate(students):
                reg_num = f"ITSA-{ev.id:02d}-2026-{(idx + 1):04d}"
                reg = EventRegistration(
                    event_id=ev.id,
                    user_id=student.id,
                    registration_number=reg_num,
                    status="CONFIRMED",
                    registered_at=ev.registration_deadline - timedelta(days=2, hours=idx)
                )
                db.session.add(reg)
                db.session.flush()
                total_regs += 1
                ev.current_registrations += 1

                # Generate Real Digital Ticket with QR code
                ticket = TicketService.generate_ticket(reg.id)
                total_tickets += 1

                # Record PRESENT Attendance
                scan_time = ev.start_datetime + timedelta(minutes=15 + idx * 3)
                att = Attendance(
                    event_id=ev.id,
                    user_id=student.id,
                    registration_id=reg.id,
                    ticket_id=ticket.id,
                    scanned_by=coord_user_id,
                    scanned_at=scan_time,
                    status="PRESENT",
                    notes="Seeded demo attendance - Verified PRESENT"
                )
                db.session.add(att)
                db.session.flush()
                total_attendances += 1

                # Generate Real ReportLab Vector PDF Certificate
                cert = CertificateService.generate_certificate(
                    user_id=student.id,
                    event_id=ev.id,
                    attendance_id=att.id,
                    certificate_type="PARTICIPATION"
                )
                total_certificates += 1

                # Points for attendance (+10) and registration (+3)
                p_reg = ItsaPoints(user_id=student.id, points=3, reason="REGISTRATION", related_event_id=ev.id, created_at=reg.registered_at)
                p_att = ItsaPoints(user_id=student.id, points=10, reason="ATTENDANCE", related_event_id=ev.id, created_at=scan_time)
                db.session.add_all([p_reg, p_att])

                # Notification: Certificate ready
                notif = Notification(
                    user_id=student.id,
                    type="CERTIFICATE_READY",
                    title=f"Certificate Ready: {ev.title}",
                    message=f"Congratulations {student.full_name}! Your verified certificate for {ev.title} is now available for download.",
                    related_event_id=ev.id,
                    is_read=False,
                    created_at=scan_time + timedelta(hours=1)
                )
                db.session.add(notif)

        # 7b. Register all 5 students for TechFest 2026 (Upcoming, Registration Open)
        techfest = created_events[0]
        for idx, student in enumerate(students):
            reg_num = f"ITSA-{techfest.id:02d}-2026-{(idx + 1):04d}"
            reg = EventRegistration(
                event_id=techfest.id,
                user_id=student.id,
                registration_number=reg_num,
                status="CONFIRMED",
                registered_at=now - timedelta(days=1, hours=idx)
            )
            db.session.add(reg)
            db.session.flush()
            total_regs += 1
            techfest.current_registrations += 1

            ticket = TicketService.generate_ticket(reg.id)
            total_tickets += 1

            p_reg = ItsaPoints(user_id=student.id, points=3, reason="REGISTRATION", related_event_id=techfest.id, created_at=reg.registered_at)
            db.session.add(p_reg)

            notif = Notification(
                user_id=student.id,
                type="EVENT_REGISTRATION",
                title=f"Registration Confirmed: TechFest 2026",
                message=f"You are successfully registered for TechFest 2026! Your digital QR ticket {ticket.ticket_code} is ready in My Tickets.",
                related_event_id=techfest.id,
                is_read=False,
                created_at=reg.registered_at
            )
            db.session.add(notif)

        # 7c. Register Students 1, 2, 3 for CodeSprint 2026 (Upcoming Competition)
        codesprint = created_events[1]
        for idx, student in enumerate(students[:3]):
            reg_num = f"ITSA-{codesprint.id:02d}-2026-{(idx + 1):04d}"
            reg = EventRegistration(
                event_id=codesprint.id,
                user_id=student.id,
                registration_number=reg_num,
                status="CONFIRMED",
                registered_at=now - timedelta(hours=12 + idx)
            )
            db.session.add(reg)
            db.session.flush()
            total_regs += 1
            codesprint.current_registrations += 1

            ticket = TicketService.generate_ticket(reg.id)
            total_tickets += 1

            p_reg = ItsaPoints(user_id=student.id, points=3, reason="REGISTRATION", related_event_id=codesprint.id, created_at=reg.registered_at)
            db.session.add(p_reg)

        db.session.commit()
        print(f"✅ Registrations created: {total_regs}")
        print(f"✅ Digital QR tickets generated: {total_tickets}")
        print(f"✅ Attendances recorded (All PRESENT): {total_attendances}")
        print(f"✅ Real PDF Certificates generated: {total_certificates}")

        # ── 8. Event Feedback & AI Sentiment ────────────────────────────────
        print("\n── Seeding Student Feedback & Sentiment Records ───────────────")
        feedbacks_data = [
            (completed_events[0].id, students[0].id, 5, 5, 5, 5, 5,
             "Exceptional AI masterclass! The hands-on deep dive into Gemini API and modern transformer architectures was brilliant.",
             "Please organize an advanced session covering multi-agent frameworks next semester.", "POSITIVE"),
            (completed_events[0].id, students[2].id, 5, 5, 4, 5, 5,
             "One of the best workshops organized by ITSA. Practical coding notebooks were well documented and easy to follow.",
             "Extending the Q&A session by 30 minutes would be wonderful.", "POSITIVE"),
            (completed_events[1].id, students[1].id, 5, 5, 5, 5, 5,
             "Comprehensive full-stack engineering session. The Flask architecture and Bootstrap UI walkthrough were clear and practical.",
             "Would love a follow-up session covering Redis caching and WebSockets.", "POSITIVE"),
            (completed_events[1].id, students[3].id, 4, 4, 4, 4, 4,
             "Great hands-on coding bootcamp. Really helped bridge theoretical concepts with real-world project deployment.",
             "More frontend component design exercises would be great.", "POSITIVE"),
            (completed_events[2].id, students[4].id, 5, 5, 5, 4, 5,
             "Outstanding DevOps insights! Learned Docker containerization and CI/CD pipelines directly from experienced faculty.",
             "Please conduct a 2-day Kubernetes intensive workshop.", "POSITIVE")
        ]

        total_feedbacks = 0
        for eid, uid, r, sr, or_, vr, cr, comment, sugg, sent in feedbacks_data:
            fb = Feedback(
                event_id=eid,
                user_id=uid,
                rating=r,
                speaker_rating=sr,
                organization_rating=or_,
                venue_rating=vr,
                content_rating=cr,
                content=comment,
                suggestions=sugg,
                ai_sentiment=sent,
                ai_keywords='["Hands-on", "Practical", "Excellent", "DevOps", "Gemini"]',
                submitted_at=now - timedelta(days=2)
            )
            db.session.add(fb)
            total_feedbacks += 1

            # Award +5 points for feedback
            p_fb = ItsaPoints(user_id=uid, points=5, reason="FEEDBACK", related_event_id=eid, created_at=fb.submitted_at)
            db.session.add(p_fb)

        print(f"✅ Seeded {total_feedbacks} feedback records with sentiment analysis.")

        # ── 9. Community Posts, Threaded Comments, 5 Reactions & Hashtags ───
        print("\n── Seeding Academic Community Social Feed ─────────────────────")
        # Hashtags
        tag_names = ["ITSA", "TechFest2026", "WebDev", "AI", "CloudDevOps", "CompetitiveCoding"]
        tag_objects = {}
        for tn in tag_names:
            h = Hashtag(name=tn, post_count=0)
            db.session.add(h)
            db.session.flush()
            tag_objects[tn] = h

        # Posts
        post1 = Post(
            user_id=students[0].id,
            content="Excited to participate in #TechFest2026! Our team is building a student engagement analytics dashboard. Looking for 1 collaborator with UI/UX experience. Reach out if interested! 🚀 #ITSA #WebDev",
            post_type="TEXT",
            event_id=techfest.id,
            created_at=now - timedelta(days=1, hours=4)
        )
        post2 = Post(
            user_id=coordinators[0].id,
            content="Official Announcement: Registrations for #TechFest2026 are now live! Featuring 4 tracks: AI Hackathon, Web Development, Cloud Architecture, and Competitive Coding. Reserve your spot today on the ITSA portal! 🎟️ #ITSA #TechFest2026",
            post_type="TEXT",
            event_id=techfest.id,
            created_at=now - timedelta(days=2)
        )
        post3 = Post(
            user_id=students[2].id,
            content="Just received my verified Certificate of Appreciation for the #AI & Machine Learning Masterclass! Huge thanks to Prof. Amit Deshmukh for the hands-on Gemini SDK walkthrough. 🎓✨ #ITSA",
            post_type="TEXT",
            event_id=completed_events[0].id,
            created_at=now - timedelta(days=3)
        )
        post4 = Post(
            user_id=students[1].id,
            content="The #WebDev Bootcamp was fantastic. Deployed our first full-stack Flask application with SQLite and ReportLab certificates. Looking forward to the next challenge! 💻 #ITSA #WebDev",
            post_type="TEXT",
            event_id=completed_events[1].id,
            created_at=now - timedelta(days=7)
        )
        posts = [post1, post2, post3, post4]
        db.session.add_all(posts)
        db.session.flush()

        # Link Hashtags
        for p, tlist in [(post1, ["ITSA", "TechFest2026", "WebDev"]),
                         (post2, ["ITSA", "TechFest2026"]),
                         (post3, ["ITSA", "AI"]),
                         (post4, ["ITSA", "WebDev"])]:
            for tname in tlist:
                th = tag_objects[tname]
                th.post_count += 1
                ph = PostHashtag(post_id=p.id, hashtag_id=th.id)
                db.session.add(ph)

        # Award points for posting (+2)
        for p in posts:
            db.session.add(ItsaPoints(user_id=p.user_id, points=2, reason="POST", created_at=p.created_at))

        # Threaded Comments & Replies
        c1 = Comment(
            post_id=post1.id,
            user_id=students[1].id,
            content="Hi Aarav! I would love to collaborate on the UI. I have experience with Bootstrap 5.3 and responsive mobile components.",
            created_at=post1.created_at + timedelta(minutes=45)
        )
        db.session.add(c1)
        db.session.flush()

        # Threaded reply to c1
        r1 = CommentReply(
            comment_id=c1.id,
            user_id=students[0].id,
            content="Awesome Priya! Let's connect tomorrow after lectures in Advanced Computer Lab 1.",
            mentioned_user_id=students[1].id,
            created_at=c1.created_at + timedelta(minutes=30)
        )
        c2 = Comment(
            post_id=post2.id,
            user_id=students[3].id,
            content="Registered for the WebDev track! Really excited for the project exhibition.",
            created_at=post2.created_at + timedelta(hours=3)
        )
        c3 = Comment(
            post_id=post3.id,
            user_id=students[4].id,
            content="The certificate design looks amazing Rohan, congratulations!",
            created_at=post3.created_at + timedelta(hours=2)
        )
        db.session.add_all([r1, c2, c3])

        # Award points for commenting (+1)
        for c in [c1, c2, c3]:
            db.session.add(ItsaPoints(user_id=c.user_id, points=1, reason="COMMENT", created_at=c.created_at))

        # Five Sentiment Reactions: LIKE, LOVE, CELEBRATE, INSIGHTFUL, SUPPORT
        reactions_data = [
            (post1.id, students[1].id, "LIKE"),
            (post1.id, students[3].id, "SUPPORT"),
            (post2.id, students[0].id, "INSIGHTFUL"),
            (post2.id, students[4].id, "LOVE"),
            (post3.id, students[0].id, "CELEBRATE"),
            (post3.id, coordinators[2].id, "LOVE"),
            (post4.id, students[2].id, "SUPPORT"),
            (post4.id, coordinators[3].id, "CELEBRATE")
        ]
        for pid, uid, rtype in reactions_data:
            pr = PostReaction(post_id=pid, user_id=uid, reaction_type=rtype)
            db.session.add(pr)

        print(f"✅ Seeded {len(posts)} posts, {len(tag_names)} hashtags, threaded comments, and all 5 reaction types.")

        # ── 10. AI Recommendations, Analysis & Admin Audit Logs ──────────────
        print("\n── Seeding AI Recommendations, Analytics & Audit Logs ─────────")
        recs_data = [
            (students[0].id, techfest.id, 0.94, "High alignment with your profile interests in Cloud Computing & Full-Stack Web Development."),
            (students[1].id, codesprint.id, 0.96, "Matches your demonstrated skills in Data Structures & Competitive Programming."),
            (students[2].id, codesprint.id, 0.89, "Recommended based on your interest in Algorithmic Optimization and Python."),
            (students[3].id, techfest.id, 0.91, "Recommended for UI/UX Design project showcase and Technical Symposium."),
            (students[4].id, techfest.id, 0.85, "Great foundational event for first-year engineering students exploring AI & Web tech.")
        ]
        for uid, eid, score, reason in recs_data:
            rec = AiRecommendation(user_id=uid, event_id=eid, score=score, reason=reason, model_version="v2.5")
            db.session.add(rec)

        # AI Analysis Records
        ai_a1 = AiAnalysis(
            analysis_type="FEEDBACK_SENTIMENT",
            related_id=completed_events[0].id,
            output_data={
                "summary": "AI & Machine Learning Masterclass received overwhelmingly positive sentiment (100% positive, 5.0/5 average rating). Key praise focused on hands-on Gemini notebooks.",
                "sentiment": "POSITIVE",
                "average_rating": 5.0,
                "confidence_score": 0.98
            },
            model_version="gemini-3.5-flash"
        )
        ai_a2 = AiAnalysis(
            analysis_type="FEEDBACK_SENTIMENT",
            related_id=completed_events[1].id,
            output_data={
                "summary": "Web Development Bootcamp received 98% positive sentiment rating. Students highlighted practical Flask and Bootstrap walkthroughs.",
                "sentiment": "POSITIVE",
                "average_rating": 4.8,
                "confidence_score": 0.95
            },
            model_version="gemini-3.5-flash"
        )
        db.session.add_all([ai_a1, ai_a2])

        # Admin Audit Logs
        audits_data = [
            (admin.id, "RESET_LOCAL_DATABASE", "SYSTEM", None, {"reason": "Authorized local database reset for professional demo presentation"}),
            (admin.id, "CREATE_EVENT", "EVENT", techfest.id, {"title": "TechFest 2026", "capacity": 200}),
            (admin.id, "ASSIGN_COORDINATOR", "COORDINATOR", coordinators[0].id, {"event": "TechFest 2026", "role": "Lead Coordinator"}),
            (admin.id, "VERIFY_ATTENDANCE", "EVENT", completed_events[0].id, {"status": "ALL_STUDENTS_PRESENT"}),
            (admin.id, "GENERATE_CERTIFICATES", "CERTIFICATE", None, {"event": "AI & Machine Learning Masterclass", "status": "COMPLETED"})
        ]
        for uid, action, etype, eid, details in audits_data:
            log = AuditLog(
                user_id=uid,
                action=action,
                entity_type=etype,
                entity_id=eid,
                details=details,
                ip_address="127.0.0.1",
                created_at=now - timedelta(hours=1)
            )
            db.session.add(log)

        db.session.commit()

        # ── 11. Recalculate Accurate Total Points on Student Profiles ────────
        print("\n── Recalculating Leaderboard Points for Student Profiles ──────")
        for s in students:
            total_pts = db.session.query(db.func.sum(ItsaPoints.points)).filter(ItsaPoints.user_id == s.id).scalar() or 0
            sp = StudentProfile.query.filter_by(user_id=s.id).first()
            if sp:
                sp.total_points = total_pts
                print(f"  Leaderboard: {s.full_name:18s} -> {total_pts} ITSA Points")

        db.session.commit()

        # ── 12. Verification & Summary Audit ────────────────────────────────
        print("\n" + "=" * 70)
        print("  DATABASE RESET & DEMO DATA GENERATION COMPLETE - VERIFICATION")
        print("=" * 70)
        
        v_admin = User.query.filter_by(role="ADMIN").count()
        v_coord = User.query.filter_by(role="COORDINATOR").count()
        v_student = User.query.filter_by(role="STUDENT").count()
        v_events = Event.query.count()
        v_regs = EventRegistration.query.count()
        v_tickets = EventTicket.query.count()
        v_att = Attendance.query.count()
        v_att_present = Attendance.query.filter_by(status="PRESENT").count()
        v_certs = Certificate.query.count()
        v_posts = Post.query.count()
        v_comments = Comment.query.count()
        v_reactions = PostReaction.query.count()
        v_points = ItsaPoints.query.count()
        v_notifs = Notification.query.count()
        v_feedback = Feedback.query.count()

        print(f"  Administrators   : {v_admin} (Expected: exactly 1)  {'✅' if v_admin == 1 else '❌'}")
        print(f"  Coordinators     : {v_coord} (Expected: exactly 5)  {'✅' if v_coord == 5 else '❌'}")
        print(f"  Students         : {v_student} (Expected: exactly 5)  {'✅' if v_student == 5 else '❌'}")
        print(f"  Events           : {v_events} (Expected: exactly 5)  {'✅' if v_events == 5 else '❌'}")
        print(f"  Registrations    : {v_regs}                          ✅")
        print(f"  Digital Tickets  : {v_tickets}                       ✅")
        print(f"  Attendance Total : {v_att}                           ✅")
        print(f"  Attendance PRESENT: {v_att_present} (100% PRESENT)   {'✅' if v_att == v_att_present else '❌'}")
        print(f"  Certificates (PDF): {v_certs} (Generated on disk)   ✅")
        print(f"  Community Posts  : {v_posts}                         ✅")
        print(f"  Comments/Replies : {v_comments + CommentReply.query.count()} ✅")
        print(f"  Reactions (5 types): {v_reactions}                   ✅")
        print(f"  ITSA Points Log  : {v_points}                        ✅")
        print(f"  Notifications    : {v_notifs}                        ✅")
        print(f"  Event Feedback   : {v_feedback}                      ✅")

        # Check physical existence of generated certificate PDFs
        missing_pdfs = 0
        all_certs = Certificate.query.all()
        for c in all_certs:
            pdf_path = CertificateService.get_pdf_full_path(c)
            if not pdf_path or not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                missing_pdfs += 1

        print(f"  Physical PDF Check : {len(all_certs) - missing_pdfs}/{len(all_certs)} Verified Valid on Disk {'✅' if missing_pdfs == 0 else '❌'}")

        print("=" * 70)
        return {
            "backup_path": backup_file_path,
            "total_deleted": total_deleted,
            "users": v_admin + v_coord + v_student,
            "admins": v_admin,
            "coordinators": v_coord,
            "students": v_student,
            "events": v_events,
            "registrations": v_regs,
            "tickets": v_tickets,
            "attendance": v_att,
            "attendance_present": v_att_present,
            "certificates": v_certs,
            "posts": v_posts,
            "missing_pdfs": missing_pdfs
        }

if __name__ == '__main__':
    run_reset_and_demo_seed()
