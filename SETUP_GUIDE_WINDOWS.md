# ITSA Platform — Windows Setup Guide

> **Generated:** 2026-11-11 | **Python:** 3.14.0 | **Status:** ✅ Fully Verified

---

## 🖥️ Environment Summary

| Component         | Details                                                                 |
|:------------------|:------------------------------------------------------------------------|
| **OS**            | Windows (PowerShell)                                                    |
| **Python**        | 3.14.0 — `C:\Users\tiwar\AppData\Local\Programs\Python\Python314\`     |
| **Git**           | 2.55.0 — `C:\Program Files\Git\cmd\git.exe`                            |
| **Project Path**  | `C:\Users\tiwar\Downloads\itsa-platform (2)\itsa-platform`             |
| **Database**      | SQLite (local dev) — `instance\itsa_platform.db`                       |
| **Test Results**  | ✅ 72 passed / 0 failed                                                  |

---

## 🚀 Daily Startup (Every Time You Want to Run the App)

Open **PowerShell** and run these three commands:

```powershell
# 1. Navigate to the project folder
cd "C:\Users\tiwar\Downloads\itsa-platform (2)\itsa-platform"

# 2. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 3. Start the Flask development server
python run.py
```

Then open your browser at: **http://localhost:5000/**

Press `Ctrl+C` in the terminal to stop the server.

---

## 🔑 Standard Demo Login Accounts

| Role | Email | Password | Full Name / Description |
|:---|:---|:---|:---|
| **Administrator** | `admin@itsa.edu` | `SecureLocalAdmin#2026` | Prof. Rajeshwari Natarajan (Full Superuser Access) |
| **Coordinator 1** | `coord1@itsa.edu` | `Coord#2026` | Prof. Rajesh Kulkarni (Lead: TechFest 2026, IT Dept) |
| **Coordinator 2** | `coord2@itsa.edu` | `Coord#2026` | Dr. Sunita Patil (Lead: CodeSprint 2026, CE Dept) |
| **Coordinator 3** | `coord3@itsa.edu` | `Coord#2026` | Prof. Amit Deshmukh (Lead: AI Masterclass, DS Dept) |
| **Coordinator 4** | `coord4@itsa.edu` | `Coord#2026` | Dr. Neha Sharma (Lead: WebDev Bootcamp, IT Dept) |
| **Coordinator 5** | `coord5@itsa.edu` | `Coord#2026` | Prof. Vikram Joshi (Lead: Cloud & DevOps, AI Dept) |
| **Student 1** | `student1@itsa.edu` | `Student@12345` | Aarav Sharma (Year 3, Information Technology) |
| **Student 2** | `student2@itsa.edu` | `Student@12345` | Priya Patel (Year 2, Computer Engineering) |
| **Student 3** | `student3@itsa.edu` | `Student@12345` | Rohan Kulkarni (Year 4, Data Science) |
| **Student 4** | `student4@itsa.edu` | `Student@12345` | Ananya Deshmukh (Year 3, Information Technology) |
| **Student 5** | `student5@itsa.edu` | `Student@12345` | Aditya Verma (Year 1, AI & Data Science) |

---

## 🧪 Running Tests

```powershell
cd "C:\Users\tiwar\Downloads\itsa-platform (2)\itsa-platform"
.\venv\Scripts\Activate.ps1
pytest -q
```

**Expected result:** `72 passed` (the documented baseline of 36 was expanded by the project author)

For verbose output with coverage:
```powershell
pytest -v --cov=app --cov-report=term-missing
```

---

## 📂 Project Structure Overview

```
itsa-platform/
├── app/                    # Flask application package
│   ├── __init__.py         # Application factory (create_app)
│   ├── config.py           # DevelopmentConfig / TestingConfig / ProductionConfig
│   ├── extensions.py       # db, login_manager, migrate, cors, limiter
│   ├── models/             # 30 SQLAlchemy models (User, Event, Ticket, etc.)
│   ├── routes/             # Blueprints: auth, admin, events, attendance, ai, ...
│   ├── services/           # Business logic layer (ai_service, cert_service, ...)
│   ├── templates/          # Jinja2 HTML templates (Bootstrap 5.3)
│   └── static/             # CSS, JS, images, vendor (Chart.js, etc.)
├── scripts/                # Utility scripts
│   ├── seed_demo_data.py   # Safe idempotent demo data seeder (tagged @example.test)
│   └── init_prod_admin.py  # Production admin initialiser (Render only)
├── tests/                  # 72-test pytest suite (all use in-memory SQLite)
├── instance/
│   └── itsa_platform.db    # SQLite database (DO NOT DELETE)
├── uploads/                # User-uploaded files (tickets, certificates, etc.)
├── venv/                   # Python 3.14 virtual environment
├── .env                    # Environment variables (NOT committed to git)
├── .env.example            # Template for .env
├── run.py                  # Application entry point
└── requirements.txt        # Python dependencies
```

