from datetime import datetime
from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.event import Event, EventCategory, Venue, EventCoordinator
from app.services.event_service import EventService
from app.services.registration_service import RegistrationService
from app.utils.responses import success_response, error_response, paginated_response
from app.utils.decorators import coordinator_required, admin_required
from app.utils.file_utils import save_uploaded_file, ALLOWED_IMAGE_EXTENSIONS

events_bp = Blueprint('api_events', __name__, url_prefix='/api/v1/events')

@events_bp.route('', methods=['GET'])
def list_events():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category_id = request.args.get('category_id')
    status = request.args.get('status')
    search = request.args.get('search')
    archive = request.args.get('archive', 'false').lower() == 'true'

    query = Event.query

    if not current_user.is_authenticated or current_user.is_student:
        # Public & students only see non-draft events
        if archive:
            query = query.filter(Event.status.in_(['COMPLETED', 'CANCELLED']))
        else:
            query = query.filter(Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'ONGOING']))
    else:
        if status:
            query = query.filter_by(status=status)

    if category_id:
        query = query.filter_by(category_id=int(category_id))

    if search:
        query = query.filter(Event.title.ilike(f"%{search.strip()}%") | Event.description.ilike(f"%{search.strip()}%"))

    query = query.order_by(Event.start_datetime.desc() if archive else Event.start_datetime.asc())

    total = query.count()
    events = query.offset((page - 1) * per_page).limit(per_page).all()

    return paginated_response([e.to_dict() for e in events], page, per_page, total)


@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return success_response(event.to_dict())


@events_bp.route('', methods=['POST'])
@coordinator_required
def create_event():
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    poster_path = None
    if 'poster_image' in request.files:
        try:
            poster_path = save_uploaded_file(request.files['poster_image'], subfolder='events/posters', allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
        except ValueError as e:
            return error_response("FILE_INVALID", str(e), 400)

    try:
        event = EventService.create_event(current_user.id, data, poster_path=poster_path)
        return success_response(event.to_dict(), "Event created successfully.", 201)
    except ValueError as e:
        return error_response("EVENT_VALIDATION_ERROR", str(e), 400)


@events_bp.route('/<int:event_id>', methods=['PUT', 'POST'])
@coordinator_required
def update_event(event_id):
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    poster_path = None
    if 'poster_image' in request.files:
        try:
            poster_path = save_uploaded_file(request.files['poster_image'], subfolder='events/posters', allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
        except ValueError as e:
            return error_response("FILE_INVALID", str(e), 400)

    try:
        event = EventService.update_event(event_id, data, poster_path=poster_path)
        return success_response(event.to_dict(), "Event updated successfully.")
    except ValueError as e:
        return error_response("EVENT_UPDATE_ERROR", str(e), 400)


@events_bp.route('/<int:event_id>/status', methods=['PUT', 'POST'])
@coordinator_required
def change_status(event_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    new_status = data.get('status')
    if not new_status:
        return error_response("EVENT_STATUS_ERROR", "New status required.", 400)

    try:
        event = EventService.change_status(event_id, new_status)
        return success_response(event.to_dict(), f"Event status updated to {new_status}.")
    except ValueError as e:
        return error_response("EVENT_STATUS_ERROR", str(e), 400)


@events_bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    if current_user.role != 'STUDENT':
        return error_response("AUTH_INSUFFICIENT_ROLE", "Only students can register for events.", 403)

    try:
        registration = RegistrationService.register_student(event_id, current_user)
        return success_response(registration.to_dict(), "Successfully registered for event!", 201)
    except ValueError as e:
        return error_response("REGISTRATION_ERROR", str(e), 400)


@events_bp.route('/<int:event_id>/registrations', methods=['GET'])
@coordinator_required
def get_registrations(event_id):
    event = Event.query.get_or_404(event_id)
    regs = event.registrations.order_by(EventRegistration.registered_at.desc()).all()
    return success_response([r.to_dict() for r in regs])


@events_bp.route('/<int:event_id>/coordinators', methods=['POST'])
@admin_required
def assign_coordinator(event_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    coordinator_id = data.get('coordinator_id')
    role_in_event = data.get('role_in_event', 'Support')

    if not coordinator_id:
        return error_response("VALIDATION_ERROR", "Coordinator ID required.", 400)

    try:
        assignment = EventService.assign_coordinator(event_id, int(coordinator_id), current_user.id, role_in_event)
        return success_response(assignment.to_dict(), "Coordinator assigned successfully.")
    except Exception as e:
        return error_response("ASSIGNMENT_ERROR", str(e), 400)
