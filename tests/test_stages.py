import json
import sys
from pathlib import Path

import pytest

from adapterforge import export
from adapterforge.deploy import write_modelfile
from adapterforge.merge import restore_base_tokenizer
from adapterforge.models import is_quantized, local_model_path
from adapterforge.shell import PYTHON, StageError, run


def _fake_llama_cpp(root: Path) -> Path:
    root.mkdir()
    (root / "convert_hf_to_gguf.py").write_text("")
    return root


def test_stages_use_the_running_interpreter() -> None:
    assert PYTHON == sys.executable


def test_run_reports_missing_executable_as_stage_error() -> None:
    with pytest.raises(StageError, match="not found"):
        run(["adapterforge-no-such-binary"], stage="train")


def test_run_reports_nonzero_exit() -> None:
    with pytest.raises(StageError, match="exit code 3"):
        run([sys.executable, "-c", "raise SystemExit(3)"], stage="merge")


def test_local_model_path_keeps_existing_directory(tmp_path: Path) -> None:
    assert local_model_path(str(tmp_path)) == str(tmp_path)


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ({"quantization": {"bits": 4}}, True),
        ({"quantization_config": {"bits": 4}}, True),
        ({"model_type": "qwen2"}, False),
    ],
)
def test_is_quantized_reads_config(
    tmp_path: Path, config: dict, expected: bool
) -> None:
    (tmp_path / "config.json").write_text(json.dumps(config))
    assert is_quantized(tmp_path) is expected


def test_restore_base_tokenizer_overwrites_rewritten_files(tmp_path: Path) -> None:
    base, fused = tmp_path / "base", tmp_path / "fused"
    base.mkdir()
    fused.mkdir()
    (base / "tokenizer_config.json").write_text("original")
    (fused / "tokenizer_config.json").write_text("rewritten")
    (fused / "model.safetensors").write_text("weights")

    copied = restore_base_tokenizer(base, fused)

    assert copied == ["tokenizer_config.json"]
    assert (fused / "tokenizer_config.json").read_text() == "original"
    assert (fused / "model.safetensors").read_text() == "weights"


def test_modelfile_uses_absolute_gguf_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    write_modelfile(
        Path("out/model.gguf"), tmp_path / "Modelfile", system_prompt="Be brief."
    )
    lines = (tmp_path / "Modelfile").read_text().splitlines()
    assert lines[0] == f"FROM {(tmp_path / 'out' / 'model.gguf').resolve()}"
    assert lines[1] == 'SYSTEM """Be brief."""'


def test_converter_python_prefers_llama_cpp_venv(tmp_path: Path) -> None:
    venv_python = tmp_path / ".venv" / "bin" / "python"
    assert export.converter_python(tmp_path) == PYTHON
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("")
    assert export.converter_python(tmp_path) == str(venv_python)
    assert export.converter_python(tmp_path, Path("/opt/py")) == "/opt/py"


def test_export_refuses_quantized_model(tmp_path: Path) -> None:
    model = tmp_path / "fused"
    model.mkdir()
    (model / "config.json").write_text(json.dumps({"quantization": {"bits": 4}}))
    with pytest.raises(StageError, match="--dequantize"):
        export.export_to_gguf(
            model, tmp_path / "m.gguf", _fake_llama_cpp(tmp_path / "llama.cpp")
        )


class _Probe:
    def __init__(self, stdout: str, returncode: int = 0) -> None:
        self.stdout, self.returncode = stdout, returncode


@pytest.mark.parametrize(
    ("versions", "refused"),
    [
        ("3 14 2.2.6", True),
        ("3 14 2.3.0", False),
        ("3 13 2.2.6", False),
        ("3 14 2.5.3", False),
    ],
)
def test_numpy_check_refuses_only_the_corrupting_combination(
    monkeypatch: pytest.MonkeyPatch, versions: str, refused: bool
) -> None:
    monkeypatch.setattr(
        export.subprocess, "run", lambda *a, **k: _Probe(versions + "\n")
    )
    if refused:
        with pytest.raises(StageError, match="numpy>=2.3"):
            export.check_converter_numpy("py")
    else:
        export.check_converter_numpy("py")


def test_numpy_check_reports_missing_numpy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        export.subprocess, "run", lambda *a, **k: _Probe("", returncode=1)
    )
    with pytest.raises(StageError, match="cannot import numpy"):
        export.check_converter_numpy("py")
