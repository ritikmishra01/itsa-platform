# AI API Documentation -- ITSA Platform

## Gemini API Integration

### Package
google-generativeai (Google official Python SDK)

### Model
gemini-2.0-flash -- Fast, cost-effective, suitable for chatbot and content generation

### API Key Management

1. Store GEMINI_API_KEY in .env only
2. Load via python-dotenv at startup
3. NEVER hardcode in source code
4. NEVER log or print the key
5. NEVER expose in API responses
6. NEVER send to frontend

### Initialization

import google.generativeai as genai
import os
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

### Request Format

For chatbot (multi-turn):
response = model.generate_content(contents=[
    {role: user, parts: [system_prompt + user_message]}
])

For content generation (single turn):
response = model.generate_content(prompt)

### Response Handling

text = response.text  -- string output
Always wrap in try/except to handle API failures gracefully.

### Error Handling

| Error | HTTP Response |
|---|---|
| API key invalid (401) | 503 AI_SERVICE_UNAVAILABLE |
| Rate limit exceeded (429) | 429 AI_RATE_LIMIT |
| Service unavailable (503) | 503 AI_SERVICE_UNAVAILABLE |
| Content blocked by safety | 422 AI_CONTENT_BLOCKED |
| Network timeout | 503 AI_SERVICE_UNAVAILABLE |

### Retry Strategy

On 503 or network errors: retry up to 3 times with exponential backoff (1s, 2s, 4s).
On 429 rate limit: do NOT retry -- return error to user with Retry-After hint.
On 422 content blocked: return AI_CONTENT_BLOCKED -- do not retry.

### Safety Settings

Configure safety settings to allow standard college/educational content.
Block harassment, hate speech, dangerous content at BLOCK_MEDIUM_AND_ABOVE threshold.

### Application Rate Limits

Per user per hour:
- Chatbot: max 20 messages
- Content generation: max 10 requests
- Feedback analysis: max 5 requests
- Content moderation: max 20 requests

Track with in-memory counter or Flask-Limiter keyed by user_id.

### Prompt Injection Protection

1. Never concatenate raw user input into system prompt
2. Always pass user content as a separate user message turn
3. Strip HTML tags from user input before sending
4. Limit user input length (1000 chars for chat, 500 for other inputs)
5. Validate AI JSON output before using it (for moderation and analysis prompts)
6. System prompt always set as a fixed constant (not from user or DB)

### Data Privacy

- Do NOT send student emails, student IDs, or full personal records to Gemini API
- Feedback is anonymized before analysis (remove user identifiers)
- Log all AI calls with user_id and feature name -- NOT the content
- Do not store AI responses indefinitely -- only store analysis results

### Token Management

Set max_output_tokens per request type:
- Chatbot: 1024 tokens
- Event description: 800 tokens
- Announcement: 600 tokens
- Caption: 100 tokens
- Feedback analysis: 1500 tokens
- Moderation: 300 tokens

### Fallback Strategy

If Gemini API unavailable:
- Chatbot: Return message directing user to contact admin
- Description generator: Return empty field (user fills manually)
- Feedback analysis: Return cached result or defer
- Moderation: Flag for human review without AI input

### Cost Management

- Monitor token usage in development
- Use gemini-2.0-flash (most cost-efficient)
- Cache identical requests where appropriate (e.g., same event feedback analysis)
- Set per-user rate limits to control costs
