"""
certificate_service.py
======================
Generates A4-landscape PDF certificates matching the official
Shree L. R. Tiwari College of Engineering Certificate of Appreciation design.

Public API is unchanged:
  - CertificateService.generate_certificate(user_id, event_id, attendance_id, certificate_type)
  - CertificateService.verify_certificate(certificate_code)

All branding values (college name, tagline, logo path, signatory names) are
read from Flask app config (configured via .env variables).
"""

import io
import os
import uuid
import textwrap
import math
import qrcode
from datetime import datetime

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

from flask import current_app
from app.extensions import db
from app.models.certificate import Certificate
from app.models.event import Event
from app.models.user import User
from app.services.notification_service import NotificationService


# ── Colour palette ─────────────────────────────────────────────────────────────
MAROON      = colors.HexColor('#800000')
DARK_GOLD   = colors.HexColor('#C5A028')
LIGHT_GOLD  = colors.HexColor('#E8C84A')
BODY_TEXT   = colors.HexColor('#1A1A1A')
GREY_TEXT   = colors.HexColor('#444444')
WHITE       = colors.white
CREAM_BG    = colors.HexColor('#FAFAF5')
# ──────────────────────────────────────────────────────────────────────────────


def _resolve_logo_path(config_path: str) -> str | None:
    """Return an absolute path to the logo PNG if it exists, else None."""
    if not config_path:
        return None
    if os.path.isabs(config_path) and os.path.exists(config_path):
        return config_path
    # Relative to project root (two levels up from this file: app/services/ → root)
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    candidate = os.path.join(basedir, config_path)
    if os.path.exists(candidate):
        return candidate
    return None


def _draw_placeholder_crest(c: rl_canvas.Canvas, x: float, y: float,
                              size: float = 60) -> None:
    """
    Draw a simple decorative crest/emblem when no real logo is available.
    Positioned so its centre is at (x, y).
    """
    r = size / 2
    # Outer gold circle
    c.setStrokeColor(DARK_GOLD)
    c.setFillColor(DARK_GOLD)
    c.setLineWidth(1.5)
    c.circle(x, y, r, stroke=1, fill=0)
    # Inner maroon circle
    c.setStrokeColor(MAROON)
    c.circle(x, y, r * 0.78, stroke=1, fill=0)
    # Cross-like decoration
    c.setFillColor(MAROON)
    c.setLineWidth(1)
    cross_w = r * 0.12
    cross_h = r * 0.55
    c.rect(x - cross_w / 2, y - cross_h / 2, cross_w, cross_h, fill=1, stroke=0)
    c.rect(x - cross_h / 2, y - cross_w / 2, cross_h, cross_w, fill=1, stroke=0)
    # "SLRTCE" text in centre
    c.setFont('Helvetica-Bold', max(5, size * 0.115))
    c.setFillColor(DARK_GOLD)
    c.drawCentredString(x, y - size * 0.07, 'SLRTCE')


def _draw_corner_band(c: rl_canvas.Canvas, pw: float, ph: float,
                       band: float = 55) -> None:
    """
    Draw gold diagonal corner bands (top-left and bottom-right) matching
    the reference photograph's decorative gold corners.
    """
    c.saveState()
    # Top-left triangle
    c.setFillColor(DARK_GOLD)
    path = c.beginPath()
    path.moveTo(0, ph)
    path.lineTo(band, ph)
    path.lineTo(0, ph - band)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    # Bottom-right triangle
    path2 = c.beginPath()
    path2.moveTo(pw, 0)
    path2.lineTo(pw - band, 0)
    path2.lineTo(pw, band)
    path2.close()
    c.drawPath(path2, fill=1, stroke=0)
    # Maroon inner accent on top-left corner
    c.setFillColor(MAROON)
    path3 = c.beginPath()
    path3.moveTo(0, ph)
    path3.lineTo(band * 0.55, ph)
    path3.lineTo(0, ph - band * 0.55)
    path3.close()
    c.drawPath(path3, fill=1, stroke=0)
    # Maroon inner accent on bottom-right corner
    path4 = c.beginPath()
    path4.moveTo(pw, 0)
    path4.lineTo(pw - band * 0.55, 0)
    path4.lineTo(pw, band * 0.55)
    path4.close()
    c.drawPath(path4, fill=1, stroke=0)
    c.restoreState()


