"""Wraps `mlx_lm.lora` to run QLoRA fine-tuning on a local or Hugging Face base model."""

from pathlib import Path

from .shell import run


def run_training(
    model: str,
    data_dir: Path,
    adapter_path: Path,
    iters: int = 600,
    batch_size: int = 4,
    learning_rate: float = 1e-5,
    fine_tune_type: str = "lora",
) -> None:
    adapter_path.mkdir(parents=True, exist_ok=True)
    command = [
        "python",
        "-m",
        "mlx_lm.lora",
        "--model",
        model,
        "--train",
        "--data",
        str(data_dir),
        "--adapter-path",
        str(adapter_path),
        "--iters",
        str(iters),
        "--batch-size",
        str(batch_size),
        "--learning-rate",
        str(learning_rate),
        "--fine-tune-type",
        fine_tune_type,
    ]
    run(command, stage="train")
