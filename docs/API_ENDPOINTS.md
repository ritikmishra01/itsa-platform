# API Endpoints — ITSA Platform

> Base URL: `/api/v1` | Auth: Session cookie | Format: JSON

---

## AUTH ENDPOINTS

### POST /api/v1/auth/register
Register a new student account.
- **Auth**: None (public)
- **Roles**: Anyone

**Request Body**:
```json
{
  "email": "student@college.edu",
  "password": "SecurePass123",
  "full_name": "Rahul Sharma",
  "student_id": "CS2021001",
  "department": "Computer Science",
  "year_of_study": 2
}
```

**Success 201**:
```json
{
  "success": true,
  "data": { "id": 1, "email": "student@college.edu", "role": "STUDENT" },
  "message": "Registration successful"
}
```

**Errors**: `400 AUTH_VALIDATION_ERROR`, `409 AUTH_EMAIL_EXISTS`, `409 AUTH_STUDENT_ID_EXISTS`

---

### POST /api/v1/auth/login
- **Auth**: None | **Request**: `{ "email": "...", "password": "..." }`
- **Success 200**: `{ "success": true, "data": { "id": 1, "role": "STUDENT", "full_name": "..." } }`
- **Errors**: `401 AUTH_INVALID_CREDENTIALS`, `403 AUTH_ACCOUNT_SUSPENDED`

---

### POST /api/v1/auth/logout
- **Auth**: Required | **Success 200**: `{ "success": true, "message": "Logged out" }`

---

### GET /api/v1/auth/me
Get the currently authenticated user.
- **Auth**: Required
- **Success 200**: Full user profile object including student/coordinator profile data

---

### PUT /api/v1/auth/change-password
- **Auth**: Required
- **Request**: `{ "old_password": "...", "new_password": "...", "confirm_password": "..." }`
- **Errors**: `400 AUTH_WRONG_PASSWORD`, `400 AUTH_PASSWORD_WEAK`

---

### PUT /api/v1/auth/profile
Update current user profile.
- **Auth**: Required
- **Request**: `{ "full_name": "...", "bio": "...", "phone": "...", "github_url": "...", "linkedin_url": "...", "department": "...", "year_of_study": 2, "interests": "..." }`
- Profile image upload via multipart: `PUT /api/v1/auth/profile/image`

---

## EVENT ENDPOINTS

### GET /api/v1/events
List all published events with optional filters.
- **Auth**: Optional (unauthenticated users see public events)
- **Query Params**: `status`, `category_id`, `search`, `page`, `per_page`, `date_from`, `date_to`
- **Success 200**: Paginated list of events

---

### POST /api/v1/events
Create a new event.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR

**Request Body**:
```json
{
  "title": "Web Dev Workshop",
  "description": "Learn modern web development...",
  "category_id": 2,
  "venue_id": 1,
  "start_datetime": "2026-09-15T09:00:00",
  "end_datetime": "2026-09-15T17:00:00",
  "registration_deadline": "2026-09-14T23:59:00",
  "max_participants": 50,
  "is_free": true,
  "tags": "web,javascript,react"
}
```
- **Success 201**: Created event object
- **Errors**: `400 EVENT_VALIDATION_ERROR`, `422 EVENT_INVALID_DATES`

---

### GET /api/v1/events/{id}
Get a single event by ID.
- **Auth**: Optional | **Success 200**: Full event object with coordinator list and registration status

---

### PUT /api/v1/events/{id}
Update an event.
- **Auth**: Required | **Roles**: ADMIN (any event), COORDINATOR (assigned events only)
- **Errors**: `403 EVENT_NOT_ASSIGNED`, `404 EVENT_NOT_FOUND`, `422 EVENT_CANNOT_EDIT_STATUS`

---

### DELETE /api/v1/events/{id}
Delete an event (Admin only).
- **Auth**: Required | **Roles**: ADMIN
- **Note**: Sets status to CANCELLED. Hard delete only in DRAFT status.

---

### POST /api/v1/events/{id}/publish
Change event status to PUBLISHED.
- **Auth**: Required | **Roles**: ADMIN
- **Errors**: `422 EVENT_ALREADY_PUBLISHED`, `422 EVENT_MISSING_COORDINATOR`

---

### POST /api/v1/events/{id}/cancel
Cancel an event and notify all registrants.
- **Auth**: Required | **Roles**: ADMIN
- **Request**: `{ "reason": "Venue unavailable" }`

---

### POST /api/v1/events/{id}/register
Register the current student for an event.
- **Auth**: Required | **Roles**: STUDENT

