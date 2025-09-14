import json, logging
from firebase_functions import https_fn
from firebase_admin import storage
from .utils.storage import blob_exists, ensure_inline, sign_v4_inline
from .utils.text import candidates_for_filename

LIB_PREFIX = "slp_library"

def handle_library_link(req: https_fn.Request) -> https_fn.Response:
    gloss = req.args.get("gloss") if req.method == "GET" else None
    if req.method != "GET":
        try:
            payload = json.loads(req.get_data().decode("utf-8"))
            gloss = gloss or payload.get("gloss")
        except Exception:
            return https_fn.Response("Invalid JSON", status=400)
    if not gloss:
        return https_fn.Response("Missing 'gloss'", status=400)

    bucket = storage.bucket()
    cand_names = candidates_for_filename(gloss)  # 不带 .mp4 的候选文件名（小写为主）
    logging.info(f"[library_link] bucket={bucket.name} gloss='{gloss}' candidates={cand_names[:5]}...")

    chosen_key = None
    for base in cand_names:
        key = f"{LIB_PREFIX}/{base}.mp4"
        if blob_exists(key):
            chosen_key = key
            break

    if not chosen_key:
        msg = f"gloss not found. tried={ [f'{LIB_PREFIX}/{c}.mp4' for c in cand_names] }"
        return https_fn.Response(msg, status=404)

    ensure_inline(chosen_key)
    url = sign_v4_inline(chosen_key)
    return https_fn.Response(json.dumps({"status":"ok","key":chosen_key,"signed_url":url}),
                             headers={"Content-Type":"application/json"})
