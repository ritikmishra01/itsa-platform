# Function Specification -- ITSA Platform

Format: function_name | module | purpose | inputs | outputs | auth | tables | errors | side effects

---

## Auth Module (app/services/auth_service.py)

### register_user
Purpose: Create new student account
Inputs: email:str, password:str, full_name:str, student_id:str, department:str, year_of_study:int
Returns: User object
Validation: email format, password complexity, year 1-4, student_id alphanumeric
Auth: None (public)
Tables: users, student_profiles
Errors: AUTH_EMAIL_EXISTS, AUTH_STUDENT_ID_EXISTS, AUTH_PASSWORD_WEAK

### login_user
Purpose: Authenticate user and create session
Inputs: email:str, password:str, remember:bool
Returns: User object
Auth: None
Tables: users
Errors: AUTH_INVALID_CREDENTIALS, AUTH_ACCOUNT_SUSPENDED

### change_password
Purpose: Update user password after verifying old password
Inputs: user_id:int, old_password:str, new_password:str
Returns: bool
Auth: Authenticated (owner)
Tables: users
Errors: AUTH_WRONG_PASSWORD, AUTH_PASSWORD_WEAK

### update_profile
Purpose: Update student or coordinator profile fields
Inputs: user_id:int, data:dict
Returns: User object
Auth: Authenticated (owner) or Admin
Tables: users, student_profiles, coordinator_profiles

### suspend_user
Purpose: Suspend a user account
Inputs: admin_id:int, user_id:int, reason:str
Returns: bool
Auth: Admin only
Tables: users
Side effects: logs to audit_logs

---

## Event Module (app/services/event_service.py)

### create_event
Purpose: Create a new event in DRAFT status
Inputs: creator_id:int, data:dict (title, description, category_id, venue_id, start_datetime, end_datetime, registration_deadline, max_participants, ...)
Returns: Event object
Validation: end > start, deadline < start, start in future
Auth: Admin or Coordinator
Tables: events
Errors: EVENT_VALIDATION_ERROR, EVENT_INVALID_DATES

### publish_event
Purpose: Change event from DRAFT to PUBLISHED
Inputs: user_id:int, event_id:int
Returns: Event object
Auth: Admin
Tables: events
Errors: EVENT_ALREADY_PUBLISHED, EVENT_NOT_FOUND

### cancel_event
Purpose: Cancel event and notify all registrants
Inputs: admin_id:int, event_id:int, reason:str
Returns: Event object
Auth: Admin
Tables: events, event_registrations, event_tickets, notifications
Side effects: Invalidates all tickets, cancels all registrations, sends notifications, deducts points

### assign_coordinator
Purpose: Assign coordinator to an event
Inputs: admin_id:int, event_id:int, coordinator_id:int, role_in_event:str
Returns: EventCoordinator object
Auth: Admin
Tables: event_coordinators
Errors: EVENT_NOT_FOUND, AUTH_INSUFFICIENT_ROLE (if user is not coordinator)

---

## Registration Module (app/services/registration_service.py)

### register_for_event
Purpose: Register a student for an event
Inputs: user_id:int, event_id:int
Returns: dict (registration, ticket)
Validation: event open, deadline not passed, capacity not reached, not already registered
Auth: Student
Tables: event_registrations, event_tickets, itsa_points, notifications
Errors: REG_ALREADY_REGISTERED, REG_EVENT_FULL, REG_DEADLINE_PASSED, REG_EVENT_NOT_OPEN
Side effects: generates QR ticket, awards +3 points, sends notification

### cancel_registration
Purpose: Cancel a student registration
Inputs: user_id:int, registration_id:int
Returns: bool
Auth: Student (own) or Admin (any)
Tables: event_registrations, event_tickets, itsa_points
Errors: REG_NOT_FOUND, REG_CANCELLATION_DEADLINE_PASSED, REG_NOT_OWNER
Side effects: invalidates ticket, deducts -3 points, sends notification

---

## Ticket Module (app/services/ticket_service.py)

### generate_ticket
Purpose: Create ticket record and QR image
Inputs: registration_id:int
Returns: EventTicket object
Auth: System (called internally after registration)
Tables: event_tickets
Side effects: creates PNG file at uploads/tickets/{code}.png

### validate_ticket_for_attendance
Purpose: Run all 6 validation steps before marking attendance
Inputs: ticket_code:str, event_id:int, coordinator_id:int
Returns: dict with ticket and registration info
Errors: ATT_TICKET_NOT_FOUND, ATT_WRONG_EVENT, ATT_REGISTRATION_CANCELLED, ATT_TICKET_INVALID, ATT_ALREADY_ATTENDED, ATT_EVENT_NOT_ACTIVE, ATT_COORDINATOR_NOT_ASSIGNED

