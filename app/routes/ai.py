from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.ai_service import AIService
from app.utils.responses import success_response, error_response
from app.utils.decorators import coordinator_required, admin_required

ai_bp = Blueprint('api_ai', __name__, url_prefix='/api/v1/ai')

@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json() if request.is_json else request.form.to_dict()
    message = data.get('message', '').strip() if data else ''
    history = data.get('history', []) if data else []

    if not message:
        return error_response("VALIDATION_ERROR", "Message is required.", 400)

    reply = AIService.chat_with_assistant(current_user, message, history)
    return success_response({'reply': reply})


@ai_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    recs = AIService.recommend_events(current_user, top_n=5)
    return success_response(recs)


@ai_bp.route('/generate-description', methods=['POST'])
@coordinator_required
def generate_description():
    data = request.get_json() if request.is_json else request.form.to_dict()
    title = data.get('title', '')
    category = data.get('category_name', 'General')
    date_str = data.get('start_datetime', '')
    venue_str = data.get('venue_name', 'Campus Auditorium')
    topics = data.get('topics')
    audience = data.get('audience')

    description = AIService.generate_event_description(title, category, date_str, venue_str, topics, audience)
    return success_response({'description': description})


@ai_bp.route('/generate-announcement', methods=['POST'])
@coordinator_required
def generate_announcement():
    data = request.get_json() if request.is_json else request.form.to_dict()
    title = data.get('title', '')
    date_str = data.get('start_datetime', '')
    venue_str = data.get('venue_name', '')
    tone = data.get('tone', 'formal')
    channel = data.get('channel', 'email')

    announcement = AIService.generate_announcement(title, date_str, venue_str, tone, channel)
    return success_response({'announcement': announcement})


@ai_bp.route('/generate-caption', methods=['POST'])
@coordinator_required
def generate_caption():
    data = request.get_json() if request.is_json else request.form.to_dict()
    title = data.get('title', '')
    highlights = data.get('highlights')
    hashtags = data.get('hashtags')

    caption = AIService.generate_social_caption(title, highlights, hashtags)
    return success_response({'caption': caption})


@ai_bp.route('/analyze-feedback/<int:event_id>', methods=['POST', 'GET'])
@coordinator_required
def analyze_feedback(event_id):
    analysis = AIService.analyze_feedback(event_id)
    return success_response(analysis)


@ai_bp.route('/moderate-content', methods=['POST'])
@admin_required
def moderate_content():
    data = request.get_json() if request.is_json else request.form.to_dict()
    content = data.get('content', '')
    result = AIService.moderate_content(content)
    return success_response(result)


@ai_bp.route('/predict-registrations/<int:event_id>', methods=['GET'])
@coordinator_required
def predict_registrations(event_id):
    prediction = AIService.predict_registrations(event_id)
    return success_response(prediction)
