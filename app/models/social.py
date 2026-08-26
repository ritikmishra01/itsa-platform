from datetime import datetime
from app.extensions import db

class PostShare(db.Model):
    __tablename__ = 'post_shares'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    shared_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    platform = db.Column(db.Enum('FEED', 'EXTERNAL', name='share_platforms'), default='FEED', nullable=False)


class SavedPost(db.Model):
    __tablename__ = 'saved_posts'
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='uq_saved_post_user'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Hashtag(db.Model):
    __tablename__ = 'hashtags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False) # Without #
    post_count = db.Column(db.Integer, default=0, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    posts = db.relationship('PostHashtag', backref='hashtag', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'post_count': self.post_count
        }


class PostHashtag(db.Model):
    __tablename__ = 'post_hashtags'

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtags.id', ondelete='CASCADE'), primary_key=True, index=True)


class Mention(db.Model):
    __tablename__ = 'mentions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)
    reply_id = db.Column(db.Integer, db.ForeignKey('comment_replies.id', ondelete='CASCADE'), nullable=True)
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    mentioning_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
