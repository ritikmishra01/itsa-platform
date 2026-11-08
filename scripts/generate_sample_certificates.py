# -*- coding: utf-8 -*-
"""
generate_sample_certificates.py
================================
Standalone script to generate 6 sample certificates using MOCK data.
No database writes -- safe to run against any environment.

Usage:
    .\venv\Scripts\python.exe scripts\generate_sample_certificates.py

Output files are saved to: uploads/certificates/samples/
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

# Add the project root to sys.path so imports work when run from root
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, basedir)

# We use the PDF renderer directly without Flask app context
# by importing the private functions and providing config values manually.
import qrcode

# Import the renderer helpers from certificate_service
from app.services.certificate_service import (
    _generate_pdf,
    _resolve_logo_path,
    _format_event_date,
)


# ── Configuration (reads from environment, falls back to defaults) ─────────────
COLLEGE_NAME     = os.environ.get('COLLEGE_NAME', 'SHREE L. R. TIWARI COLLEGE OF ENGINEERING')
COLLEGE_TAGLINE  = os.environ.get(
    'COLLEGE_TAGLINE',
    'Autonomous Institute, Affiliated to University of Mumbai | '
    'Approved by AICTE & DTE, Maharashtra State | NAAC Accredited | '
    'NBA Accredited Program | ISO 9001:2015 Certified | DTE Code No: 3423 | '
    'Recognized under Section 2(f) of the UGC Act 1956 | '
    'Minority Status (Hindi Linguistic)'
)
COLLEGE_LOGO_PATH = os.environ.get('COLLEGE_LOGO_PATH', 'app/static/img/slrtce_logo.png')
SIGN_COORD        = os.environ.get('CERT_SIGN_COORD',       'Mr. Manthan Joshi')
SIGN_COORD_TITLE  = os.environ.get('CERT_SIGN_COORD_TITLE', 'Technical Coordinator, SLRTCE')
SIGN_DEAN         = os.environ.get('CERT_SIGN_DEAN',        'Ms. Saumya Philip')
SIGN_DEAN_TITLE   = os.environ.get('CERT_SIGN_DEAN_TITLE',  'Dean – SWDC')
SIGN_PRINCIPAL    = os.environ.get('CERT_SIGN_PRINCIPAL',   'Prof. Dr. Umesh S. Bhadade')
SIGN_PRINCIPAL_TITLE = os.environ.get('CERT_SIGN_PRINCIPAL_TITLE', 'Principal, SLRTCE')
SIGN_SECRETARY    = os.environ.get('CERT_SIGN_SECRETARY',   'SECRETARY\nRAHUL EDUCATION')

VERIFY_BASE = os.environ.get('FRONTEND_URL', 'http://localhost:5000')
OUTPUT_DIR  = os.path.join(basedir, 'uploads', 'certificates', 'samples')
# ─────────────────────────────────────────────────────────────────────────────


def make_qr(cert_code: str, tmp_dir: str) -> str:
    """Generate a QR PNG and return its path."""
    verify_url = f"{VERIFY_BASE}/certificates/verify/{cert_code}"
    qr = qrcode.QRCode(version=2, box_size=5, border=2,
                        error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_path = os.path.join(tmp_dir, f"qr_{cert_code}.png")
    qr.make_image(fill_color='#1a1a1a', back_color='white').save(qr_path)
    return qr_path


def generate_sample(label: str, student_name: str, event_title: str,
                    event_date_str: str, certificate_type: str,
                    custom_achievement: str = '') -> str:
    """Render one sample PDF and return its output path."""
    cert_code   = f"SAMPLE-CERT-{uuid.uuid4()}"
    issue_date  = datetime.utcnow().strftime('%d/%m/%y')
    logo_path   = _resolve_logo_path(COLLEGE_LOGO_PATH)

    qr_path = make_qr(cert_code, OUTPUT_DIR)

    safe_label = label.replace(' ', '_').replace('/', '-')
    out_path   = os.path.join(OUTPUT_DIR, f"{safe_label}.pdf")

    try:
        _generate_pdf(
            output_path=out_path,
            student_name=student_name,
            event_title=event_title,
            event_date_str=event_date_str,
            certificate_type=certificate_type,
            cert_code=cert_code,
            verify_url=f"{VERIFY_BASE}/certificates/verify/{cert_code}",
            qr_temp_path=qr_path,
            issue_date=issue_date,
            college_name=COLLEGE_NAME,
            tagline=COLLEGE_TAGLINE,
            logo_path=logo_path,
            sign_coord=SIGN_COORD,
            sign_coord_title=SIGN_COORD_TITLE,
            sign_dean=SIGN_DEAN,
            sign_dean_title=SIGN_DEAN_TITLE,
            sign_principal=SIGN_PRINCIPAL,
            sign_principal_title=SIGN_PRINCIPAL_TITLE,
            sign_secretary=SIGN_SECRETARY,
            custom_achievement=custom_achievement,
        )
    finally:
        if os.path.exists(qr_path):
            os.remove(qr_path)

    return out_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n[CERT]  Generating sample certificates -> {OUTPUT_DIR}\n")

    samples = [
        {
            'label':              '01_participation_normal_name',
            'student_name':       'Ritik Mishra',
            'event_title':        'ITSA Tech Expo 2025',
            'event_date_str':     '13th April 2025',
            'certificate_type':   'PARTICIPATION',
            'custom_achievement': '',
        },
        {
            'label':              '02_participation_long_name',
            'student_name':       'Smt. Priyanka Suryanarayana Venkatasubramanian',
            'event_title':        'ITSA Tech Expo 2025',
            'event_date_str':     '13th April 2025',
            'certificate_type':   'PARTICIPATION',
            'custom_achievement': '',
        },
        {
            'label':              '03_winner_certificate',
            'student_name':       'Janit Singh',
            'event_title':        'Jarvis 2.0',
            'event_date_str':     '13th, 14th & 15th April 2026',
            'certificate_type':   'WINNER',
            'custom_achievement': '1st Place',
        },
        {
            'label':              '04_runner_up_certificate',
            'student_name':       'Amit Kumar Sharma',
            'event_title':        'Jarvis 2.0',
            'event_date_str':     '13th, 14th & 15th April 2026',
            'certificate_type':   'WINNER',
            'custom_achievement': '2nd Runner Up',
        },
        {
            'label':              '05_multi_day_date_range',
            'student_name':       'Pooja Deshmukh',
            'event_title':        'National Hackathon & Innovation Summit',
            'event_date_str':     '10th – 14th March 2026',
            'certificate_type':   'PARTICIPATION',
            'custom_achievement': '',
        },
        {
            'label':              '06_volunteer_certificate',
            'student_name':       'Karan Mehta',
            'event_title':        'ITSA Annual Cultural Fest',
            'event_date_str':     '22nd February 2026',
            'certificate_type':   'VOLUNTEER',
            'custom_achievement': 'Volunteer Contribution',
        },
    ]

    results = []
    for s in samples:
        try:
            path = generate_sample(**s)
            size_kb = os.path.getsize(path) // 1024
            print(f"  [OK]  {s['label']}  ({size_kb} KB)")
            results.append((s['label'], path, True, None))
        except Exception as exc:
            print(f"  [FAIL]  {s['label']}  ERROR: {exc}")
            results.append((s['label'], None, False, str(exc)))

    passed = sum(1 for r in results if r[2])
    print(f"\n{'─'*60}")
    print(f"  {passed}/{len(samples)} sample PDFs generated successfully.")
    if passed == len(samples):
        print(f"  Open the files in '{OUTPUT_DIR}' to verify visually.")
    else:
        print("  Some samples failed — see errors above.")
    print(f"{'─'*60}\n")

    return 0 if passed == len(samples) else 1


if __name__ == '__main__':
    sys.exit(main())
