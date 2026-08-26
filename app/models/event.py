from datetime import datetime
from app.extensions import db

class EventCategory(db.Model):
    __tablename__ = 'event_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True) # Bootstrap icon class
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    events = db.relationship('Event', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    room_number = db.Column(db.String(50), nullable=True)
    building = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    events = db.relationship('Event', backref='venue', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'capacity': self.capacity,
            'room_number': self.room_number,
            'building': self.building
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('event_categories.id', ondelete='SET NULL'), nullable=True, index=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='SET NULL'), nullable=True)
    poster_image = db.Column(db.String(255), nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False, index=True)
    end_datetime = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, nullable=True) # Null = unlimited
    current_registrations = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(
        db.Enum('DRAFT', 'PUBLISHED', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'ONGOING', 'COMPLETED', 'CANCELLED', name='event_statuses'),
        default='DRAFT',
        nullable=False,
        index=True
    )
    is_free = db.Column(db.Boolean, default=True, nullable=False)
    registration_fee = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    tags = db.Column(db.String(500), nullable=True) # Comma-separated
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    coordinators = db.relationship('EventCoordinator', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    gallery_items = db.relationship('EventGallery', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    volunteers = db.relationship('EventVolunteer', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='linked_event', lazy='dynamic')

    def is_registration_open(self):
        now = datetime.utcnow()
        if self.status != 'REGISTRATION_OPEN':
            return False
        if now > self.registration_deadline:
            return False
        if self.max_participants and self.current_registrations >= self.max_participants:
            return False
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'venue_id': self.venue_id,
            'venue_name': self.venue.name if self.venue else None,
            'poster_image': self.poster_image,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'max_participants': self.max_participants,
            'current_registrations': self.current_registrations,
            'status': self.status,
            'is_free': self.is_free,
            'registration_fee': float(self.registration_fee) if self.registration_fee else 0.0,
            'tags': self.tags.split(',') if self.tags else [],
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EventCoordinator(db.Model):
    __tablename__ = 'event_coordinators'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'coordinator_id', name='uq_event_coordinator'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    coordinator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_in_event = db.Column(db.String(100), default='Support', nullable=True) # Lead, Support, Registration, etc.
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    coordinator = db.relationship('User', foreign_keys=[coordinator_id])
    assigner = db.relationship('User', foreign_keys=[assigned_by])

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'coordinator_id': self.coordinator_id,
            'coordinator_name': self.coordinator.full_name if self.coordinator else None,
            'coordinator_email': self.coordinator.email if self.coordinator else None,
            'role_in_event': self.role_in_event,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None
        }
