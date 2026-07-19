<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Roadmap</h1>
</div>

## Shipped

- `dataset` / `train` / `merge` / `export` / `deploy` / `pipeline` commands (v0.1.0)
- CI: lint, format check, test, dependency security audit, SBOM generation on macOS runners (v0.1.1)

## Next

- Resume/checkpoint support for interrupted `train` runs
- Automatic base-model download when `--model` names a Hugging Face repo not yet cached locally
- Optional evaluation step after training (run the held-out `test.jsonl` split through the fused model and report a rough win rate against the base model)

## Known Limitations

> **Note:** `export` requires a separately cloned llama.cpp checkout with its own Python dependencies installed; this is intentional (see `ARCHITECTURE.md`) but is a manual setup step, not something `pip install adapterforge` alone gives you.

> **Note:** No resume support yet: an interrupted `train` run has to restart from iteration 0.

## Dual-Licensing Readiness

Not planned. AdapterForge is a personal-use CLI wrapper around existing open-source tools (MLX, llama.cpp, Ollama); there is no enterprise-shaped feature set (multi-tenant management, fleet deployment, compliance reporting) that would justify a commercial tier. Stays MIT.
