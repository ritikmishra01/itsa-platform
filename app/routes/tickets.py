from flask import Blueprint, send_file, abort
from flask_login import login_required, current_user
from app.models.ticket import EventTicket
from app.models.registration import EventRegistration
from app.utils.responses import success_response, error_response
import os
from flask import current_app

tickets_bp = Blueprint('api_tickets', __name__, url_prefix='/api/v1/tickets')

@tickets_bp.route('/my', methods=['GET'])
@login_required
def get_my_tickets():
    regs = EventRegistration.query.filter_by(user_id=current_user.id, status='CONFIRMED').all()
    tickets = []
    for r in regs:
        if r.ticket and r.ticket.is_valid:
            t_data = r.ticket.to_dict()
            t_data['event'] = r.event.to_dict()
            tickets.append(t_data)
    return success_response(tickets)


@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    ticket = EventTicket.query.get_or_404(ticket_id)
    if ticket.registration.user_id != current_user.id and current_user.role != 'ADMIN':
        return error_response("AUTH_INSUFFICIENT_ROLE", "Unauthorized to view this ticket.", 403)
    return success_response(ticket.to_dict())
