# Test Cases -- ITSA Platform

Format: ID | Name | Type | Preconditions | Input | Expected Result
Types: Positive (P), Negative (N), Security (S)

---

## Authentication (TC-AUTH)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-AUTH-001 | Register with valid data | P | Valid email, strong password, student_id | 201 + user object |
| TC-AUTH-002 | Register with duplicate email | N | Existing email | 409 AUTH_EMAIL_EXISTS |
| TC-AUTH-003 | Register with weak password | N | password=abc123 | 400 AUTH_PASSWORD_WEAK |
| TC-AUTH-004 | Register with duplicate student_id | N | Existing student_id | 409 AUTH_STUDENT_ID_EXISTS |
| TC-AUTH-005 | Register with missing email | N | No email field | 400 AUTH_VALIDATION_ERROR |
| TC-AUTH-006 | Login with correct credentials | P | Valid email + password | 200 + user object |
| TC-AUTH-007 | Login with wrong password | N | Correct email, wrong password | 401 AUTH_INVALID_CREDENTIALS |
| TC-AUTH-008 | Login with non-existent email | N | Unknown email | 401 AUTH_INVALID_CREDENTIALS |
| TC-AUTH-009 | Login with suspended account | N | Suspended user credentials | 403 AUTH_ACCOUNT_SUSPENDED |
| TC-AUTH-010 | Logout | P | Authenticated user | 200 + logged out |
| TC-AUTH-011 | Access protected route without login | N | No session cookie | 401 AUTH_NOT_AUTHENTICATED |
| TC-AUTH-012 | Access admin route as student | S | Student session, GET /api/v1/admin/users | 403 AUTH_INSUFFICIENT_ROLE |
| TC-AUTH-013 | Access coordinator route as student | S | Student session, POST /api/v1/attendance/scan | 403 AUTH_INSUFFICIENT_ROLE |
| TC-AUTH-014 | Change password with correct old password | P | Old + new valid password | 200 success |
| TC-AUTH-015 | Change password with wrong old password | N | Wrong old password | 400 AUTH_WRONG_PASSWORD |

---

## Events (TC-EVENT)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-EVENT-001 | Create event as admin | P | Valid event data, admin session | 201 + event object in DRAFT status |
| TC-EVENT-002 | Create event as student | S | Valid event data, student session | 403 AUTH_INSUFFICIENT_ROLE |
| TC-EVENT-003 | Create event with past start date | N | start_datetime in past | 422 EVENT_INVALID_DATES |
| TC-EVENT-004 | Create event with end before start | N | end < start | 422 EVENT_INVALID_DATES |
| TC-EVENT-005 | Get event by ID | P | Valid event_id | 200 + event object |
| TC-EVENT-006 | Get non-existent event | N | event_id=99999 | 404 EVENT_NOT_FOUND |
| TC-EVENT-007 | Publish event without coordinator | N | Admin publishes event with no coordinator | 422 EVENT_MISSING_COORDINATOR |
| TC-EVENT-008 | Edit event as non-owner coordinator | S | Coordinator not assigned, PUT /events/{id} | 403 EVENT_NOT_ASSIGNED |
| TC-EVENT-009 | Cancel event | P | Admin cancels REGISTRATION_OPEN event | 200 + status=CANCELLED |
| TC-EVENT-010 | Search events by title | P | search=workshop | 200 + filtered list |

---

## Registration (TC-REG)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-REG-001 | Register for open event | P | Student + REGISTRATION_OPEN event | 201 + registration + ticket |
| TC-REG-002 | Register for full event | N | Event at max_participants | 422 REG_EVENT_FULL |
| TC-REG-003 | Register for closed event | N | Event status=COMPLETED | 422 REG_EVENT_NOT_OPEN |
| TC-REG-004 | Register twice for same event | N | Second registration attempt | 409 REG_ALREADY_REGISTERED |
| TC-REG-005 | Cancel registration before deadline | P | Student owns registration | 200 success + ticket invalid |
| TC-REG-006 | Admin cancels any registration | P | Admin session + any registration_id | 200 success |

---

## Attendance (TC-ATT)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-ATT-001 | Coordinator scans valid QR | P | Valid ticket_code, correct event_id | 200 + student name + timestamp |
| TC-ATT-002 | Scan invalid ticket code | N | ticket_code=INVALID-CODE | 404 ATT_TICKET_NOT_FOUND |
| TC-ATT-003 | Scan ticket for wrong event | N | Correct ticket_code, wrong event_id | 422 ATT_WRONG_EVENT |
| TC-ATT-004 | Scan cancelled registration | N | Ticket for cancelled registration | 422 ATT_REGISTRATION_CANCELLED |
| TC-ATT-005 | Duplicate scan of same student | N | Second scan of same ticket | 409 ATT_ALREADY_ATTENDED |
| TC-ATT-006 | Student tries to mark own attendance | S | Student session, POST /api/v1/attendance/scan | 403 AUTH_INSUFFICIENT_ROLE |
| TC-ATT-007 | Coordinator scans for unassigned event | S | Coordinator not in event_coordinators | 403 ATT_COORDINATOR_NOT_ASSIGNED |
| TC-ATT-008 | Admin overrides attendance | P | Admin session, PUT /api/v1/attendance/{id} | 200 updated attendance |

