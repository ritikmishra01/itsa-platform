# Technology Stack — ITSA Platform

## Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Primary programming language |
| Flask | 3.x | Web framework (routes, templating, WSGI) |
| Flask-SQLAlchemy | 3.x | ORM integration with Flask |
| SQLAlchemy | 2.x | ORM for MySQL interaction |
| Flask-Login | 0.6.x | User session management |
| Flask-Migrate | 4.x | Database migration (Alembic wrapper) |
| Flask-CORS | 4.x | CORS headers for API |
| Flask-Limiter | 3.x | Rate limiting |
| Werkzeug | 3.x | Password hashing, secure_filename |
| PyMySQL | 1.x | MySQL driver for Python |
| python-dotenv | 1.x | Load .env into environment |

## Database

| Technology | Version | Purpose |
|---|---|---|
| MySQL | 8.x | Primary relational database |
| InnoDB | — | Storage engine (transactions, FK) |

## Frontend

| Technology | Version | Purpose |
|---|---|---|
| HTML5 | — | Page structure |
| CSS3 | — | Styling |
| JavaScript | ES6+ | Client interactivity |
| Bootstrap | 5.3 | Responsive UI components |
| Chart.js | 4.x | Analytics charts |
| html5-qrcode | 2.x | Browser-based QR scanning |

## AI & ML

| Technology | Version | Purpose |
|---|---|---|
| google-generativeai | latest | Gemini API SDK |
| Scikit-learn | 1.x | ML models (recommendations, prediction) |
| Pandas | 2.x | Data manipulation and analytics |
| NumPy | 1.x | Numerical operations |

## Utilities

| Technology | Purpose |
|---|---|
| qrcode[pil] | Generate QR code PNG images |
| Pillow | Image processing |
| ReportLab | PDF certificate generation |
| smtplib (stdlib) | Email sending |
| uuid (stdlib) | UUID generation for ticket codes |
| joblib | Serialize/deserialize ML models |

## Computer Vision

| Technology | Purpose |
|---|---|
| OpenCV (cv2) | Optional: server-side QR decoding for uploaded QR images |

## DevOps

| Technology | Purpose |
|---|---|
| Git | Version control |
| GitHub | Remote repository |
| Gunicorn | Production WSGI server |
| Render | Cloud deployment platform |

---

## requirements.txt

`
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Migrate==4.0.7
Flask-CORS==4.0.1
Flask-Limiter==3.7.0
SQLAlchemy==2.0.31
PyMySQL==1.1.1
Werkzeug==3.0.3
python-dotenv==1.0.1
google-generativeai==0.7.2
scikit-learn==1.5.1
pandas==2.2.2
numpy==1.26.4
qrcode[pil]==7.4.2
Pillow==10.4.0
reportlab==4.2.2
joblib==1.4.2
opencv-python-headless==4.10.0.84
gunicorn==22.0.0
`
"@ | Out-File -FilePath "C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\docs\TECH_STACK.md" -Encoding utf8
Write-Host "TECH_STACK.md done"

# AUTHENTICATION.md
@"
# Authentication — ITSA Platform

## Overview

Authentication uses **Flask-Login** with server-side sessions. No JWT tokens.

## Registration Flow

1. POST /api/v1/auth/register with email, password, full_name, student_id, department, year_of_study
2. Validate all fields (see VALIDATION_RULES.md)
3. Check email uniqueness in users table
4. Check student_id uniqueness in student_profiles table
5. Hash password: generate_password_hash(password)
6. Create User record (role=STUDENT)
7. Create StudentProfile record
8. Auto-login the new user
9. Return 201 with user data

## Login Flow

1. POST /api/v1/auth/login with email and password
2. Find User by email
3. Check is_suspended = FALSE
4. Check is_active = TRUE
5. Verify password: check_password_hash(user.password_hash, password)
6. login_user(user, remember=remember_me)
7. Return 200 with user data

## Session Management

Flask-Login sets a session cookie on login. The session is stored server-side.
Cookie properties (set in config):
`python
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True  # Production only
PERMANENT_SESSION_LIFETIME = timedelta(days=1)
`

## UserLoader

`python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
`

## Protected Routes

`python
@app.route('/api/v1/posts')
@login_required
def get_posts():
    ...
`

## Role Decorators

`python
from functools import wraps
from flask_login import current_user
from flask import jsonify

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"success": False, "error": {"code": "AUTH_NOT_AUTHENTICATED"}}), 401
        if current_user.role != 'ADMIN':
            return jsonify({"success": False, "error": {"code": "AUTH_INSUFFICIENT_ROLE"}}), 403
        return f(*args, **kwargs)
    return decorated

def coordinator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"success": False, "error": {"code": "AUTH_NOT_AUTHENTICATED"}}), 401
        if current_user.role not in ('COORDINATOR', 'ADMIN'):
            return jsonify({"success": False, "error": {"code": "AUTH_INSUFFICIENT_ROLE"}}), 403
        return f(*args, **kwargs)
    return decorated
`

## Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 digit (0-9)
- No maximum (up to 128 characters)

## Logout

`python
@app.route('/api/v1/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out"})
`
"@ | Out-File -FilePath "C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\docs\AUTHENTICATION.md" -Encoding utf8
Write-Host "AUTHENTICATION.md done"

# AUTHORIZATION.md
@"
# Authorization — ITSA Platform

## Role-Based Access Control (RBAC)

Three roles with increasing privileges: STUDENT < COORDINATOR < ADMIN

## Role Decorators

See AUTHENTICATION.md for decorator implementations.

Available decorators:
- @login_required — Any authenticated user
- @coordinator_required — COORDINATOR or ADMIN
- @admin_required — ADMIN only

## Resource-Level Authorization

Beyond role checks, some resources require ownership/assignment verification:

**Events (Coordinator)**:
`python
def check_coordinator_assigned(coordinator_id, event_id):
    assignment = EventCoordinator.query.filter_by(
        event_id=event_id,
        coordinator_id=coordinator_id
    ).first()
    if not assignment:
        raise AuthorizationError("ATT_COORDINATOR_NOT_ASSIGNED")
`

**Posts/Comments (Owner)**:
`python
def check_post_owner(user_id, post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != user_id and current_user.role != 'ADMIN':
        raise AuthorizationError("SOCIAL_NOT_OWNER")
`

## Permission Matrix

| Action | STUDENT | COORDINATOR | ADMIN |
|---|---|---|---|
| Register | ✅ | ❌ | ❌ |
| Create Event | ❌ | ✅ (assigned) | ✅ |
| Scan QR Attendance | ❌ | ✅ (assigned) | ✅ |
| Override Attendance | ❌ | ❌ | ✅ |
| Delete Any Post | ❌ | ❌ | ✅ |
| Suspend User | ❌ | ❌ | ✅ |
| View System Analytics | ❌ | ❌ | ✅ |
| Award Points Manually | ❌ | ❌ | ✅ |

## Rules

1. Never trust client-supplied role information
2. Read role from database via current_user.role (loaded by Flask-Login's user_loader)
3. Coordinators always checked against event_coordinators table
4. HTTP 403 returned (not 404) when user is authenticated but lacks permission
5. HTTP 401 returned when user is not authenticated at all
