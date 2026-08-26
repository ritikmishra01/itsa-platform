from app.models.user import User, StudentProfile, CoordinatorProfile
from app.models.event import EventCategory, Venue, Event, EventCoordinator
from app.models.registration import EventRegistration
from app.models.ticket import EventTicket
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import Feedback
from app.models.post import Post, PostMedia, PostReaction
from app.models.comment import Comment, CommentReply
from app.models.social import PostShare, SavedPost, Hashtag, PostHashtag, Mention
from app.models.notification import Notification
from app.models.gamification import ItsaPoints
from app.models.gallery import EventGallery, EventVolunteer
from app.models.report import Report
from app.models.ai_models import AiRecommendation, AiAnalysis
from app.models.audit import AuditLog

__all__ = [
    'User', 'StudentProfile', 'CoordinatorProfile',
    'EventCategory', 'Venue', 'Event', 'EventCoordinator',
    'EventRegistration', 'EventTicket', 'Attendance',
    'Certificate', 'Feedback',
    'Post', 'PostMedia', 'PostReaction',
    'Comment', 'CommentReply',
    'PostShare', 'SavedPost', 'Hashtag', 'PostHashtag', 'Mention',
    'Notification', 'ItsaPoints',
    'EventGallery', 'EventVolunteer',
    'Report', 'AiRecommendation', 'AiAnalysis', 'AuditLog'
]
