"""
test_certificate_download.py
=============================
Tests for certificate download endpoint and PDF generation/recovery:
1. Certificate with valid existing PDF file on disk.
2. Certificate whose pdf_path is None (e.g. seeded demo certificates).
3. Certificate whose PDF file no longer exists on disk (recovery/regeneration).
4. Full cycle: generate new certificate and download it.
5. Unauthorized access (other student blocked with 403, unauthenticated blocked, admin allowed).
6. Revoked certificate blocked with 404.
7. Non-existent certificate returns 404.
"""

import os
import uuid
from datetime import datetime, timedelta
import pytest
from app.extensions import db
from app.models.user import User, StudentProfile
from app.models.event import Event
from app.models.attendance import Attendance
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.certificate import Certificate
from app.services.certificate_service import CertificateService


def _create_attendance_fixture(app, student_user, event_obj, coord_user):
    """Helper to create registration, ticket, and attendance records."""
    reg = EventRegistration(
        event_id=event_obj.id,
        user_id=student_user.id,
        registration_number=f"REG-{uuid.uuid4().hex[:8].upper()}",
        status='CONFIRMED',
    )
    db.session.add(reg)
    db.session.flush()

    ticket = EventTicket(
        registration_id=reg.id,
        ticket_code=f"TCK-{uuid.uuid4().hex[:8].upper()}",
        is_valid=True,
    )
    db.session.add(ticket)
    db.session.flush()

    att = Attendance(
        event_id=event_obj.id,
        user_id=student_user.id,
        registration_id=reg.id,
        ticket_id=ticket.id,
        scanned_by=coord_user.id,
        scanned_at=datetime.utcnow(),
        status='PRESENT',
    )
    db.session.add(att)
    db.session.commit()
    return att


def test_download_certificate_with_valid_existing_pdf(app, auth_client_student):
    """Test 1: Certificate with a valid existing PDF file on disk."""
    with app.app_context():
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        coord = User.query.filter_by(email='test_coord@itsa.edu').first()
        event = Event.query.first()
        att = _create_attendance_fixture(app, student, event, coord)

        # Generate certificate
        cert = CertificateService.generate_certificate(student.id, event.id, att.id)
        cert_id = cert.id
        full_path = CertificateService.get_pdf_full_path(cert)
        assert full_path is not None
        assert os.path.isfile(full_path)

    # Download as the student
    res = auth_client_student.get(f'/api/v1/certificates/{cert_id}/download')
    assert res.status_code == 200
    assert res.mimetype == 'application/pdf'
    assert b'%PDF' in res.data[:10]
    assert 'attachment' in res.headers.get('Content-Disposition', '')


def test_download_certificate_when_pdf_path_is_none(app, auth_client_student):
    """Test 2: Certificate whose pdf_path is None (e.g. seeded demo certificates)."""
    with app.app_context():
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        coord = User.query.filter_by(email='test_coord@itsa.edu').first()
        event = Event.query.first()
        att = _create_attendance_fixture(app, student, event, coord)

        # Manually create certificate record with pdf_path=None
        cert_code = f"TEST-NONE-CERT-{uuid.uuid4().hex[:8].upper()}"
        cert = Certificate(
            user_id=student.id,
            event_id=event.id,
            attendance_id=att.id,
            certificate_code=cert_code,
            certificate_type='PARTICIPATION',
            pdf_path=None,  # Simulates missing pdf_path
            is_valid=True,
        )
        db.session.add(cert)
        db.session.commit()
        cert_id = cert.id

    # Download: should NOT raise AttributeError, should safely regenerate and serve PDF
    res = auth_client_student.get(f'/api/v1/certificates/{cert_id}/download')
    assert res.status_code == 200
    assert res.mimetype == 'application/pdf'
    assert b'%PDF' in res.data[:10]

    # Verify database was updated with the new path
    with app.app_context():
        updated_cert = Certificate.query.get(cert_id)
        assert updated_cert.pdf_path is not None
        assert updated_cert.pdf_path.endswith('.pdf')
        full_path = CertificateService.get_pdf_full_path(updated_cert)
        assert os.path.isfile(full_path)


