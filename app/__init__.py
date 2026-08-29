import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from app.config import config_by_name
from app.extensions import db, login_manager, migrate, cors, limiter
from app.routes import register_routes

def create_app(config_name=None):
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Dynamic database URL normalization & validation for active runtime environment
    if not app.config.get('TESTING'):
        from app.config import normalize_database_url
        try:
            db_uri = normalize_database_url(os.environ.get('DATABASE_URL'))
            app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
            if db_uri.startswith('sqlite:'):
                app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
            else:
                app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                    "pool_pre_ping": True,
                    "pool_recycle": 300,
                }
        except Exception as e:
            app.logger.critical(f"Database configuration error: {e}")
            raise

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    limiter.init_app(app)

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Configure logging
    if not app.debug or os.environ.get('FLASK_ENV') == 'production':
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('ITSA Platform startup')

    # Ensure Upload Directories Exist (Local or Render Persistent Disk)
    upload_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
    try:
        os.makedirs(upload_dir, exist_ok=True)
        for sub in ['tickets', 'certificates', 'profiles', 'events/posters', 'posts/images', 'posts/videos', 'gallery']:
            os.makedirs(os.path.join(upload_dir, sub), exist_ok=True)
    except Exception as e:
        app.logger.warning(f"Could not create upload directory {upload_dir}: {e}")

    # Active Session Suspension & Account Status Guard
    @app.before_request
    def check_user_session_status():
        from flask_login import current_user, logout_user
        from flask import session, redirect, url_for, flash
        if current_user.is_authenticated:
            if getattr(current_user, 'is_suspended', False) or not getattr(current_user, 'is_active', True):
                logout_user()
                session.clear()
                if request.path.startswith('/api/') or request.is_json:
                    return jsonify({
                        "success": False,
                        "error": {
                            "code": "AUTH_SUSPENDED",
                            "message": "Your account has been suspended. Please contact ITSA administration."
                        }
                    }), 403
                flash("Your account has been suspended. Please contact ITSA administration.", "danger")
                return redirect(url_for('pages.login_page'))

    # Security & No-Cache Headers (Prevents back-button restoring protected views)
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    # Global Template Filters
    @app.template_filter('upload_url')
    def upload_url_filter(file_path):
        if not file_path:
            return '/static/img/placeholder.svg'
        path = str(file_path).replace('\\', '/').lstrip('/')
        if not path.startswith('uploads/'):
            path = f"uploads/{path}"
        return f"/{path}"

    # Global Template Context Processor
    @app.context_processor
    def inject_global_vars():
        from flask_login import current_user
        from app.models.notification import Notification
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return {
            'app_name': app.config.get('APP_NAME', 'ITSA Platform'),
            'now': datetime.utcnow(),
            'unread_notifications_count': unread_count
        }

    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": {"code": "SYS_BAD_REQUEST", "message": "Bad request parameters."}}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": {"code": "SYS_UNAUTHORIZED", "message": "Authentication required."}}), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": {"code": "SYS_FORBIDDEN", "message": "Access forbidden."}}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": {"code": "SYS_NOT_FOUND", "message": "API endpoint not found."}}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def ratelimit_handler(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded. Please try again later."}}), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Server Error: {error}")
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "error": {"code": "SYS_INTERNAL_ERROR", "message": "An internal error occurred."}}), 500
        return render_template('errors/500.html'), 500

    # Register Blueprints
    register_routes(app)

    return app
