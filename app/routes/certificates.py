from flask import Blueprint, send_file, abort
from flask_login import login_required, current_user
from app.models.certificate import Certificate
from app.services.certificate_service import CertificateService
from app.utils.responses import success_response, error_response
import os
from flask import current_app

certs_bp = Blueprint('api_certificates', __name__, url_prefix='/api/v1/certificates')

@certs_bp.route('/my', methods=['GET'])
@login_required
def get_my_certificates():
    certs = Certificate.query.filter_by(user_id=current_user.id, is_valid=True).all()
    return success_response([c.to_dict() for c in certs])


@certs_bp.route('/verify/<string:certificate_code>', methods=['GET'])
def verify_certificate(certificate_code):
    data, err_msg = CertificateService.verify_certificate(certificate_code)
    if err_msg:
        return error_response("CERT_VERIFICATION_FAILED", err_msg, 404)
    return success_response(data, "Certificate verified authentic.")


@certs_bp.route('/<int:cert_id>/download', methods=['GET'])
@login_required
def download_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    if cert.user_id != current_user.id and current_user.role != 'ADMIN':
        return error_response("AUTH_INSUFFICIENT_ROLE", "Unauthorized.", 403)

    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], cert.pdf_path.replace('uploads/', ''))
    if not os.path.exists(full_path):
        # Regenerate if missing
        CertificateService.generate_certificate(cert.user_id, cert.event_id, cert.attendance_id, cert.certificate_type)

    return send_file(full_path, as_attachment=True, download_name=f"ITSA_Certificate_{cert.event.title.replace(' ', '_')}.pdf")