**Business Logic**:
1. Check event status = REGISTRATION_OPEN
2. Check deadline not passed
3. Check max_participants not reached
4. Check student not already registered
5. Create registration → Generate ticket → Send notification → Award points

- **Success 201**: `{ "registration": {...}, "ticket": { "ticket_code": "...", "qr_url": "..." } }`
- **Errors**: `409 REG_ALREADY_REGISTERED`, `422 REG_EVENT_FULL`, `422 REG_DEADLINE_PASSED`, `422 REG_EVENT_NOT_OPEN`

---

### DELETE /api/v1/events/{id}/register
Cancel the current student registration.
- **Auth**: Required | **Roles**: STUDENT
- **Errors**: `404 REG_NOT_FOUND`, `422 REG_CANCELLATION_DEADLINE_PASSED`

---

### GET /api/v1/events/{id}/registrations
Get registration list for an event.
- **Auth**: Required | **Roles**: ADMIN (any), COORDINATOR (assigned)
- **Query Params**: `status`, `page`, `per_page`

---

### GET /api/v1/events/{id}/attendance
Get attendance list for an event.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR (assigned)

---

### POST /api/v1/events/{id}/coordinators
Assign a coordinator to an event.
- **Auth**: Required | **Roles**: ADMIN
- **Request**: `{ "coordinator_id": 5, "role_in_event": "Lead" }`

---

### GET /api/v1/events/{id}/gallery
Get gallery media for an event.
- **Auth**: Optional | **Success 200**: List of gallery items

### POST /api/v1/events/{id}/gallery
Upload media to event gallery.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR (assigned)
- **Multipart form**: `file`, `caption`, `is_featured`

---

### GET /api/v1/events/{id}/feedback
Get feedback for an event.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR (assigned)

### GET /api/v1/events/{id}/analytics
Get analytics data for an event.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR (assigned)
- **Returns**: registration_count, attendance_count, attendance_rate, avg_rating, hourly_attendance

---

## TICKET ENDPOINTS

### GET /api/v1/tickets/{id}
Get ticket details.
- **Auth**: Required | **Roles**: STUDENT (own ticket only), ADMIN

**Success 200**:
```json
{
  "id": 1,
  "ticket_code": "ITSA-TKT-a1b2c3d4-...",
  "event": { "title": "Web Dev Workshop", "date": "..." },
  "student_name": "Rahul Sharma",
  "is_valid": true,
  "issued_at": "2026-09-01T10:30:00"
}
```

### GET /api/v1/tickets/{id}/qr
Get QR code image for a ticket.
- **Auth**: Required | **Roles**: STUDENT (own ticket only)
- **Returns**: PNG image file (with Content-Type: image/png)

---

## ATTENDANCE ENDPOINTS

### POST /api/v1/attendance/scan
**Most critical endpoint** — Coordinator scans student QR to mark attendance.
- **Auth**: Required | **Roles**: COORDINATOR, ADMIN

**Request Body**:
```json
{
  "ticket_code": "ITSA-TKT-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_id": 42
}
```

**6-Step Validation**:
1. ticket_code exists in event_tickets
2. ticket belongs to event_id
3. registration status = CONFIRMED
4. ticket is_valid = TRUE
5. No existing attendance for (event_id, user_id)
6. Event status is ONGOING or REGISTRATION_CLOSED

**Success 200**:
```json
{
  "success": true,
  "data": {
    "student_name": "Rahul Sharma",
    "scanned_at": "2026-09-15T09:32:00",
    "status": "PRESENT"
  },
  "message": "Attendance recorded successfully"
}
```

**Errors**: `404 ATT_TICKET_NOT_FOUND`, `409 ATT_ALREADY_ATTENDED`, `422 ATT_WRONG_EVENT`, `422 ATT_REGISTRATION_CANCELLED`, `422 ATT_TICKET_INVALID`, `422 ATT_EVENT_NOT_ACTIVE`, `403 ATT_COORDINATOR_NOT_ASSIGNED`

---

### GET /api/v1/attendance/my
Get current student's attendance history.
- **Auth**: Required | **Roles**: STUDENT
- **Returns**: List of attended events with timestamps

### PUT /api/v1/attendance/{id}
Override attendance record.
- **Auth**: Required | **Roles**: ADMIN
- **Request**: `{ "status": "PRESENT", "notes": "Manual correction" }`

---

## SOCIAL FEED ENDPOINTS

### GET /api/v1/posts
Get paginated feed of posts.
- **Auth**: Required | **Query Params**: `page`, `per_page`, `user_id`, `event_id`
- **Returns**: Paginated posts with reaction counts, comment counts, user reaction

