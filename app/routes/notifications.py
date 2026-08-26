from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.notification_service import NotificationService
from app.utils.responses import success_response

notifications_bp = Blueprint('api_notifications', __name__, url_prefix='/api/v1/notifications')

@notifications_bp.route('', methods=['GET'])
@login_required
def get_notifications():
    notifs = NotificationService.get_user_notifications(current_user.id)
    return success_response([n.to_dict() for n in notifs])


@notifications_bp.route('/<int:notif_id>/read', methods=['PUT', 'POST'])
@login_required
def mark_read(notif_id):
    NotificationService.mark_as_read(notif_id, current_user.id)
    return success_response({}, "Marked as read.")


@notifications_bp.route('/read-all', methods=['PUT', 'POST'])
@login_required
def mark_all_read():
    NotificationService.mark_all_as_read(current_user.id)
    return success_response({}, "All notifications marked as read.")
