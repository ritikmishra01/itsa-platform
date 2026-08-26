# ITSA Platform: Production Deployment & Architecture Manual

**System**: Information Technology Students' Association (ITSA) AI-Powered Event Management & Student Engagement Platform  
**Target Cloud Platform**: Render (Web Service + Managed PostgreSQL + Persistent Disk Storage)  
**Database**:
- **Local Development**: SQLite (`itsa_platform.db`)
- **Production Cloud**: PostgreSQL (`DATABASE_URL` via Render Managed Database)
**WSGI Application Server**: Gunicorn  
**AI Integration**: Google Gemini 2.0 Flash API  

---

## 1. System Architecture Overview

```
                        [ Internet / Students / Coordinators / Admins ]
                                               │
                                               ▼ (HTTPS / SSL)
                                   ┌──────────────────────┐
                                   │ Render Cloud Gateway │
                                   │  (Reverse Proxy /    │
                                   │   SSL Termination)   │
                                   └──────────┬───────────┘
                                              │
                                              ▼
                        ┌──────────────────────────────────────────┐
                        │   Render Web Service (Linux Container)    │
                        │                                          │
                        │   ┌──────────────────────────────────┐   │
                        │   │ Gunicorn WSGI Server (4 Workers) │   │
                        │   └────────────────┬─────────────────┘   │
                        │                    │                     │
                        │   ┌────────────────▼─────────────────┐   │
                        │   │ Flask 3.0 Application Factory    │   │
                        │   │  - Auth (Flask-Login / RBAC)     │   │
                        │   │  - Events & Registrations        │   │
                        │   │  - QR Scanner & Attendance       │   │
                        │   │  - ReportLab PDF Certificates    │   │
                        │   │  - Social Community Feed         │   │
                        │   │  - Scikit-learn ML Engine        │   │
                        │   └────────────────┬─────────────────┘   │
                        └────────────┬───────┴────────┬────────────┘
                                     │                │
            ┌────────────────────────┼────────────────┼────────────────────────┐
            │                        │                │                        │
            ▼                        ▼                ▼                        ▼
 ┌──────────────────────┐ ┌───────────────────┐ ┌─────────────┐ ┌──────────────────────┐
 │ Render PostgreSQL    │ │ Persistent Disk   │ │ Google      │ │ SMTP Email Gateway   │
 │ Database             │ │ (/var/data/uploads│ │ Gemini 2.0  │ │ (Gmail / SendGrid)   │
 │ - 30 relational tbls │ │ - Posters/Tickets │ │ Flash API   │ │ - Registration alert │
 │ - ACID Transactions  │ │ - Certs/Gallery)  │ │ - AI Chat   │ │ - Attendance notice  │
 └──────────────────────┘ └───────────────────┘ └─────────────┘ └──────────────────────┘
```

---

## 2. Server & Runtime Specification

| Parameter | Production Value | Description |
| :--- | :--- | :--- |
| **Python Runtime** | `3.11.8` / `3.13` | Modern CPython engine |
| **WSGI Server** | `Gunicorn 21.2.0+` | Multi-worker prefork WSGI container |
| **Gunicorn Command** | `gunicorn "run:app" --workers 4 --bind 0.0.0.0:$PORT --timeout 120` | High-throughput concurrent request worker pool |
| **Pre-Deploy Command** | `python scripts/init_prod_admin.py` | Idempotent schema verification, category seeding, and initial administrator bootstrap |
| **Health Check Path** | `/health` | Monitored by Render orchestrator (HTTP 200) |
| **Persistent Storage** | `/var/data/uploads` (5GB Render Disk) | Stores generated QR tickets, certificates, event banners, and gallery media |

---

## 3. Environment Variables Reference

