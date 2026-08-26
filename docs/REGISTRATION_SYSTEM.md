# Registration System — ITSA Platform

## Eligibility Checks (in order)

1. User is authenticated
2. User role is STUDENT
3. User account is active and not suspended
4. Event status is REGISTRATION_OPEN
5. Registration deadline has not passed
6. max_participants not reached (if set)
7. Student is not already registered (unique constraint check)

All checks fail fast — first failure returns error.

## Registration Flow

Student clicks Register
→ POST /api/v1/events/{id}/register
→ Eligibility checks (7 steps)
→ BEGIN TRANSACTION
→ Create EventRegistration (status=CONFIRMED)
→ Generate registration_number: ITSA-{EVENT_ID}-{YEAR}-{SEQUENCE}
→ Increment events.current_registrations
→ Generate QR ticket (EventTicket record)
→ Generate QR image file
→ Award +3 ITSA points
→ COMMIT TRANSACTION
→ Send registration confirmation (in-app + email) — async
→ Return 201 with registration and ticket data

## Registration Cancellation

Student cancels before registration_deadline:
→ Set registration.status = CANCELLED
→ Set registration.cancelled_at = NOW()
→ Set ticket.is_valid = FALSE
→ Decrement events.current_registrations
→ Deduct -3 ITSA points
→ Send cancellation notification

Admin can cancel at any time (no deadline restriction).

## Capacity Management

Race condition protection:
- Application-level check: current_registrations < max_participants
- Database transaction wraps the check and insert atomically
- Unique constraint on (event_id, user_id) prevents true duplicates
- If concurrent registrations exceed capacity, last ones fail at DB level

## Registration Number Format

ITSA-{EVENT_ID}-{YEAR}-{ZERO_PADDED_SEQUENCE}
Example: ITSA-42-2026-0001

## Status Values

| Status | Description |
|---|---|
| CONFIRMED | Active valid registration |
| CANCELLED | Student or admin cancelled |
| WAITLISTED | Future feature (not implemented in v1) |
