# Validation Rules — ITSA Platform

## User Registration

| Field | Type | Required | Rules | Error Code |
|---|---|---|---|---|
| email | string | Yes | Valid email format, max 255 chars, unique | AUTH_EMAIL_EXISTS |
| password | string | Yes | Min 8 chars, 1 upper, 1 lower, 1 digit | AUTH_PASSWORD_WEAK |
| full_name | string | Yes | 2-100 chars, letters and spaces only | AUTH_VALIDATION_ERROR |
| student_id | string | Yes | 5-20 chars, alphanumeric | AUTH_STUDENT_ID_EXISTS |
| department | string | Yes | Must be from predefined list | AUTH_VALIDATION_ERROR |
| year_of_study | integer | Yes | Must be 1, 2, 3, or 4 | AUTH_VALIDATION_ERROR |

## Event Creation

| Field | Type | Required | Rules |
|---|---|---|---|
| title | string | Yes | 5-200 chars |
| description | string | Yes | 50-5000 chars |
| category_id | integer | Yes | Must exist in event_categories |
| start_datetime | datetime | Yes | Must be future date |
| end_datetime | datetime | Yes | Must be after start_datetime |
| registration_deadline | datetime | Yes | Must be before start_datetime |
| max_participants | integer | No | If set: positive integer >= 10 |
| poster_image | file | No | Max 5MB, JPEG/PNG/WEBP only |

## Post Creation

| Field | Rules |
|---|---|
| content | Required if no media, max 5000 chars |
| images | Max 5 files, each max 10MB, JPEG/PNG/WEBP |
| video | Max 1 file, max 100MB, MP4/MOV/AVI |
| hashtags | Auto-extracted, max 20 per post, each max 50 chars |
| mentions | Auto-extracted, max 10 per post |

## Comment

| Field | Rules |
|---|---|
| content | Required, 1-2000 chars |

## Reply

| Field | Rules |
|---|---|
| content | Required, 1-1000 chars |

## Feedback

| Field | Rules |
|---|---|
| rating | Required, integer 1-5 |
| content | Optional, max 2000 chars |

## AI Chat Input

| Field | Rules |
|---|---|
| message | Required, 1-1000 chars, no HTML/script tags |

## QR Scan Input

| Field | Rules |
|---|---|
| ticket_code | Required, format: ITSA-TKT-{uuid} |
| event_id | Required, integer, coordinator must be assigned |

## Profile Update

| Field | Rules |
|---|---|
| full_name | Optional, 2-100 chars |
| bio | Optional, max 500 chars |
| phone | Optional, valid phone format (+XX XXXXXXXXXX) |
| github_url | Optional, must start with https://github.com/ |
| linkedin_url | Optional, must start with https://linkedin.com/ |
| year_of_study | Optional, 1-4 |
| interests | Optional, max 500 chars |