---

## ⚙️ Environment Variables (`.env`)

The `.env` file is already configured for local development. Key settings:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=itsa_super_secret_development_key_change_in_prod_2026
PORT=5000
DATABASE_URL=sqlite:///itsa_platform.db

# Add your Gemini API key here to enable AI features:
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
```

> **To enable AI features** (chatbot, description generator, sentiment analysis):
> 1. Get a free API key at https://aistudio.google.com/apikey
> 2. Open `.env` and set: `GEMINI_API_KEY=your_actual_key_here`
> 3. Restart the server

---

## 🗄️ Database Management

### View current database stats
```powershell
cd "C:\Users\tiwar\Downloads\itsa-platform (2)\itsa-platform"
.\venv\Scripts\Activate.ps1
python -c "
from app import create_app, db
from app.models.user import User
from app.models.event import Event
app = create_app('development')
with app.app_context():
    print(f'Users: {User.query.count()}')
    print(f'Events: {Event.query.count()}')
"
```

### Add optional demo data (safe — only adds `@example.test` records)
```powershell
# Inspect what it will create first (read the script):
# cat scripts\seed_demo_data.py | Select-String "DEMO_"

# Run it (idempotent — safe to run multiple times):
python scripts\seed_demo_data.py

# Remove only demo data when done:
python scripts\seed_demo_data.py --clean
```

> ⚠️ The seeder only creates/removes records tagged with `@example.test`. It **never** touches real data.

---

## 🛠️ Resolved Issues & Functional Status

All reported platform issues have been thoroughly debugged, repaired, and regression-tested:

### 1. Admin Event Creation
- **Root Cause:** In the redesigned `app/templates/admin/events.html`, the "Create Event" button lacked Bootstrap modal trigger attributes, and `#createEventModal` markup was missing from the template.
- **Fix:** Restored complete `#createEventModal` with full form inputs (title, category, venue, start/end/deadline datetimes, max participants, poster upload, tags) and integrated Gemini AI event description generator (`#btnAIGenDesc`). Wired up asynchronous submission in `app/static/js/admin-events.js`.

### 2. Admin User Provisioning (Student & Coordinator)
- **Root Cause:** Endpoint mismatch between `/api/v1/admin/coordinators` and `/api/v1/admin/users/coordinator`, along with missing error diagnostics for password complexity requirements.
- **Fix:** Added endpoint route aliases `@admin_bp.route('/users/coordinator')` and `@admin_bp.route('/users/coordinators')` in `app/routes/admin.py`. Enhanced `app/templates/admin/users.html` and `app/templates/admin/coordinators.html` with explicit password hints (`Min 8 chars with uppercase, lowercase, and digit`), loading indicators, and informative toast error handling. Verified both student and coordinator accounts can be provisioned and log in immediately.

### 3. Coordinator QR Attendance Camera
- **Root Cause:** `Html5Qrcode` was passed an empty `{}` fallback object which threw an uncaught error (`0 keys`). Additionally, camera constraint detection defaulted to mobile `facingMode: "environment"` which fails on Windows laptops lacking rear cameras.
- **Fix:** Implemented resilient candidate selection in `app/templates/coordinator/scanner.html`:
  1. Requests direct camera permission via `navigator.mediaDevices.getUserMedia({ video: true })` on button click before querying camera IDs.
  2. Queries available camera IDs and prioritizes user selection or primary laptop webcam device ID.
  3. Provides fallbacks for `{ facingMode: "user" }` and `{ facingMode: "environment" }` without empty object exceptions.
  4. Provides clear contextual status messages for permission denial, camera in use by other apps, and devices without cameras, while maintaining ticket image upload and manual code entry fallbacks.

---

## 🔧 Troubleshooting