### POST /api/v1/posts
Create a new post.
- **Auth**: Required | **Roles**: All authenticated
- **Multipart form** (for media uploads):
  - `content` (text)
  - `post_type` (TEXT/IMAGE/VIDEO/MIXED)
  - `event_id` (optional)
  - `images[]` (up to 5 files)
  - `video` (optional, 1 file)
  - Auto-detects hashtags and mentions from content

### GET /api/v1/posts/{id}
Get a single post with all data.

### PUT /api/v1/posts/{id}
Edit a post.
- **Auth**: Required | **Roles**: Post owner, ADMIN
- **Request**: `{ "content": "Updated text" }`

### DELETE /api/v1/posts/{id}
Delete a post (cascade: media, reactions, comments, saves, shares).
- **Auth**: Required | **Roles**: Post owner, ADMIN

### POST /api/v1/posts/{id}/react
Add or update a reaction on a post.
- **Auth**: Required
- **Request**: `{ "reaction_type": "LIKE" }`
- **Note**: Replaces existing reaction if any

### DELETE /api/v1/posts/{id}/react
Remove reaction from a post.
- **Auth**: Required

### GET /api/v1/posts/{id}/comments
Get comments for a post with replies.
- **Auth**: Required | **Query Params**: `page`, `per_page`

### POST /api/v1/posts/{id}/comments
Add a comment to a post.
- **Auth**: Required
- **Request**: `{ "content": "Great post!" }`

### POST /api/v1/posts/{id}/share
Share a post to the feed.
- **Auth**: Required
- **Request**: `{ "platform": "FEED" }`

### POST /api/v1/posts/{id}/save
Save a post to personal collection.
- **Auth**: Required
- **Errors**: `409 SOCIAL_ALREADY_SAVED`

### DELETE /api/v1/posts/{id}/save
Remove a post from saved collection.

### POST /api/v1/posts/{id}/report
Report a post.
- **Auth**: Required
- **Request**: `{ "reason": "INAPPROPRIATE", "description": "Contains offensive content" }`

---

## COMMENT ENDPOINTS

### PUT /api/v1/comments/{id}
Edit a comment.
- **Auth**: Required | **Roles**: Comment owner, ADMIN

### DELETE /api/v1/comments/{id}
Delete a comment.
- **Auth**: Required | **Roles**: Comment owner, ADMIN

### GET /api/v1/comments/{id}/replies
Get replies for a comment.

### POST /api/v1/comments/{id}/replies
Add a reply to a comment.
- **Request**: `{ "content": "I agree!", "mentioned_user_id": 5 }`

### POST /api/v1/comments/{id}/report
Report a comment.

---

## CERTIFICATE ENDPOINTS

### GET /api/v1/certificates
Get all certificates for the current student.
- **Auth**: Required | **Roles**: STUDENT

### GET /api/v1/certificates/{id}
Get certificate details.
- **Auth**: Required | **Roles**: Certificate owner, ADMIN

### GET /api/v1/certificates/{id}/download
Download certificate as PDF.
- **Auth**: Required | **Roles**: Certificate owner, ADMIN
- **Returns**: PDF file

### GET /api/v1/certificates/verify/{code}
**Public endpoint** — Verify a certificate by code.
- **Auth**: None
- **Returns**:
```json
{
  "valid": true,
  "student_name": "Rahul Sharma",
  "event_name": "Web Dev Workshop",
  "event_date": "2026-09-15",
  "issued_at": "2026-09-15T18:00:00",
  "certificate_code": "ITSA-CERT-..."
}
```
- **Errors**: `404 CERT_NOT_FOUND`, `410 CERT_REVOKED`

---

## FEEDBACK ENDPOINTS

### POST /api/v1/feedback
Submit feedback for an event.
- **Auth**: Required | **Roles**: STUDENT
- **Request**: `{ "event_id": 42, "rating": 4, "content": "Great workshop!" }`
- **Validation**: Student must have PRESENT attendance for the event
- **Errors**: `409 FEED_ALREADY_SUBMITTED`, `422 FEED_NOT_ATTENDED`, `422 FEED_WINDOW_CLOSED`

### GET /api/v1/feedback/my
Get current student feedback submissions.

---

## NOTIFICATION ENDPOINTS

### GET /api/v1/notifications
Get notifications for current user.
- **Query Params**: `page`, `per_page`, `unread_only`

### PUT /api/v1/notifications/{id}/read
Mark notification as read.

### PUT /api/v1/notifications/read-all
Mark all notifications as read.

### DELETE /api/v1/notifications/{id}
Delete a notification.

---

## HASHTAG ENDPOINTS

