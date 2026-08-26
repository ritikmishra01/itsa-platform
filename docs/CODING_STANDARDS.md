# Coding Standards -- ITSA Platform

## Python Standards

- PEP 8 compliance
- Use black for auto-formatting: black app/
- Use isort for import ordering: isort app/
- Use flake8 for linting: flake8 app/ --max-line-length=100
- Type hints on all function signatures
- Google-style docstrings on all service functions

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Variables | snake_case | event_count |
| Functions | snake_case | generate_ticket_qr |
| Classes | PascalCase | EventService |
| Constants | UPPER_SNAKE_CASE | MAX_UPLOAD_SIZE |
| Route URLs | kebab-case | /api/v1/my-tickets |
| DB Tables | snake_case | event_registrations |

## Architecture Rules

1. Routes call services only -- no DB queries in routes
2. Services contain all business logic -- call repositories
3. Repositories contain all DB queries -- return ORM objects
4. Models define SQLAlchemy schema and to_dict() only -- no business logic
5. Utils are pure functions with no Flask context dependencies

## Security Coding Rules

1. NEVER hardcode secrets in source code
2. ALWAYS validate input before processing
3. ALWAYS check authorization in service layer
4. NEVER use f-strings in SQL queries -- use ORM
5. ALWAYS use secure_filename() for uploads
6. NEVER log passwords or API keys
7. ALWAYS call db.session.rollback() on exception before re-raising

## Import Order

1. Standard library (os, uuid, json, datetime)
2. Third-party (flask, sqlalchemy, requests)
3. Local application (app.models, app.services, app.utils)

## Database Patterns

Always use try/except around db.session.commit().
Rollback on IntegrityError and re-raise as ConflictError.
Use ORM queries -- never raw SQL strings.

## Function Design

- Max ~50 lines per function
- Single responsibility principle
- Return early on errors (guard clauses)
- Explicit return types in type hints
- No side effects in utility functions