def _draw_border(c: rl_canvas.Canvas, pw: float, ph: float,
                  margin: float = 18) -> None:
    """
    Draw the two-layer decorative border:
    - Outer maroon rectangle (thick)
    - Inner thin gold rectangle (inset by ~6 pt)
    """
    c.saveState()
    # Outer maroon border
    c.setStrokeColor(MAROON)
    c.setLineWidth(3.5)
    c.rect(margin, margin, pw - 2 * margin, ph - 2 * margin, stroke=1, fill=0)
    # Inner gold hairline
    inner = margin + 5
    c.setStrokeColor(DARK_GOLD)
    c.setLineWidth(1)
    c.rect(inner, inner, pw - 2 * inner, ph - 2 * inner, stroke=1, fill=0)
    c.restoreState()


def _draw_header(c: rl_canvas.Canvas, pw: float, ph: float,
                  logo_path: str | None,
                  college_name: str, tagline: str) -> float:
    """
    Draw college logo + name + tagline header.
    Returns the Y coordinate of the bottom of the header area.
    """
    margin      = 24
    inner_left  = 30
    logo_size   = 68        # logo diameter in pts
    header_top  = ph - 30   # top of usable inner area

    # ── Logo (left of header) ──────────────────────────────────────────────
    logo_cx = inner_left + logo_size / 2
    logo_cy = header_top - logo_size / 2 - 6

    if logo_path:
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, logo_cx - logo_size / 2, logo_cy - logo_size / 2,
                        width=logo_size, height=logo_size, mask='auto',
                        preserveAspectRatio=True)
        except Exception:
            _draw_placeholder_crest(c, logo_cx, logo_cy, logo_size)
    else:
        _draw_placeholder_crest(c, logo_cx, logo_cy, logo_size)

    # ── College name (right of logo, centred on remaining width) ──────────
    text_left  = inner_left + logo_size + 10
    text_width = pw - text_left - 30

    # Split college name into two lines for visual balance (matches reference)
    name_parts = college_name.split(' ', 5)
    # Aim for roughly: line1 = first half, line2 = second half
    half = max(1, len(name_parts) // 2)
    name_line1 = ' '.join(name_parts[:half])
    name_line2 = ' '.join(name_parts[half:])

    name_cx = text_left + text_width / 2

    c.saveState()
    c.setFillColor(MAROON)

    # Line 1 of college name
    font_size_1 = 26
    c.setFont('Times-Bold', font_size_1)
    c.drawCentredString(name_cx, logo_cy + 14, name_line1)

    # Line 2 of college name
    font_size_2 = 24
    c.setFont('Times-Bold', font_size_2)
    c.drawCentredString(name_cx, logo_cy + 14 - font_size_1 - 2, name_line2)

    # Tagline (small, centred, italic-style using Helvetica-Oblique)
    c.setFillColor(GREY_TEXT)
    c.setFont('Helvetica', 6.5)
    tagline_y = logo_cy + 14 - font_size_1 - font_size_2 - 8

    # Word-wrap tagline to fit within text_width
    words = tagline.split()
    lines, current = [], []
    for word in words:
        test = ' '.join(current + [word])
        if c.stringWidth(test, 'Helvetica', 6.5) <= text_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))

    tagline_bottom_y = tagline_y
    for i, line in enumerate(lines[:3]):   # max 3 tagline rows
        c.drawCentredString(name_cx, tagline_y - i * 8, line)
        tagline_bottom_y = tagline_y - i * 8

    c.restoreState()

    # ── Horizontal maroon divider ─────────────────────────────────────────
    divider_y = min(logo_cy - logo_size / 2, tagline_bottom_y) - 10
    c.saveState()
    c.setStrokeColor(MAROON)
    c.setLineWidth(2)
    c.line(inner_left, divider_y, pw - inner_left, divider_y)
    c.restoreState()

    return divider_y


