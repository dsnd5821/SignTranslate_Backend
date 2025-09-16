import json
import firebase_admin.firestore
from firebase_functions import https_fn
from .utils.storage import ensure_inline, sign_v4_inline
from .utils.text import norm_gloss_lower

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

    g = norm_gloss_lower(gloss)

    try:
        db = firebase_admin.firestore.client()
        collection = db.collection("library_table")
        doc = None
        for field in ("normalized_gloss", "gloss_en"):
            query = collection.where(field, "==", g).limit(1)
            docs_iter = query.stream()
            doc = next(docs_iter, None)
            if doc:
                break
    except Exception as e:
        print(f"Error querying Firestore for gloss {g}: {e}")
        return https_fn.Response("Internal server error: failed to query library table", status=500)

    if not doc:
        return https_fn.Response(f"gloss not found: {g}", status=404)

    data = doc.to_dict() if doc else None
    key = (data or {}).get("storage_location")
    if not key:
        return https_fn.Response(f"storage location missing for gloss: {g}", status=404)

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
