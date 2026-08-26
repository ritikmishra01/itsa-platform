# Environment Variables — ITSA Platform

> Copy `.env.example` to `.env`. Fill in real values. Never commit `.env`.

---

## Flask Core

| Variable | Required | Default | Example | Notes |
|---|---|---|---|---|
| `FLASK_ENV` | Yes | — | `development` | `development`, `production`, `testing` |
| `FLASK_DEBUG` | Yes | — | `True` | `False` in production always |
| `SECRET_KEY` | Yes | — | `xK9#mP2@...` | Min 32 random chars. Rotate if exposed. |
| `PORT` | No | `5000` | `5000` | Server port |

## Database

| Variable | Required | Default | Example | Notes |
|---|---|---|---|---|
| `DATABASE_URL` | Yes | — | `mysql+pymysql://user:pass@host:3306/itsa_platform` | Full SQLAlchemy URL |
| `MYSQL_HOST` | Yes | — | `localhost` | DB host |
| `MYSQL_PORT` | No | `3306` | `3306` | DB port |
| `MYSQL_DATABASE` | Yes | — | `itsa_platform` | DB name |
| `MYSQL_USER` | Yes | — | `root` | DB user |
| `MYSQL_PASSWORD` | Yes | — | `your_password` | DB password. Never commit. |

## AI — Gemini

| Variable | Required | Default | Example | Notes |
|---|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | `AIzaSy...` | Get from Google AI Studio. Never expose. |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | `gemini-2.0-flash` | Model name |
| `AI_MAX_TOKENS` | No | `1024` | `1024` | Max output tokens per request |

## Email / SMTP

| Variable | Required | Default | Example | Notes |
|---|---|---|---|---|
| `SMTP_HOST` | Yes | — | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | No | `587` | `587` | 587=TLS, 465=SSL |
| `SMTP_USERNAME` | Yes | — | `itsa@gmail.com` | Email account |
| `SMTP_PASSWORD` | Yes | — | `app_password_here` | Use App Password for Gmail |
| `SMTP_USE_TLS` | No | `True` | `True` | Enable STARTTLS |
| `EMAIL_FROM_NAME` | No | `ITSA Platform` | `ITSA Platform` | Sender display name |
| `EMAIL_FROM_ADDRESS` | Yes | — | `noreply@itsa.edu` | From address |

## File Uploads

| Variable | Required | Default | Example | Notes |
|---|---|---|---|---|
| `UPLOAD_FOLDER` | No | `uploads` | `uploads` | Relative path from project root |
| `MAX_CONTENT_LENGTH` | No | `104857600` | `104857600` | 100MB in bytes |

## Security

| Variable | Required | Default | Example | Notes |
|---|---|---|---|---|
| `BCRYPT_LOG_ROUNDS` | No | `12` | `12` | Higher = slower but safer |
| `SESSION_COOKIE_SECURE` | No | `False` | `True` | Set True in production (HTTPS) |
| `SESSION_COOKIE_HTTPONLY` | No | `True` | `True` | Always True |
| `SESSION_COOKIE_SAMESITE` | No | `Lax` | `Lax` | CSRF protection |

## Rate Limiting

| Variable | Required | Default | Example |
|---|---|---|---|
| `RATELIMIT_DEFAULT` | No | `200 per day;50 per hour` | `200 per day;50 per hour` |
| `RATELIMIT_STORAGE_URL` | No | `memory://` | `memory://` |

## Application Settings

| Variable | Required | Default | Example | Notes |
|---|---|---|---|---|
| `APP_NAME` | No | `ITSA Platform` | `ITSA Platform` | |
| `FRONTEND_URL` | No | `http://localhost:5000` | `https://itsa.onrender.com` | Used in email links |
| `FEEDBACK_WINDOW_HOURS` | No | `24` | `24` | Hours after event end to allow feedback |

## Gamification Points

| Variable | Required | Default |
|---|---|---|
| `POINTS_ATTENDANCE` | No | `10` |
| `POINTS_REGISTRATION` | No | `3` |
| `POINTS_FEEDBACK` | No | `5` |
| `POINTS_POST` | No | `2` |
| `POINTS_COMMENT` | No | `1` |
| `POINTS_VOLUNTEER` | No | `15` |

---

## .env.example Content

```bash
# Flask Core
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change-this-to-a-long-random-secret-minimum-32-chars
PORT=5000

# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/itsa_platform
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=itsa_platform
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
AI_MAX_TOKENS=1024

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=True
EMAIL_FROM_NAME=ITSA Platform
EMAIL_FROM_ADDRESS=noreply@itsa.example.com

# Uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=104857600

# Security
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# App
APP_NAME=ITSA Platform
FRONTEND_URL=http://localhost:5000
FEEDBACK_WINDOW_HOURS=24

# Points
POINTS_ATTENDANCE=10
POINTS_REGISTRATION=3
POINTS_FEEDBACK=5
POINTS_POST=2
POINTS_COMMENT=1
POINTS_VOLUNTEER=15
```
