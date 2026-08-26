from datetime import datetime
from app.extensions import db
from app.models.event import Event, EventCoordinator
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.services.gamification_service import GamificationService
from app.services.notification_service import NotificationService

class AttendanceService:
    @staticmethod
    def scan_attendance(coordinator_user, event_id, ticket_code, notes=None):
        """
        Critical Attendance Scan Flow.
        The COORDINATOR scans the STUDENT'S ticket.
        Executes 6-step server-side validation.
        """
        event = Event.query.get(event_id)
        if not event:
            raise ValueError("Event not found.")

        # Check authorization: Coordinator must be assigned or user is Admin
        if coordinator_user.role != 'ADMIN':
            assignment = EventCoordinator.query.filter_by(event_id=event_id, coordinator_id=coordinator_user.id).first()
            if not assignment:
                raise ValueError("Unauthorized: You are not assigned as a coordinator for this event.")

        # Step 1: Ticket exists
        ticket = EventTicket.query.filter_by(ticket_code=ticket_code.strip()).first()
        if not ticket:
            raise ValueError("Invalid QR Code: Ticket not found.")

        # Step 2: Ticket belongs to this event
        registration = ticket.registration
        if not registration or registration.event_id != int(event_id):
            raise ValueError("Ticket Mismatch: This ticket is for a different event.")

        # Step 3: Registration is confirmed
        if registration.status != 'CONFIRMED':
            raise ValueError(f"Invalid Registration: Registration status is {registration.status}.")

        # Step 4: Ticket is valid
        if not ticket.is_valid:
            raise ValueError("Invalid Ticket: Ticket has been revoked or invalidated.")

        # Step 5: Duplicate check
        existing_att = Attendance.query.filter_by(event_id=event_id, user_id=registration.user_id).first()
        if existing_att:
            raise ValueError(f"Duplicate Attendance: Student '{registration.user.full_name}' was already checked in at {existing_att.scanned_at.strftime('%H:%M:%S')}.")

        # Step 6: Event status check
        if event.status not in ('ONGOING', 'REGISTRATION_CLOSED', 'COMPLETED', 'PUBLISHED', 'REGISTRATION_OPEN') and coordinator_user.role != 'ADMIN':
            raise ValueError(f"Event is not active for attendance scanning (Status: {event.status}).")

        # Record attendance
        attendance = Attendance(
            event_id=event_id,
            user_id=registration.user_id,
            registration_id=registration.id,
            ticket_id=ticket.id,
            scanned_by=coordinator_user.id,
            scanned_at=datetime.utcnow(),
            status='PRESENT',
            notes=notes
        )
        db.session.add(attendance)
        db.session.flush()

        # Award points (+10)
        GamificationService.award_points(registration.user_id, 10, 'ATTENDANCE', related_event_id=event.id)

        # Generate certificate automatically
        from app.services.certificate_service import CertificateService
        try:
            CertificateService.generate_certificate(registration.user_id, event_id, attendance.id)
        except Exception as e:
            # Certificate generation failure should not block attendance marking
            pass

        # Send notification to student
        NotificationService.create_notification(
            user_id=registration.user_id,
            notif_type='SYSTEM',
            title=f"Attendance Marked: {event.title}",
            message=f"Your attendance for '{event.title}' has been successfully recorded! +10 ITSA Points awarded.",
            related_event_id=event.id,
            send_email_alert=True,
            user_email=registration.user.email
        )

        db.session.commit()
        return attendance

    @staticmethod
    def get_event_attendance(event_id):
        return Attendance.query.filter_by(event_id=event_id).order_by(Attendance.scanned_at.desc()).all()

    @staticmethod
    def manual_override(attendance_id, status, notes=None):
        att = Attendance.query.get(attendance_id)
        if not att:
            raise ValueError("Attendance record not found.")
        att.status = status
        if notes:
            att.notes = notes
        db.session.commit()
        return att
