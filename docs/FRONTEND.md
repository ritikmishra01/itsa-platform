# ITSA Platform: Frontend Architecture & Documentation

## 1. Overview
The frontend of the **ITSA AI-Powered Event Management & Student Engagement Platform** is designed as a responsive, accessible, and modern college community portal. It utilizes server-rendered HTML5 templates powered by **Jinja2** inside Flask, structured with **Bootstrap 5.3**, styled with custom design tokens, and augmented with lightweight, dependency-free vanilla JavaScript for interactive client-side operations (asynchronous API calls, modals, toasts, and real-time QR scanning).

---

## 2. Frontend Technologies Actually Used

| Technology | Version / Source | Purpose in Platform |
| :--- | :--- | :--- |
| **HTML5** | Semantic Standard | Base document structure, forms, data attributes, and accessible layouts. |
| **CSS3** | Custom (`static/css/main.css`) | Custom color system, CSS variables, card elevation, typography, and responsive tweaks. |
| **JavaScript** | ES6+ (`static/js/main.js`) | Asynchronous fetch requests (`apiCall`), dynamic DOM updates, modals, and toasts. |
| **Bootstrap** | `5.3.3` (CDN) | Grid system, responsive utility classes, flexbox layouts, buttons, dropdowns, and navbars. |
| **Bootstrap Icons** | `1.11.3` (CDN) | Vector icon set for UI actions, event categories, status indicators, and role badges. |
| **Chart.js** | `4.4.1` (CDN) | Interactive analytics visualizations on Admin and Coordinator dashboards. |
| **html5-qrcode** | `2.3.8` (CDN) | Client-side camera-based QR code scanning for fast coordinator attendance verification. |
| **Inter & JetBrains Mono**| Google Fonts | Professional sans-serif typography for UI and monospace font for IDs/tickets. |

---

## 3. Frontend Structure & Organization

```text
app/
├── static/
│   ├── css/
│   │   └── main.css             # Unified CSS styles, theme variables, and card layouts
│   ├── js/
│   │   └── main.js              # apiCall helper, toast notifications, dynamic components
│   └── img/
│       └── placeholder.svg      # Fallback graphic for posters and profile images
└── templates/
    ├── base.html                # Main master layout (Student, Coordinator & Public views)
    ├── admin/                   # Dedicated Admin Control Center layout and modules
    │   ├── base_admin.html      # Sidebar + topbar layout for administrator views
    │   ├── dashboard.html       # Metrics overview, quick actions, event statistics
    │   ├── users.html           # User management, role filtering, suspension modal
    │   ├── coordinators.html    # Faculty coordinator records and assignment overview
    │   ├── events.html          # Event publishing, drafts, cancellations, and creation
    │   ├── registrations.html   # Global student registration roster and status controls
    │   ├── attendance.html      # College-wide attendance logs and manual overrides
    │   ├── certificates.html    # Certificate issuance tracking and verification codes
    │   ├── community.html       # Social feed moderation, post deletion, report queues
    │   ├── reports.html         # User report resolution center for flagged content
    │   ├── notifications.html   # System-wide announcement dispatch and broadcast logs
    │   ├── analytics.html       # Visual charts (attendance, departments, monthly trends)
    │   ├── settings.html        # Platform configuration, points rules, window settings
    │   ├── gallery.html         # Media gallery upload, featuring, and asset management
    │   ├── gamification.html    # ITSA points transactions and manual point adjustments
    │   ├── ai_center.html       # AI prompt testing, description generation, moderation
    │   ├── audit_logs.html      # Security audit trails and administrative action logs
    │   └── search.html          # Unified search across users, events, and registrations
    ├── auth/                    # Authentication Views
    │   ├── login.html           # Unified login form with remember-me checkbox
    │   └── register.html        # Student onboarding form with roll number & department
    ├── public/                  # Publicly Accessible Views
    │   ├── events.html          # Filterable event directory with category & search filters
    │   ├── event_detail.html    # Comprehensive event overview, schedule & registration CTA
    │   └── verify_cert.html     # Public certificate verification and authenticity badge
    ├── student/                 # Authenticated Student Views
    │   ├── dashboard.html       # Student home: metrics, registrations, AI recommendations
    │   ├── feed.html            # Social feed: posts, reactions, comments, media uploads
    │   ├── profile.html         # Profile management: bio, GitHub, LinkedIn, contact
    │   ├── tickets.html         # Issued event tickets with interactive QR display
    │   ├── attendance.html      # Student personal attendance log and verification status
    │   ├── certificates.html    # Issued certificates with instant PDF download links
    │   ├── notifications.html   # Student personal notification and announcement center
    │   ├── leaderboard.html     # Real-time ITSA points ranking and engagement tiers
    │   └── chatbot.html         # Interactive AI assistant powered by Gemini API
    ├── coordinator/             # Authenticated Coordinator Views
    │   ├── dashboard.html       # Coordinator home: assigned events, quick scan shortcuts
    │   ├── event_manage.html    # Specific event roster, attendance review, attendee export
    │   ├── scanner.html         # Live QR camera scanner and manual code entry form
    │   ├── gallery.html         # Event photo upload and media gallery curator
    │   └── feedback.html        # Event feedback review with AI sentiment breakdown
    └── errors/                  # Custom HTTP Error Handlers
        ├── 400.html             # Bad Request
        ├── 401.html             # Unauthorized / Authentication Required
        ├── 403.html             # Access Forbidden / Role Restricted
        ├── 404.html             # Page Not Found
        ├── 429.html             # Rate Limit Exceeded
        └── 500.html             # Internal Server Error
```

---

## 4. Key Frontend Implementation Details

### 4.1 Master Layout Hierarchy
1. **`base.html`**: The default layout wrapper. It provides the top navigation bar with dynamic navigation links based on user roles (`current_user.is_authenticated`, `current_user.is_student`, `current_user.is_coordinator`, `current_user.is_admin`), the active notification badge counter, user profile dropdown with role badge, and global toast message containers.
2. **`admin/base_admin.html`**: Extends `base.html` but replaces the standard content area with a responsive two-column layout featuring an admin sidebar (`<div class="col-lg-3 col-xl-2 admin-sidebar">`) that provides direct navigation to all 17 administrative modules.

### 4.2 Asynchronous Client API Integration (`static/js/main.js`)
All form submissions and client-side actions use a unified asynchronous wrapper:
```javascript
async function apiCall(endpoint, method = 'GET', data = null) { ... }
```
- Automatically handles JSON payload formatting and headers.
- Automatically captures API error envelopes (`{"success": false, "error": {"message": "..."}}`).
- Emits toast notifications using Bootstrap's Toast API (`showToast(message, type)`).
- Supports auto-dismissing alerts and UI status indicators.

### 4.3 QR Code Attendance Scanner (`coordinator/scanner.html`)
The QR attendance module employs `html5-qrcode` to interface directly with the device's video input. Upon scanning a valid student ticket QR code (`ITSA-TKT-...`), the client sends a `POST /api/v1/attendance/scan` request and displays immediate audio/visual validation status (ticket owner, event match, duplicate warning, or verified entry).