# File Uploads — ITSA Platform

## Upload Categories

| Category | Max Size | Allowed Types | Storage Path |
|---|---|---|---|
| Profile image | 2MB | JPEG, PNG, WEBP | uploads/profiles/ |
| Event poster | 5MB | JPEG, PNG, WEBP | uploads/events/posters/ |
| Post images | 10MB each | JPEG, PNG, WEBP | uploads/posts/images/ |
| Post video | 100MB | MP4, MOV, AVI | uploads/posts/videos/ |
| Gallery media | 20MB | JPEG, PNG, WEBP, MP4 | uploads/gallery/ |
| QR tickets | Auto | PNG (generated) | uploads/tickets/ |
| Certificates | Auto | PDF (generated) | uploads/certificates/ |

## Upload Process

1. Receive file from equest.files
2. Check file exists and not empty
3. Extract extension: ilename.rsplit('.', 1)[1].lower()
4. Validate extension against whitelist for category
5. Validate MIME type (read file header bytes — python-magic or imghdr)
6. Check file size against category limit
7. Apply secure_filename(original_name) (removes path traversal chars)
8. Generate UUID filename: "{uuid.uuid4()}.{extension}"
9. Save to appropriate directory
10. Store relative path in database

## Access Control

| File Type | Access |
|---|---|
| Profile images | Public (served directly) |
| Event posters | Public |
| Post images/videos | Authenticated users |
| Gallery | Authenticated users |
| QR tickets | Ticket owner only |
| Certificates | Certificate owner only (public verify via code) |

## Serving Protected Files

`python
@app.route('/uploads/tickets/<filename>')
@login_required
def serve_ticket(filename):
    ticket = EventTicket.query.filter_by(
        qr_image_path=f"uploads/tickets/{filename}"
    ).first_or_404()
    if ticket.registration.user_id != current_user.id and current_user.role != 'ADMIN':
        abort(403)
    return send_from_directory('uploads/tickets', filename)
`

## Security Rules

- Never trust original filename
- Never execute uploaded files
- UUID naming prevents path traversal and collisions
- Validate content type independently of extension
- Set Nginx/Gunicorn to prevent script execution in uploads directory

## Storage Note (Render)

Render has an ephemeral filesystem — uploads are lost on restarts.
For production, migrate to Cloudinary or Amazon S3.
Document this limitation clearly for the deployment team.
