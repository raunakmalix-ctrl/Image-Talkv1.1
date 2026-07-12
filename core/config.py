"""
Central path configuration for VAJRA v1.1 (Colab).

Everything derives from PROJECT_ROOT. In Colab the repo is cloned to
/content/VAJRA-v1.1 and this resolves automatically. Override with the
IMAGE_TALK_ROOT env var if you clone elsewhere.

Model weights live under MODEL_ROOT. To persist them across Colab sessions,
set MODEL_ROOT to a Google Drive path (e.g. /content/drive/MyDrive/image_talk_models)
via the IMAGE_TALK_MODELS env var before launching.
"""
import os
import shutil

# ── Roots ───────────────────────────────────────────────────────────────────
_HERE        = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.environ.get("IMAGE_TALK_ROOT", os.path.dirname(_HERE))
MODEL_ROOT   = os.environ.get("IMAGE_TALK_MODELS", os.path.join(PROJECT_ROOT, "models"))
OUTPUTS_DIR  = os.path.join(PROJECT_ROOT, "outputs")
UPLOADS_DIR  = os.path.join(PROJECT_ROOT, "uploads")
THIRD_PARTY  = os.path.join(PROJECT_ROOT, "third_party")   # cloned model repos
VENV_ROOT    = os.environ.get("IMAGE_TALK_VENVS", os.path.join(PROJECT_ROOT, "venvs"))
HF_CACHE_DIR = os.path.join(MODEL_ROOT, "hf_cache")

for _d in (MODEL_ROOT, OUTPUTS_DIR, UPLOADS_DIR, THIRD_PARTY, VENV_ROOT, HF_CACHE_DIR):
    os.makedirs(_d, exist_ok=True)

# Every from_pretrained()/snapshot_download() call in this project (SDXL/FLUX
# here in the main process, LTX/Kontext/Wan2.2 in their subprocess workers)
# otherwise falls back to Hugging Face's default cache
# (~/.cache/huggingface/hub) -- local to the Colab VM disk, wiped every
# session, and NOT covered by the MODEL_ROOT Drive redirect above despite
# USE_DRIVE claiming to cache "model weights". Route it through MODEL_ROOT
# too, so USE_DRIVE actually covers everything. Derived fresh from MODEL_ROOT
# on every import (rather than a notebook cell setting it once) so it's
# correct in every process: the main app imports core.config directly;
# subprocess workers inherit it via core/subprocess_runner.py's clean_env(),
# which copies the parent's environment; the download scripts import
# core.config directly too.
os.environ.setdefault("HF_HUB_CACHE", HF_CACHE_DIR)

# ── Cloned model repositories (third_party/) ────────────────────────────────
WAV2LIP_DIR    = os.path.join(THIRD_PARTY, "Wav2Lip")
LATENTSYNC_DIR = os.path.join(THIRD_PARTY, "LatentSync")
CODEFORMER_DIR = os.path.join(THIRD_PARTY, "CodeFormer")

# ── Model weight paths ──────────────────────────────────────────────────────
# Text → image
FLUX_DEV_REPO     = "black-forest-labs/FLUX.1-dev"
FLUX_SCHNELL_REPO = "black-forest-labs/FLUX.1-schnell"
# Instruction-based image editing (gated, needs HF_TOKEN + license)
FLUX_KONTEXT_REPO = "black-forest-labs/FLUX.1-Kontext-dev"

# Face swap
INSIGHTFACE_ROOT = os.path.join(MODEL_ROOT, "insightface")
INSWAPPER_PATH   = os.path.join(INSIGHTFACE_ROOT, "models", "inswapper_128.onnx")
GFPGAN_PATH      = os.path.join(MODEL_ROOT, "gfpgan", "GFPGANv1.4.pth")
CODEFORMER_PATH  = os.path.join(MODEL_ROOT, "codeformer", "codeformer.pth")

# Voice clone
XTTS_DIR = os.path.join(MODEL_ROOT, "xtts")

# Lip sync — LatentSync's own inference script expects its checkpoint at a
# fixed path inside the cloned repo (LATENTSYNC_CKPT). The real weight files
# live under MODEL_ROOT (Drive-persisted); download_models.py symlinks them
# into place -- previously this path pointed straight into third_party/,
# which is never Drive-cached and was silently rebuilt every session.
LATENTSYNC_WEIGHTS_DIR = os.path.join(MODEL_ROOT, "latentsync")
WAV2LIP_CKPT      = os.path.join(MODEL_ROOT, "wav2lip", "wav2lip_gan.pth")
LATENTSYNC_CKPT   = os.path.join(LATENTSYNC_DIR, "checkpoints", "latentsync_unet.pt")
LATENTSYNC_CONFIG = os.path.join(LATENTSYNC_DIR, "configs", "unet", "stage2.yaml")

# Transcript
WHISPERX_MODEL = os.environ.get("WHISPERX_MODEL", "large-v3")

# ── Isolated venv interpreters (built by setup/make_venvs.sh) ───────────────
def _venv_python(name):
    return os.path.join(VENV_ROOT, name, "bin", "python")

VENV_VOICE_PY      = _venv_python("venv_voice")
VENV_LATENTSYNC_PY = _venv_python("venv_latentsync")
VENV_LTX_PY        = _venv_python("venv_ltx")
VENV_WAN_PY        = _venv_python("venv_wan")

# LTX-Video 0.9.7-distilled (Lightricks) text -> video. Open (no token), fast
# few-step. Runs in its own venv (built by setup/make_ltx_venv.sh).
LTX_REPO = "Lightricks/LTX-Video-0.9.7-distilled"

# Wan2.2-I2V (Alibaba/Tongyi Wanxiang) image+prompt -> motion video, identity
# preserving, handles multi-subject images (not per-face like classic
# talking-head methods -- the uploaded photo is the first frame, diffusion
# generates the rest following the prompt). Apache-2.0, open. Runs in its own
# venv (built by setup/make_wan_venv.sh) -- needs transformers 4.49-4.51.3, incompatible with
# venv_ltx's <4.50 pin (see requirements/ltx.txt), hence a separate venv.
WAN_I2V_REPO = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"

# ── FFmpeg (Colab: apt-installed, on PATH) ──────────────────────────────────
FFMPEG_PATH  = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE_PATH = shutil.which("ffprobe") or "ffprobe"
