# Development Roadmap — ITSA Platform

---

## PHASE 1: Foundation (Week 1–2)

**Goal**: Working Flask app with database and authentication

**Deliverables**:
- [ ] Project scaffold with Flask app factory pattern
- [ ] All SQLAlchemy models created and migrated
- [ ] Student registration (with student_id, department, year)
- [ ] Login and logout (Flask-Login)
- [ ] Role system (STUDENT, COORDINATOR, ADMIN)
- [ ] Role-based decorators (@admin_required, @coordinator_required)
- [ ] Base HTML template with Bootstrap 5 navigation
- [ ] Auth pages (register, login)
- [ ] .env configuration working
- [ ] Flask-Migrate initialized

**Testing checkpoint**: Auth registration and login work end-to-end.

---

## PHASE 2: Event Management (Week 3–4)

**Goal**: Full event CRUD with lifecycle management

**Deliverables**:
- [ ] Event model and migration
- [ ] Event CRUD (Create, Read, Update, Delete)
- [ ] Event status workflow (DRAFT → PUBLISHED → REGISTRATION_OPEN → ...)
- [ ] Event categories and venues
- [ ] Event poster upload
- [ ] Coordinator assignment to events
- [ ] Public events listing page with search and filter
- [ ] Event detail page
- [ ] Admin event management panel

**Testing checkpoint**: Admin can create event, publish it, assign coordinator.

---

## PHASE 3: Registration & Tickets (Week 5)

**Goal**: Students can register and get QR tickets

**Deliverables**:
- [ ] Registration flow (eligibility checks, capacity, deadline)
- [ ] Registration number generation
- [ ] QR ticket generation (python-qrcode)
- [ ] My Tickets page for students
- [ ] Ticket QR display and download
- [ ] Registration cancellation
- [ ] Coordinator registration list view
- [ ] Registration confirmation notification

**Testing checkpoint**: Student registers, gets QR ticket, can view and download.

---

## PHASE 4: QR Attendance (Week 6)

**Goal**: Coordinator scans student QR to mark attendance

**Deliverables**:
- [ ] Coordinator QR scanner page (html5-qrcode JS)
- [ ] POST /api/v1/attendance/scan with 6-step validation
- [ ] Duplicate attendance prevention
- [ ] Live attendance count display
- [ ] Student attendance history page
- [ ] Admin attendance override

**Testing checkpoint**: Full scan flow works. Duplicate scan rejected. Wrong event rejected.

---

## PHASE 5: Certificates & Feedback (Week 7)

**Goal**: Auto-generate certificates and collect feedback

**Deliverables**:
- [ ] PDF certificate generation (ReportLab)
- [ ] Certificate triggered on attendance record
- [ ] My Certificates page
- [ ] Certificate download
- [ ] Public certificate verification page
- [ ] Feedback form (rating + text)
- [ ] Feedback eligibility check (attended only)
- [ ] Coordinator feedback view

**Testing checkpoint**: Attended student gets certificate. Verification page works without exposing PII.

---

## PHASE 6: Social Feed (Week 8–9)

**Goal**: Full social community feed

**Deliverables**:
- [ ] Post creation (text, images, video)
- [ ] Feed with pagination (20 posts/page)
- [ ] Post reactions (5 types)
- [ ] Comments and replies
- [ ] Hashtag detection and pages
- [ ] Mention detection and notifications
- [ ] Post sharing (to ITSA feed)
- [ ] Post saving and saved posts page
- [ ] Content reporting

**Testing checkpoint**: Full social cycle: create post → react → comment → reply → share → save.

---

## PHASE 7: Notifications & Gamification (Week 10)

**Goal**: Point system, leaderboard, and full notification system

**Deliverables**:
- [ ] In-app notification creation and display
- [ ] Email notifications (SMTP)
- [ ] Notification bell with unread count
- [ ] Mark as read / mark all read
- [ ] ITSA Points transaction system
- [ ] Points awarded for: attendance, registration, feedback, posts
- [ ] Leaderboard page
- [ ] Engagement score calculation and display
- [ ] Admin points management

