from datetime import datetime
from app.extensions import db

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_reported = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    replies = db.relationship('CommentReply', backref='comment', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def user(self):
        return self.author

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'author_name': self.author.full_name if self.author else None,
            'author_image': self.author.profile_image if self.author else None,
            'content': self.content,
            'replies': [r.to_dict() for r in self.replies.filter_by(is_active=True)],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CommentReply(db.Model):
    __tablename__ = 'comment_replies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author = db.relationship('User', foreign_keys=[user_id])
    mentioned_user = db.relationship('User', foreign_keys=[mentioned_user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'author_name': self.author.full_name if self.author else None,
            'author_image': self.author.profile_image if self.author else None,
            'content': self.content,
            'mentioned_user_name': self.mentioned_user.full_name if self.mentioned_user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
