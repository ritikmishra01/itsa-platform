# QR Attendance System — ITSA Platform

## 1. Overview

The QR Attendance System enables **Coordinators** to scan student QR tickets to record event attendance. Students do NOT scan their own attendance.

**Key Principle**: The QR code contains only an opaque ticket_code (UUID). All validation and business logic runs server-side.

---

## 2. Architecture Decision: Why Coordinator Scans

**Problem with self-scan**: Students could mark each other present, share QR screenshots, or mark attendance without actually attending.

**Solution**: Only assigned Coordinators can trigger attendance — they physically receive the student's phone/printout and scan it at the venue entrance. This is the same model used by airlines, concert venues, and examination halls.

---

## 3. QR Code Content Format

The QR code encodes **only** the ticket_code string:

```
ITSA-TKT-a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**What is NOT encoded**:
- Student name, email, or student ID
- Event ID or event name
- Registration number
- Any personal data

This protects student privacy and prevents information disclosure if a QR is photographed.

---

## 4. Ticket Generation Process

Triggered automatically when registration is confirmed:

```python
# Pseudocode
def generate_ticket(registration_id):
    ticket_code = f"ITSA-TKT-{str(uuid.uuid4())}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(ticket_code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path = f"uploads/tickets/{ticket_code}.png"
    img.save(path)
    # Save ticket record to DB
    ticket = EventTicket(
        registration_id=registration_id,
        ticket_code=ticket_code,
        qr_image_path=path,
        is_valid=True
    )
    db.session.add(ticket)
    db.session.commit()
```

---

## 5. QR Scanning Process

### Option A: Browser-Based Camera (Primary)
Using `html5-qrcode` JavaScript library:

```html
<!-- Include in coordinator scanner page -->
<div id="qr-reader" style="width:500px"></div>
<script>
const html5QrCode = new Html5Qrcode("qr-reader");
html5QrCode.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: 250 },
    (decodedText) => {
        scanTicket(decodedText); // POST to /api/v1/attendance/scan
    }
);
</script>
```

### Option B: Manual Entry (Fallback)
Coordinator types the ticket code manually into a text input — useful if camera fails.

### Scan API Call
```javascript
async function scanTicket(ticketCode) {
    const response = await fetch('/api/v1/attendance/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ticket_code: ticketCode,
            event_id: currentEventId
        })
    });
    const data = await response.json();
    showResult(data); // Green success / Red error feedback
}
```

---

## 6. Backend Validation Flow (6 Steps)

```
POST /api/v1/attendance/scan
  { ticket_code: "ITSA-TKT-...", event_id: 42 }
  
Step 1: Does ticket_code exist in event_tickets table?
  → NO → 404 ATT_TICKET_NOT_FOUND

Step 2: Does the ticket belong to event_id?
  → ticket.registration.event_id != event_id → 422 ATT_WRONG_EVENT

Step 3: Is the registration status CONFIRMED?
  → registration.status != CONFIRMED → 422 ATT_REGISTRATION_CANCELLED

Step 4: Is the ticket is_valid = TRUE?
  → ticket.is_valid == FALSE → 422 ATT_TICKET_INVALID

Step 5: Does an attendance record already exist for (event_id, user_id)?
  → YES → 409 ATT_ALREADY_ATTENDED

Step 6: Is the event in an active state (ONGOING or REGISTRATION_CLOSED)?
  → NO → 422 ATT_EVENT_NOT_ACTIVE

Authorization Check: Is the coordinator assigned to this event?
  → NO → 403 ATT_COORDINATOR_NOT_ASSIGNED

All checks passed:
  → CREATE attendance record
  → AWARD +10 ITSA points
  → SEND notification to student
  → RETURN success with student name and timestamp
```

---

## 7. Success Flow

```python
# After all 6 validations pass:
attendance = Attendance(
    event_id=event_id,
    user_id=registration.user_id,
    registration_id=registration.id,
    ticket_id=ticket.id,
    scanned_by=current_user.id,
    scanned_at=datetime.utcnow(),
    status='PRESENT'
)
db.session.add(attendance)
db.session.flush()

# Award points
award_points(registration.user_id, 10, 'ATTENDANCE', event_id)

# Update student total_points
StudentProfile.query.filter_by(user_id=registration.user_id).update(
    {StudentProfile.total_points: StudentProfile.total_points + 10}
)

db.session.commit()

