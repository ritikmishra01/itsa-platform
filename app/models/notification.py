from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(
        db.Enum('EVENT_REGISTRATION', 'EVENT_REMINDER', 'EVENT_CHANGE', 'EVENT_CANCELLED', 'CERTIFICATE_READY', 'POST_REACTION', 'POST_COMMENT', 'MENTION', 'ANNOUNCEMENT', 'SYSTEM', name='notification_types'),
        nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    related_event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'), nullable=True)
    related_post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='SET NULL'), nullable=True)
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    @property
    def user(self):
        return getattr(self, 'recipient', None)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'related_event_id': self.related_event_id,
            'related_post_id': self.related_post_id,
            'related_user_id': self.related_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
