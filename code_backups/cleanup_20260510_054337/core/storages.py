from django.conf import settings
from django.core.files.storage import FileSystemStorage


class ProtectedAudioStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        location = settings.BASE_DIR / "protected_media"
        super().__init__(location=location, base_url=None, *args, **kwargs)


protected_audio_storage = ProtectedAudioStorage()