# Send notification (async, non-blocking)
send_notification(
    user_id=registration.user_id,
    type='SYSTEM',
    title='Attendance Recorded',
    message=f'Your attendance for {event.title} has been recorded.'
)
```

---

## 8. Error Cases Summary

| Error Code | Cause | Display to Coordinator |
|---|---|---|
| ATT_TICKET_NOT_FOUND | Invalid QR code | "Invalid ticket — not found" |
| ATT_WRONG_EVENT | Ticket for different event | "Wrong event ticket" |
| ATT_REGISTRATION_CANCELLED | Student cancelled | "Registration cancelled" |
| ATT_TICKET_INVALID | Ticket invalidated | "Ticket is no longer valid" |
| ATT_ALREADY_ATTENDED | Duplicate scan | "Already checked in!" |
| ATT_EVENT_NOT_ACTIVE | Event not started | "Event is not active yet" |
| ATT_COORDINATOR_NOT_ASSIGNED | Not authorized | "Not authorized for this event" |

---

## 9. Duplicate Prevention

Three layers of protection:
1. **Application check** (Step 5): Query attendance table before insert
2. **Database constraint**: `UNIQUE KEY uq_attendance_event_user (event_id, user_id)` in attendance table
3. **Transaction**: The check and insert happen in a single DB transaction

Even with concurrent scans (two coordinators scanning simultaneously), the database UNIQUE constraint catches the race condition and raises an IntegrityError, which is handled gracefully.

---

## 10. Manual Attendance Override (Admin)

Admin can override attendance records via:
`PUT /api/v1/attendance/{id}` with `{ "status": "PRESENT", "notes": "Manual correction" }`

This action is logged to audit_logs with admin_id, action, and timestamp.

---

## 11. Data Stored Per Attendance Record

```json
{
  "id": 1,
  "event_id": 42,
  "user_id": 5,
  "registration_id": 23,
  "ticket_id": 23,
  "scanned_by": 8,
  "scanned_at": "2026-09-15T09:32:15",
  "status": "PRESENT",
  "notes": null
}
```

---

## 12. Security Considerations

| Risk | Mitigation |
|---|---|
| Screenshot sharing | Ticket codes are UUIDs — each is unique and can only be used once |
| Unauthorized coordinator | Coordinator must be assigned to the specific event |
| Replay attack | Attendance recorded with unique constraint — cannot mark twice |
| QR tampering | Backend validates ticket_code against database; format-only check is insufficient |
| Private data in QR | QR contains only ticket_code UUID — no personal data |

---

## 13. QR Code Implementation

```python
# requirements.txt
# qrcode[pil]==7.4.2
# Pillow==10.0.0

import qrcode
import uuid
from PIL import Image

def generate_ticket_qr(ticket_code: str, output_path: str) -> str:
    """Generate QR code PNG for a ticket code."""
    qr = qrcode.QRCode(
        version=None,  # Auto-select
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% correction
        box_size=10,
        border=4,
    )
    qr.add_data(ticket_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#1a1a1a", back_color="white")
    img.save(output_path)
    return output_path
```

---

## 14. Browser QR Scanner Setup

```html
<!-- coordinator/scanner.html -->
<script src="https://unpkg.com/html5-qrcode/minified/html5-qrcode.min.js"></script>

<div id="qr-reader" style="width: 400px; margin: auto;"></div>
<div id="scan-result" class="mt-3"></div>

<!-- Manual fallback -->
<div class="mt-3">
  <input type="text" id="manual-code" placeholder="Enter ticket code manually" class="form-control">
  <button onclick="submitManual()" class="btn btn-primary mt-2">Submit</button>
</div>

<script>
const html5QrCode = new Html5Qrcode("qr-reader");
const config = { fps: 10, qrbox: { width: 250, height: 250 } };

html5QrCode.start(
    { facingMode: "environment" },
    config,
    (decodedText) => {
        html5QrCode.stop();
        submitScan(decodedText);
    },
    (error) => { /* Ignore scan errors */ }
).catch(err => {
    document.getElementById("qr-reader").innerHTML =
        "<p class=text-danger>Camera access denied. Please use manual entry.</p>";
});

async function submitScan(ticketCode) {
    const res = await fetch("/api/v1/attendance/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticket_code: ticketCode, event_id: EVENT_ID })
    });
    const data = await res.json();
    
    const resultDiv = document.getElementById("scan-result");
    if (data.success) {
        resultDiv.innerHTML = `<div class="alert alert-success">
            ✅ ${data.data.student_name} — Checked In at ${data.data.scanned_at}
        </div>`;
        // Resume scanning after 2 seconds
        setTimeout(() => html5QrCode.start(...), 2000);
    } else {
        resultDiv.innerHTML = `<div class="alert alert-danger">
            ❌ ${data.error.message}
        </div>`;
        setTimeout(() => html5QrCode.start(...), 2000);
    }
}
</script>
```
