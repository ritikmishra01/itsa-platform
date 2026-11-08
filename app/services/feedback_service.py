from datetime import datetime
from sqlalchemy import func
from app.extensions import db
from app.models.feedback import Feedback
from app.models.event import Event
from app.models.attendance import Attendance
from app.services.gamification_service import GamificationService

class FeedbackService:
    @staticmethod
    def submit_feedback(user_id: int, event_id: int, rating: int,
                        content: str = None, speaker_rating: int = 5,
                        organization_rating: int = 5, venue_rating: int = 5,
                        content_rating: int = 5, suggestions: str = None):
        """
        Submit or edit feedback for an attended and completed event.
        Returns:
            tuple: (Feedback, is_new: bool)
        """
        event = Event.query.get(event_id)
        if not event:
            raise ValueError("Event not found.")

        # Event must be marked as COMPLETED
        if event.status != 'COMPLETED':
            raise ValueError("Feedback can only be submitted for completed events.")

        # Student must have verified attendance (PRESENT)
        att = Attendance.query.filter_by(user_id=user_id, event_id=event_id, status='PRESENT').first()
        if not att:
            raise ValueError("You can only submit feedback for events you have attended.")

        # Validate overall rating (1 to 5)
        try:
            rating_val = int(rating)
        except (ValueError, TypeError):
            raise ValueError("Overall rating must be a valid number.")

        if not (1 <= rating_val <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        # Helper to validate sub-ratings
        def _clean_sub_rating(val, default=5, name="Sub-rating"):
            if val is None or val == '':
                return default
            try:
                iv = int(val)
                if not (1 <= iv <= 5):
                    raise ValueError(f"{name} must be between 1 and 5.")
                return iv
            except (ValueError, TypeError):
                raise ValueError(f"{name} must be a valid number between 1 and 5.")

        speaker_val = _clean_sub_rating(speaker_rating, 5, "Speaker rating")
        org_val = _clean_sub_rating(organization_rating, 5, "Organization rating")
        venue_val = _clean_sub_rating(venue_rating, 5, "Venue rating")
        content_val = _clean_sub_rating(content_rating, 5, "Content rating")

        # Validate comment lengths
        clean_content = content.strip() if content else None
        clean_suggestions = suggestions.strip() if suggestions else None

        if clean_content and len(clean_content) > 1000:
            raise ValueError("Feedback comments cannot exceed 1000 characters.")
        if clean_suggestions and len(clean_suggestions) > 1000:
            raise ValueError("Suggestions cannot exceed 1000 characters.")

        # Check for existing feedback (support editing/updating)
        existing = Feedback.query.filter_by(user_id=user_id, event_id=event_id).first()
        if existing:
            existing.rating = rating_val
            existing.speaker_rating = speaker_val
            existing.organization_rating = org_val
            existing.venue_rating = venue_val
            existing.content_rating = content_val
            existing.content = clean_content
            existing.suggestions = clean_suggestions
            existing.submitted_at = datetime.utcnow()
            db.session.commit()
            return existing, False

        # Create new feedback record
        feedback = Feedback(
            event_id=event_id,
            user_id=user_id,
            rating=rating_val,
            speaker_rating=speaker_val,
            organization_rating=org_val,
            venue_rating=venue_val,
            content_rating=content_val,
            content=clean_content,
            suggestions=clean_suggestions,
            submitted_at=datetime.utcnow()
        )
        db.session.add(feedback)

        # Award points on initial feedback submission (+5 points)
        GamificationService.award_points(user_id, 5, 'FEEDBACK', related_event_id=event_id)
        db.session.commit()
        return feedback, True

    @staticmethod
    def get_student_feedback(user_id: int, event_id: int):
        """Get a specific student's feedback for an event."""
        return Feedback.query.filter_by(user_id=user_id, event_id=event_id).first()

    @staticmethod
    def get_event_feedback(event_id: int, rating: int = None):
        """Get all feedbacks for an event with optional star rating filter."""
        query = Feedback.query.filter_by(event_id=event_id)
        if rating and 1 <= rating <= 5:
            query = query.filter_by(rating=rating)
        return query.order_by(Feedback.submitted_at.desc()).all()

    @staticmethod
    def get_feedback_metrics(event_id: int = None):
        """
        Calculate aggregate feedback metrics for a specific event or across the platform.
        """
        query = db.session.query(
            func.count(Feedback.id).label('total_count'),
            func.avg(Feedback.rating).label('avg_rating'),
            func.avg(Feedback.speaker_rating).label('avg_speaker'),
            func.avg(Feedback.organization_rating).label('avg_org'),
            func.avg(Feedback.venue_rating).label('avg_venue'),
            func.avg(Feedback.content_rating).label('avg_content'),
        )
        if event_id:
            query = query.filter(Feedback.event_id == event_id)

        stats = query.first()
        total_count = stats.total_count or 0
        avg_rating = round(float(stats.avg_rating), 1) if stats.avg_rating else 0.0

        # Star distribution (1 to 5)
        dist_query = db.session.query(Feedback.rating, func.count(Feedback.id))
        if event_id:
            dist_query = dist_query.filter(Feedback.event_id == event_id)
        dist_rows = dist_query.group_by(Feedback.rating).all()

        star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for star, cnt in dist_rows:
            if star in star_counts:
                star_counts[star] = cnt

        positive_count = star_counts.get(4, 0) + star_counts.get(5, 0)
        satisfaction_rate = round((positive_count / total_count * 100), 1) if total_count > 0 else 0.0

        return {
            'total_count': total_count,
            'avg_rating': avg_rating,
            'avg_speaker_rating': round(float(stats.avg_speaker), 1) if stats.avg_speaker else 0.0,
            'avg_organization_rating': round(float(stats.avg_org), 1) if stats.avg_org else 0.0,
            'avg_venue_rating': round(float(stats.avg_venue), 1) if stats.avg_venue else 0.0,
            'avg_content_rating': round(float(stats.avg_content), 1) if stats.avg_content else 0.0,
            'star_counts': star_counts,
            'satisfaction_rate': satisfaction_rate,
        }

    @staticmethod
    def get_all_feedback_filtered(event_id: int = None, rating: int = None,
                                  start_date: str = None, end_date: str = None):
        """Retrieve feedback filtered by event, rating, and date range."""
        query = Feedback.query
        if event_id:
            query = query.filter(Feedback.event_id == event_id)
        if rating and 1 <= rating <= 5:
            query = query.filter(Feedback.rating == rating)
        if start_date:
            try:
                sd = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Feedback.submitted_at >= sd)
            except ValueError:
                pass
        if end_date:
            try:
                ed = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(Feedback.submitted_at <= ed)
            except ValueError:
                pass

        return query.order_by(Feedback.submitted_at.desc()).all()
