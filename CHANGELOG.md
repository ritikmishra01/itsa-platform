# Changelog

All notable changes and architectural updates to the **ITSA AI-Powered Event Management & Student Engagement Platform** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-25

### Added
- **Core Architecture & Framework**:
  - Flask Application Factory pattern with blueprinted modular routing.
  - Multi-tier environment configurations (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`).
  - SQLite default development storage with zero-config MySQL (PyMySQL) production fallback.
  - Security middleware: HTTP security headers, CORS origin management, and Flask-Limiter rate control.
  - Context processor for dynamic unread notification badge counters.

- **Database Layer (30 Models)**:
  - `User`, `StudentProfile`, `CoordinatorProfile`.
  - `Event`, `EventCategory`, `Venue`, `EventCoordinator`, `EventVolunteer`, `EventGallery`.
  - `EventRegistration`, `EventTicket` (UUID generation with embedded QR codes).
  - `Attendance` (6-step coordinator validation with duplicate attendance prevention).
  - `Certificate` (ReportLab landscape A4 PDF compilation with public validation QR).
  - `Feedback` (Event ratings, category scores, and suggestions).
  - `Post`, `PostMedia`, `PostReaction`, `Comment`, `CommentReply`, `PostShare`, `SavedPost`, `Hashtag`, `PostHashtag`, `Mention`.
  - `Notification`, `ItsaPoints` (transaction ledger + student total balance).
  - `Report` (community moderation queue), `AiRecommendation`, `AiAnalysis`, `AuditLog`.

- **Role-Based Access Control (RBAC)**:
  - Exact 3-tier hierarchy: `STUDENT`, `COORDINATOR`, `ADMIN`.
  - Server-side access decorators: `@student_required`, `@coordinator_required`, `@admin_required`, `@roles_required`.
  - Verification ensuring students cannot access coordinator scanning gates or admin functions.

- **QR Attendance & Scanner UI**:
  - Browser-based QR scanning via `html5-qrcode` JavaScript library.
  - Fallback manual ticket code entry.
  - 6-step server-side scan validation pipeline with real-time UI check-in feedback.
  - Automated point allocation (+10 pts) and instantaneous Certificate generation upon verified scan.

- **Social Feed & Community**:
  - Text and media posting with regex parsing for hashtags (`#tag`) and user mentions (`@name`).
  - 5-type reaction system (`LIKE`, `LOVE`, `CELEBRATE`, `INSIGHTFUL`, `SUPPORT`).
  - Threaded comment replies and post saving/sharing.
  - Community moderation reporting queue.

- **Gamification & Leaderboard**:
  - Transactional point logs with anti-duplication constraints.
  - Dynamic student leaderboard filterable by Department and Year of Study.

- **AI & Machine Learning Layer**:
  - Google Gemini 2.0 / 2.5 Flash assistant chatbot with session-aware college context.
  - Event description, announcement, and social caption auto-generators.
  - Gemini-powered feedback sentiment analysis and content moderation advisory.
  - Scikit-learn Content-Based Recommendation Engine using TF-IDF & Cosine Similarity.
  - Transparent formula-based student engagement scoring (0–100%).
  - Registration turnout regression predictor.

- **Frontend & Templates**:
  - Responsive Bootstrap 5 interface for Public, Student, Coordinator, and Admin portals.
  - Interactive Chart.js analytics graphs for categories, attendance by department, and participation by year.

- **Testing Suite**:
  - 17 unit, integration, and security test suites executed via pytest with 100% pass rate.
  - Complete 23-step End-to-End production audit script (`scripts/e2e_audit.py`).
