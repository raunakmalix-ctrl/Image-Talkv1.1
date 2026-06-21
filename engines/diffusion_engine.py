"""
Text -> image.

  - "sdxl"    : Stable Diffusion XL base 1.0 — OPEN, no HF token needed. Default.
  - "schnell" : FLUX.1-schnell, 4 steps      — gated, needs HF_TOKEN + license.
  - "dev"     : FLUX.1-dev, ~28 steps        — gated, needs HF_TOKEN + license.

Runs in the main Colab env. Lazy-loaded and unloaded by the model_manager so
it shares the GPU with the face-swap engine.
"""
import torch

from core.base_engine import BaseEngine
from core.model_manager import load_model, unload_model
from core.utils import timestamp_file
from core.device import DEVICE
from core.config import FLUX_DEV_REPO, FLUX_SCHNELL_REPO

SDXL_REPO = "stabilityai/stable-diffusion-xl-base-1.0"


def _load_pipe(variant):
    from diffusers import FluxPipeline, StableDiffusionXLPipeline

    if variant == "sdxl":
        dtype = torch.float16 if DEVICE == "cuda" else torch.float32
        print(f"[Diffusion] Loading SDXL ({SDXL_REPO}) ...")
        kw = {"torch_dtype": dtype, "use_safetensors": True}
        if DEVICE == "cuda":
            kw["variant"] = "fp16"
        pipe = StableDiffusionXLPipeline.from_pretrained(SDXL_REPO, **kw)
    else:
        repo  = FLUX_DEV_REPO if variant == "dev" else FLUX_SCHNELL_REPO
        dtype = torch.bfloat16 if DEVICE == "cuda" else torch.float32
        print(f"[Diffusion] Loading FLUX.1-{variant} ({repo}) ...")
        pipe = FluxPipeline.from_pretrained(repo, torch_dtype=dtype)

    if DEVICE == "cuda":
        total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        if total_gb >= 38:
            pipe.to("cuda")
        else:
            pipe.enable_model_cpu_offload()
        try:
            pipe.enable_vae_tiling()
        except Exception:
            pass

    print(f"[Diffusion] {variant} ready on {DEVICE.upper()}.")
    return pipe


# Per-variant defaults: (steps, guidance)
_DEFAULTS = {"sdxl": (30, 6.0), "dev": (28, 3.5), "schnell": (4, 0.0)}


class DiffusionEngine(BaseEngine):

    def load(self, variant="sdxl"):
        self.pipe = load_model(f"img_{variant}", lambda: _load_pipe(variant))
        return self.pipe

    def unload(self):
        for variant in ("sdxl", "dev", "schnell"):
            unload_model(f"img_{variant}")

    def run(self, prompt, variant="sdxl",
            width=1024, height=1024,
            steps=None, guidance=None, seed=-1):

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        d_steps, d_guid = _DEFAULTS.get(variant, _DEFAULTS["sdxl"])
        if steps is None:
            steps = d_steps
        if guidance is None:
            guidance = d_guid

        pipe = self.load(variant)

        generator = None
        if seed is not None and int(seed) >= 0:
            generator = torch.Generator(device=DEVICE).manual_seed(int(seed))

        # Both FLUX and SDXL are happy with dimensions divisible by 16.
        width  = (int(width)  // 16) * 16
        height = (int(height) // 16) * 16

        with torch.inference_mode():
            image = pipe(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=int(steps),
                guidance_scale=float(guidance),
                generator=generator,
            ).images[0]

        out_path = timestamp_file(variant, "png")
        image.save(out_path)
        print(f"[Diffusion] Saved: {out_path}")
        return out_path
