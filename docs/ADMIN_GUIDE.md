# ITSA Platform: Administrator Operational Guide

## 1. Overview
The **Admin Control Center** provides comprehensive operational, moderation, and analytical supervision over the entire ITSA platform. The `ADMIN` role possesses superuser capabilities with unconstrained access to user directories, event lifecycles, attendance logs, certificates, community moderation, gamification points, and audit logs.

---

## 2. Navigating the Admin Control Center (`/admin/dashboard`)

The administrator interface is structured into 17 specialized modules accessible from the persistent sidebar (`app/templates/admin/base_admin.html`):

1. **Dashboard (`/admin/dashboard`)**: High-level platform statistics (total students, active events, present attendances, certificates issued, pending moderation reports).
2. **User Management (`/admin/users`)**: 
   - Search and filter all registered students, coordinators, and administrators.
   - View student roll numbers, departments, years of study, and contact info.
   - **Account Suspension**: Suspend accounts for policy violations with reason logging. Suspended users are immediately evicted from active sessions.
   - **Account Reactivation**: Unsuspend previously suspended accounts.
3. **Coordinators (`/admin/coordinators`)**:
   - Manage faculty and student event coordinators.
   - View assigned events, designation, department, and employee ID.
   - Create new coordinator accounts with automatic profile generation.
4. **Events (`/admin/events`)**:
   - Create, edit, and schedule official ITSA events.
   - Transition event status: `DRAFT` &rarr; `PUBLISHED` &rarr; `REGISTRATION_OPEN` &rarr; `REGISTRATION_CLOSED` &rarr; `ONGOING` &rarr; `COMPLETED` / `CANCELLED`.
   - Assign Lead and Support coordinators to events.
5. **Registrations (`/admin/registrations`)**:
   - College-wide registration rosters across all events.
   - Filter by event, status (`CONFIRMED`, `CANCELLED`, `WAITLISTED`), and date.
6. **Attendance (`/admin/attendance`)**:
   - Master attendance registry with timestamps and coordinator scanner details.
   - **Manual Override**: Mark attendance manually for students who encountered physical ticket issues.
7. **Certificates (`/admin/certificates`)**:
   - Monitor issued certificates, verification codes, and issuance timestamps.
   - Direct PDF preview and revocation controls.
8. **Community (`/admin/community`)**:
   - Global moderation view of all student posts and comments.
   - Immediate one-click deletion of inappropriate content.
9. **Reports Queue (`/admin/reports`)**:
   - User-flagged content triage center.
   - Inspect reported text, reporter notes, and AI moderation advisory.
   - Resolve or dismiss reports with automated audit logging.
10. **Broadcasts & Notifications (`/admin/notifications`)**:
    - Multi-target announcement broadcaster (`ALL_STUDENTS`, `ALL_COORDINATORS`, `ALL_USERS`, `DEPT`, `YEAR`, `EVENT`).
    - View dispatch history, recipient counts, and delivery timestamps.
11. **Analytics (`/admin/analytics`)**:
    - Chart.js interactive charts: department-wise participation, attendance rates, registration velocity, and monthly activity trends.
12. **Settings (`/admin/settings`)**:
    - Platform configuration, points rewards, and feedback submission time windows.
13. **Media Gallery (`/admin/gallery`)**:
    - Upload high-resolution keynote and event photographs.
    - Set featured status for homepage carousel showcase.
14. **Gamification & Points (`/admin/gamification`)**:
    - View student ITSA Points balances and full transaction history.
    - **Manual Points Adjustment**: Award bonus points for external competitions or deduct penalty points.
15. **AI Innovation Center (`/admin/ai-center`)**:
    - Direct interface to Google Gemini API: generate event descriptions, compose announcements, and test moderation prompts.
16. **Audit Logs (`/admin/audit-logs`)**:
    - Immutable security audit trails recording administrator ID, action, target entity, IP address, and timestamp.
17. **Global Search (`/admin/search`)**:
    - Search across users, events, registrations, and certificates from a single search query.

---

## 3. Administrative Workflows

### 3.1 Creating and Launching an Event
1. Navigate to **Events** &rarr; click **Create New Event**.
2. Fill in Event Title, Category, Venue, Start/End DateTime, Registration Deadline, and Capacity.
3. Select assigned Coordinator(s).
4. Save as `DRAFT` or publish immediately as `REGISTRATION_OPEN`.

### 3.2 Resolving Flagged Community Content
1. Navigate to **Reports Queue** (`/admin/reports`).
2. Review the reported item and reason (`SPAM`, `INAPPROPRIATE`, `HARASSMENT`).
3. Click **Resolve (Remove Content)** to hide the item from the student feed, or **Dismiss** if no violation occurred.