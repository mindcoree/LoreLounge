from .base import DomainError


class MediaFormatError(DomainError):
    def __init__(self, upload_content_type: str):
        super().__init__(f'Unsupported file type: {upload_content_type}. Allowed: JPEG, PNG, WEBP, GIF.')
class MediaSizeError(DomainError):
    def __init__(self, max_size_mb: int):
        super().__init__(f'File is too large. Maximum size is {max_size_mb} MB.')
