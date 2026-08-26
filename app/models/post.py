from datetime import datetime
from app.extensions import db

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=True)
    post_type = db.Column(
        db.Enum('TEXT', 'IMAGE', 'VIDEO', 'MIXED', name='post_types'),
        default='TEXT',
        nullable=False
    )
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_reported = db.Column(db.Boolean, default=False, nullable=False, index=True)
    ai_moderated = db.Column(db.Boolean, default=False, nullable=False)
    ai_moderation_result = db.Column(db.String(50), nullable=True) # APPROVE, FLAG, REMOVE
    views_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    media = db.relationship('PostMedia', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('PostReaction', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    shares = db.relationship('PostShare', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    saves = db.relationship('SavedPost', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    hashtags = db.relationship('PostHashtag', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def user(self):
        return self.author

    def to_dict(self, current_user_id=None):
        reaction_counts = {}
        user_reaction = None
        for r in self.reactions:
            reaction_counts[r.reaction_type] = reaction_counts.get(r.reaction_type, 0) + 1
            if current_user_id and r.user_id == current_user_id:
                user_reaction = r.reaction_type

        is_saved = False
        if current_user_id:
            is_saved = any(s.user_id == current_user_id for s in self.saves)

        return {
            'id': self.id,
            'user_id': self.user_id,
            'author_name': self.author.full_name if self.author else None,
            'author_role': self.author.role if self.author else None,
            'author_image': self.author.profile_image if self.author else None,
            'content': self.content,
            'post_type': self.post_type,
            'event_id': self.event_id,
            'event_title': self.linked_event.title if self.linked_event else None,
            'media': [m.to_dict() for m in self.media],
            'reactions_count': sum(reaction_counts.values()),
            'reaction_breakdown': reaction_counts,
            'user_reaction': user_reaction,
            'comments_count': self.comments.filter_by(is_active=True).count(),
            'is_saved': is_saved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PostMedia(db.Model):
    __tablename__ = 'post_media'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    media_type = db.Column(db.Enum('IMAGE', 'VIDEO', name='media_types'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True) # in bytes
    media_order = db.Column(db.SmallInteger, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'media_type': self.media_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'media_order': self.media_order
        }


class PostReaction(db.Model):
    __tablename__ = 'post_reactions'
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='uq_reaction_post_user'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reaction_type = db.Column(
        db.Enum('LIKE', 'LOVE', 'CELEBRATE', 'INSIGHTFUL', 'SUPPORT', name='reaction_types'),
        default='LIKE',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'reaction_type': self.reaction_type
        }
