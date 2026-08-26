from datetime import datetime, timedelta
from sqlalchemy import func, distinct
from app.extensions import db
from app.models.user import User, StudentProfile
from app.models.event import Event, EventCategory
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import Feedback

class AnalyticsService:
    @staticmethod
    def get_admin_dashboard_metrics():
        total_students = User.query.filter_by(role='STUDENT', is_active=True).count()
        total_coordinators = User.query.filter_by(role='COORDINATOR', is_active=True).count()
        total_events = Event.query.count()
        total_registrations = EventRegistration.query.filter_by(status='CONFIRMED').count()
        total_attendances = Attendance.query.filter_by(status='PRESENT').count()
        total_certificates = Certificate.query.filter_by(is_valid=True).count()

        avg_rating_res = db.session.query(func.avg(Feedback.rating)).scalar()
        avg_rating = round(float(avg_rating_res), 1) if avg_rating_res else 0.0

        # Active students this month
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        active_students = db.session.query(func.count(distinct(Attendance.user_id))).filter(
            Attendance.scanned_at >= one_month_ago
        ).scalar() or 0

        # Events by category for chart
        cat_counts = db.session.query(
            EventCategory.name, func.count(Event.id)
        ).outerjoin(Event, EventCategory.id == Event.category_id).group_by(EventCategory.name).all()

        category_labels = [c[0] for c in cat_counts]
        category_data = [c[1] for c in cat_counts]

        # Department-wise participation
        dept_counts = db.session.query(
            StudentProfile.department, func.count(Attendance.id)
        ).join(User, StudentProfile.user_id == User.id).join(
            Attendance, User.id == Attendance.user_id
        ).group_by(StudentProfile.department).all()

        dept_labels = [d[0] for d in dept_counts] if dept_counts else ['Computer Science', 'Information Tech', 'Data Science', 'Electronics']
        dept_data = [d[1] for d in dept_counts] if dept_counts else [0, 0, 0, 0]

        # Year-wise participation
        year_counts = db.session.query(
            StudentProfile.year_of_study, func.count(Attendance.id)
        ).join(User, StudentProfile.user_id == User.id).join(
            Attendance, User.id == Attendance.user_id
        ).group_by(StudentProfile.year_of_study).order_by(StudentProfile.year_of_study).all()

        year_labels = [f"Year {y[0]}" for y in year_counts] if year_counts else ['Year 1', 'Year 2', 'Year 3', 'Year 4']
        year_data = [y[1] for y in year_counts] if year_counts else [0, 0, 0, 0]

        return {
            'total_students': total_students,
            'total_coordinators': total_coordinators,
            'total_events': total_events,
            'total_registrations': total_registrations,
            'total_attendances': total_attendances,
            'total_certificates': total_certificates,
            'avg_rating': avg_rating,
            'active_students': active_students,
            'charts': {
                'categories': {'labels': category_labels, 'data': category_data},
                'departments': {'labels': dept_labels, 'data': dept_data},
                'years': {'labels': year_labels, 'data': year_data}
            }
        }

    @staticmethod
    def get_coordinator_event_metrics(event_id):
        event = Event.query.get_or_404(event_id)
        total_regs = event.registrations.filter_by(status='CONFIRMED').count()
        total_atts = event.attendances.filter_by(status='PRESENT').count()
        att_rate = round((total_atts / total_regs * 100), 1) if total_regs > 0 else 0.0

        avg_rating = db.session.query(func.avg(Feedback.rating)).filter_by(event_id=event_id).scalar()

        # Feedback distribution (1-5 stars)
        star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        fb_records = Feedback.query.filter_by(event_id=event_id).all()
        for f in fb_records:
            if f.rating in star_counts:
                star_counts[f.rating] += 1

        return {
            'event_id': event.id,
            'event_title': event.title,
            'total_registrations': total_regs,
            'total_attendance': total_atts,
            'attendance_rate': att_rate,
            'max_participants': event.max_participants,
            'avg_rating': round(float(avg_rating), 1) if avg_rating else 0.0,
            'feedback_distribution': star_counts
        }
