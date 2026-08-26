from datetime import datetime
from app.extensions import db
from app.models.feedback import Feedback
from app.models.attendance import Attendance
from app.services.gamification_service import GamificationService

class FeedbackService:
    @staticmethod
    def submit_feedback(user_id, event_id, rating, content=None, speaker_rating=5, organization_rating=5, venue_rating=5, suggestions=None):
        # Verify student attended event
        att = Attendance.query.filter_by(user_id=user_id, event_id=event_id, status='PRESENT').first()
        if not att:
            raise ValueError("You can only submit feedback for events you have attended.")

        existing = Feedback.query.filter_by(user_id=user_id, event_id=event_id).first()
        if existing:
            raise ValueError("You have already submitted feedback for this event.")

        rating_val = int(rating)
        if not (1 <= rating_val <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        feedback = Feedback(
            event_id=event_id,
            user_id=user_id,
            rating=rating_val,
            speaker_rating=int(speaker_rating) if speaker_rating else 5,
            organization_rating=int(organization_rating) if organization_rating else 5,
            venue_rating=int(venue_rating) if venue_rating else 5,
            content=content.strip() if content else None,
            suggestions=suggestions.strip() if suggestions else None,
            submitted_at=datetime.utcnow()
        )
        db.session.add(feedback)

        # Award points for feedback (+5)
        GamificationService.award_points(user_id, 5, 'FEEDBACK', related_event_id=event_id)
        db.session.commit()
        return feedback

    @staticmethod
    def get_event_feedback(event_id):
        return Feedback.query.filter_by(event_id=event_id).order_by(Feedback.submitted_at.desc()).all()
