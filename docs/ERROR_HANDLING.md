# Error Handling -- ITSA Platform

## Philosophy

Fail gracefully. Never expose internals. Log details server-side.

## Standard Error Response

The API always returns JSON with success:false and an error object containing code and message.

## Custom Exception Classes

- ItsaError (base class with code, message, status_code)
- NotFoundError extends ItsaError (status_code=404)
- AuthorizationError extends ItsaError (status_code=403)
- ConflictError extends ItsaError (status_code=409)
- ValidationError extends ItsaError (status_code=400)
- AIServiceError extends ItsaError (status_code=503)
- FileUploadError extends ItsaError (status_code=400)

## Global Handler Pattern

- Register errorhandler for ItsaError -- returns standard JSON
- Register errorhandler for 404 -- returns SYS_NOT_FOUND
- Register errorhandler for 500 -- logs full traceback, returns generic message to client

## Service Layer Pattern

Services raise custom exceptions. Routes do NOT catch them. Global handler catches all.

## HTTP Status Codes

200 OK - Successful GET/PUT/DELETE
201 Created - Successful POST creating a resource
400 Bad Request - Validation failure
401 Unauthorized - Not authenticated
403 Forbidden - Insufficient role
404 Not Found - Resource does not exist
409 Conflict - Duplicate or conflicting resource
422 Unprocessable Entity - Business rule violation
429 Too Many Requests - Rate limit exceeded
500 Internal Server Error - Unexpected server error

## Frontend Error Display

- Toast notifications for API errors
- Inline field errors for form validation
- Full-page 404.html and 500.html templates
