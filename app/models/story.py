from datetime import datetime, timedelta
from app.extensions import db

class Story(db.Model):
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    media_type = db.Column(db.String(20), nullable=False, default='IMAGE')  # 'IMAGE', 'VIDEO', 'TEXT'
    media_url = db.Column(db.String(255), nullable=True)
    text_content = db.Column(db.Text, nullable=True)
    background_style = db.Column(db.String(150), nullable=True, default='linear-gradient(135deg, #6366f1, #a855f7)')
    caption = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('stories', lazy='dynamic', cascade='all, delete-orphan'))
    views = db.relationship('StoryView', backref='story', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = (self.created_at or datetime.utcnow()) + timedelta(hours=24)

    @property
    def is_expired(self):
        return datetime.utcnow() >= self.expires_at

    def to_dict(self, current_user_id=None):
        has_viewed = False
        if current_user_id:
            has_viewed = StoryView.query.filter_by(story_id=self.id, user_id=current_user_id).first() is not None

        return {
            'id': self.id,
            'user_id': self.user_id,
            'author_name': self.user.full_name if self.user else 'Unknown',
            'author_avatar': self.user.profile_image if self.user else None,
            'media_type': self.media_type,
            'media_url': self.media_url,
            'text_content': self.text_content,
            'background_style': self.background_style or 'linear-gradient(135deg, #6366f1, #a855f7)',
            'caption': self.caption,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'view_count': self.views.count(),
            'has_viewed': has_viewed
        }


class StoryView(db.Model):
    __tablename__ = 'story_views'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('story_views', lazy='dynamic', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('story_id', 'user_id', name='uq_story_user_view'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'story_id': self.story_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Unknown',
            'user_avatar': self.user.profile_image if self.user else None,
            'user_email': self.user.email if self.user else None,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None
        }
