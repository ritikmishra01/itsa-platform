from datetime import datetime, timedelta
from flask import Blueprint, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.story import Story, StoryView
from app.models.user import User
from app.utils.responses import success_response, error_response
from app.utils.file_utils import (
    save_uploaded_file,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    is_allowed_file
)

stories_bp = Blueprint('api_stories', __name__, url_prefix='/api/v1/stories')

ALLOWED_STORY_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS


@stories_bp.route('', methods=['GET'])
def get_stories():
    """
    Get all active, non-expired stories grouped by user.
    """
    now = datetime.utcnow()
    curr_id = current_user.id if current_user.is_authenticated else None

    # Fetch active unexpired stories
    stories = (
        Story.query
        .filter(Story.is_active == True, Story.expires_at > now)
        .order_by(Story.created_at.asc())
        .all()
    )

    # Group stories by author
    groups_map = {}
    for story in stories:
        uid = story.user_id
        if uid not in groups_map:
            author = story.user
            groups_map[uid] = {
                'user_id': uid,
                'user_name': author.full_name if author else 'ITSA Member',
                'user_avatar': author.profile_image if author else None,
                'is_own': (uid == curr_id),
                'has_unseen': False,
                'stories': []
            }
        story_data = story.to_dict(curr_id)
        if not story_data['has_viewed'] and (uid != curr_id):
            groups_map[uid]['has_unseen'] = True
        groups_map[uid]['stories'].append(story_data)

    # Separate own stories group and other groups
    my_group = groups_map.pop(curr_id, None) if curr_id else None

    # Sort others: users with unseen stories first, then by most recent story
    other_groups = list(groups_map.values())
    other_groups.sort(key=lambda g: (
        not g['has_unseen'],  # unseen (True) first
        -(datetime.fromisoformat(g['stories'][-1]['created_at']).timestamp() if g['stories'] else 0)
    ))

    result = []
    if my_group:
        result.append(my_group)
    result.extend(other_groups)

    return success_response({
        'user_groups': result,
        'my_stories': my_group['stories'] if my_group else []
    })


@stories_bp.route('', methods=['POST'])
@login_required
def create_story():
    """
    Create a new photo, video, or text story (24-hour expiration).
    """
    media_file = request.files.get('media_file') or request.files.get('file')
    media_type = request.form.get('media_type', '').upper()
    text_content = (request.form.get('text_content') or '').strip()
    caption = (request.form.get('caption') or '').strip()
    bg_style = request.form.get('background_style') or 'linear-gradient(135deg, #6366f1, #a855f7)'

    media_url = None

    if media_file and media_file.filename != '':
        # Determine media type from file extension
        filename = media_file.filename
        if not is_allowed_file(filename, ALLOWED_STORY_EXTENSIONS):
            return error_response(
                "INVALID_FILE_TYPE",
                f"File type not supported. Allowed: {', '.join(sorted(ALLOWED_STORY_EXTENSIONS))}",
                400
            )

        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext in ALLOWED_VIDEO_EXTENSIONS:
            detected_type = 'VIDEO'
        else:
            detected_type = 'IMAGE'

        if not media_type or media_type not in ('IMAGE', 'VIDEO'):
            media_type = detected_type

        try:
            rel_path = save_uploaded_file(
                media_file,
                subfolder='stories',
                allowed_extensions=ALLOWED_STORY_EXTENSIONS
            )
            media_url = f"/{rel_path}"
        except Exception as e:
            return error_response("UPLOAD_FAILED", f"Could not save story media: {str(e)}", 500)

    elif text_content:
        media_type = 'TEXT'
    else:
        return error_response(
            "VALIDATION_ERROR",
            "Please provide an image/video file or text content for your story.",
            400
        )

    now = datetime.utcnow()
    story = Story(
        user_id=current_user.id,
        media_type=media_type,
        media_url=media_url,
        text_content=text_content if media_type == 'TEXT' else None,
        background_style=bg_style,
        caption=caption or None,
        created_at=now,
        expires_at=now + timedelta(hours=24),
        is_active=True
    )

    db.session.add(story)
    db.session.commit()

    return success_response(
        story.to_dict(current_user.id),
        "Story published! It will be visible for 24 hours.",
        201
    )


@stories_bp.route('/<int:story_id>/view', methods=['POST'])
@login_required
def record_story_view(story_id):
    """
    Record that current user viewed the story (idempotent).
    """
    story = Story.query.filter_by(id=story_id, is_active=True).first_or_404()

    # Don't require recording view on expired stories
    if story.is_expired:
        return error_response("STORY_EXPIRED", "This story has expired.", 410)

    # Check if already recorded
    existing_view = StoryView.query.filter_by(story_id=story.id, user_id=current_user.id).first()
    if not existing_view:
        view = StoryView(story_id=story.id, user_id=current_user.id, viewed_at=datetime.utcnow())
        db.session.add(view)
        db.session.commit()

    return success_response({
        'story_id': story.id,
        'view_count': story.views.count(),
        'has_viewed': True
    }, "Story view recorded")


@stories_bp.route('/<int:story_id>/viewers', methods=['GET'])
@login_required
def get_story_viewers(story_id):
    """
    Viewers list: Only story author or Admin can view who watched the story.
    """
    story = Story.query.filter_by(id=story_id).first_or_404()

    is_author = (int(story.user_id) == int(current_user.id))
    is_admin = (getattr(current_user, 'role', '') == 'ADMIN')

    if not (is_author or is_admin):
        return error_response(
            "FORBIDDEN",
            "Privacy restriction: Only the story author or an administrator can view who watched this story.",
            403
        )

    views = StoryView.query.filter_by(story_id=story.id).order_by(StoryView.viewed_at.desc()).all()
    return success_response({
        'story_id': story.id,
        'total_views': len(views),
        'viewers': [v.to_dict() for v in views]
    })


@stories_bp.route('/<int:story_id>', methods=['DELETE'])
@login_required
def delete_story(story_id):
    """
    Delete a story: Only story author or Admin can delete.
    """
    story = Story.query.filter_by(id=story_id).first_or_404()

    is_author = (int(story.user_id) == int(current_user.id))
    is_admin = (getattr(current_user, 'role', '') == 'ADMIN')

    if not (is_author or is_admin):
        return error_response(
            "FORBIDDEN",
            "You do not have permission to delete this story.",
            403
        )

    story.is_active = False
    db.session.delete(story)
    db.session.commit()

    return success_response(None, "Story deleted successfully")
