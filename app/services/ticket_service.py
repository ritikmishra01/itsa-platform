import os
import uuid
import qrcode
from PIL import Image
from flask import current_app
from app.extensions import db
from app.models.ticket import EventTicket

class TicketService:
    @staticmethod
    def generate_ticket(registration_id):
        ticket_code = f"ITSA-TKT-{uuid.uuid4()}"

        # Create QR code with ticket_code only
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(ticket_code)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="#1a1a1a", back_color="#ffffff")

        # Save to uploads/tickets/
        tickets_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tickets')
        os.makedirs(tickets_dir, exist_ok=True)

        file_name = f"{ticket_code}.png"
        file_path = os.path.join(tickets_dir, file_name)
        qr_img.save(file_path)

        rel_path = f"uploads/tickets/{file_name}"

        ticket = EventTicket(
            registration_id=registration_id,
            ticket_code=ticket_code,
            qr_image_path=rel_path,
            is_valid=True
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def get_ticket_by_code(ticket_code):
        return EventTicket.query.filter_by(ticket_code=ticket_code).first()

    @staticmethod
    def invalidate_ticket(ticket_id):
        ticket = EventTicket.query.get(ticket_id)
        if ticket:
            ticket.is_valid = False
            db.session.commit()
            return True
        return False
