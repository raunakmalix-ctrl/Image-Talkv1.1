"""
Download model weights. Best-effort and idempotent: each model is independent,
so one failure won't abort the rest. Re-run safely.

Notes:
  - FLUX.1-dev is GATED. Accept the license at
    https://huggingface.co/black-forest-labs/FLUX.1-dev and set HF_TOKEN
    (or run `huggingface-cli login`) before launching. FLUX.1-schnell is open.
  - InsightFace 'buffalo_l' detector downloads itself on first face-swap run.
"""
import os
import sys
import urllib.request

# Allow running as `python setup/download_models.py` from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import (
    MODEL_ROOT, XTTS_DIR, INSIGHTFACE_ROOT, INSWAPPER_PATH, GFPGAN_PATH,
    WAV2LIP_CKPT, LATENTSYNC_DIR, LATENTSYNC_WEIGHTS_DIR,
)

# Empty string -> None, otherwise hf_hub builds an illegal "Bearer " header.
HF_TOKEN = os.environ.get("HF_TOKEN") or None


def _hf_snapshot(repo_id, local_dir, **kw):
    from huggingface_hub import snapshot_download
    os.makedirs(local_dir, exist_ok=True)
    snapshot_download(repo_id=repo_id, local_dir=local_dir,
                      token=HF_TOKEN, **kw)


def _hf_file(repo_id, filename, local_path):
    from huggingface_hub import hf_hub_download
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if os.path.exists(local_path):
        print(f"  exists: {local_path}"); return
    p = hf_hub_download(repo_id=repo_id, filename=filename, token=HF_TOKEN)
    import shutil; shutil.copy(p, local_path)
    print(f"  -> {local_path}")


def _wget(url, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if os.path.exists(local_path):
        print(f"  exists: {local_path}"); return
    print(f"  downloading {url}")
    urllib.request.urlretrieve(url, local_path)
    print(f"  -> {local_path}")


def step(name, fn):
    print(f"==> {name}")
    try:
        fn()
    except Exception as e:
        print(f"  !! {name} failed: {e}")


def xtts():
    if os.path.exists(os.path.join(XTTS_DIR, "model.pth")):
        print("  exists"); return
    _hf_snapshot("coqui/XTTS-v2", XTTS_DIR)


def inswapper():
    _hf_file("ezioruan/inswapper_128.onnx", "inswapper_128.onnx", INSWAPPER_PATH)


def gfpgan():
    _wget("https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/"
          "GFPGANv1.4.pth", GFPGAN_PATH)


def wav2lip():
    # Fallback lip-sync only (LatentSync is primary). GitHub release mirror.
    _wget("https://github.com/justinjohn0306/Wav2Lip/releases/download/"
          "models/wav2lip_gan.pth", WAV2LIP_CKPT)


def _link_tree(src_dir, dst_dir):
    """Symlink every file under src_dir into the matching path under
    dst_dir, skipping anything already there. Keeps the real blobs on
    persistent storage (MODEL_ROOT, Drive-backed when USE_DRIVE=True) and
    only places lightweight symlinks where the consuming code expects them
    -- same real-storage-plus-symlink idea used throughout this project."""
    import shutil
    for root, _, files in os.walk(src_dir):
        for fn in files:
            src = os.path.join(root, fn)
            dst = os.path.join(dst_dir, os.path.relpath(src, src_dir))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.lexists(dst):
                continue
            try:
                os.symlink(os.path.realpath(src), dst)
            except OSError:
                shutil.copy2(src, dst)


def latentsync():
    # LatentSync 1.5 weights: download the real blobs to MODEL_ROOT (Drive-
    # persisted when USE_DRIVE=True), then symlink them into
    # third_party/LatentSync/checkpoints/, the path LatentSync's own
    # inference script expects (LATENTSYNC_CKPT).
    ckpt_dir = os.path.join(LATENTSYNC_DIR, "checkpoints")
    if os.path.exists(os.path.join(ckpt_dir, "latentsync_unet.pt")):
        print("  exists"); return
    _hf_snapshot("ByteDance/LatentSync-1.5", LATENTSYNC_WEIGHTS_DIR)
    _link_tree(LATENTSYNC_WEIGHTS_DIR, ckpt_dir)


def main():
    step("XTTS-v2 (voice clone)", xtts)
    step("inswapper_128 (face swap)", inswapper)
    step("GFPGAN v1.4 (enhance)", gfpgan)
    step("Wav2Lip GAN (lip-sync fallback)", wav2lip)
    step("LatentSync 1.5 (lip re-sync)", latentsync)
    print("\nAll downloads attempted. MODEL_ROOT =", MODEL_ROOT)
    if not HF_TOKEN:
        print("NOTE: HF_TOKEN not set — FLUX.1-dev (gated) will fail to load. "
              "Either set HF_TOKEN after accepting its license, or use "
              "FLUX.1-schnell (open) in the Text -> Image tab.")


if __name__ == "__main__":
    main()
