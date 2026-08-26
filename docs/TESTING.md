# Testing -- ITSA Platform

## Testing Stack

- pytest -- test runner
- pytest-flask -- Flask test client integration
- pytest-cov -- coverage reporting
- SQLite in-memory -- test database (isolated, fast)

## Test Categories

1. Unit tests -- Service layer functions in isolation
2. Integration tests -- API endpoints (full request-response cycle)
3. Security tests -- Authorization, input validation, file uploads

## Test File Structure

tests/
-- conftest.py       (fixtures: app, client, db, users, events)
-- test_auth.py      (registration, login, logout, password change)
-- test_events.py    (CRUD, status workflow, coordinator assignment)
-- test_registration.py (register, cancel, capacity, deadline)
-- test_tickets.py   (generation, access control, invalidation)
-- test_attendance.py (scan, duplicate prevention, 6-step validation)
-- test_social.py    (posts, reactions, comments, replies, hashtags)
-- test_certificates.py (generation, download, verification)
-- test_feedback.py  (submission, eligibility, AI analysis mock)
-- test_notifications.py (creation, read, delete)
-- test_gamification.py (points, leaderboard, engagement score)
-- test_analytics.py (dashboard metrics, chart data)
-- test_ai.py        (chatbot mock, recommendations mock)
-- test_admin.py     (user management, moderation, reports)
-- test_coordinator.py (event access, attendance scanning)
-- test_security.py  (auth bypass, role elevation, injection attempts)
-- test_file_uploads.py (type validation, size limits, access control)

## conftest.py Key Fixtures

- app: Test Flask app with SQLite in-memory DB
- client: Flask test client
- db: Clean database per test
- student: Authenticated student user
- coordinator: Authenticated coordinator user
- admin: Authenticated admin user
- event: Sample REGISTRATION_OPEN event
- registration: Student registration for sample event
- ticket: Generated ticket for sample registration

## Running Tests

Run all tests: pytest tests/ -v
Run with coverage: pytest tests/ --cov=app --cov-report=html
Run single file: pytest tests/test_attendance.py -v

## Coverage Target

Minimum 80% line coverage across the app module.
Critical paths (attendance scan, registration) must have 100% coverage.

## Mocking External Services

Gemini API: Mock google.generativeai.GenerativeModel.generate_content()
Email SMTP: Mock smtplib.SMTP to prevent actual emails
ML Models: Use simple mock predictors that return fixed values
