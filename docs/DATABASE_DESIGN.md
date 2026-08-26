# Database Design — ITSA Platform

> All 30 tables documented with columns, types, constraints, indexes, and relationships.

---

## Table: users

**Purpose**: Central authentication table for all user accounts (Student, Coordinator, Admin).

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| id | INT UNSIGNED | NO | AUTO_INCREMENT | Primary key |
| email | VARCHAR(255) | NO | — | Unique login email |
| password_hash | VARCHAR(255) | NO | — | PBKDF2-SHA256 hash |
| full_name | VARCHAR(100) | NO | — | Display name |
| role | ENUM | NO | STUDENT | STUDENT, COORDINATOR, ADMIN |
| is_active | BOOLEAN | NO | TRUE | Account active flag |
| is_suspended | BOOLEAN | NO | FALSE | Suspended by admin flag |
| profile_image | VARCHAR(255) | YES | NULL | Relative file path |
| created_at | DATETIME | NO | NOW() | Registration timestamp |
| updated_at | DATETIME | NO | NOW() | Last modification |

- **Primary Key**: id
- **Unique**: email
- **Indexes**: email, role, is_active
- **Relationships**: One-to-one with student_profiles, coordinator_profiles. One-to-many with events, posts, comments, etc.

---

## Table: student_profiles

**Purpose**: Extended profile data for students. One-to-one with users.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| id | INT UNSIGNED | NO | AUTO_INCREMENT | Primary key |
| user_id | INT UNSIGNED | NO | — | FK → users.id |
| student_id | VARCHAR(50) | NO | — | College roll number |
| department | VARCHAR(100) | NO | — | e.g. Computer Science |
| year_of_study | TINYINT | NO | — | 1, 2, 3, or 4 |
| bio | TEXT | YES | NULL | Short bio |
| interests | TEXT | YES | NULL | Comma-separated tags |
| phone | VARCHAR(20) | YES | NULL | Contact number |
| github_url | VARCHAR(255) | YES | NULL | GitHub profile URL |
| linkedin_url | VARCHAR(255) | YES | NULL | LinkedIn profile URL |
| total_points | INT UNSIGNED | NO | 0 | Denormalized ITSA points total |

- **Primary Key**: id
- **Unique**: user_id, student_id
- **Foreign Key**: user_id → users.id (CASCADE DELETE)
- **Indexes**: department, year_of_study, total_points

---

## Table: coordinator_profiles

**Purpose**: Extended profile for coordinator accounts.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| id | INT UNSIGNED | NO | AUTO_INCREMENT | Primary key |
| user_id | INT UNSIGNED | NO | — | FK → users.id |
| employee_id | VARCHAR(50) | YES | NULL | Internal employee ID |
| designation | VARCHAR(100) | YES | NULL | Role title |
| department | VARCHAR(100) | YES | NULL | Department |
| phone | VARCHAR(20) | YES | NULL | Contact |

- **Primary Key**: id
- **Unique**: user_id
- **Foreign Key**: user_id → users.id (CASCADE DELETE)

---

## Table: event_categories

**Purpose**: Categorizes events by type.

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | INT UNSIGNED | NO | AUTO_INCREMENT |
| name | VARCHAR(100) | NO | — |
| description | TEXT | YES | NULL |
| icon | VARCHAR(50) | YES | NULL |
| created_at | DATETIME | NO | NOW() |

- **Unique**: name
- **Default categories**: Technical, Workshop, Seminar, Cultural, Sports, Competition, Community Service, Other

---

## Table: venues

**Purpose**: Physical locations for events.

| Column | Type | Nullable |
|---|---|---|
| id | INT UNSIGNED | NO |
| name | VARCHAR(200) | NO |
| address | TEXT | YES |
| capacity | INT UNSIGNED | YES |
| room_number | VARCHAR(50) | YES |
| building | VARCHAR(100) | YES |

---

## Table: events

**Purpose**: Core event records.

| Column | Type | Nullable | Description |
|---|---|---|---|
| id | INT UNSIGNED | NO | Primary key |
| title | VARCHAR(200) | NO | Event name |
| description | TEXT | NO | Full description |
| category_id | INT UNSIGNED | YES | FK → event_categories.id |
| venue_id | INT UNSIGNED | YES | FK → venues.id |
| poster_image | VARCHAR(255) | YES | File path |
| start_datetime | DATETIME | NO | Event start |
| end_datetime | DATETIME | NO | Event end |
| registration_deadline | DATETIME | NO | Last registration time |
| max_participants | INT UNSIGNED | YES | NULL = unlimited |
| current_registrations | INT UNSIGNED | NO | 0 — denormalized count |
| status | ENUM | NO | DRAFT | Full lifecycle status |
| is_free | BOOLEAN | NO | TRUE | |
| registration_fee | DECIMAL(10,2) | NO | 0.00 | |
| tags | VARCHAR(500) | YES | NULL | Comma-separated tags |
| created_by | INT UNSIGNED | NO | — | FK → users.id |

