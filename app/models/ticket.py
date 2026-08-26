from datetime import datetime
from app.extensions import db

class EventTicket(db.Model):
    __tablename__ = 'event_tickets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('event_registrations.id', ondelete='CASCADE'), unique=True, nullable=False)
    ticket_code = db.Column(db.String(100), unique=True, nullable=False, index=True) # ITSA-TKT-{uuid4}
    qr_image_path = db.Column(db.String(255), nullable=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_valid = db.Column(db.Boolean, default=True, nullable=False, index=True)

    attendance = db.relationship('Attendance', backref='ticket', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'registration_id': self.registration_id,
            'ticket_code': self.ticket_code,
            'qr_image_path': self.qr_image_path,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'is_valid': self.is_valid
        }
