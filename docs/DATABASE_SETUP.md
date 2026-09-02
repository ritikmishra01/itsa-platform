# ITSA Platform: Database Architecture & Setup Guide

## 1. Overview
The **ITSA Platform** uses **SQLAlchemy ORM** to achieve complete environment portability between **SQLite** (for fast zero-config local development) and **PostgreSQL** (for secure, high-concurrency cloud production on Render).

---

## 2. Environment Database Configurations

### 2.1 Local Development (SQLite)
In your local `.env`:
```env
DATABASE_URL=sqlite:///itsa_platform.db
```
SQLAlchemy automatically connects to the local SQLite database. SQLite requires no background database server process and supports full ACID transactions.

### 2.2 Cloud Production (PostgreSQL on Render)
In your Render Environment settings:
```env
DATABASE_URL=postgresql+psycopg2://user:password@dpg-xxxx-a.singapore-postgres.render.com/itsa_platform
```
The application dynamically normalizes URLs via `normalize_database_url()` in `app/config.py`:
- Strips outer quotation marks or accidental prefixes.
- Converts legacy `postgres://` or standard `postgresql://` to `postgresql+psycopg2://`.
- Configures connection pooling: `pool_pre_ping=True`, `pool_recycle=300`.

---

## 3. Database Initialization Pipeline

### 3.1 Automated Pre-Deploy Hook (`render.yaml`)
Render automatically executes the database initialization script prior to starting the web service:
```yaml
preDeployCommand: "python scripts/init_prod_admin.py"
```
The script performs the following idempotent operations:
1. Calls `db.create_all()` to generate any missing database tables in dependency order.
2. Seeds core event categories (Technical, Workshop, Seminar, Cultural, Sports, Competition, Community Service, Other).
3. Ensures the default campus venue exists (`Main University Auditorium`).
4. Creates or synchronizes the administrator account (`admin@itsa.edu`) with the secret `ADMIN_PASSWORD` environment variable.
5. Invokes `scripts/seed_demo_data.py` to ensure the 5 demo coordinators and 5 college events exist.

### 3.2 Manual Seeding Commands

To seed demo coordinators and events locally or on a new database:
```bash
python scripts/seed_demo_data.py
```

To migrate an existing local SQLite database to Render PostgreSQL:
```bash
python scripts/migrate_sqlite_to_postgres.py
```

---

## 4. Key Models & Relationships Table

| Model / Table | Primary Key | Key Foreign Keys | Key Relationships |
| :--- | :--- | :--- | :--- |
| `User` (`users`) | `id` | None | `student_profile` (1:1), `coordinator_profile` (1:1), `registrations` (1:M), `attendances` (1:M), `certificates` (1:M), `posts` (1:M), `notifications` (1:M) |
| `StudentProfile` (`student_profiles`) | `id` | `user_id` &rarr; `users.id` | Backref to `User` |
| `CoordinatorProfile` (`coordinator_profiles`) | `id` | `user_id` &rarr; `users.id` | Backref to `User` |
| `EventCategory` (`event_categories`) | `id` | None | `events` (1:M) |
| `Venue` (`venues`) | `id` | None | `events` (1:M) |
| `Event` (`events`) | `id` | `category_id`, `venue_id`, `created_by` | `coordinators` (1:M), `registrations` (1:M), `attendances` (1:M), `certificates` (1:M), `feedbacks` (1:M), `gallery_items` (1:M) |
| `EventCoordinator` (`event_coordinators`) | `id` | `event_id`, `coordinator_id`, `assigned_by` | Unique constraint `(event_id, coordinator_id)` |
| `EventRegistration` (`event_registrations`) | `id` | `event_id`, `user_id` | Unique constraint `(event_id, user_id)`, `ticket` (1:1) |
| `EventTicket` (`event_tickets`) | `id` | `registration_id` | Unique code `ticket_code` |
| `Attendance` (`attendance`) | `id` | `event_id`, `user_id`, `scanned_by` | Unique constraint `(event_id, user_id)` preventing duplicate scans |
| `Certificate` (`certificates`) | `id` | `user_id`, `event_id`, `attendance_id` | Unique `certificate_code`, linked to PDF path |
| `Feedback` (`feedback`) | `id` | `event_id`, `user_id` | Unique constraint `(event_id, user_id)` |
| `Post` (`posts`) | `id` | `user_id`, `event_id` | `media` (1:M), `reactions` (1:M), `comments` (1:M) |
| `Notification` (`notifications`) | `id` | `user_id` | Recipient user link |
| `ItsaPoints` (`itsa_points`) | `id` | `user_id`, `related_event_id` | Transaction ledger entry |