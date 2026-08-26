# Notification System — ITSA Platform

## Overview

Two channels: In-App (database) and Email (SMTP).

## Notification Types and Triggers

| Type | Trigger | Recipients | In-App | Email |
|---|---|---|---|---|
| EVENT_REGISTRATION | Student registers | Student | ✅ | ✅ |
| EVENT_REMINDER | 24h before event | All registrants | ✅ | ✅ |
| EVENT_CHANGE | Event edited | All registrants | ✅ | ✅ |
| EVENT_CANCELLED | Event cancelled | All registrants | ✅ | ✅ |
| CERTIFICATE_READY | Attendance recorded | Student | ✅ | ✅ |
| POST_REACTION | Someone reacts to your post | Post author | ✅ | ❌ |
| POST_COMMENT | Someone comments on your post | Post author | ✅ | ❌ |
| MENTION | Someone mentions you | Mentioned user | ✅ | ❌ |
| ANNOUNCEMENT | Admin creates announcement | All students | ✅ | ✅ |
| SYSTEM | System events | Specific user | ✅ | ❌ |

## In-App Notifications

Bell icon in navbar shows unread count.
Notification dropdown shows last 5.
Full notification page with pagination.
Mark single as read or mark all as read.

## Email Notifications

Sent via smtplib with HTML templates.
Sent in a background thread to not block main request.
SMTP failures are logged but do not cause the main operation to fail.

## send_notification function

`python
def send_notification(user_id, notif_type, title, message,
                      related_event_id=None, related_post_id=None, related_user_id=None):
    notification = Notification(
        user_id=user_id,
        type=notif_type,
        title=title,
        message=message,
        related_event_id=related_event_id,
        related_post_id=related_post_id,
        related_user_id=related_user_id
    )
    db.session.add(notification)
    # Committed with parent transaction or separately
`
"@ | Out-File -FilePath "C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\docs\NOTIFICATION_SYSTEM.md" -Encoding utf8
Write-Host "NOTIFICATION_SYSTEM.md done"

# GAMIFICATION.md
@"
# Gamification — ITSA Platform

## ITSA Points System

### Points Table

| Activity | Points | Notes |
|---|---|---|
| Attend event | +10 | On PRESENT attendance scan |
| Register for event | +3 | On confirmed registration |
| Submit feedback | +5 | After event attendance |
| Create social post | +2 | Per post created |
| Create comment | +1 | Per comment |
| Volunteering at event | +15 | When assigned as volunteer |
| Win competition | +25 | Admin award |
| Admin manual award | Variable | Admin-specified |
| Cancel registration | -3 | Deducted on cancellation |

### Rules

- Total points never go below 0
- All transactions logged in itsa_points table
- total_points on student_profiles is denormalized (updated after each transaction)
- Admin can manually adjust points with a reason

## Leaderboard

Ranked by total_points descending.
Filters: All Students, By Department, By Year.
Updated in real-time (after each points transaction).

## Engagement Score (0-100)

`
raw = (attendance*10) + (registrations*3) + (feedbacks*5) + (posts*2) + (comments*1) + (reactions_received*0.5) + (volunteering*15)
score = min(100, round((raw / max_possible) * 100, 1))
`

Where max_possible is calculated from the current semester's activity totals.

Score displayed on student profile with a breakdown pie chart.

## Points History

GET /api/v1/points/my returns list of all transactions with:
- points (positive or negative)
- reason
- related event name (if applicable)
- timestamp
