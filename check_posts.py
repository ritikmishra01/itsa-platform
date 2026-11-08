"""Quick diagnostic — check posts in DB and API endpoints."""
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    from app.models.post import Post
    
    total = Post.query.count()
    active = Post.query.filter_by(is_active=True).count()
    
    print(f"\n{'='*50}")
    print(f"TOTAL POSTS IN DB: {total}")
    print(f"ACTIVE POSTS: {active}")
    print(f"{'='*50}\n")
    
    if total > 0:
        print("First 5 posts:")
        for p in Post.query.order_by(Post.created_at.desc()).limit(5).all():
            author = p.author.full_name if p.author else "?"
            content = (p.content[:60] if p.content else "(no content)")
            print(f"  • ID {p.id} | {author}: {content}")
    else:
        print("No posts in DB yet.")

# Print all URL rules for posts and comments
print(f"\n{'='*50}")
print("POST & COMMENT ENDPOINTS")
print(f"{'='*50}\n")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    if 'post' in str(rule).lower() or 'comment' in str(rule).lower():
        print(f"  {rule.methods} {rule}")