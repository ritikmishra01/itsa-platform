# ITSA Platform: Notification & Broadcast Architecture

## 1. Overview
The Notification module delivers time-sensitive event alerts, administrative broadcasts, and social engagement updates to students, coordinators, and administrators. The system supports multi-channel delivery:
1. **In-App Real-Time Notifications**: Stored in the database and rendered via dynamic navbar badges and dedicated notification centers (`/student/notifications`, `/coordinator/notifications`, `/admin/notifications`).
2. **Transactional SMTP Email**: Background email dispatch using Python's `smtplib` for event registration confirmations, certificate delivery, and emergency broadcasts.

---

## 2. Notification Triggers & Matrix

| Notification Type | Trigger Event | Target Audience | In-App | Email Delivery |
| :--- | :--- | :--- | :---: | :---: |
| `EVENT_REGISTRATION` | Student confirms event registration | Student | Yes | Yes (Ticket details) |
| `EVENT_REMINDER` | Automated reminder before event start | Registered Students | Yes | Yes |
| `EVENT_CHANGE` | Schedule, venue, or details updated | Registered Students | Yes | Yes |
| `EVENT_CANCELLED` | Coordinator/Admin cancels event | Registered Students | Yes | Yes |
| `CERTIFICATE_READY`| Attendance marked `PRESENT` via QR scan | Attended Student | Yes | Yes (Download link) |
| `POST_REACTION` | Reaction added to a post | Post Author | Yes | No |
| `POST_COMMENT` | Comment added to a post | Post Author | Yes | No |
| `MENTION` | User tagged with `@username` | Mentioned Member | Yes | No |
| `ANNOUNCEMENT` | Administrative broadcast dispatch | Target Audience | Yes | Optional |
| `SYSTEM` | Account status or suspension change | Target User | Yes | No |

---

## 3. Targeted Administrative Broadcasts (`/admin/notifications`)

Administrators can dispatch targeted announcements through the Admin Control Center:
- **`ALL_STUDENTS`**: Delivers notifications to all active student accounts.
- **`ALL_COORDINATORS`**: Delivers notifications to all faculty and student event coordinators.
- **`ALL_USERS`**: Global broadcast across the entire platform.
- **`DEPT` (Department Filter)**: Filters recipients by academic department (e.g., Information Technology, Computer Science, AI & DS).
- **`YEAR` (Year of Study Filter)**: Filters by academic cohort (FE / SE / TE / BE).
- **`EVENT` (Event Attendees)**: Targets all confirmed registrants of a selected event.

Every broadcast transaction creates immutable audit trail entries in `audit_logs` and atomic records in `notifications`.

---

## 4. In-App User Experience

### 4.1 Real-Time Navbar Counter
The global context processor (`inject_global_vars` in `app/__init__.py`) dynamically calculates unread notifications on every authenticated page load:
```python
unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
```
The navbar bell displays a bold badge with the exact unread count.

### 4.2 Notification Centers
- **View Notifications**: Chronological feed displaying category icons, titles, messages, and timestamps.
- **Mark Single as Read**: Asynchronous `PUT /api/v1/notifications/<id>/read`.
- **Mark All as Read**: Bulk update `PUT /api/v1/notifications/read-all`.
- **Delete Alert**: Individual deletion `DELETE /api/v1/notifications/<id>`.

---

## 5. Backend Architecture & Resiliency

- **Model**: `Notification` (`app/models/notification.py`)
  - `user_id`: Foreign key to `users.id` (Recipient)
  - `type`: Notification enum category
  - `title` & `message`: Text payload
  - `is_read`: Boolean flag (default `False`)
  - `related_event_id`, `related_post_id`, `related_user_id`: Optional foreign keys for direct deep-linking
- **Service Layer**: `app/services/notification_service.py` provides non-blocking operations. SMTP delivery failures are caught, logged as warnings, and never interrupt database transactions or user operations.