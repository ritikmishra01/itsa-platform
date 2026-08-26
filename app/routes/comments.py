from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.social_service import SocialService
from app.utils.responses import success_response, error_response

comments_bp = Blueprint('api_comments', __name__, url_prefix='/api/v1/comments')

@comments_bp.route('/post/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    content = data.get('content')
    if not content:
        return error_response("VALIDATION_ERROR", "Comment content required.", 400)

    try:
        comment = SocialService.add_comment(post_id, current_user.id, content)
        return success_response(comment.to_dict(), "Comment posted.", 201)
    except ValueError as e:
        return error_response("COMMENT_ERROR", str(e), 400)


@comments_bp.route('/<int:comment_id>/reply', methods=['POST'])
@login_required
def add_reply(comment_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    content = data.get('content')
    mentioned_user_id = data.get('mentioned_user_id')

    if not content:
        return error_response("VALIDATION_ERROR", "Reply content required.", 400)

    try:
        reply = SocialService.add_reply(comment_id, current_user.id, content, mentioned_user_id)
        return success_response(reply.to_dict(), "Reply posted.", 201)
    except ValueError as e:
        return error_response("REPLY_ERROR", str(e), 400)