def _draw_certificate_title(c: rl_canvas.Canvas, pw: float,
                              top_y: float) -> float:
    """
    Draw 'CERTIFICATE OF APPRECIATION' centred, return bottom Y of the section.
    """
    title = 'CERTIFICATE OF APPRECIATION'
    font_size = 24
    title_y = top_y - 34

    c.saveState()
    c.setFont('Times-Bold', font_size)
    c.setFillColor(MAROON)
    c.drawCentredString(pw / 2, title_y, title)

    # Second thin divider below title
    inner_left = 30
    div2_y = title_y - 14
    c.setStrokeColor(MAROON)
    c.setLineWidth(1.5)
    c.line(inner_left, div2_y, pw - inner_left, div2_y)
    c.restoreState()

    return div2_y


def _underline(c: rl_canvas.Canvas, x1: float, y: float, x2: float) -> None:
    """Draw a thin underline between two x-coordinates at height y."""
    c.saveState()
    c.setStrokeColor(BODY_TEXT)
    c.setLineWidth(0.75)
    c.line(x1, y - 2, x2, y - 2)
    c.restoreState()


def _fit_text(c: rl_canvas.Canvas, text: str, font: str,
               max_size: float, min_size: float, max_width: float) -> float:
    """Return the largest font size ≥ min_size at which `text` fits in max_width."""
    size = max_size
    while size >= min_size:
        if c.stringWidth(text, font, size) <= max_width:
            return size
        size -= 0.5
    return min_size


def _build_achievement_line(certificate_type: str, custom_achievement: str = '') -> str:
    """
    Return the achievement phrase for the 'for achieving __ place in the' line.
    """
    if custom_achievement:
        return custom_achievement
    mapping = {
        'WINNER':        '1st Place',
        'RUNNER_UP':     '2nd Runner Up',
        'PARTICIPATION': 'Participation',
        'VOLUNTEER':     'Volunteer Contribution',
    }
    return mapping.get(certificate_type, 'Participation')


def _draw_body(c: rl_canvas.Canvas, pw: float, top_y: float,
               student_name: str, certificate_type: str,
               event_title: str, event_date_str: str,
               custom_achievement: str = '') -> float:
    """
    Draw the certificate body:
      Mr./Ms. ___name___
      for achieving ___achievement___ place in the
      ___event___ at our TECHNICAL EVENT
      held on ___date___
    Returns bottom Y of body.
    """
    left   = 40
    right  = pw - 40
    width  = right - left
    y      = top_y - 28

    achievement = _build_achievement_line(certificate_type, custom_achievement)

    c.saveState()
    c.setFillColor(BODY_TEXT)

    # ── Line 1: Mr./Ms. [name] ────────────────────────────────────────────
    prefix      = 'Mr./Ms. '
    prefix_font = 'Times-Roman'
    prefix_size = 16
    name_font   = 'Times-Bold'

    c.setFont(prefix_font, prefix_size)
    prefix_w = c.stringWidth(prefix, prefix_font, prefix_size)
    c.drawString(left, y, prefix)

    # Auto-scale name to fit remaining width
    name_available = width - prefix_w - 10
    name_size = _fit_text(c, student_name, name_font, 16, 9, name_available)
    c.setFont(name_font, name_size)
    name_w = c.stringWidth(student_name, name_font, name_size)
    name_x = left + prefix_w
    c.drawString(name_x, y, student_name)
    _underline(c, name_x, y, name_x + max(name_w, name_available))

    y -= 26

    # ── Line 2: for achieving [achievement] place in the ─────────────────
    body_font = 'Times-Roman'
    body_size = 15
    c.setFont(body_font, body_size)

    seg1   = 'for achieving   '
    seg2   = '   place in the'
    seg1_w = c.stringWidth(seg1, body_font, body_size)
    seg2_w = c.stringWidth(seg2, body_font, body_size)
    ach_avail = width - seg1_w - seg2_w - 10

    c.drawString(left, y, seg1)
    ach_x  = left + seg1_w
    ach_size = _fit_text(c, achievement, 'Times-Italic', body_size, 9, ach_avail)
    c.setFont('Times-Italic', ach_size)
    ach_w  = c.stringWidth(achievement, 'Times-Italic', ach_size)
    c.drawString(ach_x, y, achievement)
    _underline(c, ach_x, y, ach_x + max(ach_w, ach_avail))
    c.setFont(body_font, body_size)
    c.drawString(ach_x + max(ach_w, ach_avail), y, seg2)

    y -= 26

    # ── Line 3: [event] at our TECHNICAL EVENT ────────────────────────────
    seg3   = '   at our '
    seg4   = 'TECHNICAL EVENT'
    seg3_w = c.stringWidth(seg3, body_font, body_size)
    seg4_w = c.stringWidth(seg4, 'Times-Bold', body_size)
    evt_avail = width - seg3_w - seg4_w - 10

    evt_size = _fit_text(c, event_title, 'Times-Italic', body_size, 9, evt_avail)
    c.setFont('Times-Italic', evt_size)
    evt_w  = c.stringWidth(event_title, 'Times-Italic', evt_size)
    c.drawString(left, y, event_title)
    _underline(c, left, y, left + max(evt_w, evt_avail))
    c.setFont(body_font, body_size)
    c.drawString(left + max(evt_w, evt_avail), y, seg3)
    c.setFont('Times-Bold', body_size)
    c.drawString(left + max(evt_w, evt_avail) + seg3_w, y, seg4)

    y -= 26

    # ── Line 4: held on [date] ────────────────────────────────────────────
    held = 'held on   '
    held_w = c.stringWidth(held, body_font, body_size)
    c.setFont(body_font, body_size)
    c.drawString(left, y, held)
    date_x     = left + held_w
    date_avail = width - held_w - 10
    date_size  = _fit_text(c, event_date_str, 'Times-Italic', body_size, 9, date_avail)
    c.setFont('Times-Italic', date_size)
    date_w     = c.stringWidth(event_date_str, 'Times-Italic', date_size)
    c.drawString(date_x, y, event_date_str)
    _underline(c, date_x, y, date_x + max(date_w, date_avail))

    c.restoreState()
    return y - 20


