<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Security Policy</h1>
</div>

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, report it via [GitHub Security Advisory](https://github.com/9t29zhmwdh-coder/AdapterForge/security/advisories/new) or contact me via my GitHub profile.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

A response within **48 hours** is the target, and the issue will be worked on promptly.

## Supply Chain Security

- All GitHub Actions used in the CI pipeline are pinned to a specific commit SHA, not a mutable tag or branch (see `standards/ci-cd.md` section 2 in [engineering-standards](https://github.com/9t29zhmwdh-coder/engineering-standards)).
- Dependencies are declared in `pyproject.toml`; AdapterForge is a library/CLI, not an application with a committed lock file.
- `pip-audit` runs in CI on every push and pull request.
- A CycloneDX SBOM is generated in CI and attached to every GitHub Release.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅ Yes    |
| Older   | ❌ No     |

Security fixes are only applied to the latest release.

## Security Design Notes

AdapterForge runs entirely on your machine and only shells out to tools you already have installed (`mlx_lm`, `ollama`, a local llama.cpp checkout). It makes no network calls of its own and does not read, write, or transmit anything outside the paths you pass on the command line. There are no user accounts, no secrets, and no network listener, so authentication, authorization, and encryption-at-rest controls do not apply to this tool.
