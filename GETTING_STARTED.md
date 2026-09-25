# Getting Started with AdapterForge

This guide is for people with **no coding experience**. It walks you through every step needed to fine-tune your first local model with AdapterForge, from opening a terminal to running your custom model in Ollama.

> **Important:** AdapterForge only runs on **macOS with Apple Silicon** (M1/M2/M3/M4), because it depends on Apple's MLX framework for training. If you're on Windows or Linux, you cannot run AdapterForge directly on that machine: see the note at the end of this guide.

---

## Windows

AdapterForge cannot run natively on Windows: MLX is an Apple Silicon-only framework. There is no workaround, this is a hard platform requirement, not a missing dependency.

If you want to try AdapterForge, you'll need access to a Mac with Apple Silicon. Skip ahead to the **macOS** section below and run the steps there.

---

## Linux

Same limitation as Windows: AdapterForge requires macOS on Apple Silicon and cannot run on Linux. Skip ahead to the **macOS** section below if you have access to a Mac.

---

## macOS

### 1. Open a terminal

Press `Cmd+Space` to open Spotlight, type `Terminal`, and press Enter.

### 2. Check your Python version

AdapterForge needs Python 3.10 or newer. Check what you have:

```bash
python3 --version
```

- If it prints `Python 3.10.x` or higher, you're set, continue to step 3.
- If it prints an older version, or `command not found: python3`, install a current Python:
  - Easiest: download the macOS installer from [python.org/downloads](https://www.python.org/downloads/) and run it.
  - Alternative, if you use [Homebrew](https://brew.sh): `brew install python@3.12`

### 3. Install Ollama

AdapterForge deploys trained models to [Ollama](https://ollama.com), so you need it running locally first. Download the macOS app from [ollama.com](https://ollama.com), install it, and open it once so it starts running in the background.

Check it's running:

```bash
ollama list
```

If this prints a (possibly empty) list of models instead of an error, Ollama is running.

### 4. Download AdapterForge

```bash
git clone https://github.com/9t29zhmwdh-coder/AdapterForge.git
cd AdapterForge
```

If you don't have `git`, macOS will offer to install the Xcode Command Line Tools the first time you run a `git` command, follow that prompt.

### 5. Install AdapterForge

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `adapterforge` command into a private environment inside the AdapterForge folder. In a new terminal window, run `source .venv/bin/activate` again from that folder before using `adapterforge`.

### 6. Prepare your training data

AdapterForge trains on a JSONL file (one JSON example per line). Create a file, for example `raw.jsonl`, with your own `prompt`/`completion` pairs, `instruction`/`response` pairs, or chat `messages`. See the main [README](README.md#features) for the supported formats.

Convert it into the splits the trainer expects:

```bash
adapterforge dataset --input raw.jsonl --output data/
```

### 7. Fine-tune a base model

Pick an MLX base model from Hugging Face. It is downloaded on first use (a 7B 4-bit model is about 4 GB) and reused afterwards. Models you pulled with Ollama cannot be used here, since Ollama stores them in a format MLX cannot train on. For example:

```bash
adapterforge train --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --data data/ --adapter-path adapters/
```

This step can take a while depending on your dataset size and Mac.

### 8. Merge the adapter into the base model

```bash
adapterforge merge --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --adapter-path adapters/ --output fused/ --dequantize
```

`--dequantize` stores the merged model at full precision. The next step needs that, because llama.cpp cannot read the compressed 4-bit format.

### 9. Export to GGUF and deploy to Ollama

This step needs a local [llama.cpp](https://github.com/ggml-org/llama.cpp) checkout with its own Python environment, which is not installed automatically. Set it up once:

```bash
git clone --depth 1 https://github.com/ggml-org/llama.cpp.git ../llama.cpp
python3 -m venv ../llama.cpp/.venv
../llama.cpp/.venv/bin/pip install -r ../llama.cpp/requirements/requirements-convert_hf_to_gguf.txt
../llama.cpp/.venv/bin/pip install "numpy>=2.3"
```

The last line matters on Python 3.14: older numpy produces a model that loads but only answers gibberish. AdapterForge checks this and stops with a hint if it is missing.

Then convert and deploy:

```bash

adapterforge export --model-dir fused/ --output model.gguf \
  --llama-cpp-path ../llama.cpp

adapterforge deploy --gguf model.gguf --name my-model
```

### 10. Run your model

```bash
ollama run my-model
```

If you see a response, everything worked.

---

## Uninstalling

```bash
pip uninstall adapterforge
```

AdapterForge itself keeps no state outside the folders you told it to write to (`--output`, `--adapter-path`, `--gguf`, ...), delete those directories to remove training artifacts. To remove a deployed model from Ollama, run `ollama rm <name>`.

## Something not working?

Check [GitHub Issues](https://github.com/9t29zhmwdh-coder/AdapterForge/issues) to see if someone already ran into the same problem, or open a new issue with the exact command you ran and the error message you got.
