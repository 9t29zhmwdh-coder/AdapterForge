"""Thin subprocess wrapper shared by every pipeline stage."""

import subprocess
import sys

# The interpreter running AdapterForge, which is the one that has mlx-lm.
# A bare "python" does not exist on a stock Mac (only python3) and, outside an
# activated venv, would not be the environment AdapterForge was installed into.
PYTHON = sys.executable


class StageError(Exception):
    pass


def run(command: list[str], stage: str) -> None:
    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise StageError(f"{stage} failed: {command[0]} not found ({exc})") from exc
    if result.returncode != 0:
        raise StageError(
            f"{stage} failed (exit code {result.returncode}): {' '.join(command)}"
        )
