from datetime import datetime
from app.extensions import db

class ItsaPoints(db.Model):
    __tablename__ = 'itsa_points'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    points = db.Column(db.Integer, nullable=False) # Positive or negative
    reason = db.Column(
        db.Enum('ATTENDANCE', 'REGISTRATION', 'FEEDBACK', 'SOCIAL_POST', 'SOCIAL_REACTION', 'VOLUNTEERING', 'COMPETITION', 'ADMIN_ADJUSTMENT', 'CANCELLATION', name='point_reasons'),
        nullable=False
    )
    related_event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'), nullable=True)
    related_post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    related_event = db.relationship('Event', foreign_keys=[related_event_id])
    related_post = db.relationship('Post', foreign_keys=[related_post_id])
    admin_creator = db.relationship('User', foreign_keys=[created_by])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'points': self.points,
            'reason': self.reason,
            'related_event_id': self.related_event_id,
            'related_event_title': self.related_event.title if self.related_event else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
