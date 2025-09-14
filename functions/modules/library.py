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

    g = norm_gloss(gloss)
    key = f"{LIB_PREFIX}/{g}.mp4"
    try:
        if not blob_exists(key):
            return https_fn.Response(f"gloss not found: {g}", status=404)
    except Exception as e:
        print(f"Error checking blob existence for {key}: {e}")
        return https_fn.Response("Internal server error: failed to check blob existence", status=500)

    try:
        ensure_inline(key)
    except Exception as e:
        print(f"Error ensuring inline for {key}: {e}")
        return https_fn.Response("Internal server error: failed to set inline metadata", status=500)

    try:
        url = sign_v4_inline(key)
    except Exception as e:
        print(f"Error signing URL for {key}: {e}")
        return https_fn.Response("Internal server error: failed to sign URL", status=500)
    return https_fn.Response(json.dumps({"status": "ok", "key": key, "signed_url": url}),
                             headers={"Content-Type": "application/json"})
