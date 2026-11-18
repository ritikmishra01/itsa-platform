# ITSA Platform — ML Turnout Predictor, Filter Engine & Instagram-Style Stories Report

**Project:** ITSA – AI-Powered Event Management & Student Engagement Platform  
**Directory:** `C:\Users\tiwar\Downloads\itsa-platform (2)\itsa-platform`  
**Date:** November 15, 2026  
**Status:** **100% COMPLETE & VERIFIED** (87 of 87 Tests Passing)  

---

## 1. Executive Summary

Three major enhancements and defect resolutions were completed:
1. **PART A – ML Predictor Fix:** Restored the machine learning turnout prediction pipeline using a trained `scikit-learn` `RandomForestRegressor` model, saved artifacts, robust feature preprocessing, and updated template handlers.
2. **PART B – Fix All Filter Buttons:** Added the missing `#filterModal` to `admin/events.html`, repaired query handling for department filtering in `admin_users`, added interactive filter toolbars to users, registrations, and attendance management pages, and created the `/community` route alias.
3. **PART C – Instagram-Style Stories in Community:** Implemented ephemeral 24-hour stories with media (photos/videos) and text support, horizontal story tray with animated gradient rings, auto-advancing fullscreen story viewer, idempotent view tracking, author-only viewer lists, and author/admin story deletion controls.

---

## 2. Root Cause Analysis & Implementations

### Part A: ML Turnout Predictor
* **Root Causes:**
  1. `app/ai/ml_models` was empty; no serialized machine learning model bundle existed.
  2. The frontend in `app/templates/admin/ai_center.html` expected `predicted_registrations` and a string array `factors_considered`, whereas `AIService` returned `predicted_count` and omitted `factors_considered`, causing a JavaScript `TypeError: Cannot read properties of undefined (reading 'join')`.
* **Implementation:**
  - Built `app/ai/turnout_predictor.py` implementing `EventTurnoutPredictor` singleton.
  - Engineered 8 core features: `category_encoded`, `day_of_week`, `hour_of_start`, `is_weekend`, `duration_hours`, `venue_capacity`, `historical_avg_category`, `days_until_event`.
  - Trained `RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)` and saved bundle to `app/ai/ml_models/event_turnout_model.joblib` ($R^2 = 0.9833, \text{MAE} = 3.56$).
  - Updated `app/services/ai_service.py` to route turnout queries to `EventTurnoutPredictor`.
  - Updated `app/templates/admin/ai_center.html` to render prediction numbers, confidence badges, and evaluated factor cards safely.

### Part B: Filter Functionality
* **Root Causes:**
  1. `app/templates/admin/events.html` had `<button data-bs-target="#filterModal">` but `#filterModal` was never defined in the template.
  2. `pages.py` extracted `department` query argument in `admin_users()`, but never added it to the SQLAlchemy query filter.
  3. Registrations, Attendance, and Users pages lacked responsive filter toolbars.
* **Implementation:**
  - Added `#filterModal` inside `{% block body_modals %}` in `admin/events.html` with Category, Status, and Search inputs.
  - Added active filter chips and a "No matching events found" empty state with a reset button.
  - Updated `app/routes/pages.py` to apply department filtering across `StudentProfile` and `CoordinatorProfile`.
  - Added filter bars to `admin/users.html`, `admin/registrations.html`, and `admin/attendance.html`.
  - Added `@pages_bp.route('/community')` alias pointing to `social_feed`.

### Part C: Instagram-Style Stories in Community
* **Database Models:**
  - `Story` (`stories` table): `id`, `user_id` (FK), `media_type` ('IMAGE', 'VIDEO', 'TEXT'), `media_url`, `text_content`, `background_style`, `caption`, `created_at`, `expires_at`, `is_active`.
  - `StoryView` (`story_views` table): `id`, `story_id` (FK), `user_id` (FK), `viewed_at`, with `UniqueConstraint('story_id', 'user_id')`.
  - Generated database tables via `db.create_all()` without deleting existing demo data.
* **API Endpoints (`app/routes/stories.py`):**
  - `GET /api/v1/stories`: Returns active, unexpired stories grouped by author with `has_unseen` flags and `my_stories`.
  - `POST /api/v1/stories`: Supports photo/video upload (saved to `uploads/stories/`) or text stories with custom background gradients; sets 24-hour expiration.
  - `POST /api/v1/stories/<id>/view`: Records student views idempotently.
  - `GET /api/v1/stories/<id>/viewers`: Privacy-protected. Only the story author or Admin can retrieve viewer lists (returns 403 Forbidden to other users).
  - `DELETE /api/v1/stories/<id>`: Deletes stories with author or admin authorization.
* **Frontend UI (`app/static/css/stories.css`, `app/static/js/stories.js`):**
  - Top horizontal stories tray on `/community` with "Your Story" (+) button and user rings (vibrant gradient for unviewed, subtle grey for viewed).
  - Create Story modal with Photo/Video upload preview and Text Story gradient theme selector.
  - Fullscreen Story Viewer with multi-segment progress bars (5-second auto-advance), touch/click pause, left/right navigation, and author viewers list popup.

---

## 3. Automated Test Verification Matrix

All 10 tests in `tests/test_ml_filter_stories.py` and all 77 existing platform tests pass without regressions:

| Test ID | Test Name | Component | Verified Functionality | Status |
|---|---|---|---|---|
| TC-ML-01 | `test_ml_turnout_model_loading_and_prediction` | ML Predictor | Model bundle loading, 8-feature inference, confidence calculation, factor generation | **PASSED** |
| TC-FL-01 | `test_admin_events_filter` | Filters | Filter by category, status, keyword search, and empty state verification | **PASSED** |
| TC-FL-02 | `test_admin_users_filter` | Filters | Search by name/email, filter by department (`StudentProfile`), filter by role | **PASSED** |
| TC-FL-03 | `test_admin_registrations_and_attendance_filter` | Filters | Registrations filter by event/status and attendance filter by event | **PASSED** |
| TC-FL-04 | `test_community_route_alias` | Routing | `/community` accessible and renders Stories tray and Feed | **PASSED** |
| TC-ST-01 | `test_story_creation_and_expiration` | Stories | Text story creation with custom gradient and 24-hour TTL calculation | **PASSED** |
| TC-ST-02 | `test_story_image_creation` | Stories | Image upload, secure filename, media path in `uploads/stories/` | **PASSED** |
| TC-ST-03 | `test_story_views_and_viewer_privacy` | Stories | Idempotent view tracking, unseen status, 403 privacy block for non-author | **PASSED** |
| TC-ST-04 | `test_story_deletion_permissions` | Stories | 403 Forbidden for unauthorized deletion; 200 OK for author deletion | **PASSED** |
| TC-ST-05 | `test_expired_stories_filtered_out` | Stories | Stories older than 24 hours are excluded from the active story feed | **PASSED** |
| TC-ALL | Full Test Suite (pytest) | Core Suite | 87 total automated tests across all platform modules | **PASSED (87/87)** |

---

## 4. Security & Privacy Controls

1. **Viewer Privacy Control:** `GET /api/v1/stories/<id>/viewers` checks `(story.user_id == current_user.id or current_user.role == 'ADMIN')`. Unauthorized users receive `403 FORBIDDEN`.
2. **Deletion Access Control:** `DELETE /api/v1/stories/<id>` enforces ownership checks.
3. **Upload File Validation:** Validates file extensions against `ALLOWED_IMAGE_EXTENSIONS` and `ALLOWED_VIDEO_EXTENSIONS`, sanitizing file names with `secure_filename`.
4. **Data Isolation:** All local database records and relations are preserved.
