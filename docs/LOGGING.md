# Logging -- ITSA Platform

## Log Files

| File | Content |
|---|---|
| logs/app.log | General application logs |
| logs/error.log | ERROR and CRITICAL only |
| logs/audit.log | Admin action audit trail |
| logs/ai.log | AI API call logs without content |

## Log Format

[TIMESTAMP] LEVEL [MODULE] MESSAGE

## What to Log

- Application startup and shutdown
- User login/logout events (INFO)
- Failed login attempts (WARNING)
- Admin actions (INFO)
- API errors 4xx (WARNING)
- Unhandled exceptions (ERROR with stack trace)
- AI API calls without content (INFO)
- File uploads (INFO)

## What NOT to Log

- Passwords plaintext or hash
- GEMINI_API_KEY or any secret keys
- Session tokens
- Student personal data in high-frequency logs

## Log Rotation

10MB per file, keep last 30 backup files using RotatingFileHandler.

## Audit Log DB Table

All admin actions stored in audit_logs table:
- User suspension and unsuspension
- Manual points adjustment
- Attendance override
- Certificate revocation
- Content removal
- Account deletion
