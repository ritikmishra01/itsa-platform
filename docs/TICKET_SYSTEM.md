# Ticket System — ITSA Platform

## Overview

Every confirmed registration generates a unique digital QR ticket. Students present this ticket to coordinators for attendance.

## Ticket Code Format

ITSA-TKT-{uuid4}
Example: ITSA-TKT-a1b2c3d4-e5f6-7890-abcd-ef1234567890

## QR Code Specification

- Library: python-qrcode with Pillow
- Error correction: ERROR_CORRECT_H (30% restoration)
- Box size: 10 pixels per module
- Border: 4 modules
- Colors: Black on white
- Format: PNG
- Storage: uploads/tickets/{ticket_code}.png

## QR Content

The QR contains ONLY the ticket_code string. No personal data encoded.

## Ticket Display (Student)

My Tickets page shows all event tickets. Each ticket shows:
- Event name, date, venue
- Student name
- Ticket code text
- QR code image
- Status (Valid/Invalid)
- Instruction: "Show this QR to the coordinator at entry"

## Ticket Validity

- is_valid = TRUE: Active ticket
- is_valid = FALSE: Cancelled (registration cancelled) or invalidated by admin

## Security

- ticket_code is a UUID — not guessable, not sequential
- QR image served only to ticket owner (access-controlled route)
- Backend validates ticket_code against database — QR format alone is insufficient
- Ticket cannot be reused after attendance is recorded (duplicate prevention)
