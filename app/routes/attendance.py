from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.attendance_service import AttendanceService
from app.utils.responses import success_response, error_response
from app.utils.decorators import coordinator_required, admin_required

attendance_bp = Blueprint('api_attendance', __name__, url_prefix='/api/v1/attendance')

@attendance_bp.route('/scan', methods=['POST'])
@coordinator_required
def scan_attendance():
    """
    CRITICAL: The Coordinator scans the student's QR code.
    Input: ticket_code, event_id
    """
    data = request.get_json() if request.is_json else request.form.to_dict()
    ticket_code = data.get('ticket_code')
    event_id = data.get('event_id')
    notes = data.get('notes')

    if not ticket_code or not event_id:
        return error_response("ATT_VALIDATION_ERROR", "ticket_code and event_id are required.", 400)

    try:
        attendance = AttendanceService.scan_attendance(
            coordinator_user=current_user,
            event_id=int(event_id),
            ticket_code=ticket_code.strip(),
            notes=notes
        )
        return success_response(attendance.to_dict(), f"Attendance confirmed for {attendance.student.full_name} (+10 points).")
    except ValueError as e:
        return error_response("ATT_SCAN_FAILED", str(e), 400)
    except Exception as e:
        return error_response("SYS_ERROR", f"Attendance error: {str(e)}", 500)


@attendance_bp.route('/event/<int:event_id>', methods=['GET'])
@coordinator_required
def get_event_attendance(event_id):
    records = AttendanceService.get_event_attendance(event_id)
    return success_response([r.to_dict() for r in records])


@attendance_bp.route('/<int:attendance_id>/override', methods=['PUT', 'POST'])
@admin_required
def override_attendance(attendance_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    status = data.get('status', 'PRESENT')
    notes = data.get('notes')

    try:
        att = AttendanceService.manual_override(attendance_id, status, notes)
        return success_response(att.to_dict(), "Attendance record updated.")
    except ValueError as e:
        return error_response("ATT_OVERRIDE_ERROR", str(e), 400)
