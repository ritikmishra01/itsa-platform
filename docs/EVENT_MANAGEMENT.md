# Event Management — ITSA Platform

## Event Lifecycle

`
DRAFT → PUBLISHED → REGISTRATION_OPEN → REGISTRATION_CLOSED → ONGOING → COMPLETED
                                                                        ↓
                                                                   CANCELLED (any stage)
`

| Status | Description | Who Can Set |
|---|---|---|
| DRAFT | Created, not visible publicly | Admin/Coordinator |
| PUBLISHED | Visible publicly, registration not open | Admin |
| REGISTRATION_OPEN | Students can register | Admin |
| REGISTRATION_CLOSED | Registration ended, event upcoming | Admin/System |
| ONGOING | Event in progress | Admin |
| COMPLETED | Event finished | Admin |
| CANCELLED | Event cancelled | Admin only |

## Event Creation Rules

Required fields: title, description, category_id, start_datetime, end_datetime, registration_deadline
Optional: venue_id, poster_image, max_participants, tags, registration_fee

Validation:
- end_datetime must be after start_datetime
- registration_deadline must be before start_datetime
- start_datetime must be in the future (for new events)

## Coordinator Assignment

- Admin assigns coordinators via POST /api/v1/events/{id}/coordinators
- At least 1 coordinator required before moving to REGISTRATION_OPEN
- Multiple coordinators supported (Lead, Support, Registration, Volunteer Manager roles)
- Coordinators can only access events they are assigned to

## Editing Rules

| Status | Admin Can Edit | Coordinator Can Edit |
|---|---|---|
| DRAFT | All fields | All fields (assigned) |
| PUBLISHED | All fields | Description, poster |
| REGISTRATION_OPEN | Non-structural fields | Description, poster |
| COMPLETED | Notes only | None |
| CANCELLED | None | None |

## Event Cancellation

When cancelled:
1. All tickets invalidated (is_valid = FALSE)
2. All registrations marked CANCELLED
3. Notification sent to all registrants
4. Points deducted from registrants (-3 per registration)
5. Gallery and feedback preserved for records

## Event Archive

Completed events accessible via Past Events page.
Searchable by title, category, year.
Gallery, feedback stats, and attendance records preserved permanently.

## Categories

Technical, Workshop, Seminar, Cultural, Sports, Competition, Community Service, Other
