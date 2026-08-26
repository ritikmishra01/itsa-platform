from app.routes.auth import auth_bp
from app.routes.events import events_bp
from app.routes.attendance import attendance_bp
from app.routes.tickets import tickets_bp
from app.routes.certificates import certs_bp
from app.routes.posts import posts_bp
from app.routes.comments import comments_bp
from app.routes.feedback import feedback_bp
from app.routes.notifications import notifications_bp
from app.routes.gamification import gamification_bp
from app.routes.admin import admin_bp
from app.routes.ai import ai_bp
from app.routes.pages import pages_bp

def register_routes(app):
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(certs_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(gamification_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
