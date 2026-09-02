# ITSA Platform: Coordinator Operational Guide

## 1. Overview
The `COORDINATOR` role is designed for faculty mentors and student event managers. Coordinators are assigned to specific ITSA events to manage participant rosters, scan student tickets at venues, upload official event photographs, and review post-event feedback with AI sentiment summaries.

---

## 2. Navigating the Coordinator Workspace

### 2.1 Coordinator Dashboard (`/coordinator/dashboard`)
- **Assigned Events Overview**: Cards displaying all events where the coordinator is assigned as Lead or Support.
- **Live Metrics**: Total confirmed registrations, attendee counts, attendance percentages, and quick links to manage, scan, or view gallery.

### 2.2 Event Management Center (`/coordinator/events/<id>/manage`)
- **Participant Roster**: Searchable list of registered students with roll numbers, departments, contact numbers, and registration timestamps.
- **Roster Export**: Download attendee lists for venue logistics.
- **Status Controls**: Monitor capacity limits and registration deadlines.

### 2.3 Live QR Ticket Scanner (`/coordinator/events/<id>/scanner`)
- **Camera-Based Scanning**: Uses the device webcam or mobile camera via `html5-qrcode` to scan student ticket QR codes.
- **Manual Code Entry**: Backup input field allowing manual entry of ticket codes (`ITSA-TKT-...`).
- **Validation Engine**:
  1. Validates that the ticket exists and matches this specific event.
  2. Confirms registration status is `CONFIRMED`.
  3. Prevents duplicate check-ins (alerts if the student was already marked `PRESENT`).
  4. Automatically issues ITSA points (+10 pts) and triggers the certificate generation pipeline.

### 2.4 Event Photo Gallery (`/coordinator/events/<id>/gallery`)
- Upload high-resolution photographs taken during workshops, hackathons, and ceremonies.
- Add descriptive captions and tag featured keynote speakers.
- Featured images appear on the public homepage and event detail views.

### 2.5 Feedback & AI Sentiment Insights (`/coordinator/events/<id>/feedback`)
- Review student star ratings (1 to 5 stars) and qualitative commentary.
- **AI Sentiment Breakdown**: Gemini API aggregates submissions to report overall sentiment (Positive / Neutral / Needs Attention), common themes, and key student suggestions.

---

## 3. Venue Attendance Workflow (Step-by-Step)
1. Open your laptop, tablet, or smartphone and log in at `http://localhost:5000/login`.
2. Open the **Coordinator Dashboard** and click **Open Scanner** on the ongoing event.
3. Allow browser camera permissions when prompted.
4. Point the camera at the student's ticket QR code (displayed on their phone screen or printed ticket).
5. The scanner immediately displays the student's name, roll number, and a green success notification (`Attendance marked successfully`).
6. If a student attempts to reuse a ticket, a red alert displays: `Duplicate entry: Attendance already recorded`.