# ITSA Platform: Community & Social Engagement Architecture

## 1. Overview
The Community module provides a private, collegial social network designed specifically for the Information Technology Students' Association. Students and coordinators can publish technical achievements, share project updates, upload multimedia, react with distinct sentiments, discuss in threaded comments, and report inappropriate content for administrative moderation.

---

## 2. Core Features & Capabilities

### 2.1 Post Publishing & Formats
Users can create posts with flexible content types:
- **TEXT**: Discussion threads, project queries, technical announcements (up to 5,000 characters).
- **IMAGE**: Photographic highlights, design schematics, and achievement certificates (JPEG, PNG, WEBP with secure file hashing).
- **VIDEO**: Short project demos, workshop clips, or event teasers (MP4, MOV up to 100 MB).
- **EVENT-LINKED**: Posts linked directly to an active college event for seamless contextual discussion.

### 2.2 Reactions
The platform replaces binary likes with 5 expressive reaction types:
1. `LIKE` (👍) - Standard acknowledgment
2. `LOVE` (❤️) - Community appreciation
3. `CELEBRATE` (🎉) - Project milestones, contest wins, and hackathon victories
4. `INSIGHTFUL` (💡) - Thought-provoking technical shares and tutorials
5. `SUPPORT` (🤝) - Collaboration offers and mutual help

*Rules*: A user can have at most one reaction per post. Users can switch or withdraw their reaction at any time.

### 2.3 Comments & Threaded Replies
- Authenticated members can leave comments on any active community post.
- Single-level nested replies (`CommentReply`) prevent confusing deep discussion trees while maintaining clear dialog.
- Authors can edit or delete their own comments. Administrators hold global deletion privileges.

### 2.4 Mentions & Hashtags
- Dynamic extraction of `#hashtags` from post text automatically categorizes topics (e.g., `#webdev`, `#ai`, `#hackathon`).
- Automatic detection of `@mentions` triggers in-app notifications to tagged students or coordinators.

---

## 3. Moderation & Safety Pipeline

### 3.1 Community Reporting
Any authenticated user can flag a post or comment through the UI modal with standard reporting reasons:
- `SPAM` (Unsolicited promotional material)
- `INAPPROPRIATE` (Offensive language or unapproved imagery)
- `HARASSMENT` (Hostile comments or targeted bullying)
- `MISINFORMATION` (False scheduling or exam claims)
- `OTHER` (Detailed custom explanation)

### 3.2 Administrative Review (`/admin/community` & `/admin/reports`)
1. **Queued Reports**: Reported items appear in real-time on the Admin Control Center.
2. **AI Assistance**: Gemini API provides an initial advisory assessment (`is_violation`, `confidence`, and `recommended_action`).
3. **Admin Actions**:
   - **Dismiss Report**: Clears the flag and restores the item status.
   - **Deactivate Content**: Immediately hides the offending post or comment from the community feed.
   - **Suspend Account**: Automatically suspends repeat offenders with an immutable audit log record.

---

## 4. Backend Architecture & Database Mapping

- **Models**:
  - `Post` (`app/models/post.py`): Primary entity storing content, media links, and moderation status.
  - `PostMedia` (`app/models/post.py`): Media asset file paths, types, and order.
  - `PostReaction` (`app/models/post.py`): Unique constraint on `(post_id, user_id)`.
  - `Comment` & `CommentReply` (`app/models/comment.py`): Hierarchical discussion models.
  - `Report` (`app/models/report.py`): Administrative queue storing reporter ID, target item, and resolution status.
- **Service Layer**: `app/services/social_service.py` encapsulates all database operations, validation, and points distribution (rewarding ITSA points for engaging in discussions).