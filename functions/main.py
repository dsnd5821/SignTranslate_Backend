# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
initialize_app()

from modules.library import handle_library_link
from modules.slp import handle_slp_compose
from modules.utils.ffmpeg import ensure_exec, run_ffmpeg

@https_fn.on_request(region="asia-southeast1")
def ffmpeg_info(req: https_fn.Request) -> https_fn.Response:
    ensure_exec()
    import subprocess
    p = subprocess.run([str(run_ffmpeg.__globals__['FFMPEG_BIN']), "-version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return https_fn.Response(p.stdout.decode("utf-8")[:1024], headers={"Content-Type":"text/plain"})

@https_fn.on_request(region="asia-southeast1", timeout_sec=540, memory="1GiB")
def library_link(req: https_fn.Request) -> https_fn.Response:
    return handle_library_link(req)

@https_fn.on_request(region="asia-southeast1", timeout_sec=540, memory="1GiB")
def slp_compose(req: https_fn.Request) -> https_fn.Response:
    return handle_slp_compose(req)