def test_download_certificate_when_pdf_file_deleted_from_disk(app, auth_client_student):
    """Test 3: Certificate whose PDF file no longer exists on disk (recovery)."""
    with app.app_context():
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        coord = User.query.filter_by(email='test_coord@itsa.edu').first()
        event = Event.query.first()
        att = _create_attendance_fixture(app, student, event, coord)

        cert = CertificateService.generate_certificate(student.id, event.id, att.id)
        cert_id = cert.id
        full_path = CertificateService.get_pdf_full_path(cert)

        # Deliberately remove the physical file from disk to simulate loss/corruption
        assert os.path.isfile(full_path)
        os.remove(full_path)
        assert not os.path.exists(full_path)

    # Download: should automatically recover by regenerating the file
    res = auth_client_student.get(f'/api/v1/certificates/{cert_id}/download')
    assert res.status_code == 200
    assert res.mimetype == 'application/pdf'
    assert b'%PDF' in res.data[:10]

    # Verify file is restored on disk
    with app.app_context():
        updated_cert = Certificate.query.get(cert_id)
        restored_path = CertificateService.get_pdf_full_path(updated_cert)
        assert os.path.isfile(restored_path)


def test_generate_new_certificate_and_download(app, auth_client_student):
    """Test 4: Full flow — generate new certificate and then download it."""
    with app.app_context():
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        coord = User.query.filter_by(email='test_coord@itsa.edu').first()
        event = Event.query.first()
        att = _create_attendance_fixture(app, student, event, coord)

        new_cert = CertificateService.generate_certificate(
            user_id=student.id,
            event_id=event.id,
            attendance_id=att.id,
            certificate_type='WINNER',
            custom_achievement='1st Place'
        )
        assert new_cert is not None
        assert new_cert.certificate_code.startswith('ITSA-CERT-')
        assert new_cert.pdf_path is not None
        cert_id = new_cert.id

    res = auth_client_student.get(f'/api/v1/certificates/{cert_id}/download')
    assert res.status_code == 200
    assert res.mimetype == 'application/pdf'
    assert b'%PDF' in res.data[:10]


def test_download_certificate_unauthorized_user(app, client):
    """Test 5: Downloading a certificate as an unauthorized user."""
    with app.app_context():
        student1 = User.query.filter_by(email='test_student@itsa.edu').first()
        coord = User.query.filter_by(email='test_coord@itsa.edu').first()
        event = Event.query.first()
        att = _create_attendance_fixture(app, student1, event, coord)

        cert = CertificateService.generate_certificate(student1.id, event.id, att.id)
        cert_id = cert.id

        # Create a second student
        student2 = User(
            email='other_student@itsa.edu',
            full_name='Other Student',
            role='STUDENT',
            is_active=True
        )
        student2.set_password('Other@12345')
        db.session.add(student2)
        db.session.flush()
        sp2 = StudentProfile(user_id=student2.id, student_id='ST2026999', department='IT', year_of_study=2)
        db.session.add(sp2)
        db.session.commit()

    # Case A: Unauthenticated user -> 401 or redirect to login
    res_unauth = client.get(f'/api/v1/certificates/{cert_id}/download')
    assert res_unauth.status_code in (401, 302)

    # Case B: Authenticated as Student 2 (not the owner) -> 403 Forbidden
    client.post('/api/v1/auth/login', json={'email': 'other_student@itsa.edu', 'password': 'Other@12345'})
    res_other = client.get(f'/api/v1/certificates/{cert_id}/download')
    assert res_other.status_code == 403
    json_data = res_other.get_json()
    assert json_data['error']['code'] == 'AUTH_INSUFFICIENT_ROLE'

    # Case C: Admin user -> 200 OK (authorized)
    client.post('/api/v1/auth/logout')
    client.post('/api/v1/auth/login', json={'email': 'test_admin@itsa.edu', 'password': 'Admin@12345'})
    res_admin = client.get(f'/api/v1/certificates/{cert_id}/download')
    assert res_admin.status_code == 200
    assert res_admin.mimetype == 'application/pdf'


def test_download_revoked_certificate(app, auth_client_student):
    """Test 6: Revoked certificate cannot be downloaded."""
    with app.app_context():
        student = User.query.filter_by(email='test_student@itsa.edu').first()
        coord = User.query.filter_by(email='test_coord@itsa.edu').first()
        event = Event.query.first()
        att = _create_attendance_fixture(app, student, event, coord)

        cert = CertificateService.generate_certificate(student.id, event.id, att.id)
        cert.is_valid = False
        db.session.commit()
        cert_id = cert.id

    res = auth_client_student.get(f'/api/v1/certificates/{cert_id}/download')
    assert res.status_code == 404
    json_data = res.get_json()
    assert json_data['error']['code'] == 'CERTIFICATE_REVOKED'


def test_download_nonexistent_certificate(app, auth_client_student):
    """Test 7: Requesting a non-existent certificate ID returns 404."""
    res = auth_client_student.get('/api/v1/certificates/99999/download')
    assert res.status_code == 404
