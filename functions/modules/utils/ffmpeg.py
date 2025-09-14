import os, stat, pathlib, subprocess
from pathlib import Path

FFMPEG_BIN = Path(__file__).resolve().parents[2] / "bin" / "ffmpeg"
DEFAULT_FPS = 30
OUT_W, OUT_H = 1280, 720
    
def ensure_exec():
    try:
        mode = os.stat(FFMPEG_BIN).st_mode
        os.chmod(FFMPEG_BIN, mode | stat.S_IEXEC)
    except Exception:
        pass

def run_ffmpeg(args: list[str]) -> int:
    ensure_exec()
    return subprocess.run([str(FFMPEG_BIN), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode


def concat_videos(inputs: list[Path], out_path: Path, safe_copy: bool = False):
    ensure_exec()
    list_file = out_path.parent / f"{out_path.stem}_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in inputs:
            f.write(f"file '{p.as_posix()}'\n")

    if safe_copy:
        if run_ffmpeg(["-y","-f","concat","-safe","0","-i",str(list_file),"-c","copy",str(out_path)]) == 0:
            list_file.unlink(missing_ok=True); return

    rc = run_ffmpeg([
        "-y","-f","concat","-safe","0","-i",str(list_file),
        "-r",str(DEFAULT_FPS),
        "-vf",f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=decrease,pad={OUT_W}:{OUT_H}:(ow-iw)/2:(oh-ih)/2",
        "-c:v","libx264","-preset","veryfast","-crf","20",
        "-c:a","aac","-b:a","128k",
        str(out_path)
    ])
    list_file.unlink(missing_ok=True)
    if rc != 0:
        raise RuntimeError("FFmpeg concat failed")