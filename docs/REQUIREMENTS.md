# Requirements — ITSA Platform

> Every requirement has a unique ID. Reference these IDs in code comments, PR descriptions, and test cases.

---

## FUNCTIONAL REQUIREMENTS

---

### Authentication (FR-AUTH)

| ID | Requirement |
|---|---|
| FR-AUTH-001 | System shall allow new users to register with: email, password, full name, student ID, department, year of study |
| FR-AUTH-002 | System shall validate email format and uniqueness on registration |
| FR-AUTH-003 | System shall enforce password minimum 8 characters with at least one uppercase, one lowercase, one digit |
| FR-AUTH-004 | System shall hash passwords using PBKDF2-SHA256 (Werkzeug) — never store plaintext |
| FR-AUTH-005 | System shall allow registered users to login with email + password |
| FR-AUTH-006 | System shall create a secure server-side session on successful login |
| FR-AUTH-007 | System shall allow users to logout and destroy the session |
| FR-AUTH-008 | System shall assign roles (STUDENT, COORDINATOR, ADMIN) stored in the database |
| FR-AUTH-009 | System shall allow users to change their password (requires old password verification) |
| FR-AUTH-010 | System shall allow Admin to suspend/unsuspend user accounts |
| FR-AUTH-011 | Suspended users shall not be able to login |
| FR-AUTH-012 | System shall protect all non-public routes with authentication checks |
| FR-AUTH-013 | System shall never trust role information supplied by the client |

---

### User Management (FR-USER)

| ID | Requirement |
|---|---|
| FR-USER-001 | Students shall have a profile with: photo, bio, department, year, interests, GitHub URL, LinkedIn URL |
| FR-USER-002 | Students shall be able to view and edit their own profile |
| FR-USER-003 | Students shall be able to view other students public profiles |
| FR-USER-004 | Coordinators shall have a profile with: employee ID, designation, department |
| FR-USER-005 | Admin shall be able to view all user profiles |
| FR-USER-006 | Admin shall be able to edit any user profile |
| FR-USER-007 | Users shall be able to upload a profile image (JPEG/PNG/WEBP, max 2MB) |
| FR-USER-008 | Admin shall be able to create coordinator accounts |

---

### Event Management (FR-EVENT)

| ID | Requirement |
|---|---|
| FR-EVENT-001 | Admin and authorized Coordinators shall be able to create events |
| FR-EVENT-002 | Events shall have statuses: DRAFT, PUBLISHED, REGISTRATION_OPEN, REGISTRATION_CLOSED, ONGOING, COMPLETED, CANCELLED |
| FR-EVENT-003 | Events shall belong to a category (Technical, Cultural, Sports, Workshop, Seminar, Competition, Community Service, Other) |
| FR-EVENT-004 | Events shall have: title, description, category, venue, poster image, start/end datetime, registration deadline, max participants |
| FR-EVENT-005 | Admin shall be able to edit events in any status |
| FR-EVENT-006 | Coordinators shall only be able to edit events they are assigned to |
| FR-EVENT-007 | Admin shall be able to cancel any event |
| FR-EVENT-008 | Cancelling an event shall invalidate all tickets and notify all registrants |
| FR-EVENT-009 | Admin shall be able to assign one or more coordinators to an event |
| FR-EVENT-010 | At least one coordinator must be assigned before event moves to REGISTRATION_OPEN |
| FR-EVENT-011 | Events shall be searchable by title, category, status, date range |
| FR-EVENT-012 | Completed events shall be archived and viewable in a Past Events section |
| FR-EVENT-013 | Coordinators and Admin shall be able to upload photos/videos to the event gallery |
| FR-EVENT-014 | System shall track registration count against max_participants |
| FR-EVENT-015 | System shall enforce the registration deadline — no registrations after deadline |

---

### Registration System (FR-REG)

| ID | Requirement |
|---|---|
| FR-REG-001 | Authenticated students shall be able to register for REGISTRATION_OPEN events |
| FR-REG-002 | System shall check: event is open, deadline not passed, capacity not reached, student not already registered |
| FR-REG-003 | Each registration shall have a unique registration number: ITSA-{EVENT_ID}-{YEAR}-{SEQUENCE} |
| FR-REG-004 | System shall send a confirmation notification (in-app + email) upon registration |
| FR-REG-005 | Students shall be able to cancel their registration before the registration deadline |
| FR-REG-006 | Cancelling registration shall invalidate the ticket and deduct points |
| FR-REG-007 | Admin shall be able to cancel any registration at any time |
| FR-REG-008 | Students shall be able to view all their registrations (past, upcoming, cancelled) |

---

### Ticket System (FR-TICKET)

