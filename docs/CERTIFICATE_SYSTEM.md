# Certificate System -- ITSA Platform

## Overview
Auto-generated PDF attendance certificates for students who attend events (status=PRESENT).

## Certificate Code Format
ITSA-CERT-{uuid4}
Example: ITSA-CERT-b2c3d4e5-f6a7-8901-bcde-f23456789012

## Generation Trigger
1. Coordinator scans student QR ticket
2. Attendance recorded with status=PRESENT
3. System automatically calls generate_certificate(user_id, event_id, attendance_id)
4. Certificate PDF created and notification sent to student

Only one certificate per student per event -- enforced by UNIQUE(user_id, event_id) constraint.

## PDF Design (ReportLab)

- Format: A4 Landscape
- Color scheme: ITSA Blue #1a73e8 and ITSA Gold #fbbc04
- Decorative border frame
- ITSA organization name in header
- Certificate text: This is to certify that [FULL NAME] has successfully attended [EVENT TITLE] held on [DATE] at [VENUE]
- Issued date at bottom
- Verification QR code linking to /certificates/verify/{code}
- Certificate code printed in small monospace text

## Storage
PDF saved to: uploads/certificates/{certificate_code}.pdf
Path stored in certificates.pdf_path column in database.

## Certificate Verification (Public)

GET /api/v1/certificates/verify/{code}

Success response:
{valid: true, student_name: Rahul Sharma, event_name: Web Dev Workshop, event_date: 2026-09-15, issued_at: 2026-09-15T18:00:00}

Does NOT expose: email, student_id, roll number, department.

Revoked certificate response:
{valid: false, message: Certificate has been revoked}

## Revocation
Admin sets certificates.is_valid = FALSE.
Verification endpoint returns valid=false with revocation message.
PDF file is not deleted -- only the is_valid flag changes.

## Security
- certificate_code is a UUID -- not guessable
- PDF download requires authentication and ownership check
- Public verification by code only -- no personal data exposed
- One certificate per student per event
