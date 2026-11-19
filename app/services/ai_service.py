import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.event import Event, EventCategory
from app.models.user import User, StudentProfile
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.feedback import Feedback
from app.models.ai_models import AiRecommendation, AiAnalysis

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent keywords - used to decide whether to call Gemini or answer directly
# ---------------------------------------------------------------------------
_INTENT_PATTERNS = {
    'upcoming_events': [
        'upcoming', 'this week', 'next week', 'schedule', 'event list',
        'what events', 'any events', 'show events', 'events today',
        'events happening', 'event schedule', 'coming events', 'events on',
        'list events', 'calendar'
    ],
    'ticket_qr': [
        'ticket', 'qr', 'qr code', 'my ticket', 'digital ticket', 'scan',
        'ticket availability', 'seats left', 'seat availability'
    ],
    'attendance': [
        'attendance', 'attended', 'present', 'check in', 'check-in',
        'mark attendance', 'record attendance', 'scan attendance',
        'attendance information', 'how is attendance marked'
    ],
    'certificate': [
        'certificate', 'certificates', 'download certificate',
        'get certificate', 'verify certificate', 'certificate verification',
        'verify my certificate', 'certificate instructions'
    ],
    'points_leaderboard': [
        'point', 'points', 'score', 'leaderboard', 'rank', 'ranking',
        'how many points', 'my points', 'earn points', 'itsa points',
        'leaderboard points'
    ],
    'registration': [
        'register', 'registration', 'how to register', 'sign up', 'enroll',
        'registered', 'fee', 'deadline', 'seats', 'capacity'
    ],
}


def _detect_intent(message):
    """Return the matched intent key or None if Gemini should handle it."""
    lower = message.lower()
    for intent, keywords in _INTENT_PATTERNS.items():
        if any(kw in lower for kw in keywords):
            return intent
    return None


def _fetch_upcoming_events(days=7):
    """
    Optimised single-query fetch for events in the next `days` days.
    Uses joinedload to avoid N+1 queries on category and venue.
    Returns list of dicts with only the fields we need.
    """
    t0 = time.monotonic()
    now = datetime.utcnow()
    window_end = now + timedelta(days=days)

    rows = (
        Event.query
        .options(
            joinedload(Event.category),
            joinedload(Event.venue),
        )
        .filter(
            Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN', 'ONGOING']),
            Event.start_datetime >= now,
            Event.start_datetime <= window_end,
        )
        .order_by(Event.start_datetime.asc())
        .limit(10)
        .all()
    )

    elapsed = (time.monotonic() - t0) * 1000
    logger.info("[CHATBOT] DB query for upcoming events: %.1fms, found %d events", elapsed, len(rows))

    result = []
    for e in rows:
        seats_left = None
        if e.max_participants:
            seats_left = max(0, e.max_participants - e.current_registrations)
        result.append({
            'title': e.title,
            'category': e.category.name if e.category else 'General',
            'date': e.start_datetime.strftime('%a, %d %b %Y at %I:%M %p'),
            'venue': e.venue.name if e.venue else 'TBA',
            'status': e.status,
            'seats_left': seats_left,
            'is_free': e.is_free,
            'registration_deadline': (
                e.registration_deadline.strftime('%d %b %Y')
                if e.registration_deadline else 'N/A'
            ),
        })
    return result


def _call_gemini_with_timeout(prompt_text, api_key, timeout_secs=12):
    """
    Calls google.genai with a strict wall-clock timeout using a daemon thread.
    Returns the response text or None on timeout/error.
    """
    result = {'text': None, 'error': None}
    app = current_app._get_current_object()

    def _worker():
        try:
            from google import genai
            with app.app_context():
                client = genai.Client(api_key=api_key)
                cfg_model = app.config.get('GEMINI_MODEL', 'gemini-2.5-flash')
                models_to_try = list(dict.fromkeys([
                    cfg_model,
                    'gemini-2.5-flash',
                    'gemini-2.0-flash',
                    'gemini-1.5-flash',
                    'gemini-1.5-pro',
                ]))
                for m in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=m,
                            contents=prompt_text,
                        )
                        if response and response.text:
                            result['text'] = response.text.strip()
                            return
                    except Exception as model_err:
                        logger.debug("[CHATBOT] Model %s failed: %s", m, model_err)
                        continue
        except Exception as exc:
            result['error'] = str(exc)
            logger.warning("[CHATBOT] Gemini client error: %s", exc)

    t0 = time.monotonic()
    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout=timeout_secs)
    elapsed = (time.monotonic() - t0) * 1000

    if thread.is_alive():
        logger.warning("[CHATBOT] Gemini API timed out after %ds", timeout_secs)
        return None

    if result['text']:
        logger.info("[CHATBOT] Gemini responded in %.0fms", elapsed)
    elif result['error']:
        logger.warning("[CHATBOT] Gemini error in %.0fms: %s", elapsed, result['error'])

    return result['text']


