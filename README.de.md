<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>AdapterForge</h1>
</div>

[🇬🇧 English Version](README.md)

**Bringt einem lokalen Modell dein eigenes Material bei, auf deinem eigenen Mac.**

Ein allgemeines Modell kennt deine Codebasis nicht, deine Produktsprache nicht,
dein Fachgebiet nicht. Fine-Tuning ändert das, nur führt der übliche Weg über
eine Trainings-Cloud, und damit lädst du genau das Material hoch, dessentwegen
es lokal bleiben sollte. Hier läuft die ganze Kette stattdessen auf Apple
Silicon.

```
adapterforge dataset        JSONL in train/valid/test aufteilen
adapterforge train          QLoRA-Fine-Tuning über MLX
adapterforge merge          Adapter ins Basismodell einschmelzen
adapterforge export         nach GGUF konvertieren
adapterforge deploy         an Ollama übergeben
```

`adapterforge pipeline config.json` fährt alle fünf Schritte der Reihe nach.

**Nichts für dich, wenn** ein guter Prompt oder ein paar Beispiele im Kontext
schon reichen. Fine-Tuning kostet Stunden und einen sauber kuratierten
Datensatz und ist das falsche Mittel, wenn dem Modell nur gesagt werden muss,
was es tun soll.

[![CI](https://github.com/9t29zhmwdh-coder/AdapterForge/actions/workflows/ci.yml/badge.svg)](https://github.com/9t29zhmwdh-coder/AdapterForge/actions) [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/9t29zhmwdh-coder/AdapterForge/badge)](https://securityscorecards.dev/viewer/?uri=github.com/9t29zhmwdh-coder/AdapterForge) [![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13666/badge)](https://www.bestpractices.dev/projects/13666)

![Apple Silicon](https://img.shields.io/badge/Apple-Silicon-000000?logo=apple&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?logo=apple&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![AI | Ollama](https://img.shields.io/badge/AI-Ollama-black?logo=ollama&logoColor=white)

---

**Build from source, kein Installer:** ein Python-CLI, das du mit `pip install -e .` installierst und im Terminal aufrufst, kein Hintergrunddienst, kein eigener Daemon.

In der Praxis zeigst du auf ein Basismodell, das schon in deinem Ollama- oder Hugging-Face-Cache liegt, und auf eine JSONL-Datei mit Beispielen, und am Ende steht ein neuer Tag in `ollama list`, der sich wie deine Daten verhält und direkt mit `ollama run` läuft.

## Funktionen

- **Datensatz-Vorbereitung**: wandelt `prompt`/`completion`, `instruction`/`response` oder rohe Chat-`messages` im JSONL-Format in die Train/Valid/Test-Splits um, die `mlx_lm.lora` erwartet
- **QLoRA-Training**: kapselt `mlx_lm.lora` für Low-Rank-Adapter-Fine-Tuning auf Apple Silicon
- **Merge**: kapselt `mlx_lm.fuse`, um den trainierten Adapter in die Gewichte des Basismodells einzubacken
- **GGUF-Export**: konvertiert das gemergte Modell über einen lokalen llama.cpp-Checkout
- **Ollama-Deploy**: schreibt das Modelfile und ruft `ollama create` für dich auf
- **Pipeline-Modus**: fährt die ganze Kette aus einer einzigen JSON-Config, statt fünf einzelner Befehle

## Voraussetzungen

- macOS auf Apple Silicon (M-Serie)
- Python 3.10+
- [Ollama](https://ollama.com) lokal installiert und am Laufen
- Ein lokaler [llama.cpp](https://github.com/ggml-org/llama.cpp)-Checkout, nur für den `export`-Schritt nötig (nicht mitgeliefert, keine pip-Abhängigkeit)

## Schnellstart

```bash
git clone https://github.com/9t29zhmwdh-coder/AdapterForge.git
cd AdapterForge
pip install -e .

# 1. rohe JSONL-Beispiele in Train/Valid/Test-Splits umwandeln
adapterforge dataset --input raw.jsonl --output data/

# 2. QLoRA-Fine-Tuning auf einem Basismodell, das schon im MLX/HF-Cache liegt
adapterforge train --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --data data/ --adapter-path adapters/

# 3. Adapter ins Basismodell einbacken
adapterforge merge --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --adapter-path adapters/ --output fused/

# 4. nach GGUF konvertieren (braucht einen lokalen llama.cpp-Checkout)
adapterforge export --model-dir fused/ --output model.gguf \
  --llama-cpp-path ../llama.cpp

# 5. bei Ollama registrieren
adapterforge deploy --gguf model.gguf --name my-qwen
ollama run my-qwen
```

Oder alle fünf Schritte aus einer Config:

```bash
adapterforge pipeline --config pipeline.json
```

Das Config-Format zeigt [`docs/pipeline.example.json`](docs/pipeline.example.json).

## Deinstallation / Aufräumen

`pip uninstall adapterforge` entfernt das CLI. AdapterForge selbst hält keinen Zustand ausserhalb der Output-Pfade, die du übergibst (`--output`, `--adapter-path`, `--gguf`, ...), diese Ordner löschen entfernt die Trainingsartefakte. Um ein deploytes Modell aus Ollama zu entfernen: `ollama rm <name>`.

---

**Autor:** [Rafael Yilmaz](https://github.com/9t29zhmwdh-coder) · **Status:** Early Release · v0.1.2 · **Lizenz:** MIT
