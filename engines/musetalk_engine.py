"""
MuseTalk v1.5 — fast audio-driven lip-sync (sharp mouth, no head motion).

Serves both features:
  - Edit & Relip:  face_path = a video  → lips re-synced to the edited audio.
  - Talking Video: face_path = an image → static head with synced lips.

Runs in the isolated `venv_musetalk` via MuseTalk's own `scripts.inference`
(config-yaml driven), mirroring the SadTalker/LatentSync subprocess pattern.
"""
import os
import subprocess
import tempfile

from core.base_engine import BaseEngine
from core.utils import timestamp_file, to_wav, transcode_h264
from core.subprocess_runner import clean_env
from core.config import (
    VENV_MUSETALK_PY, MUSETALK_DIR, MUSETALK_UNET, MUSETALK_UNET_CONFIG,
    OUTPUTS_DIR, FFMPEG_PATH,
)

_VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v")


class MuseTalkEngine(BaseEngine):

    def run(self, face_path, audio_path, bbox_shift=0):
        if not os.path.exists(face_path):
            raise FileNotFoundError(f"Face input not found: {face_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio not found: {audio_path}")
        if not os.path.exists(VENV_MUSETALK_PY):
            raise RuntimeError("venv_musetalk missing — run setup/make_musetalk_venv.sh")
        if not os.path.exists(MUSETALK_UNET):
            raise RuntimeError("MuseTalk weights missing — see setup/make_musetalk_venv.sh")

        # MuseTalk reads with ffmpeg/opencv; normalize video inputs to H.264.
        ext = os.path.splitext(face_path)[1].lower()
        if ext in _VIDEO_EXTS:
            face_path = transcode_h264(face_path)

        wav_path, is_tmp = to_wav(audio_path)
        tmp_files = [wav_path] if is_tmp else []

        try:
            result_dir = os.path.join(OUTPUTS_DIR, "musetalk_tmp")
            os.makedirs(result_dir, exist_ok=True)

            # MuseTalk's inference YAML: one named task with the input pair.
            cfg = (
                "task_0:\n"
                f"  video_path: \"{face_path}\"\n"
                f"  audio_path: \"{wav_path}\"\n"
                f"  bbox_shift: {int(bbox_shift)}\n"
            )
            ytmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, encoding="utf-8"
            )
            ytmp.write(cfg)
            ytmp.close()
            tmp_files.append(ytmp.name)

            cmd = [
                VENV_MUSETALK_PY, "-m", "scripts.inference",
                "--inference_config", ytmp.name,
                "--result_dir", result_dir,
                "--unet_model_path", MUSETALK_UNET,
                "--unet_config", MUSETALK_UNET_CONFIG,
                "--version", "v15",
                "--ffmpeg_path", os.path.dirname(FFMPEG_PATH) or "/usr/bin",
            ]

            print(f"[MuseTalk] Running (bbox_shift={bbox_shift}) ...")
            proc = subprocess.run(
                cmd, cwd=MUSETALK_DIR, capture_output=True, text=True,
                env=clean_env({"PYTHONPATH": MUSETALK_DIR}),
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"MuseTalk failed (exit {proc.returncode}).\n"
                    f"{proc.stdout[-1000:]}\n{proc.stderr[-1500:]}"
                )

            mp4s = []
            for root, _, files in os.walk(result_dir):
                for f in files:
                    if f.endswith(".mp4"):
                        mp4s.append(os.path.join(root, f))
            if not mp4s:
                raise RuntimeError("MuseTalk ran but produced no .mp4.")

            latest   = max(mp4s, key=os.path.getmtime)
            out_path = timestamp_file("musetalk", "mp4")
            os.replace(latest, out_path)
            print(f"[MuseTalk] Output: {out_path}")
            return out_path

        finally:
            for f in tmp_files:
                try:
                    os.unlink(f)
                except Exception:
                    pass
