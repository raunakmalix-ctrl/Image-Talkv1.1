#!/usr/bin/env bash
# Build the isolated venv for LTX-2.3 (image+prompt -> motion video w/ audio).
# Separate from venv_ltx (LTX-0.9.7-distilled): LTX-2.3's pipeline needs
# transformers with Gemma3ForConditionalGeneration (>=~4.50), but venv_ltx
# pins transformers<4.50 to dodge a different, LTX-0.9.7-specific tokenizer
# regression. Optional/heavy: run only if you want the LTX 2.3 motion-video
# engine option in Text -> Video.
set -e

ROOT="${IMAGE_TALK_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
VENVS="${IMAGE_TALK_VENVS:-$ROOT/venvs}"
mkdir -p "$VENVS"

# Matches venv_ltx/venv_wan/venv_qwen's CUDA 12.6 torch wheels.
CU="https://download.pytorch.org/whl/cu126"
PY312="$(command -v python3.12 || command -v python3)"
echo "==> building venv_ltx2 with $PY312"

pip install -q virtualenv
if [ ! -x "$VENVS/venv_ltx2/bin/python" ]; then
  python -m virtualenv -p "$PY312" "$VENVS/venv_ltx2"
  "$VENVS/venv_ltx2/bin/pip" install -q --upgrade pip wheel
fi

# Install diffusers/transformers FIRST, torch trio LAST -- same ABI-mismatch
# fix used for venv_ltx/venv_wan/venv_qwen ("undefined symbol:
# torch_library_impl" when an unpinned dependency pulls a mismatched
# torchaudio).
echo "==> diffusers (git) + transformers (git) + deps"
"$VENVS/venv_ltx2/bin/pip" install -q -r "$ROOT/requirements/ltx2.txt"

echo "==> torch 2.7 (cu126) — installed last to pin a matched trio"
"$VENVS/venv_ltx2/bin/pip" install -q \
  torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url "$CU"

echo "==> venv_ltx2 ready."
