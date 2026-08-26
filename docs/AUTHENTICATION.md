# Authentication -- ITSA Platform

## Strategy
Flask-Login with server-side sessions. No JWT tokens. Session cookie is HttpOnly and SameSite=Lax.

## Registration Flow

1. POST /api/v1/auth/register
2. Validate fields: email format, password complexity, year 1-4, unique email, unique student_id
3. Hash password with Werkzeug generate_password_hash (PBKDF2-SHA256)
4. Create User record (role=STUDENT)
5. Create StudentProfile record
6. Auto-login via login_user(user)
7. Return 201 with user data

## Login Flow

1. POST /api/v1/auth/login
2. Find User by email
3. Check is_active=True and is_suspended=False
4. Verify password: check_password_hash(user.password_hash, provided_password)
5. Call login_user(user, remember=remember_me)
6. Return 200 with user data

## Session Management

Flask-Login stores user_id in signed session cookie.
Cookie properties: httponly=True, samesite=Lax, secure=True in production.
PERMANENT_SESSION_LIFETIME = 1 day.

## UserLoader

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

## Protected Routes

Use @login_required decorator from Flask-Login.
Unauthorized access redirects to /login for HTML pages or returns 401 JSON for API routes.

## Role Decorators

@admin_required -- checks current_user.role == ADMIN
@coordinator_required -- checks current_user.role in (COORDINATOR, ADMIN)

Decorators return 403 JSON if role is insufficient.

## Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 digit (0-9)

## Logout

POST /api/v1/auth/logout calls logout_user() and returns 200.
Session cookie is cleared automatically.

## Security Notes

- Passwords stored as hash only -- never plaintext
- Generic error messages for failed login (do not reveal if email exists)
- Role read from database on every request -- not from cookie
- Admin creates coordinator accounts -- coordinators cannot self-register
