from flask import Blueprint, request, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app.utils.responses import success_response, error_response
from app.utils.file_utils import save_uploaded_file, ALLOWED_IMAGE_EXTENSIONS

auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() if request.is_json else request.form.to_dict()
    if not data:
        return error_response("AUTH_VALIDATION_ERROR", "Request data required.", 400)

    try:
        user = AuthService.register_student(
            email=data.get('email'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            student_id=data.get('student_id'),
            department=data.get('department'),
            year_of_study=data.get('year_of_study'),
            phone=data.get('phone'),
            bio=data.get('bio')
        )
        login_user(user, remember=True)
        return success_response(user.to_dict(), "Registration successful.", 201)
    except ValueError as e:
        return error_response("AUTH_VALIDATION_ERROR", str(e), 400)
    except Exception as e:
        return error_response("SYS_ERROR", f"Registration error: {str(e)}", 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() if request.is_json else request.form.to_dict()
    if not data:
        return error_response("AUTH_VALIDATION_ERROR", "Email and password required.", 400)

    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False) in (True, 'true', '1', 'on')

    user, err_msg = AuthService.authenticate(email, password)
    if err_msg:
        if "suspended" in err_msg.lower():
            return error_response("AUTH_SUSPENDED", err_msg, 403)
        return error_response("AUTH_INVALID_CREDENTIALS", err_msg, 401)

    login_user(user, remember=remember)
    return success_response(user.to_dict(), "Login successful.")


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    session.clear()
    if request.is_json or request.accept_mimetypes.best == 'application/json':
        return success_response({}, "Logged out successfully.")
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('pages.login_page'))


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return success_response(current_user.to_dict())


@auth_bp.route('/profile', methods=['PUT', 'POST'])
@login_required
def update_profile():
    data = request.get_json() if request.is_json else request.form.to_dict()
    profile_image_path = None

    if 'profile_image' in request.files:
        try:
            profile_image_path = save_uploaded_file(request.files['profile_image'], subfolder='profiles', allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
        except ValueError as e:
            return error_response("FILE_INVALID", str(e), 400)

    try:
        user = AuthService.update_profile(current_user, data or {}, profile_image_path=profile_image_path)
        return success_response(user.to_dict(), "Profile updated successfully.")
    except ValueError as e:
        return error_response("VALIDATION_ERROR", str(e), 400)


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json() if request.is_json else request.form.to_dict()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not old_password or not new_password:
        return error_response("AUTH_VALIDATION_ERROR", "Current and new password are required.", 400)

    if new_password != confirm_password:
        return error_response("AUTH_PASSWORD_MISMATCH", "New passwords do not match.", 400)

    try:
        AuthService.change_password(current_user, old_password, new_password)
        return success_response({}, "Password changed successfully.")
    except ValueError as e:
        return error_response("AUTH_PASSWORD_ERROR", str(e), 400)
