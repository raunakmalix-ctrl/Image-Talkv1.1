"""
LTX-2.3 (Lightricks) image+prompt -> motion video with synchronized audio,
run in venv_ltx (shared with LTXEngine -- both use the same diffusers-from-git
install) via a worker subprocess.

Alternative to Wan2.2-I2V for the Text -> Video tab's reference-photo path:
faster/lighter and additionally generates synchronized audio (Wan2.2-I2V is
video-only), trading some multi-subject identity fidelity per early
comparisons.
"""
import os

from core.base_engine import BaseEngine
from core.utils import timestamp_file
from core.config import VENV_LTX_PY, LTX2_REPO, PROJECT_ROOT
from core.subprocess_runner import run_worker

WORKER = os.path.join(PROJECT_ROOT, "workers", "ltx2_worker.py")


class LTX2Engine(BaseEngine):

    def run(self, image_path, prompt, negative_prompt="",
            width=768, height=512, num_frames=121, fps=24, seed=-1):
        if not image_path:
            raise ValueError("A reference image is required.")
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        if not os.path.exists(VENV_LTX_PY):
            raise RuntimeError(
                "venv_ltx missing — run setup/make_ltx_venv.sh first "
                "(LTX 2.3 shares LTX-Video's venv)."
            )

        out_path = timestamp_file("ltx2", "mp4")
        return run_worker(
            VENV_LTX_PY, WORKER,
            {
                "repo": LTX2_REPO,
                "image": image_path,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width, "height": height,
                "num_frames": num_frames, "fps": fps, "seed": seed,
                "out_path": out_path,
            },
            cwd=PROJECT_ROOT,
            timeout=3600,
        )
