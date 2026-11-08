from flask import Blueprint, send_file, abort, current_app
from flask_login import login_required, current_user
from app.models.certificate import Certificate
from app.services.certificate_service import CertificateService
from app.utils.responses import success_response, error_response
import os

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

    # Ownership and role-based access check
    if cert.user_id != current_user.id and current_user.role != 'ADMIN':
        return error_response("AUTH_INSUFFICIENT_ROLE", "Unauthorized to access this certificate.", 403)

    if not cert.is_valid:
        return error_response("CERTIFICATE_REVOKED", "This certificate has been revoked.", 404)

    # Securely resolve path
    full_path = CertificateService.get_pdf_full_path(cert)

    # If pdf_path is missing or physical file is not on disk, safely regenerate
    if not full_path or not os.path.isfile(full_path):
        try:
            full_path = CertificateService.generate_pdf_for_certificate(cert)
        except Exception as e:
            current_app.logger.error(f"Failed to generate certificate PDF for cert {cert.id}: {e}")
            return error_response(
                "CERTIFICATE_NOT_FOUND",
                "Certificate PDF file could not be found or generated.",
                404
            )

    if not full_path or not os.path.isfile(full_path):
        return error_response(
            "CERTIFICATE_NOT_FOUND",
            "Certificate PDF file is not available.",
            404
        )

    event_title = cert.event.title if cert.event else "Event"
    safe_title = "".join(c for c in event_title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    download_name = f"ITSA_Certificate_{safe_title}.pdf"

    return send_file(
        full_path,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/pdf'
    )
