# Future Scope -- ITSA Platform

## Phase 2 Planned Features

### Mobile Application
Build a Flutter-based mobile app for iOS and Android.
Key features: Push notifications, native QR scanner, offline ticket viewing.

### Real-Time Features
WebSocket integration for:
- Live attendance count updates on coordinator dashboard
- Real-time feed updates without refresh
- Live event announcements during ongoing events

### Payment Integration
For paid events: integrate Razorpay or Stripe.
Registration flow includes payment step.
Refund handling on cancellation.

### Waitlist System
When event is full, students join waitlist.
Auto-promotion when registered student cancels.

### Alumni Network
Extend platform to ITSA alumni.
Alumni can post jobs, mentorship offers.
Alumni can sponsor events.

### Job Board
Internship and job postings from ITSA alumni and partners.
Students can apply directly.

### Mentorship Matching
AI-powered matching of students with alumni mentors based on interests.

### Cloud File Storage
Migrate uploads from local filesystem to Cloudinary or Amazon S3.
Solve Render ephemeral filesystem limitation.
CDN delivery for faster media loading.

### Advanced ML Models
Collaborative filtering in addition to content-based.
Deep learning for engagement prediction.
NLP for advanced feedback analysis.

### Multi-College Support
Multi-tenant architecture supporting multiple colleges.
Each college has its own ITSA namespace.
Cross-college event discovery.

### Microservices Migration
When scale requires it:
- Auth Service
- Event Service
- Notification Service
- AI Service
Separate deployments with API gateway.

### Redis Integration
Session storage in Redis for horizontal scaling.
Caching for analytics queries.
Rate limiting backed by Redis.

### Event Live Streaming
Integration with YouTube Live or Zoom for hybrid events.
Stream link embedded in event detail page.
Attendance recorded for virtual attendees.
