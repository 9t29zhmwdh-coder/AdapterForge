<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Contributing</h1>
</div>

Issues and pull requests are welcome.

## Development Setup

```bash
git clone https://github.com/9t29zhmwdh-coder/AdapterForge.git
cd AdapterForge
pip install -e ".[dev]"
```

## Before Opening a Pull Request

```bash
ruff check .
ruff format --check .
pytest tests/ -v
```

All three must pass; CI enforces the same checks on every pull request.

## Commit Style

Semantic commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.

## Pull Request Process

Every change to `main` goes through a pull request, merges require a green CI run. There is no other reviewer than me, so review turnaround depends on my availability, not a team's.
