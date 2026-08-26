# UI/UX Guidelines -- ITSA Platform

## Design Philosophy

Professional, modern, college-tech aesthetic. Clean and functional over decorative.

## Color Palette

| Name | Hex | Usage |
|---|---|---|
| ITSA Blue (Primary) | #1a73e8 | Buttons, links, headers |
| Success Green | #34a853 | Success states, attendance |
| ITSA Gold (Accent) | #fbbc04 | Leaderboard, badges, highlights |
| Danger Red | #ea4335 | Errors, cancel actions |
| Dark | #202124 | Primary text |
| Light | #f8f9fa | Page backgrounds |
| White | #ffffff | Card backgrounds |

## Typography

- Primary font: Inter (Google Fonts)
- Headings: Inter 600-700
- Body: Inter 400
- Code: JetBrains Mono

## Bootstrap 5 Components Used

Navbar, Cards, Tables, Modals, Toasts, Badges, Progress bars, Pagination, Forms, Alerts, Dropdowns, Offcanvas sidebar

## Pages List

PUBLIC: home, events, event_detail, login, register, verify_certificate

STUDENT: dashboard, feed, profile, my_events, tickets, attendance, certificates, notifications, saved_posts, leaderboard, chatbot

COORDINATOR: dashboard, assigned_events, event_manage, registrations, qr_scanner, attendance, gallery, feedback, reports

ADMIN: dashboard, users, coordinators, events, registrations, attendance, certificates, moderation, reports, analytics, settings

## State Handling

Every UI section must handle 4 states:
1. Loading state -- spinner or skeleton
2. Empty state -- illustration + helpful message + call-to-action
3. Error state -- alert with retry option
4. Success state -- toast notification

## Confirmation Dialogs

Required for destructive actions:
- Delete post or comment
- Cancel registration
- Suspend user
- Revoke certificate
- Remove gallery item

## Social Feed UI

Card-based posts. Avatar + name + timestamp header. Content area. Media gallery (up to 5 images). Reaction bar with counts. Collapsible comment section.

## QR Scanner UI

Camera viewfinder centered on page. Green overlay on successful scan. Red overlay on error. Sound feedback optional. Manual text input fallback always visible.

## Mobile Requirements

- Touch-friendly tap targets: minimum 44x44px
- Collapsible sidebar on mobile (offcanvas)
- Horizontal scroll prevention
- QR scanner optimized for mobile camera
- Tables scroll horizontally on small screens

## Accessibility Basics

- Alt text on all images
- ARIA labels on icon-only buttons
- Keyboard navigation for modals
- Color contrast ratio minimum 4.5:1 for normal text
- Form labels always present (not just placeholder)
