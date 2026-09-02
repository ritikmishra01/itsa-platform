# ITSA AI-Powered Event Management & Student Engagement Platform

> **The official production-ready digital platform for Information Technology Students' Association (ITSA)**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://sqlite.org)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.0_Flash-purple?logo=google)](https://ai.google.dev)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-blueviolet?logo=bootstrap)](https://getbootstrap.com)
[![Gunicorn](https://img.shields.io/badge/WSGI-Gunicorn-green?logo=gunicorn)](https://gunicorn.org)
[![Tests](https://img.shields.io/badge/Tests-36%20Passed-brightgreen)](tests/)

---

## 1. Project Overview

The **ITSA Platform** is an enterprise-grade, full-stack web application designed to unify student engagement, departmental technical events, attendance tracking, and social interactions within the Department of Information Technology:

- **Event Lifecycle & Registrations**: Complete scheduling, RSVP management, capacity enforcement, and registration deadlines.
- **Digital Ticketing & QR Attendance**: Fast venue check-in scanned by coordinators using device cameras with duplicate protection.
- **ReportLab Certificate Engine**: Automated vector PDF generation with public QR verification URLs.
- **Academic Social Community**: Multimedia posts, threaded comments, 5 sentiment reactions, hashtag filtering, and admin moderation.
- **Gamification & Engagement**: ITSA Points system, real-time leaderboard, and AI engagement scoring.
- **Google Gemini 2.0 Flash AI**: Integrated conversational AI assistant, event description generation, and feedback sentiment analysis.
- **Scikit-learn Recommendation Engine**: Content-based TF-IDF event recommendations tailored to student departments and interests.
- **Admin Control Center**: 17 specialized management modules for users, coordinators, events, attendance overrides, moderation, broadcasts, and analytics.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+, Flask 3.x, Flask-Login, Flask-SQLAlchemy | Application factory, routing, and RESTful APIs |
| **Database** | SQLite (Local Dev) / PostgreSQL (Render Production) | 30 relational tables with foreign keys and ACID transactions |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js | Modern, responsive, accessible user interface |
| **AI / Machine Learning** | Google Gemini 2.0 Flash SDK, Scikit-learn, Pandas, NumPy | AI Chatbot, recommendation engine & sentiment analysis |
| **Ticketing & Certificates** | `qrcode[pil]`, `reportlab`, `html5-qrcode` | Digital tickets, camera QR scanner, and verified PDF certificates |
| **Production Server** | Gunicorn, Render Cloud Web Services, Linux Containers | Production concurrency & cloud deployment |

---

## 3. Quick Start (Local Development)

```bash
# 1. Clone the repository
git clone https://github.com/ritikmishra01/itsa-platform.git
cd itsa-platform

# 2. Create and activate virtual environment
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure Environment
# Copy .env.example to .env and configure settings:
cp .env.example .env

# 5. Initialize Database & Seed Demo Data (5 Coordinators & 5 Events)
python scripts/seed_demo_data.py

# 6. Start Development Server
python run.py
```

Open your browser and navigate to: `http://localhost:5000/`

---

## 4. Default Local Accounts

| Role | Email | Password | Full Name / Description |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@itsa.edu` | `SecureLocalAdmin#2026` | ITSA Administrator (Full Superuser Access) |
| **Coordinator 1** | `coord1@itsa.edu` | `Coord#2026` | Prof. Rajesh Kulkarni (Lead: TechFest 2026) |
| **Coordinator 2** | `coord2@itsa.edu` | `Coord#2026` | Dr. Sunita Patil (Lead: CodeSprint 2026) |
| **Coordinator 3** | `coord3@itsa.edu` | `Coord#2026` | Prof. Amit Deshmukh (Lead: AI Masterclass) |
| **Coordinator 4** | `coord4@itsa.edu` | `Coord#2026` | Dr. Neha Sharma (Lead: WebDev Bootcamp) |
| **Coordinator 5** | `coord5@itsa.edu` | `Coord#2026` | Prof. Vikram Joshi (Lead: Cloud & DevOps) |
| **Student** | `rahul@itsa.edu` | `Student@12345` | Rahul Sharma (Computer Science, Year 3) |

---

## 5. Production Cloud Deployment (Render)

### Architecture
```text
GitHub (ritikmishra01/itsa-platform) ➔ Render Web Service ➔ Gunicorn (4 Workers) ➔ Render PostgreSQL
                                                                                ➔ Google Gemini API
```

### Render Configuration (`render.yaml`)
- **Build Command**: `pip install -r requirements.txt`
- **Pre-Deploy Command**: `python scripts/init_prod_admin.py`
- **Start Command**: `gunicorn "run:app" --workers 4 --bind 0.0.0.0:$PORT --timeout 120`
- **Health Check Endpoint**: `/health` (HTTP 200)

---

## 6. Automated Testing

Run the comprehensive 36-test suite:
```bash
pytest -q
```
**Test Results**: 36 Passed / 0 Failed (100% Pass Rate).

---

## 7. Documentation Directory

Comprehensive specifications are maintained in [`docs/`](docs/):

| Document | Purpose |
| :--- | :--- |
| [`docs/FINAL_PROJECT_REPORT.md`](docs/FINAL_PROJECT_REPORT.md) | Master 49-section academic and technical submission report |
| [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) | Problem statement, vision, objectives, and system workflow |
| [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) | Complete Functional (FR) and Non-Functional (NFR) requirements |
| [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md) | Monolithic layered architecture and component diagrams |
| [`docs/TECH_STACK.md`](docs/TECH_STACK.md) | Verified technical stack and library specifications |
| [`docs/FRONTEND.md`](docs/FRONTEND.md) | Frontend templates, CSS/JS structure, and UI component details |
| [`docs/BACKEND.md`](docs/BACKEND.md) | Flask Blueprints, service layer, security, and response envelopes |
| [`docs/DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md) | 30-table relational schema, primary/foreign keys, and constraints |
| [`docs/DATABASE_SETUP.md`](docs/DATABASE_SETUP.md) | SQLite and PostgreSQL setup, connection pooling, and seeding |
| [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) | REST API standards, response formats, and error codes |
| [`docs/AUTHENTICATION.md`](docs/AUTHENTICATION.md) | Flask-Login session management and cookie security |
| [`docs/EVENT_MANAGEMENT.md`](docs/EVENT_MANAGEMENT.md) | Event lifecycles, ticketing, and scheduling |
| [`docs/QR_ATTENDANCE.md`](docs/QR_ATTENDANCE.md) | QR ticketing, camera scanning engine, and duplicate prevention |
| [`docs/CERTIFICATE_SYSTEM.md`](docs/CERTIFICATE_SYSTEM.md) | ReportLab vector PDF certificate engine and verification |
| [`docs/COMMUNITY.md`](docs/COMMUNITY.md) | Academic social feed, reactions, threaded comments, and moderation |
| [`docs/NOTIFICATIONS.md`](docs/NOTIFICATIONS.md) | Dual-channel in-app alerts and multi-target admin broadcasts |
| [`docs/AI_FEATURES.md`](docs/AI_FEATURES.md) | Google Gemini 2.0 Flash and Scikit-learn TF-IDF recommendations |
| [`docs/GAMIFICATION.md`](docs/GAMIFICATION.md) | ITSA points economy, tiers, and real-time student leaderboard |
| [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) | 17-module Admin Control Center operational manual |
| [`docs/COORDINATOR_GUIDE.md`](docs/COORDINATOR_GUIDE.md) | Event Coordinator manual and venue QR scanning guide |
| [`docs/STUDENT_GUIDE.md`](docs/STUDENT_GUIDE.md) | Student user guide for registrations, tickets, and community |
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Step-by-step installation instructions across operating systems |
| [`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md) | Local run commands, accounts, and testing workflows |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Production cloud deployment manual for Render |
| [`docs/TESTING.md`](docs/TESTING.md) | Automated testing structure and test case definitions |
| [`docs/SECURITY.md`](docs/SECURITY.md) | RBAC, rate limiting, anti-caching, and input sanitization |
| [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) | Complete directory tree and annotated file reference |
| [`docs/CHANGELOG.md`](docs/CHANGELOG.md) | Development milestone history and release notes |
| [`docs/BUG_FIX_REPORT.md`](docs/BUG_FIX_REPORT.md) | Comprehensive report of all bug investigations and resolutions |

---

## 8. License

This project is licensed under the [MIT License](LICENSE).