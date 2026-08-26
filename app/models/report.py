from datetime import datetime
from app.extensions import db

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reported_post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='SET NULL'), nullable=True)
    reported_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='SET NULL'), nullable=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reason = db.Column(
        db.Enum('SPAM', 'INAPPROPRIATE', 'HARASSMENT', 'MISINFORMATION', 'OTHER', name='report_reasons'),
        nullable=False
    )
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum('PENDING', 'REVIEWED', 'RESOLVED', 'DISMISSED', name='report_statuses'),
        default='PENDING',
        nullable=False,
        index=True
    )
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    reported_post = db.relationship('Post', foreign_keys=[reported_post_id])
    reported_comment = db.relationship('Comment', foreign_keys=[reported_comment_id])

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_name': self.reporter.full_name if self.reporter else None,
            'reported_post_id': self.reported_post_id,
            'reported_comment_id': self.reported_comment_id,
            'reason': self.reason,
            'description': self.description,
            'status': self.status,
            'reviewed_by_name': self.reviewer.full_name if self.reviewer else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
