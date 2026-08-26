from datetime import datetime
from app.extensions import db

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_event_user_reg'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    registration_number = db.Column(db.String(100), unique=True, nullable=False) # ITSA-{EVENT}-{YEAR}-{SEQ}
    status = db.Column(
        db.Enum('CONFIRMED', 'CANCELLED', 'WAITLISTED', name='registration_statuses'),
        default='CONFIRMED',
        nullable=False,
        index=True
    )
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)

    ticket = db.relationship('EventTicket', backref='registration', uselist=False, cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='registration', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'user_id': self.user_id,
            'student_name': self.user.full_name if self.user else None,
            'registration_number': self.registration_number,
            'status': self.status,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason,
            'ticket': self.ticket.to_dict() if self.ticket else None
        }
