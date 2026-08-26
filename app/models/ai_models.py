from datetime import datetime
from app.extensions import db

class AiRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Float, nullable=False) # 0.0 to 1.0
    reason = db.Column(db.Text, nullable=True)
    model_version = db.Column(db.String(50), default='v1', nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    event = db.relationship('Event', foreign_keys=[event_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'category_name': self.event.category.name if self.event and self.event.category else None,
            'start_datetime': self.event.start_datetime.isoformat() if self.event and self.event.start_datetime else None,
            'score': round(self.score, 2),
            'reason': self.reason,
            'model_version': self.model_version
        }


class AiAnalysis(db.Model):
    __tablename__ = 'ai_analysis'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_type = db.Column(
        db.Enum('FEEDBACK_SENTIMENT', 'ATTENDANCE_PREDICTION', 'ENGAGEMENT_SCORE', 'REGISTRATION_PREDICTION', name='analysis_types'),
        nullable=False,
        index=True
    )
    related_id = db.Column(db.Integer, nullable=False, index=True) # event_id or user_id
    input_data = db.Column(db.JSON, nullable=True)
    output_data = db.Column(db.JSON, nullable=True)
    model_version = db.Column(db.String(50), default='v1', nullable=False)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'related_id': self.related_id,
            'output_data': self.output_data,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }
