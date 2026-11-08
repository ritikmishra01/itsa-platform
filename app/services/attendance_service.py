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

        # Sanitize and extract ticket code
        raw_code = (ticket_code or '').strip()
        if not raw_code:
            raise ValueError("Invalid ticket: Ticket code is required.")

        # Extract ticket code if formatted with surrounding characters, URLs, or JSON
        import re
        upper_code = raw_code.upper()
        if 'ITSA-TKT-' in upper_code:
            idx = upper_code.find('ITSA-TKT-')
            extracted = re.split(r'[\s"\'/?#&<>,}]', raw_code[idx:])[0]
            if extracted:
                raw_code = extracted.upper()
        elif 'DEMO-TKT-' in upper_code:
            idx = upper_code.find('DEMO-TKT-')
            extracted = re.split(r'[\s"\'/?#&<>,}]', raw_code[idx:])[0]
            if extracted:
                raw_code = extracted.upper()

        # Step 1: Ticket exists (case-insensitive)
        ticket = EventTicket.query.filter(db.func.upper(EventTicket.ticket_code) == raw_code.upper()).first()
        if not ticket:
            raise ValueError("Invalid ticket: Ticket code not found in database.")

        # Step 2: Event status check
        if event.status == 'CANCELLED':
            raise ValueError("Event is cancelled: Attendance cannot be recorded for cancelled events.")
        if event.status == 'DRAFT' and coordinator_user.role != 'ADMIN':
            raise ValueError("Event is not published: Attendance cannot be recorded for draft events.")
        if event.status not in ('ONGOING', 'REGISTRATION_CLOSED', 'COMPLETED', 'PUBLISHED', 'REGISTRATION_OPEN') and coordinator_user.role != 'ADMIN':
            raise ValueError(f"Event is not active for attendance scanning (Status: {event.status}).")

        # Step 3: Ticket belongs to this event
        registration = ticket.registration
        if not registration or registration.event_id != int(event_id):
            raise ValueError("Ticket mismatch: This ticket is for a different event.")

        # Step 4: Registration status
        if registration.status == 'CANCELLED':
            raise ValueError("Invalid registration: Student registration was cancelled.")
        if registration.status == 'WAITLISTED':
            raise ValueError("Invalid registration: Student registration is waitlisted and not confirmed.")
        if registration.status != 'CONFIRMED':
            raise ValueError(f"Invalid registration: Registration status is {registration.status}.")

        # Step 5: Ticket validity
        if not ticket.is_valid:
            raise ValueError("Invalid ticket: Ticket has been revoked or invalidated.")

        # Step 6: Duplicate check
        existing_att = Attendance.query.filter(
            (Attendance.event_id == int(event_id)) &
            ((Attendance.user_id == registration.user_id) | (Attendance.ticket_id == ticket.id))
        ).first()
        if existing_att:
            scanned_time = existing_att.scanned_at.strftime('%I:%M %p') if existing_att.scanned_at else 'earlier'
            raise ValueError(f"Already checked in: Student '{registration.user.full_name}' was already checked in at {scanned_time}.")

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
