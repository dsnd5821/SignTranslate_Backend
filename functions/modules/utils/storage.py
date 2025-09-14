from datetime import timedelta
from pathlib import Path

import google.auth
from firebase_admin import storage
from google.auth import iam
from google.auth.transport import requests

def _bucket():
    return storage.bucket()

def blob_exists(key: str) -> bool:
    return _bucket().blob(key).exists()

def download_to_tmp(key: str, local: Path) -> Path:
    _bucket().blob(key).download_to_filename(str(local))
    return local

def upload_inline(local: Path, key: str):
    b = _bucket().blob(key)
    b.content_type = "video/mp4"
    b.content_disposition = "inline"
    b.upload_from_filename(str(local))

def ensure_inline(key: str):
    b = _bucket().blob(key)
    if not b.exists():
        return
    b.content_type = "video/mp4"
    b.content_disposition = "inline"
    b.patch()

def sign_v4_inline(key: str, hours: int = 24) -> str:
    """Generate a V4 signed URL for inline access.

    The service account used must have
    ``roles/iam.serviceAccountTokenCreator`` and ``roles/storage.objectViewer``
    IAM roles.
    """

    credentials, _ = google.auth.default()
    service_account_email = getattr(credentials, "service_account_email", None)
    signer = credentials

    if not hasattr(credentials, "sign_bytes"):
        signer = iam.Signer(requests.Request(), credentials, service_account_email)

    b = _bucket().blob(key)
    return b.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=hours),
        method="GET",
        response_disposition="inline",
        response_type="video/mp4",
        service_account_email=service_account_email,
        credentials=signer,
    )
