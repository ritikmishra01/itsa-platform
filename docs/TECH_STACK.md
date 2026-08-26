# Technology Stack -- ITSA Platform

## Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Primary programming language |
| Flask | 3.x | Web framework - routes, templating, WSGI |
| Flask-SQLAlchemy | 3.x | ORM integration with Flask |
| SQLAlchemy | 2.x | ORM for MySQL database interaction |
| Flask-Login | 0.6.x | Session-based user authentication |
| Flask-Migrate | 4.x | Database migrations via Alembic |
| Flask-CORS | 4.x | CORS headers for API responses |
| Flask-Limiter | 3.x | Rate limiting for API and AI endpoints |
| Werkzeug | 3.x | Password hashing, secure_filename |
| PyMySQL | 1.x | Python MySQL driver |
| python-dotenv | 1.x | Load .env into environment variables |
| Gunicorn | 22.x | Production WSGI server |

## Database

| Technology | Version | Purpose |
|---|---|---|
| MySQL | 8.x | Primary relational database |
| InnoDB | -- | Storage engine for transactions and foreign keys |

## Frontend

| Technology | Version | Purpose |
|---|---|---|
| HTML5 | -- | Page structure |
| CSS3 | -- | Styling |
| JavaScript | ES6+ | Client-side interactivity |
| Bootstrap | 5.3 | Responsive UI component library |
| Chart.js | 4.x | Analytics charts and graphs |
| html5-qrcode | 2.x | Browser-based QR code scanning |

## AI and Machine Learning

| Technology | Version | Purpose |
|---|---|---|
| google-generativeai | latest | Google Gemini API Python SDK |
| Scikit-learn | 1.x | ML models for recommendations and prediction |
| Pandas | 2.x | Data manipulation for analytics and ML features |
| NumPy | 1.x | Numerical operations for ML |

## Utilities

| Technology | Purpose |
|---|---|
| qrcode with Pillow | Generate QR code PNG images for tickets |
| Pillow | Image processing and manipulation |
| ReportLab | PDF certificate generation |
| smtplib stdlib | Email sending via SMTP |
| uuid stdlib | UUID generation for ticket and certificate codes |
| joblib | Serialize and deserialize trained ML models |
| OpenCV cv2 | Optional server-side QR code decoding for uploaded images |

## Infrastructure

| Technology | Purpose |
|---|---|
| Git | Version control |
| GitHub | Remote repository hosting |
| Render | Cloud deployment platform |
| PlanetScale or Railway | Free tier MySQL database hosting |

## requirements.txt Content

Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Migrate==4.0.7
Flask-CORS==4.0.1
Flask-Limiter==3.7.0
SQLAlchemy==2.0.31
PyMySQL==1.1.1
Werkzeug==3.0.3
python-dotenv==1.0.1
google-generativeai==0.7.2
scikit-learn==1.5.1
pandas==2.2.2
numpy==1.26.4
qrcode[pil]==7.4.2
Pillow==10.4.0
reportlab==4.2.2
joblib==1.4.2
opencv-python-headless==4.10.0.84
gunicorn==22.0.0