| Variable | Required | Default / Format | Description |
| :--- | :---: | :--- | :--- |
| `FLASK_ENV` | **Yes** | `production` | Enables production security & disables debugging |
| `FLASK_DEBUG` | **Yes** | `False` | Disables debug interactive traceback |
| `SECRET_KEY` | **Yes** | 64-char hex / auto-generated | Used for cryptographic session cookie signing |
| `DATABASE_URL` | **Yes** | `mysql+pymysql://user:pass@host:port/dbname` or `postgresql://...` | Cloud database connection string |
| `GEMINI_API_KEY` | **Yes** | `AIzaSy...` | Google Generative AI API authentication key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model variant |
| `UPLOAD_FOLDER` | **Yes** | `/var/data/uploads` | Path to persistent storage disk mount |
| `FRONTEND_URL` | **Yes** | `https://itsa-platform.onrender.com` | Base public URL for certificate verification links |
| `ADMIN_EMAIL` | No | `admin@itsa.edu` | Initial production administrator email |
| `ADMIN_PASSWORD` | **Yes** | Secure string | Initial administrator password |
| `ADMIN_NAME` | No | `ITSA System Administrator` | Initial administrator full name |
| `SMTP_HOST` | No | `smtp.gmail.com` | SMTP host for email alerts |
| `SMTP_PORT` | No | `587` | SMTP port |
| `SMTP_USERNAME` | No | `email@example.com` | SMTP authentication user |
| `SMTP_PASSWORD` | No | `app_password` | SMTP app password |

---

## 4. Step-by-Step Render Deployment Guide

### Step 1: Push Repository to GitHub
Ensure `.env` is not committed:
```bash
git add .
git commit -m "feat(prod): prepare ITSA platform for production deployment"
git push origin main
```

### Step 2: Create a Cloud Database
1. Create a MySQL or PostgreSQL database instance (e.g. Aiven, PlanetScale, Railway, AWS RDS, or Render Managed PostgreSQL).
2. Copy the Connection URI (e.g., `mysql+pymysql://avnadmin:password@mysql-itsa.aivencloud.com:12345/defaultdb?ssl-mode=REQUIRED`).

### Step 3: Create Render Web Service
1. In the **Render Dashboard**, click **New +** &rarr; **Web Service**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name**: `itsa-platform`
   - **Region**: `Oregon (US West)` or nearest region.
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn "run:app" --workers 4 --bind 0.0.0.0:$PORT --timeout 120`
   - **Health Check Path**: `/health`

### Step 4: Attach Persistent Disk (For Media & Certificates)
1. Under the **Disks** section in Render, click **Add Disk**.
2. **Name**: `itsa-uploads`
3. **Mount Path**: `/var/data/uploads`
4. **Size**: `5 GB` (or larger based on media requirements).

### Step 5: Configure Environment Variables
In the **Environment** tab, set all required variables:
- `FLASK_ENV` = `production`
- `FLASK_DEBUG` = `False`
- `SECRET_KEY` = (Click Generate)
- `DATABASE_URL` = `<your-cloud-db-connection-string>`
- `UPLOAD_FOLDER` = `/var/data/uploads`
- `GEMINI_API_KEY` = `<your-google-gemini-api-key>`
- `FRONTEND_URL` = `https://itsa-platform.onrender.com`
- `ADMIN_EMAIL` = `admin@itsa.edu`
- `ADMIN_PASSWORD` = `<secure-production-admin-password>`
- `ADMIN_NAME` = `ITSA Administrator`

### Step 6: Trigger Deploy & Run Pre-Deploy Seed
Click **Deploy Latest Commit**. Render will build the image, mount the persistent storage, run `scripts/init_prod_admin.py` to initialize essential categories, and start Gunicorn workers.

---

## 5. Security & Verification Checks

### 1. Zero Debug Exposure
All production errors (400, 401, 403, 404, 429, 500) render custom Bootstrap error templates without technical stack traces. Technical errors are logged to Gunicorn's stderr stream.

### 2. Cookie Security
- `SESSION_COOKIE_HTTPONLY = True`: Blocks JavaScript access to session identifiers (Mitigates XSS).
- `SESSION_COOKIE_SAMESITE = 'Lax'`: Mitigates Cross-Site Request Forgery (CSRF).
- `SESSION_COOKIE_SECURE = True`: Enforces transmission exclusively over HTTPS in production.

### 3. HTTP Security & Anti-Cache Headers
Every response includes:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`
- `Pragma: no-cache`
- `Expires: 0`

---

## 6. Troubleshooting & Rollback Procedures

### Health Check Failure
- If `/health` returns non-200, check the Render deployment log.
- Verify `DATABASE_URL` connectivity and credentials.

### File Upload Permission Issues
- Ensure `UPLOAD_FOLDER` exists and has read/write permissions for the WSGI process (`chmod -R 775 /var/data/uploads`).

### Rollback Process
1. In the **Render Dashboard**, go to **Deploys**.
2. Find the previous stable build commit and click **Rollback to this deploy**.
