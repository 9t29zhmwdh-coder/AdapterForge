"""Writes an Ollama Modelfile for a GGUF and registers it with the local Ollama daemon."""

from pathlib import Path

from .shell import run


def write_modelfile(
    gguf_path: Path, modelfile_path: Path, system_prompt: str | None = None
) -> None:
    lines = [f"FROM {gguf_path}"]
    if system_prompt:
        lines.append(f'SYSTEM """{system_prompt}"""')
    modelfile_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def deploy_to_ollama(
    gguf_path: Path,
    model_name: str,
    modelfile_path: Path,
    system_prompt: str | None = None,
) -> None:
    write_modelfile(gguf_path, modelfile_path, system_prompt)
    run(["ollama", "create", model_name, "-f", str(modelfile_path)], stage="deploy")
