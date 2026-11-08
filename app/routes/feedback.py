from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.event import Event, EventCoordinator
from app.services.feedback_service import FeedbackService
from app.utils.responses import success_response, error_response
from app.utils.decorators import coordinator_required

feedback_bp = Blueprint('api_feedback', __name__, url_prefix='/api/v1/feedback')

@feedback_bp.route('', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json() if request.is_json else request.form.to_dict()
    event_id = data.get('event_id')
    rating = data.get('rating')

    if not event_id or rating is None or rating == '':
        return error_response("VALIDATION_ERROR", "Event ID and rating (1-5) are required.", 400)

    try:
        fb, is_new = FeedbackService.submit_feedback(
            user_id=current_user.id,
            event_id=int(event_id),
            rating=rating,
            content=data.get('content'),
            speaker_rating=data.get('speaker_rating', 5),
            organization_rating=data.get('organization_rating', 5),
            venue_rating=data.get('venue_rating', 5),
            content_rating=data.get('content_rating', 5),
            suggestions=data.get('suggestions')
        )
        msg = "Thank you! Feedback submitted (+5 ITSA points)." if is_new else "Your feedback has been successfully updated."
        status_code = 201 if is_new else 200
        return success_response(fb.to_dict(), msg, status_code)
    except ValueError as e:
        return error_response("FEEDBACK_ERROR", str(e), 400)


@feedback_bp.route('/my/<int:event_id>', methods=['GET'])
@login_required
def get_my_feedback(event_id):
    """Retrieve the current student's feedback for a specific event."""
    fb = FeedbackService.get_student_feedback(current_user.id, event_id)
    if not fb:
        return success_response({'submitted': False, 'feedback': None})
    return success_response({'submitted': True, 'feedback': fb.to_dict()})


@feedback_bp.route('/event/<int:event_id>', methods=['GET'])
@coordinator_required
def get_event_feedback(event_id):
    """
    Get all feedback for an event.
    Only accessible by assigned coordinators and administrators.
    """
    event = Event.query.get_or_404(event_id)
    if current_user.role != 'ADMIN':
        assignment = EventCoordinator.query.filter_by(event_id=event.id, coordinator_id=current_user.id).first()
        if not assignment:
            return error_response("AUTH_INSUFFICIENT_ROLE", "You are not assigned as a coordinator for this event.", 403)

    rating_filter = request.args.get('rating', type=int)
    records = FeedbackService.get_event_feedback(event_id, rating=rating_filter)
    metrics = FeedbackService.get_feedback_metrics(event_id)

    return success_response({
        'feedbacks': [r.to_dict() for r in records],
        'metrics': metrics
    })
