# Frontend Structure -- ITSA Platform

## Template Organization

Jinja2 templates with Bootstrap 5. All pages extend base.html.

## base.html

Provides: HTML doctype, Bootstrap CSS, Inter font, site navbar, sidebar (for auth pages), flash messages area, toast container, Bootstrap JS, Chart.js, html5-qrcode (coordinator pages only), custom JS.

## Public Pages (no auth required)

| Template | URL | Description |
|---|---|---|
| public/home.html | / | Landing page with upcoming events, about ITSA |
| public/events.html | /events | Browse all events with search and filter |
| public/event_detail.html | /events/{id} | Full event details + register button |
| auth/login.html | /login | Login form |
| auth/register.html | /register | Student registration form |
| public/verify_cert.html | /certificates/verify/{code} | Public certificate check |

## Student Pages

| Template | URL | Description |
|---|---|---|
| student/dashboard.html | /student/dashboard | Stat cards, upcoming events, points, recommendations |
| student/feed.html | /student/feed | Social community feed |
| student/profile.html | /student/profile | View/edit own profile |
| student/my_events.html | /student/my-events | Registered events (upcoming, past, cancelled) |
| student/tickets.html | /student/tickets | All QR tickets |
| student/ticket_detail.html | /student/tickets/{id} | Single ticket with QR display |
| student/attendance.html | /student/attendance | Attendance history |
| student/certificates.html | /student/certificates | My certificates list |
| student/notifications.html | /student/notifications | All notifications |
| student/saved_posts.html | /student/saved-posts | Saved posts collection |
| student/leaderboard.html | /student/leaderboard | ITSA Points leaderboard |
| student/chatbot.html | /student/chatbot | AI chatbot interface |

## Coordinator Pages

| Template | URL | Description |
|---|---|---|
| coordinator/dashboard.html | /coordinator/dashboard | Assigned events overview |
| coordinator/scanner.html | /coordinator/events/{id}/scan | QR scanner page |
| coordinator/attendance.html | /coordinator/events/{id}/attendance | Live attendance list |
| coordinator/registrations.html | /coordinator/events/{id}/registrations | Registrant list |
| coordinator/gallery.html | /coordinator/events/{id}/gallery | Upload gallery |
| coordinator/feedback.html | /coordinator/events/{id}/feedback | View feedback |
| coordinator/reports.html | /coordinator/events/{id}/reports | Event reports |

## Admin Pages

| Template | URL | Description |
|---|---|---|
| admin/dashboard.html | /admin/dashboard | System overview with Chart.js charts |
| admin/users.html | /admin/users | User management table |
| admin/coordinators.html | /admin/coordinators | Coordinator list + create |
| admin/events.html | /admin/events | All events management |
| admin/registrations.html | /admin/registrations | All registrations |
| admin/attendance.html | /admin/attendance | System-wide attendance |
| admin/certificates.html | /admin/certificates | All certificates |
| admin/moderation.html | /admin/moderation | Reports queue |
| admin/analytics.html | /admin/analytics | Charts and stats |
| admin/settings.html | /admin/settings | System settings |

## JavaScript Modules

| File | Purpose |
|---|---|
| static/js/main.js | API helpers, toast notifications, CSRF token |
| static/js/feed.js | Post creation, reactions, comments, infinite scroll |
| static/js/scanner.js | html5-qrcode wrapper with success/error UI |
| static/js/charts.js | Chart.js initialization for analytics pages |
| static/js/post_form.js | Post creation form with media preview |

## AJAX Pattern

All API calls use fetch() with JSON Content-Type.
Response handled: if success show toast, else show error.
Loading states shown during API calls.

## QR Scanner Integration

html5-qrcode library from CDN.
Camera permission requested on page load.
Fallback: manual ticket code text input.
Success: green overlay + student name + auto-resume.
Error: red overlay + error message + auto-resume.
