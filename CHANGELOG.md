# Changelog

All notable changes to this project are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [Semantic Versioning](https://semver.org/).

## [0.1.9] - 2026-08-04

### Fixed

- The release workflow no longer fails when the release for a tag already exists. It called `gh release create` unconditionally and aborted with `a release with the same tag name already exists` whenever the release had come about some other way. The build had succeeded by then; only the step after it went red. In repositories that attach binaries the release was left with nothing to download, which is the same failure wearing a friendlier face.

---

## [0.1.8] - 2026-07-31

### Changed

- Both READMEs now open with the reason to fine-tune locally at all, which is that the usual route uploads the very material that was the reason to keep things on your own machine. The five pipeline commands follow directly, and a short paragraph says who should not bother: if prompting or a few in-context examples already work, fine-tuning is the wrong tool.

---

## [0.1.7] - 2026-07-29

### Security

- The release workflow no longer grants `contents: write` for its whole run. The permission moves to the one job that publishes the release, and everything else runs with `contents: read`. OpenSSF Scorecard scores the Token-Permissions check 0 out of 10 whenever any workflow holds a top-level write permission, regardless of how little of the run needs it, so this single line was what held the check at zero.

---

## [0.1.6] - 2026-07-28

### Changed

- CodeQL moved from GitHub's default setup to an advanced setup with a committed `.github/workflows/codeql.yml`. The default setup skips pull requests that touch no code of a given language, so a dependency pull request changing only a lock file reported `skipping` on the required `Analyze (...)` checks forever and could never be merged. The workflow runs on every pull request regardless of what changed and uses the `security-extended` query suite, which the default setup does not allow choosing. Required checks are unchanged.
- The CodeQL job requests only `security-events: write` beyond the workflow-level `contents: read`. Repeating read grants at job level is what OpenSSF Scorecard counts as excessive token permissions, and it costs the full `Token-Permissions` score.
- Dependabot now groups only minor and patch updates per ecosystem; majors arrive as individual pull requests. The previous grouping bundled breaking changes with urgently needed security patches into one unreviewable diff. Actions stay grouped wholesale. Follows `engineering-standards` v0.11.0.

## [0.1.5] - 2026-07-28

### Changed

- Bumped the remaining pinned actions: `actions/setup-python` to v7.0.0, `ossf/scorecard-action` to v2.4.4, `github/codeql-action/upload-sarif` to v4.37.3. Every SHA verified against its upstream tag, annotated tags dereferenced to the commit they point at.
- The `setup-python` pin also had a bare `# v6` comment while bumping to v7.0.0; the comment now carries the full version, per `engineering-standards` v0.6.0 section 2.

setup-python v7.0.0 removes the `pip-install` input. No workflow here used it, only `python-version`, so the major bump lands without further changes.

## [0.1.4] - 2026-07-28

### Changed

- The release job attests the SBOM with `actions/attest` v4.2.0 instead of `actions/attest-build-provenance`, which is only a wrapper around it as of its v4. The job also gains the `artifact-metadata: write` permission that `actions/attest` requires, which would otherwise have surfaced as a failure at the next tag push.
- `actions/checkout` is pinned to v7.0.1 across all three workflows. Every file sat on an older v7 SHA whose comment read only `# v7`, so the pin claimed less than it resolved to.

- `ruff` is pinned to 0.16.0 instead of `>=0.6`. The open range let ruff 0.16.0 apply a new import ordering to unchanged source, which turned CI red without a single commit touching the code. `build` and `pip-audit` in the same workflow were already pinned exactly; ruff was the outlier. Dependabot's pip ecosystem bumps it as a reviewable PR from here on.

### Fixed

- Import order in `src/adapterforge/pipeline.py`, per ruff 0.16.0.

Both changes above follow `engineering-standards` v0.6.0, sections 2 and 9.

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
