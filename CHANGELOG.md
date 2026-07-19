# Changelog

All notable changes to this project are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [Semantic Versioning](https://semver.org/).

## [0.1.1] - 2026-07-20

### Added

- `CONTRIBUTING.md`, `ARCHITECTURE.md`, `ROADMAP.md`
- CI: format check (`ruff format`), dependency security audit (`pip-audit`), CycloneDX SBOM generation, automated release job that attaches the SBOM and sources release notes from this file
- `.github/dependabot.yml` for `github-actions` and `pip` ecosystem updates
- OpenSSF Scorecard workflow and README badge

### Changed

- Every GitHub Action in `ci.yml` pinned to a commit SHA instead of a mutable version tag

## [0.1.0] - 2026-07-19

### Added

- `dataset` command: converts `prompt`/`completion`, `instruction`/`response`, or chat `messages` JSONL into train/valid/test splits for `mlx_lm.lora`
- `train` command: QLoRA fine-tuning wrapper around `mlx_lm.lora`
- `merge` command: fuses a trained adapter into the base model via `mlx_lm.fuse`
- `export` command: converts a merged model to GGUF via a local llama.cpp checkout
- `deploy` command: writes an Ollama Modelfile and runs `ollama create`
- `pipeline` command: runs the full dataset to deploy chain from one JSON config
