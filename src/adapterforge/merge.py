"""Wraps `mlx_lm.fuse` to bake a trained adapter back into the base model's weights."""

import shutil
from pathlib import Path

from .models import is_quantized, local_model_path
from .shell import PYTHON, run

# LoRA leaves the tokenizer untouched, but mlx_lm.fuse rewrites these files in
# the format of the transformers version it runs with (5.x). llama.cpp's
# converter runs with 4.x and cannot read that format, and the rewritten
# tokenizer_config.json no longer carries the chat template the GGUF needs.
TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "added_tokens.json",
    "vocab.json",
    "merges.txt",
    "tokenizer.model",
)


def restore_base_tokenizer(base_dir: Path, output_dir: Path) -> list[str]:
    """Copies the base model's own tokenizer files over the rewritten ones."""
    copied = []
    for name in TOKENIZER_FILES:
        source = base_dir / name
        if source.is_file():
            shutil.copy2(source, output_dir / name)
            copied.append(name)
    return copied


def merge_adapter(
    model: str, adapter_path: Path, output_dir: Path, dequantize: bool = False
) -> None:
    """Fuses the adapter. `dequantize` writes full-precision weights, which the
    GGUF export needs: llama.cpp cannot convert MLX-quantized (4-bit QLoRA) models."""
    output_dir.mkdir(parents=True, exist_ok=True)
    base = local_model_path(model)
    command = [
        PYTHON,
        "-m",
        "mlx_lm.fuse",
        "--model",
        base,
        "--adapter-path",
        str(adapter_path),
        "--save-path",
        str(output_dir),
    ]
    if dequantize and is_quantized(base):
        command.append("--dequantize")
    run(command, stage="merge")
    restore_base_tokenizer(Path(base), output_dir)
