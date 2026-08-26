import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import (
    User, StudentProfile, CoordinatorProfile,
    EventCategory, Venue, Event, EventCoordinator,
    EventRegistration, EventTicket, Attendance,
    Certificate, Feedback, Post, PostMedia, PostReaction,
    Comment, CommentReply, PostShare, SavedPost,
    Hashtag, PostHashtag, Mention, Notification, ItsaPoints,
    EventGallery, EventVolunteer, Report, AiRecommendation,
    AiAnalysis, AuditLog
)

app = create_app('development')
with app.app_context():
    tables = db.metadata.tables.keys()
    print(f"Total tables mapped in SQLAlchemy metadata: {len(tables)}")
    print("Tables list:")
    for t in sorted(tables):
        print(f"  - {t}")
