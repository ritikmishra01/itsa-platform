# Notification System -- ITSA Platform

## Two Channels
1. In-App: Stored in notifications table, shown in navbar bell
2. Email: Sent via smtplib SMTP, HTML templates

## Notification Types and Triggers

| Type | Trigger | Recipients | In-App | Email |
|---|---|---|---|---|
| EVENT_REGISTRATION | Student registers for event | Student | Yes | Yes |
| EVENT_REMINDER | 24 hours before event start | All registrants | Yes | Yes |
| EVENT_CHANGE | Event details edited | All registrants | Yes | Yes |
| EVENT_CANCELLED | Event cancelled | All registrants | Yes | Yes |
| CERTIFICATE_READY | Attendance marked PRESENT | Student | Yes | Yes |
| POST_REACTION | Someone reacts to your post | Post author | Yes | No |
| POST_COMMENT | Someone comments on your post | Post author | Yes | No |
| MENTION | Someone mentions you in post/comment | Mentioned user | Yes | No |
| ANNOUNCEMENT | Admin broadcast | All students | Yes | Yes |
| SYSTEM | Platform system events | Specific user | Yes | No |

## In-App Notification UI

- Bell icon in navbar with unread count badge
- Dropdown preview of last 5 notifications
- Full notifications page at /student/notifications
- Mark single notification as read
- Mark all notifications as read
- Delete individual notifications

## Email Notification

- HTML email templates in app/templates/emails/
- Sent via Python smtplib in a background thread
- SMTP failures logged but do NOT cause main operation to fail
- Configuration via SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD in .env

## send_notification Function Signature

def send_notification(user_id, notif_type, title, message, related_event_id=None, related_post_id=None, related_user_id=None):
    Creates Notification DB record and optionally sends email.

## Bulk Notifications

For event cancellations and admin announcements:
def send_bulk_notification(user_ids, notif_type, title, message):
    Creates one notification record per user in a batch insert.

## Error Handling

Email sending failure is caught and logged as WARNING.
The main operation (registration, attendance) continues even if email fails.
Failed email addresses are logged for manual retry if needed.
