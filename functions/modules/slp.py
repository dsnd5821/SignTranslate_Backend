import json
import uuid
from pathlib import Path

from firebase_functions import https_fn

from .utils.text import tokenize_user_input
from .utils.storage import (
    blob_exists, download_to_tmp, upload_inline, ensure_inline, sign_v4_inline
)
from .utils.ffmpeg import concat_videos

TMP_DIR = Path("/tmp"); TMP_DIR.mkdir(exist_ok=True, parents=True)
LIB_PREFIX = "slp_library"
ABC_PREFIX = "alphabet"
OUT_PREFIX = "composed"

def _keys_for_gloss(g: str) -> list[str]:
    """库命中用库，否则按字母降级为 alphabet 片段"""
    k = f"{LIB_PREFIX}/{g}.mp4"
    if blob_exists(k):
        return [k]
    parts = []
    for ch in g:
        if ch.isalnum():
            ak = f"{ABC_PREFIX}/{ch.upper()}.mp4"
            if not blob_exists(ak):
                raise FileNotFoundError(f"alphabet missing: {ch}")
            parts.append(ak)
    return parts

def handle_slp_compose(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return https_fn.Response("Method Not Allowed", status=405)

    try:
        payload = json.loads(req.get_data().decode("utf-8"))
    except Exception:
        return https_fn.Response("Invalid JSON", status=400)

    text = payload.get("text")
    cache = bool(payload.get("cache", True))
    safe_copy = bool(payload.get("safe_copy", False))
    if not text or not isinstance(text, str):
        return https_fn.Response("Missing 'text'", status=400)

    glosses = tokenize_user_input(text)
    if not glosses:
        return https_fn.Response("No valid tokens", status=400)

    # 展开为片段键列表
    video_keys: list[str] = []
    for g in glosses:
        video_keys.extend(_keys_for_gloss(g))

    # 单片段直接返回
    if len(video_keys) == 1 and cache:
        k = video_keys[0]
        ensure_inline(k)
        url = sign_v4_inline(k)
        return https_fn.Response(json.dumps({"status":"ok","key":k,"signed_url":url,"source":"single"}),
                                 headers={"Content-Type":"application/json"})

    combo = "_".join([Path(k).stem for k in video_keys])
    dest_key = f"{OUT_PREFIX}/{combo}.mp4"

    from .utils.storage import blob_exists as exists
    if cache and exists(dest_key):
        ensure_inline(dest_key)
        url = sign_v4_inline(dest_key)
        return https_fn.Response(json.dumps({"status":"ok","key":dest_key,"signed_url":url,"source":"cache"}),
                                 headers={"Content-Type":"application/json"})

    # 下载并拼接
    locals_list = [download_to_tmp(k, TMP_DIR / f"{uuid.uuid4()}_{Path(k).name}") for k in video_keys]
    out_path = TMP_DIR / f"{uuid.uuid4()}_{Path(dest_key).name}"
    try:
        concat_videos(locals_list, out_path, safe_copy=safe_copy)
        upload_inline(out_path, dest_key)
        ensure_inline(dest_key)
        url = sign_v4_inline(dest_key)
    except Exception as e:
        return https_fn.Response(f"compose failed: {e}", status=400)
    finally:
        for p in locals_list:
            try: p.unlink(missing_ok=True)
            except: pass
        try: out_path.unlink(missing_ok=True)
        except: pass

    return https_fn.Response(json.dumps({"status":"ok","key":dest_key,"signed_url":url,"source":"composed"}),
                             headers={"Content-Type":"application/json"})
