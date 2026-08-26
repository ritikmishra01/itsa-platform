# API Error Codes — ITSA Platform

> Standard error response format:
> ```json
> { "success": false, "error": { "code": "ERROR_CODE", "message": "Human readable message" } }
> ```

---

## Authentication Errors (AUTH_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| AUTH_VALIDATION_ERROR | 400 | Validation failed | One or more registration fields are invalid |
| AUTH_EMAIL_EXISTS | 409 | Email already registered | The email is already in use |
| AUTH_STUDENT_ID_EXISTS | 409 | Student ID already registered | Roll number is already registered |
| AUTH_INVALID_CREDENTIALS | 401 | Invalid email or password | Login credentials are incorrect |
| AUTH_ACCOUNT_SUSPENDED | 403 | Account suspended | Account has been suspended by admin |
| AUTH_ACCOUNT_INACTIVE | 403 | Account inactive | Account has been deactivated |
| AUTH_NOT_AUTHENTICATED | 401 | Authentication required | Request requires login |
| AUTH_INSUFFICIENT_ROLE | 403 | Insufficient permissions | Role does not have access to this resource |
| AUTH_WRONG_PASSWORD | 400 | Current password is incorrect | Wrong old password during change |
| AUTH_PASSWORD_WEAK | 400 | Password does not meet requirements | New password fails complexity rules |
| AUTH_PASSWORD_MISMATCH | 400 | Passwords do not match | new_password != confirm_password |
| AUTH_SESSION_EXPIRED | 401 | Session expired | Login session has expired |

---

## Event Errors (EVENT_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| EVENT_NOT_FOUND | 404 | Event not found | The event ID does not exist |
| EVENT_VALIDATION_ERROR | 400 | Event data invalid | Required fields missing or invalid |
| EVENT_INVALID_DATES | 422 | Invalid event dates | end_datetime before start, or deadline after start |
| EVENT_ALREADY_PUBLISHED | 409 | Event is already published | Status already PUBLISHED |
| EVENT_MISSING_COORDINATOR | 422 | No coordinator assigned | Cannot open registration without coordinator |
| EVENT_CANNOT_EDIT_STATUS | 422 | Cannot edit in current status | Edit not allowed at this lifecycle stage |
| EVENT_NOT_ASSIGNED | 403 | Not assigned to this event | Coordinator not assigned to this event |
| EVENT_ALREADY_CANCELLED | 409 | Event already cancelled | Cannot cancel a cancelled event |

---

## Registration Errors (REG_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| REG_ALREADY_REGISTERED | 409 | Already registered for this event | Duplicate registration attempt |
| REG_EVENT_FULL | 422 | Event is full | max_participants reached |
| REG_DEADLINE_PASSED | 422 | Registration deadline has passed | After registration_deadline |
| REG_EVENT_NOT_OPEN | 422 | Event registration is not open | Status is not REGISTRATION_OPEN |
| REG_NOT_FOUND | 404 | Registration not found | Registration ID does not exist |
| REG_CANCELLATION_DEADLINE_PASSED | 422 | Cancellation no longer allowed | After event deadline |
| REG_NOT_OWNER | 403 | Cannot access this registration | Registration belongs to another user |
| REG_ALREADY_CANCELLED | 409 | Registration already cancelled | Duplicate cancellation |

---

## Attendance Errors (ATT_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| ATT_TICKET_NOT_FOUND | 404 | Ticket not found | ticket_code does not exist in database |
| ATT_WRONG_EVENT | 422 | Ticket is for a different event | Ticket does not belong to the scanned event |
| ATT_REGISTRATION_CANCELLED | 422 | Registration has been cancelled | Student cancelled their registration |
| ATT_TICKET_INVALID | 422 | Ticket has been invalidated | is_valid = FALSE |
| ATT_ALREADY_ATTENDED | 409 | Student already checked in | Duplicate attendance scan |
| ATT_EVENT_NOT_ACTIVE | 422 | Event is not active for attendance | Event not ONGOING or REGISTRATION_CLOSED |
| ATT_COORDINATOR_NOT_ASSIGNED | 403 | Not authorized for this event | Coordinator not assigned to this event |
| ATT_NOT_FOUND | 404 | Attendance record not found | For override operations |

---

## Social Errors (SOCIAL_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| SOCIAL_POST_NOT_FOUND | 404 | Post not found | Post ID does not exist |
| SOCIAL_NOT_OWNER | 403 | Cannot modify this post | Post belongs to another user |
| SOCIAL_COMMENT_NOT_FOUND | 404 | Comment not found | Comment ID does not exist |
| SOCIAL_ALREADY_REACTED | 409 | Already reacted (auto-updated) | Handled by updating existing reaction |
| SOCIAL_ALREADY_SAVED | 409 | Post already saved | Duplicate save attempt |
| SOCIAL_CONTENT_TOO_LONG | 400 | Content exceeds maximum length | Exceeds character limits |
| SOCIAL_TOO_MANY_IMAGES | 400 | Maximum 5 images per post | More than 5 images uploaded |
| SOCIAL_REPORT_EXISTS | 409 | Already reported this content | Duplicate report |

---

## Certificate Errors (CERT_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| CERT_NOT_FOUND | 404 | Certificate not found | Certificate code or ID invalid |
| CERT_REVOKED | 410 | Certificate has been revoked | is_valid = FALSE |
| CERT_NOT_OWNER | 403 | Cannot access this certificate | Belongs to another user |
| CERT_NOT_GENERATED | 422 | Certificate not yet generated | Attendance exists but PDF not yet created |

---

## Feedback Errors (FEED_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| FEED_ALREADY_SUBMITTED | 409 | Feedback already submitted | One feedback per event per student |
| FEED_NOT_ATTENDED | 422 | Must attend event to give feedback | No PRESENT attendance found |
| FEED_WINDOW_CLOSED | 422 | Feedback window has closed | Submitted after allowed window |
| FEED_EVENT_NOT_FOUND | 404 | Event not found | Invalid event_id |

---

## AI Errors (AI_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| AI_RATE_LIMIT | 429 | Too many AI requests | Chatbot rate limit exceeded |
| AI_SERVICE_UNAVAILABLE | 503 | AI service temporarily unavailable | Gemini API error |
| AI_CONTENT_BLOCKED | 422 | Content blocked by safety filters | Gemini safety filter triggered |
| AI_INVALID_INPUT | 400 | Invalid input for AI processing | Input fails sanitization |
| AI_MODEL_NOT_READY | 503 | ML model not ready | Model file missing or not trained |
| AI_NO_DATA | 422 | Insufficient data for analysis | Not enough data for ML prediction |

---

## File Errors (FILE_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| FILE_TYPE_NOT_ALLOWED | 400 | File type not allowed | Extension not in whitelist |
| FILE_TOO_LARGE | 400 | File size exceeds limit | Exceeds max file size |
| FILE_NOT_FOUND | 404 | File not found | Requested file does not exist |
| FILE_UPLOAD_FAILED | 500 | File upload failed | Server-side save error |
| FILE_INVALID | 400 | Invalid file | MIME type does not match extension |

---

## System Errors (SYS_)

| Code | HTTP | Message | Description |
|---|---|---|---|
| SYS_INTERNAL_ERROR | 500 | An unexpected error occurred | Unhandled server exception |
| SYS_DATABASE_ERROR | 500 | Database error | Database operation failed |
| SYS_NOT_FOUND | 404 | Resource not found | Generic 404 |
| SYS_METHOD_NOT_ALLOWED | 405 | Method not allowed | Wrong HTTP method |
| SYS_RATE_LIMIT | 429 | Too many requests | General rate limit exceeded |
