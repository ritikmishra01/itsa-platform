# ITSA Platform — Documentation Index

> **This docs/ folder is the Single Source of Truth for the ITSA Platform project.**
> Every architectural decision, API design, database table, AI feature, security rule, and workflow is documented here.

---

## How to Use This Documentation

1. **Start here** for an overview: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
2. **Understand requirements** before writing code: [REQUIREMENTS.md](REQUIREMENTS.md)
3. **Check role permissions** before implementing features: [USER_ROLES.md](USER_ROLES.md)
4. **Follow the database schema** — do not deviate without updating [DATABASE_DESIGN.md](DATABASE_DESIGN.md)
5. **Every API must match** [API_ENDPOINTS.md](API_ENDPOINTS.md)
6. **Every function must match** [FUNCTION_SPECIFICATION.md](FUNCTION_SPECIFICATION.md)
7. **Follow the roadmap**: [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)

---

## Documentation Maintenance Policy

Whenever you change:
- An API endpoint → update API_ENDPOINTS.md
- A database table → update DATABASE_DESIGN.md and DATABASE_SCHEMA.sql
- A backend function → update FUNCTION_SPECIFICATION.md
- An AI feature → update AI_FEATURES.md
- A user role permission → update USER_ROLES.md
- A security rule → update SECURITY.md
- A workflow → update USER_FLOWS.md

**Documentation must always reflect the actual implementation.**

---

## Complete Document Index

### Project Foundation
| File | Purpose |
|---|---|
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Vision, problem, solution, modules, benefits |
| [REQUIREMENTS.md](REQUIREMENTS.md) | FR and NFR with unique IDs |
| [USER_ROLES.md](USER_ROLES.md) | Student, Coordinator, Admin permissions |
| [FEATURES.md](FEATURES.md) | Complete feature catalog |
| [USER_FLOWS.md](USER_FLOWS.md) | All user journeys and workflows |
| [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) | 12-phase implementation plan |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [FUTURE_SCOPE.md](FUTURE_SCOPE.md) | Planned future enhancements |

### Architecture & Design
| File | Purpose |
|---|---|
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | System design and architecture |
| [TECH_STACK.md](TECH_STACK.md) | Technology choices and rationale |
| [BACKEND_STRUCTURE.md](BACKEND_STRUCTURE.md) | Flask app folder structure |
| [FRONTEND_STRUCTURE.md](FRONTEND_STRUCTURE.md) | Templates and static files |

### Database
| File | Purpose |
|---|---|
| [DATABASE_DESIGN.md](DATABASE_DESIGN.md) | All 30 tables documented |
| [DATABASE_SCHEMA.sql](DATABASE_SCHEMA.sql) | Production MySQL schema |

### API Reference
| File | Purpose |
|---|---|
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API standards and conventions |
| [API_ENDPOINTS.md](API_ENDPOINTS.md) | Every endpoint with request/response |
| [API_ERROR_CODES.md](API_ERROR_CODES.md) | All error codes |

### Implementation
| File | Purpose |
|---|---|
| [FUNCTION_SPECIFICATION.md](FUNCTION_SPECIFICATION.md) | All 88+ backend functions |
| [VALIDATION_RULES.md](VALIDATION_RULES.md) | Input validation for every form/API |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Error handling patterns |
| [LOGGING.md](LOGGING.md) | Logging strategy |
| [FILE_UPLOADS.md](FILE_UPLOADS.md) | File upload system |

### Feature Documentation
| File | Purpose |
|---|---|
| [EVENT_MANAGEMENT.md](EVENT_MANAGEMENT.md) | Event lifecycle |
| [REGISTRATION_SYSTEM.md](REGISTRATION_SYSTEM.md) | Registration flow |
| [TICKET_SYSTEM.md](TICKET_SYSTEM.md) | QR ticket generation |
| [QR_ATTENDANCE.md](QR_ATTENDANCE.md) | Attendance scanning system |
| [CERTIFICATE_SYSTEM.md](CERTIFICATE_SYSTEM.md) | PDF certificate generation |
| [FEEDBACK_SYSTEM.md](FEEDBACK_SYSTEM.md) | Event feedback |
| [SOCIAL_FEED.md](SOCIAL_FEED.md) | Community feed |
| [NOTIFICATION_SYSTEM.md](NOTIFICATION_SYSTEM.md) | Notifications |
| [GAMIFICATION.md](GAMIFICATION.md) | Points and leaderboard |
| [ANALYTICS.md](ANALYTICS.md) | Analytics and reports |

### AI Documentation
| File | Purpose |
|---|---|
| [AI_FEATURES.md](AI_FEATURES.md) | All AI/ML features |
| [AI_API_DOCUMENTATION.md](AI_API_DOCUMENTATION.md) | Gemini API integration |
| [GEMINI_PROMPTS.md](GEMINI_PROMPTS.md) | Versioned prompt library |

### Security & Auth
| File | Purpose |
|---|---|
| [AUTHENTICATION.md](AUTHENTICATION.md) | Auth system |
| [AUTHORIZATION.md](AUTHORIZATION.md) | RBAC system |
| [SECURITY.md](SECURITY.md) | Security policies |

### Testing
| File | Purpose |
|---|---|
| [TESTING.md](TESTING.md) | Testing approach and setup |
| [TEST_CASES.md](TEST_CASES.md) | All test cases |

### Operations
| File | Purpose |
|---|---|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Render deployment guide |
| [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) | All environment variables |
| [GIT_WORKFLOW.md](GIT_WORKFLOW.md) | Branching and commit strategy |
| [CODING_STANDARDS.md](CODING_STANDARDS.md) | Code quality standards |
| [UI_UX_GUIDELINES.md](UI_UX_GUIDELINES.md) | Design system |
