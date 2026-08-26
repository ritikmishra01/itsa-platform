from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('STUDENT', 'COORDINATOR', 'ADMIN', name='user_roles'), default='STUDENT', nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_suspended = db.Column(db.Boolean, default=False, nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    coordinator_profile = db.relationship('CoordinatorProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    registrations = db.relationship('EventRegistration', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', foreign_keys='Attendance.user_id', backref='student', lazy='dynamic')
    scanned_attendances = db.relationship('Attendance', foreign_keys='Attendance.scanned_by', backref='coordinator', lazy='dynamic')
    certificates = db.relationship('Certificate', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    feedback_submissions = db.relationship('Feedback', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('PostReaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    saved_posts = db.relationship('SavedPost', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='recipient', lazy='dynamic', cascade='all, delete-orphan')
    points_transactions = db.relationship('ItsaPoints', foreign_keys='ItsaPoints.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    created_events = db.relationship('Event', backref='creator', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_student(self):
        return self.role == 'STUDENT'

    @property
    def is_coordinator(self):
        return self.role == 'COORDINATOR'

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    def to_dict(self):
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_suspended': self.is_suspended,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if self.student_profile:
            data['student_profile'] = self.student_profile.to_dict()
        elif self.coordinator_profile:
            data['coordinator_profile'] = self.coordinator_profile.to_dict()
        return data


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True) # Roll number
    department = db.Column(db.String(100), nullable=False, index=True)
    year_of_study = db.Column(db.SmallInteger, nullable=False, index=True) # 1, 2, 3, 4
    bio = db.Column(db.Text, nullable=True)
    interests = db.Column(db.Text, nullable=True) # Comma-separated or JSON
    phone = db.Column(db.String(20), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    total_points = db.Column(db.Integer, default=0, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.student_id,
            'department': self.department,
            'year_of_study': self.year_of_study,
            'bio': self.bio,
            'interests': self.interests,
            'phone': self.phone,
            'github_url': self.github_url,
            'linkedin_url': self.linkedin_url,
            'total_points': self.total_points
        }


class CoordinatorProfile(db.Model):
    __tablename__ = 'coordinator_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    employee_id = db.Column(db.String(50), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'designation': self.designation,
            'department': self.department,
            'phone': self.phone
        }