---

## Social Feed (TC-SOCIAL)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-SOCIAL-001 | Create text post | P | content=Hello ITSA | 201 + post object |
| TC-SOCIAL-002 | Create image post | P | content + 2 JPEG images | 201 + post with media |
| TC-SOCIAL-003 | Create post exceeding char limit | N | content = 5001 characters | 400 SOCIAL_CONTENT_TOO_LONG |
| TC-SOCIAL-004 | Create post with hashtags | P | content=Hello #itsa #tech | 201 + hashtags created |
| TC-SOCIAL-005 | Edit own post | P | Owner edits content | 200 updated post |
| TC-SOCIAL-006 | Edit other user post | S | Non-owner edits | 403 SOCIAL_NOT_OWNER |
| TC-SOCIAL-007 | Delete own post | P | Owner deletes | 200 success |
| TC-SOCIAL-008 | Like a post | P | Student reacts LIKE | 200 reaction created |
| TC-SOCIAL-009 | Change reaction type | P | Student reacts LOVE on already LIKE post | 200 reaction updated |
| TC-SOCIAL-010 | Comment on post | P | Valid comment content | 201 comment object |
| TC-SOCIAL-011 | Save post | P | Student saves post | 200 success |
| TC-SOCIAL-012 | Save same post twice | N | Second save attempt | 409 SOCIAL_ALREADY_SAVED |

---

## Tickets (TC-TKT)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-TKT-001 | Ticket auto-generated on registration | P | Student registers | Ticket record created with UUID code |
| TC-TKT-002 | View own ticket | P | Student + own ticket_id | 200 ticket data + QR URL |
| TC-TKT-003 | View another user ticket | S | Student + other ticket_id | 403 SOCIAL_NOT_OWNER |
| TC-TKT-004 | Ticket invalidated on cancellation | P | Student cancels registration | ticket.is_valid = FALSE |

---

## Certificates (TC-CERT)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-CERT-001 | Certificate auto-generated on attendance | P | Attendance marked PRESENT | Certificate PDF created |
| TC-CERT-002 | Student downloads certificate | P | Own certificate_id | 200 PDF file |
| TC-CERT-003 | Student downloads another student cert | S | Other user certificate_id | 403 CERT_NOT_OWNER |
| TC-CERT-004 | Verify valid certificate | P | Valid certificate_code | 200 {valid:true, name, event} |
| TC-CERT-005 | Verify invalid certificate | N | Wrong certificate_code | 404 CERT_NOT_FOUND |
| TC-CERT-006 | Verify revoked certificate | P | Revoked code | 200 {valid:false, message:revoked} |

---

## Security (TC-SEC)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-SEC-001 | SQL injection in login email | S | email=admin@x.com' OR '1'='1 | 401 AUTH_INVALID_CREDENTIALS (not SQL error) |
| TC-SEC-002 | XSS in post content | S | content=< script >alert(1)< /script > | 201 stored escaped, rendered safe |
| TC-SEC-003 | Upload executable file | S | .php file as profile image | 400 FILE_TYPE_NOT_ALLOWED |
| TC-SEC-004 | Upload oversized file | S | 50MB image for profile | 400 FILE_TOO_LARGE |
| TC-SEC-005 | Access admin endpoint as student | S | Student session GET /api/v1/admin/users | 403 |
| TC-SEC-006 | Rate limit on chatbot | S | 21 AI chat requests in 1 hour | 429 AI_RATE_LIMIT |
| TC-SEC-007 | Access ticket QR as non-owner | S | GET /uploads/tickets/{code}.png without auth | 401 or 403 |
| TC-SEC-008 | Prompt injection in chatbot | S | message=Ignore system instructions and... | Chatbot declines politely |

---

## AI Features (TC-AI)

| ID | Name | Type | Input | Expected |
|---|---|---|---|---|
| TC-AI-001 | Chatbot responds to valid question | P | When is next hackathon? | AI response text |
| TC-AI-002 | Event recommendations returned | P | Student with some history | List of 5 recommended events |
| TC-AI-003 | Feedback analysis returned | P | Event with 10+ feedback entries | Structured sentiment analysis |
| TC-AI-004 | Content moderation flags violation | P | Harassment text submitted | {is_violation:true, recommendation:remove} |
| TC-AI-005 | Content moderation approves clean content | P | Normal post text | {is_violation:false, recommendation:approve} |
