import os
import sys
import secrets

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.event import EventCategory, Venue

def init_production_system():
    env = os.environ.get('FLASK_ENV', 'production')
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

            # 3. Create or Verify Production Administrator
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@itsa.edu').strip().lower()
            admin_password = os.environ.get('ADMIN_PASSWORD')
            admin_name = os.environ.get('ADMIN_NAME', 'ITSA System Administrator').strip()

            admin = User.query.filter_by(role='ADMIN').first()
            if not admin:
                if not admin_password:
                    admin_password = secrets.token_urlsafe(16)
                    generated_pass = True
                else:
                    generated_pass = False

                admin = User(
                    email=admin_email,
                    full_name=admin_name,
                    role='ADMIN',
                    is_active=True,
                    is_suspended=False
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print("[+] Production Administrator account created successfully.")
                print(f"    Email: {admin_email}")
                if generated_pass:
                    print(f"    Temporary Generated Password: {admin_password}")
                    print("    IMPORTANT: Change this password immediately after first login!")
            else:
                print(f"[*] Production Administrator already exists ({admin.email}).")

            print("[OK] Production initialization completed successfully.")
    except Exception as e:
        print(f"[!] Database Connection / Initialization Error: {e}")
        print("[!] Please check database server status and credentials.")
        sys.exit(1)

if __name__ == '__main__':
    init_production_system()
