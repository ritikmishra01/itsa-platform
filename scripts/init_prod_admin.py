import os
import sys
import secrets

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.event import EventCategory, Venue

def init_production_system(app=None):
    env = os.environ.get('FLASK_ENV', 'production')
    if app is None:
        try:
            app = create_app(env)
        except Exception as e:
            print(f"[!] Configuration Error during application startup: {e}")
            print("[!] Please verify your DATABASE_URL environment variable in Render.")
            sys.exit(1)

    try:
        with app.app_context():
            print(f"[*] Initializing ITSA Platform in [{env}] mode...")
            db.create_all()
            db.session.expire_all()

            # 1. Initialize Essential Event Categories if empty
            categories = [
                ("Technical", "Hackathons, coding contests, and developer challenges", "bi-code-slash"),
                ("Workshop", "Hands-on engineering workshops and bootcamps", "bi-tools"),
                ("Seminar", "Guest lectures by tech industry experts", "bi-mic"),
                ("Cultural", "Music, dance, drama, and artistic performances", "bi-music-note"),
                ("Sports", "Inter-department sports and athletic competitions", "bi-trophy"),
                ("Competition", "Quizzes, project expos, and debates", "bi-award"),
                ("Community Service", "Social outreach and student engagement initiatives", "bi-heart"),
                ("Other", "General meetups and informal gatherings", "bi-three-dots")
            ]

            for name, desc, icon in categories:
                if not EventCategory.query.filter_by(name=name).first():
                    db.session.add(EventCategory(name=name, description=desc, icon=icon))
            db.session.commit()
            print("[+] Essential event categories initialized.")

            # 2. Initialize Default Venue if empty
            if Venue.query.count() == 0:
                db.session.add(Venue(
                    name="Main University Auditorium",
                    address="Central University Campus",
                    capacity=500,
                    room_number="Aud-1",
                    building="Main Block"
                ))
                db.session.commit()
                print("[+] Default venue registered.")

            # 3. Create or Synchronize Production Administrator
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@itsa.edu').strip().lower()
            admin_password = os.environ.get('ADMIN_PASSWORD')
            admin_name = os.environ.get('ADMIN_NAME', 'ITSA Administrator').strip()

            clean_pw = admin_password.strip().strip('"\'') if admin_password and admin_password.strip() else None

            # Look for existing admin by email first, then by role
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User.query.filter_by(role='ADMIN').first()

            if not admin:
                # No admin exists: Create the initial administrator account
                pass_to_set = clean_pw if clean_pw else secrets.token_urlsafe(16)

                admin = User(
                    email=admin_email,
                    full_name=admin_name,
                    role='ADMIN',
                    is_active=True,
                    is_suspended=False
                )
                admin.set_password(pass_to_set)
                db.session.add(admin)
                db.session.commit()
                print(f"[+] Production Administrator account created successfully for {admin_email}.")
            else:
                # Admin account exists: Ensure account is active and synchronize credentials if configured
                updated = False
                if admin.email != admin_email:
                    admin.email = admin_email
                    updated = True
                if admin.role != 'ADMIN':
                    admin.role = 'ADMIN'
                    updated = True
                if not admin.is_active:
                    admin.is_active = True
                    updated = True
                if admin.is_suspended:
                    admin.is_suspended = False
                    updated = True

                # Synchronize password with ADMIN_PASSWORD environment variable
                if clean_pw:
                    if not admin.check_password(clean_pw):
                        admin.set_password(clean_pw)
                        updated = True
                        print(f"[+] Production Administrator password synchronized with ADMIN_PASSWORD for {admin.email}.")
                    else:
                        print(f"[*] Production Administrator password is already up-to-date for {admin.email}.")
                else:
                    print(f"[*] Production Administrator exists ({admin.email}); preserving existing credentials.")

                if updated:
                    db.session.commit()
                    print(f"[+] Production Administrator account state confirmed for {admin.email}.")

            print("[OK] Production initialization completed successfully.")
    except Exception as e:
        print(f"[!] Database Connection / Initialization Error: {e}")
        print("[!] Please check database server status and credentials.")
        sys.exit(1)

if __name__ == '__main__':
    init_production_system()
