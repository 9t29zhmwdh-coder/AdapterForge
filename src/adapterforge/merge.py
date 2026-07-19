"""Wraps `mlx_lm.fuse` to bake a trained adapter back into the base model's weights."""

from pathlib import Path

from .shell import run


def merge_adapter(model: str, adapter_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "python",
        "-m",
        "mlx_lm.fuse",
        "--model",
        model,
        "--adapter-path",
        str(adapter_path),
        "--save-path",
        str(output_dir),
    ]
    run(command, stage="merge")
