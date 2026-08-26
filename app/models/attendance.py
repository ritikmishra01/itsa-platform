from datetime import datetime
from app.extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_attendance_event_user'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('event_registrations.id', ondelete='CASCADE'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('event_tickets.id', ondelete='RESTRICT'), nullable=False)
    scanned_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum('PRESENT', 'ABSENT', 'LATE', name='attendance_statuses'),
        default='PRESENT',
        nullable=False
    )
    notes = db.Column(db.Text, nullable=True)

    certificate = db.relationship('Certificate', backref='attendance', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'user_id': self.user_id,
            'student_name': self.student.full_name if self.student else None,
            'student_id': self.student.student_profile.student_id if self.student and self.student.student_profile else None,
            'department': self.student.student_profile.department if self.student and self.student.student_profile else None,
            'registration_id': self.registration_id,
            'ticket_id': self.ticket_id,
            'scanned_by': self.scanned_by,
            'coordinator_name': self.coordinator.full_name if self.coordinator else None,
            'scanned_at': self.scanned_at.isoformat() if self.scanned_at else None,
            'status': self.status,
            'notes': self.notes
        }
