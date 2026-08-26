from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.post import Post
from app.services.social_service import SocialService
from app.utils.responses import success_response, error_response, paginated_response
from app.utils.file_utils import save_uploaded_file, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS

posts_bp = Blueprint('api_posts', __name__, url_prefix='/api/v1/posts')

@posts_bp.route('', methods=['GET'])
def get_feed():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    hashtag = request.args.get('hashtag')
    event_id = request.args.get('event_id')

    curr_id = current_user.id if current_user.is_authenticated else None
    posts, total = SocialService.get_feed(page=page, per_page=per_page, hashtag=hashtag, event_id=event_id)

    return paginated_response([p.to_dict(curr_id) for p in posts], page, per_page, total)


@posts_bp.route('', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content', '')
    post_type = request.form.get('post_type', 'TEXT')
    event_id = request.form.get('event_id')

    media_files = []
    # Check for uploaded images
    images = request.files.getlist('images')
    if images:
        for img in images:
            if img and img.filename != '':
                try:
                    p = save_uploaded_file(img, subfolder='posts/images', allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
                    if p:
                        media_files.append({'media_type': 'IMAGE', 'file_path': p})
                except ValueError as e:
                    return error_response("FILE_INVALID", str(e), 400)

    # Check for uploaded video
    if 'video' in request.files:
        vid = request.files['video']
        if vid and vid.filename != '':
            try:
                p = save_uploaded_file(vid, subfolder='posts/videos', allowed_extensions=ALLOWED_VIDEO_EXTENSIONS)
                if p:
                    media_files.append({'media_type': 'VIDEO', 'file_path': p})
            except ValueError as e:
                return error_response("FILE_INVALID", str(e), 400)

    if media_files and post_type == 'TEXT':
        post_type = 'IMAGE' if all(m['media_type'] == 'IMAGE' for m in media_files) else 'MIXED'

    try:
        post = SocialService.create_post(
            user_id=current_user.id,
            content=content,
            post_type=post_type,
            event_id=event_id,
            media_files=media_files
        )
        return success_response(post.to_dict(current_user.id), "Post created successfully.", 201)
    except ValueError as e:
        return error_response("POST_CREATION_ERROR", str(e), 400)


@posts_bp.route('/<int:post_id>/react', methods=['POST'])
@login_required
def react_post(post_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    reaction_type = data.get('reaction_type', 'LIKE') if data else 'LIKE'

    reaction, msg = SocialService.react_to_post(post_id, current_user.id, reaction_type)
    return success_response({'reaction': reaction.to_dict() if reaction else None}, msg)


@posts_bp.route('/<int:post_id>/save', methods=['POST'])
@login_required
def toggle_save_post(post_id):
    is_saved = SocialService.save_post(post_id, current_user.id)
    return success_response({'is_saved': is_saved}, "Post saved to collection." if is_saved else "Post removed from saved.")


@posts_bp.route('/<int:post_id>/report', methods=['POST'])
@login_required
def report_post(post_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    reason = data.get('reason', 'OTHER')
    description = data.get('description')

    report = SocialService.report_content(current_user.id, reason, description, post_id=post_id)
    return success_response(report.to_dict(), "Post reported for review.")


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    from app.extensions import db
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and current_user.role != 'ADMIN':
        return error_response("AUTH_INSUFFICIENT_ROLE", "Unauthorized to delete this post.", 403)

    db.session.delete(post)
    db.session.commit()
    return success_response({}, "Post deleted successfully.")
