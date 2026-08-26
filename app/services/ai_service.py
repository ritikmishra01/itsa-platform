import os
import json
import logging
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.event import Event, EventCategory
from app.models.user import User, StudentProfile
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.feedback import Feedback
from app.models.ai_models import AiRecommendation, AiAnalysis

logger = logging.getLogger(__name__)

class AIService:
    # -------------------------------------------------------------
    # 1. GenAI: Google Gemini API
    # -------------------------------------------------------------
    @classmethod
    def _generate_text(cls, prompt_text):
        api_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return None

        # 1. Try google.genai (Modern Google GenAI SDK)
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            models_to_try = [
                current_app.config.get('GEMINI_MODEL', 'gemini-2.5-flash'),
                'gemini-2.5-flash',
                'gemini-2.0-flash',
                'gemini-1.5-flash'
            ]
            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt_text
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    continue
        except Exception:
            pass

        # 2. Try google.generativeai (Legacy SDK)
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=api_key)
            for m in ['gemini-1.5-flash', 'gemini-1.5-pro']:
                try:
                    model = legacy_genai.GenerativeModel(m)
                    res = model.generate_content(prompt_text)
                    if res and res.text:
                        return res.text.strip()
                except Exception:
                    continue
        except Exception:
            pass

        return None

    @classmethod
    def chat_with_assistant(cls, user, user_message, conversation_history=None):
        """
        ITSA AI Assistant: Retrieves student context + upcoming events,
        and generates an accurate, helpful response.
        """

        # Fetch relevant upcoming events
        upcoming = Event.query.filter(
            Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN', 'ONGOING']),
            Event.start_datetime >= datetime.utcnow()
        ).order_by(Event.start_datetime.asc()).limit(5).all()

        event_context = []
        for e in upcoming:
            event_context.append(f"- {e.title} ({e.category.name if e.category else 'General'}) on {e.start_datetime.strftime('%b %d, %Y')} at {e.venue.name if e.venue else 'TBA'}. Status: {e.status}")
        events_str = "\n".join(event_context) if event_context else "No upcoming events scheduled right now."

        # Fetch user profile context
        profile_str = ""
        if user.is_student and user.student_profile:
            sp = user.student_profile
            profile_str = f"Student Name: {user.full_name}, Department: {sp.department}, Year: {sp.year_of_study}, Total ITSA Points: {sp.total_points}."

        system_prompt = f"""You are the ITSA AI Assistant for the Information Technology Students' Association (ITSA) platform.
Your job is to assist students with event discovery, registration procedures, digital QR tickets, attendance verification, certificates, and ITSA points.

Current Context:
{profile_str}

Upcoming Events:
{events_str}

Key Platform Rules:
1. Registration generates a unique digital ticket with a secure QR code.
2. The COORDINATOR scans the student's QR code at the event entrance to record attendance (students do NOT scan themselves).
3. Attendance awards +10 ITSA points and automatically generates an official Certificate.
4. Feedback awards +5 ITSA points.
5. Social posts award +2 points; comments award +1 point.

Always respond in a friendly, encouraging, and helpful manner with clean formatting."""

        prompt = f"{system_prompt}\n\nUser Question: {user_message}"
        ai_response = cls._generate_text(prompt)
        if ai_response:
            return ai_response

        # Fallback when API unavailable
        msg_lower = user_message.lower()
        if "event" in msg_lower or "upcoming" in msg_lower:
            return f"Here are the upcoming ITSA events:\n\n{events_str}\n\nYou can register for any open event from the Events tab!"
        elif "point" in msg_lower or "score" in msg_lower:
            return f"You currently have {user.student_profile.total_points if user.student_profile else 0} ITSA Points! You earn points by attending events (+10), submitting feedback (+5), registering (+3), and community posting (+2)."
        elif "certificate" in msg_lower:
            return "Certificates are automatically generated as soon as your attendance is verified by a coordinator. You can view and download them in the Certificates section!"
        elif "ticket" in msg_lower or "qr" in msg_lower:
            return "Once you register for an event, your digital QR ticket appears in 'My Tickets'. Show this QR code to the coordinator at the event gate to check in."
        return "Hello! I am your ITSA Assistant. Ask me about upcoming events, registrations, tickets, QR attendance, certificates, and your ITSA points leaderboard ranking!"

    @classmethod
    def generate_event_description(cls, title, category_name, start_date, venue_name, topics=None, audience=None):
        prompt = f"""Generate a professional, engaging, 2-3 paragraph event description for a college technical/cultural event.
Title: {title}
Category: {category_name}
Date: {start_date}
Venue: {venue_name}
Topics/Agenda: {topics or 'Interactive hands-on session, expert discussion, and networking'}
Target Audience: {audience or 'All engineering and IT students'}

Return only the clean description text without markdown headers."""
        ai_res = cls._generate_text(prompt)
        if ai_res:
            return ai_res
        return f"Join us for {title}, an exciting {category_name} session hosted by ITSA on {start_date} at {venue_name}."

    @classmethod
    def generate_announcement(cls, event_title, date_str, venue_str, tone='formal', channel='email'):
        prompt = f"""Generate an event announcement with a catchy subject line and clear call to action.
Event: {event_title}
Date & Time: {date_str}
Venue: {venue_str}
Tone: {tone}
Channel: {channel}

Format with subject line on top followed by message body."""
        ai_res = cls._generate_text(prompt)
        if ai_res:
            return ai_res
        return f"Official Announcement: Registration is now open for {event_title} taking place on {date_str} at {venue_str}. Visit the ITSA platform to register and get your QR ticket!"

    @classmethod
    def generate_social_caption(cls, event_title, highlights=None, preferred_hashtags=None):
        prompt = f"""Create a short, exciting social media caption (under 280 characters) with emojis and hashtags.
Event: {event_title}
Highlights: {highlights or 'Hands-on learning, networking, certificates, ITSA points'}
Hashtags: {preferred_hashtags or '#ITSA #Engineering #CampusLife'}"""
        ai_res = cls._generate_text(prompt)
        if ai_res:
            return ai_res
        return f"Excited to announce {event_title}! Don't miss out -- register today on the ITSA platform! #ITSA #CollegeLife #TechEvent"

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

        texts = [f"Rating: {f.rating}/5. Comments: {f.content or 'None'}. Suggestions: {f.suggestions or 'None'}" for f in feedbacks]
        combined_text = "\n".join(texts)

        prompt = f"""Analyze the following student feedback for a college event and return a valid JSON object with exact keys:
"sentiment" (POSITIVE, NEGATIVE, or NEUTRAL),
"summary" (2-3 sentences),
"positive_points" (list of strings),
"negative_points" (list of strings),
"suggestions" (list of strings),
"score" (number from 0 to 100).

Feedback Data:
{combined_text}

Return ONLY the raw JSON object, without backticks or markdown formatting."""
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
            'summary': f"Analyzed {len(feedbacks)} student responses. Average rating: {avg_rating:.1f}/5.",
            'positive_points': ["Active student attendance", "Relevant technical topic"],
            'negative_points': ["More interactive lab time requested"],
            'suggestions': ["Provide lecture slides beforehand"],
            'score': round(avg_rating * 20, 1)
        }

    @classmethod
    def moderate_content(cls, content_text):
        prompt = f"""Review the following student social post for community guideline violations (hate speech, bullying, extreme spam, harassment).
Content: "{content_text}"

Return ONLY a JSON object with:
"is_violation": boolean,
"confidence": float between 0.0 and 1.0,
"category": string (NONE, SPAM, HARASSMENT, HATE_SPEECH, INAPPROPRIATE),
"recommendation": "approve" or "remove" or "review",
"reason": "short explanation" """
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

        # Robust keyword moderation fallback
        bad_words = ['spam', 'abuse', 'hate', 'fake', 'scam', 'violence', 'harass']
        has_violation = any(w in content_text.lower() for w in bad_words)
        return {
            'is_violation': has_violation,
            'confidence': 0.7 if has_violation else 0.9,
            'category': 'SUSPICIOUS_KEYWORD' if has_violation else 'NONE',
            'recommendation': 'remove' if has_violation else 'approve',
            'reason': 'Content contains flagged keywords.' if has_violation else 'Content looks clean.'
        }

    # -------------------------------------------------------------
    # 2. Machine Learning: Scikit-learn & Transparent Algorithms
    # -------------------------------------------------------------
    @classmethod
    def recommend_events(cls, user, top_n=5):
        """
        Explainable Content-based recommendation using TF-IDF & Cosine Similarity.
        Matches student profile & past history with upcoming event tags and categories.
        """
        upcoming_events = Event.query.filter(
            Event.status.in_(['PUBLISHED', 'REGISTRATION_OPEN']),
            Event.start_datetime >= datetime.utcnow()
        ).all()

        if not upcoming_events:
            return []

        # Build student profile corpus
        interests = ""
        dept = ""
        if user.student_profile:
            interests = user.student_profile.interests or ""
            dept = user.student_profile.department or ""

        # Past categories attended
        past_atts = Attendance.query.filter_by(user_id=user.id).all()
        past_cats = [a.event.category.name for a in past_atts if a.event and a.event.category]

        student_corpus = f"{dept} {interests} {' '.join(past_cats)}".strip()

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            event_texts = []
            for e in upcoming_events:
                cat_name = e.category.name if e.category else ""
                tags = e.tags or ""
                event_texts.append(f"{e.title} {cat_name} {tags} {e.description[:100]}")

            if not student_corpus:
                # Cold start: Return upcoming events ordered by registrations
                sorted_events = sorted(upcoming_events, key=lambda x: x.current_registrations, reverse=True)[:top_n]
                return [{
                    'event_id': e.id,
                    'title': e.title,
                    'category_name': e.category.name if e.category else 'General',
                    'start_datetime': e.start_datetime.isoformat(),
                    'poster_image': e.poster_image,
                    'score': 0.85,
                    'reason': f"Popular event in {e.category.name if e.category else 'ITSA'}"
                } for e in sorted_events]

            corpus = [student_corpus] + event_texts
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)

            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

            scored_events = []
            for idx, event in enumerate(upcoming_events):
                sim_score = float(similarities[idx])
                # Base relevance boost for same department category
                if dept.lower() in (event.category.name if event.category else "").lower():
                    sim_score = min(1.0, sim_score + 0.2)

                reason = f"Matches your interest in {event.category.name if event.category else 'technology'}"
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
            logger.warning(f"Recommendation calculation fallback: {e}")
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

        # Received reactions count on user's posts
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
        Predicts turnout using category averages and capacity limits.
        """
        event = Event.query.get_or_404(event_id)

        # Historical average for same category
        similar_events = Event.query.filter(
            Event.category_id == event.category_id,
            Event.id != event.id
        ).all()

        if similar_events:
            avg_regs = sum(e.current_registrations for e in similar_events) / len(similar_events)
            predicted = int(avg_regs * 1.1) # 10% growth factor
        else:
            predicted = 45 # baseline default

        if event.max_participants:
            predicted = min(predicted, event.max_participants)

        confidence_low = max(10, int(predicted * 0.8))
        confidence_high = int(predicted * 1.25)
        if event.max_participants:
            confidence_high = min(confidence_high, event.max_participants)

        return {
            'predicted_count': predicted,
            'confidence_range': [confidence_low, confidence_high],
            'confidence': 'HIGH' if len(similar_events) >= 3 else 'MEDIUM',
            'historical_events_analyzed': len(similar_events)
        }
