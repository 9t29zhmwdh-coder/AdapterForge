"""Convert instruction/response pairs into the chat-formatted JSONL splits mlx_lm.lora expects."""

import json
import random
from pathlib import Path


class DatasetError(Exception):
    pass


def _load_records(input_path: Path) -> list[dict]:
    records = []
    with input_path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise DatasetError(
                    f"{input_path}:{line_number}: invalid JSON ({exc})"
                ) from exc
    if not records:
        raise DatasetError(f"{input_path} contains no records")
    return records


def _to_chat_example(record: dict, system_prompt: str | None) -> dict:
    if "messages" in record:
        return {"messages": record["messages"]}

    prompt = record.get("prompt") or record.get("instruction")
    completion = record.get("completion") or record.get("response")
    if not prompt or not completion:
        raise DatasetError(
            "each record needs either 'messages', or a 'prompt'/'instruction' "
            "plus 'completion'/'response' pair"
        )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    messages.append({"role": "assistant", "content": completion})
    return {"messages": messages}


def _write_jsonl(path: Path, examples: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def prepare_dataset(
    input_path: Path,
    output_dir: Path,
    train_ratio: float = 0.8,
    valid_ratio: float = 0.1,
    system_prompt: str | None = None,
    seed: int = 0,
) -> dict[str, int]:
    """Split a raw JSONL file into train/valid/test splits for mlx_lm.lora.

    Returns the number of examples written per split.
    """
    if (
        not 0 < train_ratio < 1
        or not 0 <= valid_ratio < 1
        or train_ratio + valid_ratio >= 1
    ):
        raise DatasetError(
            "train_ratio + valid_ratio must be below 1, both must be positive"
        )

    records = _load_records(input_path)
    examples = [_to_chat_example(r, system_prompt) for r in records]

    rng = random.Random(seed)
    rng.shuffle(examples)

    train_end = int(len(examples) * train_ratio)
    valid_end = train_end + max(1, int(len(examples) * valid_ratio))
    splits = {
        "train": examples[:train_end],
        "valid": examples[train_end:valid_end],
        "test": examples[valid_end:],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, split_examples in splits.items():
        if not split_examples:
            continue
        _write_jsonl(output_dir / f"{name}.jsonl", split_examples)
        counts[name] = len(split_examples)
    return counts