### PowerShell execution policy error
If `.\venv\Scripts\Activate.ps1` fails with a policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 5000 already in use
```powershell
# Find the process using port 5000
netstat -ano | findstr :5000

# Kill it (replace PID with the number shown)
taskkill /PID <PID> /F
```

### App crashes on startup — check logs
```powershell
cat logs\app.log | Select-Object -Last 50
```

### Reinstall virtual environment from scratch
```powershell
cd "C:\Users\tiwar\Downloads\itsa-platform (2)\itsa-platform"

# Remove old venv
Remove-Item -Recurse -Force venv

# Create new venv with Python 3.14
C:\Users\tiwar\AppData\Local\Programs\Python\Python314\python.exe -m venv venv

# Activate and install
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### "No module named X" error
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🌐 Application URLs

| URL                                        | Description                     |
|:-------------------------------------------|:--------------------------------|
| http://localhost:5000/                     | Public homepage / redirect      |
| http://localhost:5000/login                | Login page                      |
| http://localhost:5000/register             | Student registration            |
| http://localhost:5000/events               | Events listing (public)         |
| http://localhost:5000/events/`<id>`        | Event detail page               |
| http://localhost:5000/logout               | Logout                          |
| http://localhost:5000/health               | Health check (HTTP 200)         |
| http://localhost:5000/api/v1/auth/login    | REST API — login endpoint       |
| http://localhost:5000/api/v1/events/       | REST API — events               |
| http://localhost:5000/api/v1/ai/chat       | REST API — Gemini AI chatbot    |
| http://localhost:5000/certificates/verify  | Certificate verification        |

---

## 📦 Installed Dependencies (Python 3.14 — Nov 2026)

| Package              | Version  | Purpose                        |
|:---------------------|:---------|:-------------------------------|
| Flask                | 3.1.3    | Web framework                  |
| Flask-SQLAlchemy     | 3.1.1    | ORM integration                |
| Flask-Login          | 0.6.3    | Session authentication         |
| Flask-Migrate        | 4.1.0    | DB schema migrations (Alembic) |
| Flask-CORS           | 6.0.5    | Cross-origin resource sharing  |
| Flask-Limiter        | 4.1.1    | Rate limiting                  |
| SQLAlchemy           | 2.1.8    | Database ORM                   |
| psycopg2-binary      | 2.9.13   | PostgreSQL adapter             |
| PyMySQL              | 1.2.4    | MySQL adapter                  |
| google-genai         | 3.1.0    | Google Gemini AI (modern SDK)  |
| google-generativeai  | 0.8.6    | Google Gemini AI (legacy SDK)  |
| scikit-learn         | 1.9.1    | ML recommendation engine       |
| pandas               | 3.1.1    | Data processing                |
| numpy                | 2.5.4    | Numerical computing            |
| Pillow               | 13.0.0   | Image processing               |
| qrcode               | 8.2      | QR code generation             |
| reportlab            | 5.1.0    | PDF certificate generation     |
| gunicorn             | 27.0.0   | Production WSGI server         |
| pytest               | 9.2.0    | Testing framework              |
| pytest-flask         | 1.3.0    | Flask test utilities           |
| pytest-cov           | 7.1.0    | Test coverage                  |

---

## ⚠️ Known Non-Breaking Warnings

These warnings appear in tests and during startup — they are **informational only** and do not affect functionality:

1. **`datetime.datetime.utcnow()` is deprecated** — Python 3.14 recommends timezone-aware datetimes. The app works correctly; this is a future-proofing notice.
2. **`google.generativeai` package deprecated** — The app already uses the modern `google.genai` SDK as primary; the legacy SDK is a fallback. No action needed.
3. **`Query.get()` legacy SQLAlchemy warning** — Cosmetic only; functionality is unaffected.

---

## 🏭 Production Notes (Render Cloud — Not Needed Locally)

The production deployment uses:
- **Start command:** `gunicorn "run:app" --workers 4 --bind 0.0.0.0:$PORT --timeout 120`
- **Database:** PostgreSQL (set `DATABASE_URL` to Render PostgreSQL URL)
- **Pre-deploy:** `python scripts/init_prod_admin.py`

Do **not** set `FLASK_ENV=production` locally — it requires a PostgreSQL URL and disables SQLite.

---

*Setup guide generated by Antigravity on 2026-11-11. Project: ITSA AI-Powered Event Management & Student Engagement Platform.*
