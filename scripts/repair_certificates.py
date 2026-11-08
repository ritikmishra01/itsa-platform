"""
repair_certificates.py
======================
Safe maintenance utility to ensure all database certificate records
have valid physical PDF files and populated pdf_path fields.

- Preserves all certificate IDs, student links, event links, codes, and dates.
- Generates missing PDFs on disk with embedded SLRTCE logo and QR codes.
- Idempotent and non-destructive: skips records that already have existing PDFs.

Usage:
    .\venv\Scripts\python.exe scripts/repair_certificates.py
"""

import os
import sys

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, basedir)

from app import create_app
from app.models.certificate import Certificate
from app.services.certificate_service import CertificateService

def repair_all_certificates():
    app = create_app()
    with app.app_context():
        certs = Certificate.query.all()
        print(f"\n[CERT] Auditing {len(certs)} certificate records in database...\n")

        repaired = 0
        already_valid = 0
        failed = 0

        for c in certs:
            full_path = CertificateService.get_pdf_full_path(c)
            if full_path and os.path.isfile(full_path):
                already_valid += 1
                continue

            try:
                new_path = CertificateService.generate_pdf_for_certificate(c)
                print(f"  [OK] Repaired Cert ID={c.id} ({c.certificate_code}) -> {c.pdf_path}")
                repaired += 1
            except Exception as e:
                print(f"  [FAIL] Failed to repair Cert ID={c.id} ({c.certificate_code}): {e}")
                failed += 1

        print("\n" + "=" * 60)
        print(f"  Total Audited:  {len(certs)}")
        print(f"  Already Valid:  {already_valid}")
        print(f"  Repaired:       {repaired}")
        print(f"  Failed:         {failed}")
        print("=" * 60 + "\n")

        return failed == 0

if __name__ == '__main__':
    success = repair_all_certificates()
    sys.exit(0 if success else 1)