- **Status ENUM**: DRAFT, PUBLISHED, REGISTRATION_OPEN, REGISTRATION_CLOSED, ONGOING, COMPLETED, CANCELLED
- **Indexes**: status, start_datetime, category_id, created_by
- **Foreign Keys**: category_id (SET NULL), venue_id (SET NULL), created_by (RESTRICT)

---

## Table: event_coordinators

**Purpose**: Many-to-many junction — coordinators assigned to events.

| Column | Type | Description |
|---|---|---|
| id | INT UNSIGNED | Primary key |
| event_id | INT UNSIGNED | FK → events.id |
| coordinator_id | INT UNSIGNED | FK → users.id |
| role_in_event | VARCHAR(100) | Lead, Support, Registration, Volunteer |
| assigned_by | INT UNSIGNED | FK → users.id (admin) |
| assigned_at | DATETIME | |

- **Unique**: (event_id, coordinator_id)

---

## Table: event_registrations

**Purpose**: Student registrations for events.

| Column | Type | Description |
|---|---|---|
| id | INT UNSIGNED | Primary key |
| event_id | INT UNSIGNED | FK → events.id |
| user_id | INT UNSIGNED | FK → users.id |
| registration_number | VARCHAR(100) | ITSA-{EVENT}-{YEAR}-{SEQ} |
| status | ENUM | CONFIRMED, CANCELLED, WAITLISTED |
| registered_at | DATETIME | |
| cancelled_at | DATETIME | Nullable |
| cancellation_reason | TEXT | Nullable |

- **Unique**: (event_id, user_id) — prevents duplicate registrations
- **Unique**: registration_number

---

## Table: event_tickets

**Purpose**: QR ticket generated per confirmed registration.

| Column | Type | Description |
|---|---|---|
| id | INT UNSIGNED | Primary key |
| registration_id | INT UNSIGNED | FK → event_registrations.id (UNIQUE) |
| ticket_code | VARCHAR(100) | UUID-based code in QR |
| qr_image_path | VARCHAR(255) | Path to PNG file |
| issued_at | DATETIME | |
| is_valid | BOOLEAN | FALSE when cancelled |

- **Unique**: registration_id (one ticket per registration), ticket_code
- **Indexes**: ticket_code (for fast QR scan lookups), is_valid

---

## Table: attendance

**Purpose**: Records coordinator-scanned attendance per student per event.

| Column | Type | Description |
|---|---|---|
| id | INT UNSIGNED | Primary key |
| event_id | INT UNSIGNED | FK → events.id |
| user_id | INT UNSIGNED | FK → users.id (student) |
| registration_id | INT UNSIGNED | FK → event_registrations.id |
| ticket_id | INT UNSIGNED | FK → event_tickets.id |
| scanned_by | INT UNSIGNED | FK → users.id (coordinator) |
| scanned_at | DATETIME | Exact timestamp of scan |
| status | ENUM | PRESENT, ABSENT, LATE |
| notes | TEXT | Admin notes |

- **Unique**: (event_id, user_id) — CRITICAL: prevents duplicate attendance
- This unique constraint is the database-level guard against duplicate scans

---

## Table: certificates

**Purpose**: PDF attendance certificates.

| Column | Type | Description |
|---|---|---|
| id | INT UNSIGNED | Primary key |
| user_id | INT UNSIGNED | FK → users.id |
| event_id | INT UNSIGNED | FK → events.id |
| attendance_id | INT UNSIGNED | FK → attendance.id |
| certificate_code | VARCHAR(100) | ITSA-CERT-{uuid4} |
| pdf_path | VARCHAR(255) | File path |
| issued_at | DATETIME | |
| is_valid | BOOLEAN | Admin can revoke |

- **Unique**: (user_id, event_id), certificate_code

---

## Table: feedback

**Purpose**: Student feedback for attended events.

| Column | Type | Description |
|---|---|---|
| id | INT UNSIGNED | Primary key |
| event_id | INT UNSIGNED | FK → events.id |
| user_id | INT UNSIGNED | FK → users.id |
| rating | TINYINT | 1-5 stars |
| content | TEXT | Optional text |
| ai_sentiment | VARCHAR(50) | AI result: POSITIVE/NEGATIVE/NEUTRAL |
| ai_keywords | TEXT | JSON array from AI |
| submitted_at | DATETIME | |

