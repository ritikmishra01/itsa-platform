from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
from flask_login import current_user
from app.utils.responses import error_response

def _is_api_request():
    return request.path.startswith('/api/') or request.is_json or request.accept_mimetypes.best == 'application/json'

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if _is_api_request():
                return error_response("AUTH_NOT_AUTHENTICATED", "Authentication required", 401)
            flash("Please login to access the admin area.", "warning")
            return redirect(url_for('pages.login_page'))

        if current_user.role != 'ADMIN':
            if _is_api_request():
                return error_response("AUTH_INSUFFICIENT_ROLE", "Admin privilege required", 403)
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for('pages.home'))
        return f(*args, **kwargs)
    return decorated


def coordinator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if _is_api_request():
                return error_response("AUTH_NOT_AUTHENTICATED", "Authentication required", 401)
            flash("Please login to access this area.", "warning")
            return redirect(url_for('pages.login_page'))

        if current_user.role not in ('COORDINATOR', 'ADMIN'):
            if _is_api_request():
                return error_response("AUTH_INSUFFICIENT_ROLE", "Coordinator or Admin privilege required", 403)
            flash("Access denied. Coordinator privileges required.", "danger")
            return redirect(url_for('pages.home'))
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if _is_api_request():
                return error_response("AUTH_NOT_AUTHENTICATED", "Authentication required", 401)
            flash("Please login to access this area.", "warning")
            return redirect(url_for('pages.login_page'))

        if current_user.role != 'STUDENT':
            if _is_api_request():
                return error_response("AUTH_INSUFFICIENT_ROLE", "Student access only", 403)
            flash("Access restricted to students.", "warning")
            return redirect(url_for('pages.home'))
        return f(*args, **kwargs)
    return decorated
