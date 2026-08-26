# System Architecture — ITSA Platform

## 1. Architecture Overview

The ITSA Platform uses a **Monolithic Flask Architecture** — a single deployable Python application that handles all features.

### Why Monolithic?
- **College development team**: Easier for a small team to understand and maintain
- **Single deployment**: One Render service, simple CI/CD
- **Shared database**: No inter-service communication complexity
- **Simpler debugging**: One codebase, one log stream
- **Appropriate scale**: College platform with hundreds, not millions, of users

---

## 2. Application Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│          HTML5 + Bootstrap 5 + JavaScript + Chart.js         │
│              Jinja2 Templates + Static Files                 │
├─────────────────────────────────────────────────────────────┤
│                      API LAYER                               │
│            Flask Blueprints + Route Handlers                 │
│         Input validation, Auth checks, Response format       │
├─────────────────────────────────────────────────────────────┤
│                    SERVICE LAYER                             │
│               Business Logic + Domain Rules                  │
│        Registration rules, Points, AI orchestration          │
├─────────────────────────────────────────────────────────────┤
│                  REPOSITORY LAYER                            │
│              SQLAlchemy ORM Data Access                      │
│          Database queries, Joins, Aggregations               │
├─────────────────────────────────────────────────────────────┤
│                   DATABASE LAYER                             │
│                 MySQL 8.x via PyMySQL                        │
│          30 tables, Indexes, Foreign keys                    │
├──────────────────┬──────────────────────────────────────────┤
│   AI LAYER       │         FILE STORAGE LAYER               │
│  Gemini API      │    Local filesystem (uploads/)            │
│  Scikit-learn    │    Profiles, Posters, QR, Certs           │
│  ML Models       │                                           │
└──────────────────┴──────────────────────────────────────────┘
```

---

## 3. Module Architecture

### auth/ — Authentication & User Management
- User registration, login, logout
- Password hashing and verification
- Profile management
- Flask-Login user loader

### events/ — Event Management
- Event CRUD operations
- Event status machine
- Category and venue management
- Coordinator assignment
- Event search and filtering

### attendance/ — QR Attendance
- QR ticket generation
- Ticket validation (6-step)
- Attendance recording
- Duplicate prevention
- Live attendance tracking

### social/ — Community Feed
- Post creation and management
- Reactions, Comments, Replies
- Hashtag processing
- Mention processing
- Feed pagination
- Content reporting

### certificates/ — Certificate System
- PDF generation via ReportLab
- Certificate verification
- Download serving

### notifications/ — Notification System
- In-app notification creation
- Email dispatch via SMTP
- Bulk notifications

### analytics/ — Analytics & Reports
- Dashboard aggregations
- Chart data preparation
- PDF report generation

### ai/ — AI Integration
- Gemini API client
- ML model loading and prediction
- Recommendation engine
- Content moderation

### admin/ — Admin Panel
- User management
- Content moderation
- System settings
- Points management

---

## 4. Data Flow Architecture

### Standard Request Flow
```
HTTP Request
  → Nginx/Gunicorn
  → Flask Route Handler
    → Input Validation
    → Authentication Check (@login_required)
    → Authorization Check (@role_required)
    → Service Layer (business logic)
      → Repository Layer (database queries)
        → SQLAlchemy ORM
          → MySQL Database
      → Return domain object
    → Format response
  → HTTP Response (JSON)
```

### AI Request Flow
```
User Request
  → Flask Route
  → Rate Limit Check
  → AI Service
    → Sanitize user input
    → Build prompt (system + user message)
    → Call Gemini API / Load ML Model
    → Parse response
    → Return structured result
  → JSON Response
```

### File Upload Flow
```
Multipart Request
  → Flask Route
  → Validate file extension (whitelist)
  → Validate MIME type
  → Check file size
  → secure_filename()
  → Generate UUID filename
  → Save to uploads/{category}/
  → Store relative path in DB
  → Return file URL
```

---

## 5. Security Architecture

```
Request
  → HTTPS (Render provides TLS)
  → Flask-Login session validation
  → Role decorator check
  → Input sanitization
  → SQLAlchemy parameterized queries
  → File security checks
  → Jinja2 auto-escaping (output)
Response
```

---

## 6. Database Architecture

- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic)
- **Connection**: PyMySQL driver
- **Engine**: InnoDB (supports foreign keys, transactions)
- **Charset**: utf8mb4 (full Unicode including emoji)

---

## 7. AI Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Module (app/ai/)                   │
├─────────────────────┬───────────────────────────────────┤
│  GenAI (Gemini)     │  ML (Scikit-learn)                 │
│  gemini_client.py   │  recommendation.py                 │
│  prompts.py         │  prediction.py                     │
│  chatbot.py         │  engagement.py                     │
│  content_gen.py     │  models/ (joblib files)            │
│  moderation.py      │                                    │
│  feedback_ai.py     │                                    │
└─────────────────────┴───────────────────────────────────┘
```

**Gemini API**: REST API calls via google-generativeai SDK. Each feature has its own prompt template from `prompts.py`.

