"""
Runs inside venv_ltx (Python 3.12, diffusers). Generates a video from a text
prompt with LTX-Video-0.9.7-distilled (open, fast few-step), exports to mp4.

Invoked by core.subprocess_runner.run_worker.
"""
import os
import sys

os.environ["MPLBACKEND"] = "Agg"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.subprocess_runner import read_args, emit_result   # noqa: E402


def main():
    args = read_args()

    import torch
    from diffusers import LTXConditionPipeline
    from diffusers.utils import export_to_video

    print("[ltx_worker] Loading LTX-Video-0.9.7-distilled ...", flush=True)
    pipe = LTXConditionPipeline.from_pretrained(args["repo"], torch_dtype=torch.bfloat16)
    if torch.cuda.is_available():
        total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        if total_gb >= 38:
            pipe.to("cuda")
        else:
            pipe.enable_model_cpu_offload()
        try:
            pipe.enable_vae_tiling()
        except Exception:
            pass

    print("[ltx_worker] Generating ...", flush=True)
    frames = pipe(
        prompt=args["prompt"],
        negative_prompt=args.get("negative_prompt") or None,
        width=int(args["width"]),
        height=int(args["height"]),
        num_frames=int(args["num_frames"]),
        num_inference_steps=int(args["steps"]),
        guidance_scale=float(args["guidance"]),
        output_type="pil",
    ).frames[0]

    os.makedirs(os.path.dirname(args["out_path"]), exist_ok=True)
    export_to_video(frames, args["out_path"], fps=int(args["fps"]))
    emit_result(args["out_path"])


if __name__ == "__main__":
    main()
