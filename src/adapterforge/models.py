"""Resolves a base model to a complete local copy."""

import json
from pathlib import Path


def local_model_path(model: str) -> str:
    """A local directory for `model`, downloading the full Hugging Face repo if needed.

    Training only fetches the weights it needs, but `mlx_lm.fuse` runs offline
    and expects the complete snapshot, so a merge right after training failed
    with "cached snapshot is incomplete". Passing the same local directory to
    every stage avoids that.
    """
    candidate = Path(model).expanduser()
    if candidate.exists():
        return str(candidate)
    from huggingface_hub import snapshot_download

    return snapshot_download(model)


def is_quantized(model_dir: str | Path) -> bool:
    """True for MLX-quantized weights, which llama.cpp's converter cannot read."""
    config = Path(model_dir) / "config.json"
    if not config.is_file():
        return False
    data = json.loads(config.read_text(encoding="utf-8"))
    return "quantization" in data or "quantization_config" in data