**ML Pipeline**: Models trained offline using historical data. Stored as `.joblib` files. Loaded at startup. Predictions served synchronously.

---

## 8. Directory Structure

```
itsa-platform/
├── app/
│   ├── __init__.py              # App factory (create_app)
│   ├── config.py                # Config classes (Dev/Prod/Test)
│   ├── extensions.py            # db, login_manager, migrate, etc.
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User, StudentProfile, CoordinatorProfile
│   │   ├── event.py             # Event, EventCategory, Venue, EventCoordinator
│   │   ├── registration.py      # EventRegistration
│   │   ├── ticket.py            # EventTicket
│   │   ├── attendance.py        # Attendance
│   │   ├── certificate.py       # Certificate
│   │   ├── feedback.py          # Feedback
│   │   ├── post.py              # Post, PostMedia, PostReaction
│   │   ├── comment.py           # Comment, CommentReply
│   │   ├── social.py            # PostShare, SavedPost, Hashtag, Mention
│   │   ├── notification.py      # Notification
│   │   ├── gamification.py      # ItsaPoints
│   │   ├── report.py            # Report
│   │   ├── gallery.py           # EventGallery, EventVolunteer
│   │   ├── ai_models.py         # AiRecommendation, AiAnalysis
│   │   └── audit.py             # AuditLog
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # /api/v1/auth/*
│   │   ├── events.py            # /api/v1/events/*
│   │   ├── tickets.py           # /api/v1/tickets/*
│   │   ├── attendance.py        # /api/v1/attendance/*
│   │   ├── posts.py             # /api/v1/posts/*
│   │   ├── comments.py          # /api/v1/comments/*
│   │   ├── certificates.py      # /api/v1/certificates/*
│   │   ├── feedback.py          # /api/v1/feedback/*
│   │   ├── notifications.py     # /api/v1/notifications/*
│   │   ├── gamification.py      # /api/v1/points/*, /api/v1/leaderboard
│   │   ├── hashtags.py          # /api/v1/hashtags/*
│   │   ├── admin.py             # /api/v1/admin/*
│   │   ├── ai.py                # /api/v1/ai/*
│   │   └── pages.py             # HTML page routes (non-API)
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── event_service.py
│   │   ├── registration_service.py
│   │   ├── ticket_service.py
│   │   ├── attendance_service.py
│   │   ├── social_service.py
│   │   ├── certificate_service.py
│   │   ├── feedback_service.py
│   │   ├── notification_service.py
│   │   ├── gamification_service.py
│   │   ├── analytics_service.py
│   │   ├── admin_service.py
│   │   └── ai_service.py
│   │
│   ├── repositories/
│   │   ├── user_repo.py
│   │   ├── event_repo.py
│   │   ├── registration_repo.py
│   │   ├── attendance_repo.py
│   │   ├── post_repo.py
│   │   ├── certificate_repo.py
│   │   └── analytics_repo.py
│   │
│   ├── schemas/
│   │   ├── auth_schemas.py      # Request/response schemas
│   │   ├── event_schemas.py
│   │   ├── post_schemas.py
│   │   └── ...
│   │
│   ├── utils/
│   │   ├── decorators.py        # @admin_required, @coordinator_required
│   │   ├── validators.py        # Input validation functions
│   │   ├── responses.py         # Standard API response helpers
│   │   ├── file_utils.py        # File upload helpers
│   │   ├── email_utils.py       # SMTP email functions
│   │   └── pagination.py        # Pagination helpers
│   │
│   ├── ai/
│   │   ├── gemini_client.py     # Gemini API wrapper
│   │   ├── prompts.py           # All Gemini prompts
│   │   ├── chatbot.py           # Chatbot logic
│   │   ├── content_gen.py       # Description/announcement/caption
│   │   ├── moderation.py        # Content moderation
│   │   ├── feedback_ai.py       # Feedback analysis
│   │   ├── recommendation.py    # Scikit-learn recommendations
│   │   ├── prediction.py        # Registration prediction
│   │   ├── engagement.py        # Engagement score
│   │   └── ml_models/           # Stored .joblib model files
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── student/
│   │   ├── coordinator/
│   │   ├── admin/
│   │   ├── public/
│   │   └── emails/
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
│
├── migrations/                  # Flask-Migrate / Alembic
├── tests/                       # pytest test suite
├── docs/                        # This documentation
├── uploads/                     # User-uploaded files (gitignored)
│   ├── profiles/
│   ├── events/posters/
│   ├── posts/images/
│   ├── posts/videos/
│   ├── gallery/
│   ├── tickets/
│   └── certificates/
├── scripts/
│   ├── seed_db.py               # Seed initial data
│   └── create_admin.py          # Create first admin account
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py                       # Entry point
└── README.md
```

---

## 9. Deployment Architecture (Render)

```
GitHub Repository
  → Push to main
  → Render auto-deploy
  → pip install -r requirements.txt
  → flask db upgrade
  → gunicorn run:app --bind 0.0.0.0:$PORT --workers 2
```

External services:
- **MySQL**: PlanetScale or Railway (free tier)
- **Gemini API**: Google AI Studio
- **SMTP**: Gmail App Password or SendGrid
