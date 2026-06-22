"""
Media Studio — lightweight ffmpeg/CPU editing utilities (no GPU cost).

Used to prep inputs before spending GPU on the AI tabs: trim clips, grab a
frame, clean reference audio, convert/compress, merge, burn captions, and
remove a portrait's background.
"""
import os
import subprocess
import tempfile

from core.base_engine import BaseEngine
from core.utils import timestamp_file
from core.config import FFMPEG_PATH, FFPROBE_PATH


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0 or not (cmd and os.path.exists(cmd[-1])):
        raise RuntimeError(f"ffmpeg failed:\n{p.stderr[-1200:]}")
    return cmd[-1]


def _probe_duration(path):
    p = subprocess.run(
        [FFPROBE_PATH, "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    try:
        return float(p.stdout.strip())
    except Exception:
        return None


class MediaEngine(BaseEngine):

    # ── Trim ────────────────────────────────────────────────────────────────
    def trim_video(self, path, start, end):
        if path is None:
            raise ValueError("Upload a video.")
        start, end = float(start or 0), float(end or 0)
        out = timestamp_file("trim", "mp4")
        cmd = [FFMPEG_PATH, "-y", "-ss", str(start), "-i", path]
        if end > start:
            cmd += ["-to", str(end - start)]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", out]
        return _run(cmd)

    def trim_audio(self, path, start, end, fmt="wav"):
        if path is None:
            raise ValueError("Upload an audio file.")
        start, end = float(start or 0), float(end or 0)
        out = timestamp_file("trim", fmt)
        cmd = [FFMPEG_PATH, "-y", "-ss", str(start), "-i", path]
        if end > start:
            cmd += ["-to", str(end - start)]
        cmd += [out]
        return _run(cmd)

    # ── Frame grab ──────────────────────────────────────────────────────────
    def grab_frame(self, video, t):
        if video is None:
            raise ValueError("Upload a video.")
        out = timestamp_file("frame", "png")
        return _run([FFMPEG_PATH, "-y", "-ss", str(float(t or 0)),
                     "-i", video, "-frames:v", "1", "-q:v", "2", out])

    # ── Audio cleanup for voice cloning ───────────────────────────────────────
    def clean_audio(self, path):
        """Extract/clean: denoise + EBU-R128 loudness normalize → mono 24k wav."""
        if path is None:
            raise ValueError("Upload audio or a video.")
        out = timestamp_file("clean", "wav")
        return _run([
            FFMPEG_PATH, "-y", "-i", path, "-vn",
            "-af", "afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ac", "1", "-ar", "24000", out,
        ])

    # ── Convert / compress / resize / gif ─────────────────────────────────────
    def convert(self, path, target):
        if path is None:
            raise ValueError("Upload a file.")
        if target == "MP4 (H.264)":
            out = timestamp_file("conv", "mp4")
            return _run([FFMPEG_PATH, "-y", "-i", path, "-c:v", "libx264",
                         "-pix_fmt", "yuv420p", "-c:a", "aac", out])
        if target == "Compress MP4":
            out = timestamp_file("compressed", "mp4")
            return _run([FFMPEG_PATH, "-y", "-i", path, "-c:v", "libx264",
                         "-crf", "28", "-preset", "veryfast",
                         "-c:a", "aac", "-b:a", "96k", out])
        if target == "MP3":
            out = timestamp_file("conv", "mp3")
            return _run([FFMPEG_PATH, "-y", "-i", path, "-vn",
                         "-c:a", "libmp3lame", "-q:a", "2", out])
        if target == "WAV":
            out = timestamp_file("conv", "wav")
            return _run([FFMPEG_PATH, "-y", "-i", path, "-vn", out])
        raise ValueError(f"Unknown target: {target}")

    def resize_video(self, path, width, height):
        if path is None:
            raise ValueError("Upload a video.")
        w, h = int(width), int(height)
        out = timestamp_file("resized", "mp4")
        return _run([FFMPEG_PATH, "-y", "-i", path,
                     "-vf", f"scale={w}:{h}", "-c:a", "copy", out])

    def to_gif(self, path, fps=12, width=480):
        if path is None:
            raise ValueError("Upload a video.")
        out = timestamp_file("clip", "gif")
        vf = f"fps={int(fps)},scale={int(width)}:-1:flags=lanczos"
        return _run([FFMPEG_PATH, "-y", "-i", path, "-vf", vf, out])

    # ── Merge / concatenate ───────────────────────────────────────────────────
    def concat(self, paths, kind="video"):
        files = [p for p in (paths or []) if p]
        if len(files) < 2:
            raise ValueError("Add at least two files to merge.")
        ext = "mp4" if kind == "video" else "wav"
        # Normalize each to a uniform format, then concat-demux with -c copy.
        norm = []
        try:
            for p in files:
                tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False).name
                if kind == "video":
                    _run([FFMPEG_PATH, "-y", "-i", p, "-vf", "scale=1280:720",
                          "-r", "25", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-ar", "44100", tmp])
                else:
                    _run([FFMPEG_PATH, "-y", "-i", p, "-ac", "2", "-ar", "44100", tmp])
                norm.append(tmp)
            lst = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
            for p in norm:
                lst.write(f"file '{p}'\n")
            lst.close()
            out = timestamp_file("merged", ext)
            _run([FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0",
                  "-i", lst.name, "-c", "copy", out])
            return out
        finally:
            for p in norm:
                try: os.unlink(p)
                except Exception: pass

    # ── Burn captions (reuses faster-whisper) ─────────────────────────────────
    def burn_captions(self, video):
        if video is None:
            raise ValueError("Upload a video.")
        from engines.transcript_engine import _load_whisper, _extract_audio
        audio = _extract_audio(video)
        model = _load_whisper("cpu")
        seg_iter, _ = model.transcribe(audio, vad_filter=True)

        def ts(t):
            h = int(t // 3600); m = int((t % 3600) // 60)
            s = int(t % 60); ms = int((t - int(t)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        srt = tempfile.NamedTemporaryFile(mode="w", suffix=".srt",
                                          delete=False, encoding="utf-8")
        for i, s in enumerate(seg_iter, 1):
            txt = (s.text or "").strip()
            if txt:
                srt.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{txt}\n\n")
        srt.close()

        out = timestamp_file("captioned", "mp4")
        style = "FontSize=18,Outline=1,Shadow=0,MarginV=24"
        srt_path = srt.name.replace("\\", "/").replace(":", "\\:")
        try:
            return _run([FFMPEG_PATH, "-y", "-i", video,
                         "-vf", f"subtitles='{srt_path}':force_style='{style}'",
                         "-c:a", "copy", out])
        finally:
            try: os.unlink(srt.name)
            except Exception: pass

    # ── Background removal (rembg) ─────────────────────────────────────────────
    def remove_bg(self, image, bg="white"):
        if image is None:
            raise ValueError("Upload an image.")
        from rembg import remove
        from PIL import Image
        cut = remove(Image.open(image).convert("RGBA"))
        colors = {"white": (255, 255, 255), "black": (0, 0, 0),
                  "green": (0, 177, 64), "gray": (128, 128, 128)}
        canvas = Image.new("RGBA", cut.size, colors.get(bg, (255, 255, 255)) + (255,))
        canvas.alpha_composite(cut)
        out = timestamp_file("nobg", "png")
        canvas.convert("RGB").save(out)
        return out
