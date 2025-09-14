from datetime import timedelta
from pathlib import Path
from firebase_admin import storage
from typing import Optional

_bucket = storage.bucket()

def blob_exists(key: str) -> bool:
    return _bucket.blob(key).exists()

def download_to_tmp(key: str, local: Path) -> Path:
    _bucket.blob(key).download_to_filename(str(local))
    return local

def upload_inline(local: Path, key: str):
    blob = _bucket.blob(key)
    blob.content_type = "video/mp4"
    blob.content_disposition = "inline"
    blob.upload_from_filename(str(local))

def ensure_inline(key: str):
    blob = _bucket.blob(key)
    if not blob.exists():
        return
    blob.content_type = "video/mp4"
    blob.content_disposition = "inline"
    blob.patch()

def sign_v4_inline(key: str, hours: int = 24) -> str:
    blob = _bucket.blob(key)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=hours),
        method="GET",
        response_disposition="inline",
        response_type="video/mp4",
    )