def _draw_signatures(c: rl_canvas.Canvas, pw: float, ph: float,
                      bottom_y: float,
                      sign_coord: str, sign_coord_title: str,
                      sign_dean: str, sign_dean_title: str,
                      sign_principal: str, sign_principal_title: str,
                      sign_secretary: str,
                      issue_date: str) -> None:
    """
    Draw the 5-column signature row near the bottom of the page,
    matching the reference: Date | Coordinator | Dean | Principal | Secretary.
    """
    inner_left  = 30
    inner_right = pw - 30
    usable_w    = inner_right - inner_left
    col_w       = usable_w / 5
    sig_y       = ph * 0.14   # signature line Y

    c.saveState()
    c.setStrokeColor(BODY_TEXT)
    c.setLineWidth(0.75)

    columns = [
        {
            'label':    issue_date,
            'sublabel': 'Date of Issue',
        },
        {
            'label':    sign_coord,
            'sublabel': sign_coord_title,
        },
        {
            'label':    sign_dean,
            'sublabel': sign_dean_title,
        },
        {
            'label':    sign_principal,
            'sublabel': sign_principal_title,
        },
        {
            'label':    sign_secretary,
            'sublabel': '',
        },
    ]

    for i, col in enumerate(columns):
        cx    = inner_left + col_w * i + col_w / 2
        line_x1 = inner_left + col_w * i + 6
        line_x2 = inner_left + col_w * (i + 1) - 6

        # Signature horizontal rule
        c.line(line_x1, sig_y, line_x2, sig_y)

        # Name above line (bold, slightly italic to suggest handwriting)
        label_lines = col['label'].split('\n')
        c.setFont('Helvetica-BoldOblique', 8.5)
        c.setFillColor(BODY_TEXT)
        for j, ln in enumerate(label_lines):
            c.drawCentredString(cx, sig_y + 4 + (len(label_lines) - 1 - j) * 10, ln)

        # Title / designation below line
        if col['sublabel']:
            c.setFont('Helvetica', 7.5)
            c.setFillColor(GREY_TEXT)
            sub_lines = col['sublabel'].split('\n')
            for j, sln in enumerate(sub_lines):
                c.drawCentredString(cx, sig_y - 12 - j * 9, sln)

    c.restoreState()


