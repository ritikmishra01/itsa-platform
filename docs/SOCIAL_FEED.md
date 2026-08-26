# Social Feed — ITSA Platform

## Overview

A college community feed where ITSA students share posts, photos, videos, and engage with each other's content.

## Post Types

| Type | Description |
|---|---|
| TEXT | Text-only post (max 5000 chars) |
| IMAGE | 1-5 images (max 10MB each, JPEG/PNG/WEBP) |
| VIDEO | 1 video (max 100MB, MP4/MOV) |
| MIXED | Text + images or text + video |

## Feed Algorithm

Chronological order (newest first). Simple and transparent. No hidden ranking.
Pagination: 20 posts per page. Infinite scroll on frontend.

## Reactions (5 types)

LIKE, LOVE, CELEBRATE, INSIGHTFUL, SUPPORT

One reaction per user per post. User can change their reaction type. Reaction counts displayed per type.

## Comments

- Max 2000 characters
- Edit own comment
- Delete own comment
- Admin can delete any comment
- Nested: comment → replies (1 level only)

## Replies

- Max 1000 characters  
- Can mention one user (@username)
- No reply-to-reply nesting

## Hashtags

Auto-detected from #hashtag pattern in post/comment content.
Trending hashtags: sorted by post_count descending.
Hashtag pages: /hashtags/{name} shows all posts.

## Mentions

Auto-detected from @username in content.
Creates a MENTION notification for the mentioned user.
Username displayed as a profile link in the rendered post.

## Sharing

Share to ITSA feed: Creates a new post entry with reference to original.
External share: Records a EXTERNAL share event (no new post created).

## Content Reporting

Report reasons: SPAM, INAPPROPRIATE, HARASSMENT, MISINFORMATION, OTHER
Reports go to admin queue. AI moderation assists (advisory only).
Admin actions: Approve (dismiss report), Remove post/comment, Warn/Suspend user.

## Post Deletion Cascade

Deleting a post removes: post_media, post_reactions, comments, comment_replies, post_shares, saved_posts, post_hashtags, mentions linked to post.

## Privacy

All posts visible to all authenticated ITSA members. No private posts in v1.
