import re
from datetime import datetime
from app.extensions import db
from app.models.post import Post, PostMedia, PostReaction
from app.models.comment import Comment, CommentReply
from app.models.social import PostShare, SavedPost, Hashtag, PostHashtag, Mention
from app.models.report import Report
from app.models.user import User
from app.services.gamification_service import GamificationService
from app.services.notification_service import NotificationService

HASHTAG_REGEX = re.compile(r'#(\w+)')
MENTION_REGEX = re.compile(r'@(\w+)')

class SocialService:
    @staticmethod
    def create_post(user_id, content, post_type='TEXT', event_id=None, media_files=None):
        if not content and not media_files:
            raise ValueError("Post must contain text content or media files.")

        post = Post(
            user_id=user_id,
            content=content.strip() if content else None,
            post_type=post_type,
            event_id=int(event_id) if event_id else None,
            is_active=True
        )
        db.session.add(post)
        db.session.flush()

        # Handle media files
        if media_files:
            for idx, media_info in enumerate(media_files):
                media = PostMedia(
                    post_id=post.id,
                    media_type=media_info.get('media_type', 'IMAGE'),
                    file_path=media_info.get('file_path'),
                    file_size=media_info.get('file_size'),
                    media_order=idx
                )
                db.session.add(media)

        # Process hashtags
        if content:
            tags = set(HASHTAG_REGEX.findall(content))
            for tag_name in tags:
                clean_tag = tag_name.lower().strip()
                tag = Hashtag.query.filter_by(name=clean_tag).first()
                if not tag:
                    tag = Hashtag(name=clean_tag, post_count=1)
                    db.session.add(tag)
                    db.session.flush()
                else:
                    tag.post_count += 1

                post_tag = PostHashtag(post_id=post.id, hashtag_id=tag.id)
                db.session.add(post_tag)

        # Process mentions
        if content:
            mentions = set(MENTION_REGEX.findall(content))
            for username in mentions:
                mentioned_user = User.query.filter(User.full_name.ilike(f"%{username}%")).first()
                if mentioned_user and mentioned_user.id != user_id:
                    mention = Mention(
                        post_id=post.id,
                        mentioned_user_id=mentioned_user.id,
                        mentioning_user_id=user_id
                    )
                    db.session.add(mention)
                    NotificationService.create_notification(
                        user_id=mentioned_user.id,
                        notif_type='MENTION',
                        title="You were mentioned in a post",
                        message=f"{post.author.full_name} mentioned you in a post.",
                        related_post_id=post.id
                    )

        # Award points (+2)
        GamificationService.award_points(user_id, 2, 'SOCIAL_POST', related_post_id=post.id)

        db.session.commit()
        return post

    @staticmethod
    def get_feed(page=1, per_page=20, user_id=None, hashtag=None, event_id=None):
        query = Post.query.filter_by(is_active=True)

        if hashtag:
            clean_tag = hashtag.lower().strip()
            query = query.join(PostHashtag).join(Hashtag).filter(Hashtag.name == clean_tag)

        if event_id:
            query = query.filter_by(event_id=int(event_id))

        query = query.order_by(Post.created_at.desc())
        total = query.count()
        posts = query.offset((page - 1) * per_page).limit(per_page).all()
        return posts, total

    @staticmethod
    def react_to_post(post_id, user_id, reaction_type='LIKE'):
        post = Post.query.get_or_404(post_id)
        existing = PostReaction.query.filter_by(post_id=post_id, user_id=user_id).first()

        if existing:
            if existing.reaction_type == reaction_type:
                # Toggle off / remove reaction
                db.session.delete(existing)
                db.session.commit()
                return None, "Reaction removed"
            else:
                existing.reaction_type = reaction_type
                db.session.commit()
                return existing, "Reaction updated"

        reaction = PostReaction(post_id=post_id, user_id=user_id, reaction_type=reaction_type)
        db.session.add(reaction)

        # Notify post author if not reacting to own post
        if post.user_id != user_id:
            user = User.query.get(user_id)
            NotificationService.create_notification(
                user_id=post.user_id,
                notif_type='POST_REACTION',
                title="New Reaction on Your Post",
                message=f"{user.full_name} reacted '{reaction_type}' to your post.",
                related_post_id=post.id
            )

        db.session.commit()
        return reaction, "Reaction added"

    @staticmethod
    def add_comment(post_id, user_id, content):
        if not content or not content.strip():
            raise ValueError("Comment cannot be empty.")

        post = Post.query.get_or_404(post_id)
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content.strip(),
            is_active=True
        )
        db.session.add(comment)

        # Award points (+1)
        GamificationService.award_points(user_id, 1, 'SOCIAL_POST', related_post_id=post.id)

        # Notify author
        if post.user_id != user_id:
            user = User.query.get(user_id)
            NotificationService.create_notification(
                user_id=post.user_id,
                notif_type='POST_COMMENT',
                title="New Comment on Your Post",
                message=f"{user.full_name} commented: '{content[:50]}...'",
                related_post_id=post.id
            )

        db.session.commit()
        return comment

    @staticmethod
    def add_reply(comment_id, user_id, content, mentioned_user_id=None):
        if not content or not content.strip():
            raise ValueError("Reply cannot be empty.")

        comment = Comment.query.get_or_404(comment_id)
        reply = CommentReply(
            comment_id=comment_id,
            user_id=user_id,
            content=content.strip(),
            mentioned_user_id=mentioned_user_id,
            is_active=True
        )
        db.session.add(reply)

        if comment.user_id != user_id:
            user = User.query.get(user_id)
            NotificationService.create_notification(
                user_id=comment.user_id,
                notif_type='POST_COMMENT',
                title="New Reply to Your Comment",
                message=f"{user.full_name} replied to your comment.",
                related_post_id=comment.post_id
            )

        db.session.commit()
        return reply

    @staticmethod
    def save_post(post_id, user_id):
        existing = SavedPost.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return False # Unsaved

        saved = SavedPost(post_id=post_id, user_id=user_id)
        db.session.add(saved)
        db.session.commit()
        return True # Saved

    @staticmethod
    def report_content(reporter_id, reason, description=None, post_id=None, comment_id=None, user_id=None):
        report = Report(
            reporter_id=reporter_id,
            reported_post_id=post_id,
            reported_comment_id=comment_id,
            reported_user_id=user_id,
            reason=reason,
            description=description.strip() if description else None,
            status='PENDING'
        )
        db.session.add(report)

        if post_id:
            post = Post.query.get(post_id)
            if post:
                post.is_reported = True

        db.session.commit()
        return report
