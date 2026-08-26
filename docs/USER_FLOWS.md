# User Flows -- ITSA Platform

## Student Registration Flow

1. Student visits /register
2. Fills form: email, password, full name, student ID, department, year
3. Submits form -- POST /api/v1/auth/register
4. Backend validates all fields
5. Checks email uniqueness
6. Checks student_id uniqueness
7. Creates user record (role=STUDENT) + student_profile record
8. Auto-login the new user
9. Redirect to student dashboard

## Student Login Flow

1. Student visits /login
2. Enters email + password
3. POST /api/v1/auth/login
4. Backend finds user by email
5. Checks not suspended and active
6. Verifies password hash
7. Creates session via Flask-Login
8. Redirect to dashboard based on role

## Event Discovery Flow

1. Student visits /events
2. Sees list of PUBLISHED and REGISTRATION_OPEN events
3. Can search by title or filter by category/status/date
4. Clicks on event card
5. Views full event detail (description, venue, schedule, coordinators)
6. Sees registration status and Register button

## Event Registration Flow

1. Student clicks Register on event detail page
2. POST /api/v1/events/{id}/register
3. Backend checks: event open, deadline, capacity, not already registered
4. Creates EventRegistration record
5. Generates QR ticket
6. Awards +3 ITSA points
7. Sends confirmation notification (in-app + email)
8. Returns ticket data to frontend
9. Student sees success message with link to My Tickets

## QR Attendance Scan Flow (Coordinator scans Student)

1. Coordinator opens /coordinator/events/{id}/scan
2. Camera launches via html5-qrcode JS library
3. Student shows QR ticket on phone screen
4. Coordinator camera scans QR
5. JS library decodes ticket_code
6. POST /api/v1/attendance/scan {ticket_code, event_id}
7. Backend performs 6-step validation
8. Creates attendance record (status=PRESENT)
9. Awards +10 ITSA points to student
10. Sends notification to student
11. Returns success with student name
12. Scanner UI shows green overlay with student name
13. Camera resumes for next scan

## Certificate Flow

1. Attendance recorded (PRESENT)
2. System automatically calls generate_certificate(user_id, event_id, attendance_id)
3. Creates Certificate DB record with unique certificate_code
4. Generates PDF using ReportLab
5. Saves PDF to uploads/certificates/{code}.pdf
6. Sends CERTIFICATE_READY notification to student
7. Student visits /student/certificates
8. Sees certificate in list -- clicks Download
9. GET /api/v1/certificates/{id}/download -- returns PDF file

## Certificate Verification Flow (Public)

1. Anyone visits /certificates/verify/{certificate_code}
2. GET /api/v1/certificates/verify/{code}
3. Backend looks up certificate by code
4. If valid: returns student_name, event_name, event_date, issued_at
5. Does NOT return: email, student_id, department
6. Displays verification result on public page

## Social Post Creation Flow

1. Student clicks Create Post on feed page
2. Fills in text content
3. Optionally uploads images or video
4. Optionally links to an event
5. Submits form -- POST /api/v1/posts (multipart)
6. Backend processes: validates content, saves media files, detects hashtags, detects mentions
7. Creates Post record, PostMedia records, PostHashtag records, Mention records
8. Awards +2 ITSA points
9. Sends mention notifications to tagged users
10. Returns created post data
11. Post appears at top of feed

## Admin Content Moderation Flow

1. User reports a post -- POST /api/v1/posts/{id}/report
2. Report created in reports table (status=PENDING)
3. Admin sees report in moderation panel
4. Admin clicks Get AI Assessment
5. POST /api/v1/ai/moderate-content with post content
6. Gemini API returns recommendation (approve/remove/review)
7. Admin reviews AI recommendation
8. Admin makes final decision: Approve (dismiss) or Remove
9. Report status updated to RESOLVED or DISMISSED
10. If removed: post.is_active = FALSE, notification sent to author

## ITSA Points Earning Flow

1. Student performs an action (attend event, submit feedback, create post etc.)
2. Service function calls award_points(user_id, points, reason, related_id)
3. Creates ItsaPoints transaction record
4. Updates student_profiles.total_points += points
5. Leaderboard ranking reflects new total
6. Student sees updated points on dashboard
