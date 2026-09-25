"""Converts a merged mlx_lm model directory to GGUF via a local llama.cpp checkout.

mlx_lm has no native GGUF writer, so this shells out to llama.cpp's conversion
script. Point --llama-cpp-path at a cloned https://github.com/ggml-org/llama.cpp
checkout. Its Python requirements pin versions that conflict with mlx-lm
(transformers 4.x against 5.x), so they belong in their own environment:
`<llama.cpp>/.venv` is used when it exists, or pass --llama-cpp-python.
"""

import subprocess
from pathlib import Path

from .models import is_quantized
from .shell import PYTHON, StageError, run


def converter_python(llama_cpp_path: Path, explicit: Path | None = None) -> str:
    if explicit is not None:
        return str(explicit)
    venv_python = llama_cpp_path / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.is_file() else PYTHON


# numpy below 2.3 reuses temporaries it believes are unreferenced, and Python 3.14
# changed reference counting so that check misfires on arrays above 256 KB. The
# llama.cpp quantizer then drops every sign and writes a GGUF that loads fine
# but only produces garbage, so refuse that combination instead of exporting it.
_VERSION_PROBE = "import sys, numpy; print(sys.version_info[0], sys.version_info[1], numpy.__version__)"


def check_converter_numpy(python: str) -> None:
    try:
        probe = subprocess.run(
            [python, "-c", _VERSION_PROBE], capture_output=True, text=True, check=False
        )
    except OSError as exc:
        raise StageError(
            f"export failed: converter interpreter {python} not usable ({exc})"
        ) from exc
    if probe.returncode != 0:
        raise StageError(
            f"export failed: {python} cannot import numpy, install llama.cpp's requirements there"
        )
    major, minor, numpy_version = probe.stdout.split()
    numpy_release = tuple(int(part) for part in numpy_version.split(".")[:2])
    if (int(major), int(minor)) >= (3, 14) and numpy_release < (2, 3):
        raise StageError(
            f"export refused: numpy {numpy_version} on Python {major}.{minor} corrupts quantized GGUF files. "
            f'Run: {python} -m pip install "numpy>=2.3"'
        )


def export_to_gguf(
    model_dir: Path,
    output_gguf: Path,
    llama_cpp_path: Path,
    outtype: str = "q8_0",
    llama_cpp_python: Path | None = None,
) -> None:
    convert_script = llama_cpp_path / "convert_hf_to_gguf.py"
    if not convert_script.is_file():
        raise StageError(
            f"convert_hf_to_gguf.py not found under {llama_cpp_path}, "
            "pass --llama-cpp-path to a valid llama.cpp checkout"
        )
    if is_quantized(model_dir):
        raise StageError(
            f"{model_dir} holds MLX-quantized weights, which llama.cpp cannot convert. "
            "Merge with --dequantize first (the pipeline does this automatically)."
        )

    python = converter_python(llama_cpp_path, llama_cpp_python)
    check_converter_numpy(python)
    output_gguf.parent.mkdir(parents=True, exist_ok=True)
    command = [
        python,
        str(convert_script),
        str(model_dir),
        "--outfile",
        str(output_gguf),
        "--outtype",
        outtype,
    ]
    run(command, stage="export")
