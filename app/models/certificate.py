from datetime import datetime
from app.extensions import db

class Certificate(db.Model):
    __tablename__ = 'certificates'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='uq_cert_user_event'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance.id', ondelete='RESTRICT'), nullable=False)
    certificate_code = db.Column(db.String(100), unique=True, nullable=False, index=True) # ITSA-CERT-{uuid4}
    certificate_type = db.Column(
        db.Enum('PARTICIPATION', 'WINNER', 'VOLUNTEER', name='certificate_types'),
        default='PARTICIPATION',
        nullable=False
    )
    pdf_path = db.Column(db.String(255), nullable=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_valid = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_name': self.user.full_name if self.user else None,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'event_date': self.event.start_datetime.strftime('%B %d, %Y') if self.event and self.event.start_datetime else None,
            'certificate_code': self.certificate_code,
            'certificate_type': self.certificate_type,
            'pdf_path': self.pdf_path,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'is_valid': self.is_valid
        }
