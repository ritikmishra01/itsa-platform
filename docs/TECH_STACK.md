# Verified Technology Stack — ITSA Platform

## 1. Frontend Technologies

| Technology | Specification | Purpose in Platform |
| :--- | :--- | :--- |
| **HTML5** | Semantic Standard | Base document layout, accessible forms, data bindings |
| **CSS3** | Custom (`static/css/main.css`) | Custom design tokens, responsive cards, typography, animations |
| **JavaScript** | ES6+ (`static/js/main.js`) | Asynchronous fetch requests (`apiCall`), modal controls, dynamic DOM |
| **Bootstrap** | Version 5.3.3 (CDN) | Responsive grid, components, buttons, dropdowns, navigation bars |
| **Bootstrap Icons** | Version 1.11.3 (CDN) | Vector UI icons for event categories, roles, points, and status |
| **Chart.js** | Version 4.4.1 (CDN) | Real-time analytics charts on Admin and Coordinator dashboards |
| **html5-qrcode** | Version 2.3.8 (CDN) | Browser camera-based QR scanner for live event attendance verification |
| **Google Fonts** | Inter & JetBrains Mono | Clean user interface typography and monospace ticket/certificate IDs |

---

## 2. Backend Technologies

| Technology | Specification | Purpose in Platform |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Core programming language |
| **Flask** | >=3.0.0 | Core WSGI application framework, routing, templating, request dispatching |
| **Flask-SQLAlchemy**| >=3.1.0 | ORM integration with Flask |
| **SQLAlchemy** | >=2.0.0 | High-performance ORM, relational mapping, and pooling |
| **Flask-Login** | >=0.6.3 | Session management, remember-me cookies, user authentication state |
| **Flask-Migrate** | >=4.0.7 | Schema version control via Alembic |
| **Flask-CORS** | >=4.0.0 | Cross-Origin Resource Sharing handling for REST API endpoints |
| **Flask-Limiter** | >=3.5.0 | Rate limiting for authentication and AI generation endpoints |
| **Werkzeug** | >=3.0.0 | Cryptographic password hashing (`pbkdf2:sha256`) and secure file names |
| **python-dotenv** | >=1.0.0 | Loads `.env` file into runtime process environment |
| **Gunicorn** | >=21.2.0 | Production WSGI HTTP server with multi-worker concurrency |

---

## 3. Database Technologies

| Technology | Environment | Purpose in Platform |
| :--- | :--- | :--- |
| **SQLite 3** | Local Development | Zero-configuration, file-based relational database (`DATABASE_URL=sqlite:///itsa_platform.db`) |
| **PostgreSQL** | Render Production | Production managed relational database (`DATABASE_URL=postgresql+psycopg2://...`) |
| **psycopg2-binary**| Production Driver | High-performance PostgreSQL database adapter for Python |
| **PyMySQL** | MySQL Support (Optional) | Optional MySQL driver for enterprise campus deployments |

---

## 4. Artificial Intelligence & Machine Learning

| Technology | Package | Purpose in Platform |
| :--- | :--- | :--- |
| **Google Gemini API** | `google-generativeai` >=0.7.0 | Gemini 2.0 Flash for ITSA Chatbot, event description generation, announcement drafting, and sentiment analysis |
| **Scikit-learn** | `scikit-learn` >=1.4.0 | TF-IDF Vectorization and Cosine Similarity for personalized event recommendations |
| **NumPy & Pandas** | `numpy` >=1.26.0, `pandas` >=2.2.0 | Matrix operations, analytics aggregation, and feature processing |
| **Joblib** | `joblib` >=1.3.0 | ML model serialization and persistence |

---

## 5. Media, Documents & Utilities

| Technology | Package | Purpose in Platform |
| :--- | :--- | :--- |
| **QRCode Engine** | `qrcode[pil]` >=7.4.2 | Dynamic QR code generation for event registration tickets |
| **Pillow (PIL)** | `Pillow` >=10.0.0 | Image processing, thumbnail generation, and poster validation |
| **ReportLab** | `reportlab` >=4.0.0 | PDF document generation for official event certificates |
| **SMTP / smtplib** | Python Standard Library | Transactional email dispatch for registrations and announcements |

---

## 6. Testing & Quality Assurance

| Technology | Package | Purpose |
| :--- | :--- | :--- |
| **pytest** | >=8.0.0 | Modern Python test framework |
| **pytest-flask** | >=1.3.0 | Flask application fixture integration |
| **pytest-cov** | >=4.1.0 | Test coverage measurement and reporting |

---

## 7. Cloud Infrastructure & DevOps

| Platform / Tool | Role |
| :--- | :--- |
| **Git & GitHub** | Distributed version control and remote code repository (`ritikmishra01/itsa-platform`) |
| **Render Web Services** | Cloud hosting platform running Gunicorn on Linux container |
| **Render PostgreSQL** | Fully managed cloud database with SSL and automated backups |