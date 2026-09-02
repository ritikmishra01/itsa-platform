# ITSA Platform: Backend Architecture & Documentation

## 1. Overview
The backend of the **ITSA AI-Powered Event Management & Student Engagement Platform** follows a modular, monolithic Flask service-oriented architecture. Built with Python 3.11+, it implements the **Application Factory Pattern** (`create_app()`) and enforces strict separation of concerns between:
- **Routes / Blueprints** (HTTP request validation, serialization, and presentation views)
- **Services** (Domain business logic, transactions, points calculation, and external integrations)
- **Models** (SQLAlchemy database schemas, constraints, and relationships)
- **Utilities** (Security decorators, file handling, QR generation, and JSON responders)

---

## 2. Backend Technologies Actually Used

| Component | Technology / Library | Purpose in Platform |
| :--- | :--- | :--- |
| **Core Framework** | Python 3.11+ / Flask 3.0+ | Core WSGI application, routing, and lifecycle management. |
| **Database ORM** | Flask-SQLAlchemy / SQLAlchemy 2.0 | Object-Relational Mapping, relational modeling, and query execution. |
| **Database Drivers** | `psycopg2-binary`, SQLite | Native connection drivers for production PostgreSQL and local SQLite. |
| **Authentication** | Flask-Login 0.6+ | Session state management, `user_loader`, and remember-me token handling. |
| **Password Security**| Werkzeug 3.0+ | Cryptographic password hashing (`generate_password_hash`, `check_password_hash`). |
| **Rate Limiting** | Flask-Limiter | DoS prevention and endpoint abuse protection on authentication and AI routes. |
| **CORS** | Flask-CORS | Cross-Origin Resource Sharing handling for REST API routes. |
| **Migrations** | Flask-Migrate / Alembic | Schema version tracking and database migration operations. |
| **AI / GenAI** | `google-generativeai` (Gemini 2.0 Flash) | Event descriptions, announcement drafting, content moderation, sentiment analysis. |
| **Machine Learning** | `scikit-learn` / `numpy` | TF-IDF content-based event recommendation engine and engagement scoring. |
| **QR Code Engine** | `qrcode` / Pillow | Dynamic generation of unique ticket QR codes and certificate verification links. |
| **PDF Generation** | ReportLab 4.0+ | Programmatic creation of high-resolution, branded student certificates. |
| **Production Server**| Gunicorn 21.2+ | Production WSGI HTTP server with multi-worker concurrency. |

---

## 3. Backend Component Organization

