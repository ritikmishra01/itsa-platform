-- ============================================================
-- ITSA AI-Powered Event Management & Student Engagement Platform
-- Complete MySQL Database Schema
-- Version: 1.0.0
-- Engine: InnoDB | Charset: utf8mb4
-- ============================================================

CREATE DATABASE IF NOT EXISTS itsa_platform
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE itsa_platform;

-- ============================================================
-- TABLE: users
-- Central user accounts for all roles
-- ============================================================
CREATE TABLE users (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    role          ENUM('STUDENT','COORDINATOR','ADMIN') NOT NULL DEFAULT 'STUDENT',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    is_suspended  BOOLEAN NOT NULL DEFAULT FALSE,
    profile_image VARCHAR(255),
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Central authentication table for all user roles';

-- ============================================================
-- TABLE: student_profiles
-- Extended profile data for students
-- ============================================================
CREATE TABLE student_profiles (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id       INT UNSIGNED NOT NULL UNIQUE,
    student_id    VARCHAR(50) NOT NULL UNIQUE COMMENT 'College roll number',
    department    VARCHAR(100) NOT NULL,
    year_of_study TINYINT UNSIGNED NOT NULL COMMENT '1 to 4',
    bio           TEXT,
    interests     TEXT COMMENT 'Comma-separated interest tags',
    phone         VARCHAR(20),
    github_url    VARCHAR(255),
    linkedin_url  VARCHAR(255),
    total_points  INT UNSIGNED NOT NULL DEFAULT 0,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_sp_department (department),
    INDEX idx_sp_year (year_of_study),
    INDEX idx_sp_points (total_points)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: coordinator_profiles
-- Extended profile data for coordinators
-- ============================================================
CREATE TABLE coordinator_profiles (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     INT UNSIGNED NOT NULL UNIQUE,
    employee_id VARCHAR(50),
    designation VARCHAR(100),
    department  VARCHAR(100),
    phone       VARCHAR(20),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: event_categories
-- ============================================================
CREATE TABLE event_categories (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon        VARCHAR(50) COMMENT 'Bootstrap icon class name',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: venues
-- ============================================================
CREATE TABLE venues (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    address     TEXT,
    capacity    INT UNSIGNED,
    room_number VARCHAR(50),
    building    VARCHAR(100),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: events
-- ============================================================
CREATE TABLE events (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title                 VARCHAR(200) NOT NULL,
    description           TEXT NOT NULL,
    category_id           INT UNSIGNED,
    venue_id              INT UNSIGNED,
    poster_image          VARCHAR(255),
    start_datetime        DATETIME NOT NULL,
    end_datetime          DATETIME NOT NULL,
    registration_deadline DATETIME NOT NULL,
    max_participants      INT UNSIGNED COMMENT 'NULL means unlimited',
    current_registrations INT UNSIGNED NOT NULL DEFAULT 0,
    status                ENUM('DRAFT','PUBLISHED','REGISTRATION_OPEN','REGISTRATION_CLOSED','ONGOING','COMPLETED','CANCELLED') NOT NULL DEFAULT 'DRAFT',
    is_free               BOOLEAN NOT NULL DEFAULT TRUE,
    registration_fee      DECIMAL(10,2) DEFAULT 0.00,
    tags                  VARCHAR(500),
    created_by            INT UNSIGNED NOT NULL,
    created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_events_status (status),
    INDEX idx_events_start (start_datetime),
    INDEX idx_events_category (category_id),
    INDEX idx_events_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: event_coordinators (junction)
-- ============================================================
CREATE TABLE event_coordinators (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_id        INT UNSIGNED NOT NULL,
    coordinator_id  INT UNSIGNED NOT NULL,
    role_in_event   VARCHAR(100) DEFAULT 'Support' COMMENT 'Lead, Support, Registration, Volunteer',
    assigned_by     INT UNSIGNED NOT NULL,
    assigned_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_event_coordinator (event_id, coordinator_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (coordinator_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_ec_coordinator (coordinator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: event_registrations
-- ============================================================
CREATE TABLE event_registrations (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_id            INT UNSIGNED NOT NULL,
    user_id             INT UNSIGNED NOT NULL,
    registration_number VARCHAR(100) NOT NULL UNIQUE,
    status              ENUM('CONFIRMED','CANCELLED','WAITLISTED') NOT NULL DEFAULT 'CONFIRMED',
    registered_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at        DATETIME,
    cancellation_reason TEXT,
    UNIQUE KEY uq_event_user (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_er_user (user_id),
    INDEX idx_er_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: event_tickets
-- ============================================================
CREATE TABLE event_tickets (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    registration_id INT UNSIGNED NOT NULL UNIQUE,
    ticket_code     VARCHAR(100) NOT NULL UNIQUE COMMENT 'UUID used in QR',
    qr_image_path   VARCHAR(255),
    issued_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_valid        BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (registration_id) REFERENCES event_registrations(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_tickets_code (ticket_code),
    INDEX idx_tickets_valid (is_valid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: attendance
-- ============================================================
CREATE TABLE attendance (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_id        INT UNSIGNED NOT NULL,
    user_id         INT UNSIGNED NOT NULL,
    registration_id INT UNSIGNED NOT NULL,
    ticket_id       INT UNSIGNED NOT NULL,
    scanned_by      INT UNSIGNED NOT NULL COMMENT 'Coordinator user ID',
    scanned_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('PRESENT','ABSENT','LATE') NOT NULL DEFAULT 'PRESENT',
    notes           TEXT,
    UNIQUE KEY uq_attendance_event_user (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (registration_id) REFERENCES event_registrations(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ticket_id) REFERENCES event_tickets(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (scanned_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_att_event (event_id),
    INDEX idx_att_user (user_id),
    INDEX idx_att_scanned_by (scanned_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: certificates
-- ============================================================
CREATE TABLE certificates (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id          INT UNSIGNED NOT NULL,
    event_id         INT UNSIGNED NOT NULL,
    attendance_id    INT UNSIGNED NOT NULL,
    certificate_code VARCHAR(100) NOT NULL UNIQUE,
    pdf_path         VARCHAR(255),
    issued_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_valid         BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE KEY uq_cert_user_event (user_id, event_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (attendance_id) REFERENCES attendance(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_cert_code (certificate_code),
    INDEX idx_cert_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: feedback
-- ============================================================
CREATE TABLE feedback (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_id       INT UNSIGNED NOT NULL,
    user_id        INT UNSIGNED NOT NULL,
    rating         TINYINT UNSIGNED NOT NULL COMMENT '1 to 5',
    content        TEXT,
    ai_sentiment   VARCHAR(50) COMMENT 'POSITIVE, NEGATIVE, NEUTRAL',
    ai_keywords    TEXT COMMENT 'JSON array of keywords',
    submitted_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_feedback_event_user (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_fb_event (event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: posts
-- ============================================================
CREATE TABLE posts (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL,
    content               TEXT,
    post_type             ENUM('TEXT','IMAGE','VIDEO','MIXED') NOT NULL DEFAULT 'TEXT',
    event_id              INT UNSIGNED COMMENT 'Linked event (optional)',
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    is_reported           BOOLEAN NOT NULL DEFAULT FALSE,
    ai_moderated          BOOLEAN NOT NULL DEFAULT FALSE,
    ai_moderation_result  VARCHAR(50),
    views_count           INT UNSIGNED NOT NULL DEFAULT 0,
    created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_posts_user (user_id),
    INDEX idx_posts_active (is_active),
    INDEX idx_posts_created (created_at),
    INDEX idx_posts_reported (is_reported)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: post_media
-- ============================================================
CREATE TABLE post_media (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id     INT UNSIGNED NOT NULL,
    media_type  ENUM('IMAGE','VIDEO') NOT NULL,
    file_path   VARCHAR(255) NOT NULL,
    file_size   INT UNSIGNED COMMENT 'Size in bytes',
    media_order TINYINT UNSIGNED NOT NULL DEFAULT 0,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_pm_post (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: post_reactions
-- ============================================================
CREATE TABLE post_reactions (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id       INT UNSIGNED NOT NULL,
    user_id       INT UNSIGNED NOT NULL,
    reaction_type ENUM('LIKE','LOVE','CELEBRATE','INSIGHTFUL','SUPPORT') NOT NULL DEFAULT 'LIKE',
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_reaction_post_user (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_pr_post (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: comments
-- ============================================================
CREATE TABLE comments (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id     INT UNSIGNED NOT NULL,
    user_id     INT UNSIGNED NOT NULL,
    content     TEXT NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    is_reported BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_comments_post (post_id),
    INDEX idx_comments_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: comment_replies
-- ============================================================
CREATE TABLE comment_replies (
    id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    comment_id        INT UNSIGNED NOT NULL,
    user_id           INT UNSIGNED NOT NULL,
    content           TEXT NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    mentioned_user_id INT UNSIGNED COMMENT 'User mentioned in reply',
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (mentioned_user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_replies_comment (comment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: post_shares
-- ============================================================
CREATE TABLE post_shares (
    id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id   INT UNSIGNED NOT NULL,
    user_id   INT UNSIGNED NOT NULL,
    shared_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    platform  ENUM('FEED','EXTERNAL') NOT NULL DEFAULT 'FEED',
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_shares_post (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: saved_posts
-- ============================================================
CREATE TABLE saved_posts (
    id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id  INT UNSIGNED NOT NULL,
    user_id  INT UNSIGNED NOT NULL,
    saved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_saved_post_user (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_saved_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: hashtags
-- ============================================================
CREATE TABLE hashtags (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE COMMENT 'Without # symbol',
    post_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hashtags_count (post_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: post_hashtags (junction)
-- ============================================================
CREATE TABLE post_hashtags (
    post_id    INT UNSIGNED NOT NULL,
    hashtag_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (post_id, hashtag_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (hashtag_id) REFERENCES hashtags(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_ph_hashtag (hashtag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: mentions
-- ============================================================
CREATE TABLE mentions (
    id                 INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id            INT UNSIGNED COMMENT 'If mention is in a post',
    comment_id         INT UNSIGNED COMMENT 'If mention is in a comment',
    reply_id           INT UNSIGNED COMMENT 'If mention is in a reply',
    mentioned_user_id  INT UNSIGNED NOT NULL,
    mentioning_user_id INT UNSIGNED NOT NULL,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (reply_id) REFERENCES comment_replies(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (mentioned_user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (mentioning_user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_mentions_target (mentioned_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: notifications
-- ============================================================
CREATE TABLE notifications (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id          INT UNSIGNED NOT NULL,
    type             ENUM('EVENT_REGISTRATION','EVENT_REMINDER','EVENT_CHANGE','EVENT_CANCELLED','CERTIFICATE_READY','POST_REACTION','POST_COMMENT','MENTION','ANNOUNCEMENT','SYSTEM') NOT NULL,
    title            VARCHAR(200) NOT NULL,
    message          TEXT NOT NULL,
    is_read          BOOLEAN NOT NULL DEFAULT FALSE,
    related_event_id INT UNSIGNED,
    related_post_id  INT UNSIGNED,
    related_user_id  INT UNSIGNED,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (related_event_id) REFERENCES events(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (related_post_id) REFERENCES posts(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (related_user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_notif_user (user_id),
    INDEX idx_notif_read (is_read),
    INDEX idx_notif_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: event_gallery
-- ============================================================
CREATE TABLE event_gallery (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_id    INT UNSIGNED NOT NULL,
    uploaded_by INT UNSIGNED NOT NULL,
    file_path   VARCHAR(255) NOT NULL,
    media_type  ENUM('IMAGE','VIDEO') NOT NULL,
    caption     TEXT,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_gallery_event (event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: event_volunteers
-- ============================================================
CREATE TABLE event_volunteers (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_id    INT UNSIGNED NOT NULL,
    user_id     INT UNSIGNED NOT NULL,
    role        VARCHAR(100),
    assigned_by INT UNSIGNED NOT NULL,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_volunteer_event_user (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: itsa_points (transaction log)
-- ============================================================
CREATE TABLE itsa_points (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id          INT UNSIGNED NOT NULL,
    points           INT NOT NULL COMMENT 'Can be negative for deductions',
    reason           ENUM('ATTENDANCE','REGISTRATION','FEEDBACK','SOCIAL_POST','SOCIAL_REACTION','VOLUNTEERING','COMPETITION','ADMIN_ADJUSTMENT','CANCELLATION') NOT NULL,
    related_event_id INT UNSIGNED,
    related_post_id  INT UNSIGNED,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by       INT UNSIGNED COMMENT 'Admin ID if manual adjustment',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (related_event_id) REFERENCES events(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (related_post_id) REFERENCES posts(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_points_user (user_id),
    INDEX idx_points_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: reports (user-reported content)
-- ============================================================
CREATE TABLE reports (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reporter_id         INT UNSIGNED NOT NULL,
    reported_post_id    INT UNSIGNED,
    reported_comment_id INT UNSIGNED,
    reported_user_id    INT UNSIGNED,
    reason              ENUM('SPAM','INAPPROPRIATE','HARASSMENT','MISINFORMATION','OTHER') NOT NULL,
    description         TEXT,
    status              ENUM('PENDING','REVIEWED','RESOLVED','DISMISSED') NOT NULL DEFAULT 'PENDING',
    reviewed_by         INT UNSIGNED,
    reviewed_at         DATETIME,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (reported_post_id) REFERENCES posts(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (reported_comment_id) REFERENCES comments(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (reported_user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_reports_status (status),
    INDEX idx_reports_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: ai_recommendations
-- ============================================================
CREATE TABLE ai_recommendations (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id       INT UNSIGNED NOT NULL,
    event_id      INT UNSIGNED NOT NULL,
    score         FLOAT NOT NULL COMMENT 'Recommendation relevance score 0-1',
    reason        TEXT COMMENT 'AI-generated explanation',
    model_version VARCHAR(50) NOT NULL DEFAULT 'v1',
    generated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_rec_user (user_id),
    INDEX idx_rec_generated (generated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: ai_analysis
-- ============================================================
CREATE TABLE ai_analysis (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_type ENUM('FEEDBACK_SENTIMENT','ATTENDANCE_PREDICTION','ENGAGEMENT_SCORE','REGISTRATION_PREDICTION') NOT NULL,
    related_id    INT UNSIGNED NOT NULL COMMENT 'ID of related entity (event_id, user_id etc)',
    input_data    JSON,
    output_data   JSON,
    model_version VARCHAR(50) NOT NULL DEFAULT 'v1',
    analyzed_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_aa_type (analysis_type),
    INDEX idx_aa_related (related_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: audit_logs
-- ============================================================
CREATE TABLE audit_logs (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     INT UNSIGNED,
    action      VARCHAR(200) NOT NULL,
    entity_type VARCHAR(100),
    entity_id   INT UNSIGNED,
    details     JSON,
    ip_address  VARCHAR(45),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SEED: Default Event Categories
-- ============================================================
INSERT INTO event_categories (name, description, icon) VALUES
('Technical', 'Hackathons, coding contests, tech talks', 'bi-code-slash'),
('Workshop', 'Hands-on skill workshops', 'bi-tools'),
('Seminar', 'Lectures and knowledge sessions', 'bi-mic'),
('Cultural', 'Cultural programs and celebrations', 'bi-music-note'),
('Sports', 'Sports events and tournaments', 'bi-trophy'),
('Competition', 'Competitions and contests', 'bi-award'),
('Community Service', 'Social responsibility activities', 'bi-heart'),
('Other', 'Miscellaneous events', 'bi-three-dots');