def _generate_pdf(output_path: str,
                  student_name: str,
                  event_title: str,
                  event_date_str: str,
                  certificate_type: str,
                  cert_code: str,
                  verify_url: str,
                  qr_temp_path: str,
                  issue_date: str,
                  college_name: str,
                  tagline: str,
                  logo_path: str | None,
                  sign_coord: str,
                  sign_coord_title: str,
                  sign_dean: str,
                  sign_dean_title: str,
                  sign_principal: str,
                  sign_principal_title: str,
                  sign_secretary: str,
                  custom_achievement: str = '') -> None:
    """
    Core PDF renderer — draws the full certificate using ReportLab canvas.
    All layout is done in one pass for precise positional control.
    """
    pw, ph = landscape(A4)   # 841.89 × 595.28 pts

    c = rl_canvas.Canvas(output_path, pagesize=landscape(A4))
    c.setTitle(f"Certificate of Appreciation – {student_name}")

    # ── Background cream fill ─────────────────────────────────────────────
    c.saveState()
    c.setFillColor(CREAM_BG)
    c.rect(0, 0, pw, ph, fill=1, stroke=0)
    c.restoreState()

    # ── Corner bands (drawn first, behind everything) ──────────────────────
    _draw_corner_band(c, pw, ph, band=65)

    # ── Decorative border ─────────────────────────────────────────────────
    _draw_border(c, pw, ph)

    # ── Header: logo + college name + tagline ─────────────────────────────
    divider_y = _draw_header(c, pw, ph, logo_path, college_name, tagline)

    # ── Certificate title ─────────────────────────────────────────────────
    div2_y = _draw_certificate_title(c, pw, divider_y)

    # ── Body text ─────────────────────────────────────────────────────────
    body_bottom = _draw_body(
        c, pw, div2_y,
        student_name, certificate_type,
        event_title, event_date_str,
        custom_achievement
    )

    # ── Signature row ─────────────────────────────────────────────────────
    _draw_signatures(
        c, pw, ph, body_bottom,
        sign_coord, sign_coord_title,
        sign_dean, sign_dean_title,
        sign_principal, sign_principal_title,
        sign_secretary,
        issue_date
    )

    # ── QR code (bottom-right, above the border margin) ───────────────────
    qr_size = 62
    qr_x    = pw - 30 - qr_size - 8
    qr_y    = 32
    try:
        qr_img = ImageReader(qr_temp_path)
        c.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')
    except Exception:
        pass

    # Certificate ID micro-text below QR
    c.saveState()
    c.setFont('Courier', 5.5)
    c.setFillColor(GREY_TEXT)
    cert_id_short = cert_code[-20:] if len(cert_code) > 20 else cert_code
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 8, cert_id_short)
    c.restoreState()

    # ── Save ──────────────────────────────────────────────────────────────
    c.save()


def _format_event_date(event: Event) -> str:
    """
    Format event date as a readable string. If start and end are on different
    days, return a range like '13th, 14th & 15th April 2025'.
    """
    start = event.start_datetime
    end   = event.end_datetime if event.end_datetime else start

    def ordinal(n: int) -> str:
        suf = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10 if n % 100 not in (11, 12, 13) else 0, 'th')
        return f"{n}{suf}"

    if start.date() == end.date():
        return f"{ordinal(start.day)} {start.strftime('%B %Y')}"

    # Multi-day: list each day if ≤ 4 days span, else show range
    delta = (end.date() - start.date()).days + 1
    if delta <= 4:
        days = [start.date().replace(day=start.day + i) for i in range(delta)]
        day_strs = [ordinal(d.day) for d in days]
        if len(day_strs) > 1:
            return f"{', '.join(day_strs[:-1])} & {day_strs[-1]} {start.strftime('%B %Y')}"
        return f"{day_strs[0]} {start.strftime('%B %Y')}"
    else:
        return f"{ordinal(start.day)} – {ordinal(end.day)} {start.strftime('%B %Y')}"


