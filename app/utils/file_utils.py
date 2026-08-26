import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'png', 'jpg'}

def is_allowed_file(filename, allowed_extensions):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def save_uploaded_file(file_storage, subfolder='profiles', allowed_extensions=ALLOWED_IMAGE_EXTENSIONS):
    """
    Saves an uploaded file with a UUID name into uploads/<subfolder>.
    Returns the relative path or None on failure.
    """
    if not file_storage or file_storage.filename == '':
        return None

    if not is_allowed_file(file_storage.filename, allowed_extensions):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")

    original_filename = secure_filename(file_storage.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'dat'
    new_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    dest_path = os.path.join(upload_dir, new_filename)
    file_storage.save(dest_path)

    # Return relative URL path
    return f"uploads/{subfolder}/{new_filename}".replace('\\', '/')
