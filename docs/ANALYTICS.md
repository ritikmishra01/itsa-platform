# Analytics — ITSA Platform

## Admin Dashboard Metrics

| Metric | Query Source |
|---|---|
| Total students | COUNT(users WHERE role=STUDENT) |
| Total coordinators | COUNT(users WHERE role=COORDINATOR) |
| Total events | COUNT(events) |
| Total registrations | COUNT(event_registrations WHERE status=CONFIRMED) |
| Total attendance | COUNT(attendance WHERE status=PRESENT) |
| Certificates issued | COUNT(certificates WHERE is_valid=TRUE) |
| Average feedback rating | AVG(feedback.rating) |
| Active students (month) | COUNT DISTINCT user_id in attendance WHERE scanned_at >= month_start |

## Charts (Chart.js)

| Chart | Type | Data |
|---|---|---|
| Monthly registrations | Line | Last 12 months registration counts |
| Events by category | Pie/Doughnut | COUNT per category |
| Department participation | Bar | COUNT attendances per department |
| Year participation | Bar | COUNT per year_of_study |
| Attendance rate trend | Line | (attended/registered)*100 per month |
| Feedback rating distribution | Bar | Count of 1-5 star ratings |

## Coordinator Analytics (Assigned Events Only)

- Registration count for their event
- Attendance count and rate
- Average feedback rating
- Hourly scan-in distribution during event

## Student Analytics (Own Data)

- Events attended count
- Events registered count
- Total ITSA points
- Engagement score
- Certificates earned

## Report Generation

PDF reports via ReportLab:
- Event Report: registrations list, attendance list, feedback summary
- Monthly Summary: events, registrations, attendance, top students
- Department Report: participation by department

## Performance

Heavy analytics queries use SQLAlchemy with proper indexes.
Results can be cached (simple in-memory dict with TTL) for dashboard stats.
Date range limits applied to prevent runaway queries.
