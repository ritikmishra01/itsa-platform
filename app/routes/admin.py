from flask import Blueprint, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User, StudentProfile, CoordinatorProfile
from app.models.report import Report
from app.models.post import Post
from app.models.comment import Comment
from app.models.audit import AuditLog
from app.services.analytics_service import AnalyticsService
from app.services.gamification_service import GamificationService
from app.utils.responses import success_response, error_response, paginated_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_email, validate_password

admin_bp = Blueprint('api_admin', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/analytics/overview', methods=['GET'])
@admin_required
def get_analytics_overview():
    data = AnalyticsService.get_admin_dashboard_metrics()
    return success_response(data)


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    role = request.args.get('role')
    search = request.args.get('search')

    query = User.query
    if role:
        query = query.filter_by(role=role)
    if search:
        query = query.filter(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return paginated_response([u.to_dict() for u in users], page, per_page, total)


@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@admin_required
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'ADMIN':
        return error_response("ADMIN_PROTECTION", "Cannot suspend an administrator account.", 400)

    user.is_suspended = True
    log = AuditLog(
        user_id=current_user.id,
        action="SUSPEND_USER",
        entity_type="User",
        entity_id=user_id,
        details={"suspended_email": user.email, "reason": request.json.get("reason", "Admin policy enforcement") if request.is_json else None}
    )
    db.session.add(log)
    db.session.commit()
    return success_response(user.to_dict(), f"User '{user.full_name}' suspended.")


@admin_bp.route('/users/<int:user_id>/unsuspend', methods=['POST'])
@admin_required
def unsuspend_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_suspended = False
    log = AuditLog(
        user_id=current_user.id,
        action="UNSUSPEND_USER",
        entity_type="User",
        entity_id=user_id,
        details={"unsuspended_email": user.email}
    )
    db.session.add(log)
    db.session.commit()
    return success_response(user.to_dict(), f"User '{user.full_name}' reactivated.")


@admin_bp.route('/coordinators', methods=['POST'])
@admin_required
def create_coordinator():
    data = request.get_json() if request.is_json else request.form.to_dict()
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    full_name = data.get('full_name', '').strip()
    employee_id = data.get('employee_id', '').strip()
    designation = data.get('designation', '').strip()
    department = data.get('department', '').strip()
    phone = data.get('phone', '').strip()

    if not email or not password or not full_name:
        return error_response("VALIDATION_ERROR", "Email, password, and full name are required.", 400)

    if not validate_email(email):
        return error_response("VALIDATION_ERROR", "Invalid email format.", 400)

    valid_pw, pw_msg = validate_password(password)
    if not valid_pw:
        return error_response("PASSWORD_ERROR", pw_msg, 400)

    if User.query.filter_by(email=email).first():
        return error_response("USER_EXISTS", "User with this email already exists.", 400)

    user = User(
        email=email,
        full_name=full_name,
        role='COORDINATOR',
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    coord_profile = CoordinatorProfile(
        user_id=user.id,
        employee_id=employee_id or None,
        designation=designation or 'Event Coordinator',
        department=department or 'ITSA',
        phone=phone or None
    )
    db.session.add(coord_profile)

    log = AuditLog(
        user_id=current_user.id,
        action="CREATE_COORDINATOR",
        entity_type="User",
        entity_id=user.id,
        details={"email": email, "name": full_name}
    )
    db.session.add(log)
    db.session.commit()
    return success_response(user.to_dict(), "Coordinator account created successfully.", 201)


@admin_bp.route('/reports', methods=['GET'])
@admin_required
def list_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return success_response([r.to_dict() for r in reports])


@admin_bp.route('/reports/<int:report_id>/resolve', methods=['POST'])
@admin_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    data = request.get_json() if request.is_json else request.form.to_dict()
    action = data.get('action', 'DISMISSED') # DISMISSED, REMOVE_POST, REMOVE_COMMENT, RESTORE_POST, RESTORE_COMMENT

    if action == 'REMOVE_POST' and report.reported_post_id:
        post = Post.query.get(report.reported_post_id)
        if post:
            post.is_active = False
            report.status = 'RESOLVED'
    elif action == 'RESTORE_POST' and report.reported_post_id:
        post = Post.query.get(report.reported_post_id)
        if post:
            post.is_active = True
            report.status = 'RESOLVED'
    elif action == 'REMOVE_COMMENT' and report.reported_comment_id:
        comment = Comment.query.get(report.reported_comment_id)
        if comment:
            comment.is_active = False
            report.status = 'RESOLVED'
    elif action == 'RESTORE_COMMENT' and report.reported_comment_id:
        comment = Comment.query.get(report.reported_comment_id)
        if comment:
            comment.is_active = True
            report.status = 'RESOLVED'
    else:
        report.status = 'DISMISSED'

    report.reviewed_by = current_user.id
    report.reviewed_at = db.func.now()
    db.session.commit()
    return success_response(report.to_dict(), f"Report status updated to {report.status}.")


@admin_bp.route('/users/student', methods=['POST'])
@admin_required
def create_student():
    data = request.get_json() if request.is_json else request.form.to_dict()
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    full_name = data.get('full_name', '').strip()
    student_id = data.get('student_id', '').strip()
    department = data.get('department', '').strip()
    year_of_study = int(data.get('year_of_study', 1))

    if not email or not password or not full_name or not student_id:
        return error_response("VALIDATION_ERROR", "Email, password, full name, and Student ID are required.", 400)

    if not validate_email(email):
        return error_response("VALIDATION_ERROR", "Invalid email format.", 400)

    valid_pw, pw_msg = validate_password(password)
    if not valid_pw:
        return error_response("PASSWORD_ERROR", pw_msg, 400)

    if User.query.filter_by(email=email).first():
        return error_response("USER_EXISTS", "User with this email already exists.", 400)

    if StudentProfile.query.filter_by(student_id=student_id).first():
        return error_response("STUDENT_ID_EXISTS", "Student ID is already registered.", 400)

    user = User(
        email=email,
        full_name=full_name,
        role='STUDENT',
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    sp = StudentProfile(
        user_id=user.id,
        student_id=student_id,
        department=department or 'Information Technology',
        year_of_study=year_of_study,
        total_points=0
    )
    db.session.add(sp)

    log = AuditLog(
        user_id=current_user.id,
        action="CREATE_STUDENT",
        entity_type="User",
        entity_id=user.id,
        details={"email": email, "name": full_name, "student_id": student_id}
    )
    db.session.add(log)
    db.session.commit()
    return success_response(user.to_dict(), "Student account created successfully.", 201)


@admin_bp.route('/notifications/broadcast', methods=['POST'])
@admin_required
def broadcast_notification():
    from app.services.notification_service import NotificationService
    data = request.get_json() if request.is_json else request.form.to_dict()
    title = data.get('title', '').strip()
    message = data.get('message', '').strip()
    audience = data.get('audience', 'ALL').strip().upper() # ALL, ALL_STUDENTS, ALL_COORDINATORS, ALL_USERS, DEPT, YEAR, EVENT
    dept = data.get('department')
    year = data.get('year')
    event_id = data.get('event_id')

    if not title or not message:
        return error_response("VALIDATION_ERROR", "Title and message are required.", 400)

    if audience in ('ALL_COORDINATORS', 'COORDINATORS'):
        query = User.query.filter_by(role='COORDINATOR', is_active=True)
    elif audience in ('ALL_USERS', 'EVERYONE'):
        query = User.query.filter_by(is_active=True)
    else: # ALL, ALL_STUDENTS, DEPT, YEAR, EVENT
        query = User.query.filter_by(role='STUDENT', is_active=True)
        if audience == 'DEPT' and dept:
            query = query.join(StudentProfile).filter(StudentProfile.department == dept)
        elif audience == 'YEAR' and year:
            query = query.join(StudentProfile).filter(StudentProfile.year_of_study == int(year))
        elif audience == 'EVENT' and event_id:
            from app.models.registration import EventRegistration
            user_ids = [r.user_id for r in EventRegistration.query.filter_by(event_id=int(event_id), status='CONFIRMED').all()]
            query = query.filter(User.id.in_(user_ids))

    target_users = query.all()
    count = 0
    for u in target_users:
        NotificationService.create_notification(
            user_id=u.id,
            notif_type='ANNOUNCEMENT',
            title=title,
            message=message,
            related_event_id=int(event_id) if (event_id and str(event_id).isdigit()) else None
        )
        count += 1

    log = AuditLog(
        user_id=current_user.id,
        action="BROADCAST_NOTIFICATION",
        entity_type="Notification",
        details={"title": title, "audience": audience, "recipients_count": count}
    )
    db.session.add(log)
    db.session.commit()
    return success_response({"sent_count": count}, f"Broadcast dispatched to {count} recipient(s).")


@admin_bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    from app.models.event import EventCategory
    data = request.get_json() if request.is_json else request.form.to_dict()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    icon = data.get('icon', 'bi-calendar-event').strip()

    if not name:
        return error_response("VALIDATION_ERROR", "Category name is required.", 400)

    if EventCategory.query.filter_by(name=name).first():
        return error_response("CATEGORY_EXISTS", "Category already exists.", 400)

    cat = EventCategory(name=name, description=description, icon=icon)
    db.session.add(cat)
    db.session.commit()
    return success_response(cat.to_dict(), "Category created successfully.", 201)


@admin_bp.route('/venues', methods=['POST'])
@admin_required
def create_venue():
    from app.models.event import Venue
    data = request.get_json() if request.is_json else request.form.to_dict()
    name = data.get('name', '').strip()
    capacity = int(data.get('capacity', 100))
    building = data.get('building', '').strip()
    room_number = data.get('room_number', '').strip()

    if not name:
        return error_response("VALIDATION_ERROR", "Venue name is required.", 400)

    venue = Venue(name=name, capacity=capacity, building=building, room_number=room_number)
    db.session.add(venue)
    db.session.commit()
    return success_response(venue.to_dict(), "Venue created successfully.", 201)


@admin_bp.route('/gallery/<int:gallery_id>', methods=['DELETE', 'POST'])
@admin_required
def delete_gallery_item(gallery_id):
    from app.models.gallery import EventGallery
    item = EventGallery.query.get_or_404(gallery_id)
    db.session.delete(item)
    db.session.commit()
    return success_response(None, "Media item deleted from gallery.")


@admin_bp.route('/gallery/upload', methods=['POST'])
@admin_required
def upload_gallery_media():
    from app.models.gallery import EventGallery
    from app.models.event import Event
    from app.utils.file_utils import save_uploaded_file, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS

    event_id = request.form.get('event_id')
    caption = request.form.get('caption', '').strip()
    is_featured = request.form.get('is_featured', False) in (True, 'true', '1', 'on')

    if not event_id:
        return error_response("VALIDATION_ERROR", "Event ID is required.", 400)

    event = Event.query.get_or_404(int(event_id))

    if 'file' not in request.files:
        return error_response("FILE_MISSING", "No file uploaded.", 400)

    file = request.files['file']
    try:
        allowed = ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS)
        file_path = save_uploaded_file(file, subfolder='gallery', allowed_extensions=allowed)
        if not file_path:
            return error_response("FILE_INVALID", "Failed to save media file.", 400)

        media_type = 'VIDEO' if file.filename.rsplit('.', 1)[-1].lower() in ALLOWED_VIDEO_EXTENSIONS else 'IMAGE'
        gallery_item = EventGallery(
            event_id=event.id,
            uploaded_by=current_user.id,
            file_path=file_path,
            media_type=media_type,
            caption=caption,
            is_featured=is_featured
        )
        db.session.add(gallery_item)
        db.session.commit()
        return success_response(gallery_item.to_dict(), "Media uploaded to event gallery successfully.", 201)
    except ValueError as e:
        return error_response("FILE_INVALID", str(e), 400)


@admin_bp.route('/posts/<int:post_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_post_active(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_active = not post.is_active
    db.session.commit()
    status_str = "restored" if post.is_active else "hidden"
    return success_response(post.to_dict(), f"Post {status_str} successfully.")


@admin_bp.route('/comments/<int:comment_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_comment_active(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.is_active = not comment.is_active
    db.session.commit()
    status_str = "restored" if comment.is_active else "hidden"
    return success_response(comment.to_dict(), f"Comment {status_str} successfully.")


@admin_bp.route('/reports/export/<report_type>', methods=['GET'])
@admin_required
def export_report_csv(report_type):
    import csv
    import io
    from flask import Response
    from app.models.event import Event
    from app.models.registration import EventRegistration
    from app.models.attendance import Attendance
    from app.models.certificate import Certificate
    from app.models.gamification import ItsaPoints

    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'events':
        writer.writerow(['Event ID', 'Title', 'Category', 'Venue', 'Start DateTime', 'Registrations', 'Capacity', 'Status'])
        for e in Event.query.all():
            writer.writerow([e.id, e.title, e.category.name if e.category else '', e.venue.name if e.venue else '', e.start_datetime.isoformat(), e.current_registrations, e.max_participants or 'Unlimited', e.status])
    elif report_type == 'registrations':
        writer.writerow(['Registration ID', 'Reg Number', 'Student Name', 'Student Email', 'Department', 'Event Title', 'Status', 'Registered At'])
        for r in EventRegistration.query.all():
            writer.writerow([r.id, r.registration_number, r.user.full_name, r.user.email, r.user.student_profile.department if r.user.student_profile else '', r.event.title, r.status, r.registered_at.isoformat()])
    elif report_type == 'attendance':
        writer.writerow(['Attendance ID', 'Student Name', 'Student ID', 'Department', 'Event Title', 'Ticket Code', 'Scanned At', 'Coordinator'])
        for a in Attendance.query.all():
            writer.writerow([a.id, a.student.full_name, a.student.student_profile.student_id if a.student.student_profile else '', a.student.student_profile.department if a.student.student_profile else '', a.event.title, a.ticket.ticket_code if a.ticket else '', a.scanned_at.isoformat(), a.coordinator.full_name if a.coordinator else ''])
    elif report_type == 'certificates':
        writer.writerow(['Certificate ID', 'Cert Code', 'Student Name', 'Student Email', 'Event Title', 'Issued At', 'Valid'])
        for c in Certificate.query.all():
            writer.writerow([c.id, c.certificate_code, c.user.full_name, c.user.email, c.event.title, c.issued_at.isoformat(), c.is_valid])
    elif report_type == 'points':
        writer.writerow(['Transaction ID', 'Student Name', 'Department', 'Points', 'Reason', 'Timestamp'])
        for p in ItsaPoints.query.order_by(ItsaPoints.created_at.desc()).all():
            writer.writerow([p.id, p.user.full_name, p.user.student_profile.department if p.user.student_profile else '', p.points, p.reason, p.created_at.isoformat()])
    elif report_type == 'users':
        writer.writerow(['User ID', 'Full Name', 'Email', 'Role', 'Department', 'Student/Emp ID', 'Points', 'Status'])
        for u in User.query.all():
            dept = u.student_profile.department if u.student_profile else (u.coordinator_profile.department if u.coordinator_profile else '')
            ident = u.student_profile.student_id if u.student_profile else (u.coordinator_profile.employee_id if u.coordinator_profile else '')
            pts = u.student_profile.total_points if u.student_profile else 0
            writer.writerow([u.id, u.full_name, u.email, u.role, dept, ident, pts, 'Active' if u.is_active and not u.is_suspended else 'Suspended'])
    else:
        return error_response("INVALID_REPORT", "Unknown report type.", 400)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=itsa_{report_type}_report.csv"}
    )
