import json
from pathlib import Path

import pytest

from adapterforge.dataset import DatasetError, prepare_dataset


def _write_raw(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def test_prepare_dataset_splits_prompt_completion_pairs(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jsonl"
    _write_raw(raw, [{"prompt": f"q{i}", "completion": f"a{i}"} for i in range(10)])

    counts = prepare_dataset(raw, tmp_path / "out", train_ratio=0.8, valid_ratio=0.1)

    assert sum(counts.values()) == 10
    train_lines = (tmp_path / "out" / "train.jsonl").read_text().strip().splitlines()
    first = json.loads(train_lines[0])
    assert first["messages"][0]["role"] == "user"
    assert first["messages"][1]["role"] == "assistant"


def test_prepare_dataset_adds_system_prompt(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jsonl"
    _write_raw(
        raw, [{"instruction": f"hi{i}", "response": f"hello{i}"} for i in range(5)]
    )

    prepare_dataset(raw, tmp_path / "out", system_prompt="be terse")

    train_line = (tmp_path / "out" / "train.jsonl").read_text().strip().splitlines()[0]
    example = json.loads(train_line)
    assert example["messages"][0] == {"role": "system", "content": "be terse"}


def test_prepare_dataset_passes_through_chat_messages(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jsonl"
    messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hey"},
    ]
    _write_raw(raw, [{"messages": messages} for _ in range(5)])

    prepare_dataset(raw, tmp_path / "out")

    example = json.loads(
        (tmp_path / "out" / "train.jsonl").read_text().strip().splitlines()[0]
    )
    assert example["messages"] == messages


def test_prepare_dataset_rejects_incomplete_records(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jsonl"
    _write_raw(raw, [{"prompt": "only a prompt"}])

    with pytest.raises(DatasetError):
        prepare_dataset(raw, tmp_path / "out")


def test_prepare_dataset_rejects_empty_input(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jsonl"
    raw.write_text("")

    with pytest.raises(DatasetError):
        prepare_dataset(raw, tmp_path / "out")


def test_prepare_dataset_rejects_invalid_ratios(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jsonl"
    _write_raw(raw, [{"prompt": "q", "completion": "a"}])

    with pytest.raises(DatasetError):
        prepare_dataset(raw, tmp_path / "out", train_ratio=0.9, valid_ratio=0.2)
