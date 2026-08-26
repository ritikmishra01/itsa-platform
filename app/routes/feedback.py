from flask import Blueprint, request
from flask_login import login_required, current_user
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

    if not event_id or not rating:
        return error_response("VALIDATION_ERROR", "Event ID and rating (1-5) are required.", 400)

    try:
        fb = FeedbackService.submit_feedback(
            user_id=current_user.id,
            event_id=int(event_id),
            rating=rating,
            content=data.get('content'),
            speaker_rating=data.get('speaker_rating', 5),
            organization_rating=data.get('organization_rating', 5),
            venue_rating=data.get('venue_rating', 5),
            suggestions=data.get('suggestions')
        )
        return success_response(fb.to_dict(), "Thank you! Feedback submitted (+5 ITSA points).", 201)
    except ValueError as e:
        return error_response("FEEDBACK_ERROR", str(e), 400)


@feedback_bp.route('/event/<int:event_id>', methods=['GET'])
@coordinator_required
def get_event_feedback(event_id):
    records = FeedbackService.get_event_feedback(event_id)
    return success_response([r.to_dict() for r in records])
