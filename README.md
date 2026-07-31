<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>AdapterForge</h1>
</div>

[🇩🇪 Deutsche Version](README.de.md)

**Teaches a local model your own material, on your own Mac.**

A general model does not know your codebase, your product wording or your
domain. Fine-tuning fixes that, but the usual path runs through a training
cloud, which means uploading exactly the material that was the reason to keep
it local. This runs the whole chain on Apple Silicon instead.

```
adapterforge dataset        split your JSONL into train/valid/test
adapterforge train          QLoRA fine-tuning through MLX
adapterforge merge          fuse the adapter into the base model
adapterforge export         convert to GGUF
adapterforge deploy         hand it to Ollama
```

`adapterforge pipeline config.json` runs all five in order.

**Not for you if** prompting or a few examples in the context window already
gets you there. Fine-tuning costs hours and a curated dataset, and it is the
wrong tool when the model merely needs to be told what to do.

[![CI](https://github.com/9t29zhmwdh-coder/AdapterForge/actions/workflows/ci.yml/badge.svg)](https://github.com/9t29zhmwdh-coder/AdapterForge/actions) [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/9t29zhmwdh-coder/AdapterForge/badge)](https://securityscorecards.dev/viewer/?uri=github.com/9t29zhmwdh-coder/AdapterForge) [![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13666/badge)](https://www.bestpractices.dev/projects/13666)

![Apple Silicon](https://img.shields.io/badge/Apple-Silicon-000000?logo=apple&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?logo=apple&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![AI | Ollama](https://img.shields.io/badge/AI-Ollama-black?logo=ollama&logoColor=white)

---

**Build from source, no installer:** a Python CLI you install with `pip install -e .` and run from the terminal, no background service, no daemon of its own.

In practice, you point AdapterForge at a base model already sitting in your Ollama or Hugging Face cache and a JSONL file of examples, and after training you get a new tag in `ollama list` that behaves like your data, ready to run with `ollama run`.

## Features

- **Dataset prep**: converts `prompt`/`completion`, `instruction`/`response`, or raw chat `messages` JSONL into the train/valid/test splits `mlx_lm.lora` expects
- **QLoRA training**: wraps `mlx_lm.lora` for low-rank adapter fine-tuning on Apple Silicon
- **Merge**: wraps `mlx_lm.fuse` to bake the trained adapter back into the base model's weights
- **GGUF export**: converts the merged model via a local llama.cpp checkout
- **Ollama deploy**: writes the Modelfile and runs `ollama create` for you
- **Pipeline mode**: runs the full chain from one JSON config instead of five separate commands

## Requirements

- macOS on Apple Silicon (M-series)
- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- A local [llama.cpp](https://github.com/ggml-org/llama.cpp) checkout, only needed for the `export` step (not vendored, not a pip dependency)

## Quick Start

```bash
git clone https://github.com/9t29zhmwdh-coder/AdapterForge.git
cd AdapterForge
pip install -e .

# 1. turn a raw JSONL of examples into train/valid/test splits
adapterforge dataset --input raw.jsonl --output data/

# 2. QLoRA fine-tune a base model already in your MLX/HF cache
adapterforge train --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --data data/ --adapter-path adapters/

# 3. fuse the adapter into the base model
adapterforge merge --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --adapter-path adapters/ --output fused/

# 4. convert to GGUF (needs a local llama.cpp checkout)
adapterforge export --model-dir fused/ --output model.gguf \
  --llama-cpp-path ../llama.cpp

# 5. register with Ollama
adapterforge deploy --gguf model.gguf --name my-qwen
ollama run my-qwen
```

Or run all five steps from one config:

```bash
adapterforge pipeline --config pipeline.json
```

See [`docs/pipeline.example.json`](docs/pipeline.example.json) for the config format.

## Uninstall / Cleanup

`pip uninstall adapterforge` removes the CLI. AdapterForge itself keeps no state outside the output paths you pass it (`--output`, `--adapter-path`, `--gguf`, ...); delete those directories to remove training artifacts. To remove a deployed model from Ollama, run `ollama rm <name>`.

---

**Author:** [Rafael Yilmaz](https://github.com/9t29zhmwdh-coder) · **Status:** Early Release · v0.1.2 · **License:** MIT
