"""Thin subprocess wrapper shared by every pipeline stage."""

import subprocess


class StageError(Exception):
    pass


def run(command: list[str], stage: str) -> None:
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise StageError(f"{stage} failed (exit code {result.returncode}): {' '.join(command)}")
