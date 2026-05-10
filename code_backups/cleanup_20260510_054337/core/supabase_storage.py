import mimetypes
from datetime import datetime
from urllib.parse import quote

import requests
from django.conf import settings


class SupabaseStorageError(Exception):
    pass


def _clean_part(value):
    value = str(value or "").strip().replace("\\", "/")
    value = value.replace("..", "")
    value = value.strip("/")
    return value or "file"


def build_audio_key(question, filename):
    original_name = _clean_part(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    part = getattr(question, "part", "unknown")
    number = getattr(question, "question_number", "unknown")
    return f"listening/part-{part}/question-{number}/{timestamp}_{original_name}"


def get_supabase_config():
    url = getattr(settings, "SUPABASE_URL", "").rstrip("/")
    key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    bucket = getattr(settings, "SUPABASE_BUCKET_NAME", "aptis-audio")

    if not url:
        raise SupabaseStorageError("Thi?u SUPABASE_URL.")

    if not key:
        raise SupabaseStorageError("Thi?u SUPABASE_SERVICE_ROLE_KEY.")

    if not bucket:
        raise SupabaseStorageError("Thi?u SUPABASE_BUCKET_NAME.")

    return url, key, bucket


def upload_file_to_supabase(file_obj, key):
    url, service_key, bucket = get_supabase_config()

    content_type = (
        getattr(file_obj, "content_type", "")
        or mimetypes.guess_type(getattr(file_obj, "name", ""))[0]
        or "application/octet-stream"
    )

    safe_key = quote(key, safe="/")
    endpoint = f"{url}/storage/v1/object/{bucket}/{safe_key}"

    file_obj.seek(0)
    data = file_obj.read()

    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": content_type,
        "x-upsert": "true",
        "Cache-Control": "no-store",
    }

    response = requests.post(endpoint, headers=headers, data=data, timeout=90)

    if response.status_code not in (200, 201):
        raise SupabaseStorageError(
            f"Upload Supabase th?t b?i: {response.status_code} - {response.text[:300]}"
        )

    return {
        "key": key,
        "size": len(data),
        "content_type": content_type,
    }


def create_signed_url(key, expires_in=None):
    url, service_key, bucket = get_supabase_config()

    if expires_in is None:
        expires_in = getattr(settings, "SUPABASE_SIGNED_URL_EXPIRES", 300)

    safe_key = quote(key, safe="/")
    endpoint = f"{url}/storage/v1/object/sign/{bucket}/{safe_key}"

    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": "application/json",
    }

    response = requests.post(
        endpoint,
        headers=headers,
        json={"expiresIn": int(expires_in)},
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise SupabaseStorageError(
            f"T?o signed URL th?t b?i: {response.status_code} - {response.text[:300]}"
        )

    payload = response.json()
    signed_path = payload.get("signedURL") or payload.get("signedUrl")

    if not signed_path:
        raise SupabaseStorageError("Supabase kh?ng tr? v? signed URL.")

    if signed_path.startswith("http"):
        return signed_path

    return f"{url}/storage/v1{signed_path}"


def delete_file_from_supabase(key):
    url, service_key, bucket = get_supabase_config()

    endpoint = f"{url}/storage/v1/object/{bucket}"

    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": "application/json",
    }

    response = requests.delete(
        endpoint,
        headers=headers,
        json={"prefixes": [key]},
        timeout=30,
    )

    if response.status_code not in (200, 204):
        raise SupabaseStorageError(
            f"X?a file Supabase th?t b?i: {response.status_code} - {response.text[:300]}"
        )
