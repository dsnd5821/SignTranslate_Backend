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
    # 取默认凭证 + 刷新出 access token
    request = requests.Request()
    credentials, _ = google.auth.default()
    credentials.refresh(request)

    # 运行时 SA 的邮箱（比如 3977...-compute@developer.gserviceaccount.com）
    sa_email = getattr(credentials, "service_account_email", None)

    # 用 IAM Signer 通过 signBlob 代签
    signer = iam.Signer(request, credentials, sa_email)

    # 生成 V4 签名 URL，注意这两个关键参数
    b = storage.bucket().blob(key)
    return b.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=hours),
        method="GET",
        response_disposition="inline",
        response_type="video/mp4",
        service_account_email=sa_email,   # 关键
        access_token=credentials.token,   # 关键
        credentials=signer,               # 关键
    )