"""Converts a merged mlx_lm model directory to GGUF via a local llama.cpp checkout.

mlx_lm has no native GGUF writer, so this shells out to llama.cpp's conversion
script. Point --llama-cpp-path at a cloned https://github.com/ggml-org/llama.cpp
checkout (its Python dependencies must already be installed).
"""

from pathlib import Path

from .shell import StageError, run


def export_to_gguf(
    model_dir: Path,
    output_gguf: Path,
    llama_cpp_path: Path,
    outtype: str = "q8_0",
) -> None:
    convert_script = llama_cpp_path / "convert_hf_to_gguf.py"
    if not convert_script.is_file():
        raise StageError(
            f"convert_hf_to_gguf.py not found under {llama_cpp_path}, "
            "pass --llama-cpp-path to a valid llama.cpp checkout"
        )

    output_gguf.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "python",
        str(convert_script),
        str(model_dir),
        "--outfile",
        str(output_gguf),
        "--outtype",
        outtype,
    ]
    run(command, stage="export")