| ID | Requirement |
|---|---|
| FR-TICKET-001 | System shall automatically generate a digital QR ticket upon confirmed registration |
| FR-TICKET-002 | Each ticket shall have a unique ticket code in UUID format: ITSA-TKT-{uuid4} |
| FR-TICKET-003 | The QR code shall encode only the ticket_code — no personal data |
| FR-TICKET-004 | Students shall be able to view their ticket (with QR code) on the platform |
| FR-TICKET-005 | Students shall be able to download their QR code image |
| FR-TICKET-006 | Tickets shall be invalidated when registration is cancelled |

---

### QR Attendance (FR-ATT)

| ID | Requirement |
|---|---|
| FR-ATT-001 | The COORDINATOR (not the student) shall scan the student QR ticket to mark attendance |
| FR-ATT-002 | Backend shall validate: ticket exists, belongs to correct event, registration is CONFIRMED, ticket is valid, not already attended, event is active |
| FR-ATT-003 | System shall record: student_id, event_id, registration_id, scanned_by (coordinator), scanned_at timestamp |
| FR-ATT-004 | System shall prevent duplicate attendance with a database unique constraint on (event_id, user_id) |
| FR-ATT-005 | System shall return a clear error if duplicate scan is attempted |
| FR-ATT-006 | Coordinator shall be able to view live attendance list for their assigned event |
| FR-ATT-007 | Student shall be able to view their own attendance history |
| FR-ATT-008 | Admin shall be able to manually override attendance records |
| FR-ATT-009 | Coordinator must be assigned to the event to scan attendance for it |

---

### Social Feed (FR-SOCIAL)

