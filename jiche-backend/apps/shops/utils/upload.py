import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.validators import validate_image_file_extension
from django.core.exceptions import ValidationError


ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/jpg'}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024


def save_uploaded_image(uploaded_file) -> str:
    if uploaded_file.size > MAX_UPLOAD_SIZE:
        raise ValidationError('图片大小不能超过5M')
    if uploaded_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError('仅支持 jpg/png 格式')

    try:
        validate_image_file_extension(uploaded_file)
    except ValidationError as exc:
        raise ValidationError('仅支持 jpg/png 格式') from exc

    ext = os.path.splitext(uploaded_file.name)[1].lower() or '.jpg'
    filename = f'uploads/{uuid.uuid4().hex}{ext}'
    saved_path = default_storage.save(filename, uploaded_file)
    return f'{settings.MEDIA_URL.rstrip("/")}/{saved_path}'