class AIService:
    # ------------------------------------------------------------------
    # 1. GenAI: Google Gemini API
    # ------------------------------------------------------------------
    @classmethod
    def _generate_text(cls, prompt_text, timeout_secs=12):
        api_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            logger.warning("[CHATBOT] GEMINI_API_KEY not configured - using fallback")
            return None
        return _call_gemini_with_timeout(prompt_text, api_key, timeout_secs=timeout_secs)

    # ------------------------------------------------------------------
    # 2. Direct DB-backed response builders (no Gemini needed)
    # ------------------------------------------------------------------
    @staticmethod
    def _build_events_response(upcoming, days=7):
        if not upcoming:
            return (
                "📅 **No Upcoming Events in the Next {} Days**\n\n"
                "There are currently no scheduled events in the next {} days. "
                "Please visit the **Events** tab to browse all upcoming events or check back soon for new announcements!"
            ).format(days, days)
        lines = ["📅 **Upcoming ITSA Events (next {} days):**\n".format(days)]
        for e in upcoming:
            status_badge = {
                'REGISTRATION_OPEN': '🟢 Registration Open',
                'PUBLISHED':         '🔵 Published',
                'ONGOING':           '🟡 Ongoing',
            }.get(e['status'], e['status'])

            seats_info = ''
            if e['seats_left'] is not None:
                seats_info = " • 🪑 {} seats left".format(e['seats_left']) if e['seats_left'] > 0 else " • ⚠️ Full"

            free_info = "Free" if e['is_free'] else "Paid"
            lines.append(
                "• **{}** ({})\n"
                "  🗓️ {} | 📍 {}\n"
                "  {} | {}{}\n"
                "  ⏰ Register by: {}".format(
                    e['title'], e['category'],
                    e['date'], e['venue'],
                    status_badge, free_info, seats_info,
                    e['registration_deadline']
                )
            )
        lines.append("\nHead to the **Events** tab to register and get your QR ticket! 🎟️")
        return "\n\n".join(lines)

    @staticmethod
    def _build_ticket_response():
        return (
            "🎟️ **Your Digital QR Ticket & Availability**\n\n"
            "Once you register for an ITSA event:\n"
            "1. Your unique QR ticket is generated immediately and appears in **My Tickets**.\n"
            "2. At the venue entrance, the **Event Coordinator scans your QR code**.\n"
            "3. You do **NOT** scan anything yourself — simply show your ticket on your phone or printed copy.\n"
            "4. As soon as it is scanned, your attendance is officially recorded!\n\n"
            "Go to **My Tickets** in the sidebar to view your registered event tickets."
        )

    @staticmethod
    def _build_attendance_response():
        return (
            "✅ **How Attendance Works in ITSA**\n\n"
            "1. Register for an upcoming event to obtain your digital QR ticket.\n"
            "2. At the venue, present your QR code to the **Event Coordinator** at the check-in desk.\n"
            "3. The coordinator scans your QR code using the ITSA Scanner — attendance is marked instantly.\n"
            "4. Marking attendance automatically awards you **+10 ITSA Points**.\n"
            "5. Your verifiable **Certificate of Participation is automatically generated** upon check-in.\n\n"
            "You can view your verified attendances under the **Attendance** section."
        )

    @staticmethod
    def _build_certificate_response():
        return (
            "🎓 **ITSA Certificates & Verification**\n\n"
            "• **Issuance:** Certificates are automatically generated as soon as your attendance is scanned by a coordinator.\n"
            "• **Download:** Go to **Certificates** in the sidebar to download your certificates in high-resolution PDF format.\n"
            "• **Unique Code:** Every certificate includes a unique verification code and QR code.\n"
            "• **Verification:** Anyone can verify the authenticity of an ITSA certificate via the online Certificate Verification portal.\n\n"
            "Check your **Certificates** tab to view and download your earned credentials!"
        )

    @staticmethod
    def _build_points_response(user):
        points = 0
        if hasattr(user, 'student_profile') and user.student_profile:
            points = user.student_profile.total_points or 0
        return (
            "🏆 **Your ITSA Points: {} pts**\n\n"
            "**How to earn more points:**\n"
            "• 🎟️ Attend an event ➔ **+10 points**\n"
            "• 📝 Submit event feedback ➔ **+5 points**\n"
            "• ✍️ Register for an event ➔ **+3 points**\n"
            "• 💬 Post in Community ➔ **+2 points**\n"
            "• 💭 Comment on a post ➔ **+1 point**\n"
            "• 🤝 Volunteer at an event ➔ **+15 points**\n\n"
            "Check the **Leaderboard** to see your current rank among fellow students! 🌟"
        ).format(points)

    @staticmethod
    def _build_registration_response(upcoming):
        open_events = [e for e in upcoming if e['status'] == 'REGISTRATION_OPEN']
        if not open_events:
            return (
                "📝 **Event Registration**\n\n"
                "There are currently no events open for registration in the next 7 days.\n"
                "Visit the **Events** tab to browse all upcoming events and view registration opening dates!"
            )
        lines = ["📝 **Events Currently Open for Registration:**\n"]
        for e in open_events:
            seats_info = ''
            if e['seats_left'] is not None:
                seats_info = " | 🪑 {} seats left".format(e['seats_left']) if e['seats_left'] > 0 else " | ⚠️ Full"
            lines.append(
                "• **{}**\n"
                "  🗓️ {} | 📍 {}{}\n"
                "  ⏰ Register by: {}".format(
                    e['title'], e['date'], e['venue'], seats_info, e['registration_deadline']
                )
            )
        lines.append("\n👉 Navigate to **Events** ➔ select the event ➔ click **Register Now**! 🎟️")
        return "\n\n".join(lines)

    # ------------------------------------------------------------------
    # 3. Main chat method
    # ------------------------------------------------------------------
    @classmethod
    def chat_with_assistant(cls, user, user_message, conversation_history=None):
        """
        ITSA AI Assistant with intent detection.
        Factual questions about upcoming events, tickets, attendance, certificates,
        and points are answered directly from the database — no Gemini call needed.
        Only open-ended or complex questions are forwarded to Gemini with a timeout.
        """
        t_total = time.monotonic()
        msg_lower = user_message.lower().strip()

        # --- Step 1: detect intent ---
        intent = _detect_intent(user_message)
        logger.info("[CHATBOT] User='%s' intent='%s' msg='%s'", user.email, intent, user_message[:60])

        # --- Step 2: factual intents answered directly from DB (no Gemini) ---
        if intent in ('upcoming_events', 'registration', 'ticket_qr',
                      'attendance', 'certificate', 'points_leaderboard'):
            upcoming = _fetch_upcoming_events(days=7)

            if intent == 'upcoming_events':
                reply = cls._build_events_response(upcoming, days=7)
            elif intent == 'registration':
                reply = cls._build_registration_response(upcoming)
            elif intent == 'ticket_qr':
                reply = cls._build_ticket_response()
            elif intent == 'attendance':
                reply = cls._build_attendance_response()
            elif intent == 'certificate':
                reply = cls._build_certificate_response()
            else:  # points_leaderboard
                reply = cls._build_points_response(user)

            elapsed_ms = (time.monotonic() - t_total) * 1000
            logger.info("[CHATBOT] DB-only response delivered in %.0fms", elapsed_ms)
            return reply

        # --- Step 3: open-ended questions go to Gemini with context ---
        upcoming = _fetch_upcoming_events(days=14)
        event_context_lines = []
        for e in upcoming:
            event_context_lines.append(
                "- {} ({}) on {} at {}. Status: {}. Register by: {}.".format(
                    e['title'], e['category'], e['date'],
                    e['venue'], e['status'], e['registration_deadline']
                )
            )
        events_str = "\n".join(event_context_lines) if event_context_lines else "No upcoming events."

        profile_str = ""
        if user.is_student and user.student_profile:
            sp = user.student_profile
            profile_str = "Student: {}, Dept: {}, Year: {}, ITSA Points: {}.".format(
                user.full_name, sp.department, sp.year_of_study, sp.total_points
            )

        system_prompt = (
            "You are the ITSA AI Assistant for the Information Technology Students' Association platform.\n"
            "Help students with event discovery, registration, QR tickets, attendance, certificates, and ITSA points.\n\n"
            "{}\n\n"
            "Upcoming Events (next 14 days):\n"
            "{}\n\n"
            "Key Rules:\n"
            "1. Registration generates a unique QR digital ticket.\n"
            "2. Coordinator scans student QR at entrance (student does NOT scan).\n"
            "3. Attendance -> +10 ITSA points + Certificate auto-generated.\n"
            "4. Feedback -> +5 pts. Posts -> +2 pts. Comments -> +1 pt. Volunteering -> +15 pts.\n\n"
            "Be friendly, concise, and use clear formatting."
        ).format(profile_str, events_str)

        prompt = "{}\n\nUser: {}".format(system_prompt, user_message)
        gemini_response = cls._generate_text(prompt, timeout_secs=12)

        elapsed_ms = (time.monotonic() - t_total) * 1000
        logger.info("[CHATBOT] Total response time: %.0fms", elapsed_ms)

        if gemini_response:
            return gemini_response

        # --- Step 4: graceful fallback if Gemini unavailable ---
        logger.warning("[CHATBOT] Gemini unavailable - serving static fallback")
        if "event" in msg_lower:
            return cls._build_events_response(upcoming, days=14)
        return (
            "👋 **Hello! I'm your ITSA Assistant.**\n\n"
            "I can assist you instantly with:\n"
            "• 📅 Upcoming events this week\n"
            "• 🎟️ Your QR digital tickets and availability\n"
            "• ✅ Attendance recording & check-in process\n"
            "• 🎓 Certificate generation & verification\n"
            "• 🏆 ITSA Points breakdown & Leaderboard\n"
            "• 📝 Event registration details\n\n"
            "Try asking: *\"What events are upcoming this week?\"* or *\"How do I get my certificate?\"*"
        )

    # ------------------------------------------------------------------
    # 4. All other AI methods (unchanged)
    # ------------------------------------------------------------------
    @classmethod
    def generate_event_description(cls, title, category_name, start_date, venue_name, topics=None, audience=None):
        prompt = (
            "Generate a professional, engaging, 2-3 paragraph event description for a college technical/cultural event.\n"
            "Title: {}\nCategory: {}\nDate: {}\nVenue: {}\n"
            "Topics/Agenda: {}\nTarget Audience: {}\n\n"
            "Return only the clean description text without markdown headers."
        ).format(title, category_name, start_date, venue_name,
                 topics or 'Interactive hands-on session, expert discussion, and networking',
                 audience or 'All engineering and IT students')
        ai_res = cls._generate_text(prompt)
        if ai_res:
            return ai_res
        return "Join us for {}, an exciting {} session hosted by ITSA on {} at {}.".format(
            title, category_name, start_date, venue_name)

    @classmethod
    def generate_announcement(cls, event_title, date_str, venue_str, tone='formal', channel='email'):
        prompt = (
            "Generate an event announcement with a catchy subject line and clear call to action.\n"
            "Event: {}\nDate & Time: {}\nVenue: {}\nTone: {}\nChannel: {}\n\n"
            "Format with subject line on top followed by message body."
        ).format(event_title, date_str, venue_str, tone, channel)
        ai_res = cls._generate_text(prompt)
        if ai_res:
            return ai_res
        return (
            "Official Announcement: Registration is now open for {} taking place on {} at {}. "
            "Visit the ITSA platform to register and get your QR ticket!"
        ).format(event_title, date_str, venue_str)

    @classmethod
    def generate_social_caption(cls, event_title, highlights=None, preferred_hashtags=None):
        prompt = (
            "Create a short, exciting social media caption (under 280 characters) with emojis and hashtags.\n"
            "Event: {}\nHighlights: {}\nHashtags: {}"
        ).format(
            event_title,
            highlights or 'Hands-on learning, networking, certificates, ITSA points',
            preferred_hashtags or '#ITSA #Engineering #CampusLife'
        )
        ai_res = cls._generate_text(prompt)
        if ai_res:
            return ai_res
        return "Excited to announce {}! Don't miss out -- register today on the ITSA platform! #ITSA #CollegeLife #TechEvent".format(event_title)

    @classmethod
    def analyze_feedback(cls, event_id):
        feedbacks = Feedback.query.filter_by(event_id=event_id).all()
        if not feedbacks:
            return {
                'sentiment': 'NEUTRAL',
                'summary': 'No feedback submitted yet.',
                'positive_points': [],
                'negative_points': [],
                'suggestions': [],
                'score': 0.0
            }

        texts = [
            "Rating: {}/5. Comments: {}. Suggestions: {}".format(
                f.rating, f.content or 'None', f.suggestions or 'None'
            )
            for f in feedbacks
        ]
        combined_text = "\n".join(texts)

        prompt = (
            "Analyze the following student feedback for a college event and return a valid JSON object with exact keys:\n"
            '"sentiment" (POSITIVE, NEGATIVE, or NEUTRAL),\n'
            '"summary" (2-3 sentences),\n'
            '"positive_points" (list of strings),\n'
            '"negative_points" (list of strings),\n'
            '"suggestions" (list of strings),\n'
            '"score" (number from 0 to 100).\n\n'
            "Feedback Data:\n{}\n\n"
            "Return ONLY the raw JSON object, without backticks or markdown formatting."
        ).format(combined_text)

        ai_res = cls._generate_text(prompt)
        if ai_res:
            try:
                clean_json = ai_res.strip()
                if clean_json.startswith('```'):
                    clean_json = clean_json.split('```')[1]
                    if clean_json.startswith('json'):
                        clean_json = clean_json[4:]
                data = json.loads(clean_json)
                analysis_rec = AiAnalysis(
                    analysis_type='FEEDBACK_SENTIMENT',
                    related_id=event_id,
                    output_data=data,
                    model_version='gemini-2.5-flash'
                )
                db.session.add(analysis_rec)
                db.session.commit()
                return data
            except Exception:
                pass

        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
        sentiment = "POSITIVE" if avg_rating >= 3.8 else ("NEUTRAL" if avg_rating >= 2.8 else "NEGATIVE")
        return {
            'sentiment': sentiment,
            'summary': "Analyzed {} student responses. Average rating: {:.1f}/5.".format(len(feedbacks), avg_rating),
            'positive_points': ["Active student attendance", "Relevant technical topic"],
            'negative_points': ["More interactive lab time requested"],
            'suggestions': ["Provide lecture slides beforehand"],
            'score': round(avg_rating * 20, 1)
        }

    @classmethod
    def moderate_content(cls, content_text):
        prompt = (
            "Review the following student social post for community guideline violations "
            "(hate speech, bullying, extreme spam, harassment).\n"
            'Content: "{}"\n\n'
            "Return ONLY a JSON object with:\n"
            '"is_violation": boolean,\n'
            '"confidence": float between 0.0 and 1.0,\n'
            '"category": string (NONE, SPAM, HARASSMENT, HATE_SPEECH, INAPPROPRIATE),\n'
            '"recommendation": "approve" or "remove" or "review",\n'
            '"reason": "short explanation"'
        ).format(content_text)
        ai_res = cls._generate_text(prompt)
        if ai_res:
            try:
                clean_json = ai_res.strip()
                if clean_json.startswith('```'):
                    clean_json = clean_json.split('```')[1]
                    if clean_json.startswith('json'):
                        clean_json = clean_json[4:]
                return json.loads(clean_json)
            except Exception:
                pass

        bad_words = ['spam', 'abuse', 'hate', 'fake', 'scam', 'violence', 'harass']
        has_violation = any(w in content_text.lower() for w in bad_words)
        return {
            'is_violation': has_violation,
            'confidence': 0.7 if has_violation else 0.9,
            'category': 'SUSPICIOUS_KEYWORD' if has_violation else 'NONE',
            'recommendation': 'remove' if has_violation else 'approve',
            'reason': 'Content contains flagged keywords.' if has_violation else 'Content looks clean.'
        }

    # ------------------------------------------------------------------
    # 5. Machine Learning: Scikit-learn & Transparent Algorithms
    # ------------------------------------------------------------------
    @classmethod
    def recommend_events(cls, user, top_n=5):
        """
        Explainable Content-based recommendation using TF-IDF & Cosine Similarity.
        Matches student profile & past history with upcoming event tags and categories.
        """
        upcoming_events = (
            Event.query
            .options(joinedload(Event.category))
            .filter(
                Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN']),
                Event.start_datetime >= datetime.utcnow()
            )
            .all()
        )

        if not upcoming_events:
            return []

        interests = ""
        dept = ""
        if user.student_profile:
            interests = user.student_profile.interests or ""
            dept = user.student_profile.department or ""

        past_atts = Attendance.query.filter_by(user_id=user.id).all()
        past_cats = [a.event.category.name for a in past_atts if a.event and a.event.category]

        student_corpus = "{} {} {}".format(dept, interests, ' '.join(past_cats)).strip()

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            event_texts = []
            for e in upcoming_events:
                cat_name = e.category.name if e.category else ""
                tags = e.tags or ""
                event_texts.append("{} {} {} {}".format(e.title, cat_name, tags, e.description[:100]))

            if not student_corpus:
                sorted_events = sorted(upcoming_events, key=lambda x: x.current_registrations, reverse=True)[:top_n]
                return [{
                    'event_id': e.id,
                    'title': e.title,
                    'category_name': e.category.name if e.category else 'General',
                    'start_datetime': e.start_datetime.isoformat(),
                    'poster_image': e.poster_image,
                    'score': 0.85,
                    'reason': "Popular event in {}".format(e.category.name if e.category else 'ITSA')
                } for e in sorted_events]

            corpus = [student_corpus] + event_texts
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

            scored_events = []
            for idx, event in enumerate(upcoming_events):
                sim_score = float(similarities[idx])
                if dept.lower() in (event.category.name if event.category else "").lower():
                    sim_score = min(1.0, sim_score + 0.2)
                reason = "Matches your interest in {}".format(event.category.name if event.category else 'technology')
                if interests and any(w.lower() in event.title.lower() for w in interests.split(',')):
                    reason = "Matches your profile interest keywords"
                scored_events.append({
                    'event_id': event.id,
                    'title': event.title,
                    'category_name': event.category.name if event.category else 'General',
                    'start_datetime': event.start_datetime.isoformat(),
                    'poster_image': event.poster_image,
                    'score': round(max(0.5, sim_score), 2),
                    'reason': reason
                })

            scored_events.sort(key=lambda x: x['score'], reverse=True)
            return scored_events[:top_n]

        except Exception as e:
            logger.warning("Recommendation calculation fallback: %s", e)
            return [{
                'event_id': e.id,
                'title': e.title,
                'category_name': e.category.name if e.category else 'General',
                'start_datetime': e.start_datetime.isoformat(),
                'poster_image': e.poster_image,
                'score': 0.80,
                'reason': "Recommended for you"
            } for e in upcoming_events[:top_n]]

    @classmethod
    def calculate_engagement_score(cls, user):
        """
        Transparent student engagement score (0 - 100 scale).
        """
        if not user.is_student:
            return 0.0, {}

        atts = Attendance.query.filter_by(user_id=user.id, status='PRESENT').count()
        regs = EventRegistration.query.filter_by(user_id=user.id, status='CONFIRMED').count()
        fbs = Feedback.query.filter_by(user_id=user.id).count()
        from app.models.post import Post, PostReaction
        from app.models.comment import Comment
        posts = Post.query.filter_by(user_id=user.id, is_active=True).count()
        comments = Comment.query.filter_by(user_id=user.id, is_active=True).count()

        user_post_ids = [p.id for p in Post.query.filter_by(user_id=user.id).all()]
        reactions = PostReaction.query.filter(PostReaction.post_id.in_(user_post_ids)).count() if user_post_ids else 0

        from app.models.gallery import EventVolunteer
        volunteering = EventVolunteer.query.filter_by(user_id=user.id).count()

        raw_score = (
            (atts * 10) +
            (regs * 3) +
            (fbs * 5) +
            (posts * 2) +
            (comments * 1) +
            (reactions * 0.5) +
            (volunteering * 15)
        )

        max_expected = 150.0
        normalized_score = min(100.0, round((raw_score / max_expected) * 100.0, 1))

        breakdown = {
            'attendance_points': atts * 10,
            'registration_points': regs * 3,
            'feedback_points': fbs * 5,
            'community_points': (posts * 2) + comments + int(reactions * 0.5),
            'volunteer_points': volunteering * 15,
            'raw_total': raw_score,
            'normalized_score': normalized_score
        }
        return normalized_score, breakdown

    @classmethod
    def predict_registrations(cls, event_id):
        """
        Predicts turnout using Scikit-learn Random Forest Regressor trained on historical event features.
        """
        event = Event.query.get_or_404(event_id)

        similar_events = Event.query.filter(
            Event.category_id == event.category_id,
            Event.id != event.id
        ).all()

        if similar_events:
            avg_regs = sum(e.current_registrations for e in similar_events) / len(similar_events)
        else:
            avg_regs = 50.0

        from app.ai.turnout_predictor import EventTurnoutPredictor
        predictor = EventTurnoutPredictor.get_instance()
        prediction = predictor.predict(event, historical_avg=avg_regs)
        prediction['historical_events_analyzed'] = len(similar_events)
        return prediction
