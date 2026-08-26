# User Roles — ITSA Platform

> There are exactly THREE roles: **STUDENT**, **COORDINATOR**, **ADMIN**.
> There is NO Faculty role.

---

## Role Overview

| Role | Description | Account Creation |
|---|---|---|
| **STUDENT** | Any enrolled college student | Self-registration via /register |
| **COORDINATOR** | Authorized ITSA member managing events | Created by Admin |
| **ADMIN** | ITSA platform administrator | Pre-seeded or created by another Admin |

---

## STUDENT Role

### What Students CAN Do

**Account & Profile**
- Register a new account with student ID, department, year
- Login and logout
- View and edit their own profile
- Upload a profile photo
- Change their password
- View other students public profiles

**Events**
- Browse all PUBLISHED and REGISTRATION_OPEN events
- Search and filter events by category, date, status
- View full event details
- Register for an event (if open, not full, deadline not passed)
- Cancel their own registration (before deadline)
- View their registration history (past, upcoming, cancelled)

**Tickets & Attendance**
- View their QR ticket for each registered event
- Download their QR ticket image
- Show their QR ticket to a Coordinator for scanning
- View their attendance history

**Certificates**
- View all their earned certificates
- Download certificates as PDF

**Feedback**
- Submit feedback (rating + text) for events they attended

**Social Feed**
- Create posts (text, images, videos)
- Edit and delete their own posts
- React to any post (LIKE, LOVE, CELEBRATE, INSIGHTFUL, SUPPORT)
- Comment on posts
- Reply to comments
- Delete their own comments and replies
- Share posts to the feed
- Save posts to personal collection
- View saved posts
- Use hashtags in posts/comments
- Mention other users (@username)
- Report posts or comments for moderation
- View posts by hashtag
- Search posts

**Notifications**
- View in-app notifications
- Mark notifications as read
- Delete notifications

**Gamification**
- Earn ITSA Points for activities
- View their own points balance and history
- View the leaderboard
- View their Engagement Score

**AI**
- Use the AI chatbot (ITSA Assistant)
- Receive AI-powered event recommendations

### What Students CANNOT Do

- Create or manage events
- Scan QR tickets or mark attendance
- View other students registrations or tickets
- Access coordinator or admin dashboards
- Moderate content
- Generate reports
- Assign coordinators
- Manually award points
- Access any `/coordinator/*` or `/admin/*` routes

---

## COORDINATOR Role

### Description

A Coordinator is an authorized ITSA member who has been granted a coordinator account by Admin. Coordinators are **assigned to specific events** by Admin. They can ONLY see and manage data for their assigned events.

### What Coordinators CAN Do

**Account**
- Login and logout
- View and edit their own profile

**Events (Assigned Only)**
- View their assigned events list
- View full details of assigned events
- Upload event poster and gallery media
- Manage event updates (if authorized by Admin)
- View registrations for assigned events
- View participant list for assigned events

**Attendance**
- Open the QR scanner for their assigned event
- Scan student QR tickets using the browser-based scanner
- Manually enter ticket codes (fallback)
- View live attendance count and list
- See which students have and have not checked in
- Correct attendance manually when authorized by Admin

**Feedback & Reports**
- View event feedback for assigned events
- View event analytics for assigned events
- Generate event-specific reports

**Volunteers**
- Manage volunteer assignments for assigned events

### What Coordinators CANNOT Do

- Create events (unless specifically authorized by Admin)
- Access events they are NOT assigned to
- Scan attendance for events they are NOT assigned to
- Access admin dashboard or system settings
- Suspend users
- Moderate social feed content
- View system-wide analytics
- Create or manage coordinator accounts
- Award ITSA points manually

### CRITICAL ATTENDANCE RULE

> **The STUDENT does NOT scan their own attendance.**
>
> The flow is:
> 1. Student registers → QR ticket generated
> 2. Student arrives at event → shows QR to Coordinator
> 3. **Coordinator scans the student QR ticket**
> 4. Backend validates ticket (6-step validation)
> 5. Attendance recorded with timestamp
> 6. Student receives notification

---

## ADMIN Role

Admins have complete control over the platform with no restrictions.

### What Admins CAN Do

**User Management**
- View all users (students and coordinators)
- Create coordinator accounts
- Edit any user profile
- Suspend and unsuspend accounts
- Delete user accounts (with cascade handling)

**Event Management**
- Create, edit, publish, cancel any event
- Assign coordinators to events
- Override event status
- Delete events

**Registration & Attendance**
- View all registrations for any event
- Cancel any registration
- Manually override attendance records
- Add manual attendance entries

**Certificates**
- View all certificates
- Revoke certificates

**Social Moderation**
- View all posts and comments
- Delete any post or comment
- Review and resolve content reports
- Warn or suspend users for violations
- Use AI moderation assistance

**Announcements**
- Create system-wide announcements
- Send broadcast notifications to all students

**Gallery**
- Upload, edit, delete gallery items for any event

**Gamification**
- Manually award or deduct ITSA points with reason
- Reset leaderboard (semester reset)
- View any students points history

**Analytics & Reports**
- View system-wide analytics dashboard
- View per-event analytics
- View department and year-wise stats
- Generate PDF reports (event, monthly, department)

**System Settings**
- Manage event categories
- Manage venues
- Configure system settings
- View audit logs

---

## Role Comparison Matrix

| Action | Student | Coordinator | Admin |
|---|---|---|---|
| Register account | ✅ | ❌ (admin creates) | ❌ (admin creates) |
| Login | ✅ | ✅ | ✅ |
| Edit own profile | ✅ | ✅ | ✅ |
| Edit other profiles | ❌ | ❌ | ✅ |
| Browse events | ✅ | ✅ | ✅ |
| Register for event | ✅ | ❌ | ❌ |
| Create event | ❌ | ✅ (assigned) | ✅ |
| Edit event | ❌ | ✅ (assigned only) | ✅ |
| Cancel event | ❌ | ❌ | ✅ |
| Assign coordinator | ❌ | ❌ | ✅ |
| View registrations | Own only | Assigned event only | All |
| Scan QR attendance | ❌ | ✅ (assigned only) | ✅ |
| Override attendance | ❌ | ❌ | ✅ |
| View tickets | Own only | ❌ | ✅ |
| Download certificate | Own only | ❌ | ✅ |
| Create post | ✅ | ✅ | ✅ |
| Delete any post | ❌ | ❌ | ✅ |
| Moderate content | ❌ | ❌ | ✅ |
| View event feedback | ❌ | Assigned only | ✅ |
| View event analytics | ❌ | Assigned only | ✅ |
| View system analytics | ❌ | ❌ | ✅ |
| Award points | ❌ | ❌ | ✅ |
| Suspend users | ❌ | ❌ | ✅ |
| View audit logs | ❌ | ❌ | ✅ |

---

## Role Assignment Rules

1. Students register themselves via `/register` — role is set to STUDENT automatically
2. Coordinator accounts are created ONLY by Admin via `/admin/coordinators`
3. Admin accounts are pre-seeded in the database via an initialization script
4. Role changes must be performed by Admin in the database or admin panel
5. A user cannot change their own role
6. Role is stored in the `users.role` database column (ENUM)
7. Role is **never** trusted from client input — always read from DB session

---

## Authorization Enforcement

- Every protected route has a decorator checking the users database role
- Coordinators have an additional check: are they assigned to the requested event?
- Admin has a `@admin_required` decorator on all admin routes
- Attempting to access a forbidden route returns HTTP 403 Forbidden
- No client-side role information is trusted for authorization decisions
