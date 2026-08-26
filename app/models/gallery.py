from datetime import datetime
from app.extensions import db

class EventGallery(db.Model):
    __tablename__ = 'event_gallery'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.Enum('IMAGE', 'VIDEO', name='gallery_media_types'), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    uploader = db.relationship('User', foreign_keys=[uploaded_by])

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'uploader_name': self.uploader.full_name if self.uploader else None,
            'file_path': self.file_path,
            'media_type': self.media_type,
            'caption': self.caption,
            'is_featured': self.is_featured,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class EventVolunteer(db.Model):
    __tablename__ = 'event_volunteers'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_volunteer_event_user'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    volunteer = db.relationship('User', foreign_keys=[user_id])
    assigner = db.relationship('User', foreign_keys=[assigned_by])

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'volunteer_name': self.volunteer.full_name if self.volunteer else None,
            'role': self.role,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None
        }