### GET /api/v1/hashtags
Get trending hashtags (top 20 by post_count).

### GET /api/v1/hashtags/{name}/posts
Get posts tagged with a specific hashtag.
- **Query Params**: `page`, `per_page`

---

## GAMIFICATION ENDPOINTS

### GET /api/v1/points/my
Get current student points balance and history.
- **Returns**: `{ "total": 145, "transactions": [...] }`

### GET /api/v1/leaderboard
Get the leaderboard.
- **Query Params**: `department`, `year`, `page`, `per_page`
- **Returns**: Ranked list of students with points

---

## ADMIN ENDPOINTS

### GET /api/v1/admin/users
Get all users with filters.
- **Auth**: Required | **Roles**: ADMIN
- **Query Params**: `role`, `department`, `is_suspended`, `search`, `page`

### POST /api/v1/admin/users
Create a new user (any role).

### PUT /api/v1/admin/users/{id}
Update any user's data.

### DELETE /api/v1/admin/users/{id}
Soft-delete a user account.

### POST /api/v1/admin/users/{id}/suspend
Suspend a user account.
- **Request**: `{ "reason": "Policy violation" }`

### POST /api/v1/admin/users/{id}/unsuspend
Remove user suspension.

### GET /api/v1/admin/coordinators
List all coordinator accounts.

### POST /api/v1/admin/coordinators
Create a new coordinator account.
- **Request**: `{ "email": "...", "password": "...", "full_name": "...", "employee_id": "...", "designation": "...", "department": "..." }`

### GET /api/v1/admin/analytics/overview
System-wide analytics overview.
- **Returns**: `{ "total_users": 500, "total_events": 25, "total_registrations": 1200, "total_attendance": 980, "total_certificates": 920, "active_students_month": 200 }`

### GET /api/v1/admin/analytics/events
Events analytics data for charts.

### GET /api/v1/admin/analytics/users
Users analytics data for charts.

### GET /api/v1/admin/reports
List all content reports.
- **Query Params**: `status`, `page`

### PUT /api/v1/admin/reports/{id}
Resolve a content report.
- **Request**: `{ "status": "RESOLVED", "action": "REMOVE_POST", "note": "Content violated guidelines" }`

### GET /api/v1/admin/points
View all points transactions.

### POST /api/v1/admin/points/adjust
Manually adjust a student points.
- **Request**: `{ "user_id": 5, "points": 25, "reason": "COMPETITION", "note": "Won hackathon" }`

---

## AI ENDPOINTS

### POST /api/v1/ai/chat
Send a message to the ITSA AI Chatbot.
- **Auth**: Required | **Roles**: STUDENT
- **Rate Limit**: 20 messages/hour/user
- **Request**: `{ "message": "When is the next hackathon?", "history": [] }`
- **Response**: `{ "reply": "The next hackathon is...", "session_id": "..." }`

### GET /api/v1/ai/recommendations
Get AI event recommendations for current student.
- **Auth**: Required | **Roles**: STUDENT
- **Returns**: Top 5 recommended events with scores and reasons

### POST /api/v1/ai/generate-description
Generate an event description.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR
- **Request**: `{ "title": "...", "category": "...", "date": "...", "topics": ["..."], "target_audience": "..." }`
- **Returns**: `{ "description": "..." }`

### POST /api/v1/ai/generate-announcement
Generate an event announcement.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR
- **Request**: `{ "event_id": 42, "tone": "formal", "channel": "email" }`

### POST /api/v1/ai/analyze-feedback
Analyze feedback for an event using AI.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR (assigned)
- **Request**: `{ "event_id": 42 }`
- **Returns**: `{ "sentiment": "POSITIVE", "themes": [...], "strengths": [...], "improvements": [...], "score": 4.2 }`

### POST /api/v1/ai/moderate-content
Get AI moderation recommendation for reported content.
- **Auth**: Required | **Roles**: ADMIN
- **Request**: `{ "content": "..." }`
- **Returns**: `{ "is_violation": false, "confidence": 0.85, "category": "NONE", "recommendation": "approve" }`

### GET /api/v1/ai/engagement-score
Get AI engagement score for current student.
- **Auth**: Required | **Roles**: STUDENT
- **Returns**: `{ "score": 72.5, "breakdown": { "attendance": 40, "posts": 10, ... } }`

### GET /api/v1/ai/predict-registrations/{event_id}
Get ML registration prediction for an event.
- **Auth**: Required | **Roles**: ADMIN, COORDINATOR (assigned)
- **Returns**: `{ "predicted_count": 45, "confidence_interval": [35, 55], "confidence": "medium" }`
