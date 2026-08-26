# API Documentation — ITSA Platform

## 1. API Overview

| Property | Value |
|---|---|
| Base URL | `/api/v1` |
| Protocol | HTTP/HTTPS |
| Authentication | Session-based (Flask-Login cookies) |
| Content-Type | `application/json` |
| Response Format | JSON (see standard formats below) |
| Pagination | Offset-based with `page` and `per_page` query params |

---

## 2. Standard Response Formats

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```
The `meta` field is only present for paginated responses.

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "EVENT_NOT_FOUND",
    "message": "The requested event does not exist",
    "details": {}
  }
}
```

---

## 3. HTTP Status Codes

| Code | Meaning | When Used |
|---|---|---|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST that creates a resource |
| 400 | Bad Request | Invalid input or validation failure |
| 401 | Unauthorized | Not authenticated (not logged in) |
| 403 | Forbidden | Authenticated but insufficient role/permission |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate resource (already registered, etc.) |
| 422 | Unprocessable Entity | Validation passed but business rule failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

---

## 4. Authentication

Authentication is session-based using Flask-Login.

1. Client sends `POST /api/v1/auth/login` with credentials
2. Server sets a secure HttpOnly session cookie
3. All subsequent requests send this cookie automatically
4. Server validates session on each protected route
5. Client sends `POST /api/v1/auth/logout` to end session

**Protected routes** return `401 Unauthorized` if no valid session exists.
**Role-restricted routes** return `403 Forbidden` if the user's role is insufficient.

---

## 5. Pagination

Paginated endpoints accept:
- `page` (integer, default: 1)
- `per_page` (integer, default: 20, max: 100)

Example: `GET /api/v1/posts?page=2&per_page=20`

---

## 6. Rate Limiting

| Endpoint Category | Limit |
|---|---|
| Login | 5 requests/minute/IP |
| General API | 100 requests/minute/user |
| AI Chatbot | 20 requests/hour/user |
| AI Content Generation | 10 requests/hour/user |

Rate limit exceeded returns `429` with a `Retry-After` header.

---

## 7. Versioning

Current API version: **v1**

The version is included in the URL path: `/api/v1/...`

Breaking changes will increment the version number. Old versions will be supported for a transition period.

---

## 8. Security Considerations

- All API inputs are validated server-side
- Role checks are always performed server-side
- SQL injection prevented via SQLAlchemy ORM
- File uploads validated for type and size
- AI endpoints sanitize user input before passing to Gemini API
- Error responses never expose stack traces or internal details