---

## Attendance Module (app/services/attendance_service.py)

### scan_attendance
Purpose: Main function for coordinator QR scan -- validates and records attendance
Inputs: coordinator_id:int, ticket_code:str, event_id:int
Returns: Attendance object
Auth: Coordinator (assigned to event) or Admin
Tables: event_tickets, event_registrations, attendance, itsa_points, notifications
Errors: All ATT_ error codes
Side effects: awards +10 points, sends notification, updates student total_points

### check_duplicate_attendance
Purpose: Check if student already marked present for this event
Inputs: user_id:int, event_id:int
Returns: bool
Tables: attendance
Note: Also enforced by DB UNIQUE constraint

---

## Social Module (app/services/social_service.py)

### create_post
Purpose: Create a new social post with optional media
Inputs: user_id:int, content:str, post_type:str, media_files:list, event_id:int, hashtag_names:list, mention_usernames:list
Returns: Post object
Auth: Any authenticated user
Tables: posts, post_media, post_hashtags, hashtags, mentions, itsa_points, notifications
Side effects: saves media files, awards +2 points, sends mention notifications

### add_reaction
Purpose: Add or update a reaction on a post
Inputs: user_id:int, post_id:int, reaction_type:str
Returns: PostReaction object
Auth: Any authenticated user
Tables: post_reactions
Note: Replaces existing reaction if any -- no conflict error

### create_comment
Purpose: Add comment to post
Inputs: user_id:int, post_id:int, content:str, mention_usernames:list
Returns: Comment object
Auth: Any authenticated user
Tables: comments, mentions, notifications, itsa_points
Side effects: awards +1 point, sends post owner notification, sends mention notifications

---

## Certificate Module (app/services/certificate_service.py)

### generate_certificate
Purpose: Create certificate record and generate PDF
Inputs: user_id:int, event_id:int, attendance_id:int
Returns: Certificate object
Auth: System (called internally after attendance)
Tables: certificates
Side effects: creates PDF at uploads/certificates/{code}.pdf, sends CERTIFICATE_READY notification

### verify_certificate
Purpose: Public verification of certificate by code
Inputs: certificate_code:str
Returns: dict with {valid, student_name, event_name, event_date, issued_at}
Auth: None (public)
Tables: certificates, users, events
Note: Never returns email, student_id, or other PII

---

## Gamification Module (app/services/gamification_service.py)

### award_points
Purpose: Add points to a student and log transaction
Inputs: user_id:int, points:int, reason:str, related_event_id:int, related_post_id:int
Returns: ItsaPoints transaction object
Auth: System (called internally) or Admin (for manual awards)
Tables: itsa_points, student_profiles
Note: Updates student_profiles.total_points atomically

### calculate_engagement_score
Purpose: Calculate engagement score 0-100 for a student
Inputs: user_id:int
Returns: dict {score:float, breakdown:dict}
Auth: Any authenticated (own score) or Admin (any)
Tables: attendance, event_registrations, feedback, posts, comments
Formula: see GAMIFICATION.md

---

## AI Module (app/services/ai_service.py)

### chat_with_ai
Purpose: Process chatbot message and return AI response
Inputs: user_id:int, message:str, history:list
Returns: str (AI response text)
Auth: Student
Tables: None (stateless per call)
Errors: AI_RATE_LIMIT, AI_SERVICE_UNAVAILABLE, AI_CONTENT_BLOCKED
Security: Input sanitized, length limited, system prompt separate from user input

### recommend_events
Purpose: Get top 5 event recommendations for a student
Inputs: user_id:int
Returns: List of dicts {event_id, title, score, reason}
Auth: Student
Tables: ai_recommendations, student_profiles, event_registrations, attendance, events
Note: Falls back to popular events if student has no history (cold start)

### moderate_content
Purpose: Get AI moderation recommendation for reported content
Inputs: content_text:str
Returns: dict {is_violation, confidence, category, recommendation, reason}
Auth: Admin only
Tables: None
Note: AI recommendation is advisory -- human makes final decision

### predict_event_registrations
Purpose: Predict expected registration count for an event
Inputs: event_id:int
Returns: dict {predicted_count, confidence_interval, confidence, model_version}
Auth: Admin or Coordinator (assigned)
Tables: events, event_registrations (for feature extraction)
Note: Requires minimum 10 historical events for reliable predictions