**Testing checkpoint**: Points awarded on attendance. Leaderboard ranks correctly. Email sent on registration.

---

## PHASE 8: AI GenAI Features (Week 11)

**Goal**: Gemini API integration for chatbot and content tools

**Deliverables**:
- [ ] Gemini API client wrapper (app/ai/gemini_client.py)
- [ ] ITSA Chatbot page and API endpoint
- [ ] Event description generator (in event create form)
- [ ] Announcement generator
- [ ] Social caption generator
- [ ] Feedback sentiment analysis
- [ ] AI comment moderation (admin panel)
- [ ] Rate limiting for AI endpoints
- [ ] Prompt injection protection

**Testing checkpoint**: Chatbot responds. Description generated. Moderation returns valid JSON.

---

## PHASE 9: AI ML Features (Week 12)

**Goal**: Scikit-learn recommendation and prediction

**Deliverables**:
- [ ] Training data pipeline from database
- [ ] Event recommendation model (content-based filtering)
- [ ] Registration prediction model (Random Forest)
- [ ] Engagement score formula implementation
- [ ] Attendance pattern analysis (Pandas)
- [ ] Model serialization (joblib)
- [ ] Cold-start handling for new students
- [ ] Recommendations shown on student dashboard

**Testing checkpoint**: Student gets relevant recommendations. Prediction returns sensible count.

---

## PHASE 10: Analytics & Admin Panel (Week 13)

**Goal**: Complete admin dashboard and analytics

**Deliverables**:
- [ ] Admin dashboard with stat cards
- [ ] Monthly trend charts (Chart.js)
- [ ] Department and year participation charts
- [ ] Coordinator dashboard (assigned events only)
- [ ] Event analytics page
- [ ] PDF report generation (ReportLab)
- [ ] Admin user management (list, suspend, create coordinator)
- [ ] Admin content moderation panel (reports queue)

**Testing checkpoint**: Admin sees accurate totals. Chart data correct. Report PDF downloads.

---

## PHASE 11: Security Hardening & Testing (Week 14)

**Goal**: Secure, tested, production-ready code

**Deliverables**:
- [ ] Write pytest unit tests for all service functions
- [ ] Write integration tests for all API endpoints
- [ ] Write security tests (auth bypass, SQL injection, file upload)
- [ ] Security headers added
- [ ] Rate limiting on login and AI endpoints
- [ ] File upload validation hardened
- [ ] Input validation review
- [ ] Code review against CODING_STANDARDS.md
- [ ] 80% test coverage achieved

---

## PHASE 12: Deployment (Week 15)

**Goal**: Live on Render

**Deliverables**:
- [ ] MySQL database provisioned (PlanetScale/Railway)
- [ ] Render web service configured
- [ ] All environment variables set in Render dashboard
- [ ] gunicorn WSGI server configured
- [ ] Database migrations run on Render
- [ ] Health check endpoint `/health`
- [ ] Final documentation review and sync
- [ ] Demo walkthrough prepared
- [ ] CHANGELOG updated

---

## Phase Dependencies

```
Phase 1 (Foundation)
  └─ Phase 2 (Events)
       └─ Phase 3 (Registration + Tickets)
            └─ Phase 4 (QR Attendance)
                 └─ Phase 5 (Certificates + Feedback)
                      └─ Phase 6 (Social Feed)
                           ├─ Phase 7 (Notifications + Gamification)
                           ├─ Phase 8 (AI GenAI)  [needs Phase 2+5]
                           └─ Phase 9 (AI ML)     [needs Phase 2+3+4]
                                └─ Phase 10 (Analytics)
                                     └─ Phase 11 (Testing)
                                          └─ Phase 12 (Deployment)
```
