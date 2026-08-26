import os
import uuid
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from flask import current_app
from app.extensions import db
from app.models.certificate import Certificate
from app.models.event import Event
from app.models.user import User
from app.services.notification_service import NotificationService

class CertificateService:
    @staticmethod
    def generate_certificate(user_id, event_id, attendance_id, certificate_type='PARTICIPATION'):
        # Check if certificate already exists
        existing = Certificate.query.filter_by(user_id=user_id, event_id=event_id).first()
        if existing:
            return existing

        user = User.query.get(user_id)
        event = Event.query.get(event_id)
        if not user or not event:
            raise ValueError("User or Event not found.")

        cert_code = f"ITSA-CERT-{uuid.uuid4()}"
        certs_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
        os.makedirs(certs_dir, exist_ok=True)

        pdf_filename = f"{cert_code}.pdf"
        pdf_path = os.path.join(certs_dir, pdf_filename)
        rel_pdf_path = f"uploads/certificates/{pdf_filename}"

        # Generate verification QR Code
        verify_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5000')}/certificates/verify/{cert_code}"
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_temp_path = os.path.join(certs_dir, f"temp_qr_{cert_code}.png")
        qr.make_image(fill_color="#1a73e8", back_color="white").save(qr_temp_path)

        # Generate PDF with ReportLab
        try:
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=landscape(A4),
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CertTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=28,
                textColor=colors.HexColor('#1a73e8'),
                alignment=1, # Center
                spaceAfter=15
            )
            sub_style = ParagraphStyle(
                'CertSub',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.HexColor('#fbbc04'),
                alignment=1,
                spaceAfter=25
            )
            text_style = ParagraphStyle(
                'CertText',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=13,
                leading=20,
                textColor=colors.HexColor('#202124'),
                alignment=1,
                spaceAfter=15
            )
            name_style = ParagraphStyle(
                'CertName',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=24,
                textColor=colors.HexColor('#202124'),
                alignment=1,
                spaceAfter=15
            )
            meta_style = ParagraphStyle(
                'CertMeta',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9,
                textColor=colors.HexColor('#5f6368'),
                alignment=1
            )

            story = []
            story.append(Paragraph("INFORMATION TECHNOLOGY STUDENTS' ASSOCIATION", title_style))
            story.append(Paragraph("CERTIFICATE OF PARTICIPATION", sub_style))
            story.append(Paragraph("This is proudly presented to", text_style))
            story.append(Paragraph(user.full_name.upper(), name_style))
            event_date = event.start_datetime.strftime('%B %d, %Y')
            story.append(Paragraph(
                f"for successfully attending and actively participating in <b>{event.title}</b> "
                f"organized by ITSA on <b>{event_date}</b>.",
                text_style
            ))
            story.append(Spacer(1, 20))

            # Verification QR Code table
            qr_img = RLImage(qr_temp_path, width=1.1*inch, height=1.1*inch)
            code_para = Paragraph(f"Certificate ID: <b>{cert_code}</b><br/>Scan QR or visit verify portal to validate authenticity.", meta_style)

            footer_table = Table([[qr_img, code_para]], colWidths=[1.3*inch, 7*inch])
            footer_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT')
            ]))
            story.append(footer_table)

            doc.build(story)
        finally:
            if os.path.exists(qr_temp_path):
                try:
                    os.remove(qr_temp_path)
                except Exception:
                    pass

        certificate = Certificate(
            user_id=user_id,
            event_id=event_id,
            attendance_id=attendance_id,
            certificate_code=cert_code,
            certificate_type=certificate_type,
            pdf_path=rel_pdf_path,
            is_valid=True
        )
        db.session.add(certificate)
        db.session.commit()

        # Notify student
        NotificationService.create_notification(
            user_id=user_id,
            notif_type='CERTIFICATE_READY',
            title=f"Certificate Ready: {event.title}",
            message=f"Your verified certificate for '{event.title}' is ready for download!",
            related_event_id=event.id,
            send_email_alert=True,
            user_email=user.email
        )

        return certificate

    @staticmethod
    def verify_certificate(certificate_code):
        cert = Certificate.query.filter_by(certificate_code=certificate_code.strip()).first()
        if not cert:
            return None, "Certificate not found."
        if not cert.is_valid:
            return None, "This certificate has been revoked by administration."
        return {
            'valid': True,
            'certificate_code': cert.certificate_code,
            'student_name': cert.user.full_name,
            'event_title': cert.event.title,
            'event_date': cert.event.start_datetime.strftime('%B %d, %Y'),
            'certificate_type': cert.certificate_type,
            'issued_at': cert.issued_at.strftime('%B %d, %Y')
        }, None
