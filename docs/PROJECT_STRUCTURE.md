# ITSA Platform: Repository File Structure & Component Reference

## 1. Project Directory Tree

```text
itsa-platform/
│
├── .env.example                 # Safe environment configuration template with empty placeholders
├── .gitignore                   # Comprehensive exclusion rules (secrets, venv, cache, db, uploads)
├── CHANGELOG.md                 # Version release notes and development milestone changelog
├── README.md                    # Root GitHub repository presentation document
├── render.yaml                  # Infrastructure-as-code blueprint for Render deployment
├── requirements.txt             # Verified Python package dependencies
├── run.py                       # Main application entry point for local development
│
├── app/                         # Core Application Package (Application Factory)
│   ├── __init__.py              # Factory create_app(), blueprint registration, security headers
│   ├── config.py                # Environment configurations (Development, Production, Testing)
│   ├── extensions.py            # Centralized instances: db, login_manager, migrate, limiter, cors
│   │
│   ├── models/                  # SQLAlchemy Relational Database Schemas (30 Tables)
│   │   ├── __init__.py          # Exports all models for centralized imports
│   │   ├── ai.py                # AiRecommendation, AiAnalysis
│   │   ├── attendance.py        # Attendance records (status, timestamp, scanned_by)
│   │   ├── audit.py             # AuditLog (immutable administrative security trails)
│   │   ├── certificate.py       # Certificate (unique code, PDF path, verification)
│   │   ├── comment.py           # Comment, CommentReply, Mention
│   │   ├── event.py             # Event, EventCategory, Venue, EventCoordinator
│   │   ├── feedback.py          # Feedback (rating, content, AI sentiment)
│   │   ├── gallery.py           # EventGallery (featured photography)
│   │   ├── gamification.py      # ItsaPoints transaction ledger
│   │   ├── notification.py      # Notification (in-app alerts and broadcast records)
│   │   ├── post.py              # Post, PostMedia, PostReaction, Hashtag, PostShare
│   │   ├── registration.py      # EventRegistration (confirmed, waitlisted, cancelled)
│   │   ├── report.py            # Report (community moderation queue)
│   │   ├── ticket.py            # EventTicket (unique ticket code, QR image path)
│   │   └── user.py              # User, StudentProfile, CoordinatorProfile
│   │
│   ├── routes/                  # HTTP Blueprints & API Endpoints
│   │   ├── __init__.py          # Blueprint registration orchestrator
│   │   ├── admin.py             # /api/v1/admin (user management, moderation, broadcasts)
│   │   ├── ai.py                # /api/v1/ai (chatbot, description generator, recommendations)
│   │   ├── attendance.py        # /api/v1/attendance (coordinator QR scanner)
│   │   ├── auth.py              # /api/v1/auth (registration, login, logout, profile)
│   │   ├── certificates.py      # /api/v1/certificates (download, verification lookup)
│   │   ├── comments.py          # /api/v1/comments (discussion threads and replies)
│   │   ├── events.py            # /api/v1/events (event lifecycle, CRUD, registration)
│   │   ├── feedback.py          # /api/v1/feedback (event reviews and ratings)
│   │   ├── gamification.py      # /api/v1/points (point history and leaderboard)
│   │   ├── notifications.py     # /api/v1/notifications (read status and counts)
│   │   ├── pages.py             # Web views (Public, Student, Coordinator, Admin UI)
│   │   ├── posts.py             # /api/v1/posts (community social feed)
│   │   └── tickets.py           # /api/v1/tickets (ticket retrieval and QR assets)
│   │
│   ├── services/                # Encapsulated Business Logic Layer
│   │   ├── ai_service.py        # Gemini API client, TF-IDF event recommendations
│   │   ├── analytics_service.py # Aggregated metrics and Chart.js datasets
│   │   ├── attendance_service.py# QR ticket validation, duplicate scan prevention
│   │   ├── auth_service.py      # User authentication, password verification
│   │   ├── certificate_service.py # ReportLab PDF generation and code verification
│   │   ├── event_service.py     # Event filtering, creation, publishing, status changes
│   │   ├── feedback_service.py  # Feedback processing and sentiment categorization
│   │   ├── gamification_service.py # Points allocation rules, leaderboard ranking
│   │   ├── notification_service.py # Email dispatch and in-app alert storage
│   │   ├── social_service.py    # Feed publishing, reactions, moderation filing
│   │   └── ticket_service.py    # Unique ticket code and QR image generation
│   │
│   ├── static/                  # Client-Side Static Assets
│   │   ├── css/
│   │   │   └── main.css         # Custom theme styles, CSS variables, card elevation
│   │   ├── js/
│   │   │   └── main.js          # Asynchronous apiCall wrapper, toasts, modals
│   │   └── img/
│   │       └── placeholder.svg  # Graphic fallback for posters and profiles
│   │
│   ├── templates/               # Jinja2 Server-Rendered HTML Templates
│   │   ├── base.html            # Universal master layout with navbar and role dropdown
│   │   ├── admin/               # 17 specialized Admin Control Center modules
│   │   ├── auth/                # Login and registration templates
│   │   ├── coordinator/         # Coordinator dashboard, QR scanner, event management
│   │   ├── errors/              # 400, 401, 403, 404, 429, 500 error pages
│   │   ├── public/              # Event directory, event detail, certificate verification
│   │   └── student/             # Student dashboard, feed, tickets, certificates, chatbot
│   │
│   └── utils/                   # Shared Helper Utilities
│       ├── decorators.py        # Role-based access control (@student_required, etc.)
│       ├── file_utils.py        # Secure file saving, extensions, and directory resolution
│       ├── qr_utils.py          # QRCode rendering with Pillow
│       └── responses.py         # Standardized JSON response envelopes
│
├── docs/                        # Complete Project Documentation Suite
│   ├── README.md                # Documentation index and overview
│   ├── FINAL_PROJECT_REPORT.md  # Comprehensive 49-section academic submission report
│   ├── PROJECT_OVERVIEW.md      # Vision, problem statement, and module summaries
│   ├── REQUIREMENTS.md          # Functional & Non-Functional requirements (FR/NFR)
│   ├── USER_ROLES.md            # Role matrix: Student, Coordinator, Admin
│   ├── USER_FLOWS.md            # Step-by-step user journeys and workflows
│   ├── SYSTEM_ARCHITECTURE.md   # Architectural layers and design patterns
│   ├── TECH_STACK.md            # Verified technologies, libraries, and frameworks
│   ├── FRONTEND.md              # Frontend templates, static files, and UI components
│   ├── BACKEND.md               # Backend routes, services, models, and security
│   ├── DATABASE_DESIGN.md       # Relational database schemas and table definitions
│   ├── DATABASE_SETUP.md        # SQLite and PostgreSQL configuration guide
│   ├── API_DOCUMENTATION.md     # REST API architecture, conventions, and status codes
│   ├── AUTHENTICATION.md        # Session authentication and cookie security
│   ├── EVENT_MANAGEMENT.md      # Event lifecycles, ticketing, and scheduling
│   ├── QR_ATTENDANCE.md         # QR scanning engine and duplicate entry prevention
│   ├── CERTIFICATE_SYSTEM.md    # ReportLab PDF certificates and public verification
│   ├── COMMUNITY.md             # Community social feed, media, and moderation
│   ├── NOTIFICATIONS.md         # Multi-channel notifications and admin broadcasts
│   ├── AI_FEATURES.md           # Gemini AI features and TF-IDF recommendations
│   ├── GAMIFICATION.md          # ITSA points economy, tiers, and leaderboard
│   ├── ADMIN_GUIDE.md           # Operational guide for the Admin Control Center
│   ├── COORDINATOR_GUIDE.md     # Operational guide for Event Coordinators
│   ├── STUDENT_GUIDE.md         # User guide for Students
│   ├── INSTALLATION.md          # Step-by-step installation instructions
│   ├── LOCAL_SETUP.md           # Local run commands, accounts, and testing
│   ├── DEPLOYMENT.md            # Render cloud production deployment guide
│   ├── TESTING.md               # Test suite structure and verification commands
│   ├── SECURITY.md              # Security hardening, RBAC, and input sanitization
│   ├── PROJECT_STRUCTURE.md     # Repository directory tree and file annotations
│   ├── CHANGELOG.md             # Release history and development milestones
│   └── BUG_FIX_REPORT.md        # Comprehensive report of bug resolutions and fixes
│
├── scripts/                     # Management & Automation Scripts
│   ├── audit_db.py              # Quick script inspecting registered database tables
│   ├── e2e_audit.py             # End-to-end integration test of platform endpoints
│   ├── init_prod_admin.py       # Render pre-deploy database init & admin synchronization
│   ├── migrate_sqlite_to_postgres.py # Data migration utility for PostgreSQL
│   ├── seed_db.py               # Complete demo database populator
│   └── seed_demo_data.py        # Seeds 5 coordinators and 5 college events
│
└── tests/                       # Automated Test Suite (36 Tests, 100% Passing)
    ├── conftest.py              # Pytest application fixture and test database setup
    ├── test_admin_panel.py      # Admin control center route tests
    ├── test_ai.py               # Gemini AI and recommendation service tests
    ├── test_attendance.py       # Attendance scanning and validation tests
    ├── test_auth.py             # Registration, login, logout, and session tests
    ├── test_events.py           # Event creation and filtering tests
    ├── test_features.py         # Feedback, certificates, and gamification tests
    ├── test_issue_fixes.py      # Regression tests for cookie deletion and demo seeds
    ├── test_security_and_edge_cases.py # RBAC, rate limiting, and input validation
    └── test_social.py           # Posts, reactions, and comment tests
```