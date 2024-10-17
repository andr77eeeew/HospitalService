from urllib.parse import urljoin

from HospitalSystem import settings


def build_media_absolute_uri(media_url):
    base_url = f"http://{settings.ALLOWED_HOSTS[0]}:8000" if settings.ALLOWED_HOSTS else "http://localhost:8000"
    return urljoin(base_url, media_url)
