"""
Download MuseTalk v1.5 weights via Hugging Face Hub instead of the repo's own
download_weights.sh, which hosts some files on Google Drive — those often fail
silently in Colab (Drive serves an HTML "can't scan for viruses" page instead
of the file for large downloads, and wget/curl save that page as if it were
the weight file). HF Hub is a reliable, direct source for the same weights.

Files are SYMLINKED (not copied) from HF's local cache into
third_party/MuseTalk/models/ — snapshot_download() already stores the actual
blobs under ~/.cache/huggingface/hub and returns a symlink tree pointing at
them, so copying would silently duplicate several GB on disk.
"""
import os
import sys
import glob
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import MUSETALK_DIR, MUSETALK_UNET, MUSETALK_UNET_CONFIG  # noqa: E402

MODELS_DIR = os.path.join(MUSETALK_DIR, "models")


def _link_or_copy(src, dst):
    """Symlink dst -> the real blob behind src (avoids duplicating disk
    space); fall back to a plain copy only if the filesystem can't symlink."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        return
    try:
        os.symlink(os.path.realpath(src), dst)
    except OSError:
        shutil.copy2(src, dst)


def main():
    if os.path.exists(MUSETALK_UNET) and os.path.exists(MUSETALK_UNET_CONFIG):
        print(f"  exists: {MUSETALK_UNET}")
        return

    from huggingface_hub import snapshot_download

    print("Downloading TMElyralab/MuseTalk weights from Hugging Face Hub ...")
    os.makedirs(MODELS_DIR, exist_ok=True)
    snap = snapshot_download(repo_id="TMElyralab/MuseTalk")

    # Link the whole snapshot into models/, preserving its internal layout.
    for src in glob.glob(os.path.join(snap, "**", "*"), recursive=True):
        if os.path.isdir(src):
            continue
        rel = os.path.relpath(src, snap)
        dst = os.path.join(MODELS_DIR, rel)
        _link_or_copy(src, dst)

    # Defensive: if the HF repo's internal layout doesn't match the expected
    # models/musetalkV15/{unet.pth,musetalk.json} path, search and relocate.
    for target in (MUSETALK_UNET, MUSETALK_UNET_CONFIG):
        if os.path.exists(target):
            continue
        name = os.path.basename(target)
        hits = glob.glob(os.path.join(MODELS_DIR, "**", name), recursive=True)
        if hits:
            _link_or_copy(hits[0], target)
            print(f"  relocated {hits[0]} -> {target}")

    if os.path.exists(MUSETALK_UNET):
        print(f"MuseTalk weights ready: {MUSETALK_UNET}")
    else:
        print(f"!! {MUSETALK_UNET} still missing after download — "
              f"check the HF repo layout or download manually.")


if __name__ == "__main__":
    main()
