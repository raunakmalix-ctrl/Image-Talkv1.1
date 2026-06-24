"""
Runs inside venv_ltx (diffusers from git, which has FluxKontextPipeline).
Instruction-based image editing with FLUX.1-Kontext-dev (gated — reads HF_TOKEN
from the environment). Invoked by core.subprocess_runner.run_worker.
"""
import os
import sys

os.environ["MPLBACKEND"] = "Agg"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.subprocess_runner import read_args, emit_result   # noqa: E402


def main():
    args = read_args()

    import torch
    from diffusers import FluxKontextPipeline
    from diffusers.utils import load_image

    print("[kontext_worker] Loading FLUX.1-Kontext-dev ...", flush=True)
    pipe = FluxKontextPipeline.from_pretrained(args["repo"], torch_dtype=torch.bfloat16)
    if torch.cuda.is_available():
        total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        pipe.to("cuda") if total_gb >= 38 else pipe.enable_model_cpu_offload()

    generator = None
    if int(args.get("seed", -1)) >= 0:
        generator = torch.Generator(device="cuda").manual_seed(int(args["seed"]))

    print("[kontext_worker] Editing ...", flush=True)
    image = pipe(
        image=load_image(args["image"]),
        prompt=args["prompt"],
        num_inference_steps=int(args["steps"]),
        guidance_scale=float(args["guidance"]),
        generator=generator,
    ).images[0]

    os.makedirs(os.path.dirname(args["out_path"]), exist_ok=True)
    image.save(args["out_path"])
    emit_result(args["out_path"])


if __name__ == "__main__":
    main()
