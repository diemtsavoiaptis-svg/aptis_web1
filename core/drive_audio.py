import re
from urllib.parse import urlparse, parse_qs


def extract_drive_file_id(value):
    value = str(value or "").strip()

    if not value:
        return ""

    patterns = [
        r"/file/d/([^/]+)",
        r"id=([^&]+)",
        r"/d/([^/]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1).strip()

    parsed = urlparse(value)
    query = parse_qs(parsed.query)

    if "id" in query and query["id"]:
        return query["id"][0].strip()

    return ""


def build_drive_audio_url(file_id):
    file_id = str(file_id or "").strip()

    if not file_id:
        return ""

    return f"https://drive.google.com/uc?export=download&id={file_id}"
