from datetime import datetime
from app.extensions import db
from app.models.event import Event, EventCategory, Venue, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.services.notification_service import NotificationService
from app.services.gamification_service import GamificationService

class EventService:
    @staticmethod
    def create_event(creator_id, data, poster_path=None):
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category_id = data.get('category_id')
        venue_id = data.get('venue_id')
        start_datetime = data.get('start_datetime')
        end_datetime = data.get('end_datetime')
        registration_deadline = data.get('registration_deadline')
        max_participants = data.get('max_participants')
        is_free = data.get('is_free', True)
        registration_fee = data.get('registration_fee', 0.0)
        tags = data.get('tags', '')

        if not title or not description or not start_datetime or not end_datetime or not registration_deadline:
            raise ValueError("Title, description, start time, end time, and registration deadline are required.")

        # Parse datetimes if string
        if isinstance(start_datetime, str):
            start_datetime = datetime.fromisoformat(start_datetime)
        if isinstance(end_datetime, str):
            end_datetime = datetime.fromisoformat(end_datetime)
        if isinstance(registration_deadline, str):
            registration_deadline = datetime.fromisoformat(registration_deadline)

        if end_datetime <= start_datetime:
            raise ValueError("Event end time must be after start time.")
        if registration_deadline > start_datetime:
            raise ValueError("Registration deadline must be before or at event start time.")

        event = Event(
            title=title,
            description=description,
            category_id=int(category_id) if category_id else None,
            venue_id=int(venue_id) if venue_id else None,
            poster_image=poster_path,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            registration_deadline=registration_deadline,
            max_participants=int(max_participants) if max_participants else None,
            status=data.get('status', 'DRAFT'),
            is_free=bool(is_free),
            registration_fee=float(registration_fee) if registration_fee else 0.0,
            tags=tags.strip() if tags else None,
            created_by=creator_id
        )
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def update_event(event_id, data, poster_path=None):
        event = Event.query.get(event_id)
        if not event:
            raise ValueError("Event not found.")

        if 'title' in data:
            event.title = data['title'].strip()
        if 'description' in data:
            event.description = data['description'].strip()
        if 'category_id' in data:
            event.category_id = int(data['category_id']) if data['category_id'] else None
        if 'venue_id' in data:
            event.venue_id = int(data['venue_id']) if data['venue_id'] else None
        if poster_path:
            event.poster_image = poster_path
        if 'start_datetime' in data and data['start_datetime']:
            val = data['start_datetime']
            event.start_datetime = datetime.fromisoformat(val) if isinstance(val, str) else val
        if 'end_datetime' in data and data['end_datetime']:
            val = data['end_datetime']
            event.end_datetime = datetime.fromisoformat(val) if isinstance(val, str) else val
        if 'registration_deadline' in data and data['registration_deadline']:
            val = data['registration_deadline']
            event.registration_deadline = datetime.fromisoformat(val) if isinstance(val, str) else val
        if 'max_participants' in data:
            event.max_participants = int(data['max_participants']) if data['max_participants'] else None
        if 'status' in data:
            event.status = data['status']
        if 'is_free' in data:
            event.is_free = bool(data['is_free'])
        if 'registration_fee' in data:
            event.registration_fee = float(data['registration_fee']) if data['registration_fee'] else 0.0
        if 'tags' in data:
            event.tags = data['tags'].strip()

        db.session.commit()
        return event

    @staticmethod
    def change_status(event_id, new_status):
        event = Event.query.get(event_id)
        if not event:
            raise ValueError("Event not found.")

        valid_statuses = ['DRAFT', 'PUBLISHED', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'ONGOING', 'COMPLETED', 'CANCELLED']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid event status: {new_status}")

        if new_status == 'CANCELLED':
            # Invalidate all tickets and notify students
            for reg in event.registrations.filter_by(status='CONFIRMED').all():
                reg.status = 'CANCELLED'
                reg.cancelled_at = datetime.utcnow()
                reg.cancellation_reason = "Event cancelled by administration."
                if reg.ticket:
                    reg.ticket.is_valid = False
                GamificationService.award_points(reg.user_id, -3, 'CANCELLATION', related_event_id=event.id)
                NotificationService.create_notification(
                    user_id=reg.user_id,
                    notif_type='EVENT_CANCELLED',
                    title=f"Event Cancelled: {event.title}",
                    message=f"The event '{event.title}' scheduled for {event.start_datetime.strftime('%b %d, %Y')} has been cancelled.",
                    related_event_id=event.id,
                    send_email_alert=True,
                    user_email=reg.user.email
                )

        event.status = new_status
        db.session.commit()
        return event

    @staticmethod
    def assign_coordinator(event_id, coordinator_id, assigned_by_id, role_in_event='Support'):
        existing = EventCoordinator.query.filter_by(event_id=event_id, coordinator_id=coordinator_id).first()
        if existing:
            existing.role_in_event = role_in_event
            db.session.commit()
            return existing

        assignment = EventCoordinator(
            event_id=event_id,
            coordinator_id=coordinator_id,
            role_in_event=role_in_event,
            assigned_by=assigned_by_id
        )
        db.session.add(assignment)
        db.session.commit()

        # Send notification to coordinator
        NotificationService.create_notification(
            user_id=coordinator_id,
            notif_type='SYSTEM',
            title="Assigned as Coordinator",
            message=f"You have been assigned as a {role_in_event} coordinator for an event.",
            related_event_id=event_id
        )
        return assignment
