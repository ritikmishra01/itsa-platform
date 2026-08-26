# Backend Structure -- ITSA Platform

## Flask Application Factory

The app uses the factory pattern. create_app() in app/__init__.py initializes all extensions and registers all blueprints.

## Directory Structure

app/
  __init__.py            -- App factory (create_app function)
  config.py              -- DevelopmentConfig, ProductionConfig, TestingConfig
  extensions.py          -- db, login_manager, migrate, limiter (initialized here)

  models/
    __init__.py          -- Imports all models for Alembic discovery
    user.py              -- User, StudentProfile, CoordinatorProfile
    event.py             -- Event, EventCategory, Venue, EventCoordinator
    registration.py      -- EventRegistration
    ticket.py            -- EventTicket
    attendance.py        -- Attendance
    certificate.py       -- Certificate
    feedback.py          -- Feedback
    post.py              -- Post, PostMedia, PostReaction
    comment.py           -- Comment, CommentReply
    social.py            -- PostShare, SavedPost, Hashtag, PostHashtag, Mention
    notification.py      -- Notification
    gamification.py      -- ItsaPoints
    report.py            -- Report
    gallery.py           -- EventGallery, EventVolunteer
    ai_models.py         -- AiRecommendation, AiAnalysis
    audit.py             -- AuditLog

  routes/
    __init__.py
    auth.py              -- Blueprint: api_v1_auth, prefix /api/v1/auth
    events.py            -- Blueprint: api_v1_events, prefix /api/v1/events
    tickets.py           -- Blueprint: api_v1_tickets, prefix /api/v1/tickets
    attendance.py        -- Blueprint: api_v1_attendance, prefix /api/v1/attendance
    posts.py             -- Blueprint: api_v1_posts, prefix /api/v1/posts
    comments.py          -- Blueprint: api_v1_comments, prefix /api/v1/comments
    certificates.py      -- Blueprint: api_v1_certs, prefix /api/v1/certificates
    feedback.py          -- Blueprint: api_v1_feedback, prefix /api/v1/feedback
    notifications.py     -- Blueprint: api_v1_notif, prefix /api/v1/notifications
    gamification.py      -- Blueprint: api_v1_game, prefix /api/v1
    hashtags.py          -- Blueprint: api_v1_hashtags, prefix /api/v1/hashtags
    admin.py             -- Blueprint: api_v1_admin, prefix /api/v1/admin
    ai.py                -- Blueprint: api_v1_ai, prefix /api/v1/ai
    pages.py             -- Blueprint: pages, prefix / (HTML page routes)

  services/
    auth_service.py      -- register_user, login_user, update_profile, etc.
    event_service.py     -- create_event, update_event, publish_event, etc.
    registration_service.py  -- register_for_event, cancel_registration, etc.
    ticket_service.py    -- generate_ticket, generate_ticket_qr, etc.
    attendance_service.py    -- scan_attendance, validate_ticket, etc.
    social_service.py    -- create_post, add_reaction, create_comment, etc.
    certificate_service.py   -- generate_certificate, verify_certificate, etc.
    feedback_service.py  -- submit_feedback, get_event_feedback, etc.
    notification_service.py  -- send_notification, send_email_notification, etc.
    gamification_service.py  -- award_points, get_leaderboard, etc.
    analytics_service.py -- get_admin_overview, get_event_analytics, etc.
    admin_service.py     -- suspend_user, manage_reports, etc.
    ai_service.py        -- chat_with_ai, recommend_events, moderate_content, etc.

  repositories/
    user_repo.py         -- get_user_by_id, get_user_by_email, etc.
    event_repo.py        -- get_event, list_events, etc.
    registration_repo.py -- get_registration, count_registrations, etc.
    attendance_repo.py   -- get_attendance, check_duplicate, etc.
    post_repo.py         -- get_feed, get_post, get_trending_hashtags, etc.
    certificate_repo.py  -- get_certificate_by_code, etc.
    analytics_repo.py    -- get_monthly_stats, get_department_stats, etc.

  schemas/
    auth_schemas.py      -- RegistrationSchema, LoginSchema
    event_schemas.py     -- EventCreateSchema, EventUpdateSchema
    post_schemas.py      -- PostCreateSchema
    feedback_schemas.py  -- FeedbackCreateSchema

  utils/
    decorators.py        -- admin_required, coordinator_required, roles_required
    validators.py        -- validate_email, validate_password, validate_file, etc.
    responses.py         -- success_response, error_response helpers
    file_utils.py        -- save_upload, generate_uuid_filename, etc.
    email_utils.py       -- send_email, send_registration_email, etc.
    pagination.py        -- paginate_query helper

  ai/
    gemini_client.py     -- Gemini API wrapper class
    prompts.py           -- All prompt constants (PROMPT_CHATBOT_SYSTEM_V1 etc.)
    chatbot.py           -- chat_with_ai(user_id, message, history) function
    content_gen.py       -- generate_description, generate_announcement, etc.
    moderation.py        -- moderate_content(text) function
    feedback_ai.py       -- analyze_feedback_sentiment(event_id) function
    recommendation.py    -- recommend_events(user_id) using Scikit-learn
    prediction.py        -- predict_registrations(event_id) using Scikit-learn
    engagement.py        -- calculate_engagement_score(user_id) formula-based
    ml_models/           -- Stored .joblib model files (gitignored)

  templates/
    base.html            -- Base template with nav, scripts, toast container
    auth/                -- login.html, register.html
    public/              -- home.html, events.html, event_detail.html, verify_cert.html
    student/             -- dashboard.html, feed.html, profile.html, tickets.html, etc.
    coordinator/         -- dashboard.html, scanner.html, attendance.html, etc.
    admin/               -- dashboard.html, users.html, events.html, analytics.html, etc.
    emails/              -- registration.html, reminder.html, certificate.html
    errors/              -- 404.html, 500.html

  static/
    css/main.css         -- Custom CSS overrides
    js/main.js           -- Global JS utilities (toast, API helpers)
    js/feed.js           -- Social feed interactions
    js/scanner.js        -- QR scanner (html5-qrcode wrapper)
    js/charts.js         -- Chart.js initialization helpers
    img/                 -- Logo, illustrations, icons
