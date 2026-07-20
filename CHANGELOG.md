# Changelog

All notable changes to this project are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [Semantic Versioning](https://semver.org/).

## [0.1.3] - 2026-07-20

### Changed

- OpenSSF Best Practices Badge questionnaire filled out and linked in the README (in-progress, 99%).
- Split the Best Practices/Scorecard/CI badges from the tech-stack badges onto their own README line.
- Split the README's security/CI badges onto their own line, separate from the platform/tech/AI badges (they were rendering as a single merged line).

## [0.1.2] - 2026-07-20

### Added

- Build provenance attestation (`actions/attest-build-provenance`) for the SBOM attached to each release
- Required status checks (`Lint, format, test, build`, `Security audit`) added to the `solo-main-protection` ruleset, CI must be green before a pull request can merge

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
