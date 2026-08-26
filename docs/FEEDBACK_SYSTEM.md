# Certificate System — ITSA Platform

## Overview

Auto-generated PDF attendance certificates for students who attend events (status=PRESENT).

## Certificate Code Format

ITSA-CERT-{uuid4}
Example: ITSA-CERT-b2c3d4e5-f6a7-8901-bcde-f23456789012

## Generation Trigger

Automatically generated when:
1. Coordinator scans student QR → attendance recorded → status=PRESENT
2. OR: Admin manually triggers generation

Only one certificate per student per event (UNIQUE constraint).

## PDF Design (ReportLab)

- Format: A4 Landscape (297mm x 210mm)
- Color scheme: ITSA Blue (#1a73e8) and Gold (#fbbc04)
- Decorative border
- ITSA header with organization name
- Certificate text: "This is to certify that [FULL NAME] has successfully attended [EVENT TITLE] held on [DATE] at [VENUE]"
- Issued date
- Verification QR code (links to /certificates/verify/{code})
- Digital signature area placeholder
- Certificate code printed in small text at bottom

## Storage

PDF saved to: uploads/certificates/{certificate_code}.pdf
Path stored in certificates.pdf_path column.

## Certificate Verification (Public)

GET /certificates/verify/{code}

Returns:
`json
{
  "valid": true,
  "student_name": "Rahul Sharma",
  "event_name": "Web Dev Workshop",
  "event_date": "2026-09-15",
  "issued_at": "2026-09-15T18:00:00"
}
`

Does NOT expose: email, student_id, roll number, department.

## Revocation

Admin sets is_valid = FALSE.
Verification returns: { "valid": false, "message": "Certificate has been revoked" }
"@ | Out-File -FilePath "C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform\docs\CERTIFICATE_SYSTEM.md" -Encoding utf8
Write-Host "CERTIFICATE_SYSTEM.md done"

# FEEDBACK_SYSTEM.md
@"
# Feedback System — ITSA Platform

## Eligibility

Student must have PRESENT attendance for the event.
One feedback per student per event (UNIQUE constraint).
Feedback window: 24 hours after event end_datetime (configurable via FEEDBACK_WINDOW_HOURS env var).

## Feedback Data

- rating: 1-5 stars (required, integer)
- content: optional text, max 2000 characters

## Submission Flow

POST /api/v1/feedback
→ Check student has PRESENT attendance for event_id
→ Check feedback window is open
→ Check no existing feedback (UNIQUE constraint)
→ Create Feedback record
→ Award +5 ITSA points
→ Return 201

## Display

Coordinator sees: all feedback for assigned events, average rating, distribution.
Admin sees: all feedback for any event.
Students do NOT see others' feedback.

## AI Feedback Analysis

POST /api/v1/ai/analyze-feedback { "event_id": 42 }

Fetches all feedback texts and ratings.
Anonymizes data (removes any user identifiers).
Sends to Gemini API with PROMPT_FEEDBACK_ANALYSIS_V1.
Returns structured analysis: sentiment, themes, strengths, improvements, quotes.
Result cached in ai_analysis table to avoid re-analyzing same data.
