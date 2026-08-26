# Git Workflow -- ITSA Platform

## Branch Strategy

| Branch | Purpose |
|---|---|
| main | Production-ready code only |
| develop | Integration branch for features |
| feature/* | New feature development |
| bugfix/* | Bug fixes |
| hotfix/* | Critical production fixes |

## Branch Naming Examples

- feature/user-authentication
- feature/event-management
- feature/qr-attendance
- feature/social-feed
- bugfix/ticket-qr-generation
- hotfix/login-session-error

## Commit Message Format

type(scope): description

Types: feat, fix, docs, refactor, test, chore, style

Examples:
- feat(auth): add student registration with student ID validation
- fix(attendance): prevent duplicate scan on concurrent requests
- docs(api): update event endpoints documentation
- test(registration): add capacity limit test cases

## .gitignore Must Include

.env
__pycache__/
*.pyc
venv/
uploads/
logs/
instance/
.pytest_cache/
htmlcov/
*.sqlite3
app/ai/ml_models/*.joblib

## NEVER Commit

- .env file
- API keys or passwords
- Database dumps with real user data
- Uploaded user files
- Trained ML models with private training data

## Pull Request Process

1. Create branch from develop
2. Write code and tests
3. All tests pass locally
4. Open PR to develop
5. At least 1 code review required
6. Merge after approval
