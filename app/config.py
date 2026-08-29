import os
from datetime import timedelta
from dotenv import load_dotenv

from sqlalchemy.engine import make_url

# Load .env file from base directory
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

def normalize_database_url(raw_url=None, base_dir=None):
    """
    Safely normalizes and validates a database connection URL.
    - Trims whitespace and quotes.
    - Strips accidental 'DATABASE_URL=' prefix if pasted into value field.
    - Converts postgres:// and postgresql:// to postgresql+psycopg2://
    - Converts mysql:// to mysql+pymysql://
    - Defaults to local SQLite if empty.
    - Validates syntax without leaking passwords in error messages.
    """
    if base_dir is None:
        base_dir = basedir

    if raw_url is None:
        raw_url = os.environ.get('DATABASE_URL')

    if not raw_url or not str(raw_url).strip():
        # Fallback to local SQLite database
        return f"sqlite:///{os.path.join(base_dir, 'itsa_platform.db')}"

    url = str(raw_url).strip()

    # Strip surrounding quotes if present (e.g. "postgresql://..." or 'postgresql://...')
    while (url.startswith('"') and url.endswith('"')) or (url.startswith("'") and url.endswith("'")):
        url = url[1:-1].strip()

    # Strip accidental environment variable prefix if user pasted "DATABASE_URL=..." into value box
    if url.startswith("DATABASE_URL="):
        url = url[len("DATABASE_URL="):].strip()
        while (url.startswith('"') and url.endswith('"')) or (url.startswith("'") and url.endswith("'")):
            url = url[1:-1].strip()

    # Detect unconfigured placeholder strings
    if url.startswith("<") and url.endswith(">"):
        raise ValueError(
            "DATABASE_URL contains an unconfigured placeholder. "
            "Please configure the actual PostgreSQL connection URL in Render environment settings."
        )

    # Normalize driver scheme prefixes
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    elif url.startswith("mysql://") and not url.startswith("mysql+"):
        url = "mysql+pymysql://" + url[len("mysql://"):]

    # Validate syntax with SQLAlchemy make_url
    try:
        parsed = make_url(url)
        if (parsed.drivername.startswith("postgresql") or parsed.drivername.startswith("mysql")) and not parsed.host:
            raise ValueError("Database connection URL is missing a valid host.")
    except Exception:
        scheme_hint = url.split("://")[0] if "://" in url else "unknown"
        raise ValueError(
            f"Could not parse SQLAlchemy URL for driver '{scheme_hint}'. "
            "Please check that the DATABASE_URL environment variable is formatted correctly."
        ) from None

    return url

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'itsa-platform-default-dev-secret-key-2026')
    APP_NAME = os.environ.get('APP_NAME', 'ITSA AI-Powered Platform')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')

    # Database configuration with cloud URL normalization (PostgreSQL / MySQL / SQLite)
    SQLALCHEMY_DATABASE_URI = normalize_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite:'):
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }

    # Session & Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # File uploads: support explicit absolute path (e.g. Render persistent disk) or relative to basedir
    upload_env = os.environ.get('UPLOAD_FOLDER', 'uploads')
    if os.path.isabs(upload_env):
        UPLOAD_FOLDER = upload_env
    else:
        UPLOAD_FOLDER = os.path.join(basedir, upload_env)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 104857600)) # 100 MB

    # Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', 1024))

    # SMTP / Email
    SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'True').lower() in ('true', '1')
    EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', 'ITSA Platform')
    EMAIL_FROM_ADDRESS = os.environ.get('EMAIL_FROM_ADDRESS', 'noreply@itsa.edu')

    # Points & Rules
    FEEDBACK_WINDOW_HOURS = int(os.environ.get('FEEDBACK_WINDOW_HOURS', 72))
    POINTS_ATTENDANCE = int(os.environ.get('POINTS_ATTENDANCE', 10))
    POINTS_REGISTRATION = int(os.environ.get('POINTS_REGISTRATION', 3))
    POINTS_FEEDBACK = int(os.environ.get('POINTS_FEEDBACK', 5))
    POINTS_POST = int(os.environ.get('POINTS_POST', 2))
    POINTS_COMMENT = int(os.environ.get('POINTS_COMMENT', 1))
    POINTS_VOLUNTEER = int(os.environ.get('POINTS_VOLUNTEER', 15))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
