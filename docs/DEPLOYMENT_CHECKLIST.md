# ITSA Platform: Production Deployment & Verification Checklist

This checklist tracks the production readiness and post-deployment validation for the ITSA AI-Powered Event Management Platform.

---

## 1. Pre-Deployment Configuration & Codebase Audit

- [x] **Git Repository Ready**: Repository structured with clean application factory and entry point (`run.py`).
- [x] **Sensitive Files Excluded**: `.gitignore` strictly excludes `.env`, `venv/`, `__pycache__/`, `uploads/`, `*.db`, `*.log`.
- [x] **Environment Template Complete**: `.env.example` includes all required configuration parameters.
- [x] **Dependencies Verified**: `requirements.txt` contains pinned versions for Flask, SQLAlchemy, Gunicorn, PyMySQL, ReportLab, Gemini SDK, Scikit-learn, and dependencies.
- [x] **Cloud Database Compatibility**: SQLAlchemy database URL parser normalizes `mysql://` and `postgres://` for cloud providers.
- [x] **Production Initialization Ready**: `scripts/init_prod_admin.py` provides idempotent category seeding and secure admin account provisioning.
- [x] **Persistent Storage Configured**: Configurable `UPLOAD_FOLDER` supporting Render persistent disk mount (`/var/data/uploads`).
- [x] **AI Configuration & Graceful Fallback**: `GEMINI_API_KEY` loaded from environment variables with graceful error responses if unreachable.
- [x] **Gunicorn WSGI Server Configured**: `gunicorn "run:app" --workers 4 --bind 0.0.0.0:$PORT` configured for multi-process concurrency.
- [x] **Production Error Pages & Security**: User-friendly error templates for 400, 401, 403, 404, 429, 500 without stack trace exposure.
- [x] **Automated Test Suite Passing**: 100% test pass rate across 31 automated tests (`pytest`).

---

## 2. Render Cloud Deployment Steps

- [ ] **GitHub Repository Connected**: Web Service created on Render dashboard linked to repository `main` branch.
- [ ] **Persistent Disk Attached**: 5GB persistent disk mounted at `/var/data/uploads`.
- [ ] **Environment Variables Set**:
  - `FLASK_ENV=production`
  - `FLASK_DEBUG=False`
  - `SECRET_KEY` (Generated)
  - `DATABASE_URL` (Cloud Database URI)
  - `UPLOAD_FOLDER=/var/data/uploads`
  - `GEMINI_API_KEY`
  - `FRONTEND_URL=https://<your-service>.onrender.com`
  - `ADMIN_EMAIL=admin@itsa.edu`
  - `ADMIN_PASSWORD` (Secure production password)
  - `ADMIN_NAME=ITSA Administrator`
- [ ] **Build & Deploy Successful**: Build completes, pre-deploy script executes, and Gunicorn workers start listening.
- [ ] **Health Endpoint Operational**: `GET /health` returns HTTP 200 `{"status": "healthy"}`.

---

## 3. Post-Deployment User Flow Verification

### Authentication & Role Isolation
- [ ] **Student Registration & Login**: Student account created, profile initialized with 0 points.
- [ ] **Student Logout**: Session destroyed, redirected to `/login`, browser Back blocked.
- [ ] **Coordinator Login & Access**: Assigned events visible, scanner operational.
- [ ] **Coordinator Logout**: Session destroyed, redirected to `/login`.
- [ ] **Admin Login & Dashboard**: Control Center, analytics metrics, and module navigation functioning.
- [ ] **Admin Logout**: Session destroyed, redirected to `/login`.
- [ ] **RBAC Protection**: Student blocked from `/admin/*` and `/coordinator/*`; Coordinator blocked from `/admin/*`.

### Event Lifecycle & QR Attendance
- [ ] **Event Creation & Publishing**: Admin/Coordinator creates event with poster upload, sets status to `REGISTRATION_OPEN`.
- [ ] **Student Event Registration**: Student registers, receives unique registration ID and auto-generated QR ticket.
- [ ] **Coordinator QR Scanning**: Coordinator scans student QR ticket, attendance recorded as `PRESENT`, duplicate scans rejected with proper error message.
- [ ] **Points Awarded**: +3 for registration, +10 for verified attendance, reflected on leaderboard.

### Certificates & Verification
- [ ] **Certificate Auto-Generation**: Attendance triggers ReportLab PDF certificate with unique verification hash.
- [ ] **Public Verification Endpoint**: Visiting `/certificates/verify/<code_or_hash>` verifies validity and displays student/event details.
- [ ] **PDF Download**: Student downloads certificate PDF cleanly.

### Social Community & Moderation
- [ ] **Post Creation & Media**: Student creates post with hashtags and optional image upload.
- [ ] **Reactions & Comments**: Users react and comment on posts.
- [ ] **Content Reporting & Moderation**: Admin reviews report queue in `/admin/community`, resolves/dismisses flags, hides/restores content.

### Broadcast & Notifications
- [ ] **Admin Broadcast**: Admin sends broadcast to `ALL_STUDENTS` / `ALL_COORDINATORS`.
- [ ] **Inbox Delivery**: Notifications appear in Student and Coordinator inboxes; marking all as read updates badge count.

### AI Engine Validation
- [ ] **AI Chatbot**: Student asks ITSA Assistant questions and receives contextual answers.
- [ ] **AI Recommendations**: Student dashboard displays personalized event recommendations.
- [ ] **AI Moderation & Summaries**: Admin event summaries and sentiment analysis operate cleanly.
