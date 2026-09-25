<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Architecture</h1>
</div>

AdapterForge is a thin CLI orchestrator, not a framework. Each pipeline stage is a Python module that shells out to an existing, already-trusted tool and does nothing clever on its own:

```
raw JSONL --> dataset.py --> mlx_lm.lora (train.py) --> mlx_lm.fuse (merge.py)
    --> llama.cpp convert script (export.py) --> ollama create (deploy.py)
```

- **`dataset.py`**: pure Python, no subprocesses. Reads a raw JSONL file, normalizes each record into the chat `messages` format `mlx_lm.lora` expects, and writes `train.jsonl`/`valid.jsonl`/`test.jsonl` splits.
- **`train.py`**, **`merge.py`**, **`export.py`**, **`deploy.py`**: each wraps exactly one external command (`mlx_lm.lora`, `mlx_lm.fuse`, a llama.cpp conversion script, `ollama create`) via the shared `shell.run()` helper, which raises `StageError` on a non-zero exit code or a missing executable instead of failing silently. The MLX stages run under the interpreter AdapterForge itself runs in (`sys.executable`), so they work without an activated environment. The llama.cpp script runs in its own environment, because its pinned transformers 4.x cannot coexist with mlx-lm's 5.x.
- **`models.py`**: resolves a Hugging Face model id to one complete local snapshot that every stage shares, since `mlx_lm.fuse` works offline and fails on the partial snapshot training leaves behind.
- **`pipeline.py`**: reads one JSON config and calls the stage modules above in sequence, resolving every path in the config relative to the config file's own directory.
- **`cli.py`**: `argparse`-based entry point, one subcommand per stage plus `pipeline`.

There is intentionally no plugin system, no queue, and no persistent service: every invocation is a single foreground process that exits when its stage finishes or fails.

## Why shell out instead of calling libraries directly

`mlx_lm.lora` and `mlx_lm.fuse` are maintained as CLI modules upstream, not as a stable importable API, and GGUF conversion only exists as a llama.cpp script, not a Python package. Wrapping the CLIs keeps AdapterForge decoupled from those projects' internal APIs and lets a user swap in a newer llama.cpp checkout without waiting for an AdapterForge release.
