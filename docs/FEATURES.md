# Features -- ITSA Platform

## Feature Catalog

### Authentication & User Management
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-AUTH-01 | Student self-registration | Public | High |
| F-AUTH-02 | Login with email + password | All | High |
| F-AUTH-03 | Session-based authentication | All | High |
| F-AUTH-04 | Role-based access control | System | High |
| F-AUTH-05 | Student profile management | Student | High |
| F-AUTH-06 | Profile image upload | All | Medium |
| F-AUTH-07 | Password change | All | High |
| F-AUTH-08 | Admin creates coordinator accounts | Admin | High |
| F-AUTH-09 | Admin suspend/unsuspend users | Admin | High |

### Event Management
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-EVT-01 | Create events (DRAFT to COMPLETED lifecycle) | Admin/Coord | High |
| F-EVT-02 | Event categories and venues | Admin | High |
| F-EVT-03 | Event poster upload | Admin/Coord | Medium |
| F-EVT-04 | Coordinator assignment | Admin | High |
| F-EVT-05 | Event search and filter | All | High |
| F-EVT-06 | Past events archive | All | Medium |
| F-EVT-07 | Event gallery upload | Admin/Coord | Medium |
| F-EVT-08 | Event cancellation with notifications | Admin | High |

### Registration & Ticketing
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-REG-01 | Event registration with eligibility checks | Student | High |
| F-REG-02 | Capacity and deadline enforcement | System | High |
| F-REG-03 | Registration cancellation | Student/Admin | High |
| F-REG-04 | QR ticket auto-generation | System | High |
| F-REG-05 | Ticket view and download | Student | High |

### QR Attendance
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-ATT-01 | Browser-based QR scanner | Coordinator | High |
| F-ATT-02 | 6-step ticket validation | System | High |
| F-ATT-03 | Duplicate attendance prevention | System | High |
| F-ATT-04 | Live attendance tracking | Coordinator | High |
| F-ATT-05 | Admin attendance override | Admin | Medium |

### Social Community Feed
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-SOC-01 | Create text/image/video posts | All auth | High |
| F-SOC-02 | Paginated feed (20 per page) | All auth | High |
| F-SOC-03 | 5-type reactions on posts | All auth | High |
| F-SOC-04 | Comments and replies | All auth | High |
| F-SOC-05 | Hashtag detection and pages | All auth | Medium |
| F-SOC-06 | Mention users in posts/comments | All auth | Medium |
| F-SOC-07 | Share posts to feed | All auth | Medium |
| F-SOC-08 | Save posts to personal collection | All auth | Medium |
| F-SOC-09 | Report content | All auth | High |
| F-SOC-10 | Admin content moderation panel | Admin | High |

### Certificates
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-CERT-01 | Auto PDF certificate on attendance | System | High |
| F-CERT-02 | Certificate download | Student | High |
| F-CERT-03 | Public certificate verification | Public | High |
| F-CERT-04 | Admin certificate revocation | Admin | Medium |

### Notifications
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-NOTIF-01 | In-app notifications bell | All auth | High |
| F-NOTIF-02 | Email notifications via SMTP | System | High |
| F-NOTIF-03 | Mark read / mark all read | All auth | Medium |

### Gamification
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-GAME-01 | ITSA Points transaction system | System | High |
| F-GAME-02 | Leaderboard by total points | All auth | High |
| F-GAME-03 | Engagement score (0-100) | System | Medium |
| F-GAME-04 | Points history for student | Student | Medium |
| F-GAME-05 | Admin manual points adjustment | Admin | Medium |

### AI Features
| ID | Feature | Technology | Roles | Priority |
|---|---|---|---|---|
| F-AI-01 | ITSA AI Chatbot | Gemini API | Student | High |
| F-AI-02 | Event recommendations | Scikit-learn | Student | High |
| F-AI-03 | Event description generator | Gemini API | Admin/Coord | Medium |
| F-AI-04 | Announcement generator | Gemini API | Admin/Coord | Medium |
| F-AI-05 | Feedback sentiment analysis | Gemini API | Admin/Coord | High |
| F-AI-06 | Comment moderation assist | Gemini API | Admin | High |
| F-AI-07 | Registration prediction | Scikit-learn | Admin/Coord | Medium |
| F-AI-08 | Attendance analytics | Pandas + ML | Admin/Coord | Medium |

### Analytics
| ID | Feature | Roles | Priority |
|---|---|---|---|
| F-AN-01 | Admin dashboard with stat cards | Admin | High |
| F-AN-02 | Chart.js analytics charts | Admin | High |
| F-AN-03 | Coordinator event analytics | Coordinator | High |
| F-AN-04 | PDF report generation | Admin/Coord | Medium |
