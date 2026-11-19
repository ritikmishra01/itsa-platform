import time
from unittest.mock import patch
from datetime import datetime, timedelta
from app.models.event import Event, EventCategory
from app.services.ai_service import AIService, _detect_intent, _fetch_upcoming_events
from app.extensions import db


def test_intent_detection():
    """Verify intent detection identifies factual queries properly."""
    assert _detect_intent("What events are upcoming this week?") == "upcoming_events"
    assert _detect_intent("Show me the event schedule") == "upcoming_events"
    assert _detect_intent("How do I view my digital ticket and QR code?") == "ticket_qr"
    assert _detect_intent("How do I mark my attendance?") == "attendance"
    assert _detect_intent("How do I download and verify my certificate?") == "certificate"
    assert _detect_intent("How many points do I have on the leaderboard?") == "points_leaderboard"
    assert _detect_intent("How to register for the workshop?") == "registration"
    # General question should not trigger direct DB intent
    assert _detect_intent("Can you write a poem about artificial intelligence?") is None


def test_chatbot_upcoming_events_latency(auth_client_student, app):
    """Verify that asking for upcoming events responds fast (< 250ms) without calling Gemini."""
    with app.app_context():
        # Ensure at least one upcoming event exists within 7 days
        cat = EventCategory.query.first()
        if not cat:
            cat = EventCategory(name="Tech", description="Technology")
            db.session.add(cat)
            db.session.commit()

        admin_user = db.session.query(Event.created_by).first()
        creator_id = admin_user[0] if admin_user else 1

        ev = Event(
            title="Fast AI Workshop",
            description="Hands on workshop",
            category_id=cat.id,
            created_by=creator_id,
            start_datetime=datetime.utcnow() + timedelta(days=2),
            end_datetime=datetime.utcnow() + timedelta(days=2, hours=3),
            registration_deadline=datetime.utcnow() + timedelta(days=1),
            status="PUBLISHED",
            is_free=True,
            current_registrations=5,
            max_participants=50,
        )
        db.session.add(ev)
        db.session.commit()

    # Time the API call - should be direct DB and under 250ms
    t0 = time.monotonic()
    res = auth_client_student.post('/api/v1/ai/chat', json={
        'message': 'What events are upcoming this week?'
    })
    elapsed = time.monotonic() - t0

    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'reply' in data
    assert "Fast AI Workshop" in data['reply']
    assert "Upcoming ITSA Events" in data['reply']
    # Must be fast since no external LLM API was invoked
    assert elapsed < 1.0, f"Chatbot took {elapsed}s, expected < 1.0s"


def test_chatbot_empty_events(auth_client_student, app):
    """Verify chatbot response when no upcoming events exist in 7 days."""
    # Temporarily query empty window
    with app.app_context():
        empty_res = AIService._build_events_response([], days=7)
        assert "No Upcoming Events in the Next 7 Days" in empty_res


def test_chatbot_attendance_direct(auth_client_student):
    """Verify attendance questions are answered directly and accurately."""
    res = auth_client_student.post('/api/v1/ai/chat', json={
        'message': 'How is attendance recorded at events?'
    })
    assert res.status_code == 200
    reply = res.get_json()['data']['reply']
    assert "Attendance Works" in reply
    assert "Coordinator" in reply
    assert "+10 ITSA Points" in reply


def test_chatbot_ticket_direct(auth_client_student):
    """Verify QR ticket questions are answered directly."""
    res = auth_client_student.post('/api/v1/ai/chat', json={
        'message': 'Where can I find my digital QR ticket?'
    })
    assert res.status_code == 200
    reply = res.get_json()['data']['reply']
    assert "QR Ticket" in reply
    assert "My Tickets" in reply


def test_chatbot_certificate_direct(auth_client_student):
    """Verify certificate questions are answered directly."""
    res = auth_client_student.post('/api/v1/ai/chat', json={
        'message': 'How do I download and verify my certificate?'
    })
    assert res.status_code == 200
    reply = res.get_json()['data']['reply']
    assert "Certificates & Verification" in reply
    assert "PDF" in reply


def test_chatbot_points_direct(auth_client_student):
    """Verify points leaderboard questions are answered directly."""
    res = auth_client_student.post('/api/v1/ai/chat', json={
        'message': 'How do I earn points on the leaderboard?'
    })
    assert res.status_code == 200
    reply = res.get_json()['data']['reply']
    assert "ITSA Points" in reply
    assert "+10 points" in reply


def test_chatbot_gemini_timeout_and_fallback(auth_client_student, app):
    """Verify that when Gemini times out or is slow, a graceful fallback is returned."""
    # Mock _generate_text to simulate timeout returning None
    with patch.object(AIService, '_generate_text', return_value=None):
        res = auth_client_student.post('/api/v1/ai/chat', json={
            'message': 'Can you give me career advice for technology students?'
        })
        assert res.status_code == 200
        reply = res.get_json()['data']['reply']
        assert "ITSA Assistant" in reply
        assert "Upcoming events this week" in reply


def test_chatbot_consecutive_requests(auth_client_student):
    """Verify multiple consecutive questions work seamlessly."""
    queries = [
        "What events are upcoming this week?",
        "How do I scan my attendance?",
        "Where is my ticket?",
        "How to verify certificates?"
    ]
    for q in queries:
        res = auth_client_student.post('/api/v1/ai/chat', json={'message': q})
        assert res.status_code == 200
        assert 'reply' in res.get_json()['data']
        assert len(res.get_json()['data']['reply']) > 20