class CertificateService:

    @staticmethod
    def generate_certificate(user_id: int, event_id: int, attendance_id: int,
                              certificate_type: str = 'PARTICIPATION',
                              custom_achievement: str = '') -> Certificate:
        """
        Generate (or retrieve existing) a certificate PDF for the given
        student / event / attendance record.

        Args:
            user_id:            Student's user ID.
            event_id:           Event ID.
            attendance_id:      Attendance record ID (foreign key).
            certificate_type:   One of PARTICIPATION | WINNER | VOLUNTEER.
            custom_achievement: Optional override for the achievement description
                                line (e.g. "2nd Runner Up"). If empty, derived
                                from certificate_type.

        Returns:
            Certificate model instance (new or existing).
        """
    @staticmethod
    def get_pdf_full_path(cert: Certificate) -> str | None:
        """
        Safely resolve the physical filesystem path for a certificate PDF.
        Returns normalized absolute path if valid, or None if pdf_path is missing
        or if path traversal is detected.
        """
        if not cert or not cert.pdf_path:
            return None

        upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        clean_rel = cert.pdf_path.replace('uploads/', '').replace('\\', '/').lstrip('/')
        full_path = os.path.abspath(os.path.join(upload_folder, clean_rel))

        # Path traversal guard: must be strictly inside upload_folder
        try:
            if os.path.commonpath([upload_folder, full_path]) != upload_folder:
                return None
        except ValueError:
            return None

        return full_path

    @staticmethod
    def generate_pdf_for_certificate(cert: Certificate, custom_achievement: str = '') -> str:
        """
        Generate (or re-generate) the physical PDF file for an existing Certificate
        record, save its relative path to cert.pdf_path, commit to DB, and return
        the absolute file path.
        """
        user = cert.user or User.query.get(cert.user_id)
        event = cert.event or Event.query.get(cert.event_id)
        if not user or not event:
            raise ValueError("Associated User or Event not found for certificate.")

        # Ensure unique certificate code is set
        cert_code = cert.certificate_code or f"ITSA-CERT-{uuid.uuid4()}"
        if not cert.certificate_code:
            cert.certificate_code = cert_code

        certs_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
        os.makedirs(certs_dir, exist_ok=True)

        pdf_filename = f"{cert_code}.pdf"
        pdf_path = os.path.join(certs_dir, pdf_filename)
        rel_pdf_path = f"uploads/certificates/{pdf_filename}"
        qr_temp_path = os.path.join(certs_dir, f"temp_qr_{cert_code}.png")

        # QR code for verification
        verify_url = (
            f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5000')}"
            f"/certificates/verify/{cert_code}"
        )
        qr = qrcode.QRCode(version=2, box_size=5, border=2,
                            error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr.make_image(fill_color='#1a1a1a', back_color='white').save(qr_temp_path)

        # Pull branding from config
        cfg = current_app.config
        college_name = cfg.get('COLLEGE_NAME', 'SHREE L. R. TIWARI COLLEGE OF ENGINEERING')
        tagline = cfg.get('COLLEGE_TAGLINE', '')
        logo_raw = cfg.get('COLLEGE_LOGO_PATH', '')
        logo_path = _resolve_logo_path(logo_raw)
        sign_coord = cfg.get('CERT_SIGN_COORD', 'Technical Coordinator')
        sign_coord_title = cfg.get('CERT_SIGN_COORD_TITLE', 'Technical Coordinator, SLRTCE')
        sign_dean = cfg.get('CERT_SIGN_DEAN', 'Dean – SWDC')
        sign_dean_title = cfg.get('CERT_SIGN_DEAN_TITLE', '')
        sign_principal = cfg.get('CERT_SIGN_PRINCIPAL', 'Principal, SLRTCE')
        sign_principal_title = cfg.get('CERT_SIGN_PRINCIPAL_TITLE', '')
        sign_secretary = cfg.get('CERT_SIGN_SECRETARY', 'SECRETARY\nRAHUL EDUCATION')

        issue_date = cert.issued_at.strftime('%d/%m/%y') if cert.issued_at else datetime.utcnow().strftime('%d/%m/%y')
        event_date_str = _format_event_date(event)

        try:
            _generate_pdf(
                output_path=pdf_path,
                student_name=user.full_name,
                event_title=event.title,
                event_date_str=event_date_str,
                certificate_type=cert.certificate_type,
                cert_code=cert_code,
                verify_url=verify_url,
                qr_temp_path=qr_temp_path,
                issue_date=issue_date,
                college_name=college_name,
                tagline=tagline,
                logo_path=logo_path,
                sign_coord=sign_coord,
                sign_coord_title=sign_coord_title,
                sign_dean=sign_dean,
                sign_dean_title=sign_dean_title,
                sign_principal=sign_principal,
                sign_principal_title=sign_principal_title,
                sign_secretary=sign_secretary,
                custom_achievement=custom_achievement,
            )
        finally:
            try:
                if os.path.exists(qr_temp_path):
                    os.remove(qr_temp_path)
            except Exception:
                pass

        # Update database record
        cert.pdf_path = rel_pdf_path
        db.session.commit()

        return pdf_path

    @staticmethod
    def generate_certificate(user_id: int, event_id: int, attendance_id: int,
                              certificate_type: str = 'PARTICIPATION',
                              custom_achievement: str = '') -> Certificate:
        """
        Generate (or retrieve existing) a certificate PDF for the given
        student / event / attendance record.

        Args:
            user_id:            Student's user ID.
            event_id:           Event ID.
            attendance_id:      Attendance record ID (foreign key).
            certificate_type:   One of PARTICIPATION | WINNER | VOLUNTEER.
            custom_achievement: Optional override for the achievement description
                                line (e.g. "2nd Runner Up"). If empty, derived
                                from certificate_type.

        Returns:
            Certificate model instance (new or existing).
        """
        # Check if existing certificate exists for this user and event
        existing = Certificate.query.filter_by(user_id=user_id, event_id=event_id).first()
        if existing:
            full_path = CertificateService.get_pdf_full_path(existing)
            if full_path and os.path.isfile(full_path):
                return existing
            # If pdf_path is missing or physical file is gone, safely generate it
            CertificateService.generate_pdf_for_certificate(existing, custom_achievement)
            return existing

        user = User.query.get(user_id)
        event = Event.query.get(event_id)
        if not user or not event:
            raise ValueError("User or Event not found.")

        cert_code = f"ITSA-CERT-{uuid.uuid4()}"
        certificate = Certificate(
            user_id=user_id,
            event_id=event_id,
            attendance_id=attendance_id,
            certificate_code=cert_code,
            certificate_type=certificate_type,
            pdf_path=None,
            is_valid=True,
        )
        db.session.add(certificate)
        db.session.flush()

        CertificateService.generate_pdf_for_certificate(certificate, custom_achievement)

        # Notify student
        NotificationService.create_notification(
            user_id=user_id,
            notif_type='CERTIFICATE_READY',
            title=f"Certificate Ready: {event.title}",
            message=(
                f"Your verified certificate for '{event.title}' "
                f"is ready for download!"
            ),
            related_event_id=event.id,
            send_email_alert=True,
            user_email=user.email,
        )

        return certificate

    @staticmethod
    def verify_certificate(certificate_code: str):
        """
        Verify a certificate by its unique code.

        Returns:
            (dict, None)       — on success
            (None, error_msg)  — on failure
        """
        cert = Certificate.query.filter_by(
            certificate_code=certificate_code.strip()
        ).first()
        if not cert:
            return None, "Certificate not found."
        if not cert.is_valid:
            return None, "This certificate has been revoked by administration."
        return {
            'valid':            True,
            'certificate_code': cert.certificate_code,
            'student_name':     cert.user.full_name,
            'event_title':      cert.event.title,
            'event_date':       cert.event.start_datetime.strftime('%B %d, %Y'),
            'certificate_type': cert.certificate_type,
            'issued_at':        cert.issued_at.strftime('%B %d, %Y'),
        }, None
