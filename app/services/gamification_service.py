from datetime import datetime
from app.extensions import db
from app.models.user import User, StudentProfile
from app.models.gamification import ItsaPoints
from app.models.notification import Notification

class GamificationService:
    @staticmethod
    def award_points(user_id, points, reason, related_event_id=None, related_post_id=None, created_by=None):
        """
        Awards or deducts ITSA points with transaction logging and student total update.
        """
        user = User.query.get(user_id)
        if not user or user.role != 'STUDENT':
            return None

        # Create point transaction record
        tx = ItsaPoints(
            user_id=user_id,
            points=points,
            reason=reason,
            related_event_id=related_event_id,
            related_post_id=related_post_id,
            created_by=created_by
        )
        db.session.add(tx)

        # Update denormalized total points
        if user.student_profile:
            new_total = max(0, user.student_profile.total_points + points)
            user.student_profile.total_points = new_total

        db.session.commit()
        return tx

    @staticmethod
    def get_leaderboard(limit=50, department=None, year_of_study=None):
        query = db.session.query(User, StudentProfile).join(
            StudentProfile, User.id == StudentProfile.user_id
        ).filter(
            User.role == 'STUDENT',
            User.is_active == True,
            User.is_suspended == False
        )

        if department:
            query = query.filter(StudentProfile.department == department)
        if year_of_study:
            query = query.filter(StudentProfile.year_of_study == year_of_study)

        results = query.order_by(StudentProfile.total_points.desc()).limit(limit).all()

        leaderboard = []
        for rank, (user, profile) in enumerate(results, start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': user.id,
                'full_name': user.full_name,
                'student_id': profile.student_id,
                'department': profile.department,
                'year_of_study': profile.year_of_study,
                'total_points': profile.total_points,
                'profile_image': user.profile_image
            })
        return leaderboard

    @staticmethod
    def get_user_points_history(user_id):
        return ItsaPoints.query.filter_by(user_id=user_id).order_by(ItsaPoints.created_at.desc()).all()
