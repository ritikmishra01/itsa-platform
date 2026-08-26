from datetime import datetime
from app.extensions import db
from app.models.notification import Notification
from app.utils.email_utils import send_email

class NotificationService:
    @staticmethod
    def create_notification(user_id, notif_type, title, message, related_event_id=None, related_post_id=None, related_user_id=None, send_email_alert=False, user_email=None):
        notif = Notification(
            user_id=user_id,
            type=notif_type,
            title=title,
            message=message,
            related_event_id=related_event_id,
            related_post_id=related_post_id,
            related_user_id=related_user_id
        )
        db.session.add(notif)
        db.session.commit()

        if send_email_alert and user_email:
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                <h2 style="color: #1a73e8;">{title}</h2>
                <p>{message}</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #888;">ITSA AI-Powered Platform - Official Notification</p>
            </div>
            """
            send_email(user_email, f"ITSA Alert: {title}", html)

        return notif

    @staticmethod
    def mark_as_read(notif_id, user_id):
        notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return True

    @staticmethod
    def get_user_notifications(user_id, limit=30):
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()
