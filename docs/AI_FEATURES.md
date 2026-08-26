# AI Features — ITSA Platform

---

## SECTION 1: GenAI Features (Google Gemini API)

### 1.1 ITSA AI Chatbot

**Purpose**: A 24/7 AI assistant that answers student questions about ITSA events, procedures, and the platform.

**Technology**: Google Gemini API (`gemini-2.0-flash`)

| Property | Value |
|---|---|
| Endpoint | POST /api/v1/ai/chat |
| Auth | Required (STUDENT) |
| Rate Limit | 20 messages/hour/user |
| Input | User message (max 1000 chars) + conversation history (last 10 turns) |
| Output | AI text response |

**What it can answer**:
- Upcoming events, event details
- How to register, cancel, get tickets
- ITSA points and leaderboard
- Certificate download and verification
- Platform usage guidance

**What it cannot do**:
- Access real-time database (pass event context via system prompt)
- Make booking actions on behalf of the student
- Access personal data of other students

**Safety**: Gemini safety filters enabled. Input sanitized. System prompt guards against prompt injection.

---

### 1.2 AI Event Description Generator

**Purpose**: Auto-generate professional event descriptions for coordinators and admin during event creation.

| Property | Value |
|---|---|
| Endpoint | POST /api/v1/ai/generate-description |
| Auth | Required (ADMIN, COORDINATOR) |
| Rate Limit | 10 requests/hour/user |
| Input | title, category, date, venue, topics[], target_audience |
| Output | 2-3 paragraph professional description (max 800 words) |

**Use Case**: Coordinator fills in basic event details → clicks "Generate Description" → AI fills in the description field → Coordinator can edit before saving.

---

### 1.3 AI Event Announcement Generator

**Purpose**: Generate ready-to-publish announcements for email newsletters or the social feed.

| Input | Output |
|---|---|
| event_id, tone (formal/casual), channel (email/social/notice) | Complete announcement text with subject line |

---

### 1.4 AI Social Caption Generator

**Purpose**: Generate engaging captions for event-related social posts.

| Input | Output |
|---|---|
| event_name, highlights, preferred_hashtags[] | Caption text (max 300 chars) with hashtags and emojis |

---

### 1.5 AI Feedback Sentiment Analysis

**Purpose**: Analyze all feedback for an event and produce a structured summary for coordinators.

| Property | Value |
|---|---|
| Endpoint | POST /api/v1/ai/analyze-feedback |
| Auth | Required (ADMIN, COORDINATOR assigned) |
| Input | event_id → fetches all feedback texts and ratings (anonymized) |
| Output | Structured analysis |

**Output Format**:
```json
{
  "overall_sentiment": "POSITIVE",
  "avg_rating": 4.2,
  "total_responses": 45,
  "key_themes": ["Good hands-on activities", "Expert speakers", "Venue too small"],
  "strengths": ["Clear explanations", "Practical demonstrations"],
  "improvements": ["More time needed", "Better audio system"],
  "representative_quotes": ["Excellent workshop!", "Very informative session"],
  "ai_score": 82
}
```

**Privacy**: Feedback is anonymized before sending to Gemini. No student names or IDs included.

---

### 1.6 AI Comment Moderation

**Purpose**: Assist admin in reviewing reported content by providing an AI recommendation.

| Property | Value |
|---|---|
| Endpoint | POST /api/v1/ai/moderate-content |
| Auth | Required (ADMIN) |
| Input | content_text (reported post or comment) |
| Output | Moderation recommendation |

**Output Format**:
```json
{
  "is_violation": false,
  "confidence": 0.87,
  "category": "NONE",
  "recommendation": "approve",
  "reason": "Content is appropriate and does not violate guidelines"
}
```

**Categories**: SPAM, HARASSMENT, HATE_SPEECH, MISINFORMATION, INAPPROPRIATE, NONE

**IMPORTANT**: AI provides a recommendation only. The **human admin** makes the final decision. AI moderation is advisory, not automated enforcement.

---

## SECTION 2: Machine Learning Features (Scikit-learn)

### 2.1 AI Event Recommendation System

**Purpose**: Recommend the most relevant upcoming events to each student.