| ID | Requirement |
|---|---|
| FR-SOCIAL-001 | Students shall be able to create posts (TEXT, IMAGE, VIDEO, MIXED) |
| FR-SOCIAL-002 | Posts shall support up to 5 images (max 10MB each, JPEG/PNG/WEBP) |
| FR-SOCIAL-003 | Posts shall support up to 1 video (max 100MB, MP4/MOV) |
| FR-SOCIAL-004 | Post text shall be max 5000 characters |
| FR-SOCIAL-005 | Students shall be able to edit their own posts |
| FR-SOCIAL-006 | Students shall be able to delete their own posts |
| FR-SOCIAL-007 | Admin shall be able to delete any post |
| FR-SOCIAL-008 | Students shall be able to react to posts (LIKE, LOVE, CELEBRATE, INSIGHTFUL, SUPPORT) |
| FR-SOCIAL-009 | Each user can have only one reaction per post (can change reaction type) |
| FR-SOCIAL-010 | Students shall be able to comment on posts (max 2000 chars) |
| FR-SOCIAL-011 | Students shall be able to reply to comments (one level deep, max 1000 chars) |
| FR-SOCIAL-012 | Students shall be able to share posts to the ITSA feed |
| FR-SOCIAL-013 | Students shall be able to save posts to a personal collection |
| FR-SOCIAL-014 | Posts shall support hashtags (#hashtag) auto-detected from content |
| FR-SOCIAL-015 | Posts and comments shall support @mentions that trigger notifications |
| FR-SOCIAL-016 | Students shall be able to report posts and comments |
| FR-SOCIAL-017 | Feed shall use pagination (20 posts per page, chronological order) |
| FR-SOCIAL-018 | Students shall be able to view posts by hashtag |
| FR-SOCIAL-019 | Admin shall be able to moderate reported content |
| FR-SOCIAL-020 | AI shall assist admin with content moderation recommendations |

---

### Certificate System (FR-CERT)

| ID | Requirement |
|---|---|
| FR-CERT-001 | System shall auto-generate a PDF certificate when attendance status = PRESENT |
| FR-CERT-002 | Each certificate shall have a unique code: ITSA-CERT-{uuid4} |
| FR-CERT-003 | Certificate shall contain: student name, event title, event date, certificate code, verification QR |
| FR-CERT-004 | Students shall be able to download their certificates as PDF |
| FR-CERT-005 | Anyone shall be able to verify a certificate at /certificates/verify/{code} without exposing PII |
| FR-CERT-006 | Admin shall be able to revoke a certificate (is_valid = FALSE) |
| FR-CERT-007 | Only one certificate per student per event |

---

### Feedback System (FR-FEED)

| ID | Requirement |
|---|---|
| FR-FEED-001 | Students who attended (PRESENT) shall be able to submit feedback for the event |
| FR-FEED-002 | Feedback shall include: rating (1-5 stars, required), text content (optional, max 2000 chars) |
| FR-FEED-003 | Only one feedback submission per student per event |
| FR-FEED-004 | Coordinator and Admin shall be able to view all feedback for an event |
| FR-FEED-005 | Admin/Coordinator shall be able to trigger AI sentiment analysis on event feedback |

---

### Notification System (FR-NOTIF)

| ID | Requirement |
|---|---|
| FR-NOTIF-001 | System shall send in-app notifications for key events |
| FR-NOTIF-002 | System shall send email notifications via SMTP for key events |
| FR-NOTIF-003 | Registration confirmation shall trigger both in-app and email notification |
| FR-NOTIF-004 | Event reminders shall be sent 24 hours before event start |
| FR-NOTIF-005 | Event changes (time, venue, cancellation) shall notify all registrants |
| FR-NOTIF-006 | Certificate generation shall trigger a notification |
| FR-NOTIF-007 | Post reactions, comments, and mentions shall trigger notifications |
| FR-NOTIF-008 | Admin announcements shall be broadcastable to all students |
| FR-NOTIF-009 | Users shall be able to mark notifications as read |
| FR-NOTIF-010 | Email sending failure shall not break the main registration/attendance flow |

---

### Gamification (FR-GAME)

| ID | Requirement |
|---|---|
| FR-GAME-001 | Students shall earn ITSA Points for: attendance (+10), registration (+3), feedback (+5), post (+2), comment (+1), volunteering (+15) |
| FR-GAME-002 | Points shall be deducted on registration cancellation (-3) |
| FR-GAME-003 | Total points shall never go below 0 |
| FR-GAME-004 | All point transactions shall be logged with reason and timestamp |
| FR-GAME-005 | A leaderboard shall rank students by total ITSA points |
| FR-GAME-006 | Admin shall be able to manually award or deduct points with a reason |
| FR-GAME-007 | An Engagement Score (0-100) shall be calculated per student |

---

### AI Features (AI)

| ID | Requirement |
|---|---|
| AI-001 | System shall provide an AI chatbot (Gemini) to answer ITSA-related questions |
| AI-002 | System shall provide AI-based event recommendations (Scikit-learn) per student |
| AI-003 | System shall provide AI feedback sentiment analysis for events (Gemini) |
| AI-004 | System shall provide AI comment moderation assistance (Gemini) |
| AI-005 | System shall provide AI event description generation (Gemini) |
| AI-006 | System shall provide AI announcement generation (Gemini) |
| AI-007 | System shall provide AI social caption generation (Gemini) |
| AI-008 | System shall provide AI registration prediction per event (Scikit-learn) |
| AI-009 | System shall calculate and display an AI Engagement Score per student |
| AI-010 | Gemini API key shall always be stored in .env — never hardcoded |

---

### Analytics (FR-AN)

| ID | Requirement |
|---|---|
| FR-AN-001 | Admin shall have a dashboard showing: total users, events, registrations, attendance, certificates, active students |
| FR-AN-002 | Admin shall see monthly registration trends (line chart) |
| FR-AN-003 | Admin shall see events by category (pie chart) |
| FR-AN-004 | Admin shall see department-wise participation (bar chart) |
| FR-AN-005 | Admin shall see year-wise participation (bar chart) |
| FR-AN-006 | Coordinator shall see analytics only for their assigned events |
| FR-AN-007 | System shall support PDF report generation for events |
| FR-AN-008 | All charts shall use Chart.js |

---

## NON-FUNCTIONAL REQUIREMENTS

| ID | Category | Requirement |
|---|---|---|
| NFR-001 | Security | Passwords stored as PBKDF2-SHA256 hash — never plaintext |
| NFR-002 | Security | All routes protected by server-side authorization |
| NFR-003 | Security | All user input validated server-side before processing |
| NFR-004 | Security | SQL injection prevented via SQLAlchemy ORM parameterized queries |
| NFR-005 | Security | XSS prevented via Jinja2 auto-escaping and CSP headers |
| NFR-006 | Security | File uploads validated for type, size, and renamed to UUID-based names |
| NFR-007 | Security | API keys and secrets stored only in .env — never committed |
| NFR-008 | Security | Audit log maintained for all admin actions |
| NFR-009 | Performance | Page load time shall be under 3 seconds for standard pages |
| NFR-010 | Performance | Feed pagination prevents loading all posts at once |
| NFR-011 | Performance | Database indexes on all foreign keys and frequently queried columns |
| NFR-012 | Scalability | Application shall handle 500 concurrent users without degradation |
| NFR-013 | Availability | Application shall target 99% uptime on Render |
| NFR-014 | Maintainability | Code shall follow PEP 8 and project CODING_STANDARDS.md |
| NFR-015 | Maintainability | All business logic shall be in the service layer (not routes) |
| NFR-016 | Usability | UI shall be responsive on mobile (375px+) and desktop (1280px+) |
| NFR-017 | Reliability | Database transactions used for critical operations (registration, attendance) |
| NFR-018 | Data Integrity | Foreign key constraints enforced at database level |
| NFR-019 | Privacy | Certificate verification page shall not expose student PII |
| NFR-020 | Privacy | QR codes shall not contain personal data — only a UUID ticket code |
