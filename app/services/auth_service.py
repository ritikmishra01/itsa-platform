from datetime import datetime
from app.extensions import db
from app.models.user import User, StudentProfile, CoordinatorProfile
from app.utils.validators import validate_email, validate_password
from app.models.audit import AuditLog

class AuthService:
    @staticmethod
    def register_student(email, password, full_name, student_id, department, year_of_study, phone=None, bio=None):
        if not validate_email(email):
            raise ValueError("Invalid email format.")

        valid_pw, pw_msg = validate_password(password)
        if not valid_pw:
            raise ValueError(pw_msg)

        if User.query.filter_by(email=email.strip().lower()).first():
            raise ValueError("An account with this email already exists.")

        if StudentProfile.query.filter_by(student_id=student_id.strip()).first():
            raise ValueError("A student profile with this Student ID/Roll number already exists.")

        try:
            year_int = int(year_of_study)
            if year_int not in (1, 2, 3, 4):
                raise ValueError("Year of study must be 1, 2, 3, or 4.")
        except (TypeError, ValueError):
            raise ValueError("Year of study must be an integer between 1 and 4.")

        user = User(
            email=email.strip().lower(),
            full_name=full_name.strip(),
            role='STUDENT',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # Get user.id

        profile = StudentProfile(
            user_id=user.id,
            student_id=student_id.strip().upper(),
            department=department.strip(),
            year_of_study=year_int,
            phone=phone.strip() if phone else None,
            bio=bio.strip() if bio else None,
            total_points=0
        )
        db.session.add(profile)
        db.session.commit()
        return user

    @staticmethod
    def authenticate(email, password):
        if not email or not password:
            return None, "Email and password are required."

        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user or not user.check_password(password):
            return None, "Invalid email or password."

        if not user.is_active:
            return None, "Your account is inactive. Please contact ITSA administration."

        if user.is_suspended:
            return None, "Your account has been suspended. Please contact ITSA administration."

        return user, None

    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValueError("Current password is incorrect.")

        valid_pw, pw_msg = validate_password(new_password)
        if not valid_pw:
            raise ValueError(pw_msg)

        user.set_password(new_password)
        db.session.commit()
        return True

    @staticmethod
    def update_profile(user, data, profile_image_path=None):
        if 'full_name' in data and data['full_name']:
            user.full_name = data['full_name'].strip()

        if profile_image_path:
            user.profile_image = profile_image_path

        if user.role == 'STUDENT' and user.student_profile:
            sp = user.student_profile
            if 'department' in data and data['department']:
                sp.department = data['department'].strip()
            if 'year_of_study' in data and data['year_of_study']:
                try:
                    sp.year_of_study = int(data['year_of_study'])
                except (ValueError, TypeError):
                    pass
            if 'bio' in data:
                sp.bio = data['bio'].strip()
            if 'interests' in data:
                sp.interests = data['interests'].strip()
            if 'phone' in data:
                sp.phone = data['phone'].strip()
            if 'github_url' in data:
                sp.github_url = data['github_url'].strip()
            if 'linkedin_url' in data:
                sp.linkedin_url = data['linkedin_url'].strip()

        elif user.role == 'COORDINATOR' and user.coordinator_profile:
            cp = user.coordinator_profile
            if 'designation' in data:
                cp.designation = data['designation'].strip()
            if 'department' in data:
                cp.department = data['department'].strip()
            if 'phone' in data:
                cp.phone = data['phone'].strip()

        db.session.commit()
        return user