- **Unique**: (event_id, user_id) — one feedback per attendance

---

## Table: posts

**Purpose**: Social community feed posts.

| Column | Type | Description |
|---|---|---|
| id | INT UNSIGNED | Primary key |
| user_id | INT UNSIGNED | FK → users.id (author) |
| content | TEXT | Post text |
| post_type | ENUM | TEXT, IMAGE, VIDEO, MIXED |
| event_id | INT UNSIGNED | Optional linked event |
| is_active | BOOLEAN | Soft delete flag |
| is_reported | BOOLEAN | Has pending report |
| ai_moderated | BOOLEAN | AI reviewed flag |
| ai_moderation_result | VARCHAR(50) | AI recommendation |
| views_count | INT UNSIGNED | View counter |
| created_at, updated_at | DATETIME | |

---

## Table: post_media

**Purpose**: Media files (images/videos) attached to posts.

| Column | Type | Description |
|---|---|---|
| post_id | INT UNSIGNED | FK → posts.id |
| media_type | ENUM | IMAGE, VIDEO |
| file_path | VARCHAR(255) | Stored file path |
| file_size | INT UNSIGNED | Bytes |
| media_order | TINYINT | Display order |

---

## Table: post_reactions

**Purpose**: User reactions on posts.

| Column | Type | Description |
|---|---|---|
| post_id | INT UNSIGNED | FK → posts.id |
| user_id | INT UNSIGNED | FK → users.id |
| reaction_type | ENUM | LIKE, LOVE, CELEBRATE, INSIGHTFUL, SUPPORT |

- **Unique**: (post_id, user_id) — one reaction per user per post

---

## Table: comments & comment_replies

**Purpose**: Nested comment system (2 levels: comment → reply).

| Table | Key Columns |
|---|---|
| comments | id, post_id, user_id, content, is_active, is_reported |
| comment_replies | id, comment_id, user_id, content, mentioned_user_id |

---

## Table: post_shares, saved_posts

| Table | Key Columns |
|---|---|
| post_shares | id, post_id, user_id, platform (FEED/EXTERNAL) |
| saved_posts | id, post_id, user_id — UNIQUE (post_id, user_id) |

---

## Table: hashtags & post_hashtags

| Table | Key Columns |
|---|---|
| hashtags | id, name (UNIQUE), post_count |
| post_hashtags | post_id + hashtag_id (composite PK) |

---

## Table: mentions

**Purpose**: Track @mentions in posts, comments, and replies.

- Links: mentioning_user_id, mentioned_user_id
- Context: post_id OR comment_id OR reply_id (one will be set)

---

## Table: notifications

| Column | Description |
|---|---|
| user_id | Recipient |
| type | ENUM of notification types |
| title, message | Content |
| is_read | Read flag |
| related_* | Optional linked entities |

---

## Table: event_gallery, event_volunteers

| Table | Purpose |
|---|---|
| event_gallery | Event photos/videos uploaded by coordinators |
| event_volunteers | Student volunteers assigned to events |

---

## Table: itsa_points

**Purpose**: Transaction log for all ITSA point changes.

- Positive values = award, Negative = deduction
- reason ENUM documents the cause
- total_points on student_profiles is updated after each transaction

---

## Table: reports

**Purpose**: Content moderation reports from users.

- status: PENDING → REVIEWED → RESOLVED/DISMISSED
- Admin reviews and takes action

---

## Table: ai_recommendations, ai_analysis

| Table | Purpose |
|---|---|
| ai_recommendations | ML event recommendations per user |
| ai_analysis | General AI analysis results storage |

---

## Table: audit_logs

**Purpose**: Immutable log of all admin actions for accountability.

- Stores: user_id, action, entity_type, entity_id, details (JSON), IP, timestamp
- Never deleted (append-only)

---

## Entity Relationship Summary

```
users ─────────────────────────────────────────────────
  ├─ student_profiles (1:1)
  ├─ coordinator_profiles (1:1)
  ├─ events (created_by → 1:many)
  ├─ event_coordinators (many:many via events)
  ├─ event_registrations (1:many)
  │     └─ event_tickets (1:1)
  │           └─ attendance (1:1 per event)
  │                 └─ certificates (1:1 per event)
  ├─ feedback (1:many)
  ├─ posts (1:many)
  │     ├─ post_media (1:many)
  │     ├─ post_reactions (many:many)
  │     ├─ comments (1:many)
  │     │     └─ comment_replies (1:many)
  │     ├─ post_shares (1:many)
  │     ├─ saved_posts (many:many)
  │     └─ post_hashtags (many:many via hashtags)
  ├─ notifications (1:many)
  ├─ itsa_points (1:many)
  └─ reports (1:many)
```
