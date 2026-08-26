import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file from base directory
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'itsa-platform-default-dev-secret-key-2026')
    APP_NAME = os.environ.get('APP_NAME', 'ITSA AI-Powered Platform')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')

    # Database configuration with cloud URL normalization (PostgreSQL / MySQL / SQLite)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('mysql://'):
            database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
        elif database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://') and not database_url.startswith('postgresql+'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    else:
        # Fallback to local SQLite database
        database_url = f"sqlite:///{os.path.join(basedir, 'itsa_platform.db')}"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if database_url.startswith('sqlite:'):
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
