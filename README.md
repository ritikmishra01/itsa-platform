# ITSA AI-Powered Event Management & Student Engagement Platform

> **The official production-ready digital platform for Information Technology Students' Association (ITSA)**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-orange?logo=mysql)](https://mysql.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-purple?logo=google)](https://ai.google.dev)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-blueviolet?logo=bootstrap)](https://getbootstrap.com)
[![Gunicorn](https://img.shields.io/badge/WSGI-Gunicorn-green?logo=gunicorn)](https://gunicorn.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 1. Project Overview

ITSA Platform is a **full-stack, production-ready web application** designed to unify student engagement, technical events, attendance tracking, and social interactions within the Information Technology department:

- **Event Lifecycle & Registrations**: Full scheduling, RSVP management, capacity enforcement, and registration deadlines.
- **Digital Ticketing & QR Attendance**: Fast check-in scanned by coordinators with duplicate protection.
- **ReportLab Certificate Engine**: Automated PDF generation with public QR verification URLs.
- **Social Community Hub**: Multi-media posts, threaded comments, reactions, hashtag filtering, and admin moderation.
- **Gamification & Engagement**: ITSA Points system, real-time leaderboard, and engagement scoring.
- **Google Gemini 2.0 Flash AI**: Integrated conversational AI assistant, event recommendation engine, and content summaries.
- **Admin Control Center**: Unified management of events, users, coordinators, content moderation, broadcast messaging, and analytics.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+, Flask 3.x, Flask-Login, Flask-SQLAlchemy | Modular backend & RESTful APIs |
| **Database** | MySQL 8.x / PostgreSQL | 30 relational tables with foreign keys and ACID transactions |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js | Modern responsive user interface |
| **AI / Machine Learning** | Google Gemini 2.0 Flash SDK, Scikit-learn, Pandas, NumPy | AI Chatbot, ML Recommendation Engine & Analytics |
| **Ticketing & Certificates** | `qrcode[pil]`, `reportlab`, `html5-qrcode` | Digital tickets, scanner, and verified PDF certificates |
| **WSGI Server & Hosting** | Gunicorn, Render, Linux Containers | Production concurrency & cloud deployment |

---

## 3. Quick Start (Local Development)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/itsa-platform.git
cd itsa-platform

# 2. Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure Environment
cp .env.example .env
# Set your DATABASE_URL, GEMINI_API_KEY, and SECRET_KEY in .env

# 5. Initialize Database & Seed Development Data
python scripts/seed_db.py

# 6. Start Development Server
python run.py
```

Visit `http://localhost:5000` in your web browser.

---

## 4. Production Cloud Deployment (Render)

### Architecture
```
GitHub Repository ➔ Render Web Service ➔ Gunicorn (4 Workers) ➔ Cloud MySQL / PostgreSQL
                                                              ➔ Render Persistent Disk (/var/data/uploads)
                                                              ➔ Google Gemini API
```

### Environment Variables
Configure the following in the Render dashboard:
- `FLASK_ENV`: `production`
- `FLASK_DEBUG`: `False`
- `SECRET_KEY`: `<cryptographic-random-string>`
- `DATABASE_URL`: `mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>`
- `UPLOAD_FOLDER`: `/var/data/uploads`
- `GEMINI_API_KEY`: `<your-gemini-api-key>`
- `FRONTEND_URL`: `https://your-service.onrender.com`
- `ADMIN_EMAIL`: `admin@itsa.edu`
- `ADMIN_PASSWORD`: `<your-secure-admin-password>`

### Render Build & Start Commands
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Pre-Deploy Command**: `python scripts/init_prod_admin.py`
- **Start Command**: `gunicorn "run:app" --workers 4 --bind 0.0.0.0:$PORT --timeout 120`
- **Health Check Endpoint**: `/health`

---

## 5. User Roles & Security

1. **Student (`STUDENT`)**: Event discovery, registrations, QR tickets, certificates, community posts, leaderboard, and AI assistant.
2. **Coordinator (`COORDINATOR`)**: Assigned event management, live camera QR attendance scanner, registrations oversight, and feedback reports.
3. **Administrator (`ADMIN`)**: Full platform control, user management, coordinator provisioning, content moderation, broadcast messaging, and exportable analytics.

---

## 6. Automated Testing

Run the complete test suite:
```bash
pytest
```

---

## 7. Documentation Directory

Detailed specifications are available in [`docs/`](docs/):
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) &mdash; Comprehensive Render deployment manual
- [`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md) &mdash; Production launch verification checklist
- [`docs/BUG_FIX_REPORT.md`](docs/BUG_FIX_REPORT.md) &mdash; Audit & fix report
- [`docs/DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md) &mdash; Complete 30-table relational database design
- [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) &mdash; RESTful API specifications
- [`docs/QR_ATTENDANCE.md`](docs/QR_ATTENDANCE.md) &mdash; QR ticketing & scanning architecture

---

## License

This project is licensed under the [MIT License](LICENSE).
