"""Runs the full dataset -> train -> merge -> export -> deploy chain from one JSON config."""

import json
from pathlib import Path

from .deploy import deploy_to_ollama
from .export import export_to_gguf
from .merge import merge_adapter
from .train import run_training
from . import dataset as dataset_module


def _resolve_path(base_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base_dir / path


def run_pipeline(config_path: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    base_dir = config_path.parent

    data_dir = _resolve_path(base_dir, config["data_dir"])
    if raw_dataset := config.get("raw_dataset"):
        dataset_module.prepare_dataset(
            input_path=_resolve_path(base_dir, raw_dataset),
            output_dir=data_dir,
            system_prompt=config.get("system_prompt"),
        )

    adapter_path = _resolve_path(base_dir, config["adapter_path"])
    run_training(
        model=config["model"],
        data_dir=data_dir,
        adapter_path=adapter_path,
        iters=config.get("iters", 600),
        batch_size=config.get("batch_size", 4),
        learning_rate=config.get("learning_rate", 1e-5),
    )

    fused_dir = _resolve_path(base_dir, config["fused_dir"])
    merge_adapter(
        model=config["model"], adapter_path=adapter_path, output_dir=fused_dir
    )

    gguf_path = _resolve_path(base_dir, config["gguf_path"])
    export_to_gguf(
        model_dir=fused_dir,
        output_gguf=gguf_path,
        llama_cpp_path=_resolve_path(base_dir, config["llama_cpp_path"]),
        outtype=config.get("outtype", "q8_0"),
    )

    deploy_to_ollama(
        gguf_path=gguf_path,
        model_name=config["ollama_model_name"],
        modelfile_path=_resolve_path(
            base_dir, config.get("modelfile_path", "Modelfile")
        ),
        system_prompt=config.get("system_prompt"),
    )