| Component | File / Folder | Purpose |
| :--- | :--- | :--- |
| **Application Factory** | `app/__init__.py` | Initializes Flask app, registers blueprints, configures logging, and sets security headers. |
| **Configuration** | `app/config.py` | Environment-aware configs (`DevelopmentConfig`, `ProductionConfig`, `TestingConfig`). |
| **Extensions** | `app/extensions.py` | Centralized instantiation of `db`, `login_manager`, `migrate`, `cors`, and `limiter`. |
| **Entry Point** | `run.py` | Local development entry point and shell context configuration. |
| **User Models** | `app/models/user.py` | `User`, `StudentProfile`, `CoordinatorProfile`. |
| **Event Models** | `app/models/event.py` | `Event`, `EventCategory`, `Venue`, `EventCoordinator`. |
| **Registration Models**| `app/models/registration.py` | `EventRegistration`. |
| **Ticket Models** | `app/models/ticket.py` | `EventTicket`. |
| **Attendance Models** | `app/models/attendance.py` | `Attendance` records and coordinator scan logs. |
| **Certificate Models**| `app/models/certificate.py` | `Certificate` records, unique verification codes, and PDF paths. |
| **Feedback Models** | `app/models/feedback.py` | `Feedback` submissions, ratings, and AI sentiment analysis. |
| **Social Models** | `app/models/post.py`, `comment.py` | Posts, media attachments, reactions, comments, and replies. |
| **Notification Models**| `app/models/notification.py`| Targeted notifications and system broadcast logs. |
| **Gamification Models**| `app/models/gamification.py`| `ItsaPoints` transaction ledger and points history. |
| **Gallery Models** | `app/models/gallery.py` | `EventGallery` media assets. |
| **Moderation Models** | `app/models/report.py` | `Report` queues for flagged posts and comments. |
| **AI Models** | `app/models/ai.py` | `AiRecommendation` and `AiAnalysis` cached logs. |
| **Audit Models** | `app/models/audit.py` | `AuditLog` immutable administrative tracking. |
| **Auth Service** | `app/services/auth_service.py` | User registration, authentication verification, and profile management. |
| **Event Service** | `app/services/event_service.py`| Event creation, status transitions, publishing, and filtering. |
| **Ticket Service** | `app/services/ticket_service.py`| Automated ticket code generation and QR code image rendering. |
| **Attendance Service**| `app/services/attendance_service.py`| QR ticket validation, duplicate entry prevention, and scan recording. |
| **Certificate Service**| `app/services/certificate_service.py`| ReportLab PDF certificate generation, verification, and downloads. |
| **Social Service** | `app/services/social_service.py`| Feed posts, comments, reactions, and report filing. |
| **Feedback Service**| `app/services/feedback_service.py`| Student feedback recording and automatic points reward dispatch. |
| **Notification Service**| `app/services/notification_service.py`| Role-based broadcasts, targeted alerts, and read status management. |
| **Gamification Service**| `app/services/gamification_service.py`| Points awarding, deductions, and leaderboard calculations. |
| **AI Service** | `app/services/ai_service.py`| Google Gemini API client, TF-IDF event recommendations, sentiment analyzer. |
| **Analytics Service** | `app/services/analytics_service.py`| Aggregations for department participation, attendance rates, and trends. |
| **Decorators** | `app/utils/decorators.py` | `@student_required`, `@coordinator_required`, `@admin_required`. |
| **Responses** | `app/utils/responses.py` | Standardized `success_response` and `error_response` JSON structures. |
| **File Utils** | `app/utils/file_utils.py` | Secure filename handling, extension validation, and upload path storage. |

---

## 4. Route Blueprints & API Endpoints

The application registers 14 dedicated Flask Blueprints in `app/routes/__init__.py`:

1. **`pages_bp` (`app/routes/pages.py`)**: Web views for Public, Student, Coordinator, and Admin interfaces.
2. **`auth_bp` (`/api/v1/auth`)**: Registration, login, logout, profile updates, and active session retrieval.
3. **`events_bp` (`/api/v1/events`)**: Event CRUD, publishing, cancellation, registration, and attendee rosters.
4. **`tickets_bp` (`/api/v1/tickets`)**: Ticket retrieval and QR code asset fetching.
5. **`attendance_bp` (`/api/v1/attendance`)**: Coordinator QR code scanner endpoint and personal attendance histories.
6. **`certificates_bp` (`/api/v1/certificates`)**: Certificate retrieval, PDF download, and public verification lookup.
7. **`posts_bp` (`/api/v1/posts`)**: Social community feed, post publishing, deletions, and reactions.
8. **`comments_bp` (`/api/v1/comments`)**: Post comments, replies, and comment deletions.
9. **`feedback_bp` (`/api/v1/feedback`)**: Event rating and feedback submission.
10. **`notifications_bp` (`/api/v1/notifications`)**: User notification queue, read toggles, and bulk read operations.
11. **`gamification_bp` (`/api/v1/points`)**: Point ledger history and platform-wide leaderboard ranking.
12. **`admin_bp` (`/api/v1/admin`)**: User suspension, coordinator assignments, broadcast dispatch, and moderation.
13. **`ai_bp` (`/api/v1/ai`)**: Gemini AI chatbot interactions, event description generator, and recommendation queries.

---

## 5. Security & Session Architecture
- **Flask-Login Authentication**: User sessions are authenticated server-side using secure cookies.
- **Strict Role-Based Access Control (RBAC)**: All sensitive routes are safeguarded by custom decorators (`@student_required`, `@coordinator_required`, `@admin_required`).
- **Comprehensive Cookie Clearing**: During logout, both `remember_token` and `session` cookies are deleted with matching `HttpOnly`, `SameSite=Lax`, and standard path/domain parameters to ensure complete cookie destruction across all modern web browsers.
- **Anti-Caching HTTP Headers**: `@app.after_request` serves `Cache-Control: no-store, no-cache, must-revalidate, max-age=0, private`, `Pragma: no-cache`, and `Expires: 0` for dynamic routes, preventing backward navigation from exposing cached views.