import json
from pathlib import Path
from firebase_functions import https_fn

from .utils.storage import blob_exists, ensure_inline, sign_v4_inline
from .utils.text import norm_gloss

LIB_PREFIX = "slp_library"

def handle_library_link(req: https_fn.Request) -> https_fn.Response:
    # support GET ?gloss= or POST {"gloss": "..."}
    gloss = req.args.get("gloss") if req.method == "GET" else None
    if req.method != "GET":
        try:
            payload = json.loads(req.get_data().decode("utf-8"))
            gloss = gloss or payload.get("gloss")
        except Exception:
            return https_fn.Response("Invalid JSON", status=400)

    if not gloss:
        return https_fn.Response("Missing 'gloss'", status=400)

    g = norm_gloss(gloss)
    key = f"{LIB_PREFIX}/{g}.mp4"
    if not blob_exists(key):
        return https_fn.Response(f"gloss not found: {g}", status=404)

    ensure_inline(key)
    url = sign_v4_inline(key)
    return https_fn.Response(json.dumps({"status": "ok", "key": key, "signed_url": url}),
                             headers={"Content-Type": "application/json"})
