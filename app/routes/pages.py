from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.event import Event, EventCategory, Venue, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import Feedback
from app.models.post import Post
from app.models.notification import Notification
from app.models.report import Report
from app.models.user import User, StudentProfile
from app.services.gamification_service import GamificationService
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import AIService
from app.utils.decorators import coordinator_required, admin_required, student_required

pages_bp = Blueprint('pages', __name__)

# -------------------------------------------------------------
# Static Uploads Serving
# -------------------------------------------------------------
@pages_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    import os
    from flask import Response
    clean_filename = filename.replace('\\', '/').lstrip('/')
    if clean_filename.startswith('uploads/'):
        clean_filename = clean_filename[len('uploads/'):]

    upload_dir = current_app.config['UPLOAD_FOLDER']
    full_path = os.path.join(upload_dir, clean_filename)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        placeholder_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">
            <rect width="400" height="250" fill="#f8f9fa"/>
            <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#5f6368">Image Unavailable</text>
            <text x="50%" y="60%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#9aa0a6">ITSA Media Repository</text>
        </svg>"""
        return Response(placeholder_svg, mimetype="image/svg+xml")

    return send_from_directory(upload_dir, clean_filename)


@pages_bp.route('/logout')
def logout():
    from flask_login import logout_user
    from flask import session, current_app
    logout_user()
    session.clear()
    flash("You have been logged out successfully.", "info")
    response = redirect(url_for('pages.login_page'))

    # Explicitly clear both session and remember cookies
    cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', 'remember_token')
    session_cookie = current_app.config.get('SESSION_COOKIE_NAME', 'session')
    rem_path = current_app.config.get('REMEMBER_COOKIE_PATH', '/')
    sess_path = current_app.config.get('SESSION_COOKIE_PATH', '/')
    rem_domain = current_app.config.get('REMEMBER_COOKIE_DOMAIN')
    sess_domain = current_app.config.get('SESSION_COOKIE_DOMAIN')

    response.delete_cookie(cookie_name, path=rem_path, domain=rem_domain)
    response.delete_cookie(session_cookie, path=sess_path, domain=sess_domain)
    # Also delete root path fallback
    response.delete_cookie('remember_token', path='/')
    response.delete_cookie('session', path='/')
    return response

# -------------------------------------------------------------
# Health Check Endpoint (Phase 1 Requirement)
# -------------------------------------------------------------
@pages_bp.route('/health', methods=['GET'])
def health_check():
    from flask import jsonify
    return jsonify({
        "status": "healthy",
        "service": "ITSA AI-Powered Platform",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# -------------------------------------------------------------
# Public Pages
# -------------------------------------------------------------
@pages_bp.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('pages.login_page'))
    if current_user.role == 'ADMIN':
        return redirect(url_for('pages.admin_dashboard'))
    elif current_user.role == 'COORDINATOR':
        return redirect(url_for('pages.coordinator_dashboard'))
    return redirect(url_for('pages.student_dashboard'))


@pages_bp.route('/events')
def events_page():
    category_id = request.args.get('category_id')
    search = request.args.get('search')
    archive = request.args.get('archive', 'false').lower() == 'true'

    query = Event.query
    if archive:
        query = query.filter(Event.status.in_(['COMPLETED', 'CANCELLED']))
    else:
        query = query.filter(Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'ONGOING']))

    if category_id:
        query = query.filter_by(category_id=int(category_id))
    if search:
        query = query.filter(Event.title.ilike(f"%{search.strip()}%") | Event.description.ilike(f"%{search.strip()}%"))

    events = query.order_by(Event.start_datetime.desc() if archive else Event.start_datetime.asc()).all()
    categories = EventCategory.query.all()

    return render_template('public/events.html', events=events, categories=categories, current_cat=category_id, search=search, is_archive=archive)


@pages_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    user_registered = False
    user_attended = False
    user_ticket = None

    if current_user.is_authenticated and current_user.is_student:
        reg = EventRegistration.query.filter_by(event_id=event.id, user_id=current_user.id, status='CONFIRMED').first()
        if reg:
            user_registered = True
            user_ticket = reg.ticket
        att = Attendance.query.filter_by(event_id=event.id, user_id=current_user.id, status='PRESENT').first()
        if att:
            user_attended = True

    return render_template('public/event_detail.html', event=event, user_registered=user_registered, user_attended=user_attended, user_ticket=user_ticket)


@pages_bp.route('/login')
def login_page():
    if current_user.is_authenticated:
        if current_user.role == 'ADMIN':
            return redirect(url_for('pages.admin_dashboard'))
        elif current_user.role == 'COORDINATOR':
            return redirect(url_for('pages.coordinator_dashboard'))
        return redirect(url_for('pages.student_dashboard'))
    return render_template('auth/login.html')


@pages_bp.route('/register')
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('pages.student_dashboard'))
    return render_template('auth/register.html')


@pages_bp.route('/certificates/verify')
@pages_bp.route('/certificates/verify/<string:code>')
def verify_certificate_page(code=None):
    cert_data = None
    err_msg = None
    if code:
        from app.services.certificate_service import CertificateService
        cert_data, err_msg = CertificateService.verify_certificate(code)
    return render_template('public/verify_cert.html', cert_data=cert_data, err_msg=err_msg, code=code)


# -------------------------------------------------------------
# Student Pages
# -------------------------------------------------------------
@pages_bp.route('/dashboard')
@pages_bp.route('/student/dashboard')
@student_required
def student_dashboard():
    # Upcoming registered events
    my_regs = EventRegistration.query.filter_by(user_id=current_user.id, status='CONFIRMED').all()
    reg_events = [r.event for r in my_regs if r.event.status in ('REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'ONGOING')]

    # AI Recommendations
    recs = AIService.recommend_events(current_user, top_n=3)

    # Engagement Score
    score, breakdown = AIService.calculate_engagement_score(current_user)

    # Counts
    att_count = Attendance.query.filter_by(user_id=current_user.id, status='PRESENT').count()
    cert_count = Certificate.query.filter_by(user_id=current_user.id, is_valid=True).count()

    return render_template('student/dashboard.html',
                           upcoming_events=reg_events,
                           recommendations=recs,
                           engagement_score=score,
                           engagement_breakdown=breakdown,
                           att_count=att_count,
                           cert_count=cert_count)


@pages_bp.route('/feed')
@login_required
def social_feed():
    hashtag = request.args.get('hashtag')
    return render_template('student/feed.html', hashtag=hashtag)


@pages_bp.route('/profile')
@pages_bp.route('/student/profile')
@login_required
def profile_page():
    return render_template('student/profile.html')


@pages_bp.route('/my-events')
@pages_bp.route('/student/events')
@student_required
def my_events():
    regs = EventRegistration.query.filter_by(user_id=current_user.id).order_by(EventRegistration.registered_at.desc()).all()
    return render_template('student/my_events.html', registrations=regs)


@pages_bp.route('/my-tickets')
@pages_bp.route('/tickets')
@pages_bp.route('/student/tickets')
@student_required
def my_tickets():
    regs = EventRegistration.query.filter_by(user_id=current_user.id, status='CONFIRMED').all()
    tickets = [r.ticket for r in regs if r.ticket and r.ticket.is_valid]
    return render_template('student/tickets.html', tickets=tickets)


@pages_bp.route('/my-attendance')
@pages_bp.route('/attendance')
@pages_bp.route('/student/attendance')
@student_required
def my_attendance():
    atts = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.scanned_at.desc()).all()
    return render_template('student/attendance.html', attendances=atts)


@pages_bp.route('/my-certificates')
@pages_bp.route('/certificates')
@pages_bp.route('/student/certificates')
@student_required
def my_certificates():
    certs = Certificate.query.filter_by(user_id=current_user.id, is_valid=True).order_by(Certificate.issued_at.desc()).all()
    return render_template('student/certificates.html', certificates=certs)


@pages_bp.route('/leaderboard')
def leaderboard_page():
    dept = request.args.get('department')
    year = request.args.get('year')
    year_int = int(year) if year else None
    board = GamificationService.get_leaderboard(limit=50, department=dept, year_of_study=year_int)
    return render_template('student/leaderboard.html', leaderboard=board, current_dept=dept, current_year=year)


@pages_bp.route('/chatbot')
@student_required
def chatbot_page():
    return render_template('student/chatbot.html')


@pages_bp.route('/notifications')
@pages_bp.route('/student/notifications')
@pages_bp.route('/coordinator/notifications')
@login_required
def notifications_page():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('student/notifications.html', notifications=notifs)


# -------------------------------------------------------------
# Coordinator Pages
# -------------------------------------------------------------
@pages_bp.route('/coordinator/dashboard')
@coordinator_required
def coordinator_dashboard():
    if current_user.role == 'ADMIN':
        assigned_events = Event.query.order_by(Event.start_datetime.desc()).all()
    else:
        coords = EventCoordinator.query.filter_by(coordinator_id=current_user.id).all()
        assigned_events = [c.event for c in coords if c.event]

    return render_template('coordinator/dashboard.html', events=assigned_events)


@pages_bp.route('/coordinator/events/<int:event_id>/scan')
@coordinator_required
def coordinator_scanner(event_id):
    event = Event.query.get_or_404(event_id)
    recent_attendances = Attendance.query.filter_by(event_id=event.id).order_by(Attendance.scanned_at.desc()).limit(10).all()
    return render_template('coordinator/scanner.html', event=event, recent_attendances=recent_attendances)


@pages_bp.route('/coordinator/events/<int:event_id>/attendance')
@coordinator_required
def coordinator_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    records = Attendance.query.filter_by(event_id=event.id).order_by(Attendance.scanned_at.desc()).all()
    return render_template('coordinator/attendance.html', event=event, records=records)


@pages_bp.route('/coordinator/events/<int:event_id>/feedback')
@coordinator_required
def coordinator_feedback(event_id):
    event = Event.query.get_or_404(event_id)
    feedbacks = Feedback.query.filter_by(event_id=event.id).order_by(Feedback.submitted_at.desc()).all()
    metrics = AnalyticsService.get_coordinator_event_metrics(event_id)
    return render_template('coordinator/feedback.html', event=event, feedbacks=feedbacks, metrics=metrics)


# -------------------------------------------------------------
# Admin Pages
# -------------------------------------------------------------
@pages_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    from app.models.post import Post
    from app.models.registration import EventRegistration
    from app.models.attendance import Attendance
    from app.models.certificate import Certificate
    from app.models.audit import AuditLog

    metrics = AnalyticsService.get_admin_dashboard_metrics()
    
    # Extended metrics
    total_coordinators = User.query.filter_by(role='COORDINATOR').count()
    upcoming_events_count = Event.query.filter(
        Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN', 'ONGOING']),
        Event.start_datetime >= datetime.utcnow()
    ).count()
    total_certificates = Certificate.query.count()
    total_posts = Post.query.count()

    extended_metrics = {
        **metrics,
        'total_coordinators': total_coordinators,
        'upcoming_events_count': upcoming_events_count,
        'total_certificates': total_certificates,
        'total_posts': total_posts
    }

    # Upcoming events list with coordinators
    upcoming_events = Event.query.filter(
        Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN', 'ONGOING', 'DRAFT'])
    ).order_by(Event.start_datetime.asc()).limit(6).all()

    # Recent activity stream
    recent_activities = []
    # 1. Audit logs
    for log in AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all():
        recent_activities.append({
            'user': log.user.full_name if log.user else 'System',
            'action': log.action.replace('_', ' ').title(),
            'timestamp': log.created_at,
            'icon': 'bi-shield-check',
            'badge': 'bg-primary'
        })
    # 2. Recent registrations
    for reg in EventRegistration.query.order_by(EventRegistration.registered_at.desc()).limit(5).all():
        recent_activities.append({
            'user': reg.user.full_name,
            'action': f"Registered for '{reg.event.title}'",
            'timestamp': reg.registered_at,
            'icon': 'bi-ticket-perforated',
            'badge': 'bg-info'
        })
    # 3. Recent attendances
    for att in Attendance.query.order_by(Attendance.scanned_at.desc()).limit(5).all():
        recent_activities.append({
            'user': att.student.full_name,
            'action': f"Attended '{att.event.title}' (Verified)",
            'timestamp': att.scanned_at,
            'icon': 'bi-patch-check',
            'badge': 'bg-success'
        })
    
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]

    return render_template(
        'admin/dashboard.html',
        metrics=extended_metrics,
        upcoming_events=upcoming_events,
        recent_activities=recent_activities,
        active_page='dashboard'
    )


@pages_bp.route('/admin/users')
@admin_required
def admin_users():
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '')
    dept_filter = request.args.get('department', '')

    query = User.query
    if search:
        query = query.filter(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    if role_filter:
        query = query.filter_by(role=role_filter)

    users = query.order_by(User.created_at.desc()).all()
    students = [u for u in users if u.role == 'STUDENT']
    coordinators = [u for u in users if u.role == 'COORDINATOR']

    departments = ['Computer Science', 'Information Technology', 'Data Science', 'Artificial Intelligence', 'Cybersecurity', 'Electronics']

    return render_template(
        'admin/users.html',
        users=users,
        students=students,
        coordinators=coordinators,
        departments=departments,
        search=search,
        role_filter=role_filter,
        dept_filter=dept_filter,
        active_page='users'
    )


@pages_bp.route('/admin/events')
@admin_required
def admin_events():
    cat_id = request.args.get('category_id')
    status_filter = request.args.get('status')
    search = request.args.get('search', '').strip()

    query = Event.query
    if cat_id:
        query = query.filter_by(category_id=int(cat_id))
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    events = query.order_by(Event.start_datetime.desc()).all()
    categories = EventCategory.query.all()
    venues = Venue.query.all()
    coordinators = User.query.filter_by(role='COORDINATOR', is_active=True).all()

    return render_template(
        'admin/events.html',
        events=events,
        categories=categories,
        venues=venues,
        coordinators=coordinators,
        search=search,
        cat_id=cat_id,
        status_filter=status_filter,
        active_page='events'
    )


@pages_bp.route('/admin/coordinators')
@admin_required
def admin_coordinators():
    coordinators = User.query.filter_by(role='COORDINATOR').order_by(User.created_at.desc()).all()
    return render_template('admin/coordinators.html', coordinators=coordinators, active_page='users')


@pages_bp.route('/admin/registrations')
@admin_required
def admin_registrations():
    from app.models.registration import EventRegistration
    event_id = request.args.get('event_id')
    status = request.args.get('status')
    dept = request.args.get('department')

    query = EventRegistration.query
    if event_id:
        query = query.filter_by(event_id=int(event_id))
    if status:
        query = query.filter_by(status=status)
    if dept:
        query = query.join(User).join(StudentProfile).filter(StudentProfile.department == dept)

    registrations = query.order_by(EventRegistration.registered_at.desc()).all()
    events = Event.query.all()
    departments = ['Computer Science', 'Information Technology', 'Data Science', 'Artificial Intelligence', 'Cybersecurity', 'Electronics']

    confirmed_count = sum(1 for r in registrations if r.status == 'CONFIRMED')
    cancelled_count = sum(1 for r in registrations if r.status == 'CANCELLED')

    return render_template(
        'admin/registrations.html',
        registrations=registrations,
        events=events,
        departments=departments,
        confirmed_count=confirmed_count,
        cancelled_count=cancelled_count,
        total_count=len(registrations),
        active_page='registrations'
    )


@pages_bp.route('/admin/attendance')
@admin_required
def admin_attendance():
    from app.models.attendance import Attendance
    from app.models.registration import EventRegistration
    event_id = request.args.get('event_id')

    query = Attendance.query
    if event_id:
        query = query.filter_by(event_id=int(event_id))

    records = query.order_by(Attendance.scanned_at.desc()).all()
    events = Event.query.all()

    total_registered = EventRegistration.query.filter_by(status='CONFIRMED').count()
    total_attended = len(records)
    attendance_rate = round((total_attended / total_registered * 100) if total_registered > 0 else 0, 1)

    return render_template(
        'admin/attendance.html',
        records=records,
        events=events,
        total_registered=total_registered,
        total_attended=total_attended,
        attendance_rate=attendance_rate,
        active_page='attendance'
    )


@pages_bp.route('/admin/certificates')
@admin_required
def admin_certificates():
    from app.models.certificate import Certificate
    event_id = request.args.get('event_id')

    query = Certificate.query
    if event_id:
        query = query.filter_by(event_id=int(event_id))

    certificates = query.order_by(Certificate.issued_at.desc()).all()
    events = Event.query.all()

    return render_template(
        'admin/certificates.html',
        certificates=certificates,
        events=events,
        total_count=len(certificates),
        active_page='certificates'
    )


@pages_bp.route('/admin/community')
@pages_bp.route('/admin/moderation')
@admin_required
def admin_community():
    from app.models.post import Post, PostReaction
    from app.models.comment import Comment

    posts = Post.query.order_by(Post.created_at.desc()).all()
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    reports = Report.query.order_by(Report.created_at.desc()).all()
    reactions_count = PostReaction.query.count()

    pending_reports = [r for r in reports if r.status == 'PENDING']

    return render_template(
        'admin/community.html',
        posts=posts,
        comments=comments,
        reports=reports,
        pending_reports=pending_reports,
        reactions_count=reactions_count,
        active_page='community'
    )


@pages_bp.route('/admin/gallery')
@admin_required
def admin_gallery():
    from app.models.gallery import EventGallery
    gallery_items = EventGallery.query.order_by(EventGallery.uploaded_at.desc()).all()
    events = Event.query.all()
    return render_template('admin/gallery.html', gallery_items=gallery_items, events=events, active_page='gallery')


@pages_bp.route('/admin/notifications')
@admin_required
def admin_notifications():
    from app.models.notification import Notification
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(50).all()
    events = Event.query.filter(Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN', 'ONGOING'])).all()
    departments = ['Computer Science', 'Information Technology', 'Data Science', 'Artificial Intelligence', 'Cybersecurity', 'Electronics']
    return render_template('admin/notifications.html', notifications=notifications, events=events, departments=departments, active_page='notifications')


@pages_bp.route('/admin/gamification')
@admin_required
def admin_gamification():
    from app.models.gamification import ItsaPoints
    leaderboard = GamificationService.get_leaderboard(limit=50)
    recent_transactions = ItsaPoints.query.order_by(ItsaPoints.created_at.desc()).limit(30).all()
    total_points_distributed = db.session.query(db.func.sum(ItsaPoints.points)).scalar() or 0
    active_students_count = StudentProfile.query.filter(StudentProfile.total_points > 0).count()
    users = User.query.filter_by(role='STUDENT', is_active=True).all()

    return render_template(
        'admin/gamification.html',
        leaderboard=leaderboard,
        recent_transactions=recent_transactions,
        total_points=total_points_distributed,
        active_students=active_students_count,
        users=users,
        active_page='gamification'
    )


@pages_bp.route('/admin/ai-center')
@admin_required
def admin_ai_center():
    events = Event.query.all()
    students = User.query.filter_by(role='STUDENT', is_active=True).limit(20).all()
    reports = Report.query.filter_by(status='PENDING').all()
    return render_template('admin/ai_center.html', events=events, students=students, reports=reports, active_page='ai_center')


@pages_bp.route('/admin/analytics')
@admin_required
def admin_analytics():
    metrics = AnalyticsService.get_admin_dashboard_metrics()
    return render_template('admin/analytics.html', metrics=metrics, active_page='analytics')


@pages_bp.route('/admin/reports')
@admin_required
def admin_reports():
    events_count = Event.query.count()
    from app.models.registration import EventRegistration
    from app.models.attendance import Attendance
    from app.models.certificate import Certificate
    from app.models.gamification import ItsaPoints

    counts = {
        'events': events_count,
        'registrations': EventRegistration.query.count(),
        'attendance': Attendance.query.count(),
        'certificates': Certificate.query.count(),
        'points': ItsaPoints.query.count(),
        'users': User.query.count()
    }
    return render_template('admin/reports.html', counts=counts, active_page='reports')


@pages_bp.route('/admin/audit-logs')
@admin_required
def admin_audit_logs():
    from app.models.audit import AuditLog
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', logs=logs, active_page='audit_logs')


@pages_bp.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html', active_page='settings')


@pages_bp.route('/admin/search')
@admin_required
def admin_search():
    from app.models.registration import EventRegistration
    from app.models.ticket import EventTicket
    from app.models.certificate import Certificate
    from app.models.post import Post

    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('pages.admin_dashboard'))

    students = User.query.filter(User.role == 'STUDENT', (User.full_name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%"))).all()
    coordinators = User.query.filter(User.role == 'COORDINATOR', (User.full_name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%"))).all()
    events = Event.query.filter(Event.title.ilike(f"%{q}%") | Event.description.ilike(f"%{q}%")).all()
    registrations = EventRegistration.query.filter(EventRegistration.registration_number.ilike(f"%{q}%")).all()
    tickets = EventTicket.query.filter(EventTicket.ticket_code.ilike(f"%{q}%")).all()
    certificates = Certificate.query.filter(Certificate.certificate_code.ilike(f"%{q}%")).all()
    posts = Post.query.filter(Post.content.ilike(f"%{q}%")).all()

    total_matches = len(students) + len(coordinators) + len(events) + len(registrations) + len(tickets) + len(certificates) + len(posts)

    return render_template(
        'admin/search.html',
        search_query=q,
        total_matches=total_matches,
        students=students,
        coordinators=coordinators,
        events=events,
        registrations=registrations,
        tickets=tickets,
        certificates=certificates,
        posts=posts,
        active_page='search'
    )

