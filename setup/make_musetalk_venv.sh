#!/usr/bin/env bash
# Build the isolated venv for MuseTalk v1.5 (optional enhanced lip-sync).
# Separate/opt-in (like make_ltx_venv.sh) because of the heavy, version-pinned
# mmlab stack. Python 3.10 + torch 2.0.1 (cu118) match MuseTalk + mmcv wheels.
set -e

ROOT="${IMAGE_TALK_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
VENVS="${IMAGE_TALK_VENVS:-$ROOT/venvs}"
TP="$ROOT/third_party"
V="$VENVS/venv_musetalk"
CU="https://download.pytorch.org/whl/cu118"
PY310="$(command -v python3.10 || command -v python3)"
mkdir -p "$VENVS"

echo "==> venv_musetalk with $PY310"
pip install -q virtualenv
if [ ! -x "$V/bin/python" ]; then
  python -m virtualenv -p "$PY310" "$V"
  "$V/bin/pip" install -q --upgrade pip wheel
fi

echo "==> torch 2.0.1 (cu118)"
"$V/bin/pip" install -q \
  torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url "$CU"

echo "==> MuseTalk requirements + extras"
[ -f "$TP/MuseTalk/requirements.txt" ] && \
  "$V/bin/pip" install -q -r "$TP/MuseTalk/requirements.txt" || true
"$V/bin/pip" install -q -r "$ROOT/requirements/musetalk.txt"

echo "==> mmlab (openmim)"
"$V/bin/pip" install -q -U openmim
"$V/bin/mim" install -q mmengine
"$V/bin/mim" install -q "mmcv==2.0.1"
"$V/bin/mim" install -q "mmdet==3.1.0"
"$V/bin/mim" install -q "mmpose==1.1.0"

echo "==> downloading MuseTalk weights"
if [ -f "$TP/MuseTalk/download_weights.sh" ]; then
  ( cd "$TP/MuseTalk" && PATH="$V/bin:$PATH" bash download_weights.sh ) || \
    echo "  !! weight download failed — re-run this cell or download manually"
fi

echo "==> venv_musetalk ready."
