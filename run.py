import os
from app import create_app, db
from app.models import (
    User, StudentProfile, CoordinatorProfile,
    EventCategory, Venue, Event, EventCoordinator,
    EventRegistration, EventTicket, Attendance,
    Certificate, Feedback, Post, Comment, Notification, ItsaPoints
)

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Event': Event,
        'EventRegistration': EventRegistration,
        'Attendance': Attendance,
        'Certificate': Certificate
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=port, debug=debug)
