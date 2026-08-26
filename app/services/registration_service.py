from datetime import datetime
from app.extensions import db
from app.models.event import Event
from app.models.registration import EventRegistration
from app.services.ticket_service import TicketService
from app.services.gamification_service import GamificationService
from app.services.notification_service import NotificationService

class RegistrationService:
    @staticmethod
    def register_student(event_id, user):
        event = Event.query.get(event_id)
        if not event:
            raise ValueError("Event not found.")

        if event.status != 'REGISTRATION_OPEN':
            raise ValueError(f"Registration is not open for this event (Current status: {event.status}).")

        now = datetime.utcnow()
        if now > event.registration_deadline:
            raise ValueError("Registration deadline for this event has passed.")

        if event.max_participants and event.current_registrations >= event.max_participants:
            raise ValueError("Event registration is full.")

        existing = EventRegistration.query.filter_by(event_id=event_id, user_id=user.id).first()
        if existing:
            if existing.status == 'CONFIRMED':
                raise ValueError("You are already registered for this event.")
            elif existing.status == 'CANCELLED':
                # Re-activate registration
                existing.status = 'CONFIRMED'
                existing.cancelled_at = None
                existing.cancellation_reason = None
                existing.registered_at = datetime.utcnow()
                event.current_registrations += 1
                if existing.ticket:
                    existing.ticket.is_valid = True
                else:
                    TicketService.generate_ticket(existing.id)
                GamificationService.award_points(user.id, 3, 'REGISTRATION', related_event_id=event.id)
                db.session.commit()
                return existing

        # Generate unique registration number
        reg_count = EventRegistration.query.filter_by(event_id=event_id).count() + 1
        current_year = datetime.utcnow().year
        reg_number = f"ITSA-{event.id}-{current_year}-{reg_count:04d}"

        registration = EventRegistration(
            event_id=event_id,
            user_id=user.id,
            registration_number=reg_number,
            status='CONFIRMED'
        )
        db.session.add(registration)
        event.current_registrations += 1
        db.session.flush() # Get registration.id

        # Generate digital ticket with QR
        ticket = TicketService.generate_ticket(registration.id)

        # Award points for registering
        GamificationService.award_points(user.id, 3, 'REGISTRATION', related_event_id=event.id)

        # Send confirmation notification
        NotificationService.create_notification(
            user_id=user.id,
            notif_type='EVENT_REGISTRATION',
            title=f"Registration Confirmed: {event.title}",
            message=f"You have successfully registered for {event.title}. Your ticket code is {ticket.ticket_code}.",
            related_event_id=event.id,
            send_email_alert=True,
            user_email=user.email
        )

        db.session.commit()
        return registration

    @staticmethod
    def cancel_registration(registration_id, user):
        registration = EventRegistration.query.get(registration_id)
        if not registration:
            raise ValueError("Registration not found.")

        # Check ownership or admin
        if registration.user_id != user.id and user.role != 'ADMIN':
            raise ValueError("Unauthorized to cancel this registration.")

        if registration.status == 'CANCELLED':
            raise ValueError("Registration is already cancelled.")

        event = registration.event
        now = datetime.utcnow()
        if user.role != 'ADMIN' and now > event.registration_deadline:
            raise ValueError("Cannot cancel registration after the registration deadline.")

        registration.status = 'CANCELLED'
        registration.cancelled_at = datetime.utcnow()
        registration.cancellation_reason = "Cancelled by user." if user.id == registration.user_id else "Cancelled by admin."

        if registration.ticket:
            registration.ticket.is_valid = False

        if event.current_registrations > 0:
            event.current_registrations -= 1

        # Deduct registration points
        GamificationService.award_points(registration.user_id, -3, 'CANCELLATION', related_event_id=event.id)

        NotificationService.create_notification(
            user_id=registration.user_id,
            notif_type='EVENT_CANCELLED',
            title=f"Registration Cancelled: {event.title}",
            message=f"Your registration for {event.title} has been cancelled.",
            related_event_id=event.id
        )

        db.session.commit()
        return True