**Technology**: Content-based filtering using TF-IDF vectorization and cosine similarity.

**Input Features**:
| Feature | Source | Encoding |
|---|---|---|
| Event category | events.category_id | Label encoding |
| Student department | student_profiles.department | Label encoding |
| Student year | student_profiles.year_of_study | Numeric |
| Student interests | student_profiles.interests | TF-IDF |
| Event tags | events.tags | TF-IDF |
| Past registrations | event_registrations | Category frequency |
| Past attendance | attendance | Category frequency |

**Algorithm**:
1. Build event feature matrix (category + tags TF-IDF)
2. Build student preference vector (interests + historical categories)
3. Compute cosine similarity between student vector and all upcoming events
4. Return top 5 events sorted by similarity score

**Cold Start Problem**: New students with no history → Fall back to top 5 most popular events in their department.

**Output**:
```json
[
  {
    "event_id": 12,
    "title": "Python Workshop",
    "score": 0.87,
    "reason": "Based on your interest in programming and past workshop attendance"
  }
]
```

**Model Storage**: `app/ai/ml_models/recommendation_model.joblib`

**Retraining**: Triggered weekly via a script or after a set number of new attendance records.

**Evaluation Metrics**: Precision@5, Recall@5

---

### 2.2 AI Registration Prediction

**Purpose**: Predict how many students will register for a future event, to help coordinators plan resources.

**Technology**: Random Forest Regressor (Scikit-learn)

**Input Features**:
| Feature | Description |
|---|---|
| category_encoded | Event category (label encoded) |
| day_of_week | 0=Monday to 6=Sunday |
| hour_of_start | Event start hour (0-23) |
| is_weekend | Boolean |
| duration_hours | Event duration |
| venue_capacity | Max venue capacity |
| historical_avg_category | Avg registrations for this category |
| days_until_event | Lead time |

**Output**:
```json
{
  "predicted_count": 45,
  "confidence_interval": [35, 55],
  "confidence": "medium",
  "model_version": "v1",
  "data_points_used": 24
}
```

**Limitations**:
- Accuracy improves with more historical events (needs 20+ for reliable predictions)
- Does not account for extraordinary events (holidays, exam season)
- Confidence reported as low/medium/high based on data availability

**Retraining**: After each event completes (when final registration count is known).

---

### 2.3 AI Student Engagement Score

**Purpose**: A transparent, fair score (0-100) that quantifies how engaged a student is with ITSA.

**Formula**:
```
raw_score = (
    (events_attended * 10) +
    (events_registered * 3) +
    (feedback_submitted * 5) +
    (posts_created * 2) +
    (comments_made * 1) +
    (reactions_received * 0.5) +
    (volunteering_events * 15)
)

normalized_score = min(100, (raw_score / max_possible_score) * 100)
```

**Weights Rationale**:
| Activity | Points | Reasoning |
|---|---|---|
| Attending event | 10 | Highest — shows real commitment |
| Volunteering | 15 | Goes above student role |
| Submitting feedback | 5 | Helps ITSA improve |
| Registering | 3 | Shows intent |
| Creating post | 2 | Community building |
| Commenting | 1 | Minor engagement |
| Reactions received | 0.5 | Passive metric |

**Normalization**: `max_possible_score` is calculated based on current semester activity levels.

**Display**: Score shown on student profile and leaderboard with a breakdown.

**Update Frequency**: Recalculated after each activity.

---

### 2.4 AI Attendance Analytics

**Purpose**: Analyze attendance patterns to identify trends and potential issues.

**Technology**: Pandas aggregations + basic ML clustering (optional)

**Metrics Calculated**:
- Attendance rate per event: `(attended / registered) * 100`
- No-show rate
- Department-wise attendance comparison
- Year-wise attendance comparison
- Time-of-day attendance patterns
- Category-wise attendance trends

**Output** (for Chart.js visualization):
```json
{
  "attendance_rate": 87.5,
  "no_show_rate": 12.5,
  "by_department": [{"dept": "CS", "rate": 92}, ...],
  "by_year": [{"year": 1, "rate": 85}, ...],
  "trend": "improving"
}
```
