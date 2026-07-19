"""AdapterForge CLI: dataset prep, QLoRA training, merging, GGUF export and Ollama deploy."""

import argparse
import sys
from pathlib import Path

from . import dataset as dataset_module
from .deploy import deploy_to_ollama
from .export import export_to_gguf
from .merge import merge_adapter
from .pipeline import run_pipeline
from .shell import StageError
from .train import run_training


def _add_dataset_command(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("dataset", help="split a raw JSONL file into train/valid/test")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--system-prompt", default=None)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--valid-ratio", type=float, default=0.1)


def _add_train_command(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("train", help="run QLoRA fine-tuning via mlx_lm.lora")
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--adapter-path", required=True, type=Path)
    parser.add_argument("--iters", type=int, default=600)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=1e-5)


def _add_merge_command(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("merge", help="fuse a trained adapter into the base model")
    parser.add_argument("--model", required=True)
    parser.add_argument("--adapter-path", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)


def _add_export_command(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("export", help="convert a merged model to GGUF via llama.cpp")
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--llama-cpp-path", required=True, type=Path)
    parser.add_argument("--outtype", default="q8_0")


def _add_deploy_command(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("deploy", help="register a GGUF with the local Ollama daemon")
    parser.add_argument("--gguf", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--modelfile", type=Path, default=Path("Modelfile"))
    parser.add_argument("--system-prompt", default=None)


def _add_pipeline_command(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("pipeline", help="run the full chain from a JSON config file")
    parser.add_argument("--config", required=True, type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adapterforge",
        description="Local QLoRA adapter training pipeline for Ollama models on Apple Silicon.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_dataset_command(subparsers)
    _add_train_command(subparsers)
    _add_merge_command(subparsers)
    _add_export_command(subparsers)
    _add_deploy_command(subparsers)
    _add_pipeline_command(subparsers)
    return parser


def _dispatch(args: argparse.Namespace) -> None:
    if args.command == "dataset":
        counts = dataset_module.prepare_dataset(
            input_path=args.input,
            output_dir=args.output,
            train_ratio=args.train_ratio,
            valid_ratio=args.valid_ratio,
            system_prompt=args.system_prompt,
        )
        print(f"wrote splits: {counts}")
    elif args.command == "train":
        run_training(
            model=args.model,
            data_dir=args.data,
            adapter_path=args.adapter_path,
            iters=args.iters,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )
    elif args.command == "merge":
        merge_adapter(model=args.model, adapter_path=args.adapter_path, output_dir=args.output)
    elif args.command == "export":
        export_to_gguf(
            model_dir=args.model_dir,
            output_gguf=args.output,
            llama_cpp_path=args.llama_cpp_path,
            outtype=args.outtype,
        )
    elif args.command == "deploy":
        deploy_to_ollama(
            gguf_path=args.gguf,
            model_name=args.name,
            modelfile_path=args.modelfile,
            system_prompt=args.system_prompt,
        )
    elif args.command == "pipeline":
        run_pipeline(args.config)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        _dispatch(args)
    except (dataset_module.DatasetError, StageError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
