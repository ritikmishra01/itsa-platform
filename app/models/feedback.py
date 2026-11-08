from datetime import datetime
from app.extensions import db

class Feedback(db.Model):
    __tablename__ = 'feedback'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_feedback_event_user'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = db.Column(db.SmallInteger, nullable=False) # 1 to 5 overall
    speaker_rating = db.Column(db.SmallInteger, default=5, nullable=True) # 1 to 5
    organization_rating = db.Column(db.SmallInteger, default=5, nullable=True) # 1 to 5
    venue_rating = db.Column(db.SmallInteger, default=5, nullable=True) # 1 to 5
    content_rating = db.Column(db.SmallInteger, default=5, nullable=True) # 1 to 5
    content = db.Column(db.Text, nullable=True) # Main feedback comment
    suggestions = db.Column(db.Text, nullable=True) # Suggestions for improvement
    ai_sentiment = db.Column(db.String(50), nullable=True) # POSITIVE, NEGATIVE, NEUTRAL, MIXED
    ai_keywords = db.Column(db.Text, nullable=True) # JSON array
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'user_id': self.user_id,
            'student_name': self.user.full_name if self.user else None,
            'student_id': self.user.student_profile.student_id if self.user and self.user.student_profile else None,
            'department': self.user.student_profile.department if self.user and self.user.student_profile else None,
            'rating': self.rating,
            'speaker_rating': self.speaker_rating or 5,
            'organization_rating': self.organization_rating or 5,
            'venue_rating': self.venue_rating or 5,
            'content_rating': self.content_rating or 5,
            'content': self.content,
            'suggestions': self.suggestions,
            'ai_sentiment': self.ai_sentiment,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'submitted_at_formatted': self.submitted_at.strftime('%b %d, %Y - %I:%M %p') if self.submitted_at else None,
        }